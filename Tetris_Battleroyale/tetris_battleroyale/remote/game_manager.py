class GameManager:
    def __init__(self, game_id):
        self.min_num_players_to_start = 2

        self.game_id = game_id
        self.players_id: list[int] = []

    def add_player_to_game(self, player_id):
        '''Add a player in the game.
        Return true if the game can start, false otherwise'''
        self.players_id.append(player_id)
        return self.is_game_full()

    def is_game_full(self):
        '''Checks if the game is full'''
        print(f"Game {self.game_id} is full: {len(self.players_id)} players")
        return len(self.players_id) >= self.min_num_players_to_start
    
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