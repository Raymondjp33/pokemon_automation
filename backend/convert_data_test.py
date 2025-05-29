import json
from pathlib import Path

def convert_pokemon_data(old_data):
    new_data = {}

    new_data['pokemon'] = []

    for entry in old_data:
        new_entry = {
            "pokemon": entry.get("pokemon", "Unknown"),
            "encounters": entry.get("encounters", 0),
            "encounter_method": entry.get("encounter_method", "unknown"),
            "started_hunt_timestamp": entry.get("started_hunt_timestamp", None),
        }

        caught_timestamp = entry.get("caught_timestamp")
        encounters = entry.get("encounters")

        # Add optional fields if present
        if encounters is not None:
            new_entry["caught_timestamp"] = caught_timestamp
            new_entry["catches"] = [
                {
                    "caught_timestamp": caught_timestamp,
                    "encounters": encounters
                }
            ]
        else:
            new_entry["catches"] = []

        new_data['pokemon'].append(new_entry)

    return new_data

# Example usage:
input_path = Path("switch1_data.json")
output_path = Path("switch1_data_new.json")

# Load old data
with input_path.open("r", encoding="utf-8") as f:
    old_json = json.load(f)

# Convert
new_json = convert_pokemon_data(old_json['pokemon'])

# Save new data
with output_path.open("w", encoding="utf-8") as f:
    json.dump(new_json, f, indent=4)

print(f"Converted {len(new_json)} entries.")