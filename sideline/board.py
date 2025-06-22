import numpy as np
from tile import Tile

class Board:
    
    def __init__(self, owner):
        self.owner = owner
        
    def boardSetup(self):
        board = np.zeros((4,4))
        for i in range(4):
            for j in range(4):
                board[i,j] = 5 # Tile(i,j,"")
        return board