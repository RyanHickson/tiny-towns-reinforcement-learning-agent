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
    player.total_score = 0

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
            if tile_content == barrett_castle:
                player.feedable_count += 1
                player.feedable_dict[tile_coords] = "barrett_castle"
        return player.feedable_count, player.feedable_dict
    
    def get_cottage_stats(player):
        player.cottage_score = 0
        player.barrett_castle_present = False

        player.cottage_count = 0
        player.fed_cottage_count = 0

        player.feedable_coords = []

        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == cottage:
                player.cottage_count += 1
                player.feedable_coords.append(tile_coords)
            if tile_content == barrett_castle:
                player.barrett_castle_present = True
                player.feedable_coords.append(tile_coords)

        player.unfed_cottage_count = player.cottage_count

        if granary in cards_this_game:
            for cottage_coord in player.feedable_coords:
                cottage_surrounding_coords = check_surrounding_tiles(cottage_coord)
                for coords in cottage_surrounding_coords:
                    try:
                        tile_content = player_board_dict[coords]
                    except:
                        continue
                    if tile_content == granary:
                        player.cottage_score += 3
                        player.fed_cottage_count += 1
                        player.unfed_cottage_count -= 1
                        break   # ensures each cottage only fed once

        return player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords
    
    # def get_chapel_score():
    #     if chapel_choice == chapel:
    #     if chapel_choice == temple:
    #     if chapel_choice == abbey:
    #     if chapel_choice == cloister:
    #     return chapel_score
    
    # def get_tavern_score():
    #     if tavern_choice == tavern:
    #     if tavern_choice == inn:
    #     if tavern_choice == almshouse:
    #     if tavern_choice == feast_hall:
    #     return tavern_score
    
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
        for combination in feed_combinations:   # EACH GAME IN WHICH DIFFERENT COMBINATIONS OF FEEDABLE BUILDINGS ARE FED

            player.cottage_score = 0
            player.monument_score = 0
            player.total_score = 0

            fed_board = np.full((4, 4), False)
            for coord_pair in combination:
                fed_board[coord_pair] = True
                if isinstance(player.board[coord_pair], CottageType):
                    player.cottage_score += 3
                if isinstance(player.board[coord_pair], Monument):
                    player.monument_score += 5

            player.total_score += get_factory_score(player)
            player.total_score += player.cottage_score
            player.total_score += player.monument_score
            games_dict[combination] = player.total_score

        print(games_dict)
        best_scoring_game = max(games_dict.values())
        return print(best_scoring_game)
        print("FARM TEST")
        print("{} scores {}VP from their factories.".format(player.__str__(), get_factory_score(player)))
        print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
        print("{} has a total score of {}VP".format(player.__str__(), player.total_score))
        return player.total_score



            



    
    player.total_score += get_factory_score(player)
    player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count, player.feedable_coords = get_cottage_stats(player)
    player.total_score += player.cottage_score
    print("FARM TEST 2 ")
    print("{} scores {}VP from their factories.".format(player.__str__(), get_factory_score(player)))
    print("{} scores {}VP from their cottages.".format(player.__str__(), player.cottage_score))
    print("{} has a total score of {}VP".format(player.__str__(), player.total_score))

    return player.total_score