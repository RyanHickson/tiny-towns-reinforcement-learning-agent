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
    #     if tavern_choice == feast_hall:
        return player.tavern_score
    
    # def get_theatre_score():
    #     if theatre_choice == theatre:
    #     if theatre_choice == bakery:
    #     if theatre_choice == market:
    #     if theatre_choice == tailor:
    #     return theatre_score
    
    # def get_well_score():
    #     if well_choice == well:
    #     if well_choice == fountain:
    #     if well_choice == millstone:
    #     if well_choice == shed:
    #     return well_score
    
    # def get_monument_score():
    #     if monument == architects_guild:
    #     if monument == archive_of_the_second_age:
    #     if monument == barrett_castle:
    #     if monument == cathedral_of_caterina:
    #     if monument == fort_ironweed:
    #     if monument == grand_mausoleum_of_the_rodina:
    #     if monument == grove_university:
    #     if monument == mandras_palace:
    #     if monument == obelisk_of_the_crescent:
    #     if monument == opaleyes_watch:
    #     if monument == shrine_of_the_elder_tree:
    #     if monument == silva_forum:
    #     if monument == the_sky_baths:
    #     if monument == the_starloom:
    #     if monument == statue_of_the_bondmaker:
    #     return monument_score

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


            player.total_score += player.factory_score
            player.total_score += player.cottage_score
            player.total_score += player.chapel_score
            player.total_score += player.tavern_score
            player.total_score += player.monument_score
            games_dict[combination] = player.total_score
            scores_dict[combination] = [player.factory_score, player.cottage_score, player.chapel_score, player.monument_score, player.total_score]

        best_scoring_game = max(games_dict, key=games_dict.get)
        player.factory_score, player.cottage_score, player.chapel_score, player.monument_score, player.total_score = scores_dict[best_scoring_game]

        print("{} scores {}VP from their factories.".format(player.__str__(), player.factory_score))
        print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
        print("{} scores {}VP from their chapels.".format(player.__str__(), player.chapel_score))
        print("{} scores {}VP from their taverns.".format(player.__str__(), player.tavern_score))
        print("{} scores {}VP from their monument.".format(player.__str__(), player.monument_score))
        print("{} has a total score of {}VP".format(player.__str__(), player.total_score))
        return player.total_score



            


    player.factory_score = get_factory_score(player)
    player.chapel_score = get_chapel_score(player)
    player.tavern_score = get_tavern_score(player)

    
    player.total_score += player.factory_score
    player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords = get_cottage_stats(player)
    player.total_score += player.cottage_score
    player.total_score += player.chapel_score
    player.total_score += player.tavern_score
    player.total_score += player.monument_score
    print("{} scores {}VP from their factories.".format(player.__str__(), player.factory_score))
    print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
    print("{} scores {}VP from their chapels.".format(player.__str__(), player.chapel_score))
    print("{} scores {}VP from their taverns.".format(player.__str__(), player.tavern_score))
    print("{} scores {}VP from their monument.".format(player.__str__(), player.monument_score))
    print("{} has a total score of {}VP".format(player.__str__(), player.total_score))
    return player.total_score