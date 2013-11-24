#!/usr/bin/env python
from collections import defaultdict
from math import log
import random
import sys

# from simulator import ExitRoomSimulator
from simulator import GridWorldWithVehicle

gamma = 1.0
EPISODES = 2

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

        f = open('./gwwv_tree.dat', 'r')
        for line in f.readlines():
            split = line.split()
            self.nodes[int(split[0])] = \
                    {'name' : split[1],\
                    'children' : [int(c) for c in split[2:]]}

        self.t = 0
        print self.nodes

    def initEpisodes(self, ep_count):
        self.t = 0
        self.translated_advice = []
        self.ep_count = ep_count + 1
    
    def MaxQ_0(self, i):
        # alpha = 1.0 / (self.ep_count * (log(self.t + 1)+1))
        alpha = 1.0 / (self.ep_count)

        # If it is a primitive action
        print i
        if self.nodes[i]['children'] == []:
            state = self.getState(i)
            print state
            reward = self.execute(i)
            print 'reward', reward, alpha, self.ep_count
            # alpha = self.alpha(i)
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
            epsi = self.epsilon()

            # for 3-advice-full 
            if i == 1:
                self.advice.pop(0)
                self.cur_box = (self.simulator.state[0]/6, \
                        self.simulator.state[1]/6)
                self.tar_box = self.getTarget(self.cur_box, self.advice[0])
                self.translated_advice = self.advice[:2]
                to_solve = 1
                partial_tar_box = self.tar_box[:]
                partial_advice = self.translated_advice[:]
                print self.tar_box

            state = self.getState(i)
            while not self.terminated(i, state):
                # choose action using q value
                if random.random() < epsi:
                    action = self.nodes[i]['children'][\
                            random.randrange(len(self.nodes[i]['children']))]
                    print 'action chosen', action, epsi
                else:
                    max_child = -1
                    max_q_value = -1000000
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
                new_state = self.getState(i)

                # update C value using evaluate function

                # alpha = self.alpha(i)
                self.c_func[(i, state, action)] = \
                        (1-alpha) * self.c_func[(i, state, action)] + \
                        alpha * (gamma**N) * self.evaluateMaxNode(i, new_state)

                count += N 

                state = new_state

                # The part I despise
                if i == 1:
                    old_box = self.cur_box[:]
                    self.cur_box = (self.simulator.state[0]/6, \
                            self.simulator.state[1]/6)

                    # if you solved Node 2 properly
                    print 'partial target', tuple(partial_tar_box) 
                    print 'cur_box', self.cur_box
                    if self.cur_box == tuple(partial_tar_box):
                        to_solve -= 1
                        partial_advice.pop(0)
                        self.translated_advice = partial_advice[:2]
                        partial_tar_box = self.getTarget(self.cur_box,\
                                                partial_advice[0])
                        print 'to solve', to_solve

                    # else, you need to solve another node 2.
                    elif self.cur_box != old_box: 
                        to_solve += 1
                        partial_advice.insert(0, self.getTargetDir(\
                                self.cur_box, partial_tar_box))
                        partial_tar_box = old_box[:]
                        self.translated_advice = partial_advice[:2]
                    print partial_advice, self.translated_advice
            #end while

            return count

    def evaluateMaxNode(self, i, state):
        state = self.getState(i)
        if self.nodes[i]['children'] == []:
            try:
                return self.v_func[(i, state)]
            except KeyError:
                self.v_func[(i, state)] = 0
                return 0
        else:
            max_child = -1
            max_q_value = -1000
            max_v = -1
            for j in self.nodes[i]['children']:
                # compute q(i, s, j)
                v = self.evaluateMaxNode(j, state)
                value = v + \
                        self.c_func[(i, state, j)]
                if value > max_q_value:
                    max_child = j
                    max_q_value = value
                    max_v = v

            #TODO: Check whether paper is wrong.
            return max_q_value

    def startEpisode(self):
        for i in xrange(EPISODES):
            self.initEpisodes(i)
            start = [random.randrange(6), random.randrange(6)]
            self.simulator = GridWorldWithVehicle(6,\
                    03,\
                    33)
            self.advice = ['E', 'E', 'E', 'S', 'S', 'S', 'E', 'E', 'S', 'S']
            # print >> sys.stderr, "start is ", start
            self.MaxQ_0(0)
            print "Episode", i, "done."
        # for i in xrange(6):
        #     for j in xrange(2):
        #         print str(i), str(4+j), self.evaluateMaxNode(2, (i, 4+j))
                
        for key in self.v_func:
            print key, self.v_func[key]
        for key in self.c_func:
            print key, self.c_func[key]

    def terminated(self, i, state):
        if i == 0:
            if len(self.advice) == 0:
                return True
            else:
                return False
        elif i == 1:
            if (self.simulator.state[0]/6, self.simulator.state[1]/6) == \
                    self.tar_box:
                print "1 terminated"
                return True
            else: 
                return False
        elif i == 2:
            if (self.simulator.state[0]/6, self.simulator.state[1]/6) != \
                    self.cur_box:
                print "2 terminated", self.simulator.state, self.cur_box,\
                        self.tar_box
                return True
            else: 
                return False
        else:
            return True

    def getState(self, i):
        state = [self.simulator.state[0]%6, self.simulator.state[1]%6,\
                 self.simulator.state[2], self.simulator.state[3]]
        if i > 2 or i == 1:
            state.extend(self.advice[:2])
        elif i == 2:
            state.extend(self.translated_advice[:2])
        elif i == 0:
            state = self.advice[:]
        return tuple(state)

    def execute(self, i):
        if i == 3: # N
            return self.simulator.simulateStepWithAcc(0, 1)
        if i == 4: # NE
            return self.simulator.simulateStepWithAcc(1, 1)
        if i == 5: # E
            return self.simulator.simulateStepWithAcc(1, 0)
        if i == 6: # SE
            return self.simulator.simulateStepWithAcc(1, -1)
        if i == 7: # S
            return self.simulator.simulateStepWithAcc(0, -1)
        if i == 8: # SW
            return self.simulator.simulateStepWithAcc(-1, -1)
        if i == 9: # W
            return self.simulator.simulateStepWithAcc(-1, 0)
        if i == 10: # NW
            return self.simulator.simulateStepWithAcc(-1, 1)
        if i == 11: # zero acc
            return self.simulator.simulateStepWithAcc(0, 0)
        
        print i, "THIS SHOULD NOT HAPPEN"

    def getTarget(self, current, tar_dir):
        target = list(current[:])
        if tar_dir == 'E':
            target[0] += 1
        elif tar_dir == 'W':
            target[0] -= 1
        elif tar_dir == 'N':
            target[1] += 1
        elif tar_dir == 'S':
            target[1] -= 1

        return tuple(target)

    def getTargetDir(self, current, target):
        x_diff = current[0] - target[0]
        y_diff = current[1] - target[1]

        if x_diff == -1 and y_diff == 0:
            return 'E'
        if x_diff == 1 and y_diff == 0:
            return 'W'
        if x_diff == 0 and y_diff == -1:
            return 'N'
        if x_diff == 0 and y_diff == 1:
            return 'S'

    def alpha(self, i):
        return 1.0/ (self.ep_count)

    def epsilon(self):
        return 1.35 / (log(self.ep_count+1)+1)


if __name__ == '__main__':
    agent = MaxQAgent()
    agent.startEpisode()

