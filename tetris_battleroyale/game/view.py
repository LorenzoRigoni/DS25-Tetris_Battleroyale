import pygame
from .game_view import GameView
from .vars import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class TetrisView:
    '''This class is the view of the MVC pattern. It manages the display of the game.'''

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris BattleRoyale')
        self.clock = pygame.time.Clock()

        self.game_views = []
        for i in range(4):
            game_surface = pygame.Surface((GAME_SCREEN_WIDTH // 2, GAME_SCREEN_HEIGHT // 2))
            game_view = GameView(main=False, screen=game_surface)
            self.game_views.append((game_view, game_surface))
        
        main_surface = pygame.Surface((GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT))
        self.main_game_view = GameView(main=True, screen=main_surface)

    def update(self, grid, current_piece,grids, current_pieces, next_piece, hold_piece, game_over,games_over,name,names):
        '''Update all yje svreens'''
        self.screen.fill(BLACK)

        small_width = GAME_SCREEN_WIDTH // 2
        small_height = GAME_SCREEN_HEIGHT // 2
        views_copy = self.game_views.copy()
        for i, (game_view, game_surface) in enumerate(views_copy):
            x = i % 2 * small_width + (GAME_SCREEN_WIDTH*2 if i >= 4 else 0)
            y = ((i// 2)%2) * small_height
            game_view.update(grids[i], current_pieces[i], next_piece, hold_piece, games_over[i])
            
            pygame.draw.rect(game_surface, WHITE, (0, 0, small_width, small_height), 2)

            font = pygame.font.Font(None, 36)
            text = font.render(names[i], True, WHITE)
            text_rect = text.get_rect(center=(small_width // 2, 18))
            game_surface.blit(text, text_rect)

            self.screen.blit(game_surface, (x, y))
        main_x = SCREEN_WIDTH // 2
        main_y = 0

        self.main_game_view.update(grid, current_piece, next_piece, hold_piece, game_over)

        font = pygame.font.Font(None, 36)
        text = font.render(name, True, WHITE)
        text_rect = text.get_rect(center=(GAME_SCREEN_WIDTH // 2, 18))
        self.main_game_view.screen.blit(text, text_rect)
        self.screen.blit(self.main_game_view.screen, (main_x, main_y))
    
    def display_searching(self,number_out_of_5):
        '''Display the searching screen'''
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render(f"Searching for a game... {number_out_of_5}/5", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def display_pause(self):
        '''Display the pause screen'''
        font = pygame.font.Font(None, 74)
        text = font.render("Paused", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)

        button_text = font.render("Exit to Main Menu", True, BLACK)
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.draw.rect(self.screen, WHITE, button_rect.inflate(20, 20), 0)
        self.screen.blit(button_text, button_rect)
        return button_rect
    
    def display_game_over(self):
        '''Display the game over screen'''
        font = pygame.font.Font(None, 74)
        text = font.render("Game over", True, WHITE, (128, 128, 128))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def display_winner(self, winner_name):
        '''Display the winner screen'''
        font = pygame.font.Font(None, 74)
        text = font.render(f"{winner_name} wins!", True, WHITE, (128, 128, 128))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def update_all(self):
        pygame.display.flip()
        self.clock.tick(30)
