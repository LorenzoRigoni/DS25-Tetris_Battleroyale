# model.py

import random
from vars import *

class TetrisModel:
    def __init__(self, controller,player_number=10):
        # Initialize the game grid and the current and next pieces
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.hold_piece = None  # Pezzo in hold
        self.can_hold = True  # Flag per controllare se il pezzo può essere messo in hold
        self.controller = controller  # Reference to the controller
        self.player_number = player_number  # Player number (for multiplayer)

    def new_piece(self):
        # Define the shapes of the Tetris pieces
        shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1], [1, 1]],  # O
            [[1, 1, 0], [0, 1, 1]],  # S
            [[0, 1, 1], [1, 1, 0]],  # Z
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]]   # J
        ]
        # Choose a random shape and color for the new piece
        shape = random.choice(shapes)
        color = COLORS[shapes.index(shape)]  # Picks the color associated with the shape
        return {'shape': shape, 'color': color, 'x': COLS // 2 - len(shape[0]) // 2, 'y': 0}

    def move_piece(self, dx, dy):
        # Move the piece by dx and dy, and check for collisions
        self.current_piece['x'] += dx
        self.current_piece['y'] += dy
        if self.check_collision():
            # If there is a collision, revert the move
            self.current_piece['x'] -= dx
            self.current_piece['y'] -= dy
            return False
        return True

    def rotate_piece(self):
        # Rotate the current piece
        piece = self.current_piece
        shape = piece['shape']
        new_shape = [list(row) for row in zip(*shape[::-1])]  # Rotate the shape
        old_shape = piece['shape']

        # Try to rotate the piece
        piece['shape'] = new_shape

        # If there is a collision, try to move the piece laterally
        if self.check_collision():
            for dx in [-1, 1, -2, 2, -3, 3]:  # Try different lateral positions
                piece['x'] += dx
                if not self.check_collision():
                    return
            # If no valid position is found, revert the rotation
            piece['shape'] = old_shape

    def check_collision(self, piece=None):
        # Check if the current piece collides with the grid boundaries or other pieces
        if piece is None:
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
        # Lock the current piece in place and spawn a new piece
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + y][piece['x'] + x] = piece['color']
        
        # Spawn a new piece
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True  # Reset the hold flag

        # Check if the new piece collides immediately (game over condition)
        if self.check_collision():
            return True  # Game over
        return False  # Game continues

    def clear_lines(self):
        # Clear any full lines and return the number of lines cleared
        lines_to_clear = [y for y in range(ROWS) if all(self.grid[y])]
        if len(lines_to_clear) == 4:
            self.controller.send_broken_row(self.player_number)  # Send the broken row to the server
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(COLS)])
        return len(lines_to_clear)

    def get_ghost_piece(self):
        # Create a copy of the current piece
        ghost_piece = {
            'shape': self.current_piece['shape'],
            'color': self.current_piece['color'],
            'x': self.current_piece['x'],
            'y': self.current_piece['y']
        }

        # Move the ghost piece down until it collides
        while not self.check_collision(ghost_piece):
            ghost_piece['y'] += 1
        ghost_piece['y'] -= 1  # Move back to the last valid position

        return ghost_piece

    def hold_current_piece(self):
        # Metodo per mettere il pezzo corrente in hold
        if self.can_hold:
            if self.hold_piece is None:
                self.hold_piece = self.current_piece
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
            else:
                # Scambia il pezzo corrente con quello in hold
                self.current_piece, self.hold_piece = self.hold_piece, self.current_piece
            self.can_hold = False  # Imposta il flag a False per evitare di mettere in hold più di una volta

    def drop_piece_to_bottom(self):
        # Move the piece down until it collides
        while self.move_piece(0, 1):
            pass
        self.lock_piece()
        lines_cleared = self.clear_lines()
        if lines_cleared:
            print(f"Lines cleared: {lines_cleared}")

    def rotate_piece_intelligently(self):
        # Try to rotate the piece and handle collisions
        self.rotate_piece()
        if self.check_collision():
            # If there is a collision, try to move the piece left
            self.move_piece(-1, 0)
            if self.check_collision():
                # If still colliding, try to move the piece right
                self.move_piece(2, 0)
                if self.check_collision():
                    # If still colliding, revert everything
                    self.move_piece(-1, 0)
                    self.rotate_piece()  # Revert the rotation

    def check_collision_with_gray_line(self):
        # Check if the current piece collides with the new gray line
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x
                    new_y = piece['y'] + y
                    if new_y >= ROWS - 1:  # Check if the piece is on the new gray line
                        return True
        return False

    def add_gray_line_with_hole(self):
        # Add a gray line with one random hole at the bottom and shift everything up
        gray_color = (128, 128, 128)  # Gray color

        # Shift all rows up by one
        for y in range(1, ROWS):
            self.grid[y - 1] = self.grid[y]
        
        # Create a new line with one random hole
        new_line = [gray_color for _ in range(COLS)]  # Fill the line with gray blocks
        hole_index = random.randint(0, COLS - 1)  # Randomly choose an index for the hole
        new_line[hole_index] = 0  # Set the hole (0 means empty)

        # Add the new line at the bottom
        self.grid[ROWS - 1] = new_line

        # Check if the current piece is affected and move it up if necessary
        if self.check_collision_with_gray_line():
            self.current_piece['y'] -= 1  # Move the current piece up