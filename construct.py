from resources import *
from choices import *
from cards import Card
from ry import *
from ui import *


def player_construct(self, construction_dict, dictionary_of_players, opaleye_construct=False):
    if not opaleye_construct:
        placement = construction_dict["placement"]
        building = construction_dict["card"]
        co_ords = construction_dict["co-ords"]
        self.board[placement] = building  # BUILDING PLACEMENT ASSIGNMENT
        for coord_pair in co_ords:
            if coord_pair != placement and isinstance(self.board[coord_pair], Resource):
                self.board[coord_pair] = empty
    else:
        placement = construction_dict["placement"]
        building = construction_dict["card"]
        self.board[placement] = building

    match construction_dict["card"].__str__():
        case "Factory":
            resource_choice_index = handle_input(
                factory_resource_choice_text.format(resource_names_dict),
                range(1, 6),
                int,
            )
            self.factory_resources.append(resource_choice_index)
        case "Warehouse":
            self.warehouse_capacity += 3
        case "Bank":
            resource_choice_index = handle_input(
                bank_resource_choice_text.format(self.resource_choice_dict),
                range(1, 6),
                int,
            )
            self.bank_resources.append(resource_choice_index)
        case "Architect's Guild":
            completed_swaps = 0
            allowed_swaps = 2
            building_dict = dict_enum(self.all_cards)
            for i, row in enumerate(self.board):
                for j, tile in enumerate(row):
                    if isinstance(tile, Card):
                        if completed_swaps < allowed_swaps:
                            swap_index = handle_input(
                                f"Select a building to replace: {building_dict} ",
                                building_dict,
                                parse=int,
                            )
                            self.board[i, j] = building_dict[swap_index]
                            completed_swaps += 1
        case "Grove University":
            want_to_build = handle_input(            
                want_to_build_text.format(self.__str__(), no_yes_dict),
                range(2),
                parse=int,)
            if want_to_build:
                possible_cards = dict_enum(self.get_buildable_cards())
                card = handle_input(possible_cards, possible_cards, parse=int)
                grove_university_dict = {}
                for tile_id, tile_coords in board_tile_dict.items():
                    if self.board[tile_coords] == empty:
                         grove_university_dict[tile_id] = tile_coords
                where_to_build = handle_input(grove_university_dict, grove_university_dict, parse=int)
                self.construct({"placement": grove_university_dict[where_to_build], "card": possible_cards[card], "co-ords": []}, dictionary_of_players=dictionary_of_players, opaleye_construct=True)

        case "Opaleye's Watch":
            opaleyes_watch_buildings = 3
            opaleye_choices = dict_enum(self.get_buildable_cards())
            for el in range(opaleyes_watch_buildings):
                opaleye_building_choice = handle_input(
                    f"Select a building to hold: {opaleye_choices} ",
                    opaleye_choices,
                    parse=int,
                )
                self.opaleyes_watch_holdings.append(
                    opaleye_choices[opaleye_building_choice]
                )
                opaleye_choices.pop(opaleye_building_choice)

        case "Shrine of the Elder Tree":
            self.shrine_key = 0
            for row in self.board:
                for tile in row:
                    if isinstance(tile, Card):
                        self.shrine_key += 1
            return self.shrine_key


    master_builder_queue = list(dictionary_of_players.keys())
    for each_player in master_builder_queue:
        temp_acting_player = dictionary_of_players[each_player]
        opaleyes_watch_holdings_display = [el.__str__() for el in temp_acting_player.opaleyes_watch_holdings]
        if construction_dict["card"].__str__() in opaleyes_watch_holdings_display:
            want_to_build = handle_input(want_to_build_text.format(temp_acting_player.__str__(), no_yes_dict), range(2), parse=int)
            if want_to_build:
                opaleye_building_choice = construction_dict["card"]
                opaleye_placement_dict = {}
                for tile_id, tile_coords in board_tile_dict.items():
                    if temp_acting_player.board[tile_coords] == empty:
                        opaleye_placement_dict[tile_id] = tile_coords
                where_to_build = handle_input(where_to_build_text.format(temp_acting_player.__str__(), opaleye_placement_dict), opaleye_placement_dict, parse=int)
                temp_acting_player.opaleyes_watch_holdings.remove(construction_dict["card"])
                temp_acting_player.construct({"placement": opaleye_placement_dict[where_to_build], "card": opaleye_building_choice, "co-ords": []}, dictionary_of_players=dictionary_of_players, opaleye_construct=True)