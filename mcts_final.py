import random as rdm
import copy
import json
from tqdm import tqdm

from gymnasium import Env
from gymnasium.spaces import MultiDiscrete

# import your existing functions/classes; adjust paths as needed
from player import Player
from agent import Agent
from choices import *
from cards import *
from resources import *
from layout_variants import find_all_placements, create_variants
from placement_check import find_all_layouts, score_action, actions_equal
from score import get_score
from observation import get_observation

# Import the MCTSAgent you provided. Adjust the module name/path if necessary.
# from mcts_module import MCTSAgent
# If MCTSAgent is in the same module or another file, import accordingly.
from mcts_sp import MCTSAgent   # <-- change this to the actual path/name


class TinyTownsEnv(Env):
    """
    Fully automated Tiny Towns environment: every decision uses an MCTSAgent
    (or falls back to simple heuristics).
    """

    def __init__(self, iterations_per_agent=20, mcts_explore=1.414):
        self.dictionary_of_players = {}
        self.dictionary_of_agents = {}
        self.cottage_choice = cottage
        self.farm_choice = farm
        self.factory_choice = factory
        self.tavern_choice = tavern
        self.chapel_choice = chapel
        self.theatre_choice = theatre
        self.well_choice = well

        self.get_observation = get_observation
        self.game_data = []

        # You can make number_of_players configurable; for now default to 2
        self.number_of_players = 2

        self.action_space = MultiDiscrete(
            [
                5,  # RESOURCE INDEX
                16,  # TILE ID INDEX
                2,  # NO/ YES
                8,  # BUILDING TYPE
                7,  # BUILDING TYPE WITHOUT MONUMENT
            ]
        )

        # choose random community cards as before
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

        # Create MCTS agents and players
        for player_id in range(1, self.number_of_players + 1):
            # instantiate an MCTSAgent (tune iterations/exploration as desired)
            mcts_agent = MCTSAgent(f"Player{player_id}_MCTS", iterations=iterations_per_agent, exploration_const=mcts_explore)
            self.dictionary_of_agents[player_id] = mcts_agent

        # Shuffle assignment of monuments/agents to players and create Player objects
        agent_keys = list(self.dictionary_of_agents.keys())
        rdm.shuffle(agent_keys)

        for player_idx in range(1, self.number_of_players + 1):
            monument_choice = rdm.choice(monuments_deck)
            agent_for_player = self.dictionary_of_agents[agent_keys[player_idx - 1]]
            player = Player(player_idx, monument_choice, agent_for_player)
            # give each player the global card set + their monument (as in your original code)
            player.all_cards = self.card_choices + [player.get_monument()]
            self.dictionary_of_players[player_idx] = player
            # remove used monument so unique monuments (matches original logic)
            monuments_deck.remove(player.get_monument())

        self.player_queue = list(self.dictionary_of_players.keys())
        self.master_builder_queue = self.player_queue.copy()

    # -------------------------
    # Helper utilities
    # -------------------------
    def resource_to_id(self, resource):
        """Return the key for resource in resource_dict, or None."""
        for k, v in resource_dict.items():
            if v is resource:
                return k
        return None

    def choose_master_resource_and_tile(self, player):
        """
        Use player's agent (prefer choose_resource_and_tile or select_resource_and_tile)
        to pick (resource, tile_coords). If the agent returns ids, convert as needed.
        """
        agent = player.get_agent()
        # prefer new MCTS interface
        if hasattr(agent, "select_resource_and_tile"):
            try:
                resource, tile_coords = agent.select_resource_and_tile(self, player)
                return resource, tile_coords
            except Exception:
                pass

        # fallback to older select_resource_and_tile interface if present
        if hasattr(agent, "select_resource_and_tile"):
            try:
                # assume it returns (resource_id, tile_index) as in step()
                res_id, tile_index = agent.select_resource_and_tile(self, player)
                resource = resource_dict[res_id]
                return resource, board_tile_dict[tile_index]
            except Exception:
                pass

        # ultimate fallback: random
        empty_tiles = [k for k, v in board_tile_dict.items() if player.board[v] == empty]
        if not empty_tiles:
            return wood, (0, 0)
        tile_index = rdm.choice(empty_tiles)
        resource_choice = rdm.choice(list(resource_dict.values()))
        return resource_choice, board_tile_dict[tile_index]

    def choose_tile_for_resource(self, player, resource):
        """
        If a tile must be chosen for a resource and we want an MCTS decision,
        wrap a short search by MCTS agent to place that particular resource.
        We'll ask the agent for its usual choice and accept if resource matches,
        otherwise fallback to heuristic placement.
        """
        # Prefer agent decision if possible
        agent = player.get_agent()
        if hasattr(agent, "select_resource_and_tile"):
            try:
                chosen_resource, tile_coords = agent.select_resource_and_tile(self, player)
                # if agent picked the same resource, use that tile
                if chosen_resource.__str__() == resource.__str__():
                    return tile_coords
            except Exception:
                pass

        # fallback heuristic: place on a random empty tile
        empty_positions = [pos for pos in player.get_board() if True]  # won't use; we'll compute coordinates
        empties = []
        for i, row in enumerate(player.get_board()):
            for j, tile in enumerate(row):
                if tile == empty:
                    empties.append((i, j))
        if empties:
            return rdm.choice(empties)
        return (0, 0)

    def decide_warehouse_store(self, player, resource_id):
        """
        Simple heuristic for warehouse: store if there's room and
        we don't already have this resource there (and randomly).
        """
        if len(player.get_warehouse_resources()) < player.warehouse_capacity:
            if resource_id not in player.get_warehouse_resources():
                # store with 40% probability (tweakable)
                return rdm.random() < 0.4
        return False

    def decide_build(self, acting_player):
        """
        Decide whether to build and which build to perform.
        Strategy: Evaluate all build choices by simulating the effect on a deep-copy
        of the player (applying construct), then pick the build that yields the
        highest immediate score (get_score). If none improve, skip building.
        """
        coord_dictionary, build_options, placement_display = find_all_placements(
            acting_player, acting_player.get_buildable_cards()
        )
        if not coord_dictionary:
            return None  # nothing to build

        best_score = -1e9
        best_choice = None
        # iterate through placement_display keys (human-readable) and corresponding build options
        for key_idx, option_key in enumerate(placement_display):
            candidate_list = placement_display[option_key]
            if not candidate_list:
                continue
            # each option corresponds to build_options[key_idx]
            build_dict = build_options[key_idx] if key_idx < len(build_options) else None
            if not build_dict:
                continue

            # build_dict maps possible placements; evaluate each placement choice
            for placement_choice_key, building_dict in build_dict.items():
                try:
                    # simulate construction on a deep-copy of the player
                    player_copy = copy.deepcopy(acting_player)
                    # construct expects building dict and dictionary_of_players in your implementation;
                    # pass an empty dict for dictionary_of_players if not needed
                    player_copy.construct(building_dict, dictionary_of_players={})
                    # evaluate with get_score (you may want to use a simulated scoring)
                    score_after = get_score(self, player_copy, simulated_scoring=True)
                    if score_after > best_score:
                        best_score = score_after
                        best_choice = (building_dict, placement_choice_key)
                except Exception:
                    continue

        # If best score is not an improvement or no best_choice -> skip
        if best_choice:
            return best_choice[0]  # return building_dict to pass to construct
        return None

    # -------------------------
    # Main game loop (fully automated)
    # -------------------------
    def play(self):
        finished = False
        players_finished = 0

        while not finished:
            first_player = self.master_builder_queue[0]
            acting_player = self.dictionary_of_players[first_player]

            # If fort_ironweed present, skip as original logic; otherwise run the round
            if fort_ironweed not in acting_player.board or len(self.master_builder_queue) == 1:
                # MASTER BUILDER: choose resource & tile using agent
                resource_obj, tile_coords = self.choose_master_resource_and_tile(acting_player)
                # Convert resource to id if needed
                resource_id = self.resource_to_id(resource_obj)
                resource_choice = resource_obj

                # RESOURCE PLACEMENT ROUND
                for each_player in list(self.master_builder_queue):
                    current_player = self.dictionary_of_players[each_player]
                    # If player has factory resource options, allow them to choose differently:
                    if resource_id in current_player.get_factory_resources():
                        # agent may choose a different resource when it's their turn
                        chosen_resource, chosen_tile = self.choose_master_resource_and_tile(current_player)
                        resource_choice = chosen_resource
                    else:
                        resource_choice = resource_obj

                    # Warehouse logic: decide whether to place in warehouse
                    # Using decision heuristic
                    resource_id_choice = self.resource_to_id(resource_choice)
                    if len(current_player.get_warehouse_resources()) < current_player.warehouse_capacity:
                        if self.decide_warehouse_store(current_player, resource_id_choice):
                            current_player.warehouse_resources.append(resource_id_choice)
                            # if they stored the resource, skip placing on board this round for them
                            continue

                    # place resource on an empty tile (use MCTS to pick tile where possible)
                    # If agent has already selected a tile in choose_master_resource_and_tile that matches the resource,
                    # you could use that; otherwise pick a heuristic tile.
                    # We'll ask agent for tile specifically:
                    tile_coords = self.choose_tile_for_resource(current_player, resource_choice)

                    # ensure tile is empty; if not, fallback random:
                    if current_player.board[tile_coords] != empty:
                        # find random empty tile
                        empties = []
                        for i, row in enumerate(current_player.board):
                            for j, t in enumerate(row):
                                if t == empty:
                                    empties.append((i, j))
                        if empties:
                            tile_coords = rdm.choice(empties)
                        else:
                            # no empty tiles
                            continue

                    current_player.board[tile_coords] = resource_choice

                    # update filled flag if board has no empty
                    if empty not in current_player.board:
                        current_player.board_is_filled = True

                # BUILDING ROUND
                for each_player in list(self.master_builder_queue):
                    current_player = self.dictionary_of_players[each_player]
                    # iterate building choices until no further builds
                    while True:
                        coord_dictionary, build_options, placement_display = find_all_placements(
                            current_player, current_player.get_buildable_cards()
                        )
                        if not coord_dictionary:
                            break
                        # ask the automated builder whether to build and which build
                        build_choice_dict = self.decide_build(current_player)
                        if build_choice_dict:
                            try:
                                current_player.construct(build_choice_dict, dictionary_of_players=self.dictionary_of_players)
                            except Exception:
                                break
                            # continue to see if more builds possible
                        else:
                            # skip building for this player
                            break

                    current_player.score = get_score(self, current_player)
                    # optional printing for debugging
                    print(f"{current_player} score: {current_player.score}")

            else:
                # fort_ironweed branch: skip as original behaviour
                print(fort_ironweed_turn_skip_text.format(acting_player))

            # Rotate master builder queue (same as your original)
            last_played = self.master_builder_queue.pop(0)
            self.master_builder_queue.append(last_played)

            # Check for finished players (no empty tiles)
            for each_player in list(self.dictionary_of_players.keys()):
                player_obj = self.dictionary_of_players[each_player]
                if player_obj.get_board_is_filled():
                    if each_player in self.master_builder_queue:
                        players_finished += 1
                        player_obj.finish_position = players_finished
                        self.master_builder_queue.remove(each_player)

            if not self.master_builder_queue:
                finished = True

        # GAME COMPLETE - compute final scores and declare winner(s)
        print(game_completion_text)
        player_scores = {}
        for each_player in self.player_queue:
            player = self.dictionary_of_players[each_player]
            player.score = get_score(self, player)
            player_scores[player] = player.score

        for player_obj, score in player_scores.items():
            print("{} scores {}VP!".format(player_obj, score))

        winning_player = max(player_scores, key=player_scores.get)
        joint_winners = [winning_player]
        for player_obj, score in player_scores.items():
            if player_obj != winning_player and score == player_scores[winning_player]:
                joint_winners.append(player_obj)
        print("{} win!".format([winner.__str__() for winner in joint_winners]))

    # convenience wrappers from original class
    def get_card_choices(self):
        return [el for el in self.card_choices]

    def show_card_choices(self):
        return [el.__str__() for el in self.card_choices]

    def empty_tile_action_space(self):
        actions = []
        # This function requires a player context to make sense; left as-is for compatibility
        return actions

    def record_game(self):
        game_data = {
            "card_choices": self.show_card_choices(),
            "players": []
        }
        for each_player in self.player_queue:
            player = self.dictionary_of_players[each_player]
            player_data = {
                "player_id": each_player,
                "agent": str(player.get_agent()),
                "monument": player.get_monument().__str__(),
                "final score": player.score
            }
            game_data["players"].append(player_data)
        self.game_data.append(game_data)

    def export_data(self, file_path="game_data.json"):
        with open(file_path, "w") as f:
            json.dump(self.game_data, f, indent=2)


if __name__ == "__main__":
    game = TinyTownsEnv()
    game.play()