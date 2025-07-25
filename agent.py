from choices import *
from score import get_score
from resources import *
import random as rdm
from layout_variants import find_all_placements
from ry import *

class Agent:
    """
    Agent to act to gain immediate reward
    """
    def __init__(self, name):
        self.name = name


        # self.actions = actions
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 1
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.policy = {
            "cottage_priority": 4,
            "farm_priority": 1,
            "factory_priority": 2,
            "tavern_priority": 3,
            "theatre_priority": 3,
            "monument_priority": 7,
            "shrine_priority": 1
        }

        # self.resource_epsilon
        # self.exploration_rate = exploration_rate
        # self.exploration_decay = exploration_decay

    def __str__(self):
        return "{}".format(self.name)

    def get_state(self, player, game):
        pass
        # STATE LOGIC

    # def update_agent_policy(self, score):
    #     if 16 < score:
            


    def board_scan(self, game, player):
        """
        Assist in resource placement decision by assessing placement
        options for what layout variants they assist in completing.
        """
        best_placement_score = -float("inf")
        best_moves = []
        empty_tile_list = []
        for tile_index in range(1,17):
            tile_coords = board_tile_dict[tile_index]
            if player.board[tile_coords] == empty:
                empty_tile_list.append(tile_index)
        saved_board = player.board.copy()

        for resource_index, resource in resource_dict.items():
            for tile_index in empty_tile_list:
                tile_coords = board_tile_dict[tile_index]
                player.board[tile_coords] = resource

                current_placement_score = 0

                for card in player.get_buildable_cards():
                    layout = card.get_layout()
                    for row_index, row in enumerate(layout):
                        for cell_index, cell in enumerate(row):
                            if cell == resource:
                                board_position = (tile_coords[0] - row_index, tile_coords[1] - cell_index)
                                try:
                                    if player.board[board_position] == resource:
                                        current_placement_score += 5
                                except:
                                    continue

                adjacent_coords = player.check_adjacent_tiles(tile_coords)
                for adjacent_coord_pair in adjacent_coords:
                    adjacent_tile = player.board[adjacent_coord_pair]
                    if adjacent_tile == resource:
                        current_placement_score += 1
                
                adjacent_empty = sum(1 for adjacent_coord_pair in adjacent_coords if player.board[adjacent_coord_pair] == empty)
                if adjacent_empty == 0:
                    current_placement_score -= 2

                current_placement_score += get_score(game, player)

                if best_placement_score < current_placement_score:
                    best_placement_score = current_placement_score
                    best_moves = [(resource_index, tile_index)]
                elif best_placement_score == current_placement_score:
                    best_moves.append((resource_index, tile_index))


                player.board = saved_board.copy()
        
        if best_moves:
            return rdm.choice(best_moves)
        else:
            best_resource_id = rdm.choice([key for key in resource_dict.keys()])
            best_tile_index = rdm.choice(empty_tile_list)
        return best_resource_id, best_tile_index

    def choose_resource_and_tile(self, game, player):
        """
        Select a resource and a tile placement.
        """
        best_score = -float("inf")
        best_resource_id = None
        best_tile_index = None
        best_choice_list = []
        empty_tile_list = []

        self.board_scan(game, player)

        
        saved_board = player.board
        # observation = game.get_observation(player.get_id())

        for tile_index in range(1,17):
            tile_coords = board_tile_dict[tile_index]
            if player.board[tile_coords] == empty:
                empty_tile_list.append(tile_index)

        if rdm.random() < self.epsilon:
            resource_dist_choice = rdm.randint(0, player.resource_distribution[0])
            if resource_dist_choice < player.resource_distribution[1]:
                resource_index = 1
            else:
                resource_dist_choice -= player.resource_distribution[1]
                if resource_dist_choice < player.resource_distribution[2]:
                    resource_index = 2
                else:
                    resource_dist_choice -= player.resource_distribution[2]
                    if resource_dist_choice < player.resource_distribution[3]:
                        resource_index = 3
                    else:
                        resource_dist_choice -= player.resource_distribution[3]
                        if resource_dist_choice < player.resource_distribution[4]:
                            resource_index = 4
                        else:
                            resource_index = 5
            # resource_index = rdm.choice(list(resource_dict.keys()))
            tile_index = rdm.choice(empty_tile_list)
            return resource_index, tile_index

        for resource_index, resource in resource_dict.items():
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
                        if best_score == score:
                            best_choice_list.append((resource_index, tile_index))
                        elif best_score < score:
                            best_choice_list = [(resource_index, tile_index)]
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
