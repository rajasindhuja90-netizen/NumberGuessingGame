# cartoon_guess_kivy.py
"""
Kivy GUI starter for Cartoon Number Guessing Game
Simple UI: character selection, level, start round, input guess, show hints and leaderboard popup
"""
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import random, os, json, time
from datetime import datetime

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: dp(12)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: 1, 0.98, 0.96, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "✨ Cartoon Number Guessing (Kivy) ✨"
        size_hint_y: 0.12
        bold: True
        font_size: '20sp'
    GridLayout:
        cols: 2
        size_hint_y: 0.28
        spacing: dp(6)
        Label:
            text: "Name:"
            size_hint_x: 0.3
        TextInput:
            id: name_input
            text: root.player_name
            multiline: False
        Label:
            text: "Character:"
        Spinner:
            id: char_spinner
            text: root.character_text
            values: ['🐱 Cat','🤖 Robot','🐼 Panda','🦖 Dino']
            on_text: root.on_character(self.text)
        Label:
            text: "Level:"
        Spinner:
            id: level_spinner
            text: 'Easy'
            values: ['Easy','Medium','Hard']
            on_text: root.on_level(self.text)
    BoxLayout:
        size_hint_y: 0.16
        spacing: dp(6)
        Button:
            text: "Start Round"
            on_release: root.start_round()
        Button:
            text: "Hint"
            on_release: root.use_hint()
        Button:
            text: "Leaderboard"
            on_release: root.show_leaderboard()
    BoxLayout:
        size_hint_y: 0.32
        orientation: 'vertical'
        Label:
            id: status_label
            text: root.status_text
            halign: 'center'
            valign: 'middle'
            text_size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(6)
            TextInput:
                id: guess_input
                hint_text: "Enter guess"
                multiline: False
                input_filter: 'int'
            Button:
                text: "Try!"
                size_hint_x: 0.4
                on_release: root.try_guess(guess_input.text)
    Label:
        text: root.footer_text
        size_hint_y: 0.08
        font_size: '12sp'
'''

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)
LEADERBOARD_FILE = os.path.join(ASSETS_DIR, "leaderboard.json")

class GuessApp(App):
    player_name = StringProperty("Player")
    character_text = StringProperty("🐱 Cat")
    status_text = StringProperty("Press Start to play.")
    footer_text = StringProperty("Hints: 3   Attempts: 0")
    secret = NumericProperty(0)

    def build(self):
        self.root = Builder.load_string(KV)
        self.hints_left = 3
        self.attempts_left = 0
        self.score = 0
        return self.root

    def on_character(self, text):
        self.character_text = text

    def on_level(self, text):
        self.level = text

    def start_round(self):
        name = self.root.ids.name_input.text.strip()
        if name:
            self.player_name = name
        lvl = self.root.ids.level_spinner.text
        if lvl == 'Easy':
            rng = 10
            tries = 6
        elif lvl == 'Medium':
            rng = 50
            tries = 7
        else:
            rng = 100
            tries = 9
        self.secret = random.randint(1, rng)
        self.attempts_left = tries
        self.hints_left = 3
        self.start_time = time.time()
        self.score = 100
        self.status_text = f"New round started! Guess 1..{rng}"
        self.footer_text = f"Hints: {self.hints_left}   Attempts: {self.attempts_left}"

    def use_hint(self):
        if self.hints_left <= 0:
            self.status_text = "No hints left!"
            return
        rng = 10 if self.root.ids.level_spinner.text == 'Easy' else (50 if self.root.ids.level_spinner.text=='Medium' else 100)
        t = (3 - self.hints_left) % 3
        if t == 0:
            spread = max(1, int(rng * 0.12))
            low = max(1, self.secret - spread)
            high = min(rng, self.secret + spread)
            hint = f"It's between {low} and {high}"
        elif t == 1:
            hint = "Even" if self.secret % 2 == 0 else "Odd"
        else:
            low = max(1, self.secret - 5)
            high = min(rng, self.secret + 5)
            hint = f"Within {low} and {high}"
        self.hints_left -= 1
        self.status_text = "💡 Hint: " + hint
        self.footer_text = f"Hints: {self.hints_left}   Attempts: {self.attempts_left}"

    def try_guess(self, guess_text):
        if not guess_text:
            self.status_text = "Enter a guess!"
            return
        try:
            guess = int(guess_text)
        except ValueError:
            self.status_text = "Invalid number."
            return
        if guess == self.secret:
            elapsed = int(time.time() - self.start_time)
            final_score = max(10, self.score + max(0, 60 - elapsed))
            self.status_text = f"🎉 Correct! Score {final_score}"
            self.record_score(final_score)
            return
        elif guess < self.secret:
            self.status_text = "⬆️ Too low!"
        else:
            self.status_text = "⬇️ Too high!"
        self.attempts_left -= 1
        self.footer_text = f"Hints: {self.hints_left}   Attempts: {self.attempts_left}"
        if self.attempts_left <= 0:
            self.status_text = f"💥 Out of attempts! Number: {self.secret}"

    def show_leaderboard(self):
        table = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    table = json.load(f)
            except:
                table = []
        if not table:
            self.status_text = "Leaderboard empty."
            return
        text = "\\n".join([f"{i+1}. {e['name']} - {e['score']}" for i, e in enumerate(table[:10])])
        self.status_text = text

    def record_score(self, score):
        table = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    table = json.load(f)
            except:
                table = []
        table.append({"name": self.player_name, "score": score, "when": datetime.utcnow().isoformat()+"Z"})
        table = sorted(table, key=lambda e: -e['score'])
        table = table[:50]
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(table, f, indent=2)
        self.show_leaderboard()

if __name__ == '__main__':
    GuessApp().run()