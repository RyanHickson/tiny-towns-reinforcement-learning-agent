from resources import *
from choices import *
from cards import Card
from ry import *
from ui import *

def player_construct(self, construction_dict):
    placement = construction_dict["placement"]
    building = construction_dict["card"]
    co_ords = construction_dict["co-ords"]
    self.board[placement] = building
    for coord_pair in co_ords:
        if coord_pair != placement and isinstance(self.board[coord_pair], Resource):
            self.board[coord_pair] = empty

    match construction_dict["card"].__str__():
        case "Factory":
            resource_choice_index = handle_input(factory_resource_choice_text.format(resource_names_dict), range(1,6), int)
            self.factory_resources.append(resource_choice_index)
        case "Warehouse":
            self.warehouse_capacity += 3
        case "Bank":
            print("constructing bank")
            resource_choice_index = handle_input(bank_resource_choice_text.format(self.resource_choice_dict), range(1,6), int)
            self.bank_resources.append(resource_choice_index)
        case "Architect's Guild":
            completed_swaps = 0
            allowed_swaps = 2
            building_dict = dict_enum(self.all_cards)
            for i, row in enumerate(self.board):
                for j ,tile in enumerate(row):
                    print(tile)
                    print(tile.__str__())
                    print(type(tile))
                    if isinstance(tile, Card):
                        if completed_swaps < allowed_swaps:
                            swap_index = handle_input(f"Select a building to replace: {building_dict} ", building_dict, parse=int)
                            self.board[i, j] = building_dict[swap_index]
                            completed_swaps += 1
        # case "Grove University":
        #     place a building on an empty tile
        case "Shrine of the Elder Tree":
            self.shrine_key = 0
            for row in self.board:
                for tile in row:
                    if isinstance(tile, Card):
                        self.shrine_key += 1
            return self.shrine_key