# vars.py
import random
# Dimensioni della finestra di gioco
GAME_SCREEN_WIDTH = 400  # Aumentata per far spazio al prossimo pezzo
GAME_SCREEN_HEIGHT = 800

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Dimensioni del blocco
BLOCK_SIZE = GAME_SCREEN_WIDTH // 10  # 10 blocks per row

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0)     # Red
]

# Matrice di gioco
ROWS = 20
COLS = 10

# Velocità di discesa
FALL_SPEED = 500  # in millisecondi

# Area del prossimo pezzo
NEXT_PIECE_AREA_WIDTH = 4  # Larghezza in blocchi (ridotta)
NEXT_PIECE_AREA_HEIGHT = 4  # Altezza in blocchi (ridotta)

# Area di hold
HOLD_PIECE_AREA_WIDTH = 4  # Larghezza in blocchi (ridotta)
HOLD_PIECE_AREA_HEIGHT = 4  # Altezza in blocchi (ridotta)