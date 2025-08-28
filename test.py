import json
import random as rdm
from itertools import combinations

# filename = "test.json"



# names_list = ["Scott", "Ryan", "Sam", "Zoe"]
# rooms_list = ["kitchen", "bathroom", "bedroom", "hallway", "living room", "dining room"]


# lucky_dict = {}

# for _ in range(50):
#     name_choice = rdm.choice(names_list)
#     room_choice = rdm.choice(rooms_list)
#     lucky_dict[name_choice] = room_choice
#     with open(filename, "a") as f:
#         f.write(json.dumps(lucky_dict, indent=2) + "\n")


from player import *
from cards import *
from resources import *


class Game:
    def __init__(self, exploration_const=1.414, max_search_depth=16):
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
player = Player(1, rdm.choice(monuments_deck), "agentio")

game = Game()
player.all_cards = game.community_cards + [player.get_monument()]
game.player = player
print(game.player.display_all_cards())
print(game.player.get_display_board())
best_score = -17

all_tiles = []
for tile_index in range(1, 17):
    tile_coords = board_tile_dict[tile_index]
    all_tiles.append(tile_coords)

for _ in range(1000):
    player.board = np.full((4, 4), empty)
    game_tiles = all_tiles.copy()
    rdm.shuffle(game_tiles)
    player.board[game_tiles.pop()] = player.get_monument()
    for tile_coords in game_tiles:
        card = rdm.choice(game.player.get_buildable_cards())
        player.board[tile_coords] = card
    score = get_score(game, player)
    print(player.get_display_board())
    print(score)
    if best_score < score:
        best_score = score
        print(best_score)