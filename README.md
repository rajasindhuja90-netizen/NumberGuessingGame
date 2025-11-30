Cartoon Number Guessing — Web

This folder contains a small static web version of the Cartoon Number Guessing game.

Files:
- `index.html` — main page
- `styles.css` — simple styles
- `app.js` — game logic (uses LocalStorage for the leaderboard)

How to run:
- Open `web/index.html` in your browser (double-click or drag into browser).
- Optional: place sound files in `assets/sounds/` relative to repository root. Filenames expected: `start.wav`, `win.wav`, `pop.wav`, `hint.wav`, `lose.wav`.

Notes:
- Leaderboard is stored locally in your browser's LocalStorage (key `cartoon_guess_leaderboard_v1`).
- This is a static client-only site — no server required.

Want more?
- I can add an export/import for leaderboard JSON, or integrate the existing `leaderboard.json` file by providing a small server to serve and merge scores. Ask and I can implement it.
