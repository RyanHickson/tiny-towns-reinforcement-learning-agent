from resources import *
from cards import *
from itertools import combinations

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
                    if isinstance(player.board[coord_pair], FarmType):
                        if isinstance(player.board[feedable_coord_pair], CottageType):
                            player.cottage_score += 3
                            player.fed_coords.append(feedable_coord_pair)
                        if barrett_castle in player.get_all_cards():
                            if isinstance(player.board[feedable_coord_pair], Monument):
                                player.monument_score += 5
                                player.fed_coords.append(feedable_coord_pair)

        if greenhouse in cards_this_game:
            greenhouse_feed_list, player.fed_coords = player.greenhouse_feeding()
            player.cottage_score += sum([sum(el) for el in greenhouse_feed_list[:player.greenhouse_count]])

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
                        player.cottage_score += 3
                        player.fed_cottage_count += 1
                        player.unfed_cottage_count -= 1
                        player.fed_coords.append(coord_pair)
                        break   # ensures each cottage only fed once

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
            temple_adjacent_fed_count = 0
            for coord_pair in player.chapel_coords: # for each temple on the board
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
                abbey_adjacent_tile_contents = player.check_adjacent_tiles(coord_pair)
                for adjacent_coords in abbey_adjacent_tile_contents:
                    try:
                        adjacent_tile_content = player.board[adjacent_coords]
                    except:
                        continue
                if not isinstance(adjacent_tile_content, FactoryType) or isinstance(adjacent_tile_content, TavernType) or isinstance(adjacent_tile_content, TheatreType):
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
                    total_score -= 1
                case 2:
                    total_score += 5
                case 3:
                    total_score -= 3
                case 4:
                    total_score += 15
                case 5:
                    total_score -= 5
                case _: # 6+ case
                    total_score += 26
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
    #     if market in cards_this_game:
    #     if tailor in cards_this_game:
        return player.theatre_score
    
    # def get_well_score(player):
    #     if well in cards_this_game:
    #     if fountain in cards_this_game:
    #     if millstone in cards_this_game:
    #     if shed in cards_this_game:
    #     return player.well_score
    
    # def get_monument_score(player):
    #     if player.get_monument() == architects_guild:
    #     if player.get_monument() == archive_of_the_second_age:
    #     if player.get_monument() == barrett_castle:
    #     if player.get_monument() == cathedral_of_caterina:
    #     if player.get_monument() == fort_ironweed:
    #     if player.get_monument() == grand_mausoleum_of_the_rodina:
    #     if player.get_monument() == grove_university:
    #     if player.get_monument() == mandras_palace:
    #     if player.get_monument() == obelisk_of_the_crescent:
    #     if player.get_monument() == opaleyes_watch:
    #     if player.get_monument() == shrine_of_the_elder_tree:
    #     if player.get_monument() == silva_forum:
    #     if player.get_monument() == the_sky_baths:
    #     if player.get_monument() == the_starloom:
    #     if player.get_monument() == statue_of_the_bondmaker:
    #     return player.monument_score

    def get_farm_count(player):
        player.farm_count = 0
        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == farm:
                player.farm_count += 1
        return player.farm_count

    
    if farm in cards_this_game:
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
                    player.cottage_score += 3
                    player.fed_cottage_count += 1
                if barrett_castle in player.get_all_cards():
                    if isinstance(player.board[coord_pair], Monument):
                        player.monument_score += 5
                        player.fed_cottage_count += 2
            player.unfed_cottage_count = player.cottage_score - player.fed_cottage_count


            player.factory_score = get_factory_score(player)
            player.chapel_score = get_chapel_score(player)
            player.tavern_score = get_tavern_score(player)
            player.theatre_score = get_theatre_score(player)


            player.total_score += player.factory_score
            player.total_score += player.cottage_score
            player.total_score += player.chapel_score
            player.total_score += player.tavern_score
            player.total_score += player.theatre_score
            player.total_score += player.monument_score
            games_dict[combination] = player.total_score
            scores_dict[combination] = [player.factory_score, player.cottage_score, player.chapel_score, player.monument_score, player.total_score]

        best_scoring_game = max(games_dict, key=games_dict.get)
        player.factory_score, player.cottage_score, player.chapel_score, player.monument_score, player.total_score = scores_dict[best_scoring_game]

        print("{} scores {}VP from their factories.".format(player.__str__(), player.factory_score))
        print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
        print("{} scores {}VP from their chapels.".format(player.__str__(), player.chapel_score))
        print("{} scores {}VP from their taverns.".format(player.__str__(), player.tavern_score))
        print("{} scores {}VP from their theatres.".format(player.__str__(), player.theatre_score))
        print("{} scores {}VP from their monument.".format(player.__str__(), player.monument_score))
        print("{} has a total score of {}VP".format(player.__str__(), player.total_score))
        return player.total_score



            


    player.factory_score = get_factory_score(player)
    player.chapel_score = get_chapel_score(player)
    player.tavern_score = get_tavern_score(player)
    player.theatre_score = get_theatre_score(player)
    
    player.total_score += player.factory_score
    player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords = get_cottage_stats(player)
    player.total_score += player.cottage_score
    player.total_score += player.chapel_score
    player.total_score += player.tavern_score
    player.total_score += player.theatre_score
    player.total_score += player.monument_score
    print("{} scores {}VP from their factories.".format(player.__str__(), player.factory_score))
    print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
    print("{} scores {}VP from their chapels.".format(player.__str__(), player.chapel_score))
    print("{} scores {}VP from their taverns.".format(player.__str__(), player.tavern_score))
    print("{} scores {}VP from their theatres.".format(player.__str__(), player.theatre_score))
    print("{} scores {}VP from their monument.".format(player.__str__(), player.monument_score))
    print("{} has a total score of {}VP".format(player.__str__(), player.total_score))
    return player.total_score