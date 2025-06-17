# SINGLE PLAYER PLAYTEST
import random
from player import *
from buildingLayouts import *
from cards import *
from resources import *


class Game:
    def __init__(self):
        # self.cottageChoice = random.choice(cottageDeck)
        # self.farmChoice = random.choice(farmDeck)
        # self.factoryChoice = random.choice(factoryDeck)
        # self.tavernChoice = random.choice(tavernDeck)
        # self.chapelChoice = random.choice(chapelDeck)
        # self.theatreChoice = random.choice(theatreDeck)
        # self.wellChoice = random.choice(wellDeck)
        
        self.cottageChoice = cottage
        self.farmChoice = farm
        self.factoryChoice = tradingPost
        self.tavernChoice = inn
        self.chapelChoice = chapel
        self.theatreChoice = bakery
        self.wellChoice = shed
        
        self.cardChoices = [self.cottageChoice,
                            self.farmChoice,
                            self.factoryChoice,
                            self.tavernChoice,
                            self.chapelChoice,
                            self.theatreChoice,
                            self.wellChoice]

    def play(self):
        finished = False
        playerOne = Player(1, "architectsGuild") # random.choice(monumentsDeck)
        while not finished:
            self.checkForBuildable()
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
            self.checkForBuildable()
            finished = True
        print("Game completed!")

    def showCardChoices(self):
        return [el.getName() for el in self.cardChoices]
    
    def checkForBuildable(self):
        for building in self.cardChoices:
            currentLayout = building.getLayout()
            print(building.getName())
            print(f"{currentLayout=}")

def main():
    """Main entry point for the game."""
    game = Game()
    game.play()


if __name__ == "__main__":
    main()