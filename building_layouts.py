import numpy as np
from layout_variants import *
from resources import *

# W = WOOD
# C = WHEAT (CROP)
# B = BRICK
# G = GLASS
# S = STONE

# COTTAGE TYPES
cottage_layout = [[" ","wheat"],
                 ["brick","glass"]]

# FARM TYPES
farm_layout = [["wheat","wheat"],
              ["wood","wood"]]

orchard_layout = [["stone","wheat"],
                 ["wheat","wood"]]

greenhouse_layout = [["wheat","glass"],
                    ["wood","wood"]]

granary_layout = [["wheat","wheat"],
                 ["wood","brick"]]

# FACTORY TYPES
factory_layout = [["wood"," "," "," "],
                 ["brick","stone","stone","brick"]]

warehouse_layout = [["wheat","wood","wheat"],
                   ["brick"," ","brick"]]

trading_post_layout = [["stone","wood"," "],
                     ["stone","wood","brick"]]

bank_layout = [["wheat","wheat"," "],
              ["wood","glass","brick"]]

# TAVERN TYPES
tavern_layout = [["brick","brick","glass"]]

almshouse_layout = [["stone","stone","glass"]]

inn_layout = [["wheat","stone","glass"]]

feast_hall_layout = [["wood","wood","glass"]]

# CHAPEL TYPES
chapel_layout = [[" "," ","glass"],
                ["stone","glass","stone"]]

temple_layout = [[" "," ","glass"],
                ["brick","brick","stone"]]

abbey_layout = [[" "," ","glass"],
               ["brick","stone","stone",]]

cloister_layout = [[" "," ","glass"],
                  ["wood","brick","stone"]]

# THEATRE TYPES
theatre_layout = [[" ","stone"," "],
                 ["wood","glass","wood"]]

tailor_layout = [[" ","wheat"," "],
                ["stone","glass","stone"]]

market_layout = [[" ","wood"," "],
                ["stone","glass","stone"]]

bakery_layout = [[" ","wheat"," "],
                ["brick","glass","brick"]]

# WELL TYPES
well_layout = [["wood","stone"]]

fountain_layout = [["wood","stone"]]

millstone_layout = [["wood","stone"]]

shed_layout = [["wood","stone"]]

# MONUMENTS
architects_guild_layout = [[" "," ","glass"],
                         [" ","wheat","stone"],
                         ["wood","brick"," "]]

archive_of_the_second_age_layout = [["wheat","wheat"],
                               ["brick","glass"]]

barrett_castle_layout = [["wheat"," "," ","stone"],
                       ["wood","glass","glass","brick"]]

cathedral_of_caterina_layout = [[" ","wheat"],
                             ["stone","glass"]]

fort_ironweed_layout = [["wheat"," ","brick"],
                      ["stone","wood","stone"]]

grand_mausoleum_of_the_rodina_layout = [["wheat","wheat"],
                                   ["brick","stone"]]

grove_university_layout = [[" ","brick"," "],
                         ["stone","glass","stone"]]

mandras_palace_layout = [["wheat","glass"],
                       ["brick","wood"]]

obelisk_of_the_crescent_layout = [["wheat"," "," "],
                              ["brick","glass","brick"]]

opaleyes_watch_layout = [["wood"," "," "," "],
                       ["brick","glass","wheat","wheat"],
                       ["stone"," "," "," "]]

shrine_of_the_elder_tree_layout = [["brick","wheat","stone"],
                              ["wood","glass","wood"]]

silva_forum_layout = [[" "," ","wheat"," "],
                    ["brick","brick","stone","wood"]]

the_sky_baths_layout = [[" ","wheat"," "],
                     ["stone","glass","wood"],
                     ["brick"," ","brick"]]

the_starloom_layout = [["glass","glass",],
                     ["wood","wheat"]]

statue_of_the_bondmaker_layout = [["wood","stone","stone","glass"],
                                  ["wheat"," "," "," "]]

def get_not_wilds(layout):
    """
    Return tiles of a building _layout that contain one of the resources required to complete that building
    """
    co_ords = []
    for row_index, row in enumerate(layout):
        for col_index, cell in enumerate(row):
            if cell != " ":
                co_ords.append((row_index, col_index))
    return co_ords

def find_placements(board, card):
    """
    Finds all building placement possibilities and returns a dictionary of
    co-ordinate pair keys and building placement possibility values
    """
    variants = create_variants(card.get_layout())
    board_rows, board_cols = len(board), len(board[0])
    placement_dict = {}
    placement_options = []
    build_list = []

    for variant in variants:
        variant = np.array(variant)
        variant_rows, variant_cols = variant.shape
        not_wilds = get_not_wilds(variant.tolist())

        for i in range(board_rows - variant_rows + 1):
            for j in range(board_cols - variant_cols + 1):
                match = True
                for r, c in not_wilds:
                    board_value = board[i + r][j + c]
                    layout_value = variant[r][c]
                    if board_value != layout_value and board_value != wild:      # CHECK FOR RESOURCE MISMATCH AND WILD RESOURCE
                        match = False
                        break
                if match:
                    coord_set = []
                    for el in not_wilds:
                        coord_set.append((i+el[0], j+el[1]))
                    for coord_pair in coord_set:
                        if coord_pair in placement_dict.keys():
                            placement_dict[coord_pair].add(card.get_name())
                        else:
                            placement_dict[coord_pair] = {card.get_name()}
                        placement_options.append({
                            coord_pair: card.get_name(),
                            "co-ords": coord_set
                        })
    for el in placement_options:
            if el not in build_list:
                build_list.append(el)
    return placement_dict, build_list

def find_all_placements(player, cards):
    coord_dictionary = dict()
    all_build_options = []
    for card in cards:
        build_dict, build_options = find_placements(player.show_board(), card)
        for coord, building in build_dict.items():
            if coord in coord_dictionary.keys():
                coord_dictionary[coord].update(building)
            else:
                coord_dictionary[coord] = set(building)
        all_build_options.append(build_options)
    return coord_dictionary, all_build_options