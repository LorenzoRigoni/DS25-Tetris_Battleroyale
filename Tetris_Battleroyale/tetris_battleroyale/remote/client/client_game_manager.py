from client import Client
from package import Package

class ClientGameManager(Client):
    '''Manage the game functions of the users'''

    def __init__(self, player_id, player_name, controller):
        Client.__init__(self, controller.server_ip, controller.server_port, controller)
        self.player_id = player_id
        self.player_name = player_name
        self.lobbies = {}

    def handle_data(self, data):
        '''Handle the data received from the server (only game aspects)'''
        packet_type = data.get("type")

        if packet_type == Package.UPDATE_STATE:
            lobby_id = data["lobby_id"]
            player_id = data["player_id"]
            new_grid = data["grid"]
            new_current_piece = data["current_piece"]
            self.controller.updateEnemies(player_id, new_grid, new_current_piece)
        elif packet_type == Package.SEND_ROW:
            lobby_id = data["lobby_id"]
            player_id = data["player_id"]
            player_name = data["player_name"]
            target = data["target"]
            rows = data["rows"]
            #TODO: call to the method of controller for add the broken rows
        elif packet_type == Package.PLAYER_DEFEATED:
            lobby_id = data["lobby_id"]
            player_id = data["player_id"]
            player_name = data["player_name"]
            #TODO: call to the method of controller for show a message with name of player defeated
        elif packet_type == Package.GAME_OVER:
            lobby_id = data["lobby_id"]
            winner = data["winner"]
            #TODO: call to the method of controller for show a message with name of winner
        

    def send_game_state(self, grid, lobby_id, current_piece):
        '''Send the game state of the user to the server'''
        self.send(Package.UPDATE_STATE, player_id = self.player_id, grid = grid, lobby_id = lobby_id, current_piece = current_piece)

    def send_broken_row(self, rows, lobby_id, target):
        '''Send the broken rows to the server with the information for who is/are the targets'''
        if target != None:
            self.send(Package.SEND_ROW, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name, target = target, rows = rows)
        else:
            self.send(Package.SEND_ROW, lobby_id = lobby_id, player_id = self.player_id, player_name = self.player_name, rows = rows)

    def send_defeat(self, lobby_id):
        '''Send the message to the server of a player who lost the game'''
        self.send(Package.PLAYER_DEFEATED, player_id = self.player_id, player_name = self.player_name, lobby_id = lobby_id)