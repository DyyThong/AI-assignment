#import sys, pygame
#from pygame import display
import queue
import sys
import time
import datetime

#https://baldur.iti.kit.edu/theses/SokobanPortfolio.pdf
#https://verificationglasses.wordpress.com/2021/01/17/a-star-sokoban-planning/
#https://home.cse.ust.hk/~yqsong/teaching/comp3211/projects/2017Fall/G14.pdf

WALLS = []
PLAYER = ()
BOXES = []
GOALS = []
STUCK = []

#number of states created and visited
STATECREATED = 0
STATEVISITED = 0

#Create level information from text file
def parseLevel(filename):
    '''Notation:
        - @: agent
        - #: wall
        - $: box
        - .: destination
        - *: box on destination
        - +: agent on destination
    '''
    global WALLS
    global PLAYER
    global BOXES
    global GOALS

    with open(filename, "r") as f:
        level = f.read().strip("\n").split("\n")
    for x in range(len(level)):
        wall = []
        for y in range(len(level[x])):
            char = level[x][y]
            if (char == "@"):
                wall.append(0)
                PLAYER = (x,y)
            elif (char == "#"):
                wall.append(1)
            elif (char == "$"):
                wall.append(0)
                BOXES.append((x,y))
            elif (char == "."):
                wall.append(0)
                GOALS.append((x,y))
            elif (char == "*"):
                wall.append(0)
                BOXES.append((x,y))
                GOALS.append((x,y))
            elif (char == "+"):
                wall.append(0)
                GOALS.append((x,y))
                PLAYER = (x,y)
            elif (char == " "):
                wall.append(0)
        WALLS.append(wall)

#Mark the cells where a box can't reach a goal (I call them stuck cells)
def getDeadlocks():
    global STUCK
    #First, assume that all cells are stuck cell
    STUCK = [(x,y) for x in range(len(WALLS)) for y in range(len(WALLS[x]))]

    #For each goal, we place a box there and try to PULL it across the map
    #If we can reach a cell by pulling, it also means that we can push a block at that cell to the goal.
    #So we'll remove that cell from the stuck list
    for goal in GOALS:
        q = queue.Queue()
        if goal not in STUCK:
            continue
        q.put(goal)

        '''We can perform a pull if:
            - The box doesn't move to a wall
            - The agent doesn't move to a wall
        '''
        while not q.empty():
            (x,y) = q.get()

            if (x,y) not in STUCK:
                continue

            STUCK.remove((x,y))
            #Try to pull a block upward
            if (x - 2 >= 0 and (x - 1, y) in STUCK):
                if WALLS[x-1][y] != 1 and WALLS[x-2][y] != 1:
                    q.put((x - 1, y))
            #Try to pull a block downward
            if (x + 2 < len(WALLS) and (x + 1, y) in STUCK):
                if  WALLS[x+1][y] != 1 and WALLS[x+2][y] != 1:
                    q.put((x + 1, y))
            #Try to pull a block to the left
            if (y - 2 >= 0 and (x, y - 1) in STUCK):
                if WALLS[x][y-1] != 1 and WALLS[x][y - 2] != 1:
                    q.put((x, y - 1))
            #Try to pull a block to the right
            if (y + 2 < len(WALLS[x]) and (x, y + 1) in STUCK):
                if WALLS[x][y + 1] != 1 and WALLS[x][y + 2] != 1:
                    q.put((x, y + 1))

    #Remove the walls from the final list
    STUCK = [cell for cell in STUCK if WALLS[cell[0]][cell[1]] == 0]

class State:
    def __init__(self, boxes, player, cost, prevState):
        self.boxes = boxes.copy()
        self.player = player
        self.cost = cost    #The number of moves it take to get to the current state
        self.priority = self.calPriority()
        self.prevState = prevState     #previous state

    def __lt__(self, other):
        # The metric to determine which move we should prioritize
        return (self.cost + self.priority) < (other.cost + other.priority)

    def __str__(self):
        string = ""
        string += "Boxes: " + str(self.boxes) + "\n"
        string += "Player: " + str(self.player) + "\n"
        string += "Cost: " + str(self.cost) + "\n"
        return string

    #calculating the prority value of a state
    #priority value is determined by the total manhattan distance of every boxes to its nearest goals
    def calPriority(self):
        priority = 0
        for box in self.boxes:
            minDis = min([calManhattan(box, goal) for goal in GOALS])
            priority += minDis
        return priority

#Calculating the manhattan distance between 2 points
def calManhattan(pointA, pointB):
    (xA, yA) = pointA
    (xB, yB) = pointB
    return abs(xA - xB) + abs(yA - yB)

def isWinning(state):
    #Check if all the boxes are at the goals
    return set(state.boxes) == set(GOALS)

def isStuckState(boxes):
    for box in boxes:
        if box in STUCK:
            return True
    return False

#Trasition from one state to the next
def handleMoves(state, action):
    #xNext and yNext are the position of the player after the move
    #xBox and yBox are the position of the boxes after the move,
    #assume that we hit a block and move it in that direction
    global STATECREATED
    (xPlayer, yPlayer) = state.player
    if action == "UP":
        (xNext, yNext) = (xPlayer - 1, yPlayer)
        (xBox, yBox) = (xNext - 1, yNext)
    elif action == "DOWN":
        (xNext, yNext) = (xPlayer + 1, yPlayer)
        (xBox, yBox) = (xNext + 1, yNext)
    elif action == "LEFT":
        (xNext, yNext) = (xPlayer, yPlayer - 1)
        (xBox, yBox) = (xNext, yNext - 1)
    elif action == "RIGHT":
        (xNext, yNext) = (xPlayer, yPlayer + 1)
        (xBox, yBox) = (xNext, yNext + 1)
    else:
        return None

    #Wall and out of bound check
    if (xNext < 0 or xNext >= len(WALLS)):
        return None
    elif (yNext < 0 or yNext >= len(WALLS[xNext])):
        return None
    elif WALLS[xNext][yNext]:
        return None

    #If we dont hit any boxes, move to a new state
    if (xNext, yNext) not in state.boxes:
        STATECREATED += 1
        return State(state.boxes, (xNext, yNext), state.cost + 1, state)
    else:
        #Cant move if the block hits a wall go goes out of bound
        if xBox < 0 or xBox >= len(WALLS):
            return None
        elif yBox < 0 or yBox >= len(WALLS[xBox]):
            return None
        elif WALLS[xBox][yBox]:
            return None
        #Cant move if the block hits another block
        elif (xBox, yBox) in state.boxes:
            return None
        #Discard state if a box move to a stuck cell
        elif (xBox, yBox) in STUCK:
            return None
        else:
            #Note to self:if we dont use copy(), the new name will just be an alias of the old object
            newBoxes = state.boxes.copy()
            newBoxes.remove((xNext, yNext))
            newBoxes.append((xBox, yBox))
            STATECREATED += 1
            return State(newBoxes, (xNext, yNext), state.cost + 1, state)

#Heuristic solver using A* algorithm
def solveHeuristic():
    getDeadlocks()
    global STATEVISITED
    global STATECREATED

    initState = State(BOXES, PLAYER, 0, None)
    STATECREATED = 1
    STATEVISITED = 1
    if isStuckState(initState.boxes):
        return None

    moves = ["UP", "DOWN", "LEFT", "RIGHT"]
    pq = queue.PriorityQueue()
    pq.put(initState)
    visited = []
    visited.append((set(initState.boxes), initState.player))
    while not pq.empty():
        current = pq.get()
        STATEVISITED += 1
        if (isWinning(current)):
            return current
        neighbors = [handleMoves(current, move) for move in moves]
        for state in neighbors:
            if (state == None):     #Invalid move
                continue
            elif ((set(state.boxes), state.player) in visited):  #Ignore the visted states
                continue
            else:
                visited.append((set(state.boxes), state.player))
                pq.put(state)
    return None

def printPath(finalState):
    state = finalState
    while (state != None):
        print(state)
        print("___________________________________________")
        state = state.prevState

# Initialize the pygame
#pygame.init()

# Create the screen
#screen = display.set_mode((800, 600))

#while True:
#    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>")
        exit(1)

    parseLevel(sys.argv[1])
    start = time.time()
    path = solveHeuristic()
    end = time.time()
    print("Time elapsed: " + str(datetime.timedelta(seconds=end - start)))
    print("State created: " + str(STATECREATED))
    print("State visited: "+ str(STATEVISITED))
    print("Cost: " + str(path.cost))


#solveHeuristic()