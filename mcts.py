from resources import *
import numpy as np
from layout_variants import *
import hashlib
from joblib import Parallel, delayed
import random as rdm
from player import *
import logging
import math
import copy
from placement_check import actions_equal, score_action, work_towards_layout


class MCTSAgent:
    def __init__(self, name, max_search_depth=16, exploration_const=1.414):
        self.name = name
        self.mcts = MCTS(exploration_const, max_search_depth)
        self.game_state = None

    def choose_action(self, game, player):
        self.game_state = BoardState(player)
        self.mcts.community_cards = getattr(game, "community_cards", self.mcts.community_cards)

        best_action = self.mcts.search(self.game_state)

        if best_action:
            return best_action
        else:
            empty_list = []
            for tile_index in range(1, 17):
                tile_coords = board_tile_dict[tile_index]
                if isinstance(player.board[tile_coords], EmptyResource):
                    empty_list.append(tile_coords)

            if empty_list:
                resource_index = rdm.choice(list(resource_dict.keys()))
                tile_coords = rdm.choice(empty_list)
                resource = resource_dict[resource_index]
                return resource, tile_coords



class MCTS:
    def __init__(self, exploration_const=1.414, max_search_depth=16):
        self.cottage_choice = rdm.choice(cottage_deck)
        self.farm_choice = rdm.choice(farm_deck)
        self.factory_choice = rdm.choice(factory_deck)
        self.tavern_choice = rdm.choice(tavern_deck)
        self.chapel_choice = rdm.choice(chapel_deck)
        self.theatre_choice = rdm.choice(theatre_deck)
        self.well_choice = rdm.choice(well_deck)

        self.community_cards = [
            self.cottage_choice,
            self.farm_choice,
            self.factory_choice,
            self.tavern_choice,
            self.chapel_choice,
            self.theatre_choice,
            self.well_choice,
        ]

        self.exploration_const = exploration_const
        self.max_search_depth = max_search_depth
        self.transposition_table = {}
        self.priority_cards = []

    def get_community_cards(self):
        return self.community_cards

    def get_transposition_table(self):
        return self.transposition_table
    
    def get_board_strings(self, boardstate):
        boards = create_variants(boardstate.player.get_display_board())
        new_array = np.array([str(board) for board in boards])
        boards = np.unique(new_array)
        return boards
    
    def stable_hash(self, board_string):
        return hashlib.md5(board_string.encode()).hexdigest()
    
    def format_board_for_hash(self, board):
        board_hash_list = []
        for row in board:
            row_hash = []
            for el in row:
                row_hash.append(el.__str__())
            board_hash_list.append(row_hash)
        return str(board_hash_list)
        
    
    def get_or_create_node(self, state, parent=None, action=None):
        board_varieties = self.get_board_strings(state)
        # sortable_board_varieties = []
        for board in board_varieties:
            # board_string = self.format_board_for_hash(board)
            # sortable_board_varieties.append(board_string)
            hash_board = self.stable_hash(board)
            if hash_board in self.get_transposition_table():
                existing_node = self.get_transposition_table()[hash_board]
                if parent:
                    existing_node.add_parent(parent, action)
                return existing_node
        canonical_board = sorted(board_varieties)[0]
        new_node = MCTSNode(state, parent, action)
        new_node.empty_tiles = state.get_empty_tile_list()
        self.transposition_table[self.stable_hash(canonical_board)] = new_node
        return new_node
    
    def select(self, node):
        while not node.is_leaf() and not node.state.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.select_best_child(self.exploration_const)
            node.empty_tiles = node.state.get_empty_tile_list()
        return node

    def search(self, current_state):
        root_node = MCTSNode(current_state)
        root_node.empty_tiles = current_state.get_empty_tile_list()

        nodes_to_simulate = []
        for _ in range(self.max_search_depth):
            node = self.select(root_node)
            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = self.expand(node)
            nodes_to_simulate.append(node)

            rewards = Parallel(n_jobs=-1)(delayed(self.simulate)(node) for node in nodes_to_simulate)

            for node, reward in zip(nodes_to_simulate, rewards):
                node.backpropagate(reward)

        actions = []
        empty_tiles = current_state.get_empty_tile_list()

        wood_count = 0
        wheat_count = 0
        glass_count = 0
        brick_count = 0
        stone_count = 0
        
        tile_coords_with_resources = []
        board = current_state.player.get_display_board()
        for r_i, row in enumerate(board):
            for c_i, col in enumerate(row):
                tile = board[r_i][c_i]
                if isinstance(tile, Resource) and not isinstance(tile, EmptyResource):
                    tile_coords_with_resources.append((r_i, c_i))
                if tile.__str__() == wood.__str__():
                    wood_count += 1
                if tile.__str__() == wheat.__str__():
                    wheat_count += 1
                if tile.__str__() == glass.__str__():
                    glass_count += 1
                if tile.__str__() == brick.__str__():
                    brick_count += 1
                if tile.__str__() == stone.__str__():
                    stone_count += 1
        resource_count_dict = {wood: wood_count, wheat: wheat_count, glass: glass_count, brick: brick_count, stone: stone_count}
        if tile_coords_with_resources:
            rdm.shuffle(tile_coords_with_resources)
            tile_coords_for_adjacency_check = tile_coords_with_resources.pop()
            tiles_adjacent_to_resource = current_state.player.check_adjacent_tiles(tile_coords_for_adjacency_check)
            for resource in resource_list:
                for tile_coords in tiles_adjacent_to_resource:
                    actions.append((resource, tile_coords))
        else:
            overrepresented_resource = max(resource_count_dict, key=resource_count_dict.get)
            resource = overrepresented_resource
            while resource == overrepresented_resource:
                resource = rdm.choice(resource_list)
            tile_coords = rdm.choice(empty_tiles)

        if root_node.children:
            best_child = max(root_node.children, key=lambda child: child.visits)
            for parent, action in best_child.parents:
                if parent == root_node:
                    return action
        underrepresented_resource = min(resource_count_dict, key=resource_count_dict.get)
        random_tile_coords = rdm.choice(empty_tiles)
        logging.debug("Underrepresented resource chosen, may not have expanded correctly")
        return underrepresented_resource, random_tile_coords
    
    def expand(self, node):
        if node.untried_actions is None:
            node.empty_tiles = node.state.get_empty_tile_list()
            node.untried_actions = node.get_legal_actions()
            board = node.state.player.get_board()
            self.community_cards = self.get_community_cards()

        scored_actions = []
        board = node.state.player.get_board()
        max_test_score = -17
        test_score = None
        top_scoring_actions = []
        buildable_cards = node.state.player.get_buildable_cards()
        late_game_flip = False
        
        if not self.priority_cards:
            if node.state.current_turn < 20:
                self.priority_cards = [card for card in buildable_cards if card.get_priority() != "LateGame"]
                rdm.shuffle(self.priority_cards)
            else:
                self.priority_cards = [card for card in buildable_cards if card.get_priority() != "EarlyGame"]
                rdm.shuffle(self.priority_cards)
        # rdm.shuffle(buildable_cards)
        for card in self.priority_cards:
            moves_wanted = work_towards_layout(board, card.get_layout())
            if len(moves_wanted) <= 1:
                rdm.shuffle(self.priority_cards)
                if not late_game_flip:
                    if 20 < node.state.current_turn:
                        late_game_flip = True
                        self.priority_cards = []
            test_board = copy.deepcopy(board)
            test_player = copy.deepcopy(node.state.player)
            test_player.board = test_board
            for action in moves_wanted:
                resource, tile_coords = action
                test_board[tile_coords] = resource
                test_score = get_score(node.state, test_player, simulated_scoring=True)
            if test_score:
                if max_test_score < test_score:
                    max_test_score = test_score
                    best_action = moves_wanted[0]
                    top_scoring_actions = moves_wanted
        if not top_scoring_actions:
            for action in node.untried_actions:
                scored_action = (action, score_action(action, board, self.get_community_cards()))
                scored_actions.append(scored_action)
            scored_actions.sort(key=lambda item: item[1], reverse=True)

            top_scoring_actions = [action for action, score in scored_actions[:3]]

        for action in top_scoring_actions:
            for untried_action in node.untried_actions:
                if actions_equal(action, untried_action):
                    node.untried_actions.remove(untried_action)
                    current_state = node.state.apply_action(action)
                    child = self.get_or_create_node(current_state, node, action)

                    if child:
                        if child not in node.children:
                            node.children.append(child)
                            
                            board_string = self.format_board_for_hash(board)
                            hash_board = self.stable_hash(board_string)
                            if hash_board not in child.parents:
                                child.add_parent(node, action)
                        return child
        
        if node.untried_actions:
            rdm.shuffle(node.untried_actions)
            action = node.untried_actions.pop()
            current_state = node.state.apply_action(action)
            child = self.get_or_create_node(current_state, node, action)

            if child:
                if child not in node.children:
                    node.children.append(child)
                    parent_board = self.format_board_for_hash(board)
                    if parent_board not in child.parents:
                        child.add_parent(node, action)
                return child
        return node


    def simulate(self, node):
        current_state = copy.deepcopy(node.state)

        sim_depth = 0
        max_sim_depth = 16

        while not current_state.is_terminal() and sim_depth < max_sim_depth:
            empty_tiles = current_state.get_empty_tile_list()
            if not empty_tiles:
                break

            actions = []
            for tile_coords in empty_tiles:
                for resource in resource_list:
                    actions.append((resource, tile_coords))
            
            if not actions:
                break

            scored_actions = node.prioritise_actions(actions, current_state.player.get_board(), self.get_community_cards())

            top_scoring_actions = scored_actions[:3] if len(scored_actions) >= 3 else scored_actions
            action = top_scoring_actions[0]
            current_state = current_state.apply_action(action)
            sim_depth += 1
        return current_state.evaluate()






class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state

        self.parents = []
        self.children = []

        self.visits = 0
        self.total_reward = 0
        self.untried_actions = None
        self.empty_tiles = []

    def add_parent(self, parent, action):
        self.parents.append((parent, action))

    def is_fully_expanded(self):
        return self.untried_actions is not None and len(self.untried_actions) == 0
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def get_legal_actions(self):
        self.empty_tiles = self.state.get_empty_tile_list()

        if 10 < len(self.empty_tiles):
            tile_sample = rdm.sample(self.empty_tiles, min(10, len(self.empty_tiles)))
        else:
            tile_sample = self.empty_tiles


        rdm.shuffle(resource_list)
        rdm.shuffle(tile_sample)
        actions = []
        for tile_coords in tile_sample:
            for resource in resource_list:
                actions.append((resource, tile_coords))
        return actions
    
    def ucb1_score(self, exploration_const=1.414):
        if self.visits == 0:
            return float("inf")
        
        exploitation = self.total_reward / self.visits

        if self.parents:
            parent_visits = max(parent.visits for parent, action in self.parents)
            exploration = exploration_const * math.sqrt(math.log(parent_visits) / self.visits)
        else:
            exploration = 0

        return exploration + exploitation
    
    def select_best_child(self, exploration_const=1.414):
        return max(self.children, key=lambda child: child.ucb1_score(exploration_const))
    
    def add_child(self, action, state):
        child = MCTSNode(state, self, action)
        self.children.append(child)
        return child
    
    def update(self, reward):
        self.visits += 1
        self.total_reward += reward

    def backpropagate(self, reward):
        self.update(reward)
        for parent, action in self.parents:
            if parent:
                parent.backpropagate(reward)

    def prioritise_actions(self, actions, board, community_cards):
        scored_actions = []
        for action in actions:
            resource, tile_coords = action
            sim_board = copy.deepcopy(board)
            sim_board[tile_coords] = resource
            coord_dict, build_options, _ = find_all_placements(self.state.player, community_cards)
            score = 0
            if build_options:
                score += sum(len(option) for option in build_options) * 10
            scored_actions.append((score, action))
        scored_actions.sort(key=lambda x: x[0], reverse=True)
        return [action for _, action in scored_actions]





class BoardState:
    def __init__(self, player=None):
        self.player = player
        self.current_turn = 0
        self.max_turns = 100
        self.build_project = None

    def get_empty_tile_list(self):
        board = self.player.get_board()
        empty_tile_list = []
        for r_i, row in enumerate(board):
            for c_i, col in enumerate(row):
                if isinstance(board[r_i, c_i], EmptyResource):
                    empty_tile_list.append((r_i, c_i))
        return empty_tile_list
    
    def is_terminal(self):
        return len(self.get_empty_tile_list()) == 0
    
    def apply_action(self, action):
        resource, tile_coords = action

        current_state = copy.copy(self)
        new_player = copy.deepcopy(self.player)

        row, col = tile_coords
        current_state.player = new_player
        new_player.board[row][col] = resource
        current_state.current_turn += 1
        current_state.auto_build()
        return current_state

    def auto_build(self):
        """
        Construct one building if possible
        """
        try:
            coord_dictionary, build_options, placement_display = (
                find_all_placements(self.player, self.player.get_buildable_cards())
            )
            if not coord_dictionary:
                return

            for build_option in build_options:
                if not build_option:
                    continue

                for building_dict in build_option.values():
                    try:
                        self.player.construct(building_dict, {})
                        self.player.board = self.player.get_board()
                        return
                    except:
                        continue
        
        except:
            pass

    def evaluate(self):
        try:
            score = get_score(self, self.player, simulated_scoring=True)
            if self.finished:
                print(f"Score: {score}")

            normalised_score = (score + 16) / 100
            return max(0, min(1, normalised_score))
        except:
            return self.heuristic_evaluate()

    def heuristic_evaluate(self):
        score = 0
        building_count = 0
        resource_count = 0

        for row in self.player.get_board():
            for tile in row:
                if isinstance(tile, EmptyResource):
                    continue
                elif isinstance(tile, Card):
                    building_count += 1
                else:
                    resource_count += 1

        if building_count < resource_count:
            score -= resource_count - building_count

        total_placements = building_count + resource_count
        score += total_placements * 0.5

        return max(0, min(1, score / 50))


def run_mcts():
    mcts_agent = MCTSAgent("Agent")
    monument = rdm.choice(monuments_deck)
    player = Player(1, monument, mcts_agent)
    print(player.get_monument())
    print(player.get_monument().__str__())
    player.all_cards = mcts_agent.mcts.community_cards + [monument]
    board_state = BoardState(player)
    current_turn = 0

    while not board_state.is_terminal() and current_turn < 100:
        print(f"\nTurn {current_turn + 1}")

        current_node = MCTSNode(board_state)
        action = mcts_agent.choose_action(board_state, player)
        print(f"Agent chose {action[0]}, {action[1]}")
        board_state = board_state.apply_action(action)
        current_turn += 1
        player = board_state.player
        print(player.get_display_board())
        score = board_state.evaluate()
        print(score)

    board_state.finished = True
    print("Game finished.")
    final_score = board_state.evaluate()
    print(f"Final score: {final_score}")


if __name__ == "__main__":
    run_mcts()
