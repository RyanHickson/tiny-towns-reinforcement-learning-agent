import numpy as np
import random as rdm
from buildingLayouts import *
from resources import *

# testBoard = np.array([["B", "G", "B", "G"],
#                       ["W", "C", "W", "G"],
#                       ["S", "W", "C", "S"],
#                       ["S", "W", "B", "C"]])

testBoard = np.array([[wheat, wild, brick, glass],
                      [brick, wild, brick, wild],
                      [wild, wild, wild, wild],
                      [wood, wild, wild, wild]])

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
        return f"Player {self.getID()} has the current board: \n {self.showBoard()} \n Their monument this game is {self.monument.getName()}"
    
    def getID(self):
        return self.playerID
    
    def describeTownBoard(self):
        self.townBoardDict = {}
        for row in range(4):
            for tile in range(4):
                self.townBoardDict[row, tile] = self.board[row, tile].getName()
        return self.townBoardDict
    
    def showBoard(self):
        self.townBoard = np.full((4,4), emptyTile)
        self.townBoardDict = self.describeTownBoard()
        for row in range(4):
            for col in range(4):
                self.townBoard[row, col] = self.townBoardDict[row, col]
        return self.townBoard