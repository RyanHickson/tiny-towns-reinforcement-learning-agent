from choices import board_tile_dict
from resources import *
from cards import *

def get_player_score(self):
    """
    The method to be called by the player class/ object/ instance
    to calculate player score based on current town board.
    Only complete after game is completed but may be called
    throughout to give RL agent some idea of how it is performing.
    """
    total_score = 0
    empty_tile_score = -1
    empty_tile_count = 0
    cottage_count = 0
    feedable_list = []  # used by farm building
    orchard_fed_dict = {}

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
        tile_content = self.board[tile_coords]

        match tile_content.__str__():
            case "Farm":
                farm_count += 1
            # fed_count = farm_count * 4 # each farm feeds 4 buildings
            # feed_list_descending[:fed_count] # get the most victory points for the number of farms that can feed buildings

            case "Orchard":
                continue
                # row_coords_list = self.check_row(tile_id)[1]
                # col_content_list = self.check_col(tile_id)[1]
                # row_col_combined = set(row_coords_list + col_content_list)
                # for coord_pair in row_col_combined:
                #     if isinstance(self.board[coord_pair], Card):
                #         if self.board[coord_pair].is_feedable:
                #             self.board[coord_pair].is_fed = True
                #             print(f"Orchard at {tile_coords} feeds tile {coord_pair}")
                #                 # total_score += self.board[coord_pair].score_when_fed()
            case "Greenhouse":
                greenhouse_count += 1
            case "Granary":
                tile_row, tile_col = tile_coords
                surrounding_tiles = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]
                for surround_coords in surrounding_tiles:
                    tile_around_granary = self.board[tile_row + surround_coords[0], tile_col + surround_coords[1]]
                    if isinstance(tile_around_granary, Card):
                        if tile_around_granary.is_feedable:
                            tile_around_granary.is_fed = True
                            # total_score += tile_around_granary.score_when_fed()
            case "Factory":
                continue    # factory scores nothing
            # case "warehouse":
            #     score -1 for each resource stored in warehouse
            case "Trading Post":
                total_score += 1
            case "Bank":
                total_score += 4
            case "Tavern":
                tavern_count += 1
            case "Almshouse":
                almshouse_count += 1
            case "Inn":
                row_content = self.check_row(tile_id)[0]
                row_content_names = [el.__str__() for el in row_content]
                col_content = self.check_col(tile_id)[0]
                col_content_names = [el.__str__() for el in col_content]
                row_content_names.remove("Inn")
                col_content_names.remove("Inn")
                if "Inn" in row_content_names:
                    continue
                if "Inn" in col_content_names:
                    continue
                total_score += 3
            case "Feast Hall":
                feast_hall_count += 1
                if player_on_right.__str__().feast_hall_count < self.feast_hall_count:   # if player on right has lower or equal number of feast halls
                    each_feast_hall_score = 3   # each feast hall scores 3VP
                else:   # if it is not the case "that" player being scored has a higher count of feast halls
                    each_feast_hall_score = 2   # they are only worth 2VP each
            case "Chapel":
                total_score += fed_cottage_count    # barrett castle counts as two cottages for the sake of this count
            case "Temple":
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                if adjacent_tiles.get_fed_cottage_count() < 2:
                    continue
                else:
                    total_score += 4
            case "Abbey":
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                if TavernType or FactoryType or TheatreType in adjacent_tiles:
                    continue
                else:
                    total_score += 3
            case "Cloister":
                cloisters_in_corners = 0
                if self.board[0,0] == cloister:
                    cloisters_in_corners += 1
                if self.board[0,3] == cloister:
                    cloisters_in_corners += 1
                if self.board[3,0] == cloister:
                    cloisters_in_corners += 1
                if self.board[3,3] == cloister:
                    cloisters_in_corners += 1
                total_score += cloisters_in_corners
            case "Theatre":
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
            case "Tailor":
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
            case "Market":
                row_markets = 0
                col_markets = 0
                row_content = self.check_row(tile_id)[0]
                for market in row_content:
                    row_markets += 1
                col_content = self.check_col(tile_id)[0]
                for market in col_content:
                    col_markets += 1
                total_score += max(row_markets, col_markets)
            case "Bakery":
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                if FarmType or FactoryType in adjacent_tiles:
                    total_score += 3
            case "Well":
                adjacent_cottage_count = 0
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                for CottageType in adjacent_tiles:
                    adjacent_cottage_count += 1
                if barrett_castle in adjacent_tiles:
                    adjacent_cottage_count += 2
                total_score += adjacent_cottage_count
            case "Fountain":
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                if WellType in adjacent_tiles:
                    total_score += 2
            case "Millstone":
                adjacent_tiles = self.check_immediate_adjacent_tiles(tile_id)
                if FarmType or TheatreType in adjacent_tiles:
                    total_score += 2
            case "Architects Guild":
                total_score += 1
            case "Archive of the Second Age":
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
            case "Barrett Castle":
                feedable_list.insert(0, 5)  # used by farm building
                if orchard in self.board:
                    row_coords_list = self.check_row(tile_id)[1]
                    col_content_list = self.check_col(tile_id)[1]
                    row_col_combined = set(row_coords_list + col_content_list)
                    for coord_pair in row_col_combined:
                        if isinstance(self.board[coord_pair], FarmType):
                            total_score += 5
                elif tile_content.is_fed:
                    total_score += 5
            case "Cathedral of Caterina":
                total_score += 2
                empty_tile_score = 0
            case "Fort Ironweed":
                total_score += 7
            case "Grand Mausoleum of the Rodina":
                total_score += (3 * unfed_cottage_count)
            case "Grove University":
                total_score += 3
            case "Mandras Palace":
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

            case "Obelisk of the Crescent":
                continue

            case "Opaleyes Watch":
                continue

            case "Shrine of the Elder Tree":
                shrine_score_dict = {1:1, 2:2, 3:3, 4:4, 5:5, 6:8}
                shrine_of_the_elder_tree_score = shrine_score_dict[self.shrine_key]
                total_score += shrine_of_the_elder_tree_score   # score is locked in when shrine is constructed

            case "Silva Forum":
                total_score += 1
                silva_forum_score = len(self.largest_contiguous_group())
                total_score + silva_forum_score
            
            case "The Sky Baths":
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

            case "The Starloom":
                total_score += the_starloom_score   # score locked in when town is completed

            case "Statue of the Bondmaker":
                continue
            case "Cottage":
                cottage_count += 1
                if tile_id in orchard_fed_dict:
                    continue
                if orchard in self.board:
                    row_coords_list = self.check_row(tile_id)[1]
                    col_content_list = self.check_col(tile_id)[1]
                    row_col_combined = set(row_coords_list + col_content_list)
                    for coord_pair in row_col_combined:
                        if isinstance(self.board[coord_pair], FarmType):
                            orchard_fed_dict[tile_id] = "Fed"
                else:
                    feedable_list.append(3) # used by farm building
                if tile_content.is_fed:
                    total_score += 3
            case _:
                empty_tile_count += 1
    match tavern_count:
        case 0:
            pass
        case 1:
            total_score += 2
        case 2:
            total_score += 5
        case 3:
            total_score += 9
        case 4:
            total_score += 14
        case 5:
            total_score += 20
    match almshouse_count:
        case 0:
            pass
        case 1:
            total_score -= 1
        case 2:
            total_score += 5
        case 3:
            total_score -= 3
        case 4:
            total_score += 15
        case 5:
            total_score -= 5
        case 6:
            total_score += 26
    if farm in self.board:
        farms_can_feed = farm_count * 4 # each farm feeds four is_feedable buildings
        total_score += sum(feedable_list[:farms_can_feed])
    if greenhouse in self.board:
        greenhouse_feed_list, fed_coords = self.greenhouse_feeding()
        total_score += sum([sum(el) for el in greenhouse_feed_list[:greenhouse_count]])
    if orchard in self.board:
        total_score += (3 * len(orchard_fed_dict))
    total_score += (empty_tile_count * empty_tile_score)
    return total_score