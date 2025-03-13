import socket
import time
import msgpack

class Server:
    def __init__(self, host, port, num_max_lobbies, num_max_players_per_lobby, num_min_players_per_lobby):
        self.host = host
        self.port = port
        self.num_max_lobbies = num_max_lobbies
        self.num_max_players_per_lobby = num_max_players_per_lobby
        self.num_min_players_per_lobby = num_min_players_per_lobby

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        lobbies = {f"lobby_{i+1}": {"players": {}, "state": {}, "in_game": False} for i in range(self.num_max_lobbies)}

    def handle_client(self):
        '''Handle the client requests'''
        while True:
            data, addr = self.sock.recvfrom(1024)
            packet = msgpack.unpackb(data)
            packet_type = packet.get("type")

            if packet_type == "get_lobbies":
                pass
            if packet_type == "join_lobby":
                pass
            if packet_type == "leave_lobby":
                pass
            if packet_type == "send_row":
                pass
            elif packet_type == "update_game_state":
                pass

            except Exception as e:
            print(f"Error in the receivment of a packet on the server: {e}")

    def send_available_lobbies(self, addr):
        '''Send to the client the available lobbies'''
        pass

    def handle_join_lobby(self, packet, addr):
        '''Allow a player to join a lobby'''
        pass

    def handle_leave_lobby(self, packet, addr):
        '''Handle the leaving of a player from the lobby'''
        pass

    def start_game_countdown(self, lobby_id):
        '''Activate a 5 second countdown when a lobby is started'''
        pass

    def handle_send_row(self, packet):
        '''Send a broken row to all (or to a specific one) oppents'''
        pass

    def handle_game_state(self, packet):
        '''Syncronize the game state'''
        pass

    def send_message(self, message, addr):
        '''Send a message to a specific client'''
        pass

    def send_broadcast_message(self, lobby_id, message):
        '''Send a message to all the clients of a lobby'''
        pass