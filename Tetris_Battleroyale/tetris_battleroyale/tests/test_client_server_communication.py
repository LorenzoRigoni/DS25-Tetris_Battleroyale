import pytest
import socket
import threading

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Tetris_Battleroyale.tetris_battleroyale.remote.package import Package

@pytest.fixture
def server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 8080))
    yield server_socket
    server_socket.close()

@pytest.fixture
def client_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    yield client_socket
    client_socket.close()

def test_client_server_communication(server_socket, client_socket):
    '''Test the communication between client and server'''
    package = Package()
    server_address = server_socket.getsockname()

    def server():
        data, addr = server_socket.recvfrom(1024)
        type, _ = package.decode(data)
        global server_received
        server_received = type

        reply = package.encode(Package.HEARTBEAT)
        server_socket.sendto(reply, addr)

    server_thread = threading.Thread(target=server)
    server_thread.start()

    message = package.encode(Package.HEARTBEAT)
    client_socket.sendto(message, server_address)

    client_socket.settimeout(2.0)
    data, _ = client_socket.recvfrom(1024)
    client_received, _ = package.decode(data)

    server_thread.join()

    assert server_received == Package.HEARTBEAT
    assert client_received == Package.HEARTBEAT