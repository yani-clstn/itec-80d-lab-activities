import tkinter as tk

from config import (
    FONT, CARD, CARD_ALT, TEXT, TEXT_MUTED, ACCENT, ACCENT_HOVER,
    COLOR_CORRECT, COLOR_INCORRECT, COLOR_MISSED, TEXT_ON_LIGHT,
)

STEPS = [
    "Press Start Game. A grid appears and some tiles light up.",
    "Memorize their positions. The bar and countdown show how long you have.",
    "When the tiles go dark, click the ones you remember. A timer tracks how long you take.",
    "Press Submit (or the Enter key) to lock in your answer.",
    "Check the colors on the grid (see the key below).",
    "Rounds get harder: bigger grids and more tiles, 5 rounds in total.",
]


def show_help(parent):
    """Displays the instructions popup. Called from the help button in the GUI."""
    win = tk.Toplevel(parent)
    win.title("How to Play")
    win.configure(bg=CARD, padx=26, pady=22)
    win.resizable(False, False)
    win.transient(parent)

    tk.Label(win, text="How to play", font=(FONT, 16, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
    tk.Label(
        win, text="Remember where the tiles lit up, then recreate the pattern.",
        font=(FONT, 10), bg=CARD, fg=TEXT_MUTED,
    ).pack(anchor="w", pady=(2, 12))

    for number, step in enumerate(STEPS, start=1):
        row = tk.Frame(win, bg=CARD)
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=str(number), width=2, font=(FONT, 10, "bold"),
            bg=ACCENT, fg="#ffffff",
        ).pack(side="left", anchor="n")
        tk.Label(
            row, text=step, font=(FONT, 10), bg=CARD, fg=TEXT,
            wraplength=380, justify="left",
        ).pack(side="left", padx=(10, 0))

    key = tk.Frame(win, bg=CARD_ALT, padx=14, pady=10)
    key.pack(fill="x", pady=(14, 6))
    tk.Label(key, text="Color key", font=(FONT, 10, "bold"), bg=CARD_ALT, fg=TEXT).pack(anchor="w")
    for color, symbol, meaning in [
        (COLOR_CORRECT, "✓", "Correct: you found a lit tile"),
        (COLOR_INCORRECT, "✗", "Wrong: you picked a tile that was not lit"),
        (COLOR_MISSED, "!", "Missed: a lit tile you did not pick"),
    ]:
        line = tk.Frame(key, bg=CARD_ALT)
        line.pack(fill="x", pady=2)
        tk.Label(
            line, text=symbol, width=3, font=(FONT, 10, "bold"),
            bg=color, fg=TEXT_ON_LIGHT,
        ).pack(side="left")
        tk.Label(line, text=meaning, font=(FONT, 10), bg=CARD_ALT, fg=TEXT).pack(side="left", padx=10)

    tk.Label(
        win, text="Tip: wrong tiles lower your accuracy, so don't just select everything.",
        font=(FONT, 9, "italic"), bg=CARD, fg=TEXT_MUTED,
    ).pack(anchor="w", pady=(4, 12))

    close = tk.Button(
        win, text="Got it", command=win.destroy, font=(FONT, 10, "bold"),
        bg=ACCENT, fg="#ffffff", activebackground=ACCENT_HOVER, activeforeground="#ffffff",
        relief="flat", bd=0, highlightthickness=0, padx=22, pady=7, cursor="hand2",
    )
    close.pack(anchor="e")