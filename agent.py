from gymnasium.spaces import MultiDiscrete
from choices import *
from score import get_score
from resources import *
import random as rdm

class GreedyAgent:
    """
    Agent to act to gain immediate reward
    """
    def __init__(self, name):
        self.name = name
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

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

        observation = game.get_observation(player.get_id())

        for resource_index, resource in resource_dict.items():
            for tile_index in range(1,17):
                tile_coords = board_tile_dict[tile_index]
                if player.board[tile_coords] == empty:
                    saved_board = player.board
                    sim_board = player.board.copy()

                    player.board = sim_board

                    sim_board[tile_coords] = resource

                    score = get_score(game, player)
                    player.board = saved_board
                    if best_score < score:
                        best_score = score
                        best_resource_id = resource_index
                        best_tile_index = tile_index
        
        if best_resource_id is None or best_tile_index is None:
            best_resource_id = rdm.choice()
            empty_tile_index_list = [tile for tile in range(1,17) if player.board[board_tile_dict[tile]] == empty]
            best_tile_index = rdm.choice(empty_tile_index_list)
        
        return best_resource_id, best_tile_index


    
    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE
        self.action_space = MultiDiscrete([
        5,  # RESOURCE INDEX
        16, # TILE ID INDEX
        2,  # NO/ YES
        8,  # BUILDING TYPE
        7,  # BUILDING TYPE WITHOUT MONUMENT
        ])
    
    def __str__(self):
        return "{}".format(self.name)

    # def dynamic_to_fixed_action_state(self):

    
    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE
