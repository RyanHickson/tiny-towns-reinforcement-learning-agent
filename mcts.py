from choices import *
import copy
from cards import Card


class BoardState:
    def __init(self, board):







class MCTSNode:
    """
    Node for each point of Monte Carlo Tree Search
    """
    def __init__(self, state, player_id, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        
        self.children = []
        self.player_id = player_id

        self.visits = 0
        self.total_reward = 0
        self.average_reward = 0
        self.empty_tiles = []

        self.untried_actions = None
        self.legal_actions = None

        self.is_terminal = False
        self.is_fully_expanded = False

        self.buildings_constructed = 0
        self.score_estimate = 0
        self.board_fullness = 0

        def get_legal_actions(self, player):
            if self.legal_actions is not None:
                return self.legal_actions
            
            self.legal_actions = []
            empty_tile_list = []

            for tile_index in range(1, 17):
                tile_coords = board_tile_dict[tile_index]
                if player.board[tile_coords] == empty:
                    empty_tile_list.append(tile_index)

            for resource_index in resource_dict:
                for tile_index in empty_tile_list:
                    self.legal_actions.append((resource_index, tile_index))

            return self.legal_actions
        
        def take_action(self, action, game, player):
            resource_index, tile_index = action

            new_state = copy.deepcopy(self.state)

            tile_coords = board_tile_dict[tile_index]
            resource = resource_dict[resource_index]

            if "players" in new_state and player.get_id() in new_state["players"]:
                new_state["players"][player.get_id()]["board"][tile_coords] = resource

            return new_state
        
        def assess_state(self):
            if not self.state or "players" not in self.state:
                return
            
            for player_id, player_state in self.state["players"].items():
                if player_id == self.player_id:
                    board = player_state.get("board")
                    if board is not None:
                        empty_count = sum(1 for row in board for tile in row if tile == empty)
                        self.board_fullness = (16 - empty_count) / 16

                        self.buildings_constructed = sum(1 for row in board for tile in row if isinstance(tile, Card))
                        break


        

        def is_leaf_node(self):
            return len(self.children == 0)
        
        def is_terminal_node(self):
            if self.is_terminal:
                return True
            if self.state  