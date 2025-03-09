# view.py

import pygame
from vars import *

class TetrisView:
    def __init__(self):
        # Initialize the Pygame window and set up the display
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()

    def draw_grid(self, grid):
        # Draw the game grid
        self.screen.fill(BLACK)
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_piece(self, piece):
        # Draw the current piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece['color'], 
                                     ((piece['x'] + x) * BLOCK_SIZE, (piece['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_next_piece(self, next_piece):
        # Ridimensioniamo i blocchi per il prossimo pezzo
        small_block_size = BLOCK_SIZE // 2  # Rendi i blocchi più piccoli
        start_x = COLS * BLOCK_SIZE + 20  # Posizione a destra del campo di gioco
        start_y = 20  # Posizione in alto

        # Disegna il prossimo pezzo
        for y, row in enumerate(next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, next_piece['color'], 
                                     (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

        # Disegna un bordo intorno all'area del prossimo pezzo
        border_rect = pygame.Rect(start_x - 5, start_y - 5, NEXT_PIECE_AREA_WIDTH * small_block_size + 10, NEXT_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)

    def draw_hold_piece(self, hold_piece):
        # Ridimensioniamo i blocchi per il pezzo in hold
        small_block_size = BLOCK_SIZE // 2  # Rendi i blocchi più piccoli
        start_x = COLS * BLOCK_SIZE + 20  # Posizione a destra del campo di gioco
        start_y = 20 + NEXT_PIECE_AREA_HEIGHT * small_block_size + 20  # Posizione sotto il prossimo pezzo

        # Disegna il testo "HOLD" sopra l'area di hold
        font = pygame.font.SysFont(None, 24)
        hold_text = font.render("HOLD", True, WHITE)
        self.screen.blit(hold_text, (start_x, start_y - 20))

        # Disegna un bordo intorno all'area di hold (sempre visibile)
        border_rect = pygame.Rect(start_x - 5, start_y - 5, HOLD_PIECE_AREA_WIDTH * small_block_size + 10, HOLD_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)

        # Disegna il pezzo in hold (se presente)
        if hold_piece:
            for y, row in enumerate(hold_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, hold_piece['color'], 
                                        (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

    def update(self, grid, current_piece, next_piece, hold_piece):
        # Update the display with the current game state
        self.screen.fill(BLACK)
        self.draw_grid(grid)
        self.draw_ghost_piece(current_piece, grid)  # Draw the ghost piece
        self.draw_piece(current_piece)
        self.draw_next_piece(next_piece)
        self.draw_hold_piece(hold_piece)  # Draw the hold piece
        pygame.display.flip()
        self.clock.tick(30)

    def draw_ghost_piece(self, piece, grid):
        # Clone the original piece as a ghost piece
        ghost_piece = {
            'shape': piece['shape'],
            'color': piece['color'],  # Use the same color as the active piece
            'x': piece['x'],
            'y': piece['y']
        }

        # Move the ghost piece down until it collides
        while not self.check_collision(ghost_piece, grid):
            ghost_piece['y'] += 1
        ghost_piece['y'] -= 1  # Move back to the last valid position

        # List to store the edges that need to be drawn
        edges = []
        dash_length = 5  # Length of each dash segment

        for y, row in enumerate(ghost_piece['shape']):
            for x, cell in enumerate(row):
                if cell:  # If this is part of the piece
                    abs_x = ghost_piece['x'] + x
                    abs_y = ghost_piece['y'] + y

                    # Define the four edges of the cell
                    top = ((abs_x * BLOCK_SIZE, abs_y * BLOCK_SIZE), ((abs_x + 1) * BLOCK_SIZE, abs_y * BLOCK_SIZE))
                    bottom = ((abs_x * BLOCK_SIZE, (abs_y + 1) * BLOCK_SIZE), ((abs_x + 1) * BLOCK_SIZE, (abs_y + 1) * BLOCK_SIZE))
                    left = ((abs_x * BLOCK_SIZE, abs_y * BLOCK_SIZE), (abs_x * BLOCK_SIZE, (abs_y + 1) * BLOCK_SIZE))
                    right = (((abs_x + 1) * BLOCK_SIZE, abs_y * BLOCK_SIZE), ((abs_x + 1) * BLOCK_SIZE, (abs_y + 1) * BLOCK_SIZE))

                    # Check if the side is free and add it to the list
                    if y == 0 or not ghost_piece['shape'][y - 1][x]:  # Top edge
                        edges.append(top)
                    if y == len(ghost_piece['shape']) - 1 or not ghost_piece['shape'][y + 1][x]:  # Bottom edge
                        edges.append(bottom)
                    if x == 0 or not ghost_piece['shape'][y][x - 1]:  # Left edge
                        edges.append(left)
                    if x == len(row) - 1 or not ghost_piece['shape'][y][x + 1]:  # Right edge
                        edges.append(right)

        # Function to draw dashed lines
        def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=5):
            x1, y1 = start_pos
            x2, y2 = end_pos
            dx, dy = x2 - x1, y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            dashes = int(distance // (dash_length * 2))
            for i in range(dashes):
                start = (x1 + (dx * (i * 2 * dash_length) / distance), y1 + (dy * (i * 2 * dash_length) / distance))
                end = (x1 + (dx * ((i * 2 + 1) * dash_length) / distance), y1 + (dy * ((i * 2 + 1) * dash_length) / distance))
                pygame.draw.line(surface, color, start, end, 2)

        # Draw the dashed outline of the ghost piece
        for edge in edges:
            draw_dashed_line(self.screen, piece['color'], edge[0], edge[1], dash_length)

    def check_collision(self, piece, grid):
        # Check if the piece collides with the grid boundaries or other pieces
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x
                    new_y = piece['y'] + y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or grid[new_y][new_x]:
                        return True
        return False