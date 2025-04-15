# Tetris.py
import sys
from game.controller import TetrisController

# Initialize and run the game

#TODO other parameters?
isMain = bool(sys.argv[0])
ip = sys.argv[1]
port = sys.argv[2]
if isMain:
    game = TetrisController(ip,port,"client")
else:
    game = TetrisController(ip,port,"server")
game.run()