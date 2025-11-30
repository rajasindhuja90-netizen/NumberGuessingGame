# cartoon_guess_full.py
"""
Cartoon Number Guessing Game — Full Console Version
Features:
 - Cross-platform sound (pygame preferred, winsound fallback on Windows)
 - Cute Cartoon Sound Pack (place sound files in assets/sounds/)
 - Levels: Easy / Medium / Hard
 - Character selection (Cat, Robot, Panda, Dino)
 - Hints (3 per game): range hint, parity/divisibility, +/-5 proximity
 - ASCII UI menu
 - Leaderboard saved in leaderboard.json (Top 10 sorted by score, then time)
 - Works on Windows / Mac / Linux / Android (Pydroid or Termux)
"""

import random, time, os, sys, json, platform
from datetime import datetime

# -------------------------
# Config / Assets location
# -------------------------
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
LEADERBOARD_FILE = os.path.join(ASSETS_DIR, "leaderboard.json")

# Ensure assets dir exists
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# -------------------------
# Sound handling
# -------------------------
SOUND_FILES = {
    'pop': os.path.join(SOUNDS_DIR, 'pop.wav'),
    'win': os.path.join(SOUNDS_DIR, 'win.wav'),
    'lose': os.path.join(SOUNDS_DIR, 'lose.wav'),
    'hint': os.path.join(SOUNDS_DIR, 'hint.wav'),
    'start': os.path.join(SOUNDS_DIR, 'start.wav')
}

# Try pygame, else winsound (Windows), else silent
SOUND_BACKEND = None
try:
    import pygame
    pygame.mixer.init()
    SOUND_BACKEND = 'pygame'
except Exception:
    if platform.system() == "Windows":
        try:
            import winsound
            SOUND_BACKEND = 'winsound'
        except Exception:
            SOUND_BACKEND = None
    else:
        SOUND_BACKEND = None  # no sound backend

def play_sound(key):
    """Play a short sound if available and backend present."""
    path = SOUND_FILES.get(key)
    if not path or not os.path.exists(path):
        return
    try:
        if SOUND_BACKEND == 'pygame':
            snd = pygame.mixer.Sound(path)
            snd.play()
        elif SOUND_BACKEND == 'winsound':
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass

# -------------------------
# Leaderboard utilities
# -------------------------
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard_table(table):
    try:
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_score_to_leaderboard(name, score, time_taken):
    table = load_leaderboard()
    entry = {
        "name": name,
        "score": score,
        "time": time_taken,
        "when": datetime.utcnow().isoformat() + "Z"
    }
    table.append(entry)
    # Sort by score desc then time asc
    table = sorted(table, key=lambda e: (-e['score'], e['time']))
    # Keep top 50 for storage, but show top 10
    table = table[:50]
    save_leaderboard_table(table)

def show_leaderboard(top_n=10):
    table = load_leaderboard()
    if not table:
        print("\n🏆 Leaderboard empty — be the first!\n")
        return
    print("\n🏆 Leaderboard (Top {}) 🏆".format(top_n))
    for i, e in enumerate(table[:top_n], start=1):
        when = e.get('when','')
        print(f"{i:2d}. {e['name']:<12s}  Score: {e['score']:3d}  Time: {e['time']:3d}s  At:{when}")
    print()

# -------------------------
# Game variables
# -------------------------
CHARACTERS = {
    '1': ("Cat", "🐱", "Meow! I hide numbers inside yarn balls."),
    '2': ("Robot", "🤖", "Beep! I compute a secret integer."),
    '3': ("Panda", "🐼", "Nom nom... I thought of a bamboo-number."),
    '4': ("Dino", "🦖", "Roar! Try not to be eaten by wrong guesses.")
}

LEVELS = {
    '1': ("Easy", 10, 6),
    '2': ("Medium", 50, 7),
    '3': ("Hard", 100, 9)
}

# -------------------------
# Helpers
# -------------------------
def input_int(prompt, min_val=None, max_val=None):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if min_val is not None and v < min_val:
                print(f"Please enter >= {min_val}")
                continue
            if max_val is not None and v > max_val:
                print(f"Please enter <= {max_val}")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")

def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# -------------------------
# Game Flow
# -------------------------
def ascii_title():
    print(r"""
  ____                _                  _   _                  
 / ___|___  _ __  ___| |_ _ __ ___  __ _| |_(_) ___  _ __  ___ 
| |   / _ \| '_ \/ __| __| '__/ _ \/ _` | __| |/ _ \| '_ \/ __|
| |__| (_) | | | \__ \ |_| | |  __/ (_| | |_| | (_) | | | \__ \
 \____\___/|_| |_|___/\__|_|  \___|\__,_|\__|_|\___/|_| |_|___/
                                                                
    Cartoon Number Guessing — Full Edition
    """)
    print("Cute Cartoon Sound Pack selected 🎵 (place files in assets/sounds/ if you want real sounds)")
    print()

def choose_character():
    print("Choose your character:")
    for k, (name, emoji, tag) in CHARACTERS.items():
        print(f" {k}) {emoji}  {name} — {tag}")
    choice = input("Pick 1-4 (default 1): ").strip()
    if choice not in CHARACTERS:
        choice = '1'
    name, emoji, tag = CHARACTERS[choice]
    print(f"Great — you are {emoji} {name}! {tag}\n")
    return choice

def choose_level():
    print("Choose level:")
    for k, (label, rng, tries) in LEVELS.items():
        print(f" {k}) {label} (1..{rng}, {tries} tries)")
    choice = input("Pick 1-3 (default 1): ").strip()
    if choice not in LEVELS:
        choice = '1'
    return choice

def give_hint(secret, limit, hint_count_used):
    # three hint types rotating by usage
    t = hint_count_used % 3
    if t == 0:
        spread = max(1, int(limit * 0.12))
        low = max(1, secret - spread)
        high = min(limit, secret + spread)
        return f"It's between {low} and {high}."
    elif t == 1:
        if secret % 5 == 0:
            return "It's divisible by 5."
        if secret % 2 == 0:
            return "It's even."
        return "It's odd."
    else:
        low = max(1, secret - 5)
        high = min(limit, secret + 5)
        return f"It's within {low} and {high}."

def play_round(player_name, char_choice, level_choice, leaderboard_enabled=True):
    level_name, rng, max_attempts = LEVELS[level_choice]
    secret = random.randint(1, rng)
    attempts_left = max_attempts
    score = 100 + ( (3 - int(level_choice)) * 10 )  # higher base for easier levels
    hint_uses = 0
    start_time = time.time()
    play_sound('start')

    print(f"\n🎯 {CHARACTERS[char_choice][1]}  {CHARACTERS[char_choice][0]} — Level {level_name}")
    print(f"Guess a number between 1 and {rng}. You have {attempts_left} attempts. (Type 'hint' to use a hint)\n")

    while attempts_left > 0:
        s = input(f"Attempt ({attempts_left}) > ").strip().lower()
        if s == 'hint':
            if hint_uses >= 3:
                print("No hints left for this round.")
                continue
            hint_text = give_hint(secret, rng, hint_uses)
            hint_uses += 1
            score = max(0, score - 8)
            print("💡 Hint:", hint_text)
            play_sound('hint')
            continue
        try:
            guess = int(s)
        except ValueError:
            print("Enter an integer or 'hint'.")
            continue

        if guess == secret:
            elapsed = int(time.time() - start_time)
            bonus = max(10, 60 - elapsed)  # reward speed
            final_score = max(0, score + bonus)
            print(f"\n🎉 Correct! You found it in {int(time.time()-start_time)}s. +{bonus} speed bonus.")
            play_sound('win')
            if leaderboard_enabled:
                add_score_to_leaderboard(player_name, final_score, int(time.time() - start_time))
            return final_score, True
        elif guess < secret:
            print("⬆️ Too low!")
            play_sound('pop')
        else:
            print("⬇️ Too high!")
            play_sound('pop')
        attempts_left -= 1
        score = max(0, score - 10)

    # if we exit loop, player lost this round
    print(f"\n💥 Out of attempts! The number was {secret}.")
    play_sound('lose')
    if leaderboard_enabled:
        add_score_to_leaderboard(player_name, 0, int(time.time() - start_time))
    return 0, False

# -------------------------
# Main menu
# -------------------------
def main_menu():
    clear_console()
    ascii_title()
    player_name = input("Player name (leave blank to use 'Player'): ").strip() or "Player"
    while True:
        print("\nMain Menu")
        print(" 1) Play Game")
        print(" 2) View Leaderboard")
        print(" 3) Install / Manage Sounds (info)")
        print(" 4) Credits / Help")
        print(" 5) Quit")
        choice = input("Choose 1-5: ").strip()
        if choice == '1':
            char_choice = choose_character()
            level_choice = choose_level()
            total_score = 0
            rounds = 0
            # allow multiple rounds until lost or user quits
            while True:
                sc, won = play_round(player_name, char_choice, level_choice)
                total_score += sc
                rounds += 1
                print(f"\nRound {rounds} ended. Round score: {sc}. Total score: {total_score}")
                if not won:
                    print("You lost the round. Returning to main menu.")
                    break
                cont = input("Continue next round at same level? (y/n): ").strip().lower()
                if cont != 'y':
                    break
            print("\nReturning to main menu...")
            time.sleep(1.2)
        elif choice == '2':
            show_leaderboard(10)
        elif choice == '3':
            print("\nSound files can be placed in:", SOUNDS_DIR)
            print("Expected (cute pack) filenames (optional):")
            for k, v in SOUND_FILES.items():
                print(" -", os.path.basename(v))
            print("Game will try pygame -> winsound -> silent fallback.")
            input("\nPress Enter to return.")
        elif choice == '4':
            print("\nCartoon Guess Game — Help\n - Type 'hint' during a round to use one of 3 hints.\n - Leaderboard stores last scores.\n - To enable sounds: install pygame (pip install pygame) and place wav files in assets/sounds/.\n - Works in Pydroid / Termux; use Python3.\n")
            input("Press Enter to return.")
        elif choice == '5':
            print("Bye! Play again soon 🐱")
            break
        else:
            print("Invalid choice. Pick 1-5.")

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")