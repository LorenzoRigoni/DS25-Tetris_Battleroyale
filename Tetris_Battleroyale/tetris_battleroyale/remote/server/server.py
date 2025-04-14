import socket
import threading
import time
from package import Package
from lobby import Lobby

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.num_max_lobbies = 10
        self.num_max_players_per_lobby = 10
        self.num_min_players_per_lobby = 4

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        self.lobbies = [Lobby(i) for i in range(self.num_max_lobbies)]
        self.id_counter = 0
        self.players_ids_names = {}

    def shake_hand(self, addr):
        '''Defines the first iteraction between client and server. The server sends to the client a packet with the id of the player'''
        actual_counter = self.id_counter
        self.id_counter = self.id_counter + 1
        self.send_message(Package.SHAKE_HAND, addr, player_id = actual_counter)

    def send_available_lobbies(self, addr):
        '''Send to the client the available lobbies'''
        lobbies_info = [
            {
                "id": lobby.get_lobby_id(),
                "num_players": lobby.get_num_of_players(),
                "is_game_started": lobby.check_game_started()
            }
            for lobby in self.lobbies
        ]
        self.send_message(Package.GET_LOBBIES, addr, lobbies_info = lobbies_info)

    def handle_join_lobby(self, addr, lobby_id, player_id, player_name):
        '''Allow a player to join a lobby'''
        lobby = self.lobbies[lobby_id]

        if lobby.get_num_of_players() < self.num_max_players_per_lobby and not lobby.check_game_started():
            lobby.add_player_to_lobby(player_id, addr)
            self.players_ids_names[player_id] = player_name

            self.send_message(Package.JOINED_LOBBY, addr)
            self.send_broadcast_message(lobby_id, player_id, Package.PLAYER_JOINED, player_name = player_name)

            if lobby.get_num_of_players() >= self.num_min_players_per_lobby:
                threading.Thread(target=self.start_game_countdown, args=(lobby_id,)).start()
        else:
            self.send_message(Package.ERROR, addr, message = "Lobby full or already started")

    def handle_leave_lobby(self, addr, lobby_id, player_id, player_name):
        '''Handle the leaving of a player from the lobby'''

        self.lobbies[lobby_id].delete_player_to_lobby(player_id)

        self.send_message(Package.LEAVE_LOBBY, addr)
        self.send_broadcast_message(lobby_id, player_id, Package.PLAYER_LEFT, player_name = player_name)

    def start_game_countdown(self, lobby_id):
        '''Activate a 5 second countdown when a lobby is started'''
        lobby = self.lobbies[lobby_id]
        if not lobby.check_game_started():
            self.send_broadcast_message(lobby_id, None, Package.GAME_COUNTDOWN, initial_timer = 5)
            time.sleep(5)
            lobby.start_game()
            self.send_broadcast_message(lobby_id, None, Package.GAME_START)

    def send_message(self, packet_type, addr, **kwargs):
        '''Send a message to a specific client'''
        data = Package.encode(packet_type, **kwargs)
        self.socket.sendto(data, addr)

    def send_broadcast_message(self, lobby_id, player_id, packet_type, **kwargs):
        '''Send a message to all the opponents of a lobby'''
        if player_id != None:
            opponents = {f"{p_id}: {p_addr}" for p_id, p_addr in self.lobbies[lobby_id].get_players().items() if p_id != player_id}
        else:
            opponents = {f"{p_id}: {p_addr}" for p_id, p_addr in self.lobbies[lobby_id].get_players().items()}
        for addr in opponents.values():
            self.send_message(packet_type, addr, kwargs)