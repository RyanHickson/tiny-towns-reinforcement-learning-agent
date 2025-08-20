import hashlib
import numpy as np
from resources import *

def stable_hash(value):
    return hashlib.md5(value.encode()).hexdigest()

board = np.full((4,4), empty)

def get_board_hash(board):
    board_str = []
    for row in board:
        row_str = []
        for el in row:
            row_str.append(el.__str__())
        board_str.append(str(row_str))
    board_str = str(board_str)
    print(board_str)
    return stable_hash(board_str)

print(get_board_hash(board))