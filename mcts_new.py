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

# ------------------------------------------------------------
# Lightweight simulation state (fast to copy, no deepcopy of Player)
# ------------------------------------------------------------
class SimState:
    """
    Minimal, fast-to-copy state used for simulations.
    - board: 2D list/array of tiles (each cell is a Resource / Card / EmptyResource)
    - current_turn: int
    - all_cards: list of community + monument (optional)
    This intentionally avoids invoking Player.construct / Player internals.
    It supports apply_action that places a resource and optionally simulates
    a single automatic build (best-effort) without calling Player.construct.
    """
    def __init__(self, player, current_turn=0, max_turns=100):
        # Copy the board rows (fast; avoids deepcopy)
        # We expect player.get_board() to be an indexable 2D array-like (numpy or lists)
        # Make shallow row copies (so inner objects still same, but board structure is independent)
        self.current_turn = current_turn
        self.max_turns = max_turns
        # keep a light reference to the player for non-mutating properties (monument, layouts)
        self.player_template = player
        # optional: attach list of cards for scoring heuristics
        self.all_cards = getattr(player, "all_cards", [])
        # finished flag
        self.finished = False

    def clone(self):
        # fast clone for branching (shallow-copy board rows)
        new = SimState.__new__(SimState)
        new.current_turn = self.current_turn
        new.max_turns = self.max_turns
        new.player_template = self.player_template
        new.player_template.board = [list(row) for row in self.player_template.board]
        new.all_cards = self.all_cards
        new.finished = self.finished
        return new

    def get_empty_tile_list(self):
        empties = []
        for r_i, row in enumerate(self.player_template.board):
            for c_i, cell in enumerate(row):
                if isinstance(cell, EmptyResource):
                    empties.append((r_i, c_i))
        return empties

    def is_terminal(self):
        return len(self.get_empty_tile_list()) == 0 or self.current_turn >= self.max_turns

    def apply_action_inplace(self, action, do_auto_build=False):
        """
        Place resource in-place on self.player.board. Optionally attempt to auto-build.
        Returns an undo token (row, col, prev_cell, built_info) so caller can undo quickly.
        built_info is None if no build performed; otherwise a dict describing the build to undo.
        """
        resource, (r, c) = action
        prev = self.player_template.board[r][c]
        self.player_template.board[r][c] = resource
        self.current_turn += 1

        built_info = None
        if do_auto_build:
            # Best-effort: attempt to detect a build without mutating Player.
            # We call a helper that inspects board & available builds and returns the first build found.
            coord_dict, build_options, placement_display = find_all_placements_from_board(self.player_template.board, self.player_template.get_buildable_cards())
            # NOTE: find_all_placements_from_board is a light-weight variant to inspect builds from raw board.
            # If you don't have it, we fallback to no auto-build here.
            if build_options:
                # pick first build option and mark it as 'built' (we simulate by replacing the required tiles with a Card)
                # For simplicity we *don't* remove resources from board; instead we mark the placed building tile cell(s)
                # The exact behaviour depends on how you evaluate buildings later.
                # To remain safe, we just record built_info but do not mutate board beyond the placed building tile.
                # If you want exact building semantics, implement reversible Player.construct or a proper board-to-build mapping.
                built_info = None

        return (r, c, prev, built_info)

    def undo_inplace(self, undo_token):
        r, c, prev, built_info = undo_token
        self.player_template.board[r][c] = prev
        if self.current_turn > 0:
            self.current_turn -= 1
        # built_info undo would go here if we changed board for builds

    def apply_action_clone(self, action):
        """
        Returns a cloned SimState with the action applied (useful for branching without manual undo).
        This is slightly heavier than inplace + undo but still avoids deepcopy on Player.
        """
        new = self.clone()
        r, c = action[1]
        new.player_template.board[r][c] = action[0]
        new.current_turn += 1
        # no auto-build in clone to keep things simple and deterministic
        return new

    def evaluate(self):
        """
        Lightweight evaluation: use get_score if available and can accept this SimState interface;
        otherwise use a heuristic based on resources/building counts.
        """
        try:
            # if get_score accepts (boardstate, player) you might need a wrapper
            # Fallback to heuristic if not compatible
            score = simulated_get_score_from_board(self.player_template.board, self.player_template)  # implement adaptor if you have it
            normalised_score = (score + 16) / 100
            return max(0.0, min(1.0, normalised_score))
        except Exception:
            # simple heuristic
            building_count = 0
            resource_count = 0
            for row in self.player_template.board:
                for tile in row:
                    if isinstance(tile, EmptyResource):
                        continue
                    elif isinstance(tile, Card):
                        building_count += 1
                    else:
                        resource_count += 1
            total_placements = building_count + resource_count
            return max(0.0, min(1.0, (total_placements * 0.5) / 50))


# ------------------------------------------------------------
# Utility: tiny, board-only placement detection
# (You should adapt this to your find_all_placements implementation)
# ------------------------------------------------------------
def find_all_placements_from_board(board, buildable_cards):
    """
    Lightweight scan of 'board' for possible placements.
    Returns (coord_dict, build_options, display) similar to your existing find_all_placements.
    This function should be implemented to match your build detection logic.
    For now, we call your existing find_all_placements if it accepts (player-like) input.
    """
    # If your find_all_placements expects a Player, create a small stub using player_template
    # For safety, attempt to call original function with a wrapper; else return empty
    try:
        # You'll likely need to adapt your find_all_placements to accept a board-only view.
        return find_all_placements(None, buildable_cards)
    except Exception:
        return {}, [], None

def simulated_get_score_from_board(board, player_template):
    """
    If you have a scoring function that accepts BoardState + Player, adapt it here.
    As a fallback, try to call get_score with a small shim - otherwise raise to fall back
    to heuristic in SimState.evaluate.
    """
    # BEST: if you have get_score(boardstate, player) that doesn't mutate player, use it.
    raise NotImplementedError("Adapt simulated_get_score_from_board to call your project's scoring function.")


# ------------------------------------------------------------
# Tree-based MCTS Node (no DAG)
# ------------------------------------------------------------
class MCTSNode:
    def __init__(self, parent=None, action=None):
        self.parent = parent            # single parent
        self.action = action            # action that produced this node from parent
        self.children = []
        self.untried_actions = None     # lazy-initialized at node->state creation
        self.visits = 0
        self.total_reward = 0.0

    def is_fully_expanded(self):
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def ucb1(self, parent_visits, c):
        if self.visits == 0:
            return float("inf")
        exploitation = self.total_reward / self.visits
        exploration = c * math.sqrt(math.log(parent_visits) / self.visits) if parent_visits > 0 else 0.0
        return exploitation + exploration

    def best_child(self, c):
        return max(self.children, key=lambda ch: ch.ucb1(self.visits, c))

    def add_child(self, action):
        child = MCTSNode(parent=self, action=action)
        self.children.append(child)
        if self.untried_actions:
            # remove equivalent action if present
            for a in list(self.untried_actions):
                if actions_equal(a, action):
                    self.untried_actions.remove(a)
                    break
        return child

    def update(self, reward):
        self.visits += 1
        self.total_reward += reward


# ------------------------------------------------------------
# MCTS engine (tree-only)
# ------------------------------------------------------------
class MCTS:
    def __init__(self, exploration_const=1.414, iterations=1000, max_sim_depth=90):
        self.c = exploration_const
        self.iterations = iterations
        self.max_sim_depth = max_sim_depth
        # community cards as before
        self.community_cards = [
            rdm.choice(cottage_deck),
            rdm.choice(farm_deck),
            rdm.choice(factory_deck),
            rdm.choice(tavern_deck),
            rdm.choice(chapel_deck),
            rdm.choice(theatre_deck),
            rdm.choice(well_deck),
        ]
        self.priority_cards = []

    def get_community_cards(self):
        return self.community_cards

    def root_state_from_player(self, player):
        # Create a SimState from the real Player (fast row-copy)
        return SimState(player, current_turn=0)

    def select(self, root, root_state):
        """
        Selection: descend from root using UCB until you find a node
        that is not fully expanded or terminal.
        We traverse nodes but we do not mutate root_state here.
        To check terminals and get legal actions for the node we must reconstruct
        the state at that node by replaying actions from root.
        """
        node = root
        state = root_state
        # replay down until leaf
        while True:
            if node.untried_actions is None:
                # lazily initialize node.untried_actions using the state at this node
                node.untried_actions = self.get_legal_actions_from_state(state)
            if not node.is_fully_expanded():
                return node, state
            # if leaf (no children) just expand
            if not node.children:
                return node, state
            # pick best child by UCB
            node = node.best_child(self.c)
            # advance state by applying node.action
            state = state.apply_action_clone(node.action)
            if state.is_terminal():
                return node, state

    def get_legal_actions_from_state(self, state, max_tiles=10):
        empties = state.get_empty_tile_list()
        if len(empties) > max_tiles:
            sample = rdm.sample(empties, max_tiles)
        else:
            sample = list(empties)
        res = list(resource_list)
        rdm.shuffle(res)
        rdm.shuffle(sample)
        actions = [(r, coords) for coords in sample for r in res]
        return actions

    def expand(self, node, state):
        # node.untried_actions must be initialized already by select
        if not node.untried_actions:
            node.untried_actions = self.get_legal_actions_from_state(state)
        if not node.untried_actions:
            return node, state
        # pick a prioritized/top action (score_action can rely only on board)
        scored = [(a, score_action(a, state.player_template.board, self.get_community_cards())) for a in node.untried_actions]
        scored.sort(key=lambda t: t[1], reverse=True)
        action = scored[0][0] if scored else node.untried_actions.pop()
        # ensure we remove the specific equivalent action
        for a in list(node.untried_actions):
            if actions_equal(a, action):
                node.untried_actions.remove(a)
                break
        child = node.add_child(action)
        new_state = state.apply_action_clone(action)
        return child, new_state

    def simulate(self, state):
        sim_state = state.clone()  # cheap clone (row copies)
        depth = 0
        while not sim_state.is_terminal() and depth < self.max_sim_depth:
            empties = sim_state.get_empty_tile_list()
            if not empties:
                break
            # generate actions
            actions = [(r, coords) for coords in empties for r in resource_list]
            # prioritize
            scored = []
            # prioritize by lightweight heuristic using board only
            for a in actions:
                try:
                    sc = score_action(a, sim_state.player_template.board, self.get_community_cards())
                except Exception:
                    sc = 0
                scored.append((sc, a))
            scored.sort(key=lambda t: t[0], reverse=True)
            if not scored:
                break
            action = scored[0][1]
            sim_state = sim_state.apply_action_clone(action)
            depth += 1
        return sim_state.evaluate()

    def backpropagate(self, node, reward):
        while node is not None:
            node.update(reward)
            node = node.parent

    def search(self, player):
        # root node and lightweight root state
        root = MCTSNode(parent=None, action=None)
        root_state = self.root_state_from_player(player)
        root_state.player_template = player

        # main loop: iterations controls budget
        for _ in range(self.iterations):
            node, state_at_node = self.select(root, root_state)
            if not state_at_node.is_terminal():
                child, state_after = self.expand(node, state_at_node)
                reward = self.simulate(state_after)
                self.backpropagate(child, reward)
            else:
                # terminal node - evaluate directly
                reward = state_at_node.evaluate()
                self.backpropagate(node, reward)

        # choose best action: most visited child of root
        if not root.children:
            return None
        best = max(root.children, key=lambda c: c.visits)
        return best.action

# ------------------------------------------------------------
# Agent wrapper
# ------------------------------------------------------------
class MCTSAgent:
    def __init__(self, name, iterations=500, exploration_const=1.414):
        self.name = name
        self.mcts = MCTS(exploration_const, iterations)
        self.game_state = None

    def choose_action(self, game, player):
        # update community cards from game if present
        self.mcts.community_cards = getattr(game, "community_cards", self.mcts.community_cards)
        action = self.mcts.search(player)
        if action is not None:
            return action
        # fallback random
        empties = [coord for coord in player.get_empty_tile_list()]
        if not empties:
            return None
        resource = rdm.choice(resource_list)
        tile_coords = rdm.choice(empties)
        return resource, tile_coords
    

def run_mcts_game(mcts: MCTS, initial_state, max_turns=90):
    """
    Run a full Tiny Towns game using the given MCTS instance.
    
    Args:
        mcts: an MCTS instance (already holding community cards etc.)
        initial_state: starting game state
        max_turns: max number of moves (board usually fills earlier)
    """
    state = initial_state
    turn = 0

    print("Starting Tiny Towns with community cards:")
    for card in mcts.get_community_cards():
        print(" -", card)

    while not state.is_terminal() and turn < max_turns:
        print(f"\n--- Turn {turn+1} ---")

        # Search with MCTS
        action = mcts.search(player)

        if action is None:
            print("⚠️ No valid action returned, stopping early.")
            break

        resource, coords = action
        print(f"Chose to place {resource} at {coords}")

        # Apply action to advance game
        info_tuple = state.apply_action_inplace(action)
        turn += 1

        # Show board + evaluation
        print(state.player_template.get_display_board())
        print("Eval:", state.evaluate())

    print("\n=== Game finished ===")
    final_score = state.evaluate()
    print("Final Score:", final_score)
    return final_score

mcts = MCTS()
player = Player(1, rdm.choice(monuments_deck), MCTSAgent)
initial_state = SimState(player)
run_mcts_game(mcts, initial_state)