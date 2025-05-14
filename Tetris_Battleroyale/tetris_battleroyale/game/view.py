# view.py

import pygame
from game.game_view import GameView
from utils.vars import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class TetrisView:
    def __init__(self):
        # Initialize the Pygame window and set up the display
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris BattleRoyale')
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

    def update(self, grid, current_piece,grids, current_pieces, next_piece, hold_piece, game_over,games_over,name,names, current_player_id):
        # Clear the main screen
        self.screen.fill(BLACK)

        # Draw the 8 small game views
        small_width = GAME_SCREEN_WIDTH // 2
        small_height = GAME_SCREEN_HEIGHT // 2
        views_copy = self.game_views.copy()
        #remove the game view of the current player from the list of game views
        #views_copy.pop(current_player_id)
        for i, (game_view, game_surface) in enumerate(views_copy):
            x = i % 2 * small_width + (GAME_SCREEN_WIDTH*2 if i >= 4 else 0)
            y = ((i// 2)%2) * small_height
            # Update the game view on its own surface
            game_view.update(grids[i], current_pieces[i], next_piece, hold_piece, games_over[i])
            
            #draw a white border around the game view
            pygame.draw.rect(game_surface, WHITE, (0, 0, small_width, small_height), 2)

            #put player name on the game view on top of the game view
            font = pygame.font.Font(None, 36)
            text = font.render(names[i], True, WHITE)
            text_rect = text.get_rect(center=(small_width // 2, 18))
            game_surface.blit(text, text_rect)

            # Blit the game view's surface onto the main screen
            self.screen.blit(game_surface, (x, y))
        # Draw the main game view
        main_x = SCREEN_WIDTH // 2
        main_y = 0

        # Update the main game view on its own surface
        self.main_game_view.update(grid, current_piece, next_piece, hold_piece, game_over)

        #draw name of the player on the main game view
        font = pygame.font.Font(None, 36)
        text = font.render(name, True, WHITE)
        text_rect = text.get_rect(center=(GAME_SCREEN_WIDTH // 2, 18))
        self.main_game_view.screen.blit(text, text_rect)
        # Blit the main game view's surface onto the main screen
        self.screen.blit(self.main_game_view.screen, (main_x, main_y))

        #pygame.display.flip()
        #self.clock.tick(30)
    
    def display_searching(self,number_out_of_5):
        # Display the searching screen
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render(f"Searching for a game... {number_out_of_5}/5", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
    #pause screen with button to exit to main menu
    def display_pause(self):
        # Display the pause screen
        font = pygame.font.Font(None, 74)
        text = font.render("Paused", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)

        # Button to exit to main menu
        button_text = font.render("Exit to Main Menu", True, BLACK)
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.draw.rect(self.screen, WHITE, button_rect.inflate(20, 20), 0)
        self.screen.blit(button_text, button_rect)
        return button_rect
    
    def display_game_over(self):
        # Display the game over screen
        font = pygame.font.Font(None, 74)
        text = font.render("Game over", True, WHITE, (128, 128, 128))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def display_winner(self, winner_name):
        # Display the winner screen
        font = pygame.font.Font(None, 74)
        text = font.render(f"{winner_name} wins!", True, WHITE, (128, 128, 128))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def update_all(self):
        pygame.display.flip()
        self.clock.tick(30)
