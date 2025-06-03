import json
import threading
from pathlib import Path
from .game_room import GameRoom

class ServerState:
    '''This class manages and saves the values of the varibales used by the server.'''

    def __init__(self, file_path="server_state.json"):
        self.file_path = Path(file_path)
        self.lock = threading.Lock()

        self.player_and_addr = {}
        self.addr_and_player = {}
        self.player_and_name = {}
        self.player_and_game: dict[int, int] = {}

        self.player_id_counter = 0
        self.games_id = 0
        self.games: list[GameRoom] = []

    def save_locally(self):
        '''Save the server state locally'''
        with self.lock:
            try:
                serializable_dict = {f"{k[0]}::{k[1]}": v for k, v in self.addr_and_player.items()}
                data = {
                    "player_and_addr": self.player_and_addr,
                    "addr_and_player": serializable_dict,
                    "player_and_name": self.player_and_name,
                    "player_and_game": self.player_and_game,
                    "player_id_counter": self.player_id_counter,
                    "games_id": self.games_id,
                    "games": [game.to_dict() for game in self.games]
                }
                with self.file_path.open("w") as file:
                    json.dump(data, file)
            except Exception as e:
                print("Exception on saving the server state: ", e)

    def read_server_state(self, GameRoom):
        '''Read locally the last server state'''
        if not self.file_path.exists():
            return
        
        with self.lock:
            try:
                with self.file_path.open("r") as file:
                    data = json.load(file)
                    self.player_and_addr = {int(k): tuple(v) for k, v in data.get("player_and_addr", {}).items()}
                    row_addr_and_player = data["addr_and_player"]
                    self.addr_and_player = {
                        (k.split("::")[0], int(k.split("::")[1])): v
                        for k, v in row_addr_and_player.items()
                    }
                    self.player_and_name = {int(k): v for k, v in data.get("player_and_name", {}).items()}
                    self.player_and_game = {int(k): int(v) for k, v in data.get("player_and_game", {}).items()}
                    self.player_id_counter = int(data.get("player_id_counter", 0))
                    self.games_id = int(data.get("games_id", 0))
                    self.games = [GameRoom.from_dict(g) for g in data.get("games", [])]
            except Exception as e:
                print("Exception on loading the server state: ", e)