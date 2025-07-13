import numpy as np
from building_layouts import *
from cards import *
from ry import *


def rotate_90(layout):
    return np.rot90(layout)


def mirror(layout):
    return np.fliplr(layout)


def create_variants(layout):
    variants = []
    new_variant = layout.copy()
    for var in range(4):
        variants.append(new_variant)
        variants.append(mirror(new_variant))
        new_variant = rotate_90(new_variant)
    return variants


def get_not_wilds(layout):
    """
    Return tiles of a building layout that contain one of the resources required to complete that building
    """
    co_ords = []
    for row_index, row in enumerate(layout):
        for col_index, cell in enumerate(row):
            if cell != wild:
                co_ords.append((row_index, col_index))
    return co_ords


def find_placements(board, card):
    """
    Finds all building placement possibilities and returns a dictionary of
    co-ordinate pair keys and building placement possibility values
    """
    obelisk_present = False
    variants = create_variants(card.get_layout())
    board_rows, board_cols = len(board), len(board[0])
    placement_dict = {}
    placement_options = []
    placement_display = []
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
                    if (
                        board_value != layout_value.__str__()  # if tile content on player board is not the same as the tile content of the layout
                        and board_value != trading_post.__str__()  # trading post is used as a wild resource but not picked up like other resources
                    ):
                        match = False
                        break
                if match:
                    coord_set = []
                    for el in not_wilds:
                        coord_set.append((i + el[0], j + el[1]))
                    for coord_pair in coord_set:
                        if board[coord_pair] != trading_post.__str__(): # trading post being used as a wild resource is not a valid placement
                            if coord_pair in placement_dict.keys():
                                placement_dict[coord_pair].add(card.__str__())
                            else:
                                placement_dict[coord_pair] = {card.__str__()}
                                placement_options.append(
                                    {
                                        "placement": coord_pair,
                                        "card": card,
                                        "co-ords": coord_set,
                                    }
                                )
                                placement_display.append(
                                    {
                                        "placement": coord_pair,
                                        "card": card.__str__(),
                                        "co-ords": coord_set,
                                    }
                                )
                                for row in board:
                                    if obelisk_of_the_crescent.__str__() in row:
                                        obelisk_present = True
                                if card == shed or obelisk_present:
                                    for row_index, row in enumerate(board):
                                        for col_index, tile in enumerate(row):
                                            
                                            if tile == empty.__str__():
                                                placement_options.append(
                                                    {
                                                    "placement": (row_index, col_index),
                                                    "card": card,
                                                    "co-ords": coord_set,
                                                    }
                                                )
                                                placement_display.append(
                                                {
                                                    "placement": (row_index, col_index),
                                                    "card": card.__str__(),
                                                    "co-ords": coord_set,
                                                }
                                                )
    for el in placement_options:
        if el not in build_list:
            build_list.append(el)
    return placement_dict, dict_enum(build_list), placement_display

def find_all_placements(player, cards):
    coord_dictionary = dict()
    all_build_options = []
    full_placement_display = []
    for card in cards:
        build_dict, build_options, placement_display = find_placements(player.get_display_board(), card)
        for coord, building in build_dict.items():
            if coord in coord_dictionary.keys():
                coord_dictionary[coord].update(building)
            else:
                coord_dictionary[coord] = set(building)
        all_build_options.append(build_options)
        full_placement_display.append(placement_display)
    return coord_dictionary, all_build_options, full_placement_display
