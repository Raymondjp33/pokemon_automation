from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from pathlib import Path

import json
import sqlite3
import os 
import time
import redis

import eventlet
eventlet.monkey_patch()
app = Flask(__name__, static_folder=Path(__file__).resolve().parent.parent / 'stream-browser'/ 'stream_browser' / 'build' / 'web')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")  # Enable CORS
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

DB_FILE = "my_pokemon.db"
STREAM_DATA_FILE = "stream_data.json"
REDIS_CHANNEL = "update_data"

stream_data_last_modified = 0

def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)

    for message in pubsub.listen():
        # print(f'In redis listener message {message}')
        if message['type'] == 'message':
            data = json.loads(message['data'])
            try:
                if data.get('update_data', False):
                     emit_pokemon_data()
            except Exception as e:
                 print(f"Error in redis_listener: {e}")

@socketio.on('init_connect')
def handle_connect():
        try:
            if not os.path.exists(STREAM_DATA_FILE):
                return
            
            with open(STREAM_DATA_FILE) as stream_data_file:
                stream_data = json.load(stream_data_file)
            print(f"[WebSocket] Emitting init connect")
            socketio.emit("stream_data", stream_data)
            emit_pokemon_data()
        except Exception as e:
                print(f"Error reading file: {e}")

def emit_pokemon_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(STREAM_DATA_FILE) as stream_data_file:
        stream_data = json.load(stream_data_file)

    switch1_hunt_id = stream_data['switch1_hunt_id']
    switch2_hunt_id = stream_data['switch2_hunt_id']

    cursor.execute("SELECT * FROM hunt_encounters WHERE hunt_id = ? OR hunt_id = ?", (switch1_hunt_id, switch2_hunt_id,))
    pokemon_rows = cursor.fetchall()

    pokemon_data = []
    for pokemon in pokemon_rows:
        cursor.execute("SELECT * FROM catches WHERE hunt_id = ? AND name = ?", (pokemon[2], pokemon[4],))
        catch_rows = cursor.fetchall()
        pokemon_data.append({
            "encounters": pokemon[3],
            "pokemon_id": str(pokemon[1]),
            "name": pokemon[4],
            "targets": pokemon[6],
            "switchNum": pokemon[5],
            "started_hunt_ts": pokemon[7],
            "total_dens": pokemon[9],
            "catches": [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "switch": switchUsed, "total_dens": tdens} for _, _, ts, enc, method, switchUsed, _, tdens, _ in catch_rows]
        })

    print(f"[WebSocket] Emitting pokemon data")
    socketio.emit("pokemon_data", {"pokemon": pokemon_data, "pokemonStats": get_pokemon_stats(cursor)})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

def watch_file():
    global stream_data_last_modified
    while True:
        try:
            if not os.path.exists(STREAM_DATA_FILE):
                return
            mtime = os.path.getmtime(STREAM_DATA_FILE)
            if mtime == stream_data_last_modified:
                time.sleep(2)
                continue

            with open(STREAM_DATA_FILE) as f:
                file_data = json.load(f)
            stream_data_last_modified = mtime
            print(f"[WebSocket] Emitting update")
            socketio.emit('stream_data', file_data)
        except Exception as e:
                print(f"Error reading file: {e}")
        
        time.sleep(2)

def get_pokemon_stats(cursor):
    totalEggShinies = cursor.execute("SELECT COUNT(*) FROM catches WHERE encounter_method = ?", ('egg',)).fetchone()[0]
    totalEggs = cursor.execute("SELECT SUM(encounters) FROM hunt_encounters WHERE encounter_method = ?", ('egg',)).fetchone()[0]
    averageEggs = totalEggs / totalEggShinies 
    
    totalStaticShinies = cursor.execute("SELECT COUNT(*) FROM catches WHERE encounter_method = ?", ('static',)).fetchone()[0]
    totalStatic = cursor.execute("SELECT SUM(encounters) FROM hunt_encounters WHERE encounter_method = ?", ('static',)).fetchone()[0]
    averageStatic = totalStatic / totalStaticShinies

    totalWildShinies = cursor.execute("SELECT COUNT(*) FROM catches WHERE encounter_method = ?", ('wild',)).fetchone()[0]
    totalWild = cursor.execute("SELECT SUM(encounters) FROM hunt_encounters WHERE encounter_method = ?", ('wild',)).fetchone()[0]
    averageWild = totalWild / totalWildShinies 


    return {
        "totalEggShinies": totalEggShinies, "totalEggs": totalEggs, "averageEggs": averageEggs, 
        "totalStaticShinies": totalStaticShinies, "totalStatic": totalStatic, "averageStatic": averageStatic,
        "totalWildShinies":totalWildShinies, "totalWild": totalWild, "averageWild": averageWild,
        }

# http://0.0.0.0:5050/
if __name__ == '__main__':
    socketio.start_background_task(target=redis_listener)
    socketio.start_background_task(target=watch_file)
    socketio.run(app, host='0.0.0.0', port=5050)