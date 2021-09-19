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
        level = f.read().split("\n")
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
            else:
                wall.append(0)
        WALLS.append(wall)

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

def isStuck(box):
    #Test if a box is stuck
    #A box is considered stuck if we can't move it vertically or horizontally
    (x,y) = box
    #If there is wall up or below the block, we can't move it vertically
    if (x > 0 and x < len(WALLS) - 1):
        isStuckVertical = WALLS[x-1][y] or WALLS[x + 1][y]
    else:
        isStuckVertical = 1
    #If there is wall on the left or right to the block, we can't move it horizontally
    if (y > 0 and y < len(WALLS[x]) - 1):
        isStuckHorizontal = WALLS[x][y - 1] or WALLS[x][y + 1]
    else:
        isStuckHorizontal = 1
    return isStuckHorizontal and isStuckVertical

def isStuckState(state):
    # Test if a state is unsolvable
    # If one box is stuck, and it is not at a goal, then we can't move it anymore
    # Therefore it's impossible to reach the goal from that state
    for box in state.boxes:
        if isStuck(box) and (box not in GOALS):
            return True
    return False

def isWinning(state):
    #Check if all the boxes are at the goals
    return set(state.boxes) == set(GOALS)

#Trasition from one state to the next
def handleMoves(state, action):
    #xNext and yNext are the position of the player after the move
    #xBox and yBox are the position of the boxes after the move,
    #assume that we hit a block and move it in that direction
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
        else:
            #Note to self:if we dont use copy(), the new name will just be an alias of the old object
            newBoxes = state.boxes.copy()
            newBoxes.remove((xNext, yNext))
            newBoxes.append((xBox, yBox))
            return State(newBoxes, (xNext, yNext), state.cost + 1, state)

#Heuristic solver using A* algorithm
def solveHeuristic():
    global STATEVISITED
    global STATECREATED

    STATECREATED = 1
    STATEVISITED = 0
    initState = State(BOXES, PLAYER, 0, None)
    moves = ["UP", "DOWN", "LEFT", "RIGHT"]
    pq = queue.PriorityQueue()
    pq.put(initState)
    visited = []
    while not pq.empty():
        current = pq.get()
        STATEVISITED += 1
        if (isWinning(current)):
            return current
        visited.append((current.boxes, current.player))
        neighbors = [handleMoves(current, move) for move in moves]
        for state in neighbors:
            if (state == None):     #Invalid move
                continue
            elif (isStuckState(state)):  #Ignore the stuck states
                STATECREATED += 1
                continue
            elif ((state.boxes, state.player) in visited):  #Ignore the visted states
                STATECREATED += 1
                continue
            else:
                STATECREATED += 1
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
    printPath(path)

#solveHeuristic()