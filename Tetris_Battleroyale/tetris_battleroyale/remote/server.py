import socket
import threading
import time
from utils.package import Package
from utils.lobby import Lobby

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 12345
        self.num_max_lobbies = 10
        self.num_max_players_per_lobby = 10
        self.num_min_players_per_lobby = 4
        self.running = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.5)
        self.last_seen = {}

        self.lobbies = [Lobby(i) for i in range(self.num_max_lobbies)]
        self.id_counter = 0
        self.players_ids_names = {}

    def start(self):
        self.running = True
        threading.Thread(target=self.handle_request, daemon=True).start()
        threading.Thread(target=self.timeout_monitor, daemon=True).start()

    def handle_request(self):
        '''Handle the client requests'''
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                p_type, p_data = Package.decode(data)

                if p_type == Package.SHAKE_HAND:
                    self.shake_hand(addr)
                elif p_type == Package.HEARTBEAT:
                    self.last_seen[addr] = time.time()
                elif p_type == Package.GET_LOBBIES:
                    self.send_available_lobbies(addr)
                elif p_type == Package.JOIN_LOBBY:
                    self.handle_join_lobby(addr, int(p_data["lobby_id"]), int(p_data["player_id"]), p_data["player_name"])
                elif p_type == Package.LEAVE_LOBBY:
                    self.handle_leave_lobby(addr, int(p_data["lobby_id"]), int(p_data["player_id"]), p_data["player_name"])
                elif p_type == Package.SEND_ROW:
                    self.send_broken_row(int(p_data["lobby_id"]), int(p_data["player_id"]), p_data["player_name"], p_data["target"], p_data["row"])
                elif p_type == Package.UPDATE_STATE:
                    self.update_state(int(p_data["lobby_id"]), int(p_data["player_id"]), p_data["player_name"], p_data["grid_state"], p_data["current_piece"])
                elif p_type == Package.PLAYER_DEFEATED:
                    self.handle_defeat(int(p_data["lobby_id"]), int(p_data["player_id"]), p_data["player_name"])
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")

    def shake_hand(self, addr):
        '''Defines the first iteraction between client and server. The server sends to the client a packet with the id of the player'''
        actual_counter = self.id_counter
        self.id_counter = self.id_counter + 1
        self.send_message(Package.SHAKE_HAND, addr, player_id = actual_counter)

    def timeout_monitor(self):
        '''Checks if the clients are connected yet with an heartbeat packet'''
        while True:
            now = time.time()
            for client_addr, last_time in list(self.last_seen.items()):
                if now - last_time > 5:
                    #TODO: implement the disconnection of the player
                    pass
            time.sleep(1)

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
                self.start_game_countdown(lobby_id)
        else:
            self.send_message(Package.ERROR, addr, message = "Lobby full or already started")

    def handle_leave_lobby(self, addr, lobby_id, player_id, player_name):
        '''Handle the leaving of a player from the lobby'''

        self.lobbies[lobby_id].delete_player_to_lobby(player_id)

        self.send_message(Package.LEAVE_LOBBY, addr)
        self.send_broadcast_message(lobby_id, player_id, Package.PLAYER_LEFT, player_name = player_name)
        self.handle_defeat(lobby_id, player_id, player_name)

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