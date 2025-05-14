import socket
import threading
import time
from remote.package import Package
import traceback

class Client:
    '''Manage the communication of the client'''

    def __init__(self, player_name, controller):
        self.player_name = player_name
        self.player_id = -1
        self.primary_server_addr = ("127.0.0.1", 8080)
        self.backup_server_addr = ("127.0.0.1", 8081)
        self.ping_addr = ("127.0.0.1", 8082)
        self.active_server_addr = self.primary_server_addr
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.controller = controller

    def send_heartbeat(self, timeout = 3):
        ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ping_socket.settimeout(timeout)

        while self.running:
            try:
                ping_socket.sendto(Package.encode(Package.HEARTBEAT, player_id = self.player_id), self.ping_addr)
                _ = ping_socket.recv(8192)
            except socket.timeout:
                self.active_server_addr = self.backup_server_addr if self.active_server_addr == self.primary_server_addr else self.primary_server_addr
                ping_socket.sendto(Package.encode(Package.HEARTBEAT, player_id = self.player_id), self.active_server_addr)
                continue
            time.sleep(1)

        ping_socket.close()

    def start(self):
        '''Starts the client'''
        self.send(Package.HANDSHAKE, player_name = self.player_name)
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

        while self.running:
            try:
                package, _ = self.client_socket.recvfrom(8192)
                type, data = Package.decode(package)
                self.handle_received_packet(type, data)
            except OSError as e:
                if e.winerror == 10054:
                    continue
            except Exception as e:
                traceback.print_exc()

    def start_game_search(self):
        '''Start the search of a game'''
        self.send(Package.START_SEARCH, player_id = self.player_id)

    def send_game_state(self, grid, current_piece):
        '''Send the game state to the server'''
        self.send(Package.GAME_STATE, player_id = self.player_id, grid = grid, current_piece = current_piece)

    def send_broken_row(self):
        '''Send the broken row to all others players'''
        self.send(Package.SEND_ROW, player_id = self.player_id)

    def send_defeat(self):
        '''Send the defeat of the player'''
        self.send(Package.PLAYER_DEFEATED, player_id = self.player_id)

    def send_player_disconnected(self):
        '''Send a packet when the player exit from the game'''
        self.send(Package.PLAYER_LEFT, player_id = self.player_id)

    def handle_received_packet(self, type, data):
        '''Handle the data received from the server'''
        if type == Package.HANDSHAKE:
            self.player_id = int(data["player_id"])
            print("Sono il player", self.player_id)
            self.controller.player_id = self.player_id
        elif type == Package.WAIT_FOR_GAME:
            self.wait_for_game(int(data["number_of_players"]))
        elif type == Package.GAME_START:
            self.start_game()
        elif type == Package.GAME_STATE:
            self.receive_game_state(int(data["p_id"]), data["grid"], data["current_piece"], data["player_name"])
        elif type == Package.ROW_RECEIVED:
            self.receive_broken_row(data["player_name"])
        elif type == Package.PLAYER_DEFEATED:
            self.receive_defeat(int(data["p_id"]), data["player_name"])
        elif type == Package.GAME_OVER:
            self.receive_game_over(int(data["winner_id"]), data["winner_name"])

    def start_game(self):
        '''Start the game'''
        self.controller.searching=False

    def receive_game_state(self, player_id, grid, current_piece, player_name):
        '''Receive the game state of a player'''
        self.controller.receive_game_state(player_id, grid, current_piece, player_name)

    def receive_broken_row(self, player_name):
        '''Receive a broken row'''
        self.controller.receive_broken_line(player_name)

    def receive_defeat(self, player_id, player_name):
        '''Receive the defeat of a player'''
        self.controller.receive_defeat(player_id, player_name)

    def receive_game_over(self, winner_id, winner_name):
        '''Receive the game over'''
        self.controller.receive_game_over(winner_id, winner_name)

    def wait_for_game(self, number_of_players):
        '''Wait for a game to start'''
        self.controller.players_in_lobby = number_of_players

    def send(self, packet_type, **kwargs):
        '''Send a packet to the server'''
        packet = Package.encode(packet_type, **kwargs)
        self.client_socket.sendto(packet, self.active_server_addr)