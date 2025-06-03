import pygame
from .vars import *

WIDTH, HEIGHT = 400, 350

class GameView:
    '''This class manages the view of the game Tetris'''

    PERSONAL_BLOCK_SIZE =BLOCK_SIZE
    def __init__(self, main, screen=None):
        self.main = main
        if main == False:
            self.PERSONAL_BLOCK_SIZE =BLOCK_SIZE // 2  
        self.screen = screen
        self.clock = pygame.time.Clock()

    def draw_grid(self, screen, grid):
        '''Draw the game grid'''
        screen.fill(BLACK)
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell, (x * self.PERSONAL_BLOCK_SIZE, y * self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE))

    def draw_piece(self, screen, piece):
        '''Draw the current piece'''
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'], 
                                     ((piece['x'] + x) * self.PERSONAL_BLOCK_SIZE, (piece['y'] + y) * self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE, self.PERSONAL_BLOCK_SIZE))

    def draw_next_piece(self, screen, next_piece):
        '''Draw the next piece'''
        small_block_size = self.PERSONAL_BLOCK_SIZE // 2
        start_x = 20 
        start_y = 20

        for y, row in enumerate(next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_piece['color'], 
                                     (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

        border_rect = pygame.Rect(start_x - 5, start_y - 5, NEXT_PIECE_AREA_WIDTH * small_block_size + 10, NEXT_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(screen, WHITE, border_rect, 2)

    def draw_hold_piece(self, screen, hold_piece):
        '''Draw the hold piece'''
        small_block_size = self.PERSONAL_BLOCK_SIZE // 2
        start_x =20
        start_y = 20 + NEXT_PIECE_AREA_HEIGHT * small_block_size + 20

        font = pygame.font.SysFont(None, 24)
        hold_text = font.render("HOLD", True, WHITE)
        screen.blit(hold_text, (start_x, start_y - 20))

        border_rect = pygame.Rect(start_x - 5, start_y - 5, HOLD_PIECE_AREA_WIDTH * small_block_size + 10, HOLD_PIECE_AREA_HEIGHT * small_block_size + 10)
        pygame.draw.rect(screen, WHITE, border_rect, 2)

        if hold_piece:
            for y, row in enumerate(hold_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, hold_piece['color'], 
                                        (start_x + x * small_block_size, start_y + y * small_block_size, small_block_size, small_block_size))

    def draw_ghost_piece(self, screen, piece, grid):
        '''Clone the original piece as a ghost piece'''
        ghost_piece = {
            'shape': piece['shape'],
            'color': piece['color'],
            'x': piece['x'],
            'y': piece['y']
        }

        while not self.check_collision(ghost_piece, grid):
            ghost_piece['y'] += 1
        ghost_piece['y'] -= 1

        edges = []
        dash_length = 5

        for y, row in enumerate(ghost_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    abs_x = ghost_piece['x'] + x
                    abs_y = ghost_piece['y'] + y

                    top = ((abs_x * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE))
                    bottom = ((abs_x * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))
                    left = ((abs_x * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), (abs_x * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))
                    right = (((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, abs_y * self.PERSONAL_BLOCK_SIZE), ((abs_x + 1) * self.PERSONAL_BLOCK_SIZE, (abs_y + 1) * self.PERSONAL_BLOCK_SIZE))

                    if y == 0 or not ghost_piece['shape'][y - 1][x]:
                        edges.append(top)
                    if y == len(ghost_piece['shape']) - 1 or not ghost_piece['shape'][y + 1][x]:
                        edges.append(bottom)
                    if x == 0 or not ghost_piece['shape'][y][x - 1]:
                        edges.append(left)
                    if x == len(row) - 1 or not ghost_piece['shape'][y][x + 1]:
                        edges.append(right)

        def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=5):
            '''Draw the dashed line'''
            x1, y1 = start_pos
            x2, y2 = end_pos
            dx, dy = x2 - x1, y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            dashes = int(distance // (dash_length * 2))
            for i in range(dashes):
                start = (x1 + (dx * (i * 2 * dash_length) / distance), y1 + (dy * (i * 2 * dash_length) / distance))
                end = (x1 + (dx * ((i * 2 + 1) * dash_length) / distance), y1 + (dy * ((i * 2 + 1) * dash_length) / distance))
                pygame.draw.line(surface, color, start, end, 2)

        for edge in edges:
            draw_dashed_line(screen, piece['color'], edge[0], edge[1], dash_length)

    def check_collision(self, piece, grid):
        '''Check if the piece collides with the grid boundaries or other pieces'''
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x
                    new_y = piece['y'] + y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or grid[new_y][new_x]:
                        return True
        return False

    def display_game_over(self, screen, main):
        '''Display the game over'''
        if not main:
            cross_color = (255, 0, 0)
            cross_width = 5
            pygame.draw.line(screen, cross_color, (0, 0), (WIDTH/2, HEIGHT), cross_width)
            pygame.draw.line(screen, cross_color, (WIDTH/2, 0), (0, HEIGHT), cross_width)
        
    def update(self, grid, current_piece, next_piece, hold_piece, game_over=False):
        '''Update the display with the current game state'''
        self.screen.fill(BLACK)
        self.draw_grid(self.screen, grid)
        self.draw_ghost_piece(self.screen, current_piece, grid)
        self.draw_piece(self.screen, current_piece)
        if self.main:
            self.draw_next_piece(self.screen, next_piece)
            self.draw_hold_piece(self.screen, hold_piece)
        if game_over:
            self.display_game_over(self.screen,self.main)
        self.clock.tick(30)