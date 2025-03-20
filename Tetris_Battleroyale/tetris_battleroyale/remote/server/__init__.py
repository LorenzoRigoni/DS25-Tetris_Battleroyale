import threading
from server_game_manager import ServerGameManager

if __name__ == "__server__":
    server = ServerGameManager("127.0.0.1", 12345, 10, 10, 2)
    threading.Thread(target=server.handle_client, daemon=True).start()