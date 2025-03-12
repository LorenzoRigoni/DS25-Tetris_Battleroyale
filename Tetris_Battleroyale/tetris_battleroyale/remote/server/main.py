import socket
import threading
import time
import json

class Server:
    def __init__(self, host = "127.0.0.1", port = 5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.clients_names = {}
        self.opponents = {}
        self.lobbys = {}
        self.waiting_for_start = None
    
    def handle_connect(self, client):
        pass

    def handle_disconnect(self, client):
        pass

    def create_lobby(self, client):
        pass

    def get_client_data(self, client):
        pass

    def wait_for_start(self, client):
        pass

    def handle(self, client):
        pass

    def handle_receive(self, client):
        pass

    def send(self, res_type, client, data):
        pass

    def send_to_opponent(self, res_type, client, data):
        pass

    def receive(self):
        pass