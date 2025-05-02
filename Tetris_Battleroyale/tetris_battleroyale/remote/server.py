import socket
import threading
import time
from utils.package import Package
from remote.game_room import GameRoom
import traceback

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.last_seen = {}
        self.player_and_addr = {}
        self.addr_and_player = {}
        self.player_and_name = {}

        self.player_id_counter = 0
        self.games_id = 0
        self.games: list[GameRoom] = []
        #create first game
        self.games.append(GameRoom(self.games_id))
        self.player_and_game: dict[int, int] = {}
        
        threading.Thread(target=self.timeout_monitor, daemon=True).start()

    def start(self):
        '''Start the server'''
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                p_type, p_data = Package.decode(data)
                self.handle_received_packet(addr, p_type, p_data)
            except ConnectionResetError as e:
                print("Error from ", addr, " ", e)
                if addr in self.addr_and_player:
                    self.handle_disconnection(self.addr_and_player[addr])
                continue
            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")
                traceback.print_exc()
                continue

    def timeout_monitor(self):
        '''Check if all the clients are still connected'''
        while True:
            time.sleep(2)
            current_time = time.time()
            for addr, p_time in list(self.last_seen.items()):
                if current_time - p_time > 5:
                    self.handle_disconnection(self.addr_and_player[addr])

    def handle_received_packet(self, addr, p_type, p_data):
        #print(f"Received packet of type {p_type} from {addr}")
        '''Handle the client requests'''
        if p_type == Package.HAND_SHAKE:
            self.hand_shake(addr, p_data["player_name"])
        elif p_type == Package.HEARTBEAT:
            self.last_seen[addr] = time.time()
        elif p_type == Package.START_SEARCH:
            self.start_game_search(int(p_data["player_id"]))
        elif p_type == Package.GAME_STATE:
            self.send_game_state(int(p_data["player_id"]), p_data["grid"], p_data["current_piece"])
        elif p_type == Package.SEND_ROW:
            self.send_broken_row(int(p_data["player_id"]))
        elif p_type == Package.PLAYER_DEFEATED:
            self.handle_defeat(int(p_data["player_id"]))
        elif p_type == Package.PLAYER_LEFT:
            self.handle_disconnection(int(p_data["player_id"]))

    def hand_shake(self, addr, player_name):
        '''When client connects to the server for the first time, the server sends the id of the player associated to the client.'''
        actual_counter = self.player_id_counter
        self.player_id_counter += 1
        self.player_and_addr[actual_counter] = addr
        self.addr_and_player[addr] = actual_counter
        self.player_and_name[actual_counter] = player_name
        self.player_and_game[actual_counter] = self.check_availables_games()
        print(f"Player {actual_counter} connected from {addr} and {self.player_and_game}")
        self.send_message(Package.HAND_SHAKE, addr, player_id = actual_counter)
        self.start_game_search(actual_counter,self.player_and_game[actual_counter])

    def start_game_search(self, player_id,game_id):
        '''Start the search of a game'''
        if len(self.games) == 0 or game_id == -1:
            game_id = self.games_id
            self.games.append(GameRoom(self.games_id))
            self.games_id += 1

        print(f"Player {player_id} is waiting for a game",self.player_and_game[player_id])
        if self.games[game_id].add_player(player_id):
            self.send_broadcast_message(game_id, None, Package.GAME_START)
            self.games[game_id].change_room_availability()
        else:
            #send number of players to all
            self.send_broadcast_message(game_id, None, Package.WAIT_FOR_GAME, number_of_players = self.games[game_id].get_num_of_players())

    def check_availables_games(self):
        '''Check if there is a not full game. 
        Return -1 if all the games are full, otherwise the id of the first game not full'''
        for game in self.games:
            if game.is_room_available():
                return game.get_game_id()
            
        return -1
    
    def send_game_state(self, player_id, grid, current_piece):
        '''Send the game state of a player to all others players of the game'''
        self.send_broadcast_message(self.player_and_game[player_id], player_id, Package.GAME_STATE, p_id = player_id, grid = grid, current_piece = current_piece, player_name = self.player_and_game[player_id])

    def send_broken_row(self, player_id):
        '''Send the broken row to all the players of the game'''
        print("mando")
        self.send_broadcast_message(self.player_and_game[player_id], player_id, Package.ROW_RECEIVED, player_name = self.player_and_name[player_id])

    def handle_defeat(self, player_id):
        '''Handle the defeat of a player and checks if the game is over'''
        self.send_broadcast_message(self.player_and_game[player_id], player_id, Package.PLAYER_DEFEATED, p_id = player_id, player_name = self.player_and_name[player_id])
        if self.games[self.player_and_game[player_id]].is_game_over(player_id):
            winner = self.games[self.player_and_game[player_id]].get_winner_id()
            self.send_broadcast_message(
                self.player_and_game[player_id],
                player_id,
                Package.GAME_OVER,
                winner_id = winner,
                winner_name = self.player_and_name[winner]
            )
            
            finished_game_id = self.player_and_game[player_id]
            self.games.remove(self.games[finished_game_id])
            for p_id, game_id in list(self.player_and_game.items()):
                if game_id == finished_game_id:
                    del self.player_and_game[p_id]

    def handle_disconnection(self, player_id):
        '''Handle the disconnection of a player'''
        print(f"Player {player_id} disconnected => {self.player_and_addr[player_id]}")
        if player_id in self.player_and_game:
            self.handle_defeat(player_id)
        
        del self.last_seen[self.player_and_addr[player_id]]
        del self.player_and_addr[player_id]
        del self.player_and_name[player_id]
        for addr, p_id in list(self.addr_and_player.items()):
            if p_id == player_id:
                del self.addr_and_player[addr]
                break

    def send_message(self, packet_type, addr, **kwargs):
        '''Send a message to a specific client'''
        packet = Package.encode(packet_type, **kwargs)
        self.sock.sendto(packet, addr)

    def send_broadcast_message(self, game_id, player_id, packet_type, **kwargs):
        '''Send a message to all the players of a game'''
        if player_id != None:
            opponents = [addr for p_id, addr in self.player_and_addr.items() if p_id != player_id and self.player_and_game[p_id] == game_id]
        else:
           opponents = [addr for p_id, addr in self.player_and_addr.items() if self.player_and_game[p_id] == game_id]
        for addr in opponents:
            self.send_message(packet_type, addr, **kwargs)