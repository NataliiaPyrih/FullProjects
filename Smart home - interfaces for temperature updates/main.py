import threading
import subprocess

def run_server():
    subprocess.run(["python", "server.py"])

def run_interface():
    subprocess.run(["python", "interface.py"])

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_server)
    flask_thread.start()

    tkinter_thread = threading.Thread(target=run_interface)
    tkinter_thread.daemon = True
    tkinter_thread.start()