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

        # self.cottageChoice = cottage
        # self.farmChoice = farm
        # self.factoryChoice = tradingPost
        # self.tavernChoice = inn
        # self.chapelChoice = chapel
        # self.theatreChoice = bakery
        # self.wellChoice = shed

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
        finished = False
        playerOne = Player(1, rdm.choice(monumentsDeck))  # architectsGuild
        self.cardChoices.append(playerOne.monument)
        print(playerOne.describeTownBoard())
        while not finished:
            # rows, cols = playerOne.board.shape
            # for i in range(rows):
            #     for j in range(cols):
            #         chosenResource = ""
            #         while chosenResource.lower() not in resourceTypes:
            #             chosenResource = input("Choose resource: ")
            #             match chosenResource.lower():
            #                 case "wood":
            #                     playerOne.board[i,j] = "w"
            #                 case "wheat":
            #                     playerOne.board[i,j] = "c"
            #                 case "glass":
            #                     playerOne.board[i,j] = "g"
            #                 case "brick":
            #                     playerOne.board[i,j] = "b"
            #                 case "stone":
            #                     playerOne.board[i,j] = "s"
            print(Game.showCardChoices(self))
            print(playerOne.describePlayer())
            # self.checkForBuildable()
            # chapelCoords = getNotWilds(chapelLayout)
            # print(chapelCoords)
            print(findPlacements(playerOne.board, playerOne.monument))
            print("\n")
            coordDictionary = dict()
            for card in self.cardChoices:
                buildDict = findPlacements(playerOne.board, card)
                for coord, building in buildDict.items():
                    if coord in coordDictionary.keys():
                        coordDictionary[coord].update(building)
                    else:
                        coordDictionary[coord] = set(building)
            print(coordDictionary)
            print("")
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
