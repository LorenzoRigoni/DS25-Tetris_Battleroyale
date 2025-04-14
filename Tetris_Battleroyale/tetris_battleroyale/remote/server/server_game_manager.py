import time
from server import Server
from package import Package

class ServerGameManager(Server):
    '''
    This class manage the logic of server in the lobby:
        1. send the game state of a player to all others players
        2. send the broken rows to all other players (or to a specifc one)
        3. checks if remains only one player (victory)
    '''

    def __init__(self, host, port):
        Server.__init__(host, port)

    def handle_request(self):
        '''Handle the client requests'''
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                packet = Package.decode(data)
                packet_type = packet.get("type")

                if packet_type == Package.SHAKE_HAND:
                    self.shake_hand(addr)
                if packet_type == Package.GET_LOBBIES:
                    self.send_available_lobbies(addr)
                if packet_type == Package.JOIN_LOBBY:
                    self.handle_join_lobby(addr, int(packet["lobby_id"]), int(packet["player_id"]), packet["player_name"])
                if packet_type == Package.LEAVE_LOBBY:
                    self.handle_leave_lobby(addr, int(packet["lobby_id"]), int(packet["player_id"]), packet["player_name"])
                if packet_type == Package.SEND_ROW:
                    self.send_broken_row(int(packet["lobby_id"]), int(packet["player_id"]), packet["player_name"], packet["target"], packet["row"])
                elif packet_type == Package.UPDATE_STATE:
                    self.update_state(int(packet["lobby_id"]), int(packet["player_id"]), packet["player_name"], packet["grid_state"], packet["current_piece"])
                elif packet_type == Package.PLAYER_DEFEATED:
                    self.handle_defeat(int(packet["lobby_id"]), int(packet["player_id"]), packet["player_name"])

            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")

    def send_broken_row(self, lobby_id, from_player, from_name, to_player, row):
        '''Send to a player (or to all) the broken rows'''
        if to_player == None:
            self.send_broadcast_message(lobby_id, from_player, Package.ROW_RECEIVED, from_player = from_name, row = row)
        else:
            "TODO: implement the version with a target"

    def update_state(self, lobby_id, player_id, player_name, grid_state, current_piece):
        '''Update the state of a player and send to all others players'''
        if lobby_id in self.lobbies and player_id in self.lobbies[lobby_id].get_players():
            self.lobbies[lobby_id].update_game_state(grid_state)
            self.send_broadcast_message(lobby_id, Package.UPDATE_STATE, grid_state = grid_state, player_id = player_id, player_name = player_name, current_piece = current_piece)

    def handle_defeat(self, lobby_id, player_id, player_name):
        '''Manage the defeat of a player and checks if the game is over'''
        self.send_broadcast_message(lobby_id, Package.PLAYER_DEFEATED, player_id = player_id, player_name = player_name)

        if self.lobbies[lobby_id].get_num_of_players() == 1:
            winner = self.lobbies[lobby_id].get_players()
            for id in winner:
                winner_name = self.players_ids_names[id]
            self.send_broadcast_message(lobby_id, Package.GAME_OVER, winner = winner_name)
            time.sleep(5)
            self.reset_lobby(lobby_id)

    def reset_lobby(self, lobby_id):
        '''Reset the lobby when the game is over'''
        self.lobbies[lobby_id].reset_lobby()