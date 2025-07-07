# SINGLE PLAYER PLAYTEST
import random as rdm
from player import *
from building_layouts import *
from cards import *
from resources import *
from layout_variants import *
from agent import *
from game_scoring import get_game_score


class Game:
    def __init__(self):
        self.player_dict = {}
        self.agent_dict = {}

        self.number_of_players = int(input("Number of players (2-6): "))
        card_choice_mode = int(input("Select card choice mode, 1: Auto, 2: Manual "))

        if card_choice_mode == 1:   # Normal play, random card choices from each deck
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
        elif card_choice_mode == 2:     # Allows for manual card choices for a game
            card_choice_list = []
            for deck in all_decks:
                deck_list = []
                for card in deck:
                    deck_list.append(card.__str__())
                card_deck_dict = dict(enumerate(deck_list))
                card_choice_index = ""
                while card_choice_index not in card_deck_dict:
                    card_choice_index = int(input(
                        f"Choose a card from  the list: {card_deck_dict} "
                    ))
                card_choice_list.append(deck[card_choice_index])
            self.card_choices = card_choice_list

    
        for player in range(self.number_of_players):
            self.agent_dict[player] = Agent(player)
        rdm.shuffle(self.agent_dict)
        for player in range(self.number_of_players):
            self.player_dict[player] = Player(player + 1, rdm.choice(monuments_deck), self.agent_dict[player])
            monuments_deck.remove(self.player_dict[player].get_monument())
            self.player_dict[player].all_cards = self.card_choices + [self.player_dict[player].get_monument()]
        self.player_queue = list(self.player_dict.keys())
        self.master_builder_queue = self.player_queue.copy()

    def play(self):
        # SETUP
        finished = False

        # GAME
        while not finished:
            # coord_dictionary, build_options = find_all_placements(master_builder, self.card_choices)
            building_choice = ""
            while building_choice != "FIN":  # MAIN TURN LOOP
                acting_player = self.player_queue[0]   # player one becomes first player to act
                master_builder = self.player_dict[acting_player]   # assign acting player to be first master builder
                print(f"{master_builder.__str__()}, your cards this game are {[el.__str__() for el in master_builder.get_all_cards()]}")
                resource_choice_id = int(input(f"Choose a resource: {resource_names_dict} "))  # MASTER BUILDER CHOOSES A RESOURCE
                if isinstance(resource_dict[resource_choice_id], Resource):
                    for each_player in self.player_dict:    # RESOURCE PLACEMENT ROUND
                        acting_player = self.player_dict[each_player]
                        if resource_choice_id in acting_player.get_factory_resources():
                            print(f"{acting_player.__str__()}, your cards this game are {acting_player.get_all_cards()}")
                            acting_player_resource_choice_id = int(input(f"Choose a resource: {resource_names_dict} "))
                            resource_choice = resource_dict[acting_player_resource_choice_id]
                        else:
                            resource_choice = resource_dict[resource_choice_id]
                        tile_input = int(input("Enter tile ID (1-16): "))   # SELECT WHERE TO PLACE MASTER BUILDERS CHOSEN RESOURCE
                        acting_player.board[board_tile_dict[tile_input]] = resource_choice
                    
                    for each_player in self.player_dict:    # BUILDING ROUND
                        acting_player = self.player_dict[each_player]
                        coord_dictionary, build_options = find_all_placements(acting_player, acting_player.get_all_cards())
                        print(acting_player.__repr__())
                        if len(coord_dictionary) != 0:  # if resources are arranged in such a way that something can be built,
                            factory_count = acting_player.get_building_count(factory)
                            which_building_choice = dict(enumerate(build_options))
                            print(f"{which_building_choice=}")     # print choices of the tile combinations that can be picked up to construct the building in the chosen position
                            build_choice = input("What would you like to build? ")
                            chosen_building_dict = build_options[int(build_choice)]
                            print(chosen_building_dict)
                            building_placement_choice = input("Which co_ordinates should be built on, and which resources used? ")
                            print(f"{building_placement_choice=}")
                            acting_player.construct(chosen_building_dict[int(building_placement_choice)])
                            new_factory_count = acting_player.get_building_count(factory)
                            if factory_count != new_factory_count:  # if a factory has been built
                                self.factory_resources.append(int(input(f"{acting_player.__str__()}, Choose a resource: {resource_names_dict} ")))
                    finished = True
                    print(get_game_score(self))
                last_played = self.player_queue.pop(0)   # select current player, and remove them from the front of the player queue
                self.player_queue.append(last_played)    # add the current player back to the player queue
            finished = True
        print("Game completed!")

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
