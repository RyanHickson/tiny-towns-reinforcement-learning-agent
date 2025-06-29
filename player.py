import numpy as np
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
        self.current_score = 0

    def describe_player(self):
        return f"""Player {self.get_id()} has the current board: \n{self.get_display_board()} \n Their monument this game is {self.monument.get_name()}. They are being operated by agent {self.agent.get_name()}"""

    def get_id(self):
        return self.player_id

    def get_monument(self):
        return self.monument

    def get_agent(self):
        return self.agent

    def describe_town_board(self):
        """
        Returns the town board as it is, made up of
        instances of resource and building classes.
        """
        self.town_boardDict = {}
        for row in range(4):
            for tile in range(4):
                self.town_boardDict[row, tile] = self.board[row, tile]
        return self.town_boardDict

    def get_display_board(self):
        """
        Displays the board in a human friendly manner,
        by calling the get_name method for each
        resource and building on the board.
        """
        self.display_board = np.full((4, 4), emptyTile)
        self.town_boardDict = self.describe_town_board()
        for tile_id in board_tile_dict:
            self.display_board[board_tile_dict[tile_id]] = self.town_boardDict[
                board_tile_dict[tile_id]
            ].get_name()
        return self.display_board

    def get_resource_types(self):
        return self.resource_types

    def check_immediate_adjacent_tiles(self, tile_id):
        """
        A method to check the 4 immediate neighbours of a
        given tile, and return a list of their contents.
        If a tile is on a boundary and has fewer neighbours
        it will only return 2 or 3, depending on tile location.
        """
        manipulation_values = [-4, -1, +1, +4]
        adjacent_tiles_list = []
        if tile_id % 4 == 0:
            manipulation_values.remove(+1)
        elif (tile_id - 1) % 4 == 0:
            manipulation_values.remove(-1)
        for val in manipulation_values:
            if 0 < tile_id + val < 17:
                adjacent_tiles_list.append(tile_id + val)
        return adjacent_tiles_list

    def check_grouping(self, start_tile_id, visited, condition=lambda card: True):
        """
        Find single grouping
        """
        current_group = []

        def depth_first_search(tile_id):
            if tile_id in visited:
                return
            visited.add(tile_id)
            card = self.board[board_tile_dict[tile_id]]
            if not (isinstance(card, Card)) or not condition(card):
                return
            current_group.append(tile_id)
            for adjacent_tile in self.check_immediate_adjacent_tiles(tile_id):
                depth_first_search(adjacent_tile)

        depth_first_search(start_tile_id)
        return current_group

    def check_contiguous_groups(self):
        """
        A method to return the group of adjacent buildings
        on the town board that yields the highest score.
        Used for Greenhouse feeding scoring.
        """

        visited = set()
        all_groups = []

        def tile_attribute(tile):
            return getattr(tile, "is_feedable", False)

        for tile_id in board_tile_dict:
            if tile_id in visited:
                continue
            tile_content = self.board[board_tile_dict[tile_id]]
            if not isinstance(tile_content, Card):
                continue

            if not tile_attribute(tile_content):
                continue
            current_group = self.check_grouping(
                tile_id,
                visited,
                lambda tile_content: getattr(tile_content, "is_feedable", False),
            )
            if current_group:
                all_groups.append(current_group)
        return all_groups

    def largest_contiguous_group(self):
        """
        For scoring Silva Forum
        """

        largest_group = []

        for card_type in Card.__subclasses__():
            visited = set()
            for tile_id in board_tile_dict:
                if tile_id in visited:
                    continue
                tile_content = self.board[board_tile_dict[tile_id]]
                if not isinstance(tile_content, card_type):
                    continue
                current_group = self.check_grouping(
                    tile_id,
                    visited,
                    lambda tile_content: isinstance(tile_content, card_type),
                )
                if len(largest_group) < len(current_group):
                    largest_group = current_group
        return largest_group
    
    def check_row(self, tile_id):
        tile_row, tile_col = board_tile_dict[tile_id]
        row_content_list = []
        row_coords_list = []
        for col in range(4):
            row_coords = tile_row, col
            row_coords_list.append(row_coords)
            tile_content = self.board[row_coords]
            row_content_list.append(tile_content)
        return row_content_list, row_coords_list
    
    def check_col(self, tile_id):
        tile_row, tile_col = board_tile_dict[tile_id]
        col_content_list = []
        col_coords_list = []
        for row in range(4):
            col_coords = row, tile_col
            col_coords_list.append(col_coords)
            tile_content = self.board[col_coords]
            col_content_list.append(tile_content)
        return col_content_list, col_coords_list