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
        if new_x > self.n or new_y > self.n or new_x < 0 or new_y < 0:
            return 0

        if self.state == [0,3] and x == 0 and y == 1:
            return 0
        if self.state == [2,3] and x == 0 and y == 1:
            return 0
        if self.state == [3,3] and x == 0 and y == 1:
            return 0
        if self.state == [5,3] and x == 0 and y == 1:
            return 0

        self.state[0] = new_x
        self.state[1] = new_y

        if [new_x, new_y] == self.goal:
            print "Hurray"
            return 20
        else:
            return 0

