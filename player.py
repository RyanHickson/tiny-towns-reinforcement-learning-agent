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
        for key in board_tile_dict.keys():
            self.display_board[board_tile_dict[key]] = self.town_boardDict[
                board_tile_dict[key]
            ].get_name()
        return self.display_board

    def get_resource_types(self):
        return self.resource_types

    def check_immediate_adjacent_tiles(self, tile):
        """
        A method to check the 4 immediate neighbours of a
        given tile, and return a list of their contents.
        If a tile is on a boundary and has fewer neighbours
        it will only return 2 or 3, depending on tile location.
        """
        manipulation_values = [-4, -1, +1, +4]
        adjacent_tiles_list = []
        if tile % 4 == 0:
            manipulation_values.remove(+1)
        elif (tile - 1) % 4 == 0:
            manipulation_values.remove(-1)
        for val in manipulation_values:
            if 0 < tile + val < 17:
                adjacent_tiles_list.append(tile + val)
        return adjacent_tiles_list

    def check_grouping(self, start_tile, visited, check_condition_card=greenhouse):
        """
        Find single grouping
        """
        current_group = []

        def depth_first_search(tile):
            if tile in visited:
                return
            visited.add(tile)
            card = self.board[board_tile_dict[tile]]
            if not (isinstance(card, Card) and check_condition_card(card)):
                return
            current_group.append(tile)
            for adjacent_tile in self.check_immediate_adjacent_tiles(tile):
                depth_first_search(adjacent_tile)

        depth_first_search(start_tile)
        return current_group

    def check_contiguous_groups(self, check_condition_card=greenhouse):
        """
        A method to return the group of adjacent buildings
        on the town board that yields the highest score.
        Used for Greenhouse feeding and Silva Forum scoring.
        """

        visited = set()
        all_groups = []

        if check_condition_card == greenhouse:

            def tile_attribute(tile):
                return getattr(tile, "is_feedable", False)

        elif check_condition_card == silva_forum:

            def tile_type(card_type):
                return lambda t: t.get_deck() == card_type

        tiles_to_check = board_tile_dict.keys()
        for tile_id in tiles_to_check:
            if tile_id in visited:
                continue
            tile = self.board[board_tile_dict[tile_id]]
            if not isinstance(tile, Card):
                continue

            if check_condition_card == silva_forum:
                card_type = tile.get_deck()
                current_group = self.check_grouping(
                    tile_id, tile_type(card_type), visited
                )
            else:
                if not tile_attribute(tile):
                    continue
                current_group = self.check_grouping(tile_id, tile_attribute, visited)
            if current_group:
                all_groups.append(current_group)
        return all_groups
