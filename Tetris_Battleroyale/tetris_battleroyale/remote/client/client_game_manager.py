from client import Client
from package import Package

class ClientGameManager:
    '''Manage the game functions of the users'''

    def __init__(self, client: Client, player_name):
        self.client = client
        self.player_id = player_id
        self.player_name = player_name
        self.lobbies = {}

    