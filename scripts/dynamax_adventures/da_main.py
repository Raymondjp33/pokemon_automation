from __future__ import annotations

import time

import cv2
from pathlib import Path
import serial
from .battle_handler import BattleHandler
from .den_handler import DenHandler
from services.config_manager import ConfigManager

from services.common import SWITCH2_VID_NUM, SWITCH2_SERIAL, make_vid, shh, press, getframe, get_text, Point


def get_screen(vid: cv2.VideoCapture):
    frame = getframe(vid)

    if get_text(frame=frame, top_left=Point(y=502, x=1056), bottom_right=Point(y=539, x=1133), invert=True) == "Fight":
        return "Fight"

    if (
        get_text(frame=frame, top_left=Point(y=46, x=26), bottom_right=Point(y=86, x=298), invert=True)
        == "One Trainer can choose"
    ):
        return "Swapping"

    if (
        get_text(frame=frame, top_left=Point(y=163, x=691), bottom_right=Point(y=198, x=1223), invert=True)
        == "Choose the one Pokémon you'd like to keep!"
    ):
        return "Choosing"

    if get_text(frame=frame, top_left=Point(y=609, x=1091), bottom_right=Point(y=643, x=1205), invert=True) == "Catch":
        return "Catching"

    if (
        get_text(frame=frame, top_left=Point(y=46, x=21), bottom_right=Point(y=85, x=238), invert=True)
        == "Everyone will take"
    ):
        return "Selecting"

    if (
        get_text(frame=frame, top_left=Point(y=500, x=1053), bottom_right=Point(y=541, x=1182), invert=True)
        == "Cheer On"
    ):
        return "Cheer On"

    if get_text(frame=frame, top_left=Point(y=590, x=565), bottom_right=Point(y=642, x=689), invert=True) == "letdown":
        return "Let down"

    if (
        get_text(frame=frame, top_left=Point(y=587, x=356), bottom_right=Point(y=626, x=493), invert=True)
        == "Which path"
    ):
        return "Pathing"

    if get_text(frame=frame, top_left=Point(y=51, x=344), bottom_right=Point(y=105, x=454), invert=True) == "hold one":
        return "Items"

    if get_text(frame=frame, top_left=Point(y=626, x=600), bottom_right=Point(y=667, x=674), invert=True) == "rental":
        return "Rental"

    if (
        get_text(frame=frame, top_left=Point(y=242, x=245), bottom_right=Point(y=294, x=562), invert=True)
        == "Play is being suspended."
    ):
        return "Sus"


def main() -> int:
    ser_str = SWITCH2_SERIAL
    vid = make_vid(SWITCH2_VID_NUM)

    shiny_legend = False

    config = ConfigManager(Path(__file__).resolve().parent / "den_config.json")

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)

        battle_handler = BattleHandler(vid, ser)
        den_handler = DenHandler(vid, ser)
        # go_to_change_grip(ser)
        # connect_and_go_to_game(ser)
        # handle_choose_pokemon()
        # take_pokemon(ser)
        # restart_dungeon(vid, ser)
        # select_starter(vid, ser)
        # handle_choose_pokemon(vid, ser)
        # return 0

        while not shiny_legend:
            screen = get_screen(vid)

            if screen == "Fight":
                battle_handler.handle_fight()

            if screen == "Swapping":
                den_handler.swap_if_needed()

            if screen == "Catching":
                config.update({"move_index": 0, "battle_index": config.get("battle_index") + 1, "dynamax_turns": None})
                den_handler.handle_catch(is_legend=config.get("battle_index") == 4)

            if screen == "Selecting":
                den_handler.select_starter()

            if screen == "Choosing":
                shiny_legend = den_handler.handle_choose_pokemon()

                if shiny_legend:
                    break

                den_handler.restart_dungeon(keep_dungeon=config.get("keep_dungeon"))
                # return 0

            if screen == "Cheer On":
                if config.get("dynamax_turns") is not None:
                    config.update({"dynamax_turns": -1})
                print("Cheering")
                press(ser, "A")

            if screen == "Let down":
                print("Handling let down")
                den_handler.restart_dungeon(keep_dungeon=config.get("keep_dungeon"))

            if screen == "Pathing":
                den_handler.handle_pathing()

            if screen == "Items":
                den_handler.handle_select_item()

            if screen == "Rental":
                den_handler.handle_rental()

            if screen == "Sus":
                den_handler.handle_sus()

            time.sleep(5)

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
