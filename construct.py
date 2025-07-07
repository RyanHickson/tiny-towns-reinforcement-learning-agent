from resources import *
from choices import *
from cards import Card

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
            resource_choice_index = (int(input(f"Choose a resource to place on this factory: {resource_names_dict}")))
            self.factory_resources.append(resource_choice_index)
        case "Warehouse":
            self.warehouse_capacity += 3
        case "Bank":
            resource_choice_index = (int(input(f"Choose a resource to place in this bank: {resource_names_dict}")))
            self.bank_resources.append(resource_choice_index)
        case "Architect's Guild":
            print("Built Architect's Guild")
            completed_swaps = 0
            allowed_swaps = 2
            building_dict = dict(enumerate(self.all_cards))
            for i, row in enumerate(self.board):
                for j ,tile in enumerate(row):
                    print(tile)
                    print(tile.__str__())
                    print(type(tile))
                    if isinstance(tile, Card):
                        if completed_swaps < allowed_swaps:
                            swap_index = -1
                            while swap_index not in building_dict:
                                try:
                                    swap_index = int(input(f"Select a building to replace: {building_dict} "))
                                except:
                                    continue
                            self.board[i, j] = building_dict[swap_index]
                            completed_swaps += 1