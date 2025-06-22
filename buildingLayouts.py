import numpy as np
from layoutVariants import *

# W = WOOD
# C = WHEAT (CROP)
# B = BRICK
# G = GLASS
# S = STONE

# COTTAGE TYPES
cottageLayout = [[" ","wheat"],
                 ["brick","glass"]]

# FARM TYPES
farmLayout = [["wheat","wheat"],
              ["wood","wood"]]

orchardLayout = [["stone","wheat"],
                 ["wheat","wood"]]

greenhouseLayout = [["wheat","glass"],
                    ["wood","wood"]]

granaryLayout = [["wheat","wheat"],
                 ["wood","brick"]]

# FACTORY TYPES
factoryLayout = [["wood"," "," "," "],
                 ["brick","stone","stone","brick"]]

warehouseLayout = [["wheat","wood","wheat"],
                   ["brick"," ","brick"]]

tradingPostLayout = [["stone","wood"," "],
                     ["stone","wood","brick"]]

bankLayout = [["wheat","wheat"," "],
              ["wood","glass","brick"]]

# TAVERN TYPES
tavernLayout = [["brick","brick","glass"]]

almshouseLayout = [["stone","stone","glass"]]

innLayout = [["wheat","stone","glass"]]

feastHallLayout = [["wood","wood","glass"]]

# CHAPEL TYPES
chapelLayout = [[" "," ","glass"],
                ["stone","glass","stone"]]

templeLayout = [[" "," ","glass"],
                ["brick","brick","stone"]]

abbeyLayout = [[" "," ","glass"],
               ["brick","stone","stone",]]

cloisterLayout = [[" "," ","glass"],
                  ["wood","brick","stone"]]

# THEATRE TYPES
theatreLayout = [[" ","stone"," "],
                 ["wood","glass","wood"]]

tailorLayout = [[" ","wheat"," "],
                ["stone","glass","stone"]]

marketLayout = [[" ","wood"," "],
                ["stone","glass","stone"]]

bakeryLayout = [[" ","wheat"," "],
                ["brick","glass","brick"]]

# WELL TYPES
wellLayout = [["wood","stone"]]

fountainLayout = [["wood","stone"]]

millstoneLayout = [["wood","stone"]]

shedLayout = [["wood","stone"]]

# MONUMENTS
architectsGuildLayout = [[" "," ","glass"],
                         [" ","wheat","stone"],
                         ["wood","brick"," "]]

archiveOfTheSecondAgeLayout = [["wheat","wheat"],
                               ["brick","glass"]]

barrettCastleLayout = [["wheat"," "," ","stone"],
                       ["wood","glass","glass","brick"]]

cathedralOfCaterinaLayout = [[" ","wheat"],
                             ["stone","glass"]]

fortIronweedLayout = [["wheat"," ","brick"],
                      ["stone","wood","stone"]]

grandMausoleumOfTheRodinaLayout = [["wheat","wheat"],
                                   ["brick","stone"]]

groveUniversityLayout = [[" ","brick"," "],
                         ["stone","glass","stone"]]

mandrasPalaceLayout = [["wheat","glass"],
                       ["brick","wood"]]

obeliskOfTheCrescentLayout = [["wheat"," "," "],
                              ["brick","glass","brick"]]

opaleyesWatchLayout = [["wood"," "," "," "],
                       ["brick","glass","wheat","wheat"],
                       ["stone"," "," "," "]]

shrineOfTheElderTreeLayout = [["brick","wheat","stone"],
                              ["wood","glass","wood"]]

silvaForumLayout = [[" "," ","wheat"," "],
                    ["brick","brick","stone","wood"]]

theSkyBathsLayout = [[" ","wheat"," "],
                     ["stone","glass","wood"],
                     ["brick"," ","brick"]]

theStarloomLayout = [["glass","glass",],
                     ["wood","wheat"]]

statueOfTheBondmakerLayout = [["wood","stone","stone","glass"],
                              ["wheat"," "," "," "]]

def getNotWilds(layout):
    """
    Return tiles of a building layout that contain one of the resources required to complete that building
    """
    co_ords = []
    for rowIndex, row in enumerate(layout):
        for colIndex, cell in enumerate(row):
            if cell != " ":
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
                    if boardValue != layoutValue and boardValue != "wild":
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