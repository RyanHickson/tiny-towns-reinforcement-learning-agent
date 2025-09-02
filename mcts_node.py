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
from placement_check import actions_equal, score_action, find_all_layouts
import time
import json
from copy import deepcopy


class MCTSAgent:
    """
    Agent class used for instanciation of MCTS.
    Should record transposition table to persist between MCTS instances
    Should memorise tree between MCTS instances for efficiencies.
    """
    def __init__(self, name, iterations=1000, exploration_const=1.414, n_jobs=-1):
        self.name = name
        self.mcts = MCTS(exploration_const, iterations, n_jobs)
        self.game_state = None
        self.transposition_table = None

    def choose_resource_and_tile(self, game, player):
        """
        A method for performing Monte Carlo Tree Search and returning a best action tuple.
        """
        if self.game_state is None:
            self.game_state = deepcopy(game)
        else:
            self.game_state.player = player

        action = self.mcts.search(self.game_state)

        if action:
            return action
        else:
            legal = self.game_state.get_legal_actions()
            return rdm.choice(legal) if legal else None
        



class MCTSNode:
    """
    Tree node class
    """
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.untried_actions = state.get_legal_actions()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def is_leaf(self):
        return len(self.children) == 0

    def ucb_score(self, exploration_const=1.414):
        if self.visits == 0:
            return float("inf")
        exploitation = self.total_reward / self.visits
        exploration = exploration_const * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration

    def select_best_child(self, exploration_const=1.414):
        return max(self.children, key=lambda c: c.ucb_score(exploration_const))

    def add_child(self, action, state):
        child = MCTSNode(state, parent=self, action=action)
        self.children.append(child)
        return child


class MCTS:
    """
    Tree search class object
    """
    def __init__(self, exploration_const=1.414, max_iterations=1000, n_jobs=-1):
        self.exploration_const = exploration_const
        self.max_iterations = max_iterations
        self.n_jobs = n_jobs
        self.current_turn = 0
        self.random_resource_list = []
        for _ in range(100):
            self.random_resource_list.append(rdm.choice(resource_list))

    def search(self, root_state):
        root_node = MCTSNode(root_state)
        self.current_turn += 1
        if self.current_turn % 3 == 0:
            print(f"Random resource this turn: {self.random_resource_list[int(self.current_turn/3)]}")

        for _ in range(self.max_iterations):
            # Selection
            node = self.select(root_node)

            # Expansion
            if not node.state.is_terminal():
                node = self.expand(node)

            # Parallel simulation
            rewards = Parallel(n_jobs=self.n_jobs)(
                delayed(self.simulate)(node.state) for _ in range(4)
            )
            avg_reward = sum(rewards) / len(rewards)

            # Backpropagation
            self.backpropagate(node, avg_reward)

        best_child = max(root_node.children, key=lambda c: c.visits, default=None)
        return best_child.action if best_child else None

    def select(self, node):
        while not node.state.is_terminal() and node.is_fully_expanded():
            node = node.select_best_child(self.exploration_const)
        return node

    def expand(self, node):
        if not node.untried_actions:
            return node
        if self.current_turn % 3 == 0:
            limited_actions = [action for action in node.untried_actions if action[0] == self.random_resource_list[int(self.current_turn/3)]]
            if not limited_actions:
                return node
            action = rdm.choice(limited_actions)
        else:
            action = rdm.choice(node.untried_actions)
        node.untried_actions.remove(action)
        new_state = node.state.apply_action(action)
        return node.add_child(action, new_state)

    def simulate(self, state):
        rollout_state = copy.deepcopy(state)
        depth = 0
        max_depth = 60

        while not rollout_state.is_terminal() and depth < max_depth:
            actions = rollout_state.get_legal_actions()
            if not actions:
                break
            action = rdm.choice(actions)
            rollout_state = rollout_state.apply_action(action)
            depth += 1

        return rollout_state.evaluate()

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            node = node.parent



class BoardState:
    """
    Boardstate object class
    Should depend on as little as possible besides the player board
    """
    def __init__(self, player=None):
        self.player = player
        self.current_turn = 0
        self.max_turns = 100

    def get_empty_tile_list(self):
        board = self.player.get_board()
        empty_tile_list = []
        for r_i, row in enumerate(board):
            for c_i, col in enumerate(row):
                if isinstance(board[r_i, c_i], EmptyResource):
                    empty_tile_list.append((r_i, c_i))
        return empty_tile_list
    
    def get_legal_actions(self):
        empty_tiles = self.get_empty_tile_list()
        if not empty_tiles:
            return []
        legal_actions = []
        for resource in resource_list:
            for empty_tile in empty_tiles:
                legal_actions.append((resource, empty_tile))
        return legal_actions
    
    def is_terminal(self):
        return len(self.get_empty_tile_list()) == 0
    
    def apply_action(self, action):
        resource, tile_coords = action

        new_state = copy.copy(self)
        new_player = copy.deepcopy(self.player)

        row, col = tile_coords
        new_state.player = new_player
        new_player.board[row][col] = resource
        new_state.current_turn += 1
        new_state.auto_build()
        return new_state

    def auto_build(self):
        """Attempt to construct the best available building if possible."""
        try:
            coord_dict, build_options, _ = find_all_placements(
                self.player, self.player.get_buildable_cards()
            )
            if not coord_dict:
                return

            best_build = None
            best_score = -17

            for build_option in build_options:
                for building_dict in build_option.values():
                    if isinstance(building_dict["card"], WellType) and rdm.random < 0.9:
                        continue
                    # Estimate score if this build is applied
                    temp_player = copy.deepcopy(self.player)
                    try:
                        temp_player.construct(building_dict, {})
                        score = get_score(self, self.player)
                        if score > best_score:

                            best_score = score
                            best_build = building_dict
                    except:
                        continue

            if best_build:
                self.player.construct(best_build, {})
                self.player.board = self.player.get_board()
        except:
            pass

    def evaluate(self):
        """
        Return a reward from 0 to 1, reflecting likely final score.
        """
        try:
            # Prefer actual card scoring if available
            score = get_score(self, self.player)
            return score
        except:
            # Fall back to heuristic scoring
            score = 0
            building_count = 0
            resource_count = 0
            high_value_bonus = 0

            for row in self.player.get_board():
                for tile in row:
                    if isinstance(tile, EmptyResource):
                        continue
                    elif isinstance(tile, Card):
                        building_count += 1
                    else:
                        resource_count -= 0.5

            # Slightly penalize resources that don't help high-value builds
            score += high_value_bonus
            score += (building_count + resource_count) * 0.2

        # Normalize based on reasonable maximum score for the game
        max_possible_score = 100  # adjust according to game rules
        return max(0, min(1, score / max_possible_score))

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


def run_mcts(i, data_dict, monument_data_dict):
    mcts_agent = MCTSAgent("Agent", 400)
    monument = rdm.choice(monuments_deck)
    player = Player(1, monument, mcts_agent)
    monument_name = str(monument)
    if monument_name in monument_data_dict.keys():
        monument_data_dict[monument_name]["# of occurrences"] += 1
    else:
        monument_data_dict[monument_name] = dict()
        monument_data_dict[monument_name]["# of occurrences"] = 1

    cottage_choice = rdm.choice(cottage_deck)
    farm_choice = rdm.choice(farm_deck)
    factory_choice = rdm.choice(factory_deck)
    tavern_choice = rdm.choice(tavern_deck)
    chapel_choice = rdm.choice(chapel_deck)
    theatre_choice = rdm.choice(theatre_deck)
    well_choice = rdm.choice(well_deck)

    community_cards = [cottage_choice, farm_choice, factory_choice, tavern_choice, chapel_choice, theatre_choice, well_choice]
    player.all_cards = community_cards + [monument]
    print([str(card) for card in player.all_cards])
    data_dict[i]["Cards"] = [str(card) for card in community_cards]
    data_dict[i]["Monument"] = str(monument)
    data_dict[i]["Iterations"] = 150

    board_state = BoardState(player)
    current_turn = 0
    
    while not board_state.is_terminal() and current_turn < 100:
        print(f"\nTurn {current_turn + 1}")

        action = mcts_agent.choose_resource_and_tile(board_state, player)
        print(f"Agent chose {action[0]}, {action[1]}")
        board_state = board_state.apply_action(action)
        current_turn += 1
        player = board_state.player
        print(player.get_display_board())
        score = board_state.evaluate()
        print(f"Score: {score}")
        if board_state.is_terminal():
            break
    
    if len(monument_data_dict[monument_name]) == 1:
        monument_data_dict[monument_name]["Best Score"] = score
        monument_data_dict[monument_name]["Worst Score"] = score
        monument_data_dict[monument_name]["Total Score"] = score
        monument_data_dict[monument_name]["Average Score"] = score
    else:
        best_score = monument_data_dict[monument_name]["Best Score"]
        worst_score = monument_data_dict[monument_name]["Worst Score"]
        total_score = monument_data_dict[monument_name]["Total Score"]
        if best_score < score:
            monument_data_dict[monument_name]["Best Score"] = score
        elif score < worst_score:
            monument_data_dict[monument_name]["Worst Score"] = score
        
        monument_data_dict[monument_name]["Total Score"] = total_score + score

        total_score = monument_data_dict[monument_name]["Total Score"]
        occurances = monument_data_dict[monument_name]["# of occurrences"]
        monument_data_dict[monument_name]["Average Score"] = total_score/occurances

    data_dict[i]["Score"] = score
    data_dict[i]["Monument Built"] = (len(player.get_buildable_cards()) == 7)
    print("Game Completed!")
    return score
    


if __name__ == "__main__":
    data_dict = dict()
    monument_data_dict = dict()
    for i in range(1):
        timer_start = time.time()
        data_dict[i] = dict()
        run_mcts(i, data_dict, monument_data_dict)
        timer_end = time.time()
        monument_data_dict
        data_dict[i]["TimeTaken"] = timer_end - timer_start
        with open("data_dict10.json", "w") as f:
            f.write(json.dumps(monument_data_dict, indent=4))