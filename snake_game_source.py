from turtle import *
from functools import partial
import random

#Setting constants that represent the arrow keys and spacebar on the keyboard, constants that define how fast the snake moves, messages displayed
KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE = 'Up', 'Down', 'Left', 'Right', 'space'
SNAKE_MOVE_RATE = 250
SNAKE_SLOW_MOVE_RATE = 500
SCREEN_TILE = 'Snake by Yingrun Ouyang'
WIN_MSG = 'You win!'
LOSE_MSG = 'Game Over!'
INTRO_MSG = "Click anywhere to start the game ....."
COLOR_MONSTER = "purple"
FONT = ("arial", 16, "normal")
STATUS_FONT = ('arial', 16, 'bold')
FOOD_FONT = ('arial', 16, 'normal')
STATUS_BAR = 'Contact:                        Time:                       Motion:'
HEADING_BY_KEY = {KEY_UP: 90, KEY_DOWN: 270, KEY_LEFT: 180, KEY_RIGHT: 0}
GAME_AREA_WIDTH = GAME_AREA_HEIGHT = 500
CELL_WIDTH = CELL_HEIGHT = 20
N_CELL_X = GAME_AREA_WIDTH // CELL_WIDTH
N_CELL_Y = GAME_AREA_HEIGHT // CELL_HEIGHT
SNAKE_MONSTER_INIT_MIN_DISTANCE = 3
NUM_FOODS = 5 #the number of foods that appear on the screen at the start of the game

#Global variables initialized to None or default values that are used throughout the code for storing and updating game state
g_snake = None
g_monster = None
g_screen = None
g_status = None
g_is_clicked = False
g_is_game_paused = False
g_is_game_over = False
g_snake_dir = -1
g_snake_length = 1
g_food_in_stomach = 5
g_is_snake_extending = True
g_snake_movable = False
g_snake_trace = []
g_snake_pos = [0, 0]
g_monster_pos = [0, 0]
g_game_time = 0
g_num_contacts = 0
g_food_matrix = []
g_is_food_visible = None
g_food_consumed = None
g_pen = None
g_pen_gameover = None
g_pen_for_food = None
g_pen_for_status = None
g_pen_for_time = None
g_pen_for_contact = None
g_pen_for_motion = None

#Configures the game screen using Turtle graphics module. It disables the automatic screen refresh, sets the title of the game, and sets up the dimensions of the game screen.
def configScreen():
    s = Screen()
    s.tracer(0)  # disable auto screen refresh, 0=disable, 1=enable
    s.title(SCREEN_TILE)
    s.setup(GAME_AREA_WIDTH + 120, GAME_AREA_HEIGHT + 120 + 80)
    s.mode("standard")
    return s

#Defines a rectangle shape with given width and height, using the turtle graphics library.
def rectangle(width, height):
    g_pen.setheading(0)
    g_pen.forward(width)
    g_pen.right(90)
    g_pen.forward(height)
    g_pen.right(90)
    g_pen.forward(width)
    g_pen.right(90)
    g_pen.forward(height)

#Sets the heading of the snake according to the key that is pressed. It checks if the game is over or not and sets the global variables g_snake_movable and g_snake_dir accordingly.
def setSnakeHeading(key):
    global g_snake_movable
    global g_snake_dir
    global g_is_game_paused
    if not g_is_game_over:
        g_is_game_paused = False
        if key in HEADING_BY_KEY.keys():
            if (g_snake_dir + 180) % 360 != HEADING_BY_KEY[key]:
                g_snake_dir = HEADING_BY_KEY[key]
                g_snake.setheading(g_snake_dir)
                g_snake_movable = True
                checkCrossing()
                updateMotionStatus()
        g_screen.update()

# Allows the game to be paused and resumed during play.
def pauseGame():
    global g_is_game_paused
    g_is_game_paused = not g_is_game_paused
    updateMotionStatus()

#Configures the key events for the game. 
def configureKey(s):
    s.onkey(partial(onArrowKeyPressed, KEY_UP), KEY_UP) #assign the arrow keys and spacebar to specific actions in the game
    s.onkey(partial(onArrowKeyPressed, KEY_DOWN), KEY_DOWN)
    s.onkey(partial(onArrowKeyPressed, KEY_LEFT), KEY_LEFT)
    s.onkey(partial(onArrowKeyPressed, KEY_RIGHT), KEY_RIGHT)
    s.onkey(pauseGame, KEY_SPACE)
    s.listen() #make the screen listen for key presses

#Checks whether the snake has reached the game boundaries and stops the snake from moving further if it has.
def checkBoundary():
    global g_snake_movable, g_snake_pos
    cell_x, cell_y = screenPosToCellPos(g_snake_pos[0], g_snake_pos[1])
    g_snake_movable = True
    # left
    if cell_x <= 0 and g_snake_dir == 180:
        g_snake_movable = False
    # right
    if cell_x >= N_CELL_X - 1 and g_snake_dir == 0:
        g_snake_movable = False
    # up
    if cell_y <= 0 and g_snake_dir == 90:
        g_snake_movable = False
    # down
    if cell_y >= N_CELL_Y - 1 and g_snake_dir == 270:
        g_snake_movable = False
    if g_snake_movable:
        checkCrossing()

    updateMotionStatus()

#Checks if the snake's head intersects with its body.
def checkCrossing():
    global g_snake_movable, g_snake_trace, g_snake_dir, g_snake_pos
    snake_cell_x, snake_cell_y = screenPosToCellPos(g_snake_pos[0], g_snake_pos[1]) #The function first calculates the coordinates of the snake's head by converting the snake's position in pixels to a cell index
    for body in g_snake_trace:
        cell_x, cell_y = screenPosToCellPos(body[0], body[1])
        # left
        if g_snake_dir == 180:
            if cell_x + 1 == snake_cell_x and cell_y == snake_cell_y:
                g_snake_movable = False #set to False to prevent the snake from moving in the same direction that caused the collision
        # right
        if g_snake_dir == 0:
            if cell_x - 1 == snake_cell_x and cell_y == snake_cell_y:
                g_snake_movable = False
        # up
        if g_snake_dir == 90:
            if cell_x == snake_cell_x and cell_y + 1 == snake_cell_y:
                g_snake_movable = False
        # down
        if g_snake_dir == 270:
            if cell_x == snake_cell_x and cell_y - 1 == snake_cell_y:
                g_snake_movable = False

#Checking whether the game is over based on whether the snake has eaten all the food on the screen.
def updateGameStatus():
    global g_is_game_over
    if g_food_in_stomach == 0:
        max_food = 0
        for row in g_food_matrix:
            max_food = max(max_food, max(row))
        if max_food == 0:
            g_is_game_over = True
            g_pen_gameover.up()
            g_pen_gameover.goto(g_snake_pos[0] + CELL_WIDTH, g_snake_pos[1])
            g_pen_gameover.down()
            g_pen_gameover.write(WIN_MSG, align='left', font=STATUS_FONT)

# Initialize the status bar of the game, as it sets up the position of the pens and draws some rectangles on the screen
def initStatus():
    g_pen_gameover.color('red')
    g_pen_for_contact.up()
    g_pen_for_contact.goto(-130, GAME_AREA_HEIGHT // 2 - 10)
    g_pen_for_contact.down()
    g_pen_for_motion.up()
    g_pen_for_motion.goto(165, GAME_AREA_HEIGHT // 2 - 10)
    g_pen_for_motion.down()
    g_pen_for_time.up()
    g_pen_for_time.goto(10, GAME_AREA_HEIGHT // 2 - 10)
    g_pen_for_time.down()
    g_pen.up()
    g_pen.goto(-250, 290)
    g_pen.down()
    rectangle(500, 80)
    g_pen.up()
    g_pen.goto(-250, 210)
    g_pen.down()
    rectangle(500, 500)
    g_pen.up()
    g_pen.goto(-230, 60)
    g_pen.down()
    g_status.clear()
    g_status.write(STATUS_BAR, font=STATUS_FONT)
    g_screen.update()

# Updates the game time status in the GUI.
def updateTimeStatus():
    global g_game_time
    if g_is_clicked:
        g_pen_for_time.clear()
        g_game_time += 1
        g_pen_for_time.write(str(g_game_time), font=FONT)
    else:
        g_pen_for_time.clear()
        g_pen_for_time.write(str(0), font=FONT)
    if not g_is_game_over:
        g_screen.ontimer(updateTimeStatus, 1000)

#Updates the contact status on the game screen.
def updateContactStatus():
    g_pen_for_contact.clear()
    g_pen_for_contact.write(str(g_num_contacts), font=FONT)
    g_screen.update()

#Updates the motion status of the snake in the game by displaying either the direction in which the snake is moving or the word "Paused" if the game is currently paused.
def updateMotionStatus():
    if not g_is_game_over:
        g_pen_for_motion.clear()
        if g_snake_movable and (
                not g_is_game_paused):
            if g_snake_dir == 0:
                g_pen_for_motion.write('Right', font=FONT)
            elif g_snake_dir == 90:
                g_pen_for_motion.write('Up', font=FONT)
            elif g_snake_dir == 180:
                g_pen_for_motion.write('Left', font=FONT)
            else:
                g_pen_for_motion.write('Down', font=FONT)
        else:
            g_pen_for_motion.write('Paused', font=FONT)
        g_screen.update()

#Controls the movement of the snake
def onTimerSnake(dist=20):
    global g_snake_length
    global g_is_snake_extending
    global g_snake_trace
    global g_food_in_stomach
    global g_snake_pos
    if (not g_is_game_over) and (not g_is_game_paused):
        if g_snake_movable:
            g_is_snake_extending = False
            if g_food_in_stomach > 0:
                g_is_snake_extending = True
                g_food_in_stomach -= 1
                g_snake_length += 1
            temp = g_snake.color()
            g_snake.color('blue', 'black')
            g_snake.stamp()
            g_snake.color(*temp)
            g_snake.forward(dist)
            g_snake_trace.append([g_snake_pos[0], g_snake_pos[1]])
            if not g_is_snake_extending:
                g_snake.clearstamps(1)
                g_snake_trace.pop(0)
            g_snake_pos[0], g_snake_pos[1] = round(g_snake.xcor()), round(g_snake.ycor())
            #print(g_snake_trace, g_snake_pos)
            eatFood()
            checkBoundary()
            updateGameStatus()
            g_screen.update()

    if not g_is_snake_extending:
        g_screen.ontimer(onTimerSnake, SNAKE_MOVE_RATE)
    else:
        g_screen.ontimer(onTimerSnake, SNAKE_SLOW_MOVE_RATE)

#Checks whether the monster has contact with the snake's body by comparing the monster's cell position with the cell positions of each body segment of the snake
def hasContactWithBody():
    global g_monster_pos, g_snake_trace
    monster_cell_x, monster_cell_y = screenPosToCellPos(g_monster_pos[0], g_monster_pos[1])
    for body in g_snake_trace:
        cell_x, cell_y = screenPosToCellPos(body[0], body[1])
        if monster_cell_x == cell_x and monster_cell_y == cell_y:
            return True
    return False

#Controls the movement of the monster on the screen
def onTimerMonster():
    global g_monster_pos, g_is_game_over, g_num_contacts
    snake_cell_x, snake_cell_y = screenPosToCellPos(g_snake_pos[0], g_snake_pos[1]) #first calculates the differences in the x and y coordinates between the monster's position (g_monster_pos) and the snake's position (g_snake_pos).
    if not g_is_game_over:
        x_difference = g_monster_pos[0] - g_snake_pos[0]
        y_difference = g_monster_pos[1] - g_snake_pos[1]
        if abs(x_difference) > abs(y_difference):
            if x_difference > 0:
                g_monster.setheading(180)
            else:
                g_monster.setheading(0)
        else:
            if y_difference > 0:
                g_monster.setheading(270)
            else:
                g_monster.setheading(90)
        g_monster.forward(CELL_WIDTH)
        g_monster_pos = [g_monster.xcor(), g_monster.ycor()]
        monster_cell_x, monster_cell_y = screenPosToCellPos(g_monster_pos[0], g_monster_pos[1])
        if monster_cell_x == snake_cell_x and monster_cell_y == snake_cell_y: #checks if the monster has collided with the snake.
            g_is_game_over = True
            g_pen_gameover.up()
            g_pen_gameover.goto(g_snake_pos[0] + CELL_WIDTH, g_snake_pos[1])
            g_pen_gameover.down()
            g_pen_gameover.write(LOSE_MSG, align='left', font=FONT)
            g_screen.update()
        else:
            if hasContactWithBody():
                g_num_contacts += 1
                updateContactStatus()
            g_screen.update()
            g_screen.ontimer(onTimerMonster, round(SNAKE_MOVE_RATE * (2 + random.random()))) #The function updates the screen and schedules the next invocation

#converts the given screen position (x,y) to cell position in the game grid.
def screenPosToCellPos(x, y):
    return (x + GAME_AREA_WIDTH // 2 - CELL_WIDTH // 2) // CELL_WIDTH, (
            CELL_HEIGHT // 2 + 180 + CELL_HEIGHT - y) // CELL_HEIGHT

#takes in the x and y positions of a cell in the game grid and returns the corresponding screen coordinates in pixels.
def cellPosToScreenPos(cell_x, cell_y):
    return cell_x * CELL_WIDTH + CELL_WIDTH // 2 - GAME_AREA_WIDTH // 2, 180 - cell_y * CELL_HEIGHT + CELL_HEIGHT // 2

#updates the positions and visibility of food items on the game board. 
def updateFood():
    g_pen_for_food.clear()
    for cell_x in range(N_CELL_X):
        for cell_y in range(N_CELL_Y):
            if g_food_matrix[cell_x][cell_y] > 0:
                if g_is_food_visible[g_food_matrix[cell_x][cell_y]]:
                    g_pen_for_food.up()
                    x, y = cellPosToScreenPos(cell_x, cell_y)
                    g_pen_for_food.goto(x, y)
                    g_pen_for_food.write(str(g_food_matrix[cell_x][cell_y]), align='left', font=FOOD_FONT)
    g_screen.update()

#checks if the snake has eaten any food.
def eatFood():
    global g_food_in_stomach, g_food_matrix, g_food_consumed, g_snake_pos
    cell_x, cell_y = screenPosToCellPos(g_snake_pos[0], g_snake_pos[1])
    if g_food_matrix[cell_x][cell_y] > 0:
        if g_is_food_visible[g_food_matrix[cell_x][cell_y]]:
            g_food_in_stomach += g_food_matrix[cell_x][cell_y]
            g_food_matrix[cell_x][cell_y] = 0
            g_food_consumed.append(g_food_matrix[cell_x][cell_y])
            updateFood()

#creates and returns a Turtle object with a square shape and a given position and color.
def createTurtle(x, y, color="red", border="black"):
    t = Turtle("square")
    t.color(border, color)
    t.up()
    t.goto(x, y)
    return t

#sets the heading of the snake based on the arrow key pressed.
def onArrowKeyPressed(key):
    setSnakeHeading(key)

#generates a random cell position within the bounds of the game area.
def generateRandomCellPos():
    cell_x = random.randint(0, N_CELL_X - 1)
    cell_y = random.randint(0, N_CELL_Y - 1)
    return cell_x, cell_y

#generating new food items at random intervals.
def onTimerFood():
    global g_is_food_visible, g_food_consumed
    while True:
        food_index = random.randint(1, NUM_FOODS)
        if food_index not in g_food_consumed:
            break
    # print(food_index, g_is_food_visible[food_index])
    g_is_food_visible[food_index] = not g_is_food_visible[food_index]
    updateFood()
    g_screen.ontimer(onTimerFood, 5000)

# initialize some global variables and set up various timers and click events.
def startGame(x, y):
    global g_is_snake_extending
    global g_food_matrix
    global g_snake_length
    global g_is_clicked
    global g_is_food_visible
    global g_food_in_stomach
    global g_food_consumed

    g_screen.onscreenclick(None)
    g_intro.clear()

    g_is_food_visible = {}

    g_screen.ontimer(onTimerSnake, SNAKE_MOVE_RATE)
    g_screen.ontimer(onTimerMonster, 1000)
    g_screen.ontimer(onTimerFood, 5000)

    g_food_in_stomach = 5
    g_is_clicked = True
    g_pen.undo()
    configureKey(g_screen)
    g_food_matrix = [[0 for col in range(N_CELL_Y)] for row in range(N_CELL_X)]
    snake_cell_x, snake_cell_y = screenPosToCellPos(g_snake_pos[0], g_snake_pos[1])
    g_food_consumed = []
    for i in range(NUM_FOODS):
        while True:
            cell_x, cell_y = generateRandomCellPos()
            if (g_food_matrix[cell_x][cell_y]) == 0 and not \
                    (cell_x == snake_cell_x and cell_y == snake_cell_y):
                g_food_matrix[cell_x][cell_y] = i + 1
                break
        g_is_food_visible[i + 1] = True
    updateFood()
    g_screen.onclick(None)

#defining global variables
def initPens():
    global g_pen, g_pen_gameover, g_pen_for_food, g_pen_for_status, g_pen_for_time, g_pen_for_contact, g_pen_for_motion

    g_pen = Turtle()
    g_pen.hideturtle()

    g_pen_for_food = Turtle()
    g_pen_for_food.hideturtle()

    g_pen_gameover = Turtle()
    g_pen_gameover.hideturtle()

    g_pen_for_status = Turtle()
    g_pen_for_status.hideturtle()

    g_pen_for_time = Turtle()
    g_pen_for_time.hideturtle()

    g_pen_for_contact = Turtle()
    g_pen_for_contact.hideturtle()

    g_pen_for_motion = Turtle()
    g_pen_for_motion.hideturtle()

#creates the turtle objects for the game play area, including the borders, the introduction message and the status message.
def configurePlayArea():
    # motion border
    m = createTurtle(0, 0, "", "black")
    m.shapesize(25, 25, 5)
    m.goto(0, -40)  # shift down half the status

    # status border
    s = createTurtle(0, 0, "", "black")
    s.shapesize(4, 25, 5)
    s.goto(0, 250)  # shift up half the motion

    # introduction
    intro = createTurtle(-200, 150)
    intro.hideturtle()
    intro.write(INTRO_MSG, font=("Arial", 16, "normal"))

    # statuses
    status = createTurtle(0, 0, "", "black")
    status.hideturtle()
    status.goto(-220, s.ycor() - 10)

    return intro, status

#returns a random position for the monster in the play area, but it checks that the position is at least SNAKE_MONSTER_INIT_MIN_DISTANCE cells away from the initial position of the snake.
def generateMonsterPos():
    snake_cell_x, snake_cell_y = screenPosToCellPos(0, 0)
    while True:
        cell_x, cell_y = generateRandomCellPos()
        if abs(cell_x - snake_cell_x) > SNAKE_MONSTER_INIT_MIN_DISTANCE and \
                abs(cell_y - snake_cell_y) > SNAKE_MONSTER_INIT_MIN_DISTANCE:
            return cell_x, cell_y

#initializes the game environment by setting up the screen, configuring the play area, initializing pens and status, and creating the snake and monster objects.
def initMonster():
    global g_monster
    monster_cell_x, monster_cell_y = generateMonsterPos()
    g_monster_pos[0], g_monster_pos[1] = cellPosToScreenPos(monster_cell_x, monster_cell_y)
    g_monster = createTurtle(g_monster_pos[0], g_monster_pos[1] - CELL_HEIGHT // 2, "purple", "black")


def initSnake():
    global g_snake, g_snake_pos
    snake_cell_x, snake_cell_y = 12, 10
    snake_x, snake_y = cellPosToScreenPos(snake_cell_x, snake_cell_y)
    g_snake_pos[0], g_snake_pos[1] = snake_x, snake_y - CELL_HEIGHT // 2
    g_snake = createTurtle(g_snake_pos[0], g_snake_pos[1], "red", "black")

#main code block that runs when the script is executed.
if __name__ == '__main__':
    g_screen = configScreen()
    g_intro, g_status = configurePlayArea()
    initPens()
    initStatus()
    updateTimeStatus()
    updateMotionStatus()
    updateContactStatus()
    initSnake()
    initMonster()
    g_screen.onscreenclick(startGame)
    g_screen.update()
    g_screen.listen()
    g_screen.mainloop()
