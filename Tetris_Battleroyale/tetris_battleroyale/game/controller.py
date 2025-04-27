# controller.py

import pygame
from game.model import TetrisModel
from game.view import TetrisView
from utils.vars import *
import time

class TetrisController:
    current_lobby_id=0
    players_in_lobby=0
    def __init__(self,player_number = 9):
        self.running = True
        self.game_over = False 
        self.player_number = player_number
        # Initialize the model, view, and game settings
        self.model = TetrisModel(self)
        self.view = TetrisView()
        self.fall_speed = FALL_SPEED
        self.last_fall_time = pygame.time.get_ticks()
        self.fast_fall = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_cooldown = 200  # Cooldown for lateral movement (in milliseconds)
        self.searching = True

        
        #initilize grids and pieces
        self.grids = [None]*self.player_number
        self.current_pieces = [None]*self.player_number
        self.defeats = [False]*self.player_number
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = {'shape': [[1, 1, 1], [0, 1, 0]], 'color': (255, 0, 0), 'x': 3, 'y': 0}
        self.next_piece = {'shape': [[1, 1, 1], [0, 1, 0]], 'color': (255, 0, 0), 'x': 3, 'y': 0}

        for i in range(self.player_number-1):
                if self.grids[i] == None:
                    self.grids[i] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                    self.current_pieces[i] = {'shape': [[1, 1, 1], [0, 1, 0]], 'color': (255, 0, 0), 'x': 3, 'y': 0}
                    self.defeats[i] = False
            
    def handle_events(self):
        # Handle user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.model.rotate_piece_intelligently()
                elif event.key == pygame.K_SPACE:  # Drop the piece to the bottom
                    self.model.drop_piece_to_bottom()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:  # Hold the piece
                    self.model.hold_current_piece()
                elif event.key == pygame.K_m:  # Add a gray line with a random hole
                    self.model.add_gray_line_with_hole()
    #TODO remove 10 as default value also this is only for client, no server implementation yet
    def run(self):
        
        print("Starting search...")
        while self.searching:
            # Search for a game
            self.view.display_searching(self.players_in_lobby)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
        while self.running:
            #update enemies with random values for testing
            
            if not self.game_over:
                self.handle_events()

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
                    self.client.send_game_state(self.model.grid,self.model.current_piece)

                # Update the view
                self.view.update(self.model.grid, self.model.current_piece,self.grids,self.current_pieces, self.model.next_piece, self.model.hold_piece, self.game_over,self.defeats)
                # Send the game state to the server
                
            else:
                print("Game over")
                self.send_defeat()
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
        #upodate the grids and piece of the players
        self.grids[playerNumber] = grid
        self.current_pieces[playerNumber] = current_piece

    def send_game_state(self):
        # Send the game state to the server
        if hasattr(self, 'client'):
            self.client.send_game_state(self.model.grid, self.server.lobby_id, self.model.current_piece)
        #TODO
        elif hasattr(self, 'server'):
            pass
    def send_broken_row(self, target):
        # Send the broken rows to the server
        if hasattr(self, 'client'):
            self.client.send_broken_row(target)
        #TODO
        elif hasattr(self, 'server'):
            pass
    def send_defeat(self):
        # Send the defeat message to the server
        if hasattr(self, 'client'):
            self.client.send_defeat()
        #TODO
        elif hasattr(self, 'server'):
            pass
    def receive_broken_line(self):
        self.model.add_broken_line()
    
    def receive_defeat(self, player_id):
        self.defeats[player_id] = True
    
    def receive_game_state(self, grid, current_piece):
        # Update the game state of the player
        self.model.grid = grid
        self.model.current_piece = current_piece
        self.model.updateEnemies(self.player_number, grid, current_piece)