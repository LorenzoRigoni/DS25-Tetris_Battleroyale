import socket
import threading
import time
import msgpack
from package import Package

class Server:
    def __init__(self, host, port, num_max_lobbies, num_max_players_per_lobby, num_min_players_per_lobby):
        self.host = host
        self.port = port
        self.num_max_lobbies = num_max_lobbies
        self.num_max_players_per_lobby = num_max_players_per_lobby
        self.num_min_players_per_lobby = num_min_players_per_lobby

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        self.lobbies = {f"lobby_{i+1}": {"players": {}, "state": {}, "in_game": False} for i in range(self.num_max_lobbies)}

    def handle_client(self):
        '''Handle the client requests'''
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                packet = msgpack.unpackb(data)
                packet_type = packet.get("type")

                if packet_type == Package.Type.GET_AVAILABLE_LOBBIES:
                    self.send_available_lobbies(addr)
                if packet_type == Package.Type.JOIN_LOBBY:
                    self.handle_join_lobby(packet, addr)
                if packet_type == Package.Type.LEAVE_LOBBY:
                    self.handle_leave_lobby(packet, addr)
                if packet_type == Package.Type.SEND_ROW:
                    self.handle_send_row(packet)
                elif packet_type == Package.Type.UPDATE_GAME_STATE:
                    self.handle_game_state(packet)

            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")

    def send_available_lobbies(self, addr):
        '''Send to the client the available lobbies'''
        lobby_info = {lobby_id: len(lobby[Package.PLAYERS]) for lobby_id, lobby in self.lobbies.items()}
        self.send_message({Package.TYPE: "available_lobbies", "lobbies": lobby_info}, addr)

    def handle_join_lobby(self, packet, addr):
        '''Allow a player to join a lobby'''
        player_id = packet["player_id"]
        player_name = packet["player_name"]
        lobby_id = packet["lobby_id"]

        if lobby_id in self.lobbies:
            lobby = self.lobbies[lobby_id]

            if len(lobby[Package.PLAYERS]) < self.num_max_players_per_lobby and not lobby["in_game"]:
                lobby["players"][player_id] = addr
                print(f"Player {player_name} with id {player_id} joined lobby number {lobby_id}")

                #Send a broadcast message to inform all other lobby players
                broadcast_message = {"type": "player_joined", "player_id": player_id, "player_name": player_name}
                self.send_broadcast_message(lobby_id, broadcast_message)

                if len(lobby[Package.PLAYERS]) >= self.num_min_players_per_lobby:
                    threading.Thread(target=self.start_game_countdown, args=(lobby_id,)).start()

                joined_lobby_message = {Package.TYPE: "player_joined", "player_id": player_id, "player_name": player_name}
                self.send_message(joined_lobby_message, addr)
            else:
                full_lobby_message = {Package.TYPE: "error_full_lobby", "message": "Lobby full or already started"}
                self.send_message(full_lobby_message, addr)
        else:
            no_existing_lobby_message = {Package.TYPE: "error_no_existing_lobby", "message": "Lobby do not exists"}
            self.send_message(no_existing_lobby_message, addr)

    def handle_leave_lobby(self, packet, addr):
        '''Handle the leaving of a player from the lobby'''
        player_id = packet["player_id"]
        player_name = packet["player_name"]
        lobby_id = packet["lobby_id"]

        if lobby_id in self.lobbies and player_id in self.lobbies[lobby_id]["players"]:
            del self.lobbies[lobby_id]["players"][player_id]
            print(f"Player {player_name} left the lobby")

            left_message = {"type": "player_left", "player_id": player_id, "player_name": player_name}
            self.broadcast_lobby(lobby_id, left_message)

    def start_game_countdown(self, lobby_id):
        '''Activate a 5 second countdown when a lobby is started'''
        lobby = self.lobbies[lobby_id]
        if not lobby["in_game"]:
            for i in range(5, 0, -1):
                self.send_broadcast_message(lobby_id, {"type": "game_countdown", "seconds": i})
                time.sleep(1)
            lobby["in_game"] = True
            self.send_broadcast_message(lobby_id, {"type": "game_start"})

    def handle_send_row(self, packet):
        '''Send a broken row to all (or to a specific one) oppents'''
        lobby_id = packet["lobby_id"]
        from_player = packet["from"]
        to_player = packet["to"]
        lines = packet["lines"]

        if lobby_id in self.lobbies and to_player in self.lobbies[lobby_id]["players"]:
            target_addr = self.lobbies[lobby_id]["players"][to_player]
            self.send_message({"type": "row_received", "from": from_player, "lines": lines}, target_addr)

    def handle_game_state(self, packet):
        '''Syncronize the game state'''
        lobby_id = packet["lobby_id"]
        player_id = packet["player_id"]
        state = packet["grid"]

        if lobby_id in self.lobbies:
            self.lobbies[lobby_id]["state"][player_id] = state

    def send_message(self, message, addr):
        '''Send a message to a specific client'''
        packed_data = msgpack.packb(message)
        self.socket.sendto(packed_data, addr)

    def send_broadcast_message(self, lobby_id, message):
        '''Send a message to all the clients of a lobby'''
        if lobby_id in self.lobbies:
            for addr in self.lobbies[lobby_id]["players"].values():
                self.send_message(message, addr)