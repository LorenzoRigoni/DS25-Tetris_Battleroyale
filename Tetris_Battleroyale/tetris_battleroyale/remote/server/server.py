import socket
import threading
import time
from package import Package

class Server:
    def __init__(self, host, port, num_max_lobbies, num_max_players_per_lobby, num_min_players_per_lobby,controller,lobby_id):
        self.controller = controller
        self.host = host
        self.port = port
        self.num_max_lobbies = num_max_lobbies
        self.num_max_players_per_lobby = num_max_players_per_lobby
        self.num_min_players_per_lobby = num_min_players_per_lobby
        self.lobby_id = lobby_id

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        self.lobbies = {f"lobby_{i+1}": {"players": {}, "state": {}, "in_game": False} for i in range(self.num_max_lobbies)}

    def send_available_lobbies(self, addr):
        '''Send to the client the available lobbies'''
        lobby_info = {lobby_id: len(lobby[Package.PLAYERS]) for lobby_id, lobby in self.lobbies.items()}
        self.send_message(Package.GET_LOBBIES, addr, lobby_info = lobby_info)

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

                self.send_message(Package.JOINED_LOBBY, addr, player_id = player_id, player_name = player_name)
                self.send_broadcast_message(lobby_id, player_id, Package.PLAYER_JOINED, player_name = player_name)

                if len(lobby["players"]) >= self.num_min_players_per_lobby:
                    threading.Thread(target=self.start_game_countdown, args=(lobby_id,)).start()
            else:
                self.send_message(Package.ERROR, addr, message = "Lobby full or already started")
        else:
            self.send_message(Package.ERROR, addr, message = "Lobby do not exists")

    def handle_leave_lobby(self, packet, addr):
        '''Handle the leaving of a player from the lobby'''
        player_id = packet["player_id"]
        player_name = packet["player_name"]
        lobby_id = packet["lobby_id"]

        if lobby_id in self.lobbies and player_id in self.lobbies[lobby_id]["players"]:
            del self.lobbies[lobby_id]["players"][player_id]
            print(f"Player {player_name} left the lobby")

            self.send_message(Package.LEAVE_LOBBY, addr, player_id = player_id, player_name = player_name)
            self.send_broadcast_message(lobby_id, player_id, Package.PLAYER_LEFT, player_name = player_name)

    def start_game_countdown(self, lobby_id):
        '''Activate a 5 second countdown when a lobby is started'''
        lobby = self.lobbies[lobby_id]
        if not lobby["in_game"]:
            self.send_broadcast_message(lobby_id, None, Package.GAME_COUNTDOWN, initial_timer = 5)
            time.sleep(5)
            lobby["in_game"] = True
            self.send_broadcast_message(lobby_id, None, Package.GAME_START)

    def send_message(self, packet_type, addr, **kwargs):
        '''Send a message to a specific client'''
        data = Package.encode(packet_type, **kwargs)
        self.socket.sendto(data, addr)

    def send_broadcast_message(self, lobby_id, player_id, packet_type, **kwargs):
        '''Send a message to all the opponents of a lobby'''
        if lobby_id in self.lobbies:
            if player_id != None:
                opponents = {player: addr for player, addr in self.lobbies[lobby_id]["players"] if player != player_id}
            else:
                opponents = {player: addr for player, addr in self.lobbies[lobby_id]["players"]}
            for addr in opponents:
                self.send_message(packet_type, addr, **kwargs)