from player import Player
from agent import Agent
import random as rdm
from cards import *
from choices import *
import copy
from layout_variants import find_all_placements, create_variants
from score import get_score
from joblib import Parallel, delayed
import math
import json
import numpy as np
from placement_check import find_all_layouts, score_action, actions_equal
from tqdm import tqdm
import cProfile
import pstats

class Game:
    def __init__(self, player_count=2, agent=None, iterations=1000):
        self.players = [Player(i + 1, monuments_deck.pop(rdm.randint(0, len(monuments_deck) - 1)), agent) for i in range(player_count)]
        self.finished = False

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

        for player in self.players:
            player.all_cards = self.community_cards + [player.get_monument()]




class MCTSAgent:
    def __init__(self, )

if __name__ == "__main__":
    # Example usage
    game = Game(player_count=2, agent=Agent("Test Agent"), iterations=1000)
    print("Game initialized with players and community cards.")
    for player in game.players:
        print([card.__str__() for card in player.get_all_cards()])
        print(player.get_display_board())