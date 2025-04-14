class Lobby:
    def __init__(self, lobby_id):
        self.lobby_id = lobby_id
        self.players = {}
        self.game_states = {}
        self.is_game_started = False

    def add_player_to_lobby(self, player_id, player_name):
        self.players[player_id] = player_name

    def delete_player_to_lobby(self, player):
        del self.players[player]

    def update_game_state(self, player, state):
        self.game_states[player] = state

    def get_game_state_of_player(self, player):
        return self.game_states[player]
    
    def start_game(self):
        self.is_game_started = True

    def get_num_of_players(self):
        return self.players.count()
    
    def get_players(self):
        return self.players
    
    def check_game_started(self):
        return self.is_game_started
    
    def get_lobby_id(self):
        return self.lobby_id

    def reset_lobby(self):
        self.players = {}
        self.game_states = {}
        self.is_game_started = False