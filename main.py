import curses
import time
from api_utils import fetch_text_from_api
from progress_utils import (
    save_progress,
    load_completed_race_results,
    compute_user_progress_stats
)

api_url = "https://favqs.com/api/qotd"


def display_user_progress(stdscr, user_progress):
    stdscr.addstr("\nUser Progress:\n")
    stdscr.addstr(f"  • Avg Speed (Last 10 races): {user_progress['avg_speed_last_10_races']} WPM\n")
    stdscr.addstr(f"  • Avg Speed (All time):      {user_progress['avg_speed_all_time']} WPM\n")
    stdscr.addstr(f"  • Last Race Speed:           {user_progress['last_race_speed']} WPM\n")
    stdscr.addstr(f"  • Best Race Speed:           {user_progress['best_race_speed']} WPM\n")
    stdscr.addstr(f"  • Races Completed:           {user_progress['races_completed']}\n")


def display_recent_results(stdscr, recent_results):
    if recent_results:
        stdscr.addstr("\nLast 10 Completed Races:\n")
        stdscr.addstr("No.  Time\t\t\tWPM\tAccuracy\n")
        for idx, row in enumerate(recent_results, start=1):
            timestamp, wpm, accuracy, status = row
            stdscr.addstr(f"{idx:>2}.  {timestamp}\t{wpm}\t{accuracy}%\n")
    else:
        stdscr.addstr("\nNo completed races found.\n")


def render_home_screen(stdscr):
    stdscr.clear()
    stdscr.addstr("Welcome to the Speed Typing Test!\n")

    recent_results = load_completed_race_results()
    user_progress = compute_user_progress_stats()
    display_user_progress(stdscr, user_progress)
    display_recent_results(stdscr, recent_results)

    stdscr.addstr("\nPress SPACE to begin or ESC to exit...\n")
    stdscr.refresh()



def start_screen(stdscr):
    while True:
        render_home_screen(stdscr)
        key = stdscr.getkey()
        if key == " ":
            wpm_test(stdscr)
        elif key == chr(27):  
            break


def display_text(stdscr, target, current, wpm=0, accuracy=0):
    stdscr.addstr(0, 0, f"WPM: {wpm} | Accuracy: {accuracy}%")

    h, w = stdscr.getmaxyx()

    for idx, char in enumerate(target):
        row = 2 + (idx // w)
        col = idx % w
        if row < h - 1:
            if len(char) > 1:
                char = char[0] 
            stdscr.addch(row, col, char)

    for idx, char in enumerate(current):
        row = 2 + (idx // w)
        col = idx % w
        if row < h - 1:
            correct_char = target[idx]
            color = curses.color_pair(1) if char == correct_char else curses.color_pair(2)
            if len(char) > 1:
                char = char[0]  
            stdscr.addch(row, col, char, color)


def wpm_test(stdscr):
    stdscr.clear()
    stdscr.addstr("Loading quote...\n")
    stdscr.refresh()

    target_text = fetch_text_from_api(api_url)
    current_text = []

    wpm = 0
    accuracy = 0
    total_keystrokes = 0
    correct_keystrokes = 0
    start_time = time.time()

    stdscr.nodelay(True)

    while True:        
        time_elapsed = max(time.time() - start_time, 1)
        cpm = len(current_text) / (time_elapsed / 60)
        wpm = round(cpm / 5)

        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm, accuracy)
        stdscr.refresh()

        if "".join(current_text) == target_text:
            save_progress(wpm, accuracy, "COMPLETED")
            stdscr.nodelay(False)
            return

        try:
            key = stdscr.getkey()
        except:
            continue

        if key == chr(27): 
            save_progress(wpm, accuracy, "INCOMPLETE")
            stdscr.nodelay(False)
            return

        total_keystrokes += 1

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if current_text:
                current_text.pop()
        elif len(current_text) < len(target_text):
            current_text.append(key)
            if key == target_text[len(current_text) - 1]:
                correct_keystrokes += 1

        accuracy = round((correct_keystrokes / total_keystrokes) * 100) if total_keystrokes else 0


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK) 

    start_screen(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
