import turtle
import numpy as np
import time
import threading

# Constants
BOARD_SIZE = 8
CELL_SIZE = 60
OUTLINE_SIZE = 60
TOKEN_SIZE = 45
COLUMN_TRACKER_HEIGHT = 10
TOKEN_PLACEHOLDER_HEIGHT = 18
TOKEN_PLACEHOLDER_WIDTH = 55
COLUMN_TRACKER_WIDTH = 45
COLUMN_TRACKER_Y_BOTTOM = 5
BOARD_Y_BOTTOM = COLUMN_TRACKER_Y_BOTTOM + TOKEN_PLACEHOLDER_HEIGHT/2.0
TOKEN_COLORS = ('blue', 'purple')
OUTLINE_COLOR = 'orange'
COLUMN_TRACKER_COLOR = 'black'
WINNER_OUTLINE_COLOR = 'red'
BOARD_COLOR = 'gray'
BG_COLOR = 'white'


def draw_square(x, y, size, color):
    turtle.goto(x, y)
    turtle.begin_fill()
    turtle.fillcolor(color)
    for _ in range(4):
        turtle.forward(size)
        turtle.right(90)
    turtle.end_fill()


def draw_rect(x, y, height, width, color):
    turtle.goto(x, y)
    turtle.begin_fill()
    turtle.fillcolor(color)
    length = [width, height]
    for i in range(4):
        turtle.forward(length[i % 2])
        turtle.right(90)
    turtle.end_fill()


def draw_circle(color, x, y, size):
    turtle.penup()
    turtle.goto(x, y)
    turtle.dot(size, color)


def draw_token(color, row, col, size, interval):
    draw_circle(color, col * interval + interval/2.0, row * interval + interval/2.0 + BOARD_Y_BOTTOM, size)


def draw_board():
    turtle.speed(0)
    turtle.hideturtle()
    turtle.penup()
    for y in range(BOARD_SIZE):
        draw_column_tracker(y, COLUMN_TRACKER_HEIGHT, COLUMN_TRACKER_WIDTH, COLUMN_TRACKER_COLOR)
        for x in range(BOARD_SIZE):
            draw_square((x+0.05) * CELL_SIZE, (y+0.95) * CELL_SIZE + COLUMN_TRACKER_Y_BOTTOM
                        + TOKEN_PLACEHOLDER_HEIGHT / 2.0, CELL_SIZE * 0.9, BOARD_COLOR)


def update_board(board, player, col):
    for row in range(BOARD_SIZE):
        if board[row][col] == 0:
            board[row][col] = player
            color = TOKEN_COLORS[player - 1]
            draw_token(color, row, col, TOKEN_SIZE, CELL_SIZE)
            break


def draw_column_tracker(col, height, width, color):
    draw_rect(col * CELL_SIZE + (CELL_SIZE-width) / 2.0,
              COLUMN_TRACKER_Y_BOTTOM + height / 2.0, height, width, color)


def check_winner(board, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                for dr, dc in directions:
                    tokens = is_connected(board, player, row, col, dr, dc)
                    if tokens:
                        return tokens
    return None


def is_connected(board, player, row, col, dr, dc):
    tokens = []
    for _ in range(4):
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE or board[row][col] != player:
            return None
        tokens.append((row, col))
        row += dr
        col += dc
    return tokens


def outline_winner_tokens(tokens, player):
    player_color = TOKEN_COLORS[player - 1]
    for row, col in tokens:
        draw_token(OUTLINE_COLOR, row, col, OUTLINE_SIZE, CELL_SIZE)
        draw_token(player_color, row, col, TOKEN_SIZE, CELL_SIZE)


def mouse_move(x, y):
    global current_col
    col = x // CELL_SIZE
    if 0 <= col < BOARD_SIZE:
        if current_col != col:
            draw_column_tracker(col, TOKEN_PLACEHOLDER_HEIGHT, TOKEN_PLACEHOLDER_WIDTH, TOKEN_COLORS[current_player - 1])
            draw_column_tracker(col, COLUMN_TRACKER_HEIGHT, COLUMN_TRACKER_WIDTH, COLUMN_TRACKER_COLOR)
            if current_col != -1:
                draw_column_tracker(current_col, TOKEN_PLACEHOLDER_HEIGHT * 1.1, CELL_SIZE, BG_COLOR)
                draw_column_tracker(current_col, COLUMN_TRACKER_HEIGHT, COLUMN_TRACKER_WIDTH, COLUMN_TRACKER_COLOR)
            current_col = col


def mouse_click(x, y):
    global current_player, moves, game_state

    if not game_state:
        return

    x -= CELL_SIZE // 2
    if 0 <= current_col < BOARD_SIZE:
        if np.count_nonzero(board[:, current_col]) < BOARD_SIZE:
            update_board(board, current_player, current_col)
            winner_tokens = check_winner(board, current_player)
            if winner_tokens:
                turtle.title(f'Winner! Player {current_player}. Press Enter to restart')
                outline_winner_tokens(winner_tokens, current_player)
                game_state = False
                return
            moves += 1
            print(moves)
            if moves == BOARD_SIZE * BOARD_SIZE:
                turtle.title('Game Tied! Press Enter to restart')
                game_state = False
                return
            current_player = 3 - current_player
            turtle.title(f'Connect 4 - Player {current_player} Turn')
            draw_column_tracker(current_col, TOKEN_PLACEHOLDER_HEIGHT, TOKEN_PLACEHOLDER_WIDTH, TOKEN_COLORS[current_player - 1])
            draw_column_tracker(current_col, COLUMN_TRACKER_HEIGHT, COLUMN_TRACKER_WIDTH, COLUMN_TRACKER_COLOR)


def get_mouse_pos():
    return screen.getcanvas().winfo_pointerx() - screen.getcanvas().winfo_rootx(), screen.getcanvas().winfo_pointery() - screen.getcanvas().winfo_rooty()


def track_mouse_position():
    while True:
        x, y = get_mouse_pos()
        win_x, win_y = screen.screensize()
        if 0 <= x <= win_x and 0 <= y <= win_y:
            x -= CELL_SIZE // 2
            mouse_move(x, y)
        time.sleep(0.1)


def restart():
    global game_state, current_player, current_col, board, moves, screen
    game_state = True
    current_player = 1
    current_col = -1
    moves = 0
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    draw_board()
    screen.title(f'Connect 4 - Player {current_player} Turn')


# Initialize the game
game_state = True
current_player = 1
current_col = -1
moves = 0
board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

# Set up the turtle screen
screen = turtle.Screen()
screen.title(f'Connect 4 - Player {current_player} Turn')
screen.setup(BOARD_SIZE * CELL_SIZE + 2 * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 3 * CELL_SIZE)
screen.setworldcoordinates(0, 0, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 2 * COLUMN_TRACKER_HEIGHT)
screen.bgcolor(BG_COLOR)
screen.tracer(0)

# Draw the board
draw_board()

# Set up mouse and keyboard events
screen.listen()
mouse_tracker = threading.Thread(target=track_mouse_position)
mouse_tracker.daemon = True
mouse_tracker.start()
screen.onclick(mouse_click, btn=1, add=True)
screen.onkey(restart, 'Return')

# Start the game loop
turtle.mainloop()