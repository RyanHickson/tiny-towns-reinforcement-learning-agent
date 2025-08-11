from resources import *

# START OF GAME
# MONUMENT CHOICE

# IF ACTIVE PLAYER (MASTER BUILDER)
# RESOURCE CHOICE
resource_dict = {1: wood, 2: wheat, 3: glass, 4: brick, 5: stone}
resource_names_dict = {1: wood.__str__(), 2: wheat.__str__(), 3: glass.__str__(), 4: brick.__str__(), 5: stone.__str__()}

# RESOURCE PLACEMENT
board_tile_dict = {
    1: (0, 0),
    2: (0, 1),
    3: (0, 2),
    4: (0, 3),
    5: (1, 0),
    6: (1, 1),
    7: (1, 2),
    8: (1, 3),
    9: (2, 0),
    10: (2, 1),
    11: (2, 2),
    12: (2, 3),
    13: (3, 0),
    14: (3, 1),
    15: (3, 2),
    16: (3, 3),
}

no_yes_dict = {0: "No", 1: "Yes"}

store_swap_dict = {0: "Store", 1: "Swap"}

board_index_dict = {
    (0, 0): 1,
    (0, 1): 2,
    (0, 2): 3,
    (0, 3): 4,
    (1, 0): 5,
    (1, 1): 6,
    (1, 2): 7,
    (1, 3): 8,
    (2, 0): 9,
    (2, 1): 10,
    (2, 2): 11,
    (2, 3): 12,
    (3, 0): 13,
    (3, 1): 14,
    (3, 2): 15,
    (3, 3): 16,
}