# model.py

import random
from vars import *

class TetrisModel:
    def __init__(self):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    def new_piece(self):
        shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1], [1, 1]],  # O
            [[1, 1, 0], [0, 1, 1]],  # S
            [[0, 1, 1], [1, 1, 0]],  # Z
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]]   # J
        ]
        shape = random.choice(shapes)
        color = random.choice(COLORS)  # Colore casuale per ogni pezzo
        return {'shape': shape, 'color': color, 'x': COLS // 2 - len(shape[0]) // 2, 'y': 0}

    def move_piece(self, dx, dy):
        self.current_piece['x'] += dx
        self.current_piece['y'] += dy
        if self.check_collision():
            self.current_piece['x'] -= dx
            self.current_piece['y'] -= dy
            return False
        return True

    def rotate_piece(self):
        piece = self.current_piece
        shape = piece['shape']
        new_shape = [list(row) for row in zip(*shape[::-1])]  # Ruota la forma
        old_shape = piece['shape']
        old_x = piece['x']
        old_y = piece['y']

        # Prova a ruotare il pezzo
        piece['shape'] = new_shape
        piece['x'] = old_x - (len(new_shape[0]) - len(old_shape[0])) // 2
        piece['y'] = old_y - (len(new_shape) - len(old_shape)) // 2

        # Se c'è una collisione, prova a spostare il pezzo lateralmente
        if self.check_collision():
            for dx in [-1, 2, -2, 1]:  # Prova a spostare a sinistra, poi a destra
                piece['x'] = old_x + dx
                if not self.check_collision():
                    return
            # Se non funziona, annulla la rotazione
            piece['shape'] = old_shape
            piece['x'] = old_x
            piece['y'] = old_y

    def check_collision(self):
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x
                    new_y = piece['y'] + y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or self.grid[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + y][piece['x'] + x] = piece['color']
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

    def clear_lines(self):
        lines_to_clear = [y for y in range(ROWS) if all(self.grid[y])]
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(COLS)])
        return len(lines_to_clear)