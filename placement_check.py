from joblib import Parallel, delayed
import time
from building_layouts import *
from cards import *
from layout_variants import create_variants, get_not_wilds
from player import Player
import random as rdm
import numpy as np

def work_towards_layout(board, layout):
    variants = create_variants(layout)
    board_rows, board_cols = len(board), len(board[0])
    min_turns_needed = 7 # Maximum number of resources for a building construction is six
    moves_wanted = []
    best_matching_resources = 0
    # rdm.shuffle(variants)

    for variant in variants:
        
        variant = np.array(variant)
        variant_rows, variant_cols = variant.shape
        not_wilds = get_not_wilds(variant.tolist())
        
        for i in range(board_rows - variant_rows + 1):
            for j in range(board_cols - variant_cols + 1):
                matching_resources = 0
                placement_possible = True
                turns_needed = 0
                moves_needed = []
                for r, c in not_wilds:
                    board_value = board[i + r][j + c]
                    layout_value = variant[r][c]
                    if (
                        board_value == layout_value
                        or board_value == trading_post
                    ):
                        matching_resources += 1
                    elif isinstance(board_value, EmptyResource) and isinstance(layout_value, Resource):
                        moves_needed.append((layout_value, (i+r, j+c)))
                        turns_needed += 1
                    else:
                        placement_possible = False
                        break
                
                if placement_possible:
                    if (best_matching_resources < matching_resources) or (
                        best_matching_resources == matching_resources and 
                        turns_needed < min_turns_needed
                        ):
                        best_matching_resources = matching_resources
                        min_turns_needed = turns_needed
                        moves_wanted = moves_needed.copy()
                        if turns_needed <= 1:
                            return moves_wanted
    return moves_wanted


def find_all_layouts(board, card_choices):
    results = Parallel(n_jobs=-1)(delayed(work_towards_layout)(board, card.get_layout()) for card in card_choices)
    return results

def score_action(action, board, card_choices):
    resource, tile_coords = action
    row, col = tile_coords
    score = 0

    for card in card_choices:
        card_layout = card.get_layout()
        variants = create_variants(card_layout)
        for variant in variants:
            not_wilds = get_not_wilds(variant)
            if tile_coords in not_wilds:
                if resource == variant[tile_coords[0]][tile_coords[1]]:
                    score += 3
    return score

def actions_equal(a1, a2):
    return (a1[0] == a2[0]) and ([a1[1] == a2[1]])