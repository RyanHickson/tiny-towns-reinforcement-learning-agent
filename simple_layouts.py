import numpy as np
from resources import *


# COTTAGE TYPES
cottage_layout = [[wild,    wheat],
                  [brick,   glass]]

# FARM TYPES
farm_layout = [[wheat,  wheat],
               [wood,   wood]]

orchard_layout = [[wheat,  wheat],
               [wood,   wood]]

greenhouse_layout = [[wheat,  wheat],
               [wood,   wood]]

granary_layout = [[wheat,  wheat],
               [wood,   wood]]

# FACTORY TYPES
factory_layout = [[wood,    wild,   wild,   wild],
                  [brick,   stone,  stone,  brick]]

warehouse_layout = [[wood,    wild,   wild,   wild],
                  [brick,   stone,  stone,  brick]]

trading_post_layout = [[wood,    wild,   wild,   wild],
                  [brick,   stone,  stone,  brick]]

bank_layout = [[wood,    wild,   wild,   wild],
                  [brick,   stone,  stone,  brick]]

# TAVERN TYPES
tavern_layout = [[brick, brick, glass]]

almshouse_layout = [[brick, brick, glass]]

inn_layout = [[brick, brick, glass]]

feast_hall_layout = [[brick, brick, glass]]

# CHAPEL TYPES
chapel_layout = [[wild,     wild,   glass],
                 [stone,    glass,  stone]]

temple_layout = [[wild,     wild,   glass],
                 [stone,    glass,  stone]]

abbey_layout = [[wild,     wild,   glass],
                 [stone,    glass,  stone]]

cloister_layout = [[wild,     wild,   glass],
                 [stone,    glass,  stone]]

# THEATRE TYPES
theatre_layout = [[wild, stone, wild],
                  [wood, glass, wood]]

tailor_layout = [[wild, stone, wild],
                  [wood, glass, wood]]

market_layout = [[wild, stone, wild],
                  [wood, glass, wood]]

bakery_layout = [[wild, stone, wild],
                  [wood, glass, wood]]

# WELL TYPES
well_layout = [[wood, stone]]

fountain_layout = [[wood, stone]]

millstone_layout = [[wood, stone]]

shed_layout = [[wood, stone]]

# MONUMENTS
architects_guild_layout = [[brick,  wheat,  stone],
                           [wood,   glass,  wood]]

archive_of_the_second_age_layout = [[brick,  wheat,  stone],
                                    [wood,   glass,  wood]]

barrett_castle_layout = [[brick,  wheat,  stone],
                         [wood,   glass,  wood]]

cathedral_of_caterina_layout = [[brick,  wheat,  stone],
                                [wood,   glass,  wood]]

fort_ironweed_layout = [[brick,  wheat,  stone],
                        [wood,   glass,  wood]]

grand_mausoleum_of_the_rodina_layout = [[brick,  wheat,  stone],
                                        [wood,   glass,  wood]]

grove_university_layout = [[brick,  wheat,  stone],
                           [wood,   glass,  wood]]

mandras_palace_layout = [[brick,  wheat,  stone],
                         [wood,   glass,  wood]]

obelisk_of_the_crescent_layout = [[brick,  wheat,  stone],
                                  [wood,   glass,  wood]]

opaleyes_watch_layout = [[brick,  wheat,  stone],
                         [wood,   glass,  wood]]

shrine_of_the_elder_tree_layout = [[brick,  wheat,  stone],
                                   [wood,   glass,  wood]]

silva_forum_layout = [[brick,  wheat,  stone],
                      [wood,   glass,  wood]]

the_sky_baths_layout = [[brick,  wheat,  stone],
                        [wood,   glass,  wood]]

the_starloom_layout = [[brick,  wheat,  stone],
                       [wood,   glass,  wood]]

statue_of_the_bondmaker_layout = [[brick,  wheat,  stone],
                                  [wood,   glass,  wood]]