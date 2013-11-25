# Find all simulators in here.
import random

class ExitRoomSimulator:
    """A simulator for a MaxQAgent.
    """

    def __init__(self, n, init_state, goal):
        self.n = n
        self.state = init_state[:]
        self.goal = goal[:]

    def move(self, x, y):
        new_x = self.state[0] + x
        new_y = self.state[1] + y
        if new_x >= self.n or new_y >= self.n or new_x < 0 or new_y < 0:
            return -1

        if self.state == [0,3] and x == 0 and y == 1:
            return -1
        if self.state == [2,3] and x == 0 and y == 1:
            return -1
        if self.state == [3,3] and x == 0 and y == 1:
            return -1
        if self.state == [5,3] and x == 0 and y == 1:
            return -1

        self.state[0] = new_x
        self.state[1] = new_y

        if [new_x, new_y] == self.goal:
            return 20
        else:
            return -1

class GridWorldWithVehicle:
    """A simulator for a MaxQAgent.
    """

    def __init__(self, n, pos_x, pos_y):
        self.MAX_VEL = 2

        self.n = n
        self.state = [pos_x, pos_y, 0, 0]
        self.wall_block = {}
        self.readWalls()
        # print self.wall_block
        # self.state = {'vel': [0, 0],\
        #               'pos': [pos_x, pos_y]}

    def readWalls(self):
        f = open('./walls3.txt', 'r')

        for i in xrange(self.n+1):
            line = f.readline()
            split_line = line.split()
            for x_tile in split_line:
                y = int(x_tile)
                for x in xrange(self.n):
                    self.wall_block[(self.n*(y%self.n)+x,\
                        y - (y%self.n) -0.5)] = True

        for i in xrange(self.n):
            line = f.readline()
            split_line = line.split()
            for y_tile in split_line:
                x = int(y_tile)
                for y in xrange(self.n):
                    self.wall_block[(x - (x%self.n) - 0.5,\
                        self.n*(x%self.n)+y)] = True

    def moveSteps(self, x, y):
        new_x = self.state[0] + x
        new_y = self.state[1] + y

        change_tuple = (self.state[0] + x/2.0,
                        self.state[1] + y/2.0)

        try:
            self.wall_block[change_tuple]
            # print self.state, x, y, change_tuple
            # No state change because you crashed into wall.
            return -1.7
        except KeyError:
            self.state[0] = new_x
            self.state[1] = new_y
            return -1.0

    def move(self):
        # Try to alternate x and y moves as much as possible
        sign = -1 if self.state[2] < 0 else 1
        move_list = []
        for i in xrange(abs(self.state[2])):
            move_list.append((sign, 0))

        sign = -1 if self.state[3] < 0 else 1
        insert_index = 1
        for i in xrange(abs(self.state[3])):
            move_list.insert(insert_index, (0, sign))
            insert_index += 2

        reward = 0.0
        for step in move_list:
            reward += self.moveSteps(step[0], step[1])

        if len(move_list) == 0:
            return -1
        else:
            return reward/len(move_list)

    def simulateStepWithAcc(self, acc_x, acc_y):
        reward = self.move()
        new_x = self.state[2] + acc_x
        new_y = self.state[3] + acc_y

        x_sign = -1 if new_x < 0 else 1
        y_sign = -1 if new_y < 0 else 1

        self.state[2] = x_sign * min(abs(new_x), self.MAX_VEL)
        self.state[3] = y_sign * min(abs(new_y), self.MAX_VEL)

        # print self.state
        return reward

if __name__ == '__main__':
    for i in xrange(10):
        sim = GridWorldWithVehicle(6, random.randrange(0, 36),\
                                   random.randrange(0, 36))
        for j in xrange(3000):
            sim.simulateStepWithAcc(random.randrange(0, 2) - 1,\
                                    random.randrange(0, 2) - 1)

