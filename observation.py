def observe_player(self, each_player):
    player = self.dictionary_of_players[each_player]
    player_id = player.get_id()
    return {"player_id": player_id,
            "player_board": player.get_display_board(),
            "player_resources": player.get_factory_type_resources()}



def get_observation(self, each_player):
    player = self.dictionary_of_players[each_player]
    return {
        "myself": {
            "player_id": player.get_id(),
            "player_board": player.get_display_board(),
            "player_fact_type_resources": player.get_factory_type_resources(),
            "card_choices": player.display_all_cards(),
        },
        "others": 
        [observe_player(self, each_player)  for each_player in self.dictionary_of_players if self.dictionary_of_players[each_player].get_id() != player.get_id()]
    }