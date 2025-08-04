from __future__ import annotations

import time

import cv2
import serial


from services.common import *
from services.config_manager import ConfigManager

config = ConfigManager(Path(__file__).resolve().parent / 'configs' / 'tera_raid_config.json')

def tera_available(vid: cv2.VideoCapture):
    frame = getframe(vid)
    terra_available_color = (253, 253, 253)
    if color_near(frame[642][820],terra_available_color):
        return True

    return False

def get_move_index(vid: cv2.VideoCapture):
    frame = getframe(vid)
    selected_move_color = (0, 235, 255)

    if color_near(frame[456][1115], selected_move_color):
        return 0
    if color_near(frame[530][1115], selected_move_color):
        return 1
    if color_near(frame[605][1115], selected_move_color):
        return 2
    
    return -1

def handle_battle(ser: serial.Serial, vid: cv2.VideoCapture):
    turn_index = config.get('turn_index')
    has_terrad = config.get('has_terrad')
    
    press(ser, 'A', sleep_time=0.75)
    move_index = get_move_index(vid)

    config.update({'turn_index': config.get('turn_index') + 1})

    if turn_index == 0:
        print('Using Focus Energy')
        press(ser, 's', count=2, sleep_time=0.3)
        press(ser, 'A', count=2, sleep_time=0.3)
        return
    
    if not has_terrad and tera_available(vid):
        print('Terastalizing')
        config.update({'has_terrad': True})
        press(ser, 'R', sleep_time=0.5)

    print('Using rage fist')
    move_distance = move_index - 0
    press(ser, 'w', count=move_distance, sleep_time=0.3)
    press(ser, 'A', count=2, sleep_time=0.3)

def get_current_screen(vid: cv2.VideoCapture):
    frame = getframe(vid)

    if (get_text(frame=frame, top_left=Point(y=530, x=1041), bottom_right=Point(y=566, x=1128), invert=True) == 'Battle'):
        print('Battling!')
        return 'Battling'
    

def main() -> int:
    ser_str = SWITCH3_SERIAL
    vid = make_vid(SWITCH3_VID_NUM)

    # start_time = time.time()
    # print(get_move_index(vid))
    # return

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)
        
        while True:
            screen = get_current_screen(vid)

            if screen == 'Battling':
                handle_battle(ser, vid)
            
            time.sleep(2)


    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
