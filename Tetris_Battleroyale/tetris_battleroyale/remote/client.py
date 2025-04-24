import socket
import threading
import time
from utils.package import Package

class Client:
    '''Manage the communication of the client (only non-game aspects)'''

    def __init__(self, player_name, controller):
        self.player_name = player_name
        self.player_id = 0
        self.server_addr = ("127.0.0.1", 5000)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.controller = controller
        self.player_name = player_name

    def send_heartbeat(self):
        while self.running:
            self.send(Package.HEARTBEAT)
            time.sleep(2)

    def start(self):
        '''Starts the client'''
        try:
            self.client_socket.connect(self.server_addr)
        except Exception as e:
            #TODO: controller message if the server is offline
            self.running = False
            self.client_socket.close()
            print("")

        self.send(Package.HAND_SHAKE)
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

        while self.running:
            try:
                package = self.client_socket.recv(1024)
                type, data = Package.decode(package)
                self.handle_received_packet(type, data)
            except Exception as e:
                print(f"Client error: {e}")
                self.running = False

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
        if type == Package.HAND_SHAKE:
            self.player_id = int(data["player_id"])
        elif type == Package.WAIT_FOR_GAME:
            self.wait_for_game()
        elif type == Package.GAME_COUNTDOWN:
            self.start_game_countdown()
        elif type == Package.GAME_START:
            self.start_game()
        elif type == Package.GAME_STATE:
            self.receive_game_state(int(data["player_id"]), data["grid"], data["current_piece"])
        elif type == Package.ROW_RECEIVED:
            self.receive_broken_row()
        elif type == Package.PLAYER_DEFEATED:
            self.receive_defeat(int(data["player_id"]))
        elif type == Package.GAME_OVER:
            self.receive_game_over(int(data["winner"]))

    def wait_for_game(self):
        '''Wait until the game starts'''
        #TODO: method in controller for display the wait screen
        pass

    def start_game_countdown(self):
        '''Start the five seconds countdown'''
        #TODO: method in controller for display the countdown screen
        pass

    def start_game(self):
        '''Start the game after the countdown'''
        #TODO: method in controller for display the game screen
        pass

    def receive_game_state(self, player_id, grid, current_piece):
        '''Receive the game state of a player'''
        #TODO: method in controller for display the players screens
        pass

    def receive_broken_row(self):
        '''Receive a broken row'''
        #TODO: method in controller for add the row
        pass

    def receive_defeat(self, player_id):
        #TODO: method in controller for the defeat of a player
        pass

    def receive_game_over(self, winner_id):
        #TODO: method in controller for game over and display the winner
        pass
    
    def send(self, packet_type, **kwargs):
        '''Send a packet to the server'''
        data = Package.encode(packet_type, **kwargs)
        self.client_socket.send(data)