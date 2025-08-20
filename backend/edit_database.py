from pathlib import Path
import sqlite3
import json
import time

# Create (or open) the database file
conn = sqlite3.connect("my_pokemon.db")
cursor = conn.cursor()

# data_path = Path(__file__).resolve().parent / 'offload.json'
# with data_path.open() as file:
#     data = json.load(file)

# for pokemon in data['pokemon']:
#     cursor.execute(
#     "INSERT INTO pokemon (name, encounters_total, started_hunt_ts) VALUES (?, ?, ?)",
#     (pokemon['pokemon'], pokemon['encounters'], pokemon.get('started_hunt_timestamp', None),)
#     )
#     pokemon_id = cursor.lastrowid

#     for catch in pokemon['catches']:
#         cursor.execute(
#             "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
#             (
#                 pokemon_id,
#                 catch.get('caught_timestamp', 1740805200000),
#                 pokemon['encounters'],
#                 "wild",
#                 2,
#                 pokemon['pokemon'],
#                 pokemon.get('extra_data', {}).get('total_dens', None)
        #     )
        # )

# cursor.execute(
# "INSERT INTO pokemon (name, encounters_total, started_hunt_ts) VALUES (?, ?, ?)",
# ("Chinchou", 0, int(time.time() * 1000))
# )

# pokemon_name = 'Swablu'
# cursor.execute("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,))
# pokemon_row = cursor.fetchone()

# cursor.execute("SELECT SUM(encounters) FROM catches WHERE name = ?", (pokemon_name,))
# result = cursor.fetchone()[0]
# previous_encounters = result if result is not None else 0
# count_difference = pokemon_row[2] - previous_encounters
# cursor.execute(
#         "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
#         (
#         pokemon_row[0],
#         int(time.time() * 1000),
#         count_difference,
#         "route",
#         2,
#         pokemon_name,
#         None
#         )
# )

# cursor.execute("SELECT SUM(encounters) FROM catches WHERE name = ?", ('Bellsprout',))
# result = cursor.fetchone()[0]
# previous_encounters = result if result is not None else 0
# print(previous_encounters)

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS tempmons (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     encounters INTEGER DEFAULT 0
# );
# """)

# cursor.execute("""
#     CREATE UNIQUE INDEX IF NOT EXISTS idx_pokemon_name
#     ON tempmons (name);
# """)

# cursor.execute(
# "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
# (
# 74,
# int(time.time() * 1000),
# 318,
# "egg",
# 1,
# pokemon_name,
# None
# )
# )

conn.commit()
conn.close()
