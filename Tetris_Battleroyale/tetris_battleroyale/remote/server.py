import socket
import threading
import time
from utils.package import Package
from remote.game_manager import GameManager
import traceback
class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 10000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.last_seen = {}
        self.player_and_addr = {}
        self.addr_and_player = {}

        self.player_id_counter = 0
        self.games_id = 0
        self.games: list[GameManager] = []
        self.player_and_game: dict[int, int] = {}
        
        threading.Thread(target=self.timeout_monitor, daemon=True).start()

    def start(self):
        '''Start the server'''
        while True:
            try:
                data, addr = self.socket.recvfrom(10240)
                p_type, p_data = Package.decode(data)
                self.handle_received_packet(addr, p_type, p_data)
            except Exception as e:
                print(f"Error in the receivment of a packet on the server: {e}")
                print(self.player_and_game)
                traceback.print_exc()

    def timeout_monitor(self):
        '''Check if all the clients are still connected'''
        while True:
            time.sleep(2)
            current_time = time.time()
            for addr, p_time in list(self.last_seen.items()):
                if current_time - p_time > 5:
                    self.handle_disconnection(self.addr_and_player[addr])

    def handle_received_packet(self, addr, p_type, p_data):
        print(f"Received packet of type {p_type} from {addr}")
        '''Handle the client requests'''
        if p_type == Package.HAND_SHAKE:
            self.hand_shake(addr)
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

    def hand_shake(self, addr):
        '''When client connects to the server for the first time, the server sends the id of the player associated to the client.'''
        actual_counter = self.player_id_counter
        self.player_id_counter += 1
        self.player_and_addr[actual_counter] = addr
        self.addr_and_player[addr] = actual_counter
        self.player_and_game[actual_counter] = self.check_availables_games()
        self.send_message(Package.HAND_SHAKE, addr, player_id = actual_counter)

    def start_game_search(self, player_id):
        '''Start the search of a game'''
        game_id = self.check_availables_games()
        if len(self.games) == 0 or game_id == -1:
            self.games.append(GameManager(self.games_id))
            game_id = self.games_id
            self.games_id += 1

        self.player_and_game[player_id] = game_id
        self.send_message(Package.WAIT_FOR_GAME, self.player_and_addr[player_id])
        if self.games[game_id].add_player_to_game(player_id):
            self.send_broadcast_message(game_id, None, Package.GAME_COUNTDOWN)
            time.sleep(5)
            self.send_broadcast_message(game_id, None, Package.GAME_START)

    def check_availables_games(self):
        '''Check if there is a not full game. 
        Return -1 if all the games are full, otherwise the id of the first game not full'''
        for game in self.games:
            if not game.is_game_full():
                return game.get_game_id()
            
        return -1
    
    def send_game_state(self, player_id, grid, current_piece):
        '''Send the game state of a player to all others players of the game'''
        self.send_broadcast_message(self.player_and_game[player_id], None, Package.GAME_STATE, grid = grid, current_piece = current_piece, sender= player_id)

    def send_broken_row(self, player_id):
        '''Send the broken row of a player to all others'''
        self.send_broadcast_message(self.player_and_game[player_id], player_id, Package.ROW_RECEIVED)

    def handle_defeat(self, player_id):
        '''Handle the defeat of a player and checks if the game is over'''
        self.send_broadcast_message(self.player_and_game[player_id],player_id,Package.PLAYER_DEFEATED)
        if self.games[self.player_and_game[player_id]].is_game_over(player_id):
            winner = self.games[self.player_and_game[player_id]].get_winner_id()
            self.send_broadcast_message(
                self.player_and_game[player_id],
                player_id,
                Package.GAME_OVER,
                winner=winner  # Only winner is passed as a keyword arg
            )
            
            finished_game_id = self.player_and_game[player_id]
            self.games.remove(self.games[finished_game_id])
            for p_id, game_id in list(self.player_and_game.items()):
                if game_id == finished_game_id:
                    del self.player_and_game[p_id]

    def handle_disconnection(self, player_id):
        '''Handle the dicconction of a player'''
        if player_id in self.player_and_game:
            self.handle_defeat(player_id)
            del self.player_and_game[player_id]
        
        del self.last_seen[self.player_and_addr[player_id]]
        del self.player_and_addr[player_id]
        for addr, p_id in list(self.addr_and_player.items()):
            if p_id == player_id:
                del self.addr_and_player[addr]
                break

    def send_message(self, packet_type, addr, **kwargs):
        '''Send a message to a specific client'''
        packet = Package.encode(packet_type, **kwargs)
        self.socket.sendto(packet, addr)

    def send_broadcast_message(self, game_id, player_id, packet_type, **kwargs):
        '''Send a message to all the players of a game'''
        if player_id != None:
            opponents = [addr for p_id, addr in self.player_and_addr.items() if p_id != player_id and self.player_and_game[p_id] == game_id]
        else:
           opponents = [addr for p_id, addr in self.player_and_addr.items() if self.player_and_game[p_id] == game_id]
        print(f"Sending message to {len(opponents)} players")
        for addr in opponents:
            self.send_message(packet_type, addr, **kwargs)