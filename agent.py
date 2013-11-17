#!/usr/bin/env python
from collections import defaultdict
from math import log
import random

from simulator import ExitRoomSimulator

gamma = 1.0

class MaxQAgent:
    """An advice following MaxQ agent. 
    
    Node structure
    --------------
    {'name' : str,
    'children' : list}
    """

    def __init__(self):
        self.v_func = {}        # only for primitive actions
        self.c_func = defaultdict(int)        # non-primitive actions
        self.nodes = dict()

        f = open('./tree.dat', 'r')
        for line in f.readlines():
            split = line.split()
            self.nodes[int(split[0])] = \
                    {'name' : split[1],\
                    'children' : [int(c) for c in split[2:]]}

        print self.nodes 

        self.init_episode()

    def init_episode(self):
        self.t = 0
    
    def MaxQ_0(self, i):
        state = self.getState()

        # If it is a primitive action
        if self.nodes[i]['children'] == []:
            reward = self.execute(i)
            alpha = self.alpha(i)
            try:
                self.v_func[(i, state)] = (1-alpha) * self.v_func[(i, state)] + \
                        alpha*reward
            except KeyError:
                self.v_func[(i, state)] = alpha*reward

            self.t += 1
            return 1

        # If not a primitive action
        else:
            count = 0
            while not self.terminated(i, state):
                # choose action using q value
                if random.random() < self.epsilon():
                    action = self.nodes[i]['children'][\
                            random.randrange(len(self.nodes[i]['children']))]
                else:
                    max_child = -1
                    max_q_value = -1000
                    for j in self.nodes[i]['children']:
                        # compute q(i, s, j)
                        value = self.evaluateMaxNode(j, state) + \
                                self.c_func[(i, state, j)]
                        if value > max_q_value:
                            max_child = j
                            max_q_value = value

                    action =  max_child

                # call MaxQ_0 with action 
                N = self.MaxQ_0(action)

                # get the new state 
                new_state = self.getState()

                # update C value using evaluate function
                alpha = self.alpha(i)
                self.c_func[(i, state, action)] = \
                        (1-alpha) * self.c_func[(i, state, action)] + \
                        alpha * (gamma**N) * self.evaluateMaxNode(i, new_state)

                count += N 

                state = new_state
            #end while

            return count

    def evaluateMaxNode(self, i, state):
        if self.nodes[i]['children'] == []:
            try:
                return self.v_func[(i, state)]
            except KeyError:
                self.v_func[(i, state)] = 0
                return 0
        else:
            max_child = -1
            max_q_value = -1000
            for j in self.nodes[i]['children']:
                # compute q(i, s, j)
                value = self.evaluateMaxNode(j, state) + \
                        self.c_func[(i, state, j)]
                if value > max_q_value:
                    max_child = j
                    max_q_value = value

            #TODO: Check whether paper is wrong.
            return max_q_value

    def startEpisode(self):
        for i in xrange(100):
            self.simulator = ExitRoomSimulator(6,\
                    [random.randrange(6), random.randrange(6)],\
                    [0, 5])
            self.MaxQ_0(0)

    def terminated(self, i, state):
        if i == 1:
            if state[1] > 3:
                return True
            else:
                return False
        elif i == 2 or i == 0:
            if state == tuple(self.simulator.goal):
                return True
            else: 
                return False
        else:
            return True

    def getState(self):
        return (self.simulator.state[0], self.simulator.state[1])

    def execute(self, i):
        if i == 3: # North
            return self.simulator.move(-1, 0)
        if i == 4: # South
            return self.simulator.move(1, 0)
        if i == 5: # East
            return self.simulator.move(0, 1)
        
        print i, "THIS SHOULD NOT HAPPEN"


    def alpha(self, i):
        return 1.0/(self.t+1)

    def epsilon(self):
        return 0.2 / (log(self.t+1)+1)


if __name__ == '__main__':
    agent = MaxQAgent()
    agent.startEpisode()
