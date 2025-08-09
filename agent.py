from choices import *
from score import get_score
from resources import *
import random as rdm
from layout_variants import find_all_placements
from ry import *
from itertools import combinations, product
from copy import deepcopy

class Agent:
    """
    Agent to act to gain immediate reward
    """
    def __init__(self, name):
        self.name = name


        # self.actions = actions
        self.epsilon = 0.01

        self.policy = {
            "cottage_priority": 4,
            "farm_priority": 2,
            "factory_priority": 2,
            "chapel_priority": 2,
            "tavern_priority": 3,
            "theatre_priority": 3,
            "well_priority": 0.1,
            "monument_priority": 7,
            "shrine_priority": 2
        }

        # self.resource_epsilon
        # self.exploration_rate = exploration_rate
        # self.exploration_decay = exploration_decay

    def __str__(self):
        return "{}".format(self.name)

    def get_state(self, player, game):
        pass
        # STATE LOGIC

    def get_policy(self):
        return self.policy

    # def update_agent_policy(self, score):
    #     if 16 < score:

    def select_resource_and_tile(self, game, player):
        """
        Select a resource and a tile placement.
        """
        best_score = -float("inf")
        best_resource_id = None
        best_tile_index = None
        best_resource_combo = None
        best_tile_combo = None
        empty_tile_list = []
        sim_player = deepcopy(player)
        saved_board = sim_player.get_board()
        number_of_turns = 4
        
        for tile_index in range(1, 17):
                tile_coords = board_tile_dict[tile_index]
                if isinstance(sim_player.get_board()[tile_coords], EmptyResource):
                    empty_tile_list.append(tile_index)

        combo_length = min(number_of_turns, len(empty_tile_list))
        tile_combos = combinations(empty_tile_list, combo_length)
        resource_combos = product(resource_dict.keys(), repeat=combo_length)
        
        if self.epsilon < rdm.random():
            for tile_combo in tile_combos:

                for resource_combo in resource_combos:
                    for index in range(combo_length):
                        sim_board = sim_player.board.copy()
                        sim_player.board = sim_board

                        resource_index = resource_combo[index]
                        tile_index = tile_combo[index]

                        sim_player.board[board_tile_dict[tile_index]] = resource_dict[resource_index]

                        build_board = sim_board.copy()
                        sim_player.board = build_board
                        coord_dictionary, build_options, placement_display = find_all_placements(sim_player, sim_player.get_buildable_cards())

                        while coord_dictionary:
                            coord_dictionary, build_options, placement_display = find_all_placements(sim_player, sim_player.get_buildable_cards())
                            which_building_choice = dict_enum(placement_display)
                            dict_presented = dict()
                            for key in which_building_choice:
                                if which_building_choice[key]:
                                    dict_presented[key] = which_building_choice[key]
                            for build_choice in dict_presented:
                                chosen_building_dict = build_options[build_choice]
                                for key in chosen_building_dict:
                                    sim_player.construct(chosen_building_dict[key], game.dictionary_of_players, simulated_construct=True)
                                    score = get_score(game, sim_player, simulated_scoring=True)
                                    if best_score < score:
                                        best_score = score
                                        best_resource_combo = resource_combo
                                        best_tile_combo = tile_combo
                        sim_player.board = sim_board
            sim_player.board = saved_board
            if best_resource_combo == None or best_tile_combo == None:
                best_resource_id = rdm.choice([key for key in resource_dict.keys()])
                best_tile_index = rdm.choice(empty_tile_list)
                return best_resource_id, best_tile_index

            idx = rdm.choice(range_len(best_resource_combo))
            best_resource_id = best_resource_combo[idx]
            best_tile_index = best_tile_combo[idx]
            return best_resource_id, best_tile_index

        else:
            resource_index = rdm.choice(list(resource_dict.keys()))
            tile_index = rdm.choice(empty_tile_list)
            return resource_index, tile_index
        



    def __str__(self):
        return "{}".format(self.name)

    # def dynamic_to_fixed_action_state(self):

    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE
