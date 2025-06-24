# SINGLE PLAYER PLAYTEST
import random as rdm
from player import *
from building_layouts import *
from cards import *
from resources import *
from layout_variants import create_variants
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
            self.player_dict[player] = Player(player, rdm.choice(monuments_deck), self.agent_dict[player])
        print(self.player_dict)
        self.player_queue = [player for player in self.player_dict.keys()]
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

        master_builder = self.player_dict[self.player_queue.pop(0)]   # starting master builder
        print(f"{self.player_queue=}")
        print(f"{master_builder.get_id()=}")
        print(f"{master_builder.agent=}")
        # MASTER BUILDER CHOOSES A RESOURCE                 (YET TO IMPLEMENT)
        # ALL PLAYERS PLACE CHOSEN RESOURCE                 (YET TO IMPLEMENT)
        # CHECK FOR CONSTRUCTION POSSIBILITIES
        # CHOOSE IF AND WHERE TO BUILD                      (YET TO IMPLEMENT)
        # PASS MASTER BUILDER TO NEXT PLAYER (NEXT TURN)
        # print(master_builder.describe_town_board())
        while not finished:
            print(master_builder.check_immediate_adjacent_tiles(12))
            print(Game.show_card_choices(self))
            print(master_builder.describe_player())
            print("\n")
            coord_dictionary, build_options = find_all_placements(master_builder, self.card_choices)
            print(f"{coord_dictionary=}")
            print("")
            print(build_options)
            print(dict(enumerate(master_builder.get_resource_types())))
            building_choice_input = input("Build (e.g. wood, chapel, or FINISHED): ")
            if building_choice_input.upper() == "FINISHED":
                finished = True
                continue
            if building_choice_input not in building_input_dict.keys():
                print("Input not understood.")
                building_choice = ""
            else:
                building_choice = building_input_dict[building_choice_input]
                row_choice = int(input("ROW (0-3): "))
                col_choice = int(input("COLUMN (0-3): "))
                master_builder.board[row_choice,col_choice] = building_choice
                print(master_builder.describe_player())
            while building_choice != "FINISHED":
                building_choice_input = input("Build (e.g. wood, chapel, or FINISHED): ")
                if building_choice_input.upper() == "FINISHED":
                    finished = True
                    break
                if building_choice_input not in building_input_dict.keys():
                    print("Input not understood.")
                    building_choice = ""
                else:
                    building_choice = building_input_dict[building_choice_input]
                    row_choice = int(input("ROW (0-3): "))
                    col_choice = int(input("COLUMN (0-3): "))
                    master_builder.board[row_choice, col_choice] = building_choice
                    coord_dictionary, build_options = find_all_placements(master_builder, self.card_choices)
                    print(master_builder.describe_player())
                    print(master_builder.describe_town_board())
                    print(coord_dictionary)
                    print(build_options)
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
