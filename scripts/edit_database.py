from services.common import *

# catches = run_db_query("SELECT * FROM catches", (), function='fetchall')


# for catch in catches:

#         catch_id = catch[0]
#         pokemon_id = catch[1]
#         caught_timestamp = catch[2]
#         encounters = catch[3]
#         encounter_method = catch[4]
#         switch = catch[5]
#         name = catch[6]
#         total_dens = catch[7]
#         hunt_id = catch[8]

#         encounters = run_db_query("SELECT * FROM hunt_encounters WHERE pokemon_id = ? AND hunt_id = ?", (pokemon_id, hunt_id,), function='fetchall')

#         for encounter in encounters:
#                 started_ts = encounter[7]

#                 if started_ts == None:
#                         continue

#                 if started_ts > caught_timestamp:
#                         print(catch)

#                         run_db_query("UPDATE hunt_encounters SET started_hunt_ts = ? WHERE id = ?", (None, encounter[0],))

        # hunt_encounters = 0
        # total_hunts = 0
        # encounter_exists = False
        # index = 0
        # for encounter in encounters:

        #         if (index > len(encounters) ):
        #                 break

        #         hunt_encounters = hunt_encounters + encounter[3]
        #         encounter_exists = True
        #         total_hunts = total_hunts + 1

        
        # if (total_encounters != hunt_encounters):
        #         print(f'\nhunt encounters {total_encounters}, encounters {encounter[3]}')
        #         print(f'Pokemon: {pokemon}')
        #         print(f'Encounter: {encounter}')

        #         # run_db_query("UPDATE hunt_encounters SET encounters = ? WHERE id = ?", (total_encounters - encounter[3], encounter[0],))

        # continue


        # user_input = input("> ").strip()
        # inputs = user_input.split(' ')
        # hunt_id = int(inputs[0])

        # # if total_hunts > 1 and total_encounters != hunt_encounters and encounter_exists:
        # #         print(f'\nPokemon: {pokemon}')

        # # print(catch)
        # # catch_id = catch[0]
        # # pokemon_id = catch[1]
        # # caught_timestamp = catch[2]
        # # encounters = catch[3]
        # # encounter_method = catch[4]
        # # switch = catch[5]
        # name = pokemon[1]
        # # total_dens = catch[7]

        # # pokemon = run_db_query("SELECT * FROM pokemon WHERE name = ?", (name,),function= "fetchone")

        # hunt_encounter = run_db_query("SELECT * FROM hunt_encounters WHERE pokemon_id = ? AND encounter_method = ?", (pokemon_id, 'egg',), function='fetchone')
        # new_hunt = hunt_encounter == None
        # print(hunt_id)

        # if new_hunt:
        #         pokemon = run_db_query("SELECT * FROM pokemon WHERE name = ?", (name,), function='fetchone')
        #         run_db_query(
        #         "INSERT INTO hunt_encounters (pokemon_id, hunt_id, encounters, pokemon_name, switch, targets, started_hunt_ts, encounter_method, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        #         (pokemon[0], hunt_id, total_encounters, name, 2, 1, started_ts, '', None, ))
        #         print(f'Added hunt {hunt_id}')
        # # else:
        # #         hunt_id = hunt_encounter[2]
        # #         run_db_query("UPDATE hunt_encounters SET encounters = ? WHERE hunt_id = ? AND pokemon_id = ?", (hunt_encounter[3] + encounters, hunt_id, pokemon_id))
        # #         run_db_query("UPDATE hunt_encounters SET targets = ? WHERE hunt_id = ? AND pokemon_id = ?", (hunt_encounter[6] + 1, hunt_id, pokemon_id))
        # #         print(f'Updates hunt {hunt_id}')

        # run_db_query("UPDATE pokemon SET started_hunt_ms = ? WHERE id = ?", (None, pokemon_id,))


###
###             Models
###

# pokemon_id = pokemon[0]
# pokemon_name = pokemon[1]
# total_encounters = pokemon[2]
# started_ts = pokemon[3]

# catch_id = catch[0]
# pokemon_id = catch[1]
# caught_timestamp = catch[2]
# encounters = catch[3]
# encounter_method = catch[4]
# switch = catch[5]
# name = catch[6]
# total_dens = catch[7]
# hunt_id = catch[8]

# encounter_id = hunt[0]
# pokemon_id = hunt[1]
# hunt_id = hunt[2]
# encoutners = hunt[3]
# pokemon_name = hunt[4]
# switch = hunt[5]
# targets = hunt[6]
# started_ts = hunt[7]
# encounter_method = hunt[8]
# total_dens = hunt[9]

###
###             ADD NEW CATCH
###

# pokemon = run_db_query("SELECT * FROM pokemon WHERE name = ?", ('regirock',),function= "fetchone")

# pokemon_id = pokemon[0]
# caught_timestamp = int(time.time() * 1000)
# encounters = 20325
# encounter_method = 'static'
# switch = 2
# name = 'regirock'
# total_dens = None
# hunt_id = 4


# run_db_query(
#             "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
#             ( pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id))

###
###             ADD NEW HUNT
###

# pokemon_name = 'unown'
# targets = 1
# hunt_id = run_db_query("SELECT MAX(hunt_id) FROM hunt_encounters", (), function='fetchone')[0] + 1
# encounter_method = 'static'
# switch = 1
# total_dens = None
# encounters = 0

# pokemon = run_db_query("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,),function= "fetchone")
# run_db_query(
# "INSERT INTO hunt_encounters (pokemon_id, hunt_id, encounters, pokemon_name, switch, targets, started_hunt_ts, encounter_method, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
# (pokemon[0], hunt_id, encounters, pokemon_name, switch, targets, int(time.time() * 1000), encounter_method, total_dens, ))
# print(f'Added hunt {hunt_id}')

###
###             OTHER USEFUL FUNCTIONS
###


# data_path = Path(__file__).resolve().parent / 'offload.json'
# with data_path.open() as file:
#     data = json.load(file)

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS hunt_encounters (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         pokemon_id INTEGER,
#         hunt_id INTEGER,
#         encounters INTEGER
# );
# """)
   
# cursor.execute("""
#         ALTER TABLE hunt_encounters
#         ADD total_dens INTEGER;
#  """)

# user_input = input("> ").strip()
# inputs = user_input.split(' ')
# hunt_id = int(inputs[0])