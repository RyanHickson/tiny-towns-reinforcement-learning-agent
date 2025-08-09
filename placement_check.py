from joblib import Parallel, delayed
import time
from building_layouts import *
from cards import *
from layout_variants import create_variants, get_not_wilds
from player import Player
import random as rdm
import numpy as np
from agent import Agent

def work_towards_layout(board, layout):
    variants = create_variants(layout)
    board_rows, board_cols = len(board), len(board[0])
    min_turns_needed = 16
    moves_wanted = []
    best_matching_resources = 0

    for variant in variants:
        
        variant = np.array(variant)
        variant_rows, variant_cols = variant.shape
        not_wilds = get_not_wilds(variant.tolist())
        total_resource_count = len(not_wilds)
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
                        board_value.__str__() == layout_value.__str__()  # if tile content on player board is not the same as the tile content of the layout
                        or board_value.__str__() == trading_post.__str__()  # trading post is used as a wild resource but not picked up like other resources
                    ):
                        matching_resources += 1
                    elif board_value == empty and isinstance(layout_value, Resource):
                        moves_needed.append((layout_value, (i+r, j+c)))
                        turns_needed += 1
                    else:
                        placement_possible = False
                        break
                
                if placement_possible:
                    if (best_matching_resources < matching_resources) or (best_matching_resources == matching_resources and turns_needed < min_turns_needed):
                        best_matching_resources = matching_resources
                        min_turns_needed = turns_needed
                        moves_wanted = moves_needed.copy()
                        if turns_needed == 1:
                            return moves_wanted
    return moves_wanted


def find_all_layouts(board, card_choices):
    moves_wanted_list = []
    for card in card_choices:
        layout = card.get_layout()
        moves_wanted_list.append(work_towards_layout(board, layout))

    return moves_wanted_list