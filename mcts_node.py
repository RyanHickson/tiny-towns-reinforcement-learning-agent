from __future__ import annotations
import math
import random
import hashlib
import json
import msgpack
from copy import deepcopy
from typing import Dict, Optional, Tuple, List, Any

import tqdm

# --- Game engine imports (expected to exist in your project) ---
from resources import *
from choices import *
from player import Player
from placement_check import score_action
from layout_variants import find_all_placements
from layout_variants import create_variants
from score import get_score

# =============================
# Helpers & global mappings
# =============================
tile_to_index: Dict[Tuple[int, int], int] = {v: k for k, v in board_tile_dict.items()}
resource_id_by_obj: Dict[Resource, int] = {v: k for k, v in resource_dict.items()}
resource_by_str: Dict[str, Resource] = {
    str(wood): wood, str(wheat): wheat, str(glass): glass, str(brick): brick, str(stone): stone
}

# =============================
# BoardState (fixed placement)
# =============================
class BoardState:
    def __init__(self, player: Player):
        self.player = player
        self.current_turn = getattr(player, "turn", 0)
        self.max_turns = 100

    def get_empty_tile_list(self) -> List[Tuple[int, int]]:
        board = self.player.get_board()
        empties = []
        for r in range(board.shape[0]):
            for c in range(board.shape[1]):
                if isinstance(board[r, c], EmptyResource):
                    empties.append((r, c))
        return empties

    def is_terminal(self) -> bool:
        return len(self.get_empty_tile_list()) == 0

    def apply_action(self, action: Tuple[Resource, Tuple[int, int]]) -> "BoardState":
        resource, (row, col) = action
        new_state = deepcopy(self)
        new_state.player.board[row][col] = resource  # write directly into deepcopied board
        new_state.current_turn += 1
        new_state.auto_build()
        return new_state

    def auto_build(self) -> None:
        """Greedy single-build if possible (consistent with your previous heuristics)."""
        try:
            coord_dictionary, build_options, _ = find_all_placements(
                self.player, self.player.get_buildable_cards()
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
                    except Exception:
                        continue
        except Exception:
            pass

    def evaluate(self) -> float:
        """Return normalized score in [0,1]."""
        try:
            score = get_score(self, self.player, simulated_scoring=True)
            normalised = (score + 16) / 100
            return max(0.0, min(1.0, normalised))
        except Exception:
            # light heuristic fallback
            score = 0
            building_count = 0
            resource_count = 0
            for row in self.player.get_board():
                for tile in row:
                    if isinstance(tile, EmptyResource):
                        continue
                    elif getattr(tile, "__class__", None).__name__ == "Card":
                        building_count += 1
                    else:
                        resource_count += 1
            if building_count < resource_count:
                score -= (resource_count - building_count)
            score += (building_count + resource_count) * 0.5
            return max(0.0, min(1.0, score / 50.0))

# =============================
# MCTS Node
# =============================
class Node:
    """
    Node with minimal stats and children; state represented by a canonical key.
    """
    __slots__ = ("player_id", "state_key", "w", "n", "children", "is_expanded", "has_outcome")

    def __init__(self, player_id: int, state_key: str):
        self.player_id = player_id
        self.state_key = state_key
        self.w = 0.0
        self.n = 0
        self.children: Dict[Any, "Node"] = {}  # action -> Node
        self.is_expanded = False
        self.has_outcome = False

    def ucb1(self, parent_n: int, c: float = 1.414) -> float:
        if self.n == 0:
            return float("inf")
        return (self.w / self.n) + c * math.sqrt(max(1e-12, math.log(parent_n) / self.n))

    def best_child(self, c: float = 1.414) -> Tuple[Any, "Node"]:
        parent_n = max(1, sum(ch.n for ch in self.children.values()))
        best_a, best_node, best_val = None, None, -1e18
        for a, ch in self.children.items():
            val = ch.ucb1(parent_n, c)
            if val > best_val:
                best_val = val
                best_a, best_node = a, ch
        return best_a, best_node

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "state_key": self.state_key,
            "w": self.w,
            "n": self.n,
            "is_expanded": self.is_expanded,
            "has_outcome": self.has_outcome,
            "children": {}  # filled during export where child ids are known
        }

# =============================
# MCTS core with transpositions
# =============================
class MCTS:
    def __init__(
        self,
        root_state: BoardState,
        exploration_const: float = 1.2,
        allow_transpositions: bool = True,
        seed: Optional[int] = None,
        top_k_expand: int = 3,
        rollout_depth: int = 8,
        max_tile_sample: int = 10
    ):
        self.rng = random.Random(seed)
        self.C = exploration_const
        self.top_k_expand = top_k_expand
        self.rollout_depth = rollout_depth
        self.max_tile_sample = max_tile_sample

        self.transpositions: Optional[Dict[Tuple[int, str], Node]] = {} if allow_transpositions else None

        self.root_state = deepcopy(root_state)
        root_pid = self._current_player_id(root_state)
        root_key = self._state_key(root_state)
        if self.transpositions is not None:
            self.root = self.transpositions.setdefault((root_pid, root_key), Node(root_pid, root_key))
        else:
            self.root = Node(root_pid, root_key)

    # ----- public -----
    def search(self, iterations: int = 160) -> Optional[Any]:
        for _ in range(iterations):
            self._iteration()
        if not self.root.children:
            return None
        return max(self.root.children.items(), key=lambda kv: kv[1].n)[0]

    def re_root(self, state: BoardState) -> None:
        self.root_state = deepcopy(state)
        self.root = self._get_or_create_node(state)

    # ----- iteration -----
    def _iteration(self) -> None:
        s = deepcopy(self.root_state)
        path: List[Tuple[Node, Optional[Any]]] = [(self.root, None)]
        node = self.root

        # Selection
        while node.is_expanded and not node.has_outcome and node.children:
            action, child = node.best_child(self.C)
            s = s.apply_action(action)
            node = child
            path.append((node, action))

        if s.is_terminal():
            node.has_outcome = True
            reward = s.evaluate()
            self._backpropagate(path, reward)
            return

        # Expansion (one child)
        legal = self._legal_actions(s)
        if not legal:
            node.has_outcome = True
            reward = s.evaluate()
            self._backpropagate(path, reward)
            return

        scored = self._score_actions(s, legal)
        primary = [a for a, _ in scored[: self.top_k_expand]] or [a for a, _ in scored]
        action = self.rng.choice(primary)

        next_state = s.apply_action(action)
        child = self._get_or_create_node(next_state)
        node.children[action] = child
        node.is_expanded = True

        path.append((child, action))
        s = next_state

        # Rollout
        reward = self._rollout(s)
        # Backup
        self._backpropagate(path, reward)

    # ----- helpers -----
    def _current_player_id(self, state: BoardState) -> int:
        return getattr(state.player, "id", 1)

    def _state_key(self, state: BoardState) -> str:
        boards = create_variants(state.player.get_display_board())
        var_strs = [str([[str(cell) for cell in row] for row in b]) for b in boards]
        canonical = min(var_strs)
        return hashlib.md5(canonical.encode("utf-8")).hexdigest()

    def _get_or_create_node(self, state: BoardState) -> Node:
        pid = self._current_player_id(state)
        key = self._state_key(state)
        if self.transpositions is not None:
            node = self.transpositions.get((pid, key))
            if node is None:
                node = Node(pid, key)
                self.transpositions[(pid, key)] = node
            return node
        return Node(pid, key)

    def _legal_actions(self, state: BoardState) -> List[Any]:
        actions = []
        empties = state.get_empty_tile_list()
        if not empties:
            return actions
        tiles = empties if len(empties) <= self.max_tile_sample else self.rng.sample(empties, self.max_tile_sample)
        for tile in tiles:
            for resource in resource_list:
                actions.append((resource, tile))
        return actions

    def _score_actions(self, state: BoardState, actions: List[Any]) -> List[Tuple[Any, float]]:
        board = state.player.get_board()
        community_cards = getattr(state.player, "all_cards", None)
        out = []
        for a in actions:
            try:
                s = float(score_action(a, board, community_cards))
            except Exception:
                s = 0.0
            out.append((a, s))
        out.sort(key=lambda x: x[1], reverse=True)
        return out

    def _rollout(self, s: BoardState) -> float:
        depth = 0
        cur = deepcopy(s)
        while not cur.is_terminal() and depth < self.rollout_depth:
            legal = self._legal_actions(cur)
            if not legal:
                break
            top = [a for a, _ in self._score_actions(cur, legal)[:3]] or legal
            a = self.rng.choice(top)
            cur = cur.apply_action(a)
            depth += 1
        return float(cur.evaluate())

    def _backpropagate(self, path: List[Tuple[Node, Optional[Any]]], reward: float) -> None:
        for node, _ in path:
            node.n += 1
            node.w += reward

    # ----- export transposition graph -----
    def export_transposition(self) -> Dict[str, Any]:
        """
        Returns a JSON-friendly graph snapshot:
        {
          "nodes": [{...}],
          "edges": [{"from": node_id, "action": [res_str,r,c], "to": node_id}],
          "root_id": int
        }
        """
        # collect reachable nodes from root
        nodes: List[Node] = []
        node_to_id: Dict[Node, int] = {}

        def collect(n: Node):
            if n in node_to_id:
                return
            node_to_id[n] = len(nodes)
            nodes.append(n)
            for ch in n.children.values():
                collect(ch)

        collect(self.root)

        # pack nodes
        packed_nodes = []
        for n in nodes:
            packed_nodes.append({
                "player_id": n.player_id,
                "state_key": n.state_key,
                "w": n.w,
                "n": n.n,
                "is_expanded": n.is_expanded,
                "has_outcome": n.has_outcome,
            })

        # pack edges
        edges = []
        for n in nodes:
            nid = node_to_id[n]
            for action, ch in n.children.items():
                res, (r, c) = action
                edges.append({
                    "from": nid,
                    "action": [str(res), int(r), int(c)],
                    "to": node_to_id[ch]
                })

        return {
            "nodes": packed_nodes,
            "edges": edges,
            "root_id": node_to_id[self.root]
        }

    def save_transposition_json(self, path: str) -> None:
        data = self.export_transposition()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_transposition_msgpack(self, path: str) -> None:
        data = self.export_transposition()
        with open(path, "wb") as f:
            f.write(msgpack.packb(data))

# =============================
# Agent adapter to engine API
# =============================
class MCTSAgentAdapter:
    """
    Adapts MCTS to TinyTowns' agent API:
      choose_resource_and_tile(game, player) -> (resource_id, tile_index)
    """
    def __init__(self, name="MCTS", iterations=160, seed=42, C=1.2):
        self.name = name
        self.iterations = iterations
        self.C = C
        self.seed = seed
        self.inner: Optional[MCTS] = None

    def __str__(self) -> str:
        return self.name

    def choose_resource_and_tile(self, game, player) -> Tuple[int, int]:
        state = BoardState(player)
        if self.inner is None:
            self.inner = MCTS(
                root_state=state,
                exploration_const=self.C,
                allow_transpositions=True,
                seed=self.seed,
                top_k_expand=3,
                rollout_depth=8,
                max_tile_sample=10,
            )
        else:
            self.inner.re_root(state)

        action = self.inner.search(self.iterations)
        if action is None:
            empties = state.get_empty_tile_list()
            if not empties:
                return None, None
            (r, c) = random.choice(empties)
            resource_obj = random.choice(list(resource_list))
        else:
            resource_obj, (r, c) = action

        resource_id = resource_id_by_obj[resource_obj]
        tile_index = tile_to_index[(r, c)]
        return resource_id, tile_index

# =============================
# Minimal TinyTowns runner
# =============================
class TinyTownsRunner:
    """
    Lightweight, non-interactive self-play loop that relies on your Player/engine APIs.
    It:
      - sets up players and community cards
      - uses MCTSAgentAdapter for decisions
      - plays the game with greedy autobuilds (consistent with BoardState.auto_build)
      - updates scores
      - exposes the agent MCTS graph for export
    """
    def __init__(self, number_of_players: int = 2, card_choices: Optional[List[Any]] = None, seed: int = 1234):
        self.rng = random.Random(seed)
        self.number_of_players = number_of_players

        # --- community cards ---
        # If you already have game-level random community cards somewhere, set them here:
        # Example (replace with your decks if needed):
        from cards import cottage_deck, farm_deck, factory_deck, tavern_deck, chapel_deck, theatre_deck, well_deck
        if card_choices is None:
            self.card_choices = [
                self.rng.choice(cottage_deck),
                self.rng.choice(farm_deck),
                self.rng.choice(factory_deck),
                self.rng.choice(tavern_deck),
                self.rng.choice(chapel_deck),
                self.rng.choice(theatre_deck),
                self.rng.choice(well_deck),
            ]
        else:
            self.card_choices = card_choices

        # --- monuments ---
        from cards import monuments_deck
        self.monuments_deck = list(monuments_deck)
        self.rng.shuffle(self.monuments_deck)

        # --- players & agents ---
        self.players: Dict[int, Player] = {}
        for pid in range(1, number_of_players + 1):
            agent = MCTSAgentAdapter(name=f"MCTS-P{pid}", iterations=200, seed=seed + pid, C=1.2)
            monument = self.monuments_deck.pop()
            pl = Player(pid, monument, agent)
            pl.all_cards = self.card_choices + [monument]
            self.players[pid] = pl

        self.turn_order = list(self.players.keys())
        self.master_builder_queue = list(self.turn_order)

    # --- one full game ---
    def play(self) -> Tuple[List[Player], Dict[Player, int]]:
        finished = False

        while not finished:
            if not self.master_builder_queue:
                break

            first_pid = self.master_builder_queue[0]
            # master builder chooses resource+tile
            acting = self.players[first_pid]
            res_id, tile_idx = acting.get_agent().choose_resource_and_tile(self, acting)
            chosen_resource = resource_dict[res_id]

            # all players place (each selects tile for same resource)
            for pid in list(self.master_builder_queue):
                p = self.players[pid]
                p.turn = getattr(p, "turn", 0) + 1

                # let each player pick a tile for this resource
                _, tile_idx_p = p.get_agent().choose_resource_and_tile(self, p)
                rc = board_tile_dict[tile_idx_p]
                if p.get_board()[rc] == empty:
                    p.board[rc] = chosen_resource

                # autobuilds happen inside MCTS BoardState during planning,
                # but we also try greedy multi-build here to reflect a building round.
                self._building_round(p)

                # flag full boards
                if empty not in p.get_board():
                    p.board_is_filled = True

            # rotate master builder and remove finished players
            last = self.master_builder_queue.pop(0)
            self.master_builder_queue.append(last)
            to_remove = []
            for pid in self.master_builder_queue:
                if empty not in self.players[pid].get_board():
                    to_remove.append(pid)
            for pid in to_remove:
                self.master_builder_queue.remove(pid)

            finished = len(self.master_builder_queue) == 0

        # scoring
        scores: Dict[Player, int] = {}
        for p in self.players.values():
            p.score = get_score(self, p)
            scores[p] = p.score

        # winners
        best = max(scores.values()) if scores else 0
        winners = [p for p, sc in scores.items() if sc == best]
        return winners, scores
    
    def get_card_choices(self):
        return self.card_choices

    def _building_round(self, p: Player) -> None:
        """Greedy loop: keep constructing while any placement exists."""
        safety = 64  # prevent infinite loops on bad engine behavior
        while safety > 0:
            safety -= 1
            try:
                coord_dictionary, build_options, placement_display = find_all_placements(
                    p, p.get_buildable_cards()
                )
            except Exception:
                break
            if not coord_dictionary:
                break
            # choose the first available option deterministically
            for build_type in build_options:
                # chosen_idx = next(iter(build_options))
                # chosen_building_dict = build_options[chosen_idx]

                try:
                    p.player_construct(build_type, self.players)  
                    p.board = p.get_board()
                except Exception:
                    break

                if empty in p.get_board():
                    p.board_is_filled = False

                if empty in p.get_board():
                    p.board_is_filled = False

# =============================
# Training/Evaluation harness
# =============================
def run_self_play(episodes: int = 5, players: int = 2, seed: int = 777, save_graph_every: int = 1) -> None:
    """
    Runs self-play games. After each episode, dumps the transposition graph
    from Player 1's MCTS agent (as an example).
    """
    for ep in tqdm.tqdm(range(1, episodes + 1), desc="Self-play"):
        env = TinyTownsRunner(number_of_players=players, seed=seed + ep)
        winners, scores = env.play()

        # Export transposition from P1 agent, if available
        p1 = env.players[1]
        agent = p1.get_agent()
        if isinstance(agent, MCTSAgentAdapter) and agent.inner is not None:
            base = f"transpo_ep{ep}"
            agent.inner.save_transposition_json(base + ".json")
            agent.inner.save_transposition_msgpack(base + ".msgpack")

        # Optional: log outcome
        # print(f"Episode {ep}: winners {[w.__str__() for w in winners]} | scores {[ (p.__str__(), s) for p,s in scores.items() ]}")

if __name__ == "__main__":
    # Run a few episodes; transposition graphs will be saved per episode.
    run_self_play(episodes=3, players=2, seed=2025)