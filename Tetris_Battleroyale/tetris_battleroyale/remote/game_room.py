class GameRoom:
    def __init__(self, game_id):
        self.min_num_players_to_start = 2

        self.game_id = game_id
        self.players_id: list[int] = []
        self.available = True

    def add_player(self, player_id):
        '''Add a player in the game.
        Return true if the game can start, false otherwise'''
        self.players_id.append(player_id)
        return self.can_game_start()
    
    def remove_player(self, player_id):
        '''Remove the player from the room'''
        self.players_id.remove(player_id)
    
    def get_num_of_players(self):
        '''Return the number of players in the room'''
        return len(self.players_id)

    def can_game_start(self):
        '''Check if the game can start'''
        print(f"Game {self.game_id} is full: {len(self.players_id)} players")
        return len(self.players_id) >= self.min_num_players_to_start
    
    def is_room_available(self):
        '''Check if room is available'''
        return self.available
    
    def change_room_availability(self):
        '''Set to false the availability of the room'''
        self.available = False
    
    def get_game_id(self):
        '''Returns the game id'''
        return self.game_id
    
    def is_game_over(self, player_id):
        '''Removes the defeated player and checks if the game is over'''
        self.players_id.remove(player_id)
        return len(self.players_id) == 1
    
    def get_winner_id(self):
        '''Returns the id of the player who wins the game'''
        return self.players_id[0]