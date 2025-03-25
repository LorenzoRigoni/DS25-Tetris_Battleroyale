# view.py

import pygame
from game_view import GameView
from vars import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class TetrisView:
    def __init__(self):
        # Initialize the Pygame window and set up the display
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()

        # Create 5 game views: 4 small ones and 1 main one
        self.game_views = []
        for i in range(4):
            # Create a new Surface for each small game view
            game_surface = pygame.Surface((GAME_SCREEN_WIDTH // 2, GAME_SCREEN_HEIGHT // 2))
            game_view = GameView(main=False, screen=game_surface)
            self.game_views.append((game_view, game_surface))
        
        # Create a new Surface for the main game view
        main_surface = pygame.Surface((GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT))
        self.main_game_view = GameView(main=True, screen=main_surface)

    def update(self, grid, current_piece,grids, current_pieces, next_piece, hold_piece, game_over=False):
        # Clear the main screen
        self.screen.fill(BLACK)

        # Draw the 4 small game views
        small_width = GAME_SCREEN_WIDTH // 2
        small_height = GAME_SCREEN_HEIGHT // 2
        main_passed = 0
        for i, (game_view, game_surface) in enumerate(self.game_views):
            if grids[i] == None:
                main_passed=1
                continue
            x = ((i-main_passed) % 2) * small_width
            y = ((i-main_passed)// 2) * small_height

            # Update the game view on its own surface
            game_view.update(grids[i-main_passed], current_piece[i-main_passed], next_piece, hold_piece, game_over)

            # Blit the game view's surface onto the main screen
            self.screen.blit(game_surface, (x, y))

        # Draw the main game view
        main_x = SCREEN_WIDTH // 2
        main_y = 0

        # Update the main game view on its own surface
        self.main_game_view.update(grid, current_piece, next_piece, hold_piece, game_over)

        # Blit the main game view's surface onto the main screen
        self.screen.blit(self.main_game_view.screen, (main_x, main_y))

        pygame.display.flip()
        self.clock.tick(30)