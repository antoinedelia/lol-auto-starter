import time
import pyautogui
from enum import Enum
from notification import send_pushingbox_notification

BUTTON_PATH = "img/button/"
PHASE_PATH = "img/phase/"
CHAMPION_PATH = "img/champion/"
INFO_PATH = "img/info/"


class State(Enum):
    IN_LAUNCHER = 0
    GAME_SETUP = 1
    GAME_FOUND = 2
    CHAMPION_DECLARATION = 3
    BAN_CHAMPION_SELECTION = 4
    CHAMPION_SELECION = 5
    OTHER = 6


class Lane(Enum):
    BOTTOM = f"{INFO_PATH}/lane_bottom.png"
    MIDDLE = f"{INFO_PATH}/lane_middle.png"
    TOP = f"{INFO_PATH}/lane_top.png"
    JUNGLE = f"{INFO_PATH}/lane_jungle.png"
    SUPPORT = f"{INFO_PATH}/lane_support.png"


class Champion(Enum):
    GAREN = "Garen"
    EZREAL = "Ezreal"


CHAMPIONS_ORDER = {
    Lane.TOP: [
        Champion.GAREN,
    ],
    Lane.BOTTOM: [
        Champion.EZREAL,
    ]
}

CURRENT_LANE = None
CURRENT_STATE = None
NO_EVENT_FOUND_COUNT = 0


def get_current_state() -> State:
    # Phases of the lobby
    in_lobby = pyautogui.locateCenterOnScreen(f"{BUTTON_PATH}play.png", confidence=0.7)
    if in_lobby:
        return State.IN_LAUNCHER

    find_match_available = pyautogui.locateCenterOnScreen(f"{BUTTON_PATH}find_match.png", confidence=0.7)
    if find_match_available:
        return State.GAME_SETUP

    match_found = pyautogui.locateCenterOnScreen(f"{BUTTON_PATH}accept.png", confidence=0.7)
    if match_found:
        return State.GAME_FOUND

    # Phases of the game
    declare_phase = pyautogui.locateCenterOnScreen(f"{PHASE_PATH}declare.png", confidence=0.7)
    if declare_phase:
        return State.CHAMPION_DECLARATION

    ban_phase = pyautogui.locateCenterOnScreen(f"{PHASE_PATH}ban.png", confidence=0.7)
    if ban_phase:
        return State.BAN_CHAMPION_SELECTION

    choose_phase = pyautogui.locateCenterOnScreen(f"{PHASE_PATH}choose.png", confidence=0.7)
    if choose_phase:
        return State.CHAMPION_SELECION

    return State.OTHER


def get_champion_to_choose(lane: Lane) -> Champion:
    for champion in CHAMPIONS_ORDER[lane]:
        if pyautogui.locateOnScreen(f"{CHAMPION_PATH}{champion.value}.png", confidence=0.7):
            return champion


def get_lane() -> Lane:
    for lane in Lane:
        if pyautogui.locateOnScreen(lane.value, confidence=0.7):
            return lane


def move_and_click(image_path: str, clicks: int = 1, interval: float = 0.1, sleep: int = 1):
    coords = pyautogui.locateCenterOnScreen(image_path, confidence=0.7)
    pyautogui.click(coords, clicks=clicks, interval=interval)
    time.sleep(sleep)


def setup_game():
    # Click the play button
    move_and_click(f"{BUTTON_PATH}play.png")

    # Select the correct mode and validate
    move_and_click(f"{BUTTON_PATH}ranked.png")
    move_and_click(f"{BUTTON_PATH}confirm.png")

    # Choose the lanes
    move_and_click(f"{BUTTON_PATH}lane_selection.png")
    move_and_click(f"{BUTTON_PATH}bottom_lane.png")
    move_and_click(f"{BUTTON_PATH}lane_selection.png")
    move_and_click(f"{BUTTON_PATH}top_lane.png")


while True:
    CURRENT_STATE = get_current_state()

    if CURRENT_STATE == State.OTHER:
        NO_EVENT_FOUND_COUNT += 1
        print(f"No event is found. Iteration: {NO_EVENT_FOUND_COUNT}. \r", end="")
        continue
    else:
        NO_EVENT_FOUND_COUNT = 0

    if CURRENT_STATE == State.IN_LAUNCHER:
        print("Currently in lobby. Setting up game.")
        setup_game()
    elif CURRENT_STATE == State.GAME_SETUP:
        print("Game is setup. Trying to find a match...")
        move_and_click(f"{BUTTON_PATH}find_match.png")
    elif CURRENT_STATE == State.GAME_FOUND:
        print("Match found! Accepting it.")
        move_and_click(f"{BUTTON_PATH}accept.png")
    elif CURRENT_STATE == State.CHAMPION_DECLARATION:
        # TODO Check which lane we are in and choose the champion accordingly
        CURRENT_LANE = get_lane()
        champion_to_choose = get_champion_to_choose(CURRENT_LANE)
        print(f"Declaring champion {champion_to_choose}")
        move_and_click(f"{CHAMPION_PATH}{champion_to_choose.value}.png")
    elif CURRENT_STATE == State.BAN_CHAMPION_SELECTION:
        # TODO Ban someone else if the champion is selected by a teammate
        print("Banning a champion.")
        move_and_click(f"{CHAMPION_PATH}blitzcrank.png")
        move_and_click(f"{BUTTON_PATH}ban.png")
    elif CURRENT_STATE == State.CHAMPION_SELECION:
        # TODO Choose someone else if the champion is selected by a enemy or is banned
        can_lock = pyautogui.locateCenterOnScreen(f"{PHASE_PATH}lock_in.png", confidence=0.7)
        if not can_lock:
            print("Already locked champion.")
            continue

        champion_to_choose = get_champion_to_choose(CURRENT_LANE)
        print(f"Choosing champion {champion_to_choose}")
        move_and_click(f"{CHAMPION_PATH}{champion_to_choose.value}.png")
        move_and_click(f"{BUTTON_PATH}lock_in.png")

        send_pushingbox_notification("Your League of Legends game is ready!")
