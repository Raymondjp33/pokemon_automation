import os
import cv2
import numpy as np


check_both = True
# check_both = False
check_num = 3
# directory = "/Volumes/DexDrive/Current Hunt/"
directory = "/Volumes/DexDrive/temp/"

bulb_colors = [[246, 176, 210]]
snorlax_colors = [[91, 110, 50], [79, 113, 48], [74, 113, 38]]


def check_images_for_pixel():
    for file in os.listdir(directory):
        if not file.lower().endswith(".png"):
            continue

        filename_parts = file.split("-")
        switch_num = filename_parts[0]
        # timestamp = int(filename_parts[2])

        if switch_num == "2":
            continue

        if not check_both and f"{check_num}" != switch_num:
            continue

        path = os.path.join(directory, file)
        img = cv2.imread(path)

        if img is None:
            continue

        image_frame = img[101][157] if switch_num == "1" else img[240][944]
        rgb_list = bulb_colors if switch_num == "1" else snorlax_colors
        print(f"checking {path}: {image_frame}")
        if not any(np.array_equal(image_frame, rgb) for rgb in rgb_list):
            print(path)
            cv2.imshow("game2", img)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()

            if key == ord("0"):
                break


check_images_for_pixel()
