# SINGLE PLAYER PLAYTEST
import random as rdm
from player import *
from building_layouts import *
from cards import *
from resources import *
from layout_variants import *
from agent import *
from game_scoring import get_game_score
from ry import *
from ui import *
from score import get_score


class Game:
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

        self.number_of_players = handle_input(number_of_players_text, range(2,7), parse=int)

        manual_card_selection = handle_input(manual_card_selection_text, range(3), parse=int)


        if not manual_card_selection:   # Normal play, random card choices from each deck
            self.cottage_choice = rdm.choice(cottage_deck)
            self.farm_choice = rdm.choice(farm_deck)
            self.factory_choice = rdm.choice(factory_deck)
            self.tavern_choice = rdm.choice(tavern_deck)
            self.chapel_choice = rdm.choice(chapel_deck)
            self.theatre_choice = rdm.choice(theatre_deck)
            self.well_choice = rdm.choice(well_deck)

            self.card_choices = [   # Creates a list of the chosen cards for this game
            self.cottage_choice,
            self.farm_choice,
            self.factory_choice,
            self.tavern_choice,
            self.chapel_choice,
            self.theatre_choice,
            self.well_choice,
        ]
        elif manual_card_selection == 1:     # Allows for manual card choices for a game
            self.card_choices = []   # initialise card choice list
            for deck in all_decks:
                deck_list = []
                for card in deck:
                    deck_list.append(card.__str__())
                card_deck_dict = dict_enum(deck_list)
                card_choice_index = handle_input(choose_card_text.format(card_deck_dict), card_deck_dict, parse=int)    # take player input for each deck, choosing the cards for the community pool
                self.card_choices.append(deck[card_choice_index])
        elif manual_card_selection == 2:
            self.card_choices = [   # Creates a list of the chosen cards for this game
            self.cottage_choice,
            self.farm_choice,
            self.factory_choice,
            self.tavern_choice,
            self.chapel_choice,
            self.theatre_choice,
            self.well_choice,
        ]


        for player in range(self.number_of_players):
            self.dictionary_of_agents[player] = Agent(player)
        rdm.shuffle(self.dictionary_of_agents)
        if not manual_card_selection:
            for player in range(self.number_of_players):
                self.dictionary_of_players[player] = Player(player + 1, rdm.choice(monuments_deck), self.dictionary_of_agents[player])  # random assignment of a unique monument to each player
                monuments_deck.remove(self.dictionary_of_players[player].get_monument())
                self.dictionary_of_players[player].all_cards = self.card_choices + [self.dictionary_of_players[player].get_monument()]
        elif manual_card_selection:
            for player in range(self.number_of_players):
                monument_names_deck = [monument.__str__() for monument in monuments_deck]
                monument_index = handle_input(monument_selection_text.format((player + 1), dict_enum(monument_names_deck)), range_len(monument_names_deck), parse=int)  # take player input to select a unique monument for each player

                self.dictionary_of_players[player] = Player(player + 1, monuments_deck[monument_index], self.dictionary_of_agents[player])
                monuments_deck.remove(self.dictionary_of_players[player].get_monument())
                self.dictionary_of_players[player].all_cards = self.card_choices + [self.dictionary_of_players[player].get_monument()]
        self.player_queue = list(self.dictionary_of_players.keys())
        self.master_builder_queue = self.player_queue.copy()

    def play(self):
        # SETUP
        finished = False

        # GAME
        while not finished: # MAIN TURN LOOP
            # coord_dictionary, build_options = find_all_placements(master_builder, self.card_choices)

            first_player = self.master_builder_queue[0]   # player one becomes first player to act
            self.player_queue = self.master_builder_queue
            acting_player = self.dictionary_of_players[first_player]   # assign acting player to be first master builder
            print(current_player_cards_text.format(acting_player.__str__(), [el.__str__() for el in acting_player.get_all_cards()]))

            for resource_id in acting_player.bank_resources:
                print(f"Bank resource found: {resource_id}")
                try:
                    print(acting_player.resource_choice_dict)
                    acting_player.resource_choice_dict.pop(resource_id)
                    print(acting_player.resource_choice_dict)
                except:
                    continue
            resource_choice_id = handle_input(resource_selection_text.format(acting_player.__str__(), acting_player.resource_choice_dict), acting_player.resource_choice_dict, parse=int)  # MASTER BUILDER CHOOSES A RESOURCE
            resource_choice = resource_dict[resource_choice_id]



            for each_player in self.player_queue:    # RESOURCE PLACEMENT ROUND
                acting_player = self.dictionary_of_players[each_player]
                print(acting_player.__repr__())
                if acting_player != first_player:
                    if resource_choice_id in acting_player.get_factory_resources(): # CHECK FACTORY RESOURCES
                        print(current_player_cards_text.format(acting_player.__str__(), [el.__str__() for el in acting_player.get_all_cards()]))
                        acting_player_resource_choice_id = handle_input(resource_selection_text.format(acting_player.__str__(), resource_names_dict), resource_dict, parse=int)

                        resource_choice = resource_dict[acting_player_resource_choice_id]
                    else:
                        resource_choice = resource_dict[resource_choice_id]


                    tile_index = handle_input(tile_index_text.format(acting_player.__str__()), range(1, 17), parse=int)   # SELECT WHERE TO PLACE MASTER BUILDERS CHOSEN RESOURCE
                while acting_player.board[board_tile_dict[tile_index]] != empty:
                    print(not_empty_tile_text)
                    tile_index = handle_input(tile_index_text.format(acting_player.__str__()), range(1, 17), parse=int)   # If chosen tile is not empty, ask for a new tile index
                acting_player.board[board_tile_dict[tile_index]] = resource_choice  # RESOURCE PLACEMENT ASSIGNMENT
                if empty not in acting_player.board:    # check if board has no tiles free for resource placement
                    acting_player.board_is_filled = True    # mark player as having a full board



            for each_player in self.player_queue:    # BUILDING ROUND
                acting_player = self.dictionary_of_players[each_player]
                coord_dictionary, build_options, placement_display = find_all_placements(acting_player, acting_player.get_all_cards())
                print(acting_player.__repr__())


                while len(coord_dictionary) != 0:  # if resources are arranged in such a way that something can be built...
                    coord_dictionary, build_options, placement_display = find_all_placements(acting_player, acting_player.get_all_cards())
                    if len(coord_dictionary) == 0:
                        break
                    which_building_choice = dict_enum(placement_display)
                    dict_presented = dict()
                    for key in which_building_choice:
                        if which_building_choice[key] != []:
                            dict_presented[key] = which_building_choice[key]
                    print(f"{dict_presented=}")     # ...print choices of the tile combinations that can be picked up to construct the building in the chosen position
                    want_to_build = handle_input(want_to_build_text.format(acting_player.__str__(), {0: "No", 1: "Yes"}), range(2), parse=int)
                    if want_to_build:
                        build_choice = handle_input(build_choice_text, dict_presented, parse=int)
                        chosen_building_dict = build_options[build_choice]
                        print(chosen_building_dict)

                        building_placement_choice = handle_input(build_coord_text, chosen_building_dict, parse=int)
                        print(f"{building_placement_choice=}")

                        acting_player.construct(chosen_building_dict[building_placement_choice])
                    else:
                        break

                    if empty in acting_player.board:    # check if board has no tiles free for resource placement
                        acting_player.board_is_filled = False   # if player has built since being flagged as having a full board, remove their full board flag so they are not removed from queues of players to act


                print(acting_player.display_score())
                print("")
                print(f"{get_score(self, acting_player)=}")

            last_played = self.master_builder_queue.pop(0)   # select current player, and remove them from the front of the player queue
            self.master_builder_queue.append(last_played)    # add the current player to the back of the player queue
            for each_player in self.dictionary_of_players:
                if self.dictionary_of_players[each_player].get_board_is_filled():   # if player has no empty tiles free for resource placement next turn, remove them from queues of players to act
                    if each_player in self.master_builder_queue:
                        self.master_builder_queue.remove(each_player)
                if self.master_builder_queue == []:
                    finished = True
        print(game_completion_text)
        print(get_game_score(self))

    def get_card_choices(self):
        return [el for el in self.card_choices]

    def show_card_choices(self):
        return [el.__str__() for el in self.card_choices]

    def check_for_buildable(self):
        for card in self.card_choices:
            print(card.__str__())
            layouts = create_variants(card.get_layout())
            for layout_index, layout in enumerate(layouts):
                print(f"Variant {layout_index + 1}:")
                if isinstance(layout, np.ndarray):
                    print(layout.tolist())
                else:
                    print(layout)
                print("")


def main():
    """Main entry point for the game."""
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
