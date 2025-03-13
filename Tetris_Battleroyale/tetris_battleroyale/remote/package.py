import msgpack

class Package:
    """Manage the content and the delivery of packages"""
    
    GET_LOBBIES = "get_lobbies"
    LOBBY_LIST = "lobby_list"
    JOIN_LOBBY = "join_lobby"
    JOINED_LOBBY = "joined_lobby"
    LEAVE_LOBBY = "leave_lobby"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_COUNTDOWN = "game_countdown"
    GAME_START = "game_start"
    SEND_ROW = "send_row"
    ROW_RECEIVED = "row_received"
    UPDATE_STATE = "update_state"
    PLAYER_DEFEATED = "player_defeated"
    GAME_OVER = "game_over"
    ERROR = "error"

    @staticmethod
    def encode(packet_type, **kwargs):
        """Create the package"""
        packet = {"type": packet_type, **kwargs}
        return msgpack.packb(packet)

    @staticmethod
    def decode(data):
        """Decode the recived package"""
        return msgpack.unpackb(data)