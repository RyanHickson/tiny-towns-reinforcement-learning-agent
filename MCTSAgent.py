# TinyTowns – Unified Game + MCTSAgent (AI vs AI)
# ------------------------------------------------
# This file merges the original TinyTownsEnv turn control with the
# BoardState/MCTS decision logic into a clean, agent-driven Game class.
#
# It removes all interactive handle_input prompts and runs AI-vs-AI.
# Dependencies: your existing project modules (Player, cards, resources, scoring, etc.).
#
# Usage (example):
#   python unified_game.py
# ------------------------------------------------

import random as rdm
import copy
import math
import json
from joblib import Parallel, delayed
import numpy as np

# --- Project imports (expected to be available in your repo) ---
from player import Player
from cards import *  # provides cottage_deck, farm_deck, etc., Card classes
from resources import *  # provides resource_dict, EmptyResource
from layout_variants import find_all_placements, create_variants
from score import get_score
from placement_check import find_all_layouts, score_action, actions_equal
from choices import *

# Optional but helpful util if you have it
try:
    from observation import get_observation
except Exception:
    def get_observation(game, player_id):
        return {}


# ================================
# BoardState (agent-friendly view)
# ================================
class BoardState:
    """Immutable-ish snapshot the MCTS can reason over.
    Holds a reference to a Player and exposes helpers for legal moves,
    terminal checks, and one-step apply_action with a shallow auto-build.
    """

    def __init__(self, player=None, community_cards=None):
        self.player = player if player else self.create_player()
        self.finished = False

        # Use community cards supplied by Game, or roll random for one-off sims
        if community_cards:
            self.card_choices = list(community_cards)
        else:
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

        # Turn bookkeeping for rollout control
        self.current_turn = 0
        self.max_turns = 1000
        self.turns_since_build = 0
        self.fallback_board = None

    def get_card_choices(self):
        return self.card_choices

    def create_player(self):
        # Fallback player creation when simming without a real player
        monument = monuments_deck[0]
        single_agent = None
        return Player(1, monument, single_agent)

    def get_empty_tile_list(self):
        empty_list = []
        board = self.player.get_board()
        for r_i, row in enumerate(board):
            for c_i, tile in enumerate(row):
                if isinstance(tile, EmptyResource):
                    empty_list.append((r_i, c_i))
        return empty_list

    def get_empty_tile_count(self):
        return len(self.get_empty_tile_list())

    def is_terminal(self):
        return self.get_empty_tile_count() == 0 or self.max_turns <= self.current_turn

    def apply_action(self, action):
        """Return a NEW BoardState with the action applied and a single auto-build attempt."""
        resource, tile_coords = action

        new_state = copy.copy(self)
        new_player = copy.copy(self.player)

        if getattr(new_player, "turn", 0) == 1:
            new_state.fallback_board = copy.deepcopy(new_player.get_board())

        current_board = self.player.get_board()
        new_board = np.array([row.copy() for row in current_board])
        r, c = tile_coords
        new_board[r][c] = resource

        new_player.board = new_board
        new_state.player = new_player
        new_state.current_turn += 1

        check_before = copy.deepcopy(new_player.get_display_board())
        new_state.auto_build()
        check_after = new_player.get_display_board()
        board_after = copy.deepcopy(new_player.get_board())

        if np.array_equal(check_before, check_after):
            new_state.turns_since_build += 1
        else:
            new_state.turns_since_build = 0
            new_state.fallback_board = copy.deepcopy(board_after)

        number_of_turns_to_wait = min(4, new_state.get_empty_tile_count())
        if new_state.turns_since_build >= number_of_turns_to_wait:
            new_player.board = new_state.fallback_board
            new_state.player = new_player
            new_state.turns_since_build = 0
        return new_state

    def auto_build(self):
        """Attempt to construct ONE building if possible (greedy)."""
        try:
            coord_dict, build_options, _ = find_all_placements(
                self.player, self.player.get_buildable_cards()
            )
            if not coord_dict:
                return
            for build_option in build_options:
                if not build_option:
                    continue
                for building_dict in build_option.values():
                    try:
                        self.player.construct(building_dict, {})
                        self.player.board = self.player.get_board()
                        return
                    except Exception:
                        continue
        except Exception:
            pass

    def evaluate(self):
        """Return a rollout value in [0,1] (uses real scoring when available)."""
        try:
            score = get_score(self, self.player, simulated_scoring=True)
            normalised = (score + 16) / 100
            return max(0, min(1, normalised))
        except Exception:
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


# ======================
# MCTS Data Structures
# ======================
class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parents = []  # list of (parent_node, action_taken_from_parent)
        self.children = []
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions = None
        self.empty_tiles = []
        if parent:
            self.add_parent(parent, action)

    def add_parent(self, parent, action):
        self.parents.append((parent, action))

    def is_fully_expanded(self):
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def is_leaf(self):
        return len(self.children) == 0

    def get_legal_actions(self):
        self.empty_tiles = self.state.get_empty_tile_list()
        if len(self.empty_tiles) > 12:
            tile_sample = rdm.sample(self.empty_tiles, min(10, len(self.empty_tiles)))
        else:
            tile_sample = self.empty_tiles
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
            parent_visits = max(parent.visits for parent, _ in self.parents if parent)
            exploration = exploration_const * math.sqrt(max(1e-9, math.log(max(1, parent_visits)) / self.visits))
        else:
            exploration = 0.0
        return exploitation + exploration

    def select_best_child(self, exploration_const=1.414):
        return max(self.children, key=lambda child: child.ucb_score(exploration_const))

    def add_child(self, action, state):
        child = MCTSNode(state, self, action)
        self.children.append(child)
        return child

    def update(self, reward):
        self.visits += 1
        self.total_reward += reward

    def backpropagate(self, reward):
        self.update(reward)
        for parent, _ in self.parents:
            if parent:
                parent.backpropagate(reward)

    def prioritise_actions(self, actions, board, card_choices):
        scored_actions = []
        for action in actions:
            resource, tile_coords = action
            sim_board = copy.deepcopy(board)
            sim_board[tile_coords] = resource
            coord_dict, build_options, _ = find_all_placements(self.state.player, card_choices)
            score = 0
            if build_options:
                score += sum(len(option) for option in build_options) * 10
            scored_actions.append((score, action))
        scored_actions.sort(key=lambda x: x[0], reverse=True)
        return [action for _, action in scored_actions]


class MCTS:
    def __init__(self, exploration_const=1.414, max_iterations=15, batch_size=6):
        self.exploration_const = exploration_const
        self.max_iterations = max_iterations
        self.transposition_table = {}
        self.batch_size = batch_size

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
            board_string = str(board)
            if board_string in self.transposition_table:
                existing_node = self.transposition_table[board_string]
                existing_node.empty_tiles = state.get_empty_tile_list()
                if parent:
                    existing_node.add_parent(parent, action)
                return existing_node
        recorded_board = sorted(board_varieties)[0]
        node = MCTSNode(state, parent, action)
        node.empty_tiles = state.get_empty_tile_list()
        self.transposition_table[str(recorded_board)] = node
        return node

    def search(self, current_state):
        root_node = MCTSNode(current_state)
        root_node.empty_tiles = current_state.get_empty_tile_list()

        for _ in range(max(1, self.max_iterations // max(1, self.batch_size))):
            nodes_to_sim = []
            for _ in range(self.batch_size):
                node = self.select(root_node)
                node.empty_tiles = node.state.get_empty_tile_list()
                if not node.state.is_terminal() and not node.is_fully_expanded():
                    node = self.expand(node)
                nodes_to_sim.append(node)

            rewards = Parallel(n_jobs=-1)(delayed(self.simulate)(node) for node in nodes_to_sim)
            for node, reward in zip(nodes_to_sim, rewards):
                node.backpropagate(reward)

        # Choose the most visited child
        if root_node.children:
            best_child = max(root_node.children, key=lambda child: child.visits)
            for parent, action in best_child.parents:
                if parent == root_node:
                    return action

        # Fallback: choose a random legal action from root
        actions = []
        for tile_coords in current_state.get_empty_tile_list():
            for resource in resource_dict.values():
                actions.append((resource, tile_coords))
        return rdm.choice(actions) if actions else None

    def select(self, node):
        while not node.is_leaf() and not node.state.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.select_best_child(self.exploration_const)
            node.empty_tiles = node.state.get_empty_tile_list()
        return node

    def expand(self, node):
        if node.untried_actions is None:
            node.empty_tiles = node.state.get_empty_tile_list()
            node.untried_actions = node.get_legal_actions()

            # Prioritise clever actions from placement_check
            board = node.state.player.get_board()
            card_choices = node.state.get_card_choices()
            clever_moves = find_all_layouts(board, card_choices)

            non_empty_moves = [moves for moves in (clever_moves or []) if moves]
            scored_actions = []
            for action_list in non_empty_moves:
                for action in action_list:
                    scored_actions.append((action, score_action(action, board, card_choices)))
            scored_actions.sort(key=lambda x: x[1], reverse=True)
            top_scored_actions = [act for act, _ in scored_actions[:5]]

            for each_action in top_scored_actions:
                for untried_action in list(node.untried_actions):
                    if actions_equal(each_action, untried_action):
                        node.untried_actions.remove(untried_action)
                        action = each_action
                        new_state = node.state.apply_action(action)
                        child = self.get_or_create_node(new_state, node, action)
                        child.empty_tiles = new_state.get_empty_tile_list()
                        if child not in node.children:
                            node.children.append(child)
                            child.add_parent(node, action)
                        return child

        if node.untried_actions:
            action = node.untried_actions.pop()
            new_state = node.state.apply_action(action)
            child = self.get_or_create_node(new_state, node, action)
            child.empty_tiles = new_state.get_empty_tile_list()
            if child not in node.children:
                node.children.append(child)
                child.add_parent(node, action)
            return child
        return node

    def simulate(self, node):
        current_state = copy.deepcopy(node.state)
        simulation_depth = 0
        max_depth = 5

        while not current_state.is_terminal() and simulation_depth < max_depth:
            empty_tiles = current_state.get_empty_tile_list()
            if not empty_tiles:
                break
            actions = []
            for tile_coords in empty_tiles:
                for resource in resource_dict.values():
                    actions.append((resource, tile_coords))
            if not actions:
                break
            scored_actions = node.prioritise_actions(
                actions, current_state.player.get_board(), current_state.get_card_choices()
            )
            top = scored_actions[:3] if len(scored_actions) >= 3 else scored_actions
            action = rdm.choice(top) if top else None
            if not action:
                break
            current_state = current_state.apply_action(action)
            simulation_depth += 1
        return current_state.evaluate()

    # Optional persistence (debugging/analysis)
    def save_transposition_table(self, file_path):
        import os
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        table = {}
        for state_hash, node in self.transposition_table.items():
            table[str(state_hash)] = {
                "parents": len(node.parents),
                "visits": node.visits,
                "reward_sum": node.total_reward,
                "avg_reward": node.total_reward / max(1, node.visits),
                "children": len(node.children),
                "is_terminal": hasattr(node, "state") and node.state.is_terminal(),
            }
        with open(file_path, "w") as f:
            json.dump(table, f, indent=2)


# ================
# MCTS Agent
# ================
class MCTSAgent:
    def __init__(self, name, iterations=30, exploration_const=1.414):
        self.name = name
        self.mcts = MCTS(exploration_const, iterations)
        self.best_actions = 0

    def choose_resource_and_tile(self, game, player):
        state = BoardState(player, community_cards=game.community_cards)
        best_action = self.mcts.search(state)
        if best_action:
            self.best_actions += 1
            return best_action

        # Fallback random legal action
        empty_list = []
        board = player.get_board()
        for r in range(board.shape[0]):
            for c in range(board.shape[1]):
                if isinstance(board[r, c], EmptyResource):
                    empty_list.append((r, c))
        if empty_list:
            resource = rdm.choice(list(resource_dict.values()))
            tile_coords = rdm.choice(empty_list)
            return resource, tile_coords
        return None


# ======================
# Unified Game wrapper
# ======================
class Game:
    def __init__(self, player_count=2, agent_cls=MCTSAgent, iterations=30, seed=None):
        if seed is not None:
            rdm.seed(seed)
            np.random.seed(seed)
        self.players = []
        self.finished = False

        # Pick community cards
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

        # Create players + agents
        taken = set()
        for pid in range(1, player_count + 1):
            # Ensure unique monument choice per player if your deck enforces uniqueness
            # Here we sample without replacement via an index set
            while True:
                idx = rdm.randint(0, len(monuments_deck) - 1)
                if idx not in taken:
                    taken.add(idx)
                    monument = monuments_deck[idx]
                    break
            agent = agent_cls(f"Agent-{pid}", iterations=iterations) if agent_cls else None
            player = Player(pid, monument, agent)
            player.all_cards = self.community_cards + [monument]
            self.players.append(player)

    # Compatibility helpers
    def get_card_choices(self):
        return list(self.community_cards)

    # ------------- Core loop -------------
    def step_round(self):
        """One round where each player chooses and places a resource+tile, then we attempt auto-builds.
        This simplifies the master builder mechanic into per-player agent turns.
        """
        for player in self.players:
            if player.get_board_is_filled():
                continue
            agent = player.get_agent()
            if not agent:
                continue

            action = agent.choose_resource_and_tile(self, player)
            if action is None:
                continue
            resource, tile_coords = action

            # Place if legal
            if isinstance(player.board[tile_coords], EmptyResource):
                player.board[tile_coords] = resource
                # Greedy single-build attempt (same as in BoardState)
                try:
                    coord_dict, build_options, _ = find_all_placements(
                        player, player.get_buildable_cards()
                    )
                    if coord_dict:
                        for build_option in build_options:
                            if not build_option:
                                continue
                            for building_dict in build_option.values():
                                try:
                                    player.construct(building_dict, {})
                                    raise StopIteration  # built one – exit nested loops
                                except Exception:
                                    continue
                except StopIteration:
                    pass
                except Exception:
                    pass

            # Update score after each player's placement/build
            try:
                player.score = get_score(self, player)
            except Exception:
                player.score = 0

        # End condition
        self.finished = all(p.get_board_is_filled() for p in self.players)
        return self.finished

    def play(self, max_rounds=1000, verbose=True):
        rounds = 0
        while not self.finished and rounds < max_rounds:
            self.step_round()
            rounds += 1
        if verbose:
            self.print_results()
        return {p.get_id(): p.score for p in self.players}

    def print_results(self):
        print("\n=== GAME COMPLETE ===")
        scores = {}
        for p in self.players:
            try:
                p.score = get_score(self, p)
            except Exception:
                pass
            scores[p] = p.score
            print(f"{p} scores {p.score} VP")
        winning_player = max(scores, key=scores.get)
        winners = [winning_player]
        for p, s in scores.items():
            if p is not winning_player and s == scores[winning_player]:
                winners.append(p)
        print("Winners:", ", ".join(str(w) for w in winners))


# -----------------
# Quick smoke test
# -----------------
if __name__ == "__main__":
    game = Game(player_count=2, agent_cls=MCTSAgent, iterations=30, seed=42)
    results = game.play(verbose=True)
    print("Scores:", results)
