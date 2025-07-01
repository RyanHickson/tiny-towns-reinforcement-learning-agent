# SINGLE PLAYER PLAYTEST
import random as rdm
from player import *
from building_layouts import *
from cards import *
from resources import *
from layout_variants import *
from agent import *


class Game:
    def __init__(self):
        self.cottage_choice = rdm.choice(cottage_deck)
        self.farm_choice = rdm.choice(farm_deck)
        self.factory_choice = rdm.choice(factory_deck)
        self.tavern_choice = rdm.choice(tavern_deck)
        self.chapel_choice = rdm.choice(chapel_deck)
        self.theatre_choice = rdm.choice(theatre_deck)
        self.well_choice = rdm.choice(well_deck)
        self.player_dict = {}
        self.agent_dict = {}
        number_of_players = int(input("Number of players (2-6): "))
        for player in range(number_of_players):
            self.agent_dict[player] = Agent(player)
        rdm.shuffle(self.agent_dict)
        for player in range(number_of_players):
            self.player_dict[player] = Player(
                player, rdm.choice(monuments_deck), self.agent_dict[player]
            )
        print(self.player_dict)
        self.player_queue = list(self.player_dict.keys())
        print(self.player_queue)

        self.card_choices = [
            self.cottage_choice,
            self.farm_choice,
            self.factory_choice,
            self.tavern_choice,
            self.chapel_choice,
            self.theatre_choice,
            self.well_choice,
        ]

    def play(self):
        # SETUP
        finished = False

        # TURN

        master_builder = self.player_dict[
            self.player_queue.pop(0)
        ]  # starting master builder
        print(f"{self.player_queue=}")
        print(f"{master_builder.get_player_id()=}")
        print(f"{master_builder.agent=}")
        # MASTER BUILDER CHOOSES A RESOURCE                 (YET TO IMPLEMENT)
        # ALL PLAYERS PLACE CHOSEN RESOURCE                 (YET TO IMPLEMENT)
        # CHECK FOR CONSTRUCTION POSSIBILITIES
        # CHOOSE IF AND WHERE TO BUILD                      (YET TO IMPLEMENT)
        # PASS MASTER BUILDER TO NEXT PLAYER (NEXT TURN)
        # print(master_builder.describe_town_board())
        all_cards = [el for el in self.card_choices]
        all_cards.append(master_builder.get_monument())
        while not finished:
            print(f"{master_builder.check_immediate_adjacent_tiles(16)}")
            print(Game.show_card_choices(self))
            print(master_builder.describe_player())
            coord_dictionary, build_options = find_all_placements(
                master_builder, all_cards
            )
            print(dict(enumerate(master_builder.get_resource_types())))
            building_choice = ""
            while building_choice != "FIN":  # MAIN TURN LOOP
                building_choice_input = input("Build (e.g. wood, chapel, or FIN): ")
                if building_choice_input.upper() == "FIN":
                    finished = True
                    break
                try:
                    if int(building_choice_input) in range(17):
                        print("TEST")
                        tile_choice = master_builder.board[board_tile_dict[int(building_choice_input)]]
                        print(tile_choice.get_card_detail())
                except:
                    pass
                if building_choice_input not in building_input_dict.keys():
                    print("Input not understood.")
                    building_choice = ""
                else:
                    building_choice = building_input_dict[building_choice_input]
                    tile_input = int(input("Enter tile ID (1-16): "))
                    master_builder.board[board_tile_dict[tile_input]] = building_choice
                    coord_dictionary, build_options = find_all_placements(
                        master_builder, all_cards
                    )
                    print(master_builder.describe_player())
                    print(master_builder.describe_town_board())
                    print(coord_dictionary)
                    print(build_options)
                    print(master_builder.check_contiguous_groups())
                    print(master_builder.largest_contiguous_group())
                    print("")
                    print(f"{master_builder.get_score()}")
            finished = True
        print("Game completed!")

    def show_card_choices(self):
        return [el.get_name() for el in self.card_choices]

    def check_for_buildable(self):
        for card in self.card_choices:
            print(card.get_name())
            layouts = create_variants(card.get_layout())
            for i, layout in enumerate(layouts):
                print(f"Variant {i+1}:")
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
