import threading
import time
import socket
from .server import Server
from .package import Package

class PrimaryServer(Server):
    '''This class represents the primary server. Every 2 seconds, it sends to the backup server its heartbeat.
    If the primary server do not send its heartbeat for more than 5 seconds, the backup sever is promoted to primary.'''

    def __init__(self, host="127.0.0.1", port=8080):
        super().__init__(host, port, True, None)
        self.backup_ready = False
        self.heartbeat_started = False
        self.backup_addr = None

    def start_primary(self):
        '''Start the primary server'''
        threading.Thread(target=self.receive_backup_ready, daemon=True).start()
        super().start()

    def receive_backup_ready(self):
        '''Receive the packet of backup server ready'''
        while True:
            try:
                data, addr = self.sock.recvfrom(8192)
                type, content = Package.decode(data)

                if type == Package.BACKUP_READY:
                    print("Received BACKUP_CHECK from backup")
                    self.backup_ready = True
                    self.backup_addr = addr
                    if not self.heartbeat_started:
                        self.heartbeat_started = True
                        threading.Thread(target=self.send_heartbeat_to_backup, daemon=True).start()
                else:
                    self.handle_received_packet(addr, type, content)

            except Exception as e:
                print(f"Error receiving packet: {e}")
                continue

    def send_heartbeat_to_backup(self):
        '''Send heartbeat to backup server'''
        while self.backup_ready:
            try:
                packet = Package.encode(Package.PRIMARY_HEARTBEAT)
                self.sock.sendto(packet, self.backup_addr)
                time.sleep(1)
            except Exception as e:
                print("Error sending heartbeat to backup: ", e)