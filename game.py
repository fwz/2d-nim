# -*- encoding: utf8 -*-
import copy
import sys
from random import randint

""" A Board is like
0000
0000
0100
0001

1 means pickable
0 means non-pickable
"""


def num2binary(num):
    return "{0:016b}".format(num)


def binary2num(binary):
    return int(binary, 2)


def num2board(num):
    step = 4
    board_num = num2binary(num)
    board = [board_num[i:i + step] for i in xrange(0, len(board_num), step)]
    res = [[int(r[i]) for i in xrange(len(r))] for r in board]
    return res


def board2num(board):
    res = ""
    for r in board:
        res += "".join(str(x) for x in r)
    return binary2num(res)


def print_board(board, diff=False):
    print "----"
    for b in board:
        print "".join(("X" if (x == 1) else ".") if diff else str(x) for x in b)
    print "----\n"


def find_all_adj_board(board, next_flag=0):
    """
    :param board: the 4*4 int board
    :param next_flag: if next_flag = 1, then find all next boards
    :return: all adjacent board
    """

    for r in xrange(4):
        for c in xrange(4):
            if board[r][c] == 1 ^ next_flag:
                continue
            else:
                # right
                nb = copy.deepcopy(board)
                for j in range(c, min(4, c + 3)):
                    if board[r][j] == 0 ^ next_flag:
                        nb[r][j] = 1 ^ next_flag
                        yield nb, board2num(nb)
                    else:
                        break

                # down
                nb = copy.deepcopy(board)
                for i in range(r, min(4, r + 3)):
                    if i == r:
                        nb[r][c] = 1 ^ next_flag
                        continue  # single pick contained in right operation
                    if board[i][c] == 0 ^ next_flag:
                        nb[i][c] = 1 ^ next_flag
                        yield nb, board2num(nb)
                    else:
                        break


def find_winning_scene():
    """
    lose_set mean first hand must lose
    win_set mean first hand MUST win
    """

    lose_set = set()
    win_set = set()

    # init
    win_set.add(0)

    # start calc
    for i in range(1, 65536):
        flag = True

        # if all next step of current board is a win board, current board lose
        for b, n in find_all_adj_board(num2board(i), 1):
            if n not in win_set:
                flag = False
                break
        if flag:
            lose_set.add(i)
        else:
            # must be win or lose anyway
            win_set.add(i)

    print "win_set size: " + str(len(win_set))
    print "lose_set size: " + str(len(lose_set))

    return win_set, lose_set


def pre_process():
    w, l = find_winning_scene()

    win_board = list(w)
    win_board.sort()

    with open("strategy.txt", "w") as fp:
        for b in win_board:
            fp.write(str(b) + "\n")


def load_strategy():
    win_board = set()
    lose_board = set()
    with open("strategy.txt", "r") as fp:
        for l in fp.readlines():
            win_board.add(int(l.strip()))

    for i in range(65536):
        if i not in win_board:
            lose_board.add(i)

    return win_board, lose_board


def game():
    #pre_process()
    w, l = load_strategy()

    player_first = raw_input("Player first? (Y/N) : ").strip().lower() == "y"

    board = num2board(65535)

    player_should_move = player_first

    while board2num(board) != 0:
        try:
            board = move(board, l, player_should_move)
            print "Current Board:"
            print_board(board)
            player_should_move = not player_should_move
        except ValueError as e:
            print sys.exc_info()
            continue

    if player_should_move:
        print "Player Win!! Incredible!"
    else:
        print "Player Lose!! Try again?"


def move(board, l, player_should_move=True):
    if player_should_move:
        return player_move(board)
    else:
        return cpu_move(board, l)



def cpu_move(board, l):
    print "CPU is removing: "
    choice = []
    next_steps = [(b, n) for b, n in find_all_adj_board(board, next_flag=1)]

    for (b, n) in next_steps:
        if n in l:
            choice.append(n)

    nn = -1

    if not choice:
        nn = next_steps[randint(0, len(next_steps) - 1)][1]
    else:
        nn = choice[randint(0, len(choice) - 1)]

    diff = board2num(board) ^ nn
    print_board(num2board(diff), True)
    board = num2board(nn)
    return board


def player_move(board):
    print "Player's turn:"

    s_row, s_col = [int(k) for k in raw_input("input start position (row,col):").split(",")]
    e_row, e_col = [int(k) for k in raw_input("input end position (row,col):").split(",")]

    if s_row == e_row:
        direction = "right"
        length = e_col - s_col + 1

    elif s_col == e_col:
        direction = "down"
        length = e_row - s_row + 1
    else:
        raise ValueError("input not valid")

    valid = True

    if direction == "r" or direction == "right":
        for i in range(0, min(length, 3)):
            if s_col + i > 3 or board[s_row][s_col + i] == 0:
                valid = False
                break

        if not valid:
            raise ValueError("input not valid!")

        for i in range(0, min(length, 3)):
            board[s_row][s_col + i] = 0

    elif direction == "d" or direction == "down":
        for i in range(0, min(length, 3)):
            if s_row + i > 3 or board[s_row + i][s_col] == 0:
                valid = False
                break

        if not valid:
            raise ValueError("input not valid!")

        for i in range(0, min(length, 3)):
            board[s_row + i][s_col] = 0

    return board


def print_rules():
    rules = \
    """
    * There are 16 stones, arranged in 4 row * 4 column grid
    * Each player take stones in turn
    * once the stone is taken, there is a gap on it's original location on the grid
    * In each take, one should take no more than 3 stones (1/2/3). Only those in the same row or in the same column without gap between them could be taken.
    * Player who takes the last stone *LOSE*

    As mentioned, it's a 4*4 grid. Assuming `1` means there is stone on the specific cell and `0` represent a gap in the following chart.

    * the opening could be represented as (I)
    * the ending could be represented as (II)
    * one of the losing situation (LS) for current turn player could be represented as (III)

    ```
    1111   0000   0000
    1111   0000   0000
    1111   0000   0010
    1111   0000   0000
    (I)    (II)   (III)
    ```

    """
    print rules

if __name__ == "__main__":
    print_rules()
    game()
