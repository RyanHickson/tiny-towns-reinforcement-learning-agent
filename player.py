import numpy as np
import random as rdm
from buildingLayouts import *
from resources import *

# testBoard = np.array([["B", "G", "B", "G"],
#                       ["W", "C", "W", "G"],
#                       ["S", "W", "C", "S"],
#                       ["S", "W", "B", "C"]])

testBoard = np.array([['wheat', 'glass', 'brick', 'glass'],
                      ['brick', 'wild', 'brick', 'wood'],
                      ['brick', 'wheat', 'wild', 'brick'],
                      ['wood', 'brick', 'brick', 'wood']])

randomBoard = np.full((4,4), emptyTile)
resouceCodes = [" ", "W", "C", "B", "G", "S"]

for i in range(4):
    for j in range(4):
        randomBoard[(i,j)] = rdm.choice(resourceTypes).getName()

class Player:
    def __init__(self, playerID, monument):
        self.playerID = playerID
        self.monument = monument
        self.board = testBoard

        # self.board = np.full((4,4), "", dtype=str)

    def describePlayer(self):
        return f"Player {self.playerID} has the current board: \n {self.board} \n Their monument this game is {self.monument.getName()}"
    
    def describeTownBoard(self):
        self.townBoardDict = {}
        for row in range(4):
            for tile in range(4):
                self.townBoardDict[row, tile] = self.board[row, tile]
        return self.townBoardDict