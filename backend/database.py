from pathlib import Path
import sqlite3
import json

# Create (or open) the database file
conn = sqlite3.connect("my_pokemon.db")
cursor = conn.cursor()

data_path = Path(__file__).resolve().parent / 'offload.json'
with data_path.open() as file:
    data = json.load(file)

for pokemon in data['pokemon']:
    cursor.execute(
    "INSERT INTO pokemon (name, encounters_total, started_hunt_ts) VALUES (?, ?, ?)",
    (pokemon['pokemon'], pokemon['encounters'], pokemon.get('started_hunt_timestamp', None),)
    )
    pokemon_id = cursor.lastrowid

    # for catch in pokemon['catches']:
    cursor.execute(
        "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            pokemon_id,
            pokemon.get('caught_timestamp', 1740805200000),
            pokemon['encounters'],
            "dynamax_adventures",
            2,
            pokemon['pokemon'],
            pokemon['extra_data']['total_dens']
        )
    )


conn.commit()
conn.close()
