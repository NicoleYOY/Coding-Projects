import math
import random

# Constants
# This section defines various messages and prompts that the user will see during the game
prompt_set_size = 'Please specify the size of the puzzle (8 or 15): '
prompt_set_input = 'Please choose the key for {}: '
prompt_move = 'Please enter your move ({}): '
error_invalid_input = 'Invalid input, please retry.'
welcome_msg = 'Hi, there! Welcome to Yingrun\'s puzzle game! By repeatedly re-arrange and moving the tiles into a sequential order, you would have a ordered game board. Are you ready?'
win_msg = 'Congratulations! You solved the puzzle in {} moves.'
play_again_or_leave_msg = 'Enter "1" for 8-puzzle, "2" for 15-puzzle or "q" to end the puzzle: '
thanks_msg = 'Thanks for playing!'

# These are lists and dictionaries used for the game
dirs = ['up', 'down', 'left', 'right'] # possible directions
sizes = [8, 15] # possible puzzle sizes
dir_key = {} # mapping between directions and keys
key_dir = {} # mapping between keys and directions

# This function is called at the beginning of the game and displays a welcome message
def welcome():
    print(welcome_msg)

# This function prompts the user to set their own keys for each direction
def set_input():
    for dir in dirs:
        print(prompt_set_input.format(dir))
        while True:
            key = input().strip().lower()
            # Ensure that the key is one alphanumeric character and not already used for a different direction
            if len(key) != 1 or not key.isalnum() or (key in dir_key.values()):
                print(error_invalid_input)
            else:
                dir_key[dir] = key
                key_dir[key] = dir
                break

# This function checks if the puzzle is solved by comparing the current state of the board with the expected solution
def is_solved(board):
    size = len(board)
    ans = [[j * size + i + 1 for i in range(size)] for j in range(size)]
    ans[-1][-1] = ''
    if board == ans:
        return True
    return False

# This function randomizes the board by performing a number of random moves
def randomize_board(board):
    num_moves = random.randint(30, 50) # randomly choose a number of moves to perform
    row = col = len(board) - 1 # start with the empty tile in the bottom-right corner
    for i in range(num_moves):
        valid_moves = get_valid_moves(board, row, col) # get the possible moves for the current position
        move = random.choice(valid_moves) # randomly choose one of the valid moves
        row, col = move_tile(board, row, col, move) # move the tile in the chosen direction
    # If the board happens to be solved after randomizing, randomize again
    if is_solved(board):
        randomize_board(board)
    return row, col

# This function gets user input for the next move and validates it
def get_user_input(valid_dirs):
    while True:
        move = input(prompt_move.format(
            ', '.join(["{}-{}".format(d, dir_key[d]) for d in valid_dirs]))).strip().lower()
        if move in [dir_key[d] for d in valid_dirs]: # If the input is a valid key for one of the valid directions
            return key_dir[move] # Return the corresponding direction
        elif move == '-': # Set a backdoor to easily test the code
            return False
        else:
            print(error_invalid_input)

#This function takes a 2D list representing the game board and prints it in a user-friendly format.
def print_board(board):
    for row in board:
        for num in row:
            print("{:3}".format(num), end=" ")
        print()

def move_tile(board, row, col, dir):
    # This function moves the tile in the given direction by swapping the tile's position with an adjacent empty space
    # board: the current state of the board
    # row: the row index of the tile to be moved
    # col: the column index of the tile to be moved
    # dir: the direction in which to move the tile (up, down, left, or right)
    # returns the new row and column index of the moved tile
    
    # Check the direction and swap the tile with the adjacent empty space
    if dir == dirs[3]:
        board[row][col], board[row][col - 1] = board[row][col - 1], board[row][col]
        col -= 1
    elif dir == dirs[2]:
        board[row][col], board[row][col + 1] = board[row][col + 1], board[row][col]
        col += 1
    elif dir == dirs[1]:
        board[row][col], board[row - 1][col] = board[row - 1][col], board[row][col]
        row -= 1
    elif dir == dirs[0]:
        board[row][col], board[row + 1][col] = board[row + 1][col], board[row][col]
        row += 1
    return row, col


def get_board_size():
    # This function gets the desired board size from the user and returns the corresponding matrix size
    # returns the matrix size
    
    while True:
        # Ask the user for the board size
        size = int(input(prompt_set_size).strip().lower())
        # Check if the size is valid and return the corresponding matrix size
        if size in sizes:
            return int(math.sqrt(size + 1))
        else:
            print(error_invalid_input)


def get_valid_moves(board, row, col):
    # This function gets all the valid moves for a given tile on the board
    # board: the current state of the board
    # row: the row index of the tile for which to get valid moves
    # col: the column index of the tile for which to get valid moves
    # returns a list of valid moves for the tile
    
    size = len(board)
    moves = []
    # Check if moving up is valid
    if row > 0:
        moves.append(dirs[1])
    # Check if moving down is valid
    if row < size - 1:
        moves.append(dirs[0])
    # Check if moving left is valid
    if col > 0:
        moves.append(dirs[3])
    # Check if moving right is valid
    if col < size - 1:
        moves.append(dirs[2])
    return moves


def game(size):
    # This function runs the main game loop.
    while True:
        board = [[j * size + i + 1 for i in range(size)] for j in range(size)] # Creates a new board of the specified size
        board[-1][-1] = '' # Sets the bottom-right tile as the empty tile
        row, col = randomize_board(board) # Randomizes the board and gets the position of the empty tile
        print_board(board) # Prints the initial state of the board
        count = 0 # Initializes the move counter to 0
        while not is_solved(board): # Loops until the board is solved
            valid_moves = get_valid_moves(board, row, col) # Gets the valid moves for the current state of the board
            move = get_user_input(valid_moves) # Prompts the user to make a move and gets their input
            if not move: # If the user enters an empty input, they have chosen to quit the game
                break
            row, col = move_tile(board, row, col, move) # Moves the empty tile in the chosen direction and gets its new position
            count += 1 # Increments the move counter
            print_board(board) # Prints the new state of the board
        print(win_msg.format(count)) # Prints the winning message with the move count
        while True: # Loops until the user chooses to quit or play again with a new board size
            choice = input(play_again_or_leave_msg) # Prompts the user to choose whether to play again with the same board size, play again with a new board size, or quit
            if choice.lower() == 'q': # If the user chooses to quit, the game ends
                print(thanks_msg)
                return
            elif choice.lower() == '1': # If the user chooses to play again with a 8-puzzle game
                size = 3
                break
            elif choice.lower() == '2': # If the user chooses to play again with a 15-puzzle game
                size = 4
                break
            else:
                print(error_invalid_input)


def main():
    #This function is the entry point of the program. It calls the other functions in the correct order to start the game.
    welcome()
    set_input()
    size = get_board_size()
    game(size)

main()