from client import Client
from client_game_manager import ClientGameManager

if __name__ == "__client__":
    client = Client("127.0.0.1", 12345)
    client_game_manager = ClientGameManager(client, 0, "")
    client.start_listening()