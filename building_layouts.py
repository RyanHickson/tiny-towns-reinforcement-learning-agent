import numpy as np
from resources import *

# W = WOOD
# C = WHEAT (CROP)
# B = BRICK
# G = GLASS
# S = STONE

# COTTAGE TYPES
cottage_layout = [[wild, wheat], [brick, glass]]

# FARM TYPES
farm_layout = [[wheat, wheat], [wood, wood]]

orchard_layout = [[stone, wheat], [wheat, wood]]

greenhouse_layout = [[wheat, glass], [wood, wood]]

granary_layout = [[wheat, wheat], [wood, brick]]

# FACTORY TYPES
factory_layout = [[wood, wild, wild, wild], [brick, stone, stone, brick]]

warehouse_layout = [[wheat, wood, wheat], [brick, wild, brick]]

trading_post_layout = [[stone, wood, wild], [stone, wood, brick]]

bank_layout = [[wheat, wheat, wild], [wood, glass, brick]]

# TAVERN TYPES
tavern_layout = [[brick, brick, glass]]

almshouse_layout = [[stone, stone, glass]]

inn_layout = [[wheat, stone, glass]]

feast_hall_layout = [[wood, wood, glass]]

# CHAPEL TYPES
chapel_layout = [[wild, wild, glass], [stone, glass, stone]]

temple_layout = [[wild, wild, glass], [brick, brick, stone]]

abbey_layout = [
    [wild, wild, glass],
    [
        brick,
        stone,
        stone,
    ],
]

cloister_layout = [[wild, wild, glass], [wood, brick, stone]]

# THEATRE TYPES
theatre_layout = [[wild, stone, wild], [wood, glass, wood]]

tailor_layout = [[wild, wheat, wild], [stone, glass, stone]]

market_layout = [[wild, wood, wild], [stone, glass, stone]]

bakery_layout = [[wild, wheat, wild], [brick, glass, brick]]

# WELL TYPES
well_layout = [[wood, stone]]

fountain_layout = [[wood, stone]]

millstone_layout = [[wood, stone]]

shed_layout = [[wood, stone]]

# MONUMENTS
architects_guild_layout = [
    [wild, wild, glass],
    [wild, wheat, stone],
    [wood, brick, wild],
]

archive_of_the_second_age_layout = [[wheat, wheat], [brick, glass]]

barrett_castle_layout = [[wheat, wild, wild, stone], [wood, glass, glass, brick]]

cathedral_of_caterina_layout = [[wild, wheat], [stone, glass]]

fort_ironweed_layout = [[wheat, wild, brick], [stone, wood, stone]]

grand_mausoleum_of_the_rodina_layout = [[wheat, wheat], [brick, stone]]

grove_university_layout = [[wild, brick, wild], [stone, glass, stone]]

mandras_palace_layout = [[wheat, glass], [brick, wood]]

obelisk_of_the_crescent_layout = [[wheat, wild, wild], [brick, glass, brick]]

opaleyes_watch_layout = [
    [wood, wild, wild, wild],
    [brick, glass, wheat, wheat],
    [stone, wild, wild, wild],
]

shrine_of_the_elder_tree_layout = [[brick, wheat, stone], [wood, glass, wood]]

silva_forum_layout = [[wild, wild, wheat, wild], [brick, brick, stone, wood]]

the_sky_baths_layout = [[wild, wheat, wild], [stone, glass, wood], [brick, wild, brick]]

the_starloom_layout = [
    [
        glass,
        glass,
    ],
    [wood, wheat],
]

statue_of_the_bondmaker_layout = [
    [wood, stone, stone, glass],
    [wheat, wild, wild, wild],
]
