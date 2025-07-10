from resources import *
from cards import *

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
    
    def get_cottage_stats(player):
        player.cottage_score = 0

        player.cottage_count = 0
        player.farm_count = 0

        player.fed_cottage_count = 0
        player.cottage_coords = []

        for tile_coords, tile_content in player_board_dict.items():
            if tile_content == cottage:
                player.cottage_count += 1
                player.cottage_coords.append(tile_coords)
            if tile_content == farm:
                player.farm_count += 1


        player.unfed_cottage_count = player.cottage_count


        if granary in cards_this_game:
            for cottage_coord in player.cottage_coords:
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

        return player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count
    
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
    
    player.total_score += get_factory_score(player)
    player.cottage_score, player.cottage_count, player.fed_cottage_count, player.unfed_cottage_count = get_cottage_stats(player)
    player.total_score += player.cottage_score

    print("{} scores {}VP from their factories.".format(player.__str__(), get_factory_score(player)))
    print("{} scores {}VP from their cottages.".format(player.__str__(), get_cottage_score(player)))
    print("{} has a total score of {}VP".format(player.__str__(), player.total_score))

    return player.total_score