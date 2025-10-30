from pathlib import Path
import sqlite3
import json
import time
import csv

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
# ("Mamoswine", 0, int(time.time() * 1000))
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
# CREATE TABLE IF NOT EXISTS hunt_encounters (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         pokemon_id INTEGER,
#         hunt_id INTEGER,
#         encounters INTEGER
# );
# """)

# res = cursor.execute("SELECT encounters, COUNT(*) FROM hunt_encounters WHERE hunt_id = ?", (1,)).fetchone()[0]

# res = cursor.execute("SELECT AVG(encounters) FROM catches WHERE encounter_method = ?", ('egg',)).fetchone()[0]
# print(res)

# cursor.execute("SELECT * FROM pokemon")
# all_pokemon = cursor.fetchall()

# for pokemon in all_pokemon:
#         cursor.execute("UPDATE temppokemon SET total_encounters = ? WHERE id = ?", (pokemon[2], pokemon[4]))

        # pokemon_catches = cursor.fetchall()

        # for catch in pokemon_catches:

        #         if catch[4] == 'route':
        #                 cursor.execute("UPDATE catches set encounter_method = ? WHERE id = ?", ('wild', catch[0],))
        
        
# cursor.execute("""
#         ALTER TABLE hunt_encounters
#         ADD total_dens INTEGER;
#  """)

# with open(Path(__file__).resolve().parent.parent / 'scripts' / 'configs' / 'pokemon.csv', mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#                 name = row['identifier'].strip().lower()  # Normalize name
#                 species_id = int(row['species_id'])

#                 gif_number = species_id - 1

#                 if (gif_number > 801):
#                         gif_number = gif_number + 18

#                 if (gif_number > 907):
#                         gif_number = gif_number + 14

#                 print(name)
#                 cursor.execute(
#                 "INSERT INTO temppokemon (id, name, total_encounters, gif_number) VALUES (?, ?, ?, ?)",
#                 (
#                 species_id,
#                 name,
#                 0,
#                 gif_number,
#                 )
#         )
# cursor.execute(
# "INSERT INTO hunts (started_hunt_ts, switch) VALUES (?, ?)",
# (
# 1761706800000,
# 2,
# )
# )
# print(cursor.execute("SELECT * FROM hunt_encounters WHERE hunt_id = ?", (2,)).fetchone())
# cursor.execute(
# "INSERT INTO hunt_encounters (pokemon_id, hunt_id, encounters, pokemon_name, switch, targets, started_hunt_ts, encounter_method, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
# (
# 403,
# 2,
# 0,
# 'shinx',
# 1,
# 2,
# int(time.time() * 1000),
# 'egg',
# None
# )
# )

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
