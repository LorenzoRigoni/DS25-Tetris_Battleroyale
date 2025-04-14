import threading
from client import Client
from package import Package

class ClientGameManager(Client):
    '''Manage the game functions of the users'''

    def __init__(self, player_name, controller, ip, port):
        Client.__init__(self, ip, port, player_name)
        self.controller = controller
        self.player_name = player_name
        self.send(Package.SHAKE_HAND)

    def receive(self):
        '''Receive a packet from the server'''
        while self.running:
            try:
                package, _ = self.socket.recvfrom(1024)
                data = Package.decode(package)
                self.handle_data(data)
            except Exception as e:
                print(f"Client error: {e}")

    def start_listening(self):
        '''Start the thread for listening'''
        threading.Thread(target=self.receive, daemon=True).start()    

    def handle_data(self, data):
        '''Handle the data received from the server'''
        packet_type = data.get("type")

        if packet_type == Package.SHAKE_HAND:
            self.shake_hand(int(data["player_id"]))
        if packet_type == Package.UPDATE_STATE:
            self.receive_game_state(data["grid_state"], int(data["player_id"]), data["player_name"], data["current_piece"])
        elif packet_type == Package.ROW_RECEIVED:
            self.receive_broken_row(data["from_player"], data["row"])
        elif packet_type == Package.PLAYER_DEFEATED:
            self.receive_defeat(int(data["player_id"]), data["player_name"])
        elif packet_type == Package.GAME_OVER:
            self.receive_game_over(data["winner"])
        elif packet_type == Package.GET_LOBBIES:
            self.receive_lobbies(data["lobbies_info"])
        elif packet_type == Package.JOIN_LOBBY:
            self.receive_confirm_join_lobby()
        elif packet_type == Package.PLAYER_JOINED:
            self.receive_player_joined_lobby(data["player_name"])
        elif packet_type == Package.LEAVE_LOBBY:
            self.receive_confirm_leave_lobby()
        elif packet_type == Package.PLAYER_LEFT:
            self.receive_player_left_lobby(data["player_name"])
        elif packet_type == Package.GAME_COUNTDOWN:
            self.receive_game_countdown()
        elif packet_type == Package.GAME_START:
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