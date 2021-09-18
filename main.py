import sys, pygame
from pygame import display

#https://baldur.iti.kit.edu/theses/SokobanPortfolio.pdf
#https://verificationglasses.wordpress.com/2021/01/17/a-star-sokoban-planning/

WALLS = [[0, 1, 0, 1, 0, 0],
         [0, 1, 0, 1, 1, 1],
         [1, 1, 0, 0, 0, 0],
         [0, 0, 0, 0, 1, 1],
         [1, 1, 1, 0, 1, 0],
         [0, 0, 1, 0, 1, 0]]
PLAYER = (3, 3)
BOXES = [(2, 2), (2, 4), (3, 2), (4, 3)]
GOALS = [(0, 2), (2, 5), (3, 0), (5, 3)]

class State:
    def __init__(self, boxes):
        self.boxes = boxes



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
    if (y > 0 and y < len(WALLS) - 1):
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


def solveHeuristic():
    pass


# Initialize the pygame
#pygame.init()

# Create the screen
#screen = display.set_mode((800, 600))

while True:
    pass