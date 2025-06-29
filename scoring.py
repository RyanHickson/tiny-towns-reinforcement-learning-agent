from choices import board_tile_dict
from resources import *
from cards import *

# def getTileInfo()

# total_score = 0

# def getTileScore(tile)
empty_tile_score = -1
# if cathedral_of_caterina in self.board:
# empty_tile_score = 0
empty_tile_count = 0
cottage_count = 0

farm_count = 0
greenhouse_count = 0

warehouse_count = 0
trading_post_count = 0
bank_count = 0

tavern_count = 0
almshouse_count = 0
feast_hall_count = 0
chapel_count = 0

for tile_id in range(1, 17):
    tile_coords = board_tile_dict[tile_id]
    tile = self.board[tile_coords]

    match tile:
        case emptyTile:
            empty_tile_count += 1
        case cottage:
            cottage_count += 1
        case farm:
            farm_count += 1
        # fedCount = farmCount * 4 # each farm feeds 4 buildings
        # feedListDescending[:fedCount] # get the most victory points for the number of farms that can feed buildings

        case orchard:
            row_coords_list = self.check_row(tile_id)[1]
            col_content_list = self.check_col(tile_id)[1]
            row_col_combined = set(row_coords_list + col_content_list)
            for coord_pair in row_col_combined:
                if self.board[coord_pair].is_feedable():
                    self.board[coord_pair].is_fed = True
        case greenhouse:
            greenhouse_count += 1
        case granary:
            tile_row, tile_col = tile_coords
            surrounding_tiles = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]
            for surround_coords in surrounding_tiles:
                if self.board[tile_row + surround_coords[0], tile_col + surround_coords[1]].is_feedable():
                    self.board[tile_row + surround_coords[0], tile_col + surround_coords[1]].is_fed = True
        case factory:
            continue    # factory scores nothing
        case warehouse
            score -1 for each resource stored in warehouse
        case trading_post:
            total_score += 1
        case bank:
            total_score += 4
        case tavern:
            tavern_count += 1
        case almshouse:
            almshouse_count += 1
        case inn:
            if only inn in row and col:
                total_score += 3
        case feast_hall:
            feast_hall_count += 1
            if player_on_right.get_id().feast_hall_count < self.feast_all_count:   # if player on right has lower or equal number of feast halls
                each_feast_hall_score = 3   # each feast hall scores 3VP
            else:   # if it is not the case that player being scored has a higher count of feast halls
                each_feast_hall_score = 2   # they are only worth 2VP each
        case chapel:
            total_score += fed_cottage_count    # barrett castle counts as two cottages for the sake of this count
        case temple:
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            if adjacent_tiles.get_fed_cottage_count() < 2:
                continue
            else:
                total_score += 4
        case Abbey:
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            if TavernType or FactoryType or TheatreType in adjacent_tiles:
                continue
            else:
                total_score += 3
        case cloister:
            cloisters_in_corners = 0
            if self.board[0,0] == cloister:
                cloisters_in_corners += 1
            if self.board[0,3] == cloister:
                cloisters_in_corners += 1
            if self.board[3,0] == cloister:
                cloisters_in_corners += 1
            if self.board[3,3] == cloister:
                cloisters_in_corners += 1
            total_score += cloistersInCorners
        case theatre:
            row_content = self.check_row(tile_id)[0]
            col_content = self.check_col(tile_id)[0]
            row_col_combined = row_content + col_content
            if CottageType in row_col_combined:
                unique_building_count += 1
            if FarmType in row_col_combined:
                unique_building_count += 1
            if FactoryType in row_col_combined:
                unique_building_count += 1
            if TavernType in row_col_combined:
                unique_building_count += 1
            if ChapelType in row_col_combined:
                unique_building_count += 1
            if WellType in row_col_combined:
                unique_building_count += 1
            total_score += unique_building_count
        case tailor:
            total_score += 1
            centre_tile_tailors = 0
            if self.board[1,1] == tailor:
                centre_tile_tailors += 1
            if self.board[1,2] == tailor:
                centre_tile_tailors += 1
            if self.board[2,1] == tailor:
                centre_tile_tailors += 1
            if self.board[2,2] == tailor:
                centre_tile_tailors += 1
            total_score += centre_tile_tailors
        case market:
            row_markets = 0
            col_markets = 0
            row_content = self.check_row(tile_id)[0]
            for market in row_content:
                row_markets += 1
            col_content = self.check_col(tile_id)[0]
            for market in col_content:
                col_markets += 1
            total_score += max(row_markets, col_markets)
        case bakery:
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            if FarmType or FactoryType in adjacent_tiles:
                total_score += 3
        case well:
            adjacent_cottage_count = 0
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            for CottageType in adjacent_tiles:
                adjacent_cottage_count += 1
            if barrett_castle in adjacent_tiles:
                adjacent_cottage_count += 2
            total_score += adjacent_cottage_count
        case fountain:
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            if WellType in adjacent_tiles:
                total_score += 2
        case millstone:
            adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
            if FarmType or TheatreType in adjacent_tiles:
                total_score += 2
        case architects_guild:
            total_score += 1
        case archive_of_the_second_age:
            unique_building_count = 0
            if CottageType in self.board:
                unique_building_count += 1
            if FarmType in self.board:
                unique_building_count += 1
            if FactoryType in self.board:
                unique_building_count += 1
            if TavernType in self.board:
                unique_building_count += 1
            if ChapelType in self.board:
                unique_building_count += 1
            if TheatreType in self.board:
                unique_building_count += 1
            if WellType in self.board:
                unique_building_count += 1
            total_score += unique_building_count
        case barrett_castle:
            if tile.is_fed:
                total_score += 5
        case cathedral_of_caterina:
            total_score += 2
            empty_tile_score = 0
        case fortIronweed:
            total_score += 7
        case grand_mausoleum_of_the_rodina:
            total_score += (3 * unfed_cottage_count)
        case grove_university:
            total_score += 3
        case mandras_palace:
            unique_building_count = 0
            surrounding_tile_content = []
            surrounding_tiles = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]
            for surround_coords in surrounding_tiles:
                surrounding_tile_content.append(self.board[tile_row + surround_coords[0], tile_col + surround_coords[1]])
            if CottageType in surrounding_tile_content:
                unique_building_count += 1
            if FarmType in surrounding_tile_content:
                unique_building_count += 1
            if FactoryType in surrounding_tile_content:
                unique_building_count += 1
            if TavernType in surrounding_tile_content:
                unique_building_count += 1
            if ChapelType in surrounding_tile_content:
                unique_building_count += 1
            if TheatreType in surrounding_tile_content:
                unique_building_count += 1
            if WellType in surrounding_tile_content:
                unique_building_count += 1
            total_score += (2 * unique_building_count)

        case obelisk_of_the_crescent:
            continue

        case opaleyes_watch:
            continue

        case shrine_of_the_elder_tree:
            total_score += shrine_of_the_elder_tree_score   # score is locked in when shrine is constructed

        case silva_forum:
            total_score += 1
            silva_forum_score = len(self.largest_contiguous_group())
            total_score + silva_forum_score
        
        case the_sky_baths:
            missing_building_count = 0
            if CottageType not in self.board:
                missing_building_count += 1
            if FarmType not in self.board:
                missing_building_count += 1
            if FactoryType not in self.board:
                missing_building_count += 1
            if TavernType not in self.board:
                missing_building_count += 1
            if ChapelType not in self.board:
                missing_building_count += 1
            if TheatreType not in self.board:
                missing_building_count += 1
            if WellType not in self.board:
                missing_building_count += 1
            total_score += (2 * missing_building_count)

        case the_starloom:
            total_score += the_starloom_score   # score locked in when town is completed

        case statue_of_the_bondmaker:
            continue
