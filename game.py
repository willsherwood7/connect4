#board is 6 arrays of 7: {[7],[7]...}
# [0][0] is top left [5][6] is bottom right
import numpy as np
import random

import ai

board = np.zeros((6, 7), dtype=int)

def check_win(col):
    #calls check_win2 on board
    team = whos_turn()
    return check_win2(team, col, board)

def check_win2 (team, col, board2):
    # Ensure col is an integer
    col = int(col)
    #sees if this move will win the game
    #returns true if they win

    row = find_open_row(col, board2)
    board_copy = np.copy(board2)

    # Simulate the move on the copied board
    board_copy[row][col] = team

    # Check horizontally
    for c in range(col - 3, col + 1):
        if 0 <= c <= 3 and all(board_copy[row][c + i] == team for i in range(4)):
            return True

    # Check vertically
    for r in range(row - 3, row + 1):
        if 0 <= r <= 2 and all(board_copy[r + i][col] == team for i in range(4)):
            return True

    # Check diagonally (top-left to bottom-right)
    for i in range(-3, 1):
        if 0 <= row + i <= 2 and 0 <= col + i <= 3 and all(board_copy[row + i + j][col + i + j] == team for j in range(4)):
            return True

    # Check diagonally (bottom-left to top-right)
    for i in range(-3, 1):
        if 3 <= row - i <= 5 and 0 <= col + i <= 3 and all(board_copy[row - i - j][col + i + j] == team for j in range(4)):
            return True

    return False

def check_bot_won ():
    return check_won(2, board)

def check_won (team, board2):
    #checks if bot won
    # Check horizontally
    for row in range(6):
        for col in range(4):
            if all(board2[row][col + i] == team for i in range(4)):
                return True

    # Check vertically
    for row in range(3):
        for col in range(7):
            if all(board2[row + i][col] == team for i in range(4)):
                return True

    # Check diagonally (top-left to bottom-right)
    for row in range(3):
        for col in range(4):
            if all(board2[row + i][col + i] == team for i in range(4)):
                return True

    # Check diagonally (bottom-left to top-right)
    for row in range(3, 6):
        for col in range(4):
            if all(board2[row - i][col + i] == team for i in range(4)):
                return True
    return False

def check_move(col):
    #calls check_move2 on board
    return check_move2(col, board)

def check_move2 (col, board2):
    # Ensure col is an integer
    col = int(col)
    #checks if a certain column is full or if they can go there
    # returns true if valid move
    return board2[0][col] == 0

def find_open_row (col, board2):
    # returns first empty row
    for row in range(5, -1, -1):
        if board2[row][col] == 0:
            return row
    return -1

def make_move(col):
    #calls make_move2 on board
    team = whos_turn()
    return make_move2(col, team, board)

def make_move2 (col, team, board2):
    # Ensure col is an integer
    col = int(col)
    # puts new piece on the board
    # returns board
    open_row = find_open_row(col, board2)
    board2[open_row][col] = team
    return board2

def start_game ():
    #fill board with 0s
    for i in range(6):
        for j in range(7):
            board[i][j] = 0

def check_started ():
    #check if any pieces on board
    #return true if game started
    for i in range(6):
        for j in range(7):
            if not board[i][j] == 0:
                return True
    return False

def check_tied ():
    for i in range(7):
        if check_move(i):
            return False
    return not check_bot_won()

def whos_turn ():
    #return 1 or 2 of whos turn it is
    count = 0
    for i in range(6):
        for j in range(7):
            if board[i][j] == 1:
                count += 1
            elif board[i][j] == 2:
                count -= 1
    if count == 0:
        return 1
    return 2

def make_bot_move (difficulty):
    #call make_move2 function using bots
    #return board
    # Ensure difficulty is an integer
    difficulty = int(difficulty)
    if difficulty == 1:
        make_move2(easy_bot_move(), 2, board)
    elif difficulty == 2:
        make_move2(medium_bot_move(), 2, board)
    elif difficulty == 3:
        make_move2(hard_bot_move(), 2, board)
    elif difficulty == 4:
        make_move2(insane_bot_move(), 2, board)
    return board

def easy_bot_move ():
    #return spot to move
    valid_moves = get_valid_moves(board)
    return random.choice(valid_moves)

def medium_bot_move ():
    #sees if it can win anywhere and goes there if it can
    #sees if other player can win anywhere and blocks if they can
    #will not go somewhere if opponenet can win above it
    #moves random otherwise and returns move
    for col in get_valid_moves(board):
        if check_win2(2, col, board):
            return col

    for col in get_valid_moves(board):
        if check_win2(1, col, board):
            return col

    good_moves = []
    for col in get_valid_moves(board):
        board_copy = np.copy(board)
        make_move2(col, 2, board_copy)
        if not check_win2(1, col, board_copy):
            good_moves.append(col)

    if len(good_moves) == 0:
        return easy_bot_move()
    return random.choice(good_moves)


def hard_bot_move ():
    #does everything medium bot can
    #also generally tries to move near other pieces and the middle with some randomness

    for col in get_valid_moves(board):
        if check_win2(2, col, board):
            return col

    for col in get_valid_moves(board):
        if check_win2(1, col, board):
            return col

    good_moves = []
    for col in get_valid_moves(board):
        board_copy = np.copy(board)
        make_move2(col, 2, board_copy)
        if not check_win2(1, col, board_copy):
            good_moves.append(col)

    if len(good_moves) == 0:
        return easy_bot_move()

    #the simplest way for someone to beat this bot is to get 3 in a row on the bottom with nothing on either side
    #this is usually blocked by chance but this code below prevents this strategy
    #it makes sure blocking is a good move though
    if board[5][3] == 1 and board[5][2] == 1 and board[5][1] == 0 and board[5][4] == 0 and 4 in good_moves:
        return 4
    elif board[5][3] == 1 and board[5][4] == 1 and board[5][5] == 0 and board[5][2] == 0 and 2 in good_moves:
        return 2
    elif board[5][1] == 1 and board[5][2] == 1 and board[5][0] == 0 and board[5][3] == 0 and 3 in good_moves:
        return 3
    elif board[5][5] == 1 and board[5][4] == 1 and board[5][6] == 0 and board[5][3] == 0 and 3 in good_moves:
        return 3

    #calculates how good certain moves are based on closeness to middle and how many other pieces it touches
    good_moves_2 = []
    for col in range(0, 7):
        if col in good_moves:
            value = 0
            #adds points for closeness to middle
            value += 3 - abs(3 - col)

            #adds point per peice that will touch location
            row = find_open_row (col, board)
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= col + i <= 6 and 0 <= row + j <= 5 and (board[row + j][col + i] == 1 or board[row + j][col + i] == 2):
                        value += 1
            good_moves_2.append(value)
        else:
            good_moves_2.append(-1)
    #finds max value in array and randomly chooses any column with points at least one less than it
    #this makes the move quite good but also a bit random
    threshold = max(good_moves_2) - 1
    options = []
    for col in range(0, 7):
        if good_moves_2[col] >= threshold:
            options.append(col)
    return random.choice(options)


def insane_bot_move():
    flipped_board = np.flipud(board)
    col, minimax_score = ai.minimax(flipped_board, 5, -9999999, 9999999, True)
    return col

def get_valid_moves(board):
    return [col for col in range(7) if board[0][col] == 0]

def update_elo(player1_elo, player2_elo, games_played, result):
    #returns change in player 1 elo
    #games become less and less impactful until 10 games
    #players gain more from playing higher elo players
    #result is -1, 0, or 1
    multiplier = max(11 - games_played, 1)
    difference = (player1_elo - player2_elo) // 100
    if difference < 0 and result == 1:
        difference += 1
    if result == 1:
        return multiplier * (10 - difference)
    elif result == -1:
        return -(multiplier * (10 + difference))
    else:
        return - (multiplier * difference)

def get_board():
    return board

# # #testing
# # print(board)
# make_move (6)
# make_bot_move (4)
# print(board)
# make_move (6)
# make_bot_move (4)
# print(board)
# make_move (6)
# make_bot_move (4)
# print(board)
# make_move (6)
# make_bot_move (4)
# print(board)
# make_move (3)
# make_bot_move (4)
# print(board)
# print(check_bot_won())
# print(check_win(3))
# print(check_move(1))
# make_move (2)
# make_move (3)
# print(board)
# make_move (3)
# # print(check_win(3))
# make_move (2)
# print(board)
# print(check_win(3))
# make_move (3)
# print(board)
# make_bot_move (1)
# make_move (2)
# make_bot_move (1)
# print(board)
# make_move (4)
# make_bot_move (2)
# print(board)
# start_game()
# print(board)
# print(update_elo(900, 1150, 9, 1))
# print(update_elo(1150, 900, 9, -1))
# print(update_elo(1050, 1150, 13, -1))
# print(update_elo(1150, 1050, 97, 1))
# print(update_elo(1150, 1050, 97, 0))
