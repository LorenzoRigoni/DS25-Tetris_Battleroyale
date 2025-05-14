import socket
import threading
import time
import traceback
from remote.package import Package
from remote.game_room import GameRoom
from remote.server_state import ServerState

class Server:
    def __init__(self, host, port, first_start, sock):
        self.host = host
        self.port = port
        self.ping_addr = ("127.0.0.1", 8082)
        self.ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ping_sock.bind(self.ping_addr)

        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))

        self.running = True
        self.last_seen = {}

        self.state = ServerState()
        if not first_start:
            self.state.read_server_state(GameRoom)

        if len(self.state.games) == 0:
            self.state.games.append(GameRoom(self.state.games_id))
            self.state.games_id = 1

    def start(self):
        '''Start the server'''
        threading.Thread(target=self.timeout_monitor, daemon=True).start()
        threading.Thread(target=self.receive_ping_and_heartbeat, daemon=True).start()
        while self.running:
            try:
                data, addr = self.sock.recvfrom(8192)
                p_type, p_data = Package.decode(data)
                self.handle_received_packet(addr, p_type, p_data)
            except ConnectionResetError as e:
                print("Si è disconnesso ", addr)
                if addr in self.state.addr_and_player:
                    self.handle_disconnection(self.state.addr_and_player[addr])
                continue
            except OSError as e:
                if e.winerror == 10054:
                    print("Warning: remote host disconnected")
                    continue
            except Exception as e:
                print(f"Error receiving a packet on the server: {e}")
                traceback.print_exc()
                continue

    def timeout_monitor(self):
        '''Check if all the clients are still connected'''
        while self.running:
            time.sleep(2)
            current_time = time.time()
            for id, p_time in list(self.last_seen.items()):
                if current_time - p_time > 5 and id in self.state.player_and_addr:
                    self.handle_disconnection(id)
    
    def receive_ping_and_heartbeat(self):
        '''Receive the client ping and heartbeat messages'''
        while self.running:
            try:
                data, addr = self.ping_sock.recvfrom(8192)
                p_type, p_data = Package.decode(data)
                if p_type == Package.HEARTBEAT:
                    self.last_seen[int(p_data["player_id"])] = time.time()
                    self.ping_sock.sendto(Package.encode(Package.HEARTBEAT), addr)
            except Exception as e:
                print("Error in reciving ping: ", e)

    def handle_received_packet(self, addr, p_type, p_data):
        '''Handle the client requests'''
        if p_type == Package.HANDSHAKE:
            self.hand_shake(addr, p_data["player_name"])
        elif p_type == Package.START_SEARCH:
            self.start_game_search(int(p_data["player_id"]), self.check_availables_games())
        elif p_type == Package.GAME_STATE:
            self.send_game_state(int(p_data["player_id"]), p_data["grid"], p_data["current_piece"])
        elif p_type == Package.SEND_ROW:
            self.send_broken_row(int(p_data["player_id"]))
        elif p_type == Package.PLAYER_DEFEATED:
            self.handle_defeat(int(p_data["player_id"]))
        elif p_type == Package.PLAYER_LEFT:
            print(f"Player {p_data['player_id']} left the game")
            self.handle_disconnection(int(p_data["player_id"]))

    def hand_shake(self, addr, player_name):
        '''When client connects to the server for the first time, the server sends the id of the player associated to the client.'''
        actual_counter = self.state.player_id_counter
        self.state.player_id_counter += 1
        self.state.player_and_addr[actual_counter] = addr
        self.state.addr_and_player[addr] = actual_counter
        self.state.player_and_name[actual_counter] = player_name
        self.state.player_and_game[actual_counter] = self.check_availables_games()
        print("Player ", actual_counter, " connesso da ", addr)
        self.state.save_locally()
        self.send_message(Package.HANDSHAKE, addr, player_id = actual_counter)
        self.start_game_search(actual_counter, self.state.player_and_game[actual_counter])

    def start_game_search(self, player_id, game_id):
        '''Start the search of a game'''
        if len(self.state.games) == 0 or game_id == -1:
            game_id = self.state.games_id
            self.state.games.append(GameRoom(game_id))
            self.state.games_id += 1
            self.state.player_and_game[player_id] = game_id

        print(f"Player {player_id} is waiting for a game",self.state.player_and_game[player_id])
        if self.state.games[game_id].add_player(player_id):
            self.state.games[game_id].change_room_availability()
            self.send_broadcast_message(game_id, None, Package.GAME_START)
        else:
            #send number of players to all
            self.send_broadcast_message(game_id, None, Package.WAIT_FOR_GAME, number_of_players = self.state.games[game_id].get_num_of_players())

        self.state.save_locally()

    def check_availables_games(self):
        '''Check if there is a not full game. 
        Return -1 if all the games are full, otherwise the id of the first game not full'''
        for game in self.state.games:
            if game.is_room_available():
                return game.game_id
        return -1

    def send_game_state(self, player_id, grid, current_piece):
        '''Send the game state of a player to all others players of the game'''
        if player_id in self.state.player_and_game and player_id in self.state.player_and_name:
            self.send_broadcast_message(self.state.player_and_game[player_id], 
                                        player_id, 
                                        Package.GAME_STATE, 
                                        p_id = player_id,
                                        grid = grid, 
                                        current_piece = current_piece,
                                        player_name = self.state.player_and_name[player_id])

    def send_broken_row(self, player_id):
        '''Send the broken row to all the players of the game'''
        if player_id in self.state.player_and_game and player_id in self.state.player_and_name:
            self.send_broadcast_message(self.state.player_and_game[player_id], player_id, Package.ROW_RECEIVED, player_name = self.state.player_and_name[player_id])

    def handle_defeat(self, player_id):
        '''Handle the defeat of a player and checks if the game is over'''
        self.send_broadcast_message(self.state.player_and_game[player_id], player_id, Package.PLAYER_DEFEATED, p_id = player_id, player_name = self.state.player_and_name[player_id])
        self.state.games[self.state.player_and_game[player_id]].remove_player(player_id)
        if self.state.games[self.state.player_and_game[player_id]].is_game_over():
            winner = self.state.games[self.state.player_and_game[player_id]].get_winner_id()
            self.send_broadcast_message(
                self.state.player_and_game[player_id],
                player_id,
                Package.GAME_OVER,
                winner_id = winner,
                winner_name = self.state.player_and_name[winner]
            )
            
            finished_game_id = self.state.player_and_game[player_id]
            for p_id, game_id in list(self.state.player_and_game.items()):
                if game_id == finished_game_id:
                    del self.state.player_and_game[p_id]

        self.state.save_locally()

    def handle_disconnection(self, player_id):
        '''Handle the disconnection of a player'''
        print(f"Player {player_id} disconnected => {self.state.player_and_addr[player_id]}")
        if player_id in self.state.player_and_game:
            self.handle_defeat(player_id)
        
        del self.last_seen[player_id]
        del self.state.player_and_addr[player_id]
        del self.state.player_and_name[player_id]
        for addr, p_id in list(self.state.addr_and_player.items()):
            if p_id == player_id:
                del self.state.addr_and_player[addr]
                break
        self.state.save_locally()

    def send_message(self, packet_type, addr, **kwargs):
        '''Send a message to a specific client'''
        packet = Package.encode(packet_type, **kwargs)
        self.sock.sendto(packet, addr)

    def send_broadcast_message(self, game_id, player_id, packet_type, **kwargs):
        '''Send a message to all the players of a game'''
        if player_id != None:
            opponents = [addr for p_id, addr in self.state.player_and_addr.items() if p_id != player_id and self.state.player_and_game[p_id] == game_id]
        else:
           opponents = [addr for p_id, addr in self.state.player_and_addr.items() if self.state.player_and_game[p_id] == game_id]
        for addr in opponents:
            self.send_message(packet_type, addr, **kwargs)