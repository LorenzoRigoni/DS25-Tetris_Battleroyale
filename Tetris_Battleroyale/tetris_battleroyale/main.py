import pygame
import subprocess
import socket
import time
from remote.server import Server
from remote.client import Client
from game.controller import TetrisController
from utils.package import Package

WIDTH, HEIGHT = 400, 350

class TetrisLauncher:
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris Battleroyale")
        self.font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 28)
        self.running = True
        self.name = ""
        self.active_input = False
    
    def draw_button(self, text, rect, active):
        color = (0, 200, 0) if active else (0, 150, 0)
        pygame.draw.rect(self.screen, color, rect)
        txt = self.font.render(text, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect.center)
        self.screen.blit(txt, txt_rect)

    def draw_input_box(self, rect):
        color = (255, 255, 255) if self.active_input else (200, 200, 200)
        pygame.draw.rect(self.screen, color, rect, 2)
        txt = self.input_font.render(self.name or "Enter your name", True, (255, 255, 255))
        self.screen.blit(txt, (rect.x + 10, rect.y + 8))

    def is_server_running(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            ping = Package.encode(Package.PING)
            sock.sendto(ping, (ip, port))
            data, addr = sock.recvfrom(4096)
            sock.close()
            return True
        except Exception:
            return False
        
    def start_server(self):
        subprocess.Popen(["python", "server.py"])
        time.sleep(2)

    def start(self):
        ip = "127.0.0.1"
        port = 12345

        #if not self.is_server_running(ip, port):
            #self.start_server()

        controller = TetrisController()
        client = Client(self.name, controller)
        controller.client = client
        #client.start()
        #TODO questo va tolto che sta nel client
        controller.run()

    def run(self):
        input_rect = pygame.Rect(100, 120, 200, 40)
        button_rect = pygame.Rect(100, 190, 200, 50)

        while self.running:
            self.screen.fill((30, 30, 30))
            title = self.font.render("TETRIS BATTLEROYALE", True, (255, 255, 255))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

            mouse_pos = pygame.mouse.get_pos()
            click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        self.active_input = True
                    else:
                        self.active_input = False
                    if event.button == 1 and button_rect.collidepoint(mouse_pos):
                        if self.name.strip():
                            self.start()
                            self.running = False
                elif event.type == pygame.KEYDOWN and self.active_input:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif len(self.name) < 16 and event.unicode.isprintable():
                        self.name += event.unicode

            hovered = button_rect.collidepoint(mouse_pos)
            self.draw_input_box(input_rect)
            self.draw_button("Enter", button_rect, hovered)
            pygame.display.flip()

launcher = TetrisLauncher()
launcher.run()