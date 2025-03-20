from client import Client
from client_game_manager import ClientGameManager

if __name__ == "__client__":
    client = Client("127.0.0.1", 12345)
    client.start_listening()