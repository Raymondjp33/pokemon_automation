from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import eventlet
import eventlet.hubs

eventlet.hubs.use_hub("poll")
eventlet.monkey_patch()

from flask import Flask, send_from_directory  # noqa: E402
from flask_socketio import SocketIO  # noqa: E402
import redis  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from services.common import (  # noqa: E402
    REDIS_CHANNEL,
    STREAM_DATA_PATH,
    DB_FILE,
    CatchModel,
    HuntEncounterModel,
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
    conn = sqlite3.connect(str(DB_FILE))
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
# Routes & socket events
# ---------------------------------------------------------------------------


@socketio.on("init_connect")
def handle_connect():
    try:
        if not STREAM_DATA_PATH.exists():
            return
        with open(STREAM_DATA_PATH) as f:
            stream_data = json.load(f)
        print("[WebSocket] Emitting init connect")
        socketio.emit("stream_data", stream_data)
        emit_pokemon_data(full=True)
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
    socketio.run(app, host="0.0.0.0", port=5050)
