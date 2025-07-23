from gymnasium.spaces import MultiDiscrete
from choices import *
from score import get_score
from resources import *
import random as rdm
from layout_variants import find_all_placements
from ry import *

class GreedyAgent:
    """
    Agent to act to gain immediate reward
    """
    def __init__(self, name):
        self.name = name
        # self.actions = actions
        # self.learning_rate = learning_rate
        # self.discount_factor = discount_factor
        # self.exploration_rate = exploration_rate
        # self.exploration_decay = exploration_decay

        self.action_space = MultiDiscrete([
        5,  # RESOURCE INDEX
        16, # TILE ID INDEX
        2,  # NO/ YES
        8,  # BUILDING TYPE
        7,  # BUILDING TYPE WITHOUT MONUMENT
        ])

    def __str__(self):
        return "{}".format(self.name)

    def get_state(self, player, game):
        pass
        # STATE LOGIC

    def choose_resource_and_tile(self, game, player):
        """
        Select a resource and a tile placement.
        """
        best_score = -float("inf")
        best_resource_id = None
        best_tile_index = None
        best_choice_list = []
        empty_tile_list = []

        # observation = game.get_observation(player.get_id())

        for resource_index, resource in resource_dict.items():
            for tile_index in range(1,17):
                tile_coords = board_tile_dict[tile_index]
                if player.board[tile_coords] == empty:
                    empty_tile_list.append(tile_index)
                    saved_board = player.board
                    sim_board = player.board.copy()

                    player.board = sim_board

                    sim_board[tile_coords] = resource

                    coord_dictionary, build_options, placement_display = (find_all_placements(player, player.get_buildable_cards()))
                    while (len(coord_dictionary) != 0):
                        coord_dictionary, build_options, placement_display = (find_all_placements(player, player.get_buildable_cards()))
                        which_building_choice = dict_enum(placement_display)
                        dict_presented = dict()
                        for key in which_building_choice:
                            if which_building_choice[key]:
                                dict_presented[key] = which_building_choice[key]
                        for build_choice in dict_presented:
                            chosen_building_dict = build_options[build_choice]
                            for key in chosen_building_dict:
                                player.construct(chosen_building_dict[key], game.dictionary_of_players)
                                score = get_score(game, player)

                                player.board = saved_board
                                if best_score == score:
                                    best_choice_list.append((resource_index, tile_index))
                                elif best_score < score:
                                    best_choice_list.append((resource_index, tile_index))
                                    best_score = score
                                    best_resource_id = resource_index
                                    best_tile_index = tile_index
                    score = get_score(game, player)
                    player.board = saved_board
        
        if 1 < len(best_choice_list):
            best_resource_id, best_tile_index = rdm.choice(best_choice_list)
        if best_resource_id == None or best_tile_index == None:
            best_resource_id = rdm.choice([key for key in resource_dict.keys()])
            best_tile_index = rdm.choice(empty_tile_list)
        return best_resource_id, best_tile_index

    def __str__(self):
        return "{}".format(self.name)

    # def dynamic_to_fixed_action_state(self):

    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE
