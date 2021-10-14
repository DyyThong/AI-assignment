import queue
import time
import datetime
import random, sys, copy, os, pygame
from pygame.locals import *

#Code for Graphic
FPS = 30 # frames per second to update the screen
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 600 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# The total width and height of each tile in pixels.
TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED = 5 # how many pixels per frame the camera moves

# The percentage of outdoor tiles that have additional
# decoration on them, such as a tree or rock.
OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'




def main(filename):
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage
    global currentState
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('Sokoban')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'boy': pygame.image.load('boy.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}

    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}
    
    currentImage = 0
    currentState = 0
    PLAYERIMAGES = [IMAGESDICT['boy']]

    # startScreen() # show the title screen until the user presses a key

    levels = readLevelsFile(filename)
    currentLevelIndex = 0

    # while True: # main game loop
        # Run the level to actually start playing the game:
    # result = runLevel(levels, currentLevelIndex)
    runLevel(levels, currentLevelIndex)

        # if result in ('solved', 'next'):
        #     # Go to the next level.
        #     currentLevelIndex += 1
        #     if currentLevelIndex >= len(levels):
        #         # If there are no more levels, go back to the first one.
        #         currentLevelIndex = 0
        # elif result == 'back':
        #     # Go to the previous level.
        #     currentLevelIndex -= 1
        #     if currentLevelIndex < 0:
        #         # If there are no previous levels, go to the last one.
        #         currentLevelIndex = len(levels)-1
        # elif result == 'reset':
        #     pass # Do nothing. Loop re-calls runLevel() to reset the level


def runLevel(levels, levelNum):
    global currentImage, currentState
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True # set to True to call drawMap()
    # levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    # levelRect = levelSurf.get_rect()
    # levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    levelIsComplete = False
    # Track how much the camera has moved:
    cameraOffsetX = 0
    cameraOffsetY = 0
    # Track if the keys to move the camera are being held down:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True: # main game loop
        # Reset these variables:
        playerMove = False
        keyPressed = False

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                terminate()

            elif event.type == KEYDOWN:
                # Handle key presses
                keyPressed = True
                if event.key == K_RIGHT:
                    currentState += 1
                    playerMove = True

                # Set the camera move mode.
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_ESCAPE:
                    terminate() # Esc key quits.
                # elif event.key == K_BACKSPACE:
                #     return 'reset' # Reset the level.
                elif event.key == K_p:
                    # Change the player image to the next one.
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        # After the last player image, use the first one.
                        currentImage = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                # Unset the camera move mode.
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMove != False and not levelIsComplete:
    
            moved = makeMove(mapObj, gameStateObj, playerMove)

            if moved:
                # increment the step counter.
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                # level is solved, we should show the "Solved!" image.
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        # Adjust mapSurf's Rect object based on the camera offset.
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)

        # Draw mapSurf to the DISPLAYSURF Surface object.
        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        # DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            # is solved, show the "Solved!" image until the player
            # has pressed a key.
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update() # draw DISPLAYSURF to the screen.
        FPSCLOCK.tick()


def isWall(mapObj, x, y):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x'):
        return True # wall is blocking
    return False


def decorateMap(mapObj, startxy):

    startx, starty = startxy # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    mapObjCopy = copy.deepcopy(mapObj)

    # Remove the non-wall characters from the map data
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    # Flood fill to determine inside/outside floor tiles.
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # Convert the adjoined walls into corner tiles.
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['stars']:
        return True # a star is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):

    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']

    if playerMoveTo == True:
        xOffset = playerpos[currentState][1] - playerpos[currentState-1][1]
        yOffset = playerpos[currentState][0] - playerpos[currentState-1][0]

    # See if the player can move in that direction.
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            # There is a star in the way, see if the player can push it.
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                # Move the star.
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False
        # Move the player upwards.
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


# def startScreen():
#     """Display the start screen (which has the title and instructions)
#     until the player presses a key. Returns None."""

#     # Position the title image.
#     titleRect = IMAGESDICT['title'].get_rect()
#     topCoord = 50 # topCoord tracks where to position the top of the text
#     titleRect.top = topCoord
#     titleRect.centerx = HALF_WINWIDTH
#     topCoord += titleRect.height

#     # Unfortunately, Pygame's font & text system only shows one line at
#     # a time, so we can't use strings with \n newline characters in them.
#     # So we will use a list with each line in it.
#     instructionText = ['Push the stars over the marks.',
#                        'Backspace to reset level, Esc to quit.',
#                        'N for next level, B to go back a level.']

#     # Start with drawing a blank color to the entire window:
#     DISPLAYSURF.fill(BGCOLOR)

#     # Draw the title image to the window:
#     DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

#     # Position and draw the text.
#     for i in range(len(instructionText)):
#         instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
#         instRect = instSurf.get_rect()
#         topCoord += 10 # 10 pixels will go in between each line of text.
#         instRect.top = topCoord
#         instRect.centerx = HALF_WINWIDTH
#         topCoord += instRect.height # Adjust for the height of the line.
#         DISPLAYSURF.blit(instSurf, instRect)

#     while True: # Main loop for the start screen.
#         for event in pygame.event.get():
#             if event.type == QUIT:
#                 terminate()
#             elif event.type == KEYDOWN:
#                 if event.key == K_ESCAPE:
#                     terminate()
#                 return # user has pressed a key, so return.

#         # Display the DISPLAYSURF contents to the actual screen.
#         pygame.display.update()
#         FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    # Each level must end with a blank line
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = [] # Will contain a list of level objects.
    levelNum = 0
    mapTextLines = [] # contains the lines for a single level's map.
    mapObj = [] # the map object made from the data in mapTextLines
    for lineNum in range(len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        # if ';' in line:
        #     # Ignore the ; lines, they're comments in the level file.
        #     line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # A blank line indicates the end of a level's map in the file.
            # Convert the text in mapTextLines into a level object.

            # Find the longest row in the map.
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # Add spaces to the ends of the shorter rows. This
            # ensures the map will be rectangular.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # Convert mapTextLines to a map object.
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # Loop through the spaces in the map and find the @, ., and $
            # characters for the starting game state.
            startx = None # The x and y for the player's starting position
            starty = None
            goals = [] # list of (x, y) tuples for each goal.
            stars = [] # list of (x, y) for each star's starting position.
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is star & goal
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' is star
                        stars.append((x, y))

            # Basic level design sanity checks:
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            # Create level object and starting game state object.
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)
        
            # Reset the variables for reading the next map.
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):

    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) # call right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # call left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) # call down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # call up


def drawMap(mapObj, gameStateObj, goals):

    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR) # start with a blank color on the surface.

    # Draw the tile sprites onto this surface.
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            # First draw the base ground/wall tile.
            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                # Draw any tree/rock decorations that are on this tile.
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    # A goal AND star are on this space, draw goal first.
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                # Then draw the star sprite.
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y) in goals:
                # Draw a goal without a star on it.
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)

            # Last draw the player on the board.
            if (x, y) == gameStateObj['player']:
                # Note: The value "currentImage" refers
                # to a key in "PLAYERIMAGES" which has the
                # specific player image we want to show.
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    """Returns True if all the goals have stars in them."""
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            # Found a space with a goal but no star on it.
            return False
    return True



#https://baldur.iti.kit.edu/theses/SokobanPortfolio.pdf
#https://verificationglasses.wordpress.com/2021/01/17/a-star-sokoban-planning/
#https://home.cse.ust.hk/~yqsong/teaching/comp3211/projects/2017Fall/G14.pdf

#Code for Algorimth
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
    #plus the distance from the player to his nearest box
    def calPriority(self):
        priority = 0
        for box in self.boxes:
            minDis = min([calManhattan(box, goal) for goal in GOALS])
            priority += minDis
        closetBoxToPlayer = min([calManhattan(box, self.player) for box in self.boxes])
        priority = priority + 0.5 * closetBoxToPlayer
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
def solve(pq):
    getDeadlocks()
    global STATEVISITED
    global STATECREATED

    initState = State(BOXES, PLAYER, 0, None)
    STATECREATED = 1
    STATEVISITED = 1
    if isStuckState(initState.boxes):
        return None

    moves = ["UP", "DOWN", "LEFT", "RIGHT"]
    #pq = queue.PriorityQueue()
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

def solveHeuristic():
    state = solve(queue.PriorityQueue())
    if (state != None):
        printPath(state)
    return solve(queue.PriorityQueue())
def solverBlind():
    state = solve(queue.Queue())
    if (state != None):
        printPath(state)
    return solve(queue.Queue())

#Trans for graphic
playerpos = []
boxst = []

def printPath(finalState):

    global boxst, playerpos
    temp = []
    state = finalState
    while (state != None):
        playerpos.insert(0,state.player)
        temp1 = state.boxes
        temp.insert(0,temp1[0])
        
        state = state.prevState
    # print(playerpos[0])
    # print(playerpos[1])
    # print(playerpos[2])
    # print(playerpos[3])
    boxst = [(sub[1], sub[0]) for sub in temp]
    # print(temp)
    # print(boxst)



def terminate():
    pygame.quit()
    sys.exit()

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

    main(sys.argv[1])
#solveHeuristic()
