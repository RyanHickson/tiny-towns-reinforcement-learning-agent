# def getTileInfo()

# totalScore = 0

# def getTileScore(tile)
# emptyScore = -1
# if cathedralOfCaterina in board:
#     emptyScore = 0


# for row in board:
# for tile in row:
# totalScore += getTileScore(tile)
# return totalScore

# farmCount = 0
# if tile == farm:
# farmCount += 1
# fedCount = farmCount * 4 # each farm feeds 4 buildings
# feedListDescending[:fedCount] # get the most victory points for the number of farms that can feed buildings

# if tile == orchard:
# feed all in orchardRow
# feed all in orchardColumn

# if tile == greenhouse:
# go through all tiles (for col in row, for tile in col or whatever)
# store row, col, score:
# add all adjacent tiles to queue
# check queue for isFeedable
# if isFeedable, add to store, add adjacent tiles to queue, continue until entire board has been checked

# if tile is granary:
# try feed (-1, -1)
#          (-1, 0)
#          (-1, +1)
#          (0, -1)
#          (0, +1)
#          (+1, -1)
#          (+1, 0)
#          (+1, +1)

# factory scores 0

# if tile == warehouse
# score -1 for each resource stored in warehouse

# if tile == trading_post:
# totalScore += 1

# if tile == bank:
# totalScore += 4

# if tile == tavern:
# tavernCount += 1

# if tile == almshouse:
# almshouseCount += 1

# if tile == inn:
# if only inn in row and col:
# totalScore += 3

# if tile == feastHall:
# feastHallCount += 1
# if playerOnRight.feastHallCount <= self.feastHallCount
# totalScore += 2
# else totalScore += 3

# if tile == chapel:
# totalScore += (FED COTTAGE COUNT)

# if tile == temple:
# check adjacent tiles
# if adjacent FED COTTAGE COUNT >= 2:
# totalScore += 4

# if tile == Abbey:
# check adjacent tiles
# if no TAVERN, FACTORY or THEATRE
# totalScore += 3

# if tile == cloister:
# cloistersInCorners = 0
# check (0,0), (0,3), (3,0) and (3, 3) for cloisters
# totalScore += cloistersInCorners

# if tile == theatre:
# check row and col for each OTHER unique building type
# totalScore += uniqueBuildingCount

# if tile == tailor:
# totalScore += 1
# centreTileTailors = 0
# check (1,1), (1,2), (2,1) and (2,2) for tailors
# totalScore += centreTileTailors

# if tile == market
# check row and col for greatest number of markets in a line
# totalScore += greatestLineOfMarkets

# if tile == bakery:
# check for adjacent FARM or FACTORY
# if adjacent to FARM or FACTORY
# totalScore += 3

# if tile == well
# check for adjacent COTTAGE (fed or unfed)
# totalScore += adjacentCOTTAGECount

# if tile == fountain:
# check adjacent for fountain (WELL)
# if adjacent to WELL:
# totalScore += 2

# if tile == millstone:
# check adjacent for FARM or THEATRE
# if adjacent to FARM or THEATRE:
# totalScore += 2


# if tile == architectsGuild:
# tS + 1

# if archiveOfTheSecondAge:
# check board for OTHER unique building types
# tS + OTHERUniqueBuildingCount

# if barrettCastle
# if FED:
# tS + 5

# if cathedralOfCaterina:
# tS + 2
# emptyTileScore = 0 (not -1)

# if fortIronweed:
# tS + 7

# if grandMausoleumOfTheRodina:
# count UNFED COTTAGE
# tS + 3 * UNFEDCOTTAGECount

# if groveUniversity:
# tS += 3

# if mandrasPalace:
# check adjacent for unique building types
# tS + 2 * adjacentUniqueBuildingTypes

# if obeliskOfTheCrescent
# no score

# if opaleyesWatch
# no score

# if shrineOfTheElderTree
# tS + shrineOfTheElderTreeScore (locked in when built)

# if silvaForum
# tS + 1
# find largest contiguous group of buildings of the same type on town board
# tS + size of largest contiguous group of buildings of the same type on the town board

# if theSkyBaths
# tS + 2 for each missing building type

# if theStarloom
# tS + theStarLoomScore (locked in when town completed)

# if statueOfTheBondmaker
# no score
