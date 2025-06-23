# SINGLE PLAYER PLAYTEST
import random as rdm
from player import *
from buildingLayouts import *
from cards import *
from resources import *
from layoutVariants import createVariants


class Game:
    def __init__(self):
        self.cottageChoice = rdm.choice(cottageDeck)
        self.farmChoice = rdm.choice(farmDeck)
        self.factoryChoice = rdm.choice(factoryDeck)
        self.tavernChoice = rdm.choice(tavernDeck)
        self.chapelChoice = rdm.choice(chapelDeck)
        self.theatreChoice = rdm.choice(theatreDeck)
        self.wellChoice = rdm.choice(wellDeck)
        numberOfPlayers = 1

        self.cardChoices = [
            self.cottageChoice,
            self.farmChoice,
            self.factoryChoice,
            self.tavernChoice,
            self.chapelChoice,
            self.theatreChoice,
            self.wellChoice,
        ]

    def play(self):
        # SETUP
        finished = False
        playerOne = Player(1, rdm.choice(monumentsDeck))  # architectsGuild
        self.cardChoices.append(playerOne.monument)
        
        
        
        # TURN
        
        # MASTER BUILDER CHOOSES A RESOURCE                 (YET TO IMPLEMENT)
        # ALL PLAYERS PLACE CHOSEN RESOURCE                 (YET TO IMPLEMENT)
        # CHECK FOR CONSTRUCTION POSSIBILITIES
        # CHOOSE IF AND WHERE TO BUILD                      (YET TO IMPLEMENT)
        # PASS MASTER BUILDER TO NEXT PLAYER (NEXT TURN)
        print(playerOne.describeTownBoard())
        while not finished:
            print(Game.showCardChoices(self))
            print(playerOne.describePlayer())
            print("\n")
            coordDictionary, buildOptions = findAllPlacements(playerOne, self.cardChoices)
            print(f"{coordDictionary=}")
            print("")
            print(buildOptions)
            buildingChoiceInput = input("Build (e.g. wood, chapel, or FINISHED): ")
            if buildingChoiceInput == "FINISHED":
                finished = True
                continue
            buildingChoice = buildingInputDict[buildingChoiceInput]
            rowChoice = int(input("ROW (0-3): "))
            colChoice = int(input("COLUMN (0-3): "))
            playerOne.board[rowChoice,colChoice] = buildingChoice
            print(playerOne.describePlayer())
            while buildingChoice != "FINISHED":
                buildingChoiceInput = input("Build (e.g. wood, chapel, or FINISHED): ")
                if buildingChoiceInput == "FINISHED":
                    finished = True
                    break
                buildingChoice = buildingInputDict[buildingChoiceInput]
                rowChoice = int(input("ROW (0-3): "))
                colChoice = int(input("COLUMN (0-3): "))
                playerOne.board[rowChoice,colChoice] = buildingChoice
                coordDictionary, buildOptions = findAllPlacements(playerOne, self.cardChoices)
                print(playerOne.describePlayer())
                print(playerOne.describeTownBoard())
                print(coordDictionary)
                print(buildOptions)
            finished = True
        print("Game completed!")

    def showCardChoices(self):
        return [el.getName() for el in self.cardChoices]

    def checkForBuildable(self):
        for card in self.cardChoices:
            print(card.getName())
            layouts = createVariants(card.getLayout())
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
