import threading
from game_manager import GameManager

if __name__ == "__server__":
    server = GameManager("127.0.0.1", 12345, 10, 10, 2)
    threading.Thread(target=server.handle_client, daemon=True).start()