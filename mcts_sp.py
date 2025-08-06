from player import Player
from agent import Agent
import random as rdm
from cards import *
from choices import *
import copy
from layout_variants import find_all_placements, create_variants
from score import get_score
from joblib import Parallel, delayed
import math
import json
import numpy as np


class BoardState:
    def __init__(self, player=None):
        self.player = player if player else self.create_player()
        self.finished = False

        self.cottage_choice = rdm.choice(cottage_deck)
        self.farm_choice = rdm.choice(farm_deck)
        self.factory_choice = rdm.choice(factory_deck)
        self.tavern_choice = rdm.choice(tavern_deck)
        self.chapel_choice = rdm.choice(chapel_deck)
        self.theatre_choice = rdm.choice(theatre_deck)
        self.well_choice = rdm.choice(well_deck)

        self.card_choices = [
            self.cottage_choice,
            self.farm_choice,
            self.factory_choice,
            self.tavern_choice,
            self.chapel_choice,
            self.theatre_choice,
            self.well_choice,
        ]

        self.current_turn = 0
        self.max_turns = 5

    def get_card_choices(self):
        return self.card_choices

    def create_player(self):
        monument = rdm.choice(monuments_deck)
        single_agent = Agent(1)
        return Player(1, monument, single_agent)

    def get_empty_tile_list(self):
        empty_list = []
        for r_i, row in enumerate(self.player.get_board()):
            for t_i, tile in enumerate(row):
                if isinstance(tile, EmptyResource):
                    empty_list.append((r_i, t_i))
        return empty_list

    def get_empty_tile_count(self):
        return len(self.get_empty_tile_list())

    def is_terminal(self):
        empty_count = self.get_empty_tile_count()
        return empty_count == 0 or self.max_turns <= self.current_turn

    def apply_action(self, action):
        resource, tile_coords = action

        new_state = copy.deepcopy(self)

        new_state.player.board[tile_coords] = resource
        new_state.current_turn += 1

        new_state.auto_build()

        return new_state

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
            score = get_score(self, self.player)
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


class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state

        self.parents = []
        self.children = []

        self.visits = 0
        self.total_reward = 0
        self.untried_actions = None

        if parent:
            self.add_parent(parent, action)

    def add_parent(self, parent, action):
        self.parents.append((parent, action))

    def is_fully_expanded(self):
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def is_leaf(self):
        return len(self.children) == 0
    
    def get_legal_actions(self):
        empty_tiles = self.state.get_empty_tile_list()

        if 8 < len(empty_tiles):
            tile_sample = rdm.sample(empty_tiles, min(6, len(empty_tiles)))
        actions = []
        for tile_coords in tile_sample:
            for resource in resource_dict.values():
                actions.append((resource, tile_coords))
        return actions

    def ucb_score(self, exploration_const=1.414):
        if self.visits == 0:
            return float("inf")

        exploitation = self.total_reward / self.visits
        
        if self.parents:
            parent_visits = max(parent.visits for parent, action in self.parents)
            exploration = exploration_const * math.sqrt(
                math.log(parent_visits) / self.visits
            )
        else:
            exploration = 0

        return exploitation + exploration

    def select_best_child(self, exploration_const=1.414):
        return max(self.children, key=lambda child: child.ucb_score(exploration_const))

    def add_child(self, action, state):
        """
        Add node to tree
        """
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


class MCTS:
    def __init__(self, exploration_const=1.414, max_iterations=10):
        self.exploration_const = exploration_const
        self.max_iterations = max_iterations
        self.transposition_table = {}

    def get_transposition_table(self):
        return self.transposition_table

    def get_board_varieties(self, state):
        boards = create_variants(state.player.get_display_board())
        new_array = np.array([str(board) for board in boards])
        boards = np.unique(new_array)
        return boards

    def get_or_create_node(self, state, parent=None, action=None):
        board_varieties = self.get_board_varieties(state)
        for board in board_varieties:
            state_hash = str(board)
            if state_hash in self.get_transposition_table():
                return
        state_hash = sorted(board_varieties)[0]
        node = MCTSNode(state, parent, action)
        self.transposition_table[str(state_hash)] = {
                "parents": [str(el[0].state.player.get_display_board()) for el in node.parents],
                "visits": node.visits,
                "reward_sum": node.total_reward,
                "average_reward": node.total_reward / max(1, node.visits),
                "turn": (
                    node.state.current_turn
                    if hasattr(node.state, "current_turn")
                    else 0
                ),
                "terminal": (
                    node.state.is_terminal()
                    if hasattr(node.state, "is_terminal")
                    else False
                ),
            }
        return node

    def search(self, current_state):
        root_node = MCTSNode(current_state)

        for iteration in range(self.max_iterations):
            node = self.select(root_node)

            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = self.expand(node)

            reward = self.simulate(node)
            node.backpropagate(reward)

        if root_node.children:
            best_child = max(root_node.children, key=lambda child: child.visits)
            for parent, action in best_child.parents:
                if parent == root_node:
                    return action
            actions = root_node.get_legal_actions()
            return rdm.choice(actions) if actions else None
        else:
            actions = root_node.get_legal_actions()
            return rdm.choice(actions) if actions else None

    def select(self, node):
        while not node.is_leaf() and not node.state.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.select_best_child(self.exploration_const)
        return node

    def expand(self, node):
        if node.untried_actions is None:
            node.untried_actions = node.get_legal_actions()
            rdm.shuffle(node.untried_actions)

        if node.untried_actions:
            action = node.untried_actions.pop()
            new_state = node.state.apply_action(action)
            child = self.get_or_create_node(new_state, node, action)

            if child:
                if child not in node.children:
                    node.children.append(child)
                    if str(node.state.player.get_display_board()) not in child.parents:
                        child.add_parent(node, action)
                return child
        return node

    def simulate(self, node):
        current_state = copy.deepcopy(node.state)

        simulation_depth = 0
        max_depth =10

        while not current_state.is_terminal() and simulation_depth < max_depth:
            actions = node.get_legal_actions()
            if not actions:
                break

            action = rdm.choice(actions)
            current_state = current_state.apply_action(action)
            simulation_depth += 1
        return current_state.evaluate()

    def save_transposition_table(self, filename="transposition_table.json"):
        table = {}

        for state_hash, node_values in self.get_transposition_table().items():
            table[str(state_hash)] = {
                "parents": [str(el) for el in node_values["parents"]],
                "visits": node_values["visits"],
                "reward_sum": node_values["reward_sum"],
                "average_reward": node_values["reward_sum"] / max(1, node_values["visits"]),
            }
        with open(filename, "w") as f:
            json.dump(table, f, indent=4)

    def load_transposition_table(self, filename="transposition_table.json"):
        with open(filename, "r") as f:
            table = json.load(f)
            return table


class MCTSAgent:
    def __init__(self, name, iterations=20, exploration_const=1.414):
        self.name = name
        self.mcts = MCTS(exploration_const, iterations)
        self.game_state = None

    def choose_resource_and_tile(self, game, player):
        if self.game_state is None:
            self.game_state = BoardState(player)
            self.game_state.card_choices = getattr(
                game, "card_choices", self.game_state.card_choices
            )
        else:
            self.game_state.player = player

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
            else:
                return wood, (0, 0)


def test_mcts():
    mcts_agent = MCTSAgent("Agent Name", iterations=10)

    monument = rdm.choice(monuments_deck)
    player = Player(1, monument, mcts_agent)

    game_state = BoardState(player)
    mcts_agent.mcts.get_or_create_node(game_state)
    print(mcts_agent.mcts.transposition_table)
    load_dict = mcts_agent.mcts.load_transposition_table()
        
    if load_dict:
        mcts_agent.mcts.transposition_table = load_dict
    print(mcts_agent.mcts.transposition_table)

    player.all_cards = game_state.get_card_choices() + [monument]
    print([card.__str__() for card in player.get_all_cards()])

    current_turn = 0
    while not game_state.is_terminal() and current_turn < 90:
        print(f"\nTurn {current_turn + 1}")

        action = mcts_agent.choose_resource_and_tile(game_state, player)
        print(f"Agent chose {action[0]}, {action[1]}")

        game_state = game_state.apply_action(action)
        print(game_state.player.get_display_board())
        current_turn += 1

        try:
            score = game_state.evaluate()
            print(f"Current evaluation: {score:.3f}")
        except:
            print("Could not evaluate")

    print(mcts_agent.mcts.get_transposition_table())
    mcts_agent.mcts.save_transposition_table()
    print("GAME COMPLETE")
    game_state.finished = True
    print(f"Final Score: {game_state.evaluate()}")

    return game_state


if __name__ == "__main__":
    test_mcts()
