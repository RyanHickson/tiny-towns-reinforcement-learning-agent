import numpy as np
from building_layouts import *
from resources import *
from cards import *
from choices import *
from score import get_score
from construct import player_construct


class Player:
    def __init__(self, player_id, monument, agent):
        self.player_id = player_id
        self.monument = monument
        self.board = np.full((4, 4), empty)
        self.agent = agent
        self.resource_types = [wood, wheat, glass, brick, stone]
        self.score = 0
        self.all_cards = []
        self.buildable_cards = []
        self.factory_resources = []
        self.warehouse_capacity = 0
        self.warehouse_resources = []
        self.bank_resources = []
        self.opaleyes_watch_holdings = []
        self.board_is_filled = False
        self.resource_choice_dict = resource_names_dict
        self.shrine_key = 0
        self.finish_position = 0


        self.environment = [
            self.board,
            self.factory_resources,
            self.warehouse_resources,
            self.bank_resources,
        ]

    def __repr__(self):
        factory_type_text = ""
        factory_type_function = ""
        if trading_post in self.get_all_cards():
            factory_type_string_append = ""
        else:
            factory_type_string_append = " Their {} resources are {}"
        if factory in self.get_all_cards():
            factory_type_text = "factory"
            factory_type_function = self.get_factory_resources()
        elif warehouse in self.get_all_cards():
            factory_type_text = "warehouse"
            factory_type_function = self.get_warehouse_resources()
        elif bank in self.get_all_cards():
            factory_type_text = "bank"
            factory_type_function = self.get_bank_resources()

        return """{} has the current board: \n{}
Their monument this game is {}. They are being operated by agent {}
The cards available to them are {}""".format(
            self.__str__(),
            self.get_display_board(),
            self.monument.__str__(),
            self.agent.__str__(),
            self.display_all_cards(),
        ) + factory_type_string_append.format(
            factory_type_text, factory_type_function
        )

    def __str__(self):
        return "Player {}".format(self.player_id)
    
    def get_id(self):
        return self.player_id

    def get_monument(self):
        return self.monument

    def get_agent(self):
        return self.agent

    def get_score(self):
        return self.score

    def display_score(self):
        return "{} has {}VP".format(self.__str__(), self.get_score())

    def get_all_cards(self):
        return self.all_cards
    
    def get_buildable_cards(self):
        self.buildable_cards = self.get_all_cards()
        if len(self.buildable_cards) == 8:
            for tile_id, tile_coords in board_tile_dict.items():
                if isinstance(self.board[tile_coords], Monument):
                    self.buildable_cards.pop(-1)
        return self.buildable_cards

    def get_factory_resources(self):
        return self.factory_resources

    def get_warehouse_resources(self):
        return self.warehouse_resources
    
    def get_trading_post_details(self):
        trading_post_indexes = []
        trading_post_coords = []
        for tile_id, tile_coords in board_tile_dict.items():
            trading_post_indexes.append(tile_id)
            trading_post_coords.append(tile_coords)
        return trading_post_indexes, trading_post_coords

    def get_bank_resources(self):
        return self.bank_resources
    
    def get_factory_type_resources(self):
        buildable_cards = self.get_buildable_cards()
        if factory in buildable_cards:
            return self.get_factory_resources()
        if warehouse in buildable_cards:
            return self.get_warehouse_resources()
        if trading_post in buildable_cards:
            return self.get_trading_post_details()
        if bank in buildable_cards:
            return self.get_bank_resources()
        

    def display_all_cards(self):
        return [card.__str__() for card in self.get_buildable_cards()]

    def get_instance_board(self):
        """
        Returns the town board as it is, made up of
        instances of resource and building classes.
        """
        self.town_board_dict = {}
        for row in range(4):
            for tile in range(4):
                self.town_board_dict[row, tile] = self.board[row, tile]
        return self.town_board_dict

    def get_display_board(self):
        """
        Displays the board in a human friendly manner,
        by calling the __str__ method for each
        resource and building on the board.
        """
        self.display_board = np.full((4, 4), empty)
        self.town_board_dict = self.get_instance_board()
        for tile_id, tile_coords in board_tile_dict.items():
            # print(f"{self.town_board_dict[board_tile_dict[tile_id]]=}")
            self.display_board[tile_coords] = self.town_board_dict[
                tile_coords
            ].__str__()
        return self.display_board

    def get_resource_types(self):
        return [resource.__str__() for resource in self.resource_types]
    
    def get_feast_hall_count(self):
        self.feast_hall_count = 0
        for tile_id, tile_coords in board_tile_dict.items():
            if self.board[tile_coords] == feast_hall:
                self.feast_hall_count += 1
        return self.feast_hall_count

    def get_board_is_filled(self):
        return self.board_is_filled

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
    
    def check_adjacent_tiles(self, tile_coords):
        """
        A method to check the 4 surrounding neighbours of a
        given tile, and return a list of their coordinates.
        Tiles on town board boundary will have fewer neighbours.
        """
        adjacent_relations = [(-1, 0), (0, -1), (0, +1), (+1, 0)]
        adjacent_tiles_list = []    # initialise return
        for relational_vector in adjacent_relations:
            i, j = tile_coords
            r, c = relational_vector
            if -1 < i + r < 4 and -1 < j + c < 4:
                adjacent_tiles_list.append((i + r, j + c))
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
        A method to return all groups of adjacent feedable buildings
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
            if not isinstance(tile_content, Card):  # skip resources
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

    def check_row(self, coord_pair):
        tile_row, tile_col = coord_pair
        row_content_list = []
        row_coords_list = []
        for col in range(4):
            row_coords = tile_row, col
            row_coords_list.append(row_coords)
            tile_content = self.board[row_coords]
            row_content_list.append(tile_content)
        return row_content_list, row_coords_list

    def check_col(self, coord_pair):
        tile_row, tile_col = coord_pair
        col_content_list = []
        col_coords_list = []
        for row in range(4):
            col_coords = row, tile_col
            col_coords_list.append(col_coords)
            tile_content = self.board[col_coords]
            col_content_list.append(tile_content)
        return col_content_list, col_coords_list

    def greenhouse_feeding(self):
        score_list = []
        fed_coords = []
        contiguous_feedable_groups = self.check_contiguous_groups()
        for group_index, grouping in enumerate(contiguous_feedable_groups):
            current_grouping = []
            score_list.append(current_grouping)
            for tile_id in grouping:
                tile_coords = board_tile_dict[tile_id]
                if isinstance(self.board[tile_coords], CottageType):
                    current_grouping.append(self.board[tile_coords].score_when_fed())
                    fed_coords.append(tile_coords)
                if barrett_castle == self.get_monument():
                    if isinstance(self.board[tile_coords], Monument):
                        current_grouping.append(self.board[tile_coords].score_when_fed())
                        fed_coords.append(tile_coords)
        score_list = sorted(score_list, reverse=True)   # orders the lists from largest score to smallest, to score in correct order
        return score_list, fed_coords

    def get_building_count(self, building):
        building_count = 0
        for tile_id in range(1, 17):
            tile_coords = board_tile_dict[tile_id]
            tile_content = self.board[tile_coords]
            if tile_content == building:
                building_count += 1
        return building_count

    def construct(self, dict, dictionary_of_players, opaleye_construct=False):
        """
        Calls the construct method for handling using resources
        to build, and immediate effects therein.
        """
        return player_construct(self, dict, dictionary_of_players, opaleye_construct)
