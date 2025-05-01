import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.model import TetrisModel
from game.controller import TetrisController

@pytest.fixture
def model():
    '''Create the controller and the model'''
    controller = TetrisController(1)
    return TetrisModel(controller, 1)

def test_move_piece_valid(model: TetrisModel):
    '''Test a valid move'''
    initial_x = model.current_piece['x']
    moved = model.move_piece(1, 0)
    assert moved is True
    assert model.current_piece['x'] == initial_x + 1

def test_move_piece_invalid(model: TetrisModel):
    '''Test an invalid move'''
    model.current_piece['x'] = 9
    moved = model.move_piece(1, 0)
    assert moved is False

def test_drop_piece_to_bottom(model: TetrisModel):
    '''Test the fall of the piece'''
    original_piece = model.current_piece['y']
    model.current_piece['y'] = 9
    start_y = model.current_piece['y']
    model.drop_piece_to_bottom()
    end_y = model.current_piece['y']
    assert start_y > end_y
    model.current_piece['y'] = original_piece

def test_hold_current_piece(model: TetrisModel):
    '''Test the helding of the piece'''
    model.hold_piece = None
    original_piece = model.current_piece.copy()
    model.hold_current_piece()
    assert model.hold_piece is not None
    assert model.hold_piece['shape'] == original_piece['shape']

def test_lock_piece(model: TetrisModel):
    '''Test the lock of the piece'''
    model.current_piece['y'] = len(model.grid) - 2
    model.move_piece(0, 1)
    if not model.move_piece(0, 1):
        game_over = model.lock_piece()
        assert game_over in [True, False]
        assert any(cell != 0 for row in model.grid for cell in row)

def test_clear_lines(model: TetrisModel):
    '''Test the clear of the lines'''
    model.grid[-1] = [1 for _ in range(len(model.grid[0]))]
    lines_cleared = model.clear_lines()
    assert lines_cleared == 1
    assert all(cell == 0 for cell in model.grid[0])