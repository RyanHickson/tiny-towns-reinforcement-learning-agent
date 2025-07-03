import numpy as np
from building_layouts import *
from cards import *


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
                    if (
                        board_value
                        != layout_value.get_name()  # if value on player board is not the same as the value of the layout
                        and board_value != trading_post.get_name()  #
                    ):
                        match = False
                        break
                if match:
                    coord_set = []
                    for el in not_wilds:
                        coord_set.append((i + el[0], j + el[1]))
                    for coord_pair in coord_set:
                        if board[coord_pair] != trading_post.get_name():
                            if coord_pair in placement_dict.keys():
                                placement_dict[coord_pair].add(card.get_name())
                            else:
                                placement_dict[coord_pair] = {card.get_name()}
                            placement_options.append(
                                {
                                    "placement": coord_pair,
                                    "card": card,
                                    "co-ords": coord_set,
                                }
                            )
    for el in placement_options:
        if el not in build_list:
            build_list.append(el)
    return placement_dict, dict(enumerate(build_list))


def find_all_placements(player, cards):
    coord_dictionary = dict()
    all_build_options = []
    for card in cards:
        build_dict, build_options = find_placements(player.get_display_board(), card)
        for coord, building in build_dict.items():
            if coord in coord_dictionary.keys():
                coord_dictionary[coord].update(building)
            else:
                coord_dictionary[coord] = set(building)
        if build_options != {}:
            all_build_options.append(build_options)
    return dict(enumerate(coord_dictionary)), all_build_options
