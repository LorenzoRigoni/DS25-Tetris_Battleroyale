from server import Server
from package import Package

class ServerGameManager(Server):
    '''
    This class manage the logic of server in the lobby:
        1. send the game state of a player to all others players
        2. send the broken rows to all other players (or to a specifc one)
        3. checks if remains only one player (victory)
    '''

    def __init__(self, host, port, num_max_lobbies, num_max_players_per_lobby, num_min_players_per_lobby):
        Server.__init__(host, port, num_max_lobbies, num_max_players_per_lobby, num_min_players_per_lobby)

    def handle_client(self):
        '''Handle the client requests'''
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                packet =Package.decode(data)
                packet_type = packet.get("type")

                if packet_type == Package.GET_LOBBIES:
                    self.send_available_lobbies(addr)
                if packet_type == Package.JOIN_LOBBY:
                    self.handle_join_lobby(packet, addr)
                if packet_type == Package.LEAVE_LOBBY:
                    self.handle_leave_lobby(packet, addr)
                if packet_type == Package.SEND_ROW:
                    self.send_broken_row(packet["lobby_id"], packet["player_id"], packet["target"], packet["rows"])
                elif packet_type == Package.UPDATE_STATE:
                    self.update_state(packet["lobby_id"], packet["player_id"], packet["grid_state"])
                elif packet_type == Package.PLAYER_DEFEATED:
                    self.handle_defeat(packet["lobby_id"], packet["player_id"], packet["player_name"])

            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")

    def send_broken_row(self, lobby_id, from_player, to_player, lines):
        '''Send to a player (or to all) the broken rows'''
        if to_player == None:
            self.send_broadcast_message(lobby_id, from_player, Package.ROW_RECEIVED, lines = lines)
        else:
            if to_player in self.lobbies[lobby_id]["players"]:
                self.send_message(Package.SEND_ROW, self.lobbies[lobby_id]["players"][to_player], lines = lines)

    def update_state(self, lobby_id, player_id, grid_state):
        '''Update the state of a player and send to all others players'''
        if lobby_id in self.lobbies and player_id in self.lobbies[lobby_id]["players"]:
            self.lobbies[lobby_id]["state"][player_id] = grid_state
            self.send_broadcast_message(lobby_id, Package.UPDATE_STATE, grid_state = grid_state, player_id = player_id)

    def handle_defeat(self, lobby_id, player_id, player_name):
        '''Manage the defeat of a player and checks if the game is over'''
        del self.lobbies[lobby_id]["players"][player_id]
        self.send_broadcast_message(lobby_id, Package.PLAYER_DEFEATED, player_id = player_id, player_name = player_name)

        if len(self.lobbies[lobby_id]["players"]) == 1:
            winner = list(self.lobbies[lobby_id]["players"]["player_name"])[0]
            self.send_broadcast_message(lobby_id, Package.GAME_OVER, winner = winner)
            self.reset_lobby(lobby_id)

    def reset_lobby(self, lobby_id):
        '''Reset the lobby when the game is over'''
        self.lobbies[lobby_id]["players"] = {}
        self.lobbies[lobby_id]["state"] = {}
        self.lobbies[lobby_id]["in_game"] = False