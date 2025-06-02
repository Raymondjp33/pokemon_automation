from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import os, json, time
from threading import Thread
import eventlet
from pathlib import Path
import subprocess
import threading

eventlet.monkey_patch()
app = Flask(__name__, static_folder=Path(__file__).resolve().parent.parent / 'stream-browser'/ 'stream_browser' / 'build' / 'web')
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS

switch1_file_path = 'switch1_data.json'
switch2_file_path = 'switch2_data.json'
stream_data_file_path = 'stream_data.json'

modified_vars = {
    'switch1_last_modified' : 0,
    'switch2_last_modified' : 0,
    'stream_data_last_modified' : 0
    }

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@socketio.on('init_connect')
def handle_connect():
        try:
            if not os.path.exists(switch1_file_path) or not os.path.exists(switch2_file_path) or not os.path.exists(stream_data_file_path):
                return

            file_data1 = {}
            file_data2 = {}
            file_data3 = {}
            with open(switch1_file_path) as f1, open(switch2_file_path) as f2, open(stream_data_file_path) as f3:
                file_data1 = json.load(f1)
                file_data2 = json.load(f2)
                file_data3 = json.load(f3)
            print(f"[WebSocket] Emitting init connect")
            socketio.emit("switch1_data", file_data1)
            socketio.emit("switch2_data", file_data2)
            socketio.emit("stream_data", file_data3)
        except Exception as e:
                print(f"Error reading file: {e}")

def watch_files():
    global last_modified, file_data
    while True:
        handle_file_update(switch1_file_path, 'switch1_last_modified', 'switch1_data')
        handle_file_update(switch2_file_path, 'switch2_last_modified', 'switch2_data')
        handle_file_update(stream_data_file_path, 'stream_data_last_modified', 'stream_data')
       
        time.sleep(2)

def handle_file_update(file_path, modified_var, emit_variable):
    try:
        if not os.path.exists(file_path):
            return
        mtime = os.path.getmtime(file_path)
        if mtime == modified_vars[modified_var]:
            return

        file_data = {}
        with open(file_path) as f:
            file_data = json.load(f)
        modified_vars[modified_var] = mtime
        print(f"[WebSocket] Emitting update")
        socketio.emit(emit_variable, file_data)
    except Exception as e:
            print(f"Error reading file: {e}")

@socketio.on('start_process')
def start_process(data):
    def run_and_stream():
        scripts_path = Path(__file__).resolve().parent.parent / 'scripts-new' 
        print(f"Beginning process")
        process = subprocess.Popen(
            ["python3.9", "-u", str(scripts_path / data["file"])],  # Replace with your command
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            socketio.emit('process_output', {'line': line})

        process.stdout.close()
        process.wait()
        socketio.emit('process_complete', {'code': process.returncode})
        print(f"Process complete")
    threading.Thread(target=run_and_stream).start()
     


# http://0.0.0.0:5050/
if __name__ == '__main__':
    socketio.start_background_task(target=watch_files)
    socketio.run(app, host='0.0.0.0', port=5050)


# import sqlite3

# DB_FILE = "my_pokemon.db"

# def get_pokemon_data():
#     conn = sqlite3.connect(DB_FILE)
#     cur = conn.cursor()
#     cur.execute("""
#     SELECT c.caught_timestamp, c.encounters, c.encounter_method
#     FROM pokemon p JOIN catch c ON p.id = c.pokemon_id
#     WHERE p.name = ?
#     """, (pokemon_name,))

# print(get_pokemon_data)