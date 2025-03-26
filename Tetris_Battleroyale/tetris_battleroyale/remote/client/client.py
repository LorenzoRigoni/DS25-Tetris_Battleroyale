import socket
import threading
from package import Package

class Client:
    '''Manage the communication of the client (only non-game aspects)'''

    def __init__(self, server_ip, server_port,controller,ip, port):
        self.ip=ip
        self.port=port
        self.controller = controller
        self.server_addr = (server_ip, server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

    def send(self, packet_type, **kwargs):
        '''Send a packet to the server'''
        data = Package.encode(packet_type, **kwargs)
        self.socket.sendto(data, self.server_addr)

    def receive(self):
        '''Receive a packet from the server'''
        while self.running:
            try:
                package, _ = self.socket.recvfrom(1024)
                data = Package.decode(package)
                self.handle_packet(data)
            except Exception as e:
                print(f"Client error: {e}")

    def handle_data(self, data):
        '''Handle the packet received from the server (only no-game aspects)'''
        packet_type = data.get("type")

        if packet_type == Package.GET_LOBBIES:
            pass
        elif packet_type == Package.JOIN_LOBBY:
            pass
        elif packet_type == Package.PLAYER_JOINED:
            pass
        elif packet_type == Package.LEAVE_LOBBY:
            pass
        elif packet_type == Package.PLAYER_LEFT:
            pass
        elif packet_type == Package.GAME_COUNTDOWN:
            pass
        elif packet_type == Package.GAME_START:
            self.controller.run()
            pass

    def start_listening(self):
        '''Start the thread for listening'''
        threading.Thread(target=self.receive, daemon=True).start()

    def get_available_lobbies(self):
        '''Request the available lobbies'''
        self.send(Package.GET_LOBBIES)

    def join_lobby(self, lobby_id):
        '''Try to enter in a lobby'''
        self.send(Package.JOIN_LOBBY, player_id = self.player_id, player_name = self.player_name, lobby_id = lobby_id)

    def close_connection(self):
        '''Close the client connection'''
        self.running = False
        self.socket.close()