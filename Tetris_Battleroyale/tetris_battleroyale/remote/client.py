import socket
import threading
from utils.package import Package

class Client:
    '''Manage the communication of the client (only non-game aspects)'''

    def __init__(self, player_name, controller):
        self.player_name = player_name
        self.player_id = 0
        self.server_addr = ("127.0.0.1", 12345)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.controller = controller
        self.player_name = player_name
        self.send(Package.SHAKE_HAND)

    def receive(self):
        '''Receive a packet from the server'''
        while self.running:
            try:
                package, _ = self.socket.recvfrom(4096)
                type, data = Package.decode(package)
                self.handle_data(type, data)
            except Exception as e:
                print(f"Client error: {e}")

    def start(self):
        '''Start the thread for listening'''
        threading.Thread(target=self.receive, daemon=True).start()    

    def handle_data(self, type, data):
        '''Handle the data received from the server'''
        if type == Package.SHAKE_HAND:
            self.shake_hand(int(data["player_id"]))
        if type == Package.UPDATE_STATE:
            self.receive_game_state(data["grid_state"], int(data["player_id"]), data["player_name"], data["current_piece"])
        elif type == Package.ROW_RECEIVED:
            self.receive_broken_row(data["from_player"], data["row"])
        elif type == Package.PLAYER_DEFEATED:
            self.receive_defeat(int(data["player_id"]), data["player_name"])
        elif type == Package.GAME_OVER:
            self.receive_game_over(data["winner"])
        elif type == Package.GET_LOBBIES:
            self.receive_lobbies(data["lobbies_info"])
        elif type == Package.JOIN_LOBBY:
            self.receive_confirm_join_lobby()
        elif type == Package.PLAYER_JOINED:
            self.receive_player_joined_lobby(data["player_name"])
        elif type == Package.LEAVE_LOBBY:
            self.receive_confirm_leave_lobby()
        elif type == Package.PLAYER_LEFT:
            self.receive_player_left_lobby(data["player_name"])
        elif type == Package.GAME_COUNTDOWN:
            self.receive_game_countdown()
        elif type == Package.GAME_START:
            self.controller.run()
        
    def send_game_state(self, grid, lobby_id, current_piece):
        '''Send the game state of the user to the server'''
        self.send(Package.UPDATE_STATE, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name, grid_state = grid, current_piece = current_piece)

    def send_broken_row(self, lobby_id, target, row):
        '''Send the broken rows to the server with the information for who is/are the targets'''
        if target != None:
            self.send(Package.SEND_ROW, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name, target = target, row = row)
        else:
            self.send(Package.SEND_ROW, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name, row = row)

    def send_defeat(self, lobby_id):
        '''Send the message to the server that the player has lost the game'''
        self.send(Package.PLAYER_DEFEATED, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name)

    def receive_game_state(self, grid_state, player_id, player_name, current_piece):
        '''Receive the game state of the users from the server'''
        #TODO: implement in controller the method to visualize the other grids
        pass

    def receive_broken_row(self, name_sender, row):
        '''Receive the broken row from the server'''
        #TODO: implement in controller the method to add the broken row to his grid
        pass

    def receive_defeat(self, player_id, player_name):
        '''Receive the message from the server of a player who lost the game'''
        #TODO: implement in controller the method to visualize the message for the player defeated
        pass

    def receive_game_over(self, winner_name):
        '''Receive the name of the winner of the game'''
        #TODO: implement in controller the method to visualize the winner
        pass

    def send(self, packet_type, **kwargs):
        '''Send a packet to the server'''
        data = Package.encode(packet_type, **kwargs)
        self.socket.sendto(data, self.server_addr)

    def shake_hand(self, player_id):
        self.player_id = player_id

    def get_lobbies(self):
        '''Request the lobbies'''
        self.send(Package.GET_LOBBIES)

    def join_lobby(self, lobby_id):
        '''Try to enter in a lobby'''
        self.send(Package.JOIN_LOBBY, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name)

    def receive_lobbies(self, lobbies_info):
        '''Receive the info of the lobbies'''
        #TODO: implement in controller the method to visualize the lobbies
        pass

    def receive_confirm_join_lobby(self):
        '''Receive the message of confirm for join the lobby'''
        #TODO: implement in controller the method to visualize the message
        pass

    def receive_player_joined_lobby(self, player_name):
        '''Receive the message of a player who joined the lobby'''
        #TODO: implement in controller the method to visualize the message

    def receive_confirm_leave_lobby(self):
        '''Receive the message of confirm for leave the lobby'''
        #TODO: implement in controller the method to visualize the message
        pass

    def receive_player_left_lobby(self, player_name):
        '''Receive the message of a player who left the lobby'''
        #TODO: implement in controller the method to visualize the message

    def receive_game_countdown(self):
        '''Receive the message that the game is starting'''
        #TODO: implement in controller the method to visualize the message

    def close_connection(self):
        '''Close the client connection'''
        self.running = False
        self.socket.close()