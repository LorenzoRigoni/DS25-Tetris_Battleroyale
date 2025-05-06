import multiprocessing
import time
import atexit
import signal
import json
from remote.primary_server import PrimaryServer
from remote.backup_server import BackupServer

def run_primary():
    server = PrimaryServer()
    server.start_primary()

def run_backup():
    backup = BackupServer()
    backup.start_backup()

def cleanup_state_file():
    try:
        with open("server_state.json", "w") as file:
            json.dump({}, file)
    except Exception as e:
        print("Exception on cleaning the server state: ", e)

if __name__ == "__main__":
    primary_process = multiprocessing.Process(target=run_primary)
    backup_process = multiprocessing.Process(target=run_backup)

    primary_process.start()
    time.sleep(1)
    backup_process.start()

    atexit.register(cleanup_state_file)
    signal.signal(signal.SIGINT, exit(0))
    signal.signal(signal.SIGTERM, exit(0))

    primary_process.join()
    backup_process.join()