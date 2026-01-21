from __future__ import annotations

import time

import cv2
import serial
import re
import os
import numpy as np

import redis

from services.common import *

reset_counter_path = '/Users/raymondprice/Desktop/other/test_coding/pokemon_scripts/pokemon_automation/scripts/configs/bench_counter.txt'

def detect_color_square(vid, count):

    show_vid = False
    min_detection_frames = 75
    detection_window = 5
    target_colors = [(219, 172, 41), (193, 144, 13), (137, 76, 9),]
    
    tolerance = 10
    square_size = 10
    any_color_history = 0
    
    # Track if any color has been consistently detected
    color_confirmed = False

    frame = getframe(vid)
    cv2.imwrite(f"/Volumes/DexDrive/hunt/{count}.png", frame)
    
    start_time = time.time()
    while time.time() - start_time < detection_window:
        frame = getframe(vid)
        
        
        # Process each target color
        for target_color in target_colors:
                
            # Create upper and lower bounds for color detection
            lower_bound = np.array([max(0, c - tolerance) for c in target_color])
            upper_bound = np.array([min(255, c + tolerance) for c in target_color])
            
            # Create a mask for the target color
            mask = cv2.inRange(frame, lower_bound, upper_bound)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process the contours
            for contour in contours:
                # Get the bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if the contour is approximately the expected size
                if abs(w - square_size) < 5 and abs(h - square_size) < 5:
                    # Mark that we found at least one color in this frame
                    any_color_history += 1
                    # Draw a rectangle around the detected color square
                    cv2.rectangle(frame, (x, y), (x + w, y + h), 
                                 (0, 255, 0) if color_confirmed else (0, 0, 255), 2)
                    break
        
        # Check if any color is consistently detected
        if any_color_history >= min_detection_frames:
            return True
        
        # Display status
        if show_vid:
            status = "COLOR DETECTED" if color_confirmed else f"Detecting ({any_color_history}/{min_detection_frames})"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0) if color_confirmed else (0, 0, 255), 2)
            
            # Display the frame
            cv2.imshow("Color Detection", frame)
            
            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    return False

def update_reset_counter(reset = False):
    if not os.path.exists(reset_counter_path):
        print(f"File not found: {reset_counter_path}")
        return None
    
    try:
        with open(reset_counter_path, 'r') as file:
            content = file.read()
        
        match = re.search(r'Current resets: (\d+)', content)
        if not match:
            print("Could not find 'Current resets: X' pattern in the file")
            return None
        
        current_value = int(match.group(1))
        new_value = current_value + 1

        if (reset):
            new_value = 0
        
        new_content = re.sub(r'Current resets: \d+', f'Current resets: {new_value}', content)
        
        with open(reset_counter_path, 'w') as file:
            file.write(new_content)
        
        return new_value
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def restart_game(ser):
    press(ser, 'H', sleep_time=1.5)
    press(ser, 'X', sleep_time=1.3)
    press(ser, 'A', sleep_time=1.3)
    press(ser, 'A', sleep_time=1, count=2)
    time.sleep(13)
    press(ser, 'A', sleep_time=7)


def main() -> int:
    ser_str = SWITCH3_SERIAL
    vid = make_vid(SWITCH3_VID_NUM)

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)

        while True:
            
            ## Walk in then tp, zone 2
            # press(ser, 'A', sleep_time=2)
            # press(ser, 'w', duration=2.5)
            # press(ser, 'B', sleep_time=1)
            # press(ser, 'A')
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(5)

            ## Battles
            # press(ser, 'l', duration=0.5, write_null_byte=False)
            # press(ser, 'A', sleep_time=0.5, count=3)

            ## Bench
            # press(ser, 'a', duration=0.75)
            # press(ser, 'd', duration=0.5)
            # press(ser, 'w', duration=2)
            # press(ser, 's', duration=2.3)
            # press(ser, 'd', duration=2.5)
            # press(ser, 'a', duration=2.5)
            # press(ser, 's')
            # press(ser, 'A', sleep_time=0.5, count=7)
            # time.sleep(20)

            # press(ser, 's')
            # press(ser, 'A', sleep_time=0.5, count=7)
            # time.sleep(20)

            ## Teleporter
            # press(ser, 'A', sleep_time=4)
            # press(ser, 'A', sleep_time=4)
           
            ## Zone 20 charmander specific
            # press(ser, 'q', duration=0.2, write_null_byte=False)
            # press(ser, 'B', duration=0.03, write_null_byte=False)
            # press(ser, 'q', duration=6, write_null_byte=False)
            # press(ser, 'B')
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'd', duration=0.05)
            # press(ser, 'A', sleep_time=0.5, count=4)
            # press(ser, 'd')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(3.5)

            ## Walk into zone then TP
            # press(ser, 'w', duration=1.5)
            # press(ser, 'B')
            # # press(ser, 'A', sleep_time=3)
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'a')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(4)

            ## Zone tp (7)
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'a')
            # press(ser, 'w')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # press(ser, 'B')
            # time.sleep(4)

            ## Zone 3
            # press(ser, 's', duration=1, sleep_time=3)
            # press(ser, 's', duration=0.3)
            # press(ser, 'A', sleep_time=2)
            # press(ser, 's', duration=0.3)
            # press(ser, 'A', sleep_time=2)

            ## Sewers
            # press(ser, 'w', duration=0.2, write_null_byte=False)
            # press(ser, 'B', duration=0.03, write_null_byte=False)
            # press(ser, 'w', duration=4.25, write_null_byte=False)
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 's', duration=1.25)
            # press(ser, 'A', count=3, sleep_time=0.50)
            # time.sleep(3)


            ## Unspecific
            # update_reset_counter()
            # end_time = time.time()
            # print(f'Full run took {(end_time-start_time):.3f}s')
            # press(ser, 'A')

            ## Legends DLC
            restart_game(ser)
            press(ser, 'A', sleep_time=4)
            press(ser, 'j', duration=0.3)   
            count = update_reset_counter()

            if not detect_color_square(vid, count):
                break
        
        print('SHINYYY')
        press(ser, 'H', sleep_time=2)
        press(ser, 'H', duration=1.5)
        press(ser, 'A')

    # vid.release()
    # cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
