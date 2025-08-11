from choices import *

def check_adjacent_tiles(tile_index):
    """
    A method to check the 4 surrounding neighbours of a
    given tile, and return a list of their coordinates.
    Tiles on town board boundary will have fewer neighbours.
    """
    tile_coords = board_tile_dict[tile_index]
    adjacent_relations = [(-1, 0), (0, -1), (0, +1), (+1, 0)]
    adjacent_indexes = []
    for relational_vector in adjacent_relations:
        i, j = tile_coords
        r, c = relational_vector
        if -1 < i + r < 4 and -1 < j + c < 4:
            adjacent_tiles_coords = (i + r, j + c)
            adjacent_tiles_index = board_index_dict[adjacent_tiles_coords]
            adjacent_indexes.append(adjacent_tiles_index)
    return adjacent_indexes


def locate_build_placements(layout, board):
    for row in layout:
        for tile in row:
            print(tile)
            if tile != wild:
                anchor_tile = tile
    for tile_index in range(1, 17):
        tile_coords = board_tile_dict[tile_index]