# controller.py

import pygame
from model import TetrisModel
from view import TetrisView
from vars import *

class TetrisController:
    def __init__(self):
        # Initialize the model, view, and game settings
        self.model = TetrisModel()
        self.view = TetrisView()
        self.fall_speed = FALL_SPEED
        self.last_fall_time = pygame.time.get_ticks()
        self.fast_fall = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_cooldown = 200  # Cooldown for lateral movement (in milliseconds)

    def handle_events(self):
        # Handle user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.rotate_piece_intelligently()
                elif event.key == pygame.K_SPACE:  # Drop the piece to the bottom
                    self.drop_piece_to_bottom()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:  # Hold the piece
                    self.model.hold_current_piece()
                elif event.key == pygame.K_m:  # Add a gray line with a random hole
                    self.model.add_gray_line_with_hole()
        return True

    def drop_piece_to_bottom(self):
        # Move the piece down until it collides
        while self.model.move_piece(0, 1):
            pass
        self.model.lock_piece()
        lines_cleared = self.model.clear_lines()
        if lines_cleared:
            print(f"Lines cleared: {lines_cleared}")

    def rotate_piece_intelligently(self):
        # Try to rotate the piece and handle collisions
        self.model.rotate_piece()
        if self.model.check_collision():
            # If there is a collision, try to move the piece left
            self.model.move_piece(-1, 0)
            if self.model.check_collision():
                # If still colliding, try to move the piece right
                self.model.move_piece(2, 0)
                if self.model.check_collision():
                    # If still colliding, revert everything
                    self.model.move_piece(-1, 0)
                    self.model.rotate_piece()  # Revert the rotation

    def run(self):
        # Main game loop
        running = True
        game_over = False  # Flag to track game over state
        while running:
            if not game_over:
                running = self.handle_events()

                keys = pygame.key.get_pressed()
                current_time = pygame.time.get_ticks()

                # Lateral movement with cooldown
                if current_time - self.last_move_time > self.move_cooldown:
                    if keys[pygame.K_LEFT]:
                        self.model.move_piece(-1, 0)
                        self.last_move_time = current_time
                    if keys[pygame.K_RIGHT]:
                        self.model.move_piece(1, 0)
                        self.last_move_time = current_time

                # Fast fall if the key is pressed
                if keys[pygame.K_DOWN]:
                    self.fast_fall = True
                else:
                    self.fast_fall = False

                # Automatic piece falling
                if current_time - self.last_fall_time > (self.fall_speed // 10 if self.fast_fall else self.fall_speed):
                    if not self.model.move_piece(0, 1):
                        # Lock the piece and check for game over
                        game_over = self.model.lock_piece()
                        lines_cleared = self.model.clear_lines()
                        if lines_cleared:
                            print(f"Lines cleared: {lines_cleared}")
                    self.last_fall_time = current_time

                # Update the view
                self.view.update(self.model.grid, self.model.current_piece, self.model.next_piece, self.model.hold_piece)
            else:
                # Game over state
                font = pygame.font.SysFont(None, 74)
                game_over_text = font.render("GAME OVER", True, (255, 0, 0))
                self.view.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
                pygame.display.flip()

                # Wait for a key press to quit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

        pygame.quit()