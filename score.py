from resources import *
from cards import *
from itertools import combinations
from ui import score_display

def check_surrounding_tiles(tile_coords):
    """
    A method to check the 8 surrounding neighbours of a
    given tile, and return a list of their coordinates.
    Tiles on town board boundary will have fewer neighbours.
    """
    surrounding_relations = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]
    surrounding_tiles_list = []    # initialise return
    for relational_vector in surrounding_relations:
        i, j = tile_coords
        r, c = relational_vector
        surrounding_tiles_list.append((i + r, j + c))
    return surrounding_tiles_list

def get_score(game, player):

    cards_this_game = game.get_card_choices()

    player_board_dict = player.get_instance_board()
    player.monument_score = 0
    player.total_score = 0
    player.empty_tile_score = -1

    player.fed_cottage_count = 0

    player.chapel_count = 0

    def get_factory_score(player):
        player.factory_score = 0
        if factory in cards_this_game:
            pass    # factory does not affect score
        if warehouse in cards_this_game:
             for tile_coords, tile_content in player_board_dict.items():
                if tile_content == warehouse:
                    player.factory_score -= (1 * len(player.warehouse_resources))
        if trading_post in cards_this_game:
            for tile_coords, tile_content in player_board_dict.items():
                if tile_content == trading_post:
                    player.factory_score += 1
        if bank in cards_this_game:
            for tile_coords, tile_content in player_board_dict.items():
                if tile_content == bank:
                    player.factory_score += 4
        return player.factory_score
    
    def get_feedable_count(player):
        """
        Used in games with Farm card.
        """
        player.feedable_count = 0
        player.feedable_dict = {}
        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == cottage:
                player.feedable_count += 1
                player.feedable_dict[tile_coords] = "cottage"
            # if tile_content == chapel:
            #     player.chapel_count +=    # function called correctly elsewhere, REMOVE
            if tile_content == barrett_castle:
                player.feedable_count += 1
                player.feedable_dict[tile_coords] = "barrett_castle"
        return player.feedable_count, player.feedable_dict
    
    def get_cottage_stats(player):
        player.cottage_score = 0
        player.barrett_castle_present = False

        player.cottage_count = 0
        player.fed_cottage_count = 0
        player.greenhouse_count = 0

        player.feedable_coords = []

        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == cottage:
                player.cottage_count += 1
                player.feedable_coords.append(tile_coords)
            if tile_content == greenhouse:
                player.greenhouse_count += 1
            if tile_content == barrett_castle:
                player.barrett_castle_present = True
                player.feedable_coords.append(tile_coords)
        player.unfed_cottage_count = player.cottage_count


        if orchard in cards_this_game:
            player.fed_coords = []
            for feedable_coord_pair in player.feedable_coords:
                row_coords_list = player.check_row(feedable_coord_pair)[1]
                col_content_list = player.check_col(feedable_coord_pair)[1]
                row_col_combined = set(row_coords_list + col_content_list)
                for coord_pair in row_col_combined:
                    if feedable_coord_pair not in player.fed_coords:
                        if isinstance(player.board[coord_pair], FarmType):
                            if player.board[feedable_coord_pair] == cottage:
                                player.cottage_score += player.board[feedable_coord_pair].score_when_fed()
                                player.fed_coords.append(feedable_coord_pair)
                                player.fed_cottage_count += 1
                                player.unfed_cottage_count -= 1
                            if barrett_castle == player.get_monument():
                                if player.board[feedable_coord_pair] == barrett_castle:
                                    print("BARRETT FOCKIN CASLTE")
                                    player.monument_score = player.board[feedable_coord_pair].score_when_fed()
                                    player.fed_coords.append(feedable_coord_pair)
                                    player.fed_cottage_count += 2
                                    player.unfed_cottage_count -= 2

        if greenhouse in cards_this_game:
            greenhouse_feed_list, player.fed_coords = player.greenhouse_feeding()
            player.cottage_score += sum([sum(el) for el in greenhouse_feed_list[:player.greenhouse_count]])
            player.fed_cottage_count += sum([len(el) for el in greenhouse_feed_list[:player.greenhouse_count]])
            player.unfed_cottage_count -= sum([len(el) for el in greenhouse_feed_list[:player.greenhouse_count]])
            if player.cottage_score % 3 != 0:
                player.cottage_score -= 5
                player.monument_score = 5

        if granary in cards_this_game:
            player.fed_coords = []
            for coord_pair in player.feedable_coords:
                cottage_surrounding_coords = check_surrounding_tiles(coord_pair)
                for coords in cottage_surrounding_coords:
                    try:
                        tile_content = player_board_dict[coords]
                    except:
                        continue
                    if tile_content == granary:
                        if isinstance(player.board[coord_pair], CottageType):
                            player.cottage_score += player.board[coord_pair].score_when_fed()
                            player.fed_cottage_count += 1
                            player.unfed_cottage_count -= 1
                            player.fed_coords.append(coord_pair)
                            break   # ensures each cottage only fed once
                        elif isinstance(player.board[coord_pair], Monument):
                            if barrett_castle == player.get_monument():
                                player.monument_score += player.board[coord_pair].score_when_fed()
                                player.fed_cottage_count += 2
                                player.unfed_cottage_count -= 2
                                player.fed_coords.append(coord_pair)
                                break   # ensures barrett castle only fed once
            print(f"{player.fed_cottage_count=}")

        return player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords
    
    def get_chapel_score(player):
        player.chapel_score = 0
        player.chapel_count = 0
        player.chapel_coords = []
        for tile_coords, tile_content in player_board_dict.items():
            if isinstance(tile_content, ChapelType):
                player.chapel_count += 1
                player.chapel_coords.append(tile_coords)

        if chapel in cards_this_game:
            player.chapel_score = (player.fed_cottage_count * player.chapel_count)
        
        if temple in cards_this_game:
            for coord_pair in player.chapel_coords: # for each temple on the board
                temple_adjacent_fed_count = 0
                tiles_next_to_temple = player.check_adjacent_tiles(coord_pair)
                for tile_coords in tiles_next_to_temple:
                    if farm in cards_this_game:
                        player.fed_coords = combination
                    if tile_coords in player.fed_coords:
                        if player.board[tile_coords] == cottage:
                            temple_adjacent_fed_count += 1
                        if player.board[tile_coords] == barrett_castle:
                            temple_adjacent_fed_count += 2
                if 2 <= temple_adjacent_fed_count:
                    player.chapel_score += 4
        
        if abbey in cards_this_game:
            for coord_pair in player.chapel_coords: # for each abbey on board
                all_adjacent_contents = []
                abbey_adjacent_tile_contents = player.check_adjacent_tiles(coord_pair)
                for adjacent_coords in abbey_adjacent_tile_contents:
                    try:
                        adjacent_tile_content = player.board[adjacent_coords]
                        print(adjacent_tile_content)
                        all_adjacent_contents.append(adjacent_tile_content)
                    except:
                        continue
                for adjacent_tile_content in all_adjacent_contents:
                    if isinstance(adjacent_tile_content, FactoryType) or isinstance(adjacent_tile_content, TavernType) or isinstance(adjacent_tile_content, TheatreType):
                        still_might_score = False
                        break
                    else:
                        still_might_score = True
                if still_might_score:
                    player.chapel_score += 3
        
        if cloister in cards_this_game:
            cloisters_in_corners = 0
            if player.board[0,0] == cloister:
                cloisters_in_corners += 1
            if player.board[0,3] == cloister:
                cloisters_in_corners += 1
            if player.board[3,0] == cloister:
                cloisters_in_corners += 1
            if player.board[3,3] == cloister:
                cloisters_in_corners += 1
            player.chapel_score += player.chapel_count * cloisters_in_corners
        return player.chapel_score
    
    def get_tavern_score(player):
        player.tavern_score = 0
        player.tavern_count = 0
        player.tavern_coords = []
        for tile_coords, tile_content in player_board_dict.items():
            if isinstance(tile_content, TavernType):
                player.tavern_count += 1
                player.tavern_coords.append(tile_coords)
        if tavern in cards_this_game:
            match player.tavern_count:
                case 0:
                    pass
                case 1:
                    player.tavern_score += 2
                case 2:
                    player.tavern_score += 5
                case 3:
                    player.tavern_score += 9
                case 4:
                    player.tavern_score += 14
                case _: # 5+ case
                    player.tavern_score += 20
        if inn in cards_this_game:
            for inn_placement in player.tavern_coords:
                row_coords_list = player.check_row(inn_placement)[1]
                col_content_list = player.check_col(inn_placement)[1]
                row_col_combined = set(row_coords_list + col_content_list)
                for coord_pair in row_col_combined:
                    if isinstance(player.board[coord_pair], TavernType):
                        break
                    else:
                        player.tavern_score += 3
        if almshouse in cards_this_game:
            match player.tavern_count:
                case 0:
                    pass
                case 1:
                    player.tavern_score -= 1
                case 2:
                    player.tavern_score += 5
                case 3:
                    player.tavern_score -= 3
                case 4:
                    player.tavern_score += 15
                case 5:
                    player.tavern_score -= 5
                case _: # 6+ case
                    player.tavern_score += 26
        if feast_hall in cards_this_game:
            feast_hall_counts = []
            for each_player in game.dictionary_of_players.values():
                feast_hall_counts.append(each_player.get_feast_hall_count())
            player_to_right_id = (player.get_id() + 1) % len(feast_hall_counts)
            if player_to_right_id == 0:
                player_to_right_id = len(feast_hall_counts)
            player_id = player.get_id()
            print(f"{player_id=}")
            print(f"{player_to_right_id=}")
            if feast_hall_counts[player_id - 1] > feast_hall_counts[player_to_right_id - 1]:
                player.tavern_score = player.tavern_count * 3
            else:
                player.tavern_score = player.tavern_count * 2
        return player.tavern_score
    
    def get_theatre_score(player):
        player.theatre_score = 0
        player.theatre_count = 0
        player.theatre_coords = []
        for tile_coords, tile_content in player_board_dict.items():
            if isinstance(tile_content, TheatreType):
                player.theatre_count += 1
                player.theatre_coords.append(tile_coords)

        if theatre in cards_this_game:
            for theatre_coord_pair in player.theatre_coords:
                unique_building_count = 0
                row_content_list = player.check_row(theatre_coord_pair)[0]
                col_content_list = player.check_col(theatre_coord_pair)[0]
                row_col_combined = [el.__class__ for el in row_content_list + col_content_list]
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
                if Monument in row_col_combined:
                    unique_building_count += 1
                player.theatre_score += unique_building_count
        if bakery in cards_this_game:
            for bakery_coords in player.theatre_coords:
                tiles_next_to_bakery = player.check_adjacent_tiles(bakery_coords)
                for coord_pair in tiles_next_to_bakery:
                    if isinstance(player.board[coord_pair], FarmType):
                        player.theatre_score += 3
                        break
                    if isinstance(player.board[coord_pair], FactoryType):
                        player.theatre_score += 3
                        break
        if market in cards_this_game:
            for market_coords in player.theatre_coords:
                markets_in_row = 0
                markets_in_col = 0
                row_content_list = player.check_row(market_coords)[0]
                for tile_content in row_content_list:
                    if tile_content.__class__ is TheatreType:
                        markets_in_row += 1
                col_content_list = player.check_col(market_coords)[0]
                for tile_content in col_content_list:
                    if tile_content.__class__ is TheatreType:
                        markets_in_col += 1
                player.theatre_score += max(markets_in_row, markets_in_col)
        if tailor in cards_this_game:
            tailors_in_centre = 0
            if player.board[1,1] == tailor:
                tailors_in_centre += 1
            if player.board[1,2] == tailor:
                tailors_in_centre += 1
            if player.board[2,1] == tailor:
                tailors_in_centre += 1
            if player.board[2,2] == tailor:
                tailors_in_centre += 1
            player.theatre_score += player.theatre_count + (player.theatre_count * tailors_in_centre)
        return player.theatre_score
    
    def get_well_score(player):
        player.well_score = 0
        player.well_count = 0
        player.well_coords = []
        for tile_coords, tile_content in player_board_dict.items():
            if isinstance(tile_content, WellType):
                player.well_count += 1
                player.well_coords.append(tile_coords)
        if well in cards_this_game:
            for well_coords in player.well_coords:
                tiles_next_to_well = player.check_adjacent_tiles(well_coords)
                for coord_pair in tiles_next_to_well:
                    try:
                        if isinstance(player.board[coord_pair], CottageType):
                            player.well_score += 1
                        if barrett_castle == player.get_monument():
                                if isinstance(player.board[coord_pair], Monument):
                                    player.well_score += 2
                                    player.fed_coords.append(coord_pair)
                    except:
                        continue
        if fountain in cards_this_game:
            for well_coords in player.well_coords:
                tiles_next_to_well = player.check_adjacent_tiles(well_coords)
                for coord_pair in tiles_next_to_well:
                    if isinstance(player.board[coord_pair], WellType):
                        player.well_score += 2
        if millstone in cards_this_game:
            for well_coords in player.well_coords:
                tiles_next_to_well = player.check_adjacent_tiles(well_coords)
                for coord_pair in tiles_next_to_well:
                    if isinstance(player.board[coord_pair], FarmType) or isinstance(player.board[coord_pair], TheatreType):
                        player.well_score += 2
                        break
        if shed in cards_this_game:
            for well_coords in player.well_coords:
                player.well_score += 1
        return player.well_score
    
    def get_monument_score(player):
        player.monument_score = 0
        player.empty_tile_count = 0


        player.monument_constructed = False
        cottage_found = False
        farm_found = False
        factory_found = False
        tavern_found = False
        theatre_found = False
        chapel_found = False
        well_found = False


        player.total_cottage_count = 0
        unique_building_count = 0
        missing_building_types = 7
        for tile_coords, tile_content in player_board_dict.items():
            if isinstance(tile_content, Monument):
                player.monument_constructed = True
                player.monument_coords = tile_coords
            if isinstance(tile_content, Resource):
                player.empty_tile_count += 1
        for row in player.board:
            for tile in row:
                if isinstance(tile, CottageType):
                    player.total_cottage_count += 1
                    if not cottage_found:
                        unique_building_count += 1
                        cottage_found = True
                if isinstance(tile, FarmType):
                    if not farm_found:
                        unique_building_count += 1
                        farm_found = True
                if isinstance(tile, FactoryType):
                    if not factory_found:
                        unique_building_count += 1
                        factory_found = True
                if isinstance(tile, TavernType):
                    if not tavern_found:
                        unique_building_count += 1
                        tavern_found = True
                if isinstance(tile, TheatreType):
                    if not theatre_found:
                        unique_building_count += 1
                        theatre_found = True
                if isinstance(tile, ChapelType):
                    if not chapel_found:
                        unique_building_count += 1
                        chapel_found = True
                if isinstance(tile, WellType):
                    if not well_found:
                        unique_building_count += 1
                        well_found = True
        missing_building_types = 7 - unique_building_count

        if player.monument_constructed:
            
            if player.get_monument() == architects_guild:
                player.monument_score = 1
            
            if player.get_monument() == archive_of_the_second_age:
                player.monument_score = unique_building_count

        #     Barrett_Castle scoring logic handled elsewhere

            if player.get_monument() == cathedral_of_caterina:
                player.monument_score = 2
                player.empty_tile_score = 0
            
            if player.get_monument() == fort_ironweed:
                player.monument_score = 7
            
            if player.get_monument() == grand_mausoleum_of_the_rodina:
                player.unfed_cottage_count = player.total_cottage_count - player.fed_cottage_count
                player.monument_score = player.unfed_cottage_count * 3  # unfed cottage points counted by monument
                # player.cottage_score = player.unfed_cottage_count * 3
            
            if player.get_monument() == grove_university:
                player.monument_score = 3
            
            if player.get_monument() == mandras_palace:
                monument_adjacent_tile_contents = player.check_adjacent_tiles(player.monument_coords)
                for tile in monument_adjacent_tile_contents:
                    if isinstance(tile, CottageType):
                        player.total_cottage_count += 1
                        if not cottage_found:
                            unique_building_count += 1
                            cottage_found = True
                    if isinstance(tile, FarmType):
                        if not farm_found:
                            unique_building_count += 1
                            farm_found = True
                    if isinstance(tile, FactoryType):
                        if not factory_found:
                            unique_building_count += 1
                            factory_found = True
                    if isinstance(tile, TavernType):
                        if not tavern_found:
                            unique_building_count += 1
                            tavern_found = True
                    if isinstance(tile, TheatreType):
                        if not theatre_found:
                            unique_building_count += 1
                            theatre_found = True
                    if isinstance(tile, ChapelType):
                        if not chapel_found:
                            unique_building_count += 1
                            chapel_found = True
                    if isinstance(tile, WellType):
                        if not well_found:
                            unique_building_count += 1
                            well_found = True
                player.monument_score = unique_building_count * 2

            if player.get_monument() == obelisk_of_the_crescent:
                player.monument_score = 0

            if player.get_monument() == opaleyes_watch:
                player.monument_score = 0

            if player.get_monument() == shrine_of_the_elder_tree:
                shrine_score_dict = {1: 1, 2: 2, 3: 3, 4:4, 5:5, 6:8}
                player.monument_score = shrine_score_dict[player.shrine_key]
            
            if player.get_monument() == silva_forum:
                player.monument_score = 1 + len(player.largest_contiguous_group())

            if player.get_monument() == the_sky_baths:
                player.monument_score = 2 * missing_building_types

            if player.get_monument() == the_starloom:
                starloom_dict = {1: 6, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0}
                player.monument_score = starloom_dict[player.finish_position]

            if player.get_monument() == statue_of_the_bondmaker:
                player.monument_score = 0

        player.empty_tile_score *= player.empty_tile_count
        return player.monument_score, player.empty_tile_score

    def get_farm_count(player):
        player.farm_count = 0
        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == farm:
                player.farm_count += 1
        return player.farm_count

    
    if farm in cards_this_game: # CALCULATES ALL POSSIBLE FEED COMBINATION SCORES TO RETURN ONLY THE HIGHEST SCORING FARM FEED COMBINATION
        player.farm_count = get_farm_count(player)
        max_number_of_feeds = (player.farm_count * 4)   # each farm can feed four feedable buildings
        player.feedable_count, player.feedable_dict = get_feedable_count(player)
        number_of_feeds = min(player.feedable_count, max_number_of_feeds)

        feed_combinations = combinations(player.feedable_dict, number_of_feeds)
        games_dict = {}
        scores_dict = {}
        for combination in feed_combinations:   # EACH GAME IN WHICH DIFFERENT COMBINATIONS OF FEEDABLE BUILDINGS ARE FED

            player.cottage_score = 0
            player.monument_score = 0
            player.total_score = 0
            player.fed_cottage_count = 0

            fed_board = np.full((4, 4), False)
            for coord_pair in combination:
                fed_board[coord_pair] = True
                if isinstance(player.board[coord_pair], CottageType):
                    player.cottage_score += player.board[coord_pair].score_when_fed()
                    player.fed_cottage_count += 1
                if barrett_castle == player.get_monument():
                    if isinstance(player.board[coord_pair], Monument):
                        player.monument_score += player.board[coord_pair].score_when_fed()
                        player.fed_cottage_count += 2
            player.unfed_cottage_count = number_of_feeds - player.fed_cottage_count


            player.factory_score = get_factory_score(player)
            player.chapel_score = get_chapel_score(player)
            player.tavern_score = get_tavern_score(player)
            player.theatre_score = get_theatre_score(player)
            player.well_score = get_well_score(player)
            player.monument_score, player.empty_tile_score = get_monument_score(player)


            player.total_score = player.factory_score + player.cottage_score + player.chapel_score + player.tavern_score + player.theatre_score + player.well_score + player.monument_score + player.empty_tile_score
            
            games_dict[combination] = player.total_score
            scores_dict[combination] = [player.factory_score, player.cottage_score, player.chapel_score, player.tavern_score, player.theatre_score, player.well_score, player.monument_score, player.empty_tile_score, player.total_score]

        best_scoring_game = max(games_dict, key=games_dict.get) # finds the best way to feed with farms for maximum score
        player.factory_score, player.cottage_score, player.chapel_score, player.tavern_score, player.theatre_score, player.well_score, player.monument_score, player.empty_tile_score, player.total_score = scores_dict[best_scoring_game]
        print(combination)

        score_display(player)
        return player.total_score


    player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords = get_cottage_stats(player)
    player.factory_score = get_factory_score(player)
    player.chapel_score = get_chapel_score(player)
    player.tavern_score = get_tavern_score(player)
    player.theatre_score = get_theatre_score(player)
    player.well_score = get_well_score(player)
    player.monument_score, player.empty_tile_score = get_monument_score(player)


    player.total_score = player.factory_score + player.cottage_score + player.chapel_score + player.tavern_score + player.theatre_score + player.well_score + player.monument_score + player.empty_tile_score

    score_display(player)
    return player.total_score