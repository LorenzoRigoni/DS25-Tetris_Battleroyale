class Package:
    TYPE = "type"
    PLAYERS = "players"
    IN_GAME = "in_game"
    class Type:
        GET_AVAILABLE_LOBBIES = "get_lobbies"
        JOIN_LOBBY = "join_lobby"
        LEAVE_LOBBY = "leave_lobby"
        SEND_ROW = "send_row"
        UPDATE_GAME_STATE = "update_game_state"