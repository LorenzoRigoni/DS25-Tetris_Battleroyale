# view.py

import pygame
from vars import *

class TetrisView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()

    def draw_grid(self, grid):
        self.screen.fill(BLACK)
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece['color'], 
                                     ((piece['x'] + x) * BLOCK_SIZE, (piece['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_next_piece(self, next_piece):
        start_x = COLS * BLOCK_SIZE + 20  # Posizione a destra della griglia
        start_y = 20
        for y, row in enumerate(next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, next_piece['color'], 
                                     (start_x + x * BLOCK_SIZE, start_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def update(self, grid, current_piece, next_piece):
        self.draw_grid(grid)
        self.draw_piece(current_piece)
        self.draw_next_piece(next_piece)
        pygame.display.flip()
        self.clock.tick(30)