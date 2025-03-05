# controller.py

import pygame
from model import TetrisModel
from view import TetrisView
from vars import *

class TetrisController:
    def __init__(self):
        self.model = TetrisModel()
        self.view = TetrisView()
        self.fall_speed = FALL_SPEED
        self.last_fall_time = pygame.time.get_ticks()
        self.fast_fall = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_cooldown = 200  # Cooldown per il movimento laterale (in millisecondi)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.rotate_piece_intelligently()
        return True

    def rotate_piece_intelligently(self):
        # Prova a ruotare il pezzo
        self.model.rotate_piece()
        if self.model.check_collision():
            # Se c'è una collisione, prova a spostare il pezzo a sinistra
            self.model.move_piece(-1, 0)
            if self.model.check_collision():
                # Se ancora collisione, prova a spostare il pezzo a destra
                self.model.move_piece(2, 0)
                if self.model.check_collision():
                    # Se ancora collisione, annulla tutto
                    self.model.move_piece(-1, 0)
                    self.model.rotate_piece()  # Annulla la rotazione

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()

            # Movimento laterale con cooldown
            if current_time - self.last_move_time > self.move_cooldown:
                if keys[pygame.K_LEFT]:
                    self.model.move_piece(-1, 0)
                    self.last_move_time = current_time
                if keys[pygame.K_RIGHT]:
                    self.model.move_piece(1, 0)
                    self.last_move_time = current_time

            # Movimento verticale veloce se il tasto è premuto
            if keys[pygame.K_DOWN]:
                self.fast_fall = True
            else:
                self.fast_fall = False

            # Caduta automatica del pezzo
            if current_time - self.last_fall_time > (self.fall_speed // 10 if self.fast_fall else self.fall_speed):
                if not self.model.move_piece(0, 1):
                    self.model.lock_piece()
                    lines_cleared = self.model.clear_lines()
                    if lines_cleared:
                        print(f"Lines cleared: {lines_cleared}")
                self.last_fall_time = current_time

            # Aggiorna la vista
            self.view.update(self.model.grid, self.model.current_piece, self.model.next_piece)

        pygame.quit()