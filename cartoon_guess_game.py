"""
Cartoon / Fun Themed Number Guessing Game (Tkinter)
Features:
- Cartoon-themed GUI with animations
- 3 difficulty levels (Easy/Medium/Hard)
- Timer-based scoring
- Leaderboard saved to leaderboard.txt
- Sound effects (optional, uses pygame)
- Hints Power-Ups (3 per game): range hint, parity/divisibility hint, +/-5 proximity hint
- Replay option

Run instructions:
- Install dependencies if you want sound: pip install pygame
- Save this file as `cartoon_guess_game.py` and run: python cartoon_guess_game.py

Note: If pygame is not installed, the game runs without sounds.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
import threading
import os

# Try to import pygame for sounds, if available
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

LEADERBOARD_FILE = "leaderboard.txt"

# --- Utility functions ---

def play_sound(path):
    if not SOUND_AVAILABLE:
        return
    try:
        pygame.mixer.Sound(path).play()
    except Exception:
        pass


def save_score(name, score):
    try:
        with open(LEADERBOARD_FILE, "a", encoding="utf-8") as f:
            f.write(f"{name} - {score}\n")
    except Exception as e:
        print("Could not save leaderboard:", e)


def read_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return lines

# --- Main App ---

class CartoonGuessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Cartoon Number Guessing Game ✨")
        self.geometry("700x520")
        self.resizable(False, False)
        self.configure(bg="#FFFAF0")  # warm paper background

        # Game state
        self.player_name = "Player"
        self.level = 1
        self.secret = 0
        self.limit = 10
        self.attempts_left = 5
        self.max_attempts = 5
        self.score = 0
        self.start_time = None
        self.hints_left = 3
        self.game_active = False

        # Build UI
        self._build_header()
        self._build_main_area()
        self._build_footer()

        # small animation loop
        self.anim_objects = []
        self.after(1500, self._floating_animation)

    # --- UI Builders ---
    def _build_header(self):
        header = tk.Frame(self, bg="#FF8BA7", height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = tk.Label(header, text="✨ Cartoon Number Guessing ✨", font=("Comic Sans MS", 22, "bold"), bg="#FF8BA7")
        title.pack(pady=8)

        subtitle = tk.Label(header, text="Guess the number, use hints, beat the timer — be a hero!", font=("Arial", 10), bg="#FF8BA7")
        subtitle.pack()

    def _build_main_area(self):
        area = tk.Frame(self, bg="#FFFAF0")
        area.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(area, bg="#FFF1E6")
        left.place(relx=0.02, rely=0.04, relwidth=0.66, relheight=0.72)

        # Cartoon panel
        self.canvas = tk.Canvas(left, bg="#FFF1E6", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self._draw_cartoon_scene()

        right = tk.Frame(area, bg="#FFFAF0")
        right.place(relx=0.70, rely=0.04, relwidth=0.28, relheight=0.72)

        # Controls on right
        name_lbl = tk.Label(right, text="Your name:", bg="#FFFAF0", font=("Arial", 10, "bold"))
        name_lbl.pack(pady=(6,0))
        self.name_entry = tk.Entry(right)
        self.name_entry.pack(pady=4)

        level_lbl = tk.Label(right, text="Choose Level:", bg="#FFFAF0", font=("Arial", 10, "bold"))
        level_lbl.pack(pady=(8,0))
        self.level_var = tk.IntVar(value=1)
        ttk.Radiobutton(right, text="Easy (1-10)", variable=self.level_var, value=1).pack(anchor="w")
        ttk.Radiobutton(right, text="Medium (1-50)", variable=self.level_var, value=2).pack(anchor="w")
        ttk.Radiobutton(right, text="Hard (1-100)", variable=self.level_var, value=3).pack(anchor="w")

        start_btn = tk.Button(right, text="Start Game ▶", command=self.start_game, bg="#FFDE59")
        start_btn.pack(fill="x", pady=(12,6))

        hint_btn = tk.Button(right, text="Use Hint 💡 (3 left)", command=self.use_hint, bg="#A0E7E5")
        hint_btn.pack(fill="x")
        self.hint_btn = hint_btn

        self.info_label = tk.Label(right, text="Score: 0\nTimer: 0s\nAttempts: 0", bg="#FFFAF0", font=("Arial", 10))
        self.info_label.pack(pady=12)

        leaderboard_btn = tk.Button(right, text="View Leaderboard 🏆", command=self.show_leaderboard_ui, bg="#FFB6C1")
        leaderboard_btn.pack(fill="x", pady=(6,0))

    def _build_footer(self):
        footer = tk.Frame(self, bg="#FFF3E0", height=80)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        self.msg_label = tk.Label(footer, text="Welcome! Press Start to begin.", font=("Arial", 12), bg="#FFF3E0")
        self.msg_label.pack(pady=12)

    # --- Canvas art ---
    def _draw_cartoon_scene(self):
        self.canvas.delete("all")
        w = 460
        h = 330
        # sky rectangle
        self.canvas.create_rectangle(0, 0, w, h, fill="#E8F6FF", outline="")
        # ground
        self.canvas.create_rectangle(0, h-60, w, h, fill="#C8F7C5", outline="")
        # mascot (simple)
        self.canvas.create_oval(40, 100, 140, 200, fill="#FFD1DC", outline="")  # head
        self.canvas.create_oval(60, 150, 120, 230, fill="#FFF3B0", outline="")  # body
        self.canvas.create_text(90, 135, text="😊", font=("Arial", 28))
        # speech bubble placeholder
        self.speech = self.canvas.create_text(300, 80, text="I'm thinking of a number...🤫", font=("Comic Sans MS", 12, "bold"))

    # --- Game logic ---
    def start_game(self):
        # initialize
        name = self.name_entry.get().strip()
        if name:
            self.player_name = name
        else:
            self.player_name = "Player"

        self.level = self.level_var.get()
        if self.level == 1:
            self.limit = 10
            self.max_attempts = 6
        elif self.level == 2:
            self.limit = 50
            self.max_attempts = 7
        else:
            self.limit = 100
            self.max_attempts = 9

        self.secret = random.randint(1, self.limit)
        self.attempts_left = self.max_attempts
        self.hints_left = 3
        self.score = 200 - (self.level * 20)
        self.start_time = time.time()
        self.game_active = True
        self.msg_label.config(text=f"Level {self.level} started! Guess between 1 and {self.limit}.")
        self._update_info()
        self._prompt_for_guess()
        play_sound_if_available('start.wav')

    def _prompt_for_guess(self):
        if not self.game_active:
            return
        # Show input dialog on main thread
        self.after(100, self._ask_guess)

    def _ask_guess(self):
        if not self.game_active:
            return
        try:
            guess_str = simpledialog.askstring("Your Guess", f"Enter a guess (1 to {self.limit})\nAttempts left: {self.attempts_left}", parent=self)
            if guess_str is None:
                # player cancelled
                return
            guess = int(guess_str)
        except ValueError:
            messagebox.showinfo("Oops!", "Please enter a valid integer.")
            self._prompt_for_guess()
            return

        self._handle_guess(guess)

    def _handle_guess(self, guess):
        if not self.game_active:
            return
        if guess == self.secret:
            time_taken = int(time.time() - self.start_time)
            gained = max(30, self.score - time_taken)
            total = gained
            self.msg_label.config(text=f"🎉 {self.player_name}, you guessed it! +{gained} pts")
            play_sound_if_available('win.wav')
            self._celebrate()
            save_score(self.player_name, total)
            self._ask_play_again()
            self.game_active = False
            return
        else:
            self.attempts_left -= 1
            hint = "⬆️ Higher!" if guess < self.secret else "⬇️ Lower!"
            self.msg_label.config(text=hint)
            play_sound_if_available('pop.wav')
            self.score -= 10
            self._update_info()

            if self.attempts_left <= 0:
                self.msg_label.config(text=f"💥 Out of attempts! The number was {self.secret}")
                play_sound_if_available('lose.wav')
                self.game_active = False
                save_score(self.player_name, 0)
                self._ask_play_again()
                return

            # continue prompting
            self._prompt_for_guess()

    def _update_info(self):
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        self.info_label.config(text=f"Score: {self.score}\nTimer: {elapsed}s\nAttempts: {self.attempts_left}\nHints: {self.hints_left}")
        # update speech bubble
        self.canvas.itemconfigure(self.speech, text=f"I'm thinking of a number 1..{self.limit} 🤫")

    def use_hint(self):
        if not self.game_active:
            messagebox.showinfo("No game", "Start a game first to use hints.")
            return
        if self.hints_left <= 0:
            messagebox.showinfo("No hints", "You have used all hints for this level.")
            return

        # choose hint type based on hints left or randomly
        hint_type = (4 - self.hints_left) % 3  # cycles through 0,1,2
        text = ""
        if hint_type == 0:
            # range hint +/-10%
            spread = max(1, int(self.limit * 0.1))
            low = max(1, self.secret - spread)
            high = min(self.limit, self.secret + spread)
            text = f"It's between {low} and {high}!"
        elif hint_type == 1:
            # divisibility / parity
            if self.secret % 5 == 0:
                text = "It's divisible by 5!"
            elif self.secret % 2 == 0:
                text = "It's an even number!"
            else:
                text = "It's an odd number!"
        else:
            # proximity hint +/-5
            low = max(1, self.secret - 5)
            high = min(self.limit, self.secret + 5)
            text = f"It's within {low} and {high}"

        self.hints_left -= 1
        self.msg_label.config(text=f"💡 Hint: {text}")
        self._update_info()
        play_sound_if_available('hint.wav')

    def _ask_play_again(self):
        # show leaderboard and ask
        self.show_leaderboard_ui()
        if messagebox.askyesno("Play Again?", "Do you want to play another round?"):
            # reset minimal state and go to start screen
            self.name_entry.delete(0, tk.END)
            self.game_active = False
            self._draw_cartoon_scene()
        else:
            self.quit()

    def show_leaderboard_ui(self):
        lines = read_leaderboard()
        if not lines:
            messagebox.showinfo("Leaderboard", "No scores yet. Be the first!")
            return
        text = "\n".join(lines[-15:][::-1])  # show last 15 entries newest-first
        messagebox.showinfo("Leaderboard (latest)", text)

    # --- Animations ---
    def _floating_animation(self):
        # playful floating emojis that appear and fade
        if random.random() < 0.5:
            x = random.randint(260, 420)
            y = random.randint(20, 140)
            emoji = random.choice(["⭐", "🌟", "🍭", "🎈"])
            obj = self.canvas.create_text(x, y, text=emoji, font=("Arial", 18))
            self.anim_objects.append(obj)
            def float_up(o, steps=24):
                for i in range(steps):
                    try:
                        self.canvas.move(o, 0, -3)
                        self.canvas.after(40)
                        self.canvas.update()
                    except Exception:
                        break
                try:
                    self.canvas.delete(o)
                except Exception:
                    pass
            threading.Thread(target=float_up, args=(obj,), daemon=True).start()

        # schedule next
        self.after(1200, self._floating_animation)

    def _celebrate(self):
        # confetti burst
        for _ in range(40):
            x = random.randint(200, 420)
            y = random.randint(80, 260)
            size = random.randint(4,10)
            color = random.choice(["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#FFA8A8"])
            self.canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
        self.canvas.update()

# Helper to play default sounds if available (non-blocking)
def play_sound_if_available(filename):
    if not SOUND_AVAILABLE:
        return
    # The file paths are placeholders; if you want sounds, place small wav files next to the script
    sounds = {
        'start.wav': filename if False else 'start.wav',
        'win.wav': filename if False else 'win.wav',
        'lose.wav': filename if False else 'lose.wav',
        'hint.wav': filename if False else 'hint.wav',
        'pop.wav': filename if False else 'pop.wav'
    }
    # Attempt safe play (non-blocking)
    try:
        if os.path.exists('start.wav') or os.path.exists('win.wav'):
            # play a short clip (select any existing file)
            pygame.mixer.Sound('start.wav').play()
    except Exception:
        pass

# --- Run the app ---
if __name__ == '__main__':
    app = CartoonGuessGame()
    app.mainloop()