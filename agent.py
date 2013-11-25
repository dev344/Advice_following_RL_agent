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
    """An advice following Options framework agent. 
    
    Node structure
    --------------
    {'name' : str,
    'children' : list}
    """

    def __init__(self):
        self.options = dict()
        self.q = dict()
        for i in xrange(9):
            self.options[i+3] = None

    def initEpisodes(self, ep_count):
        self.done = False
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

    def takeOption(self, i):
        move_reward = 0
        step_count = 0
        if i == 3: # N
            move_reward = self.simulator.simulateStepWithAcc(0, 1)
            step_count = 1
        elif i == 4: # NE
            move_reward = self.simulator.simulateStepWithAcc(1, 1)
            step_count = 1
        elif i == 5: # E
            move_reward = self.simulator.simulateStepWithAcc(1, 0)
            step_count = 1
        elif i == 6: # SE
            move_reward = self.simulator.simulateStepWithAcc(1, -1)
            step_count = 1
        elif i == 7: # S
            move_reward = self.simulator.simulateStepWithAcc(0, -1)
            step_count = 1
        elif i == 8: # SW
            move_reward = self.simulator.simulateStepWithAcc(-1, -1)
            step_count = 1
        elif i == 9: # W
            move_reward = self.simulator.simulateStepWithAcc(-1, 0)
            step_count = 1
        elif i == 10: # NW
            move_reward = self.simulator.simulateStepWithAcc(-1, 1)
            step_count = 1
        elif i == 11: # zero acc
            move_reward = self.simulator.simulateStepWithAcc(0, 0)
            step_count = 1

        if self.terminated(0):
            self.done = True
            cur_state = [self.simulator.state[0]/SIZE, self.simulator.state[1]/SIZE]
            if cur_state == self.targets[0]:
                move_reward += 15
                if self.debug:
                    print "Yay", i, self.simulator.state, move_reward, cur_state, self.targets[0]
            else:
                move_reward += -5

            if self.debug:
                print i, self.simulator.state, cur_state, self.targets[0]
                print move_reward

        return (move_reward, step_count)
    
    def takeStep(self):
        alpha = 1.0 / (log(self.ep_count)+1)
        state = self.getState(0)
        epsi = self.epsilon()

        option = -1
        if random.random() < epsi:
            option = 3 + random.randrange(9)
            if self.debug:
                print 'random', state, self.simulator.state
                print option
        else:
            max_value = -10000
            if self.debug:
                print state, self.simulator.state
            for key in self.options:
                try:
                    value = self.q[(key, state)]
                except KeyError:
                    self.q[(key, state)] = 0
                    value = 0

                if self.debug:
                    print key, value, "|", 

                if max_value < value:
                    max_value = value
                    option = key

            if self.debug:
                print option

        
        reward, steps = self.takeOption(option)
        # print reward, option, state

        if self.debug:
            print reward, alpha*reward, steps, ']'

        new_state = self.getState(0)
        max_value = -1000 
        max_option = -1

        if self.debug:
            print new_state,

        for key in self.options:
            try:
                value = self.q[(key, new_state)]
            except KeyError:
                self.q[(key, new_state)] = 0
                value = 0

            if self.debug:
                print key, value, "|", 

            if max_value < value:
                max_value = value
                max_option = key

        if self.debug:
            print max_option

        try:
            if self.done:
                self.q[(option, state)] = (1 - alpha)*self.q[(option, state)] +\
                        alpha * (reward)
            else:
                self.q[(option, state)] = (1 - alpha)*self.q[(option, state)] +\
                        alpha * (reward + (gamma**steps) * self.q[(max_option, new_state)])

        except:
            if self.done:
                self.q[(option, state)] = alpha * \
                        (reward)
            else:
                self.q[(option, state)] = alpha * \
                        (reward + (gamma**steps) * self.q[(max_option, new_state)])

    def startEpisode(self):
        while not self.terminated(0):
            self.takeStep()
        if self.debug:
            print "Episode Ended"

    def initSimulator(self):
        start_x = 2*SIZE + random.randrange(SIZE) 
        start_y = 2*SIZE + random.randrange(SIZE)
        vel_x = random.randrange(5) - 2
        vel_y = random.randrange(5) - 2
        if self.debug:
            print 'start', start_x, start_y
        # start_x = 16
        # start_y = 22
        # vel_x = 0
        # vel_y = 1
        self.start = [start_x/SIZE, start_y/SIZE]
        self.simulator.state = [start_x, start_y, vel_x, vel_y]

        self.targets = [[2,3]]

    def startLearning(self):
        start_x = 12 + random.randrange(SIZE) 
        start_y = 12 + random.randrange(SIZE)
        self.simulator = GridWorldWithVehicle(SIZE,\
                start_x,\
                start_y)

        self.debug = False
        for i in xrange(EPISODES):
            self.initEpisodes(i)
            self.initSimulator()
            self.startEpisode()
            # print 'episode', i, 'done'
            # for key in self.q:
                # if self.q[key] != 0:
                    # print key, self.q[key]

        self.debug = True
        for i in xrange(TEST_EPISODES):
            self.initEpisodes(EPISODES + i)
            self.initSimulator()
            self.startEpisode()

        print 'END'
        for key in self.q:
            if self.q[key] > 0:
                print key, self.q[key]

    def terminated(self, i):
        if i == 0:
            cur_state = [self.simulator.state[0]/SIZE, self.simulator.state[1]/SIZE]

            if cur_state == self.start:
                return False
            else:
                return True
        else:
            print i, "Terminated?"
            return True

    def getState(self, i):
        if i == 0:
            state = (self.simulator.state[0]%SIZE,\
                     self.simulator.state[1]%SIZE,\
                     self.simulator.state[2],\
                     self.simulator.state[3])
        return state


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
        return 0.5

    def epsilon(self):
        return 0.2
        # return 1.15 / (log(self.ep_count)+1)


if __name__ == '__main__':
    agent = MaxQAgent()
    agent.startLearning()

