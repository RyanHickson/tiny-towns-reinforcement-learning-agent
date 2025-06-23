import numpy as np
import random as rdm
from building_layouts import *
from resources import *
from cards import *

# test_board = np.array([["B", "G", "B", "G"],
#                       ["W", "C", "W", "G"],
#                       ["S", "W", "C", "S"],
#                       ["S", "W", "B", "C"]])

test_board = np.array([[wheat, wild, brick, glass],
                      [brick, wild, brick, wild],
                      [wild, wild, wild, wild],
                      [wild, wild, wild, wild]])

empty_board = np.full((4,4), emptyTile)

random_board = np.full((4,4), emptyTile)

for i in range(4):
    for j in range(4):
        random_board[(i,j)] = rdm.choice(resource_types).get_name()

class Player:
    def __init__(self, player_id, monument):
        self.player_id = player_id
        self.monument = monument
        self.board = empty_board

        # self._board = np.full((4,4), "", dtype=str)

    def describe_player(self):
        return f"Player {self.get_id()} has the current _board: \n {self.show_board()} \n Their monument this game is {self.monument.get_name()}"
    
    def get_id(self):
        return self.player_id
    
    def describe_town_board(self):
        self.town_boardDict = {}
        for row in range(4):
            for tile in range(4):
                self.town_boardDict[row, tile] = self.board[row, tile]   # .getName()
        return self.town_boardDict
    
    def show_board(self):
        self.town_board = np.full((4,4), emptyTile)
        self.town_boardDict = self.describe_town_board()
        for row in range(4):
            for col in range(4):
                self.town_board[row, col] = self.town_boardDict[row, col].get_name()
        return self.town_board