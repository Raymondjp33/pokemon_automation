import os
import cv2
import numpy as np
import time


check_both = True
# check_both = False
check_num = 3
directory = "/Volumes/DexDrive/Current Hunt/"
# directory = "/Volumes/DexDrive/temp/"

bulb_colors = [[246, 176, 210]]
snorlax_colors = [[91, 110, 50], [79, 113, 48], [74, 113, 38]]
count = 0
ranges = {}


def check_images_for_pixel():
    global count
    global ranges

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
            print("Missing more than 100 encounters")
            return

        if missing:
            print(f"Missing encounters: {sorted(missing)}")
            user_input = input("Missing encounters found. Continue anyway? (y/n): ")
            if user_input.lower() != "y":
                return

    # Check for missing encounters
    if encountered_nums1:
        handle_encounter_misses(encountered_nums1)

    if encountered_nums3:
        handle_encounter_misses(encountered_nums3)

    ranges = {
        "max1": max(encountered_nums1) if encountered_nums1 else None,
        "min1": min(encountered_nums1) if encountered_nums1 else None,
        "max3": max(encountered_nums3) if encountered_nums3 else None,
        "min3": min(encountered_nums3) if encountered_nums3 else None,
    }

    # Second pass: process images
    for file in sorted(valid_files, key=lambda f: int(f.split("-")[2])):
        filename_parts = file.split("-")
        switch_num = filename_parts[0]
        encounter_num = int(filename_parts[2])

        path = os.path.join(directory, file)
        img = cv2.imread(path)
        if img is None:
            continue

        image_frame = img[101][157] if switch_num == "1" else img[240][944]
        rgb_list = bulb_colors if switch_num == "1" else snorlax_colors
        print(f"checking {path}: {image_frame}")
        count += 1

        if not any(np.array_equal(image_frame, rgb) for rgb in rgb_list):
            print(path)
            cv2.imshow("game2", img)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()
            if key == ord("0"):
                break


t0 = time.time()
check_images_for_pixel()
t1 = time.time()


delay = t1 - t0
print(f"Total time to check {count} images: {delay:.3f}s")
if ranges["min1"] is not None:
    print(f"Current ranges for 1: {ranges['min1']} - {ranges['max1']}")
if ranges["min3"] is not None:
    print(f"Current ranges for 3: {ranges['min3']} - {ranges['max3']}")

# 1
# 90762 - 150658
# 3
# 109507 - 141838
