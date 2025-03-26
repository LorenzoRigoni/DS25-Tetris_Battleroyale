# controller.py

import pygame
from model import TetrisModel
from view import TetrisView
from vars import *
from remote.client.client_game_manager import ClientGameManager
from remote.server.server_game_manager import ServerGameManager

class TetrisController:
    def __init__(self,ip,port,mode="client"):
        # Initialize the model, view, and game settings
        self.model = TetrisModel()
        self.view = TetrisView()
        self.fall_speed = FALL_SPEED
        self.last_fall_time = pygame.time.get_ticks()
        self.fast_fall = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_cooldown = 200  # Cooldown for lateral movement (in milliseconds)
        if mode == "client":
            self.client = ClientGameManager(0,"bruno",self,ip,port)
        else:
            self.server = ServerGameManager(self,ip,port,num_max_lobbies=1,num_max_players_per_lobby=10,num_min_players_per_lobby=2)

    def handle_events(self):
        # Handle user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.model.rotate_piece_intelligently()
                elif event.key == pygame.K_SPACE:  # Drop the piece to the bottom
                    self.model.drop_piece_to_bottom()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:  # Hold the piece
                    self.model.hold_current_piece()
                elif event.key == pygame.K_m:  # Add a gray line with a random hole
                    self.model.add_gray_line_with_hole()
        return True
    grids = []
    current_pieces = []
    player_number = None
    #TODO remove 4 as default value
    def run(self,player_number = 10):
        self.player_number = player_number
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
                self.view.update(self.model.grid, self.model.current_piece,self.grids,self.current_pieces, self.model.next_piece, self.model.hold_piece, game_over)
            else:
                # Game over state
                self.view.display_game_over()
                # Wait for a key press to quit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

        pygame.quit()
    def updateEnemies(self, playerNumber, grid, current_piece):
        #initilize grids and pieces
        if len(self.grids) < self.player_number:
            self.grids = [None]*self.player_number
            self.current_pieces = [None]*self.player_number
        #upodate the grids and piece of the players
        self.grids[playerNumber] = grid
        self.current_pieces[playerNumber] = current_piece