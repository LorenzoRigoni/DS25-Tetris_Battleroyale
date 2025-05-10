from bson import BSON

class Package:
    """Manage the content and the delivery of packages"""
    
    HAND_SHAKE = "hand_shake"
    PING = "ping"
    BACKUP_READY = "backup_ready"
    PRIMARY_HEARTBEAT = "primary_heartbeat"
    HEARTBEAT = "heartbeat"
    START_SEARCH = "start_search"
    WAIT_FOR_GAME = "wait_for_game"
    PLAYER_LEFT = "player_left"
    GAME_COUNTDOWN = "game_countdown"
    GAME_START = "game_start"
    SEND_ROW = "send_row"
    ROW_RECEIVED = "row_received"
    GAME_STATE = "update_state"
    PLAYER_DEFEATED = "player_defeated"
    GAME_OVER = "game_over"
    ERROR = "error"

    @staticmethod
    def encode(packet_type, **kwargs):
        """Create the package"""
        packet = {"type": packet_type, "data": kwargs}
        return BSON.encode(packet)

    @staticmethod
    def decode(data):
        """Decode the recived package"""
        packet = BSON(data).decode()
        return packet["type"], packet["data"]