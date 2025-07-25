import random as rdm
from player import *
from building_layouts import *
from cards import *
from resources import *
from layout_variants import *
from agent import *
from ry import *
from ui import *
from score import get_score
from observation import get_observation
import json
from tqdm import tqdm

from gymnasium import Env
from gymnasium.spaces import MultiDiscrete

class TinyTownsEnv(Env):
    """
    Setup game environment for RL agent gameplay
    """
    def __init__(self):
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
        self.monuments_deck = monuments_deck

        self.number_of_players = 2  # handle_input(number_of_players_text, range(2,7))
        self.manual_card_selection = 0 # handle_input(manual_card_selection_text, range(3))

        for player in range(1, self.number_of_players + 1):
            self.dictionary_of_agents[player] = Agent(player)
        self.agent_keys = list(self.dictionary_of_agents.keys())


        if not self.manual_card_selection:   # Normal play, random card choices from each deck
            self.cottage_choice = rdm.choice(cottage_deck)
            self.farm_choice = rdm.choice(farm_deck)
            self.factory_choice = rdm.choice(factory_deck)
            self.tavern_choice = rdm.choice(tavern_deck)
            self.chapel_choice = rdm.choice(chapel_deck)
            self.theatre_choice = rdm.choice(theatre_deck)
            self.well_choice = rdm.choice(well_deck)

            self.card_choices = [  # Creates a list of the chosen cards for this game
                self.cottage_choice,
                self.farm_choice,
                self.factory_choice,
                self.tavern_choice,
                self.chapel_choice,
                self.theatre_choice,
                self.well_choice,
            ]
        elif self.manual_card_selection == 1:  # Allows for manual card choices for a game
            self.card_choices = []  # initialise card choice list
            for deck in all_decks:
                deck_list = []
                for card in deck:
                    deck_list.append(card.__str__())
                card_deck_dict = dict_enum(deck_list)
                card_choice_index = handle_input(choose_card_text.format(card_deck_dict), card_deck_dict)  # take player input for each deck, choosing the cards for the community pool
                self.card_choices.append(deck[card_choice_index])
        elif self.manual_card_selection == 2:
            self.card_choices = [  # Creates a list of the chosen cards for this game
                self.cottage_choice,
                self.farm_choice,
                self.factory_choice,
                self.tavern_choice,
                self.chapel_choice,
                self.theatre_choice,
                self.well_choice,
            ]



    def refill_monuments_deck(self):
        self.monuments_deck = [
        architects_guild,
        archive_of_the_second_age,
        barrett_castle,
        cathedral_of_caterina,
        fort_ironweed,
        grand_mausoleum_of_the_rodina,
        grove_university,
        mandras_palace,
        obelisk_of_the_crescent,
        opaleyes_watch,
        shrine_of_the_elder_tree,
        silva_forum,
        the_sky_baths,
        the_starloom,
        statue_of_the_bondmaker,]
        return self.monuments_deck




    def setup_players(self):
        self.monuments_deck = self.refill_monuments_deck()
        
        rdm.shuffle(self.agent_keys)  # AGENT SHUFFLE TO NOT OVERFIT TO A SPECIFIC STARTING ORDER

        if not self.manual_card_selection:
            for player in range(1, self.number_of_players + 1):
                self.dictionary_of_players[player] = Player(player, rdm.choice(self.monuments_deck), self.dictionary_of_agents[self.agent_keys[player - 1]])  # random assignment of a unique monument to each player
                self.monuments_deck.remove(self.dictionary_of_players[player].get_monument())
                self.dictionary_of_players[player].all_cards = self.card_choices + [self.dictionary_of_players[player].get_monument()]
        elif self.manual_card_selection:
            for player in range(1, self.number_of_players + 1):
                monument_names_deck = [monument.__str__() for monument in self.monuments_deck]
                monument_index = handle_input(monument_selection_text.format((player), dict_enum(monument_names_deck)), range_len(monument_names_deck))  # take player input to select a unique monument for each player

                self.dictionary_of_players[player] = Player(player, self.monuments_deck[monument_index], self.dictionary_of_agents[self.agent_keys[player - 1]])
                self.monuments_deck.remove(self.dictionary_of_players[player].get_monument())
                self.dictionary_of_players[player].all_cards = self.card_choices + [self.dictionary_of_players[player].get_monument()]
        self.player_queue = list(self.dictionary_of_players.keys())
        self.master_builder_queue = self.player_queue.copy()



        for player in self.dictionary_of_players:
            total_count = 0
            wood_count = 0
            wheat_count = 0
            glass_count = 0
            brick_count = 0
            stone_count = 0
            acting_player = self.dictionary_of_players[player]
            for card in acting_player.get_all_cards():
                layout = card.get_layout()
                for each_list in layout:
                    for el in each_list:
                        if el != wild:
                            total_count += 1
                        if el == wood:
                            wood_count += 1
                        if el == wheat:
                            wheat_count += 1
                        if el == glass:
                            glass_count += 1
                        if el == brick:
                            brick_count += 1
                        if el == stone:
                            stone_count += 1
            acting_player.resource_distribution = [total_count, wood_count, wheat_count, glass_count, brick_count, stone_count]
        return self.master_builder_queue




    def step(self, actions):
        """
        Step function for agent play
        """

        rewards = {}
        observations = {}
        done = False

        for player_id, action in actions.items():
            player = self.dictionary_of_players[player_id]
            agent = player.get_agent()

            resource_id, tile_index = agent.board_scan(self, player)
            resource = resource_dict[resource_id]
            if player.board[board_tile_dict[tile_index]] == empty:
                player.board[board_tile_dict[tile_index]] = resource

            player.score = get_score(self, player)
            rewards[player_id] = player.score
            observations[player_id] = get_observation(self, player_id)

        done = all(player.get_board_is_filled() for player in self.dictionary_of_players)

        return rewards, observations, done





    def reset(self):
        """
        Restart play environment
        """
        # self.__init__()
        self.play()




    def record_game(self):
        game_data = {
            "card_choices": self.show_card_choices(),
            "players": []
        }
        for each_player in self.player_queue:
            player = self.dictionary_of_players[each_player]
            board = [player.board[board_tile_dict[el]].__str__() for el in range(1,17)]
            player_data = {
                "player_id": each_player,
                "agent": player.get_agent().__str__(),
                "monument": player.get_monument().__str__(),
                "final score": player.score,
                "building, turn built": player.construction_list,
                "board": board
            }
            game_data["players"].append(player_data)
        self.game_data.append(game_data)
        self.export_data()




    def get_initial_state(self):
        """
        Observe initial game conditions
        """
        game_setup_dict = {}
        game_setup_dict["community_cards"] = [card.__str__() for card in self.card_choices]
        for each_player in self.player_queue:
            player = self.dictionary_of_players[each_player]
            game_setup_dict[player.__str__()] = {
            "agent": player.get_agent().__str__(),
            "monument": player.get_monument().__str__(),
            }
        return game_setup_dict



    def export_data(self):
        with open("data.json", "a") as f:
            for game in self.game_data:
                f.write(json.dumps(game, indent=4) +"\n")
        self.game_data = []




    def start_of_game(self):
        # SETUP
        self.finished = False
        self.players_finished = 0
        # print(self.get_initial_state())
        return self.finished, self.players_finished




    def start_of_turn(self):
        if self.master_builder_queue:
            self.first_player = self.master_builder_queue[0]   # player one becomes first player to act
            self.acting_player = self.dictionary_of_players[self.first_player]   # assign acting player to be first master builder
            return self.first_player, self.acting_player
        else:
            self.first_player = False
            self.acting_player = False
            return self.first_player, self.acting_player




    def fort_ironweed_checks(self):
        if fort_ironweed not in self.acting_player.board:
            return True
        if fort_ironweed in self.acting_player.board and len(self.master_builder_queue) == 1:
            # print(fort_ironweed_last_player_text.format(self.acting_player))
            return True
        else:
            # print(fort_ironweed_turn_skip_text)
            return False



    def end_of_turn(self):
        last_played = self.master_builder_queue.pop(0)  # select current player, and remove them from the front of the player queue
        self.master_builder_queue.append(last_played)  # add the current player to the back of the player queue
        for each_player in self.dictionary_of_players:
            if self.dictionary_of_players[each_player].get_board_is_filled():  # if player has no empty tiles free for resource placement next turn, remove them from queues of players to act
                if each_player in self.master_builder_queue:
                    self.players_finished += 1
                    self.dictionary_of_players[each_player].finish_position = (self.players_finished)
                    self.master_builder_queue.remove(each_player)
        if self.master_builder_queue == []:
            self.finished = True
        return self.master_builder_queue, self.players_finished, self.dictionary_of_players, self.finished



    def assign_master_builder(self):
        self.first_player, self.acting_player = self.start_of_turn()
        if not self.first_player:
            return self.first_player, self.acting_player
        self.acting_player.can_be_master_builder = self.fort_ironweed_checks()
        return self.first_player, self.acting_player



    def bank_resource_check(self):
        for resource_id in self.acting_player.bank_resources:
            self.acting_player.resource_choice_dict.pop(resource_id, None)
        return self.acting_player.resource_choice_dict



    # GAME
    def play(self):
        epsilon = 0.5
        self.finished, self.players_finished = self.start_of_game()

        while not self.finished:  # MAIN TURN LOOP
            self.first_player, self.acting_player = self.assign_master_builder()
            if not self.first_player:
                self.finished = True
                break
            
            if self.acting_player.can_be_master_builder:
                # print(self.acting_player.__repr__())
                self.acting_player.resource_choice_dict = self.bank_resource_check()
                resource_choice_id, tile_index = self.acting_player.get_agent().board_scan(self, self.acting_player)
                # print(resource_choice_id, tile_index)
                # resource_choice_id = handle_input(resource_selection_text.format(self.acting_player.__str__(), self.acting_player.resource_choice_dict),self.acting_player.resource_choice_dict,)  # MASTER BUILDER CHOOSES A RESOURCE

                resource_choice = resource_dict[resource_choice_id]


                for each_player in self.master_builder_queue:    # RESOURCE PLACEMENT ROUND
                    self.acting_player = self.dictionary_of_players[each_player]
                    self.acting_player.turn += 1
                    # print(self.acting_player.__repr__())
                    if self.acting_player.get_id() != self.first_player:
                        if (resource_choice_id in self.acting_player.get_factory_resources()):  # CHECK FACTORY RESOURCES
                            # print(current_player_cards_text.format(self.acting_player.__str__(), [el.__str__() for el in self.acting_player.get_buildable_cards()],))
                            _, tile_index = self.acting_player.get_agent().board_scan(self, self.acting_player)
                            self.acting_player_resource_choice_id = handle_input(resource_selection_text.format(self.acting_player.__str__(), resource_names_dict), list(resource_dict.keys()))

                            resource_choice = resource_dict[self.acting_player_resource_choice_id]
                        else:
                            resource_choice = resource_dict[resource_choice_id]

                        # HANDLE WAREHOUSE STORAGE
                        if len(self.acting_player.get_warehouse_resources()) < self.acting_player.warehouse_capacity:
                            place_in_warehouse = handle_input(place_in_warehouse_text.format(self.acting_player.__str__(), no_yes_dict), list(no_yes_dict.keys()))
                            if place_in_warehouse:
                                if 0 < len(self.acting_player.get_warehouse_resources()):
                                    warehouse_swap = handle_input(warehouse_swap_text.format(self.acting_player.__str__(), store_swap_dict), list(store_swap_dict.keys()))
                                    if warehouse_swap:  # player has chosen to swap
                                        warehouse_choice_dict = dict_enum(self.acting_player.get_warehouse_resources())  # create dictionary of enumerated resources in warehouses
                                        warehouse_retrieve_choice = handle_input(warehouse_retrieve_text.format(self.acting_player.__str__(), warehouse_choice_dict), list(warehouse_choice_dict.keys())) # handle input of selecting resource
                                        # print(warehouse_retrieve_choice)
                                        # print(self.acting_player.get_warehouse_resources())
                                        self.acting_player.warehouse_resources.append(resource_choice_id)
                                        resource_choice = warehouse_choice_dict[warehouse_retrieve_choice]
                                        self.acting_player.warehouse_resources.pop(warehouse_retrieve_choice)
                                else:
                                    self.acting_player.warehouse_resources.append(resource_choice_id)
                                    break
                    # tile_index = handle_input(tile_index_text.format(self.acting_player.__str__()), range(1, 17))   # SELECT WHERE TO PLACE MASTER BUILDERS CHOSEN RESOURCE
                    while self.acting_player.board[board_tile_dict[tile_index]] != empty:
                        # print(not_empty_tile_text)
                        resource_choice_id, tile_index = self.acting_player.get_agent().board_scan(self, self.acting_player)
                        # tile_index = handle_input(tile_index_text.format(self.acting_player.__str__()), range(1, 17))   # If chosen tile is not empty, ask for a new tile index

                    self.acting_player.board[board_tile_dict[tile_index]] = resource_choice  # RESOURCE PLACEMENT ASSIGNMENT


                    if empty not in self.acting_player.board:    # check if board has no tiles free for resource placement
                        self.acting_player.board_is_filled = True    # mark player as having a full board



                for each_player in self.master_builder_queue:    # BUILDING ROUND
                    self.acting_player = self.dictionary_of_players[each_player]
                    coord_dictionary, build_options, placement_display = (find_all_placements(self.acting_player, self.acting_player.get_buildable_cards()))
                    # print(self.acting_player.__repr__())

                    while (len(coord_dictionary) != 0):  # if resources are arranged in such a way that something can be built...
                        coord_dictionary, build_options, placement_display = (find_all_placements(self.acting_player, self.acting_player.get_buildable_cards()))
                        if len(coord_dictionary) == 0:
                            break
                        which_building_choice = dict_enum(placement_display)
                        dict_presented = dict()
                        for key in which_building_choice:
                            if which_building_choice[key]:
                                dict_presented[key] = which_building_choice[key]
                        # print(f"{dict_presented=}")  # ...# print choices of the tile combinations that can be picked up to construct the building in the chosen position
                        want_to_build = handle_input(want_to_build_text.format(self.acting_player.__str__(), no_yes_dict),range(2))
                        if want_to_build:
                            build_choice = handle_input(build_choice_text, list(dict_presented.keys()))
                            chosen_building_dict = build_options[build_choice]
                            # print(chosen_building_dict)
                            building_placement_choice = handle_input(build_coord_text, list(chosen_building_dict.keys()))

                            self.acting_player.construct(chosen_building_dict[building_placement_choice], self.dictionary_of_players)  # CONSTRUCTION METHOD CALL

                        else:
                            break

                        if (
                            empty in self.acting_player.board
                        ):  # check if board has tiles free for resource placement
                            self.acting_player.board_is_filled = False  # if player has built since being flagged as having a full board, remove their full board flag so they are not removed from queues of players to act

                    self.acting_player.score = get_score(self, self.acting_player)
                    # score_display(self.acting_player)
                    # print(self.acting_player.display_score())
                    # print("")
                    # print(get_observation(self, each_player))
                    # print("")

            self.master_builder_queue, self.players_finished, self.dictionary_of_players, self.finished = self.end_of_turn()

        # print(game_completion_text)
        player_scores = {}
        for each_player in self.player_queue:
            player = self.dictionary_of_players[each_player]
            player.score = get_score(self, player)
            player_scores[player] = player.score

        # for player, score in player_scores.items():
            # print("{} scores {}VP!".format(player, score))

        winning_player = max(player_scores, key=player_scores.get)
        joint_winners = [winning_player]
        for player, score in player_scores.items():
            if player != winning_player:
                if player_scores[player] == player_scores[winning_player]:
                    joint_winners.append(player)
        # print("{} win!".format([winner.__str__() for winner in joint_winners]))

    def get_card_choices(self):
        return [el for el in self.card_choices]

    def show_card_choices(self):
        return [el.__str__() for el in self.card_choices]



def main():
    """Main entry point for the game."""
    for episode in tqdm(range(1_000_000)):
        game = TinyTownsEnv()
        game.setup_players()
        game.play()
        game.record_game()
        game.monuments_deck = game.refill_monuments_deck()


if __name__ == "__main__":
    main()
