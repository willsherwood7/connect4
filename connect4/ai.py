# This algorithm comes from https://roboticsproject.readthedocs.io/en/latest/ConnectFourAlgorithm.html
# We converted our game mechanics to a board that in can read and analyze
# This algorithm is used for the insane bot

import numpy as np
import random

# Set player values for turn counter
PLAYER = 0
BOT = 1

# Set values for rows and cols
ROW_COUNT = 6
COLUMN_COUNT = 7

# Set player piece values for board placement
PLAYER_PIECE = 1
BOT_PIECE = 2
EMPTY = 0

# Trying to connect 4 so search for places that fit 4 tokens
WINDOW_LENGTH = 4

# Set game algorithm difficulty (number of moves it looks ahead)
DEPTH = 4 # A higher value takes longer to run

# It’s important to understand that the algorithm fills the board from the top down different from real life
# np.flipud(board) flips the board around a horizontal axis, making it the correct visual orientation for Connect 4
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

# Initialise game
board = create_board()

# get all locations in the board that could contain a piece (i.e. have not yet been filled)
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


# check if there is a valid location in the chosen column
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


# check which row the piece can be placed into (i.e. the next available open row)
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


# place a piece in the next available row, in the chosen column
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# evaluate a move for how good it is and being offensive and defensive
def score_position(board, piece):
    score = 0

    # Score centre column
    centre_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    centre_count = centre_array.count(piece)
    score += centre_count * 3

    # Score horizontal positions
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            # Create a horizontal window of 4
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score vertical positions
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            # Create a vertical window of 4
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a positive diagonal window of 4
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negative diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a negative diagonal window of 4
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


# evaluate each available win spot to see if a move is good at connecting pieces or blocking
# These were the numbers that we developed over a number of rounds playing the CPU, trying to make it as difficult as possible
def evaluate_window(window, piece):
    score = 0
    # Switch scoring based on turn
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = BOT_PIECE

    # Prioritise a winning move
    # Minimax makes this less important
    if window.count(piece) == 4:
        score += 100000
    # Make connecting 3 second priority
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 100
    # Make connecting 2 third priority
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 20
    # Prioritise blocking an opponent's winning move (but not over bot winning)
    # Minimax makes this less important
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 200

    return score


# see if a win has occurred
def winning_move(board, piece):
    # Check valid horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check valid vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check valid positive diagonal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # check valid negative diagonal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


# used in the decision tree, this sees if a particular game state has ended the game
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0

# this is the minimax algorithm
# the board is the current game state, the depth is how many moves ahead we are looking at
def minimax(board, depth, alpha, beta, maximisingPlayer):
    valid_locations = get_valid_locations(board)

    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            # Weight the bot winning really high
            if winning_move(board, BOT_PIECE):
                return (None, 9999999)
            # Weight the human winning really low
            elif winning_move(board, PLAYER_PIECE):
                return (None, -9999999)
            else:  # No more valid moves
                return (None, 0)
        # Return the bot's score
        else:
            return (None, score_position(board, BOT_PIECE))

    if maximisingPlayer:
        value = -9999999
        # Randomise column to start
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            # Create a copy of the board
            b_copy = board.copy()
            # Drop a piece in the temporary board and record score
            drop_piece(b_copy, row, col, BOT_PIECE)
            if winning_move(b_copy, BOT_PIECE):
                return (col, 9999999)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimising player
        value = 9999999
        # Randomise column to start
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            # Create a copy of the board
            b_copy = board.copy()
            # Drop a piece in the temporary board and record score
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


# To get the minimaxed move, we do col, minimax_score = minimax.minimax(board, 5, -9999999, 9999999, True)
# Maximizing player is true so that it makes the best move for itself
