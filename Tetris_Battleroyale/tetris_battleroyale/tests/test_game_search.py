import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from remote.game_room import GameRoom

@pytest.fixture
def room():
    '''Create the room for tests'''
    room = GameRoom(0)
    return room

def test_add_player_to_room(room: GameRoom):
    '''Test the player joins in the lobby'''
    assert room.can_game_start() is False
    assert room.get_num_of_players() == 0
    assert room.add_player(0) is False
    assert room.get_num_of_players() == 1

def test_remove_player_from_room(room: GameRoom):
    '''Test the player leaves the lobby'''
    assert room.add_player(0) is False
    room.remove_player(0)
    assert room.get_num_of_players() == 0

def test_is_room_ready_for_game(room: GameRoom):
    '''Test the room is ready to start the game'''
    assert room.add_player(0) is False
    assert room.add_player(1) is False
    assert room.add_player(2) is False
    assert room.add_player(3) is False
    assert room.add_player(4) is True

def test_start_game(room: GameRoom):
    '''Test the room is not available anymore'''
    room.change_room_availability()
    assert room.is_room_available() is False

def test_is_game_over(room: GameRoom):
    '''Test the game is over'''
    assert room.add_player(0) is False
    assert room.add_player(1) is False
    assert room.add_player(2) is False
    assert room.add_player(3) is False
    assert room.add_player(4) is True
    room.remove_player(0)
    room.remove_player(1)
    room.remove_player(2)
    room.remove_player(3)
    assert room.is_game_over() is True