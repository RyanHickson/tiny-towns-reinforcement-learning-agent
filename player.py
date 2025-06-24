import numpy as np
import random as rdm
from building_layouts import *
from resources import *
from cards import *
from choices import *

empty_board = np.full((4, 4), emptyTile)


class Player:
    def __init__(self, player_id, monument, agent):
        self.player_id = player_id
        self.monument = monument
        self.board = empty_board
        self.agent = agent
        self.resource_types = [wood, wheat, glass, brick, stone]
        # 1      2      3      4      5

        # self._board = np.full((4,4), "", dtype=str)

    def describe_player(self):
        return f"Player {self.get_id()} has the current _board: \n {self.show_board()} \n Their monument this game is {self.monument.get_name()}. They are being operated by agent {self.agent.get_name()}"

    def get_id(self):
        return self.player_id

    def get_agent(self):
        return self.agent

    def describe_town_board(self):
        self.town_boardDict = {}
        for row in range(4):
            for tile in range(4):
                self.town_boardDict[row, tile] = self.board[row, tile]  # .getName()
        return self.town_boardDict

    def show_board(self):
        self.town_board = np.full((4, 4), emptyTile)
        self.town_boardDict = self.describe_town_board()
        for row in range(4):
            for col in range(4):
                self.town_board[row, col] = self.town_boardDict[row, col].get_name()
        return self.town_board

    def get_resource_types(self):
        return self.resource_types

    def check_immediate_adjacent_tiles(self, tile):
        """
        A method to check the 4 immediate neighbours of a
        given tile, and return a list of their contents.
        """
        current_tile_tuple = board_tile_dict[tile]
        adjacent_tiles_list = []
        for val in [-4, -1, +1, +4]:
            try:
                if (tile + val) % 4 != 0 and (tile) % 4 != 0:
                    adjacent_tiles_list.append(board_tile_dict[tile + val])
                if (tile) % 4 == 0:
                    adjacent_tiles_list.append(board_tile_dict[tile + val])
            except:
                continue
        return adjacent_tiles_list

    def check_adjacent_tiles(self):
        """
        A method to return the group of adjacent buildings
        on the town board that yields the highest score.
        Used for Greenhouse feeding and Silva Forum scoring.
        """
        # HOLD ON ACTUALLY IT MIGHT BE BETTER TO JUST CHECK THE ENTIRE BOARD FROM THE START LIKE
        # for row in self.town_board:
        # for tile in row:
        # check adjacents
        # any matches add to this group and remove from check_queue
        max_score = []
        adjacent_check_queue = []
        current_best_combination = []
        for row in range(4):
            for tile in range(4):
                if self.town_board[row, tile] == some_test_condition.get_quality():
                    self.check_immediate_adjacent_tiles()
                    # add tiles that match condition to queue
                    # add tiles that match to list
                    # check total score
