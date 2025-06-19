import numpy as np

testBoard = np.array([["b", "g", "b", "g"],
                      ["w", "c", "w", "g"],
                      ["s", "w", "c", "s"],
                      ["s", "w", "b", "c"]])

class Player:
    def __init__(self, playerNumber, monument):
        self.playerNumber = playerNumber
        self.monument = monument

        self.board = testBoard
        # self.board = np.full((4,4), "", dtype=str)

    def describePlayer(self):
        return f"Player {self.playerNumber} has the current board: \n {self.board} \n Their monument this game is {self.monument.getName()}"
    