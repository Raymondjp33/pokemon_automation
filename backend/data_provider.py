from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import eventlet
import eventlet.hubs

eventlet.hubs.use_hub("poll")
eventlet.monkey_patch()

from flask import Flask, send_from_directory  # noqa: E402
from flask_socketio import SocketIO  # noqa: E402
import redis  # noqa: E402
import serial  # noqa: E402

_PROJ_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJ_ROOT))
sys.path.insert(0, str(_PROJ_ROOT / "scripts"))

import manager as script_manager  # noqa: E402
from services.common import (  # noqa: E402
    REDIS_CHANNEL,
    STREAM_DATA_PATH,
    CatchModel,
    HuntEncounterModel,
    _get_connection,
    press,
    get_switch_serial,
)

app = Flask(
    __name__,
    static_folder=Path(__file__).resolve().parent.parent / "stream-browser" / "stream_browser" / "build" / "web",
)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

stream_data_last_modified = 0

# Tracks last-emitted state per pokemon: (hunt_id, name) -> (encounters, catch_count)
_pokemon_cache: dict[tuple[int, str], tuple[int, int]] = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class CatchData:
    catch_name: str
    caught_timestamp: int
    encounters: int
    encounter_method: str
    switch: int
    total_dens: int

    @classmethod
    def from_model(cls, c: CatchModel) -> CatchData:
        return cls(
            catch_name=c.name,
            caught_timestamp=c.caught_ts,
            encounters=c.encounters,
            encounter_method=c.encounter_method,
            switch=c.switch,
            total_dens=c.total_dens,
        )


@dataclass
class PokemonData:
    pokemon_id: str
    hunt_id: int
    encounters: int
    name: str
    switch_num: int
    targets: int
    started_hunt_ts: int
    total_dens: int
    catches: list[CatchData]
    fails: list[CatchData]

    @classmethod
    def from_model(cls, he: HuntEncounterModel, catches: list[CatchModel], fails: list[CatchModel]) -> PokemonData:
        return cls(
            pokemon_id=str(he.pokemon_id),
            hunt_id=he.hunt_id,
            encounters=he.encounters,
            name=he.pokemon_name,
            switch_num=he.switch,
            targets=he.targets,
            started_hunt_ts=he.started_ts,
            total_dens=he.total_dens,
            catches=[CatchData.from_model(c) for c in catches],
            fails=[CatchData.from_model(f) for f in fails],
        )

    def to_dict(self) -> dict:
        return {
            "pokemon_id": self.pokemon_id,
            "hunt_id": self.hunt_id,
            "encounters": self.encounters,
            "name": self.name,
            "switchNum": self.switch_num,
            "targets": self.targets,
            "started_hunt_ts": self.started_hunt_ts,
            "total_dens": self.total_dens,
            "catches": [asdict(c) for c in self.catches],
            "fails": [asdict(f) for f in self.fails],
        }


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------


def _build_pokemon_data(cursor: sqlite3.Cursor, row: tuple) -> PokemonData:
    he = HuntEncounterModel(row)
    cursor.execute(
        "SELECT * FROM catches WHERE hunt_id = ? AND name LIKE '%' || ? || '%'",
        (he.hunt_id, he.pokemon_name),
    )
    catches = [CatchModel(r) for r in cursor.fetchall()]
    cursor.execute(
        "SELECT * FROM fails WHERE hunt_id = ? AND name LIKE '%' || ? || '%'",
        (he.hunt_id, he.pokemon_name),
    )
    fails = [CatchModel(r) for r in cursor.fetchall()]
    return PokemonData.from_model(he, catches, fails)


def _fetch_all_pokemon(hunt_ids: tuple[int, int, int]) -> tuple[list[PokemonData], dict]:
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM hunt_encounters WHERE hunt_id = ? OR hunt_id = ? OR hunt_id = ?",
            hunt_ids,
        )
        pokemon_list = [_build_pokemon_data(cursor, row) for row in cursor.fetchall()]
        stats = _get_pokemon_stats(cursor)
        return pokemon_list, stats
    finally:
        conn.close()


def _get_hunt_ids() -> tuple[int, int, int] | None:
    if not STREAM_DATA_PATH.exists():
        return None
    with open(STREAM_DATA_PATH) as f:
        stream_data = json.load(f)
    return (
        stream_data["switch1Content"]["hunt_id"],
        stream_data["switch2Content"]["hunt_id"],
        stream_data["switch3Content"]["hunt_id"],
    )


def _get_pokemon_stats(cursor: sqlite3.Cursor) -> dict:
    def count(table, method):
        return cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE encounter_method = ?", (method,)).fetchone()[0]

    def total(method):
        return (
            cursor.execute(
                "SELECT SUM(encounters) FROM hunt_encounters WHERE encounter_method = ?", (method,)
            ).fetchone()[0]
            or 0
        )

    egg_shinies = count("catches", "egg")
    egg_total = total("egg")

    static_shinies = count("catches", "static")
    static_fails = count("fails", "static")
    static_total = total("static")

    wild_shinies = count("catches", "wild")
    wild_fails = count("fails", "wild")
    wild_total = total("wild")

    oldwild_shinies = count("catches", "oldwild")
    oldwild_fails = count("fails", "oldwild")
    oldwild_total = total("oldwild")

    da_shinies = cursor.execute(
        "SELECT COUNT(*) FROM catches WHERE encounters IS NOT NULL AND encounter_method = ?", ("da",)
    ).fetchone()[0]
    da_total = total("da")

    return {
        "totalEggShinies": egg_shinies,
        "totalEggs": egg_total,
        "averageEggs": egg_total / max(egg_shinies, 1),
        "totalStaticShinies": static_shinies,
        "totalStatic": static_total,
        "averageStatic": static_total / max(static_shinies + static_fails, 1),
        "totalWildShinies": wild_shinies,
        "totalWild": wild_total,
        "averageWild": wild_total / max(wild_shinies + wild_fails, 1),
        "totalOldWildShinies": oldwild_shinies,
        "totalOldWild": oldwild_total,
        "averageOldWild": oldwild_total / max(oldwild_shinies + oldwild_fails, 1),
        "totalDAShinies": da_shinies,
        "totalDA": da_total,
        "averageDA": da_total / max(da_shinies, 1),
    }


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------


def _compute_diff(pokemon_list: list[PokemonData]) -> list[PokemonData]:
    """Return only entries that changed since last emission, updating the cache."""
    changed = []
    for p in pokemon_list:
        key = (p.hunt_id, p.name)
        state = (p.encounters, len(p.catches), len(p.fails), p.total_dens)
        if _pokemon_cache.get(key) != state:
            changed.append(p)
            _pokemon_cache[key] = state
    return changed


# ---------------------------------------------------------------------------
# Emission
# ---------------------------------------------------------------------------


def emit_pokemon_data(*, full: bool = False) -> None:
    hunt_ids = _get_hunt_ids()
    if hunt_ids is None:
        return

    pokemon_list, stats = _fetch_all_pokemon(hunt_ids)

    if full:
        for p in pokemon_list:
            _pokemon_cache[(p.hunt_id, p.name)] = (p.encounters, len(p.catches), len(p.fails), p.total_dens)
        print("[WebSocket] Emitting full pokemon data")
        socketio.emit(
            "pokemon_data",
            {
                "pokemon": [p.to_dict() for p in pokemon_list],
                "pokemonStats": stats,
            },
        )
    else:
        changed = _compute_diff(pokemon_list)
        if not changed:
            return
        print(f"[WebSocket] Emitting {len(changed)} updated pokemon")
        socketio.emit(
            "pokemon_update",
            {
                "pokemon": [p.to_dict() for p in changed],
                "pokemonStats": stats,
            },
        )


# ---------------------------------------------------------------------------
# Background tasks
# ---------------------------------------------------------------------------


def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            try:
                if data.get("update_data", False):
                    emit_pokemon_data(full=False)
            except Exception as e:
                print(f"Error in redis_listener: {e}")


def watch_file():
    global stream_data_last_modified
    while True:
        try:
            if not STREAM_DATA_PATH.exists():
                time.sleep(2)
                continue
            mtime = os.path.getmtime(STREAM_DATA_PATH)
            if mtime != stream_data_last_modified:
                with open(STREAM_DATA_PATH) as f:
                    file_data = json.load(f)
                stream_data_last_modified = mtime
                print("[WebSocket] Emitting stream_data update")
                socketio.emit("stream_data", file_data)
        except Exception as e:
            print(f"Error in watch_file: {e}")
        time.sleep(2)


# ---------------------------------------------------------------------------
# Manager helpers
# ---------------------------------------------------------------------------


def _build_manager_status() -> list[dict]:
    state = script_manager._clean_state(script_manager._load_state())
    result = []
    for name, info in sorted(script_manager.REGISTRY.items()):
        entry = state.get(name)
        result.append({
            "name": name,
            "description": info["description"],
            "args_hint": info.get("args_hint", ""),
            "running": entry is not None,
            "pid": entry["pid"] if entry else None,
            "started": entry["started"] if entry else None,
        })
    return result


def _manager_start(name: str, args: list[str]) -> dict:
    if name not in script_manager.REGISTRY:
        return {"success": False, "error": f"Unknown script: {name}"}

    state = script_manager._load_state()
    entry = state.get(name)
    if entry and script_manager._is_running(entry["pid"]):
        return {"success": False, "error": f"'{name}' is already running (PID {entry['pid']})"}

    script_manager.LOGS_DIR.mkdir(exist_ok=True)
    log_path = script_manager.LOGS_DIR / f"{name.replace(':', '_')}.log"
    script_path = script_manager.SCRIPTS_DIR / script_manager.REGISTRY[name]["path"]
    cmd = [sys.executable, str(script_path)] + args

    with log_path.open("a") as log_file:
        log_file.write(f"\n{'='*60}\nStarted: {datetime.now().isoformat()}\nCmd: {' '.join(cmd)}\n{'='*60}\n")
        log_file.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(script_manager.SCRIPTS_DIR),
            stdout=log_file,
            stderr=log_file,
        )

    state[name] = {
        "pid": proc.pid,
        "log": str(log_path),
        "started": datetime.now().isoformat(),
    }
    script_manager._save_state(state)
    return {"success": True, "pid": proc.pid}


def _manager_stop(name: str) -> None:
    state = script_manager._load_state()
    names = list(state.keys()) if name == "all" else [name]

    for n in names:
        entry = state.get(n)
        if not entry:
            continue
        try:
            os.kill(entry["pid"], signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        del state[n]

    script_manager._save_state(state)


# ---------------------------------------------------------------------------
# Manager socket events
# ---------------------------------------------------------------------------

_last_manager_hash: str = ""


@socketio.on("manager_list")
def handle_manager_list():
    socketio.emit("manager_status", {"scripts": _build_manager_status()})


@socketio.on("manager_start")
def handle_manager_start(data):
    name = data.get("name", "")
    args = data.get("args", [])
    result = _manager_start(name, args)
    if not result["success"]:
        print(f"[manager_start] Error: {result['error']}")
    socketio.emit("manager_status", {"scripts": _build_manager_status()})


@socketio.on("manager_stop")
def handle_manager_stop(data):
    name = data.get("name", "")
    _manager_stop(name)
    socketio.emit("manager_status", {"scripts": _build_manager_status()})


@socketio.on("send_button")
def handle_send_button(data):
    switch_num = data.get("switch_num", 1)
    button = data.get("button", "A")
    duration = float(data.get("duration", 0.1))
    ser_str = get_switch_serial(switch_num)
    try:
        with serial.Serial(ser_str, 9600, timeout=1) as ser:
            press(ser, button, duration=duration)
        socketio.emit("button_result", {"success": True, "switch_num": switch_num, "button": button})
    except Exception as e:
        socketio.emit("button_result", {"success": False, "error": str(e), "switch_num": switch_num})


def watch_manager():
    global _last_manager_hash
    while True:
        try:
            scripts = _build_manager_status()
            h = str([(s["name"], s["running"], s["pid"]) for s in scripts])
            if h != _last_manager_hash:
                _last_manager_hash = h
                socketio.emit("manager_status", {"scripts": scripts})
        except Exception as e:
            print(f"Error in watch_manager: {e}")
        eventlet.sleep(3)


# ---------------------------------------------------------------------------
# Routes & socket events
# ---------------------------------------------------------------------------


@socketio.on("init_connect")
def handle_connect():
    try:
        if STREAM_DATA_PATH.exists():
            with open(STREAM_DATA_PATH) as f:
                stream_data = json.load(f)
            print("[WebSocket] Emitting init connect")
            socketio.emit("stream_data", stream_data)
            emit_pokemon_data(full=True)
        socketio.emit("manager_status", {"scripts": _build_manager_status()})
    except Exception as e:
        print(f"Error in handle_connect: {e}")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


# http://0.0.0.0:5050/
if __name__ == "__main__":
    socketio.start_background_task(target=redis_listener)
    socketio.start_background_task(target=watch_file)
    socketio.start_background_task(target=watch_manager)
    socketio.run(app, host="0.0.0.0", port=5050)
