from resources import *

# START OF GAME
# MONUMENT CHOICE

# IF ACTIVE PLAYER (MASTER BUILDER)
# RESOURCE CHOICE
resource_dict = {1: wood, 2: wheat, 3: glass, 4: brick, 5: stone}
resource_names_dict = {1: wood.get_name(), 2: wheat.get_name(), 3: glass.get_name(), 4: brick.get_name(), 5: stone.get_name()}

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

# BUILDING CHOICE

# BUILDING PLACEMENT
