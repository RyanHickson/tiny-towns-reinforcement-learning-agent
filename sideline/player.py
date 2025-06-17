import numpy as np
from gameBoard import *

class Player:
    def __init__(self, playerNumber, board, monument):
        self.playerNumber = playerNumber
        self.board = townBoard
        self.monument = monument

    def describePlayer(self):
        return f"Player {self.playerNumber} has the current board: \n {self.board} \n Their monument this game is {self.monument}"