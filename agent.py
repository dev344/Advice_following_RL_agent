#!/usr/bin/env python
from collections import defaultdict
from math import log
import random
import sys

# from simulator import ExitRoomSimulator
from simulator import GridWorldWithVehicle

gamma = 1.0
EPISODES = 2000000
TEST_EPISODES = 10
SIZE = 8

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

        f = open('./qlearningtree.dat', 'r')
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

        self.advices = [['n', 'n', 'n'],\
                        ['n', 'e', 'n'],\
                        ['n', 'e', 's'],\
                        ['n', 'n', 'e'],\
                        ['n', 'n', 'w'],\
                        ['n', 'w', 'n'],\
                        ['n', 'w', 's'],\
                        \
                        ['e', 'e', 'e'],\
                        ['e', 's', 'e'],\
                        ['e', 's', 'w'],\
                        ['e', 'e', 's'],\
                        ['e', 'e', 'n'],\
                        ['e', 'n', 'e'],\
                        ['e', 'n', 'w'],\
                        \
                        ['s', 's', 's'],\
                        ['s', 'w', 's'],\
                        ['s', 'w', 'n'],\
                        ['s', 's', 'w'],\
                        ['s', 's', 'e'],\
                        ['s', 'e', 's'],\
                        ['s', 'e', 'n'],\

                        ['w', 'w', 'w'],\
                        ['w', 'n', 'w'],\
                        ['w', 'n', 'e'],\
                        ['w', 'w', 'n'],\
                        ['w', 'w', 's'],\
                        ['w', 's', 'w'],\
                        ['w', 's', 'e']]
    
    def MaxQ_0(self, i):
        # alpha = 1.0 / (self.ep_count * (log(self.t + 1)+1))
        alpha = 1.0 / (log(self.ep_count)+1)

        # If it is a primitive action
        if self.debug:
            print i

        if self.nodes[i]['children'] == []:
            state = self.getState(i)
            # print state
            reward = self.execute(i)
            # alpha = self.alpha(i)
            try:
                self.v_func[(i, state)] = (1-alpha) * self.v_func[(i, state)] + \
                        alpha*reward
            except KeyError:
                self.v_func[(i, state)] = alpha*reward

            if self.debug:
                print 'reward', reward, alpha, state, i, self.v_func[(i, state)]

            if reward > 24:
                print 'reward', reward, state, i, self.v_func[(i, state)]
            self.t += 1
            return 1

        # If not a primitive action
        else:
            count = 0
            epsi = self.epsilon()

            state = self.getState(i)

            while not self.terminated(i) and count < 100:
                # choose action using q value
                if self.debug:
                    print 'else', self.simulator.state, state,
                if random.random() < epsi:
                    action = self.nodes[i]['children'][\
                            random.randrange(len(self.nodes[i]['children']))]
                    # print 'action chosen', action, epsi
                else:
                    max_child = -1
                    max_q_value = -1000000
                    for j in self.nodes[i]['children']:
                        # compute q(i, s, j)
                        value = self.evaluateMaxNode(j, state) + \
                                self.c_func[(i, state, j)]

                        if self.debug:
                            print j, value, "|",

                        if value > max_q_value:
                            max_child = j
                            max_q_value = value

                    action =  max_child

                if self.debug:
                    print 'action', action
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

            #end while

            if count >= 100:
                print "count", count, state

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
        start_x = 12 + random.randrange(SIZE) 
        start_y = 12 + random.randrange(SIZE)
        self.simulator = GridWorldWithVehicle(SIZE,\
                start_x,\
                start_y)

        self.debug = False
        for i in xrange(EPISODES):
            self.initEpisodes(i)
            start_x = 12 + random.randrange(SIZE) 
            start_y = 12 + random.randrange(SIZE)
            vel_x = random.randrange(5) - 2
            vel_y = random.randrange(5) - 2
            self.start = [start_x/SIZE, start_y/SIZE]
            self.simulator.state = [start_x, start_y, vel_x, vel_y]
            # self.advice = self.advices[random.randrange(len(self.advices))]
            self.advice = self.advices[random.randrange(2)]
            self.targets = self.getTargets(self.advice, self.start[:])
            self.done = 0

            self.MaxQ_0(0),
            # print self.targets, self.advice, start_x, start_y, \
            # self.simulator.state[0], self.simulator.state[1]

        self.debug = True
        for i in xrange(TEST_EPISODES):
            self.initEpisodes(EPISODES)
            start_x = 12 + random.randrange(SIZE) 
            start_y = 12 + random.randrange(SIZE)
            vel_x = random.randrange(5) - 2
            vel_y = random.randrange(5) - 2
            self.start = [start_x/SIZE, start_y/SIZE]
            self.simulator.state = [start_x, start_y, vel_x, vel_y]
            # self.advice = self.advices[random.randrange(len(self.advices))]
            self.advice = self.advices[random.randrange(2)]
            self.targets = self.getTargets(self.advice, self.start[:])
            self.done = 0

            # print >> sys.stderr, "start is ", start
            print self.MaxQ_0(0),
            print self.targets, self.advice, start_x, start_y, self.simulator.state[0], \
                    self.simulator.state[1]

        for key in self.v_func:
            if self.v_func[key] > 6:
                print key, self.v_func[key]
        # for key in self.c_func:
        #     print key, self.c_func[key]

    def terminated(self, i):
        if i == 0:
            cur_state = [self.simulator.state[0]/SIZE, self.simulator.state[1]/SIZE]
            if self.done == 3:
                return True
            elif cur_state == self.start or (cur_state in self.targets):
                return False
            else:
                return True
        else:
            print i, "Terminated?"
            return True

    def getState(self, i):
        if i > 2:
            state = [self.simulator.state[0]%SIZE, self.simulator.state[1]%SIZE,\
                     self.simulator.state[2], self.simulator.state[3]]
            state.extend(self.advice[self.done:])
        elif i == 0:
            state = self.advice[self.done:]
        return tuple(state)

    def execute(self, i):
        move_reward = 0
        if i == 3: # N
            move_reward = self.simulator.simulateStepWithAcc(0, 1)
        elif i == 4: # NE
            move_reward = self.simulator.simulateStepWithAcc(1, 1)
        elif i == 5: # E
            move_reward = self.simulator.simulateStepWithAcc(1, 0)
        elif i == 6: # SE
            move_reward = self.simulator.simulateStepWithAcc(1, -1)
        elif i == 7: # S
            move_reward = self.simulator.simulateStepWithAcc(0, -1)
        elif i == 8: # SW
            move_reward = self.simulator.simulateStepWithAcc(-1, -1)
        elif i == 9: # W
            move_reward = self.simulator.simulateStepWithAcc(-1, 0)
        elif i == 10: # NW
            move_reward = self.simulator.simulateStepWithAcc(-1, 1)
        elif i == 11: # zero acc
            move_reward = self.simulator.simulateStepWithAcc(0, 0)

        if [self.simulator.state[0]/SIZE, self.simulator.state[1]/SIZE] == self.targets[self.done]:
            self.done += 1
            move_reward += 14*self.done

        return move_reward

    def getTargets(self, advice, start):
        targets = []
        for direction in advice:
            if direction == 'e':
                start[0] += 1
            elif direction == 'w':
                start[0] -= 1
            elif direction == 'n':
                start[1] += 1
            elif direction == 's':
                start[1] -= 1
            targets.append(start[:])
        return targets

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
        return 1.35 / (log(self.ep_count)+1)


if __name__ == '__main__':
    agent = MaxQAgent()
    agent.startEpisode()

