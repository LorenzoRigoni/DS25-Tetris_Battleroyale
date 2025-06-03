import subprocess
import time
import os

primary_server_script = os.path.abspath("start_primary.py")
backup_server_script = os.path.abspath("start_backup.py")

subprocess.Popen(["start", "cmd", "/k", f"python {primary_server_script}"], shell=True)

time.sleep(1)

subprocess.Popen(["start", "cmd", "/k", f"python {backup_server_script}"], shell=True)