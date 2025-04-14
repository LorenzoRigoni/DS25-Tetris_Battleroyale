import socket
from package import Package

class Client:
    '''Manage the communication of the client (only non-game aspects)'''

    def __init__(self, ip, port, player_name):
        self.player_name = player_name
        self.player_id = 0
        self.ip=ip
        self.port=port
        self.server_addr = ("127.0.0.1", 8080)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

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