import numpy as np
from layoutVariants import *

# COTTAGE TYPES
cottageLayout = [["","c"],
                 ["b","g"]]

# FARM TYPES
farmLayout = [["c","c"],
              ["w","w"]]

orchardLayout = [["s","c"],
                 ["c","w"]]

greenhouseLayout = [["c","g"],
                    ["w","w"]]

granaryLayout = [["c","c"],
                 ["w","b"]]

# FACTORY TYPES
factoryLayout = [["w","","",""],
                 ["b","s","s","b"]]

warehouseLayout = [["c","w","c"],
                   ["b","","b"]]

tradingPostLayout = [["s","w",""],
                     ["s","w","b"]]

bankLayout = [["c","c",""],
              ["w","g","b"]]

# TAVERN TYPES
tavernLayout = [["b","b","g"]]

almshouseLayout = [["s","s","g"]]

innLayout = [["c","s","g"]]

feastHallLayout = [["w","w","g"]]

# CHAPEL TYPES
chapelLayout = [["","","g"],
                ["s","g","s"]]

templeLayout = [["","","g"],
                ["b","b","s"]]

abbeyLayout = [["","","g"],
               ["b","s","s",]]

cloisterLayout = [["","","g"],
                  ["w","b","s"]]

# THEATRE TYPES
theatreLayout = [["","s",""],
                 ["w","g","w"]]

tailorLayout = [["","c",""],
                ["s","g","s"]]

marketLayout = [["","w",""],
                ["s","g","s"]]

bakeryLayout = [["","c",""],
                ["b","g","b"]]

# WELL TYPES
wellLayout = [["w","s"]]

fountainLayout = [["w","s"]]

millstoneLayout = [["w","s"]]

shedLayout = [["w","s"]]

# MONUMENTS
architectsGuildLayout = [["","","g"],
                         ["","c","s"],
                         ["w","b",""]]

archiveOfTheSecondAgeLayout = [["c","c"],
                               ["b","g"]]

barrettCastleLayout = [["c","","","s"],
                       ["w","g","g","b"]]

cathedralOfCaterinaLayout = [["","c"],
                             ["s","g"]]

fortIronweedLayout = [["c","","b"],
                      ["s","w","s"]]

grandMausoleumOfTheRodinaLayout = [["c","c"],
                                   ["b","s"]]

groveUniversityLayout = [["","b",""],
                         ["s","g","s"]]

mandrasPalaceLayout = [["c","g"],
                       ["b","w"]]

obeliskOfTheCrescentLayout = [["c","",""],
                              ["b","g","b"]]

opaleyesWatchLayout = [["w","","",""],
                       ["b","g","c","c"],
                       ["s","","",""]]

shrineOfTheElderTreeLayout = [["b","c","s"],
                              ["w","g","w"]]

silvaForumLayout = [["","","c",""],
                    ["b","b","s","w"]]

theSkyBathsLayout = [["","c",""],
                     ["s","g","w"],
                     ["b","","b"]]

theStarloomLayout = [["g","g",],
                     ["w","c"]]

statueOfTheBondmakerLayout = [["w","s","s","g"],
                              ["c","","",""]]

def getNotWilds(layout):
    co_ords = []
    for rowIndex, row in enumerate(layout):
        for colIndex, cell in enumerate(row):
            if cell != "":
                co_ords.append((rowIndex, colIndex))
    return co_ords

def findPlacements(board, card):
    """
    Finds all building placement possibilities and returns a dictionary of
    co-ordinate pair keys and building placement possibility values
    NEED TO UPDATE TO RETURN REMOVABLE RESOURCE CUBE COMBINATIONS
    """
    variants = createVariants(card.getLayout())
    boardRows, boardCols = len(board), len(board[0])
    placementDict = {}

    for variant in variants:
        variant = np.array(variant)
        variantRows, variantCols = variant.shape
        notWilds = getNotWilds(variant.tolist())

        for i in range(boardRows - variantRows + 1):
            for j in range(boardCols - variantCols + 1):
                match = True
                for r, c in notWilds:
                    boardValue = board[i + r][j + c]
                    layoutValue = variant[r][c]
                    if boardValue != layoutValue:
                        match = False
                        break
                if match:
                    coordSet = []
                    for el in notWilds:
                        coordSet.append((i+el[0], j+el[1]))
                    for coordPair in coordSet:
                        if coordPair in placementDict.keys():
                            placementDict[coordPair].add(card.getName())
                        else:
                            placementDict[coordPair] = {card.getName()}

    return placementDict