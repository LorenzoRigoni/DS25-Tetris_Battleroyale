import socket
import time
import threading
from remote.package import Package
from remote.server import Server
from remote.game_room import GameRoom

class BackupServer(Server):
    '''This class represents the backup server. It checks the availability of the primary server and, when the primary goes offline, the backup is promoted
    to primary.'''
    def __init__(self, host="127.0.0.1", port=8081, primary_host = "127.0.0.1", primary_port = 8080):
        self.primary_addr = (primary_host, primary_port)
        self.backup_addr = (host, port)
        self.backup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.backup_sock.bind(self.backup_addr)

        self.last_primary_heartbeat = time.time()
        self.running = True
        self.active = False
        self.server: Server = None

    def start_backup(self):
        '''Start the backup server'''
        try:
            self.backup_sock.sendto(Package.encode(Package.BACKUP_READY), self.primary_addr)
            self.check_primary_is_alive()
        except KeyboardInterrupt:
            self.stop_backup()

    def stop_backup(self):
        '''Stop the backup server'''
        self.running = False
        if self.server:
            self.server.running = False
            self.server = None
        self.active = False

    def check_primary_is_alive(self):
        '''Check if primary server is alive'''
        while self.running:
            try:
                data, addr = self.backup_sock.recvfrom(8192)
                type, p_data = Package.decode(data)
                if type == Package.PRIMARY_HEARTBEAT:
                    self.last_primary_heartbeat = time.time()
                    if self.active:
                        self.stop_backup()
                elif type == Package.HEARTBEAT and not self.active and time.time() - self.last_primary_heartbeat > 2:
                    self.replace_primary_server()
                else:
                    self.handle_received_packet(addr, type, p_data)
            except ConnectionResetError:
                continue
            except Exception as e:
                print("Exception in the backup server: ", e)

    def replace_primary_server(self):
        '''Replace the primary server'''
        super().__init__(self.backup_addr[0], self.backup_addr[1], False, self.backup_sock)
        self.active = True
        threading.Thread(target=self.start, daemon=True).start()