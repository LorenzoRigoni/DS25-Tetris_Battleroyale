# game_view.py

import pygame
from utils.vars import *

WIDTH, HEIGHT = 400, 350

class GameView:
    PERSONAL_BLOCK_SIZE =BLOCK_SIZE
    def __init__(self, main, screen=None):
        self.main = main
        if main == False:
            self.PERSONAL_BLOCK_SIZE =BLOCK_SIZE // 2  
        self.screen = screen
        self.clock = pygame.time.Clock()

    def draw_grid(self, screen, grid):
        # Draw the game grid
        screen.fill(BLACK)
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell, (x * self.PERSONAL_BLOCK_SIZE, y * self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE))

    def draw_piece(self, screen, piece):
        # Draw the current piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'], 
                                     ((piece['x'] + x) * self.PERSONAL_BLOCK_SIZE, (piece['y'] + y) * self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE))

    def draw_next_piece(self, screen, next_piece):
        # Ridimensioniamo i blocchi per il prossimo pezzo
        small_block_size = self.PERSONAL_BLOCK_SIZE // 2  # Rendi i blocchi più piccoli
        start_x = 20  # Posizione in alto a sinistra
        start_y = 20  # Posizione in alto

        # Disegna il prossimo pezzo
        for y, row in enumerate(next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_piece['color'], 
                                     (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

        # Disegna un bordo intorno all'area del prossimo pezzo
        border_rect = pygame.Rect(start_x - 5, start_y - 5, NEXT_PIECE_AREA_WIDTH * small_block_size + 10, NEXT_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(screen, WHITE, border_rect, 2)

    def draw_hold_piece(self, screen, hold_piece):
        # Ridimensioniamo i blocchi per il pezzo in hold
        small_block_size = self.PERSONAL_BLOCK_SIZE // 2  # Rendi i blocchi più piccoli
        start_x =20  # Posizione a destra del campo di gioco
        start_y = 20 + NEXT_PIECE_AREA_HEIGHT * small_block_size + 20  # Posizione sotto il prossimo pezzo

        # Disegna il testo "HOLD" sopra l'area di hold
        font = pygame.font.SysFont(None, 24)
        hold_text = font.render("HOLD", True, WHITE)
        screen.blit(hold_text, (start_x, start_y - 20))

        # Disegna un bordo intorno all'area di hold (sempre visibile)
        border_rect = pygame.Rect(start_x - 5, start_y - 5, HOLD_PIECE_AREA_WIDTH * small_block_size + 10, HOLD_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(screen, WHITE, border_rect, 2)

        # Disegna il pezzo in hold (se presente)
        if hold_piece:
            for y, row in enumerate(hold_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, hold_piece['color'], 
                                        (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

    def draw_ghost_piece(self, screen, piece, grid):
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
                    top = ((abs_x * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE))
                    bottom = ((abs_x * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))
                    left = ((abs_x * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), (abs_x * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))
                    right = (((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))

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
            draw_dashed_line(screen, piece['color'], edge[0], edge[1], dash_length)

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

    def display_game_over(self, screen, main):
        if not main:
            cross_color = (255, 0, 0)
            cross_width = 5
            pygame.draw.line(screen, cross_color, (0, 0), (WIDTH/2, HEIGHT), cross_width)
            pygame.draw.line(screen, cross_color, (WIDTH/2, 0), (0, HEIGHT), cross_width)
        
    def update(self, grid, current_piece, next_piece, hold_piece, game_over=False):
        # Update the display with the current game state
        self.screen.fill(BLACK)
        self.draw_grid(self.screen, grid)
        self.draw_ghost_piece(self.screen, current_piece, grid)  # Draw the ghost piece
        self.draw_piece(self.screen, current_piece)
        if self.main:
            self.draw_next_piece(self.screen, next_piece)
            self.draw_hold_piece(self.screen, hold_piece)  # Draw the hold piece
        if game_over:
            self.display_game_over(self.screen,self.main)
        self.clock.tick(30)