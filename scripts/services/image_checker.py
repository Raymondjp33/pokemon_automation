import os
import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


check_both = True
# check_both = False
check_num = 3
# directory = "/Volumes/DexDrive/Current Hunt/"
directory = "/Volumes/DexDrive/Checked/snorlax/15 done/"
# directory = "/Volumes/DexDrive/Checked/bulbasaur/5 done/"
# directory = "/Volumes/DexDrive/temp/"

bulb_colors = [[246, 176, 210]]
snorlax_colors = [[91, 110, 50], [79, 113, 48], [74, 113, 38]]
count = 0
ranges = {}
PIXEL_THRESHOLD = 20
check_timestamps = True
TIMESTAMP_WINDOW = {"1": 42, "3": 30}  # seconds per switch


def pixel_matches_expected(pixel, expected_colors):
    return any(np.linalg.norm(pixel.astype(int) - np.array(rgb)) < PIXEL_THRESHOLD for rgb in expected_colors)


def check_single_file(file):
    filename_parts = file.split("-")
    switch_num = filename_parts[0]
    path = os.path.join(directory, file)
    img = cv2.imread(path)
    if img is None:
        return path, None
    image_frame = img[101][157] if switch_num == "1" else img[240][944]
    rgb_list = bulb_colors if switch_num == "1" else snorlax_colors
    if not pixel_matches_expected(image_frame, rgb_list):
        return path, img
    return path, None


def check_images_for_pixel():
    global count
    global ranges
    end_warnings = []

    # First pass: collect all encounter numbers
    encountered_nums1 = set()
    encountered_nums3 = set()
    valid_files = []

    for file in os.listdir(directory):
        if not file.lower().endswith(".png"):
            continue
        filename_parts = (file.split(".")[0]).split("-")

        if len(filename_parts) < 3:
            continue
        switch_num = filename_parts[0]
        # pokemon_name = filename_parts[1]

        encounter_num = int(filename_parts[2])
        # timestamp = int(filename_parts[3])

        if switch_num == "2":
            continue
        if not check_both and f"{check_num}" != switch_num:
            continue

        if switch_num == "1":
            encountered_nums1.add(encounter_num)
        elif switch_num == "3":
            encountered_nums3.add(encounter_num)
        valid_files.append(file)

    def handle_encounter_misses(encountered_nums):
        min_enc = min(encountered_nums)
        max_enc = max(encountered_nums)
        missing = set(range(min_enc, max_enc + 1)) - encountered_nums

        if len(missing) > 100:
            end_warnings.append("Missing more than 100 encounters")
            return

        if missing:
            end_warnings.append(f"Missing encounters: {sorted(missing)}")
            user_input = input("Missing encounters found. Continue anyway? (y/n): ")
            if user_input.lower() != "y":
                return

    # Check for missing encounters
    if encountered_nums1:
        handle_encounter_misses(encountered_nums1)

    if encountered_nums3:
        handle_encounter_misses(encountered_nums3)

    if check_timestamps:
        files_by_switch = {}
        for file in valid_files:
            parts = (file.split(".")[0]).split("-")
            sw = parts[0]
            enc_count = int(parts[2])
            timestamp = int(parts[3])
            files_by_switch.setdefault(sw, []).append((timestamp, enc_count))

        for sw, entries in files_by_switch.items():
            entries.sort()
            for i in range(1, len(entries)):
                prev_ts, prev_count = entries[i - 1]
                curr_ts, curr_count = entries[i]
                gap = (curr_ts - prev_ts) / 1000
                if gap > TIMESTAMP_WINDOW[sw]:
                    ts_str = datetime.fromtimestamp(curr_ts / 1000).strftime("%-I:%M %p %B %-d %Y")
                    end_warnings.append(f"{prev_count} - {curr_count} ~ {gap:.0f}s ({ts_str})")

    ranges = {
        "max1": max(encountered_nums1) if encountered_nums1 else None,
        "min1": min(encountered_nums1) if encountered_nums1 else None,
        "max3": max(encountered_nums3) if encountered_nums3 else None,
        "min3": min(encountered_nums3) if encountered_nums3 else None,
    }

    # Second pass: check pixels in parallel, then review flagged images
    sorted_files = sorted(valid_files, key=lambda f: int(f.split("-")[2]))
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(check_single_file, sorted_files))

    flagged = []
    for path, img in results:
        if path is not None:
            count += 1
        if img is not None:
            flagged.append((path, img))

    for path, img in flagged:
        print(path)
        cv2.imshow("game2", img)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()
        if key == ord("0"):
            break

    return end_warnings


t0 = time.time()
end_warnings = check_images_for_pixel()
t1 = time.time()


delay = t1 - t0
print(f"Total time to check {count} images: {delay:.3f}s")
if ranges["min1"] is not None:
    print(f"Current ranges for 1: {ranges['min1']} - {ranges['max1']}")
if ranges["min3"] is not None:
    print(f"Current ranges for 3: {ranges['min3']} - {ranges['max3']}")
if end_warnings:
    print("\n--- Warnings ---")
    for w in end_warnings:
        print(w)

# 1
# 90762 - 158018
# 3
# 109507 - 172201
