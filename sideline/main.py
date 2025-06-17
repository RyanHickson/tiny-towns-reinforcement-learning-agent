from resources import resourceTypes
from player import *
import numpy as np
import random
from cardDecks import *


class Game:
    def __init__(self, finished):
        self.maxRounds = 50
        self.finished = False
    
    players = 0
    currentRound = 0
    resourceChoice = ""
    playerDict = {}

    while players not in [2,3,4,5,6]:   # currently limited to 2 player games
        try:
            players = int(input("How many players? (2-6) "))
        except:
            continue

    for i in list(range(players)):
        playerDict[f"Player {i + 1}"] = Player(playerNumber=i,board=np.full((4,4), "", dtype=str),monument=random.choice(monumentsDeck))
    
    for player in playerDict.values():
        print(player)
        print(player.describePlayer())

    activePlayer = playerDict.keys()[0]


    masterBuilderCandidates = playerDict.keys()
    # Turn
    print(f"{masterBuilderCandidates=}")
    while not finished:
        try:
            print(f"{activePlayer}, choose a resource.")
            while resourceChoice.lower() not in resourceTypes:
                resourceChoice = (input("Wood, wheat, glass, brick or stone? "))    # enforce correct resource choice
            print(f"All players must add a {resourceChoice.lower()} to their town board.")
            # In turn, everybody looks to see if they can build, and chooses whether or not to do so
            print(f"Player {masterBuilderCandidates[0]}, it is the end of your turn.")
            masterBuilderCandidates.pop(0)  # removes the current active player from the start of the queue
            print(f"Player {masterBuilderCandidates[0]}, it is now your turn!")
            resourceChoice = ""
        except:
            currentRound += 1   # Track number of rounds
            print(f"End of round {currentRound}")
            if self.maxRounds < currentRound:    # Track for maximum game length
                finished = True
            masterBuilderCandidates = list(range(players))
            # Remove players who should no longer be candidates
            print("Back around to the start...")    # One more time...
            
    print("Game completed!")    # When game has finished