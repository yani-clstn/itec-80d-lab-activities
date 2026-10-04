import tkinter as tk

STEPS = [
    "Press Start Game. A grid appears and some tiles light up.",
    "Memorize their positions. The bar and countdown show how long you have.",
    "When the tiles go dark, click the ones you remember. A timer tracks how long you take.",
    "Press Submit (or the Enter key) to lock in your answer.",
    "Check the colors on the grid (see the key below).",
    "Rounds get harder: bigger grids and more tiles, 5 rounds in total.",
]


def show_help(parent, theme):
    """Displays the instructions popup, styled to match the active theme."""
    win = tk.Toplevel(parent)
    win.title("How to Play")
    win.configure(bg=theme["CARD"], padx=26, pady=22)
    win.resizable(False, False)
    win.transient(parent)

    tk.Label(
        win, text="How to play", font=("Arial", 16, "bold"), bg=theme["CARD"], fg=theme["TEXT"]
    ).pack(anchor="w")
    tk.Label(
        win, text="Remember where the tiles lit up, then recreate the pattern.",
        font=("Arial", 10), bg=theme["CARD"], fg=theme["TEXT_MUTED"],
    ).pack(anchor="w", pady=(2, 12))

    for number, step in enumerate(STEPS, start=1):
        row = tk.Frame(win, bg=theme["CARD"])
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=str(number), width=2, font=("Arial", 10, "bold"),
            bg=theme["ACCENT"], fg="#ffffff",
        ).pack(side="left", anchor="n")
        tk.Label(
            row, text=step, font=("Arial", 10), bg=theme["CARD"], fg=theme["TEXT"],
            wraplength=380, justify="left",
        ).pack(side="left", padx=(10, 0))

    key = tk.Frame(win, bg=theme["CARD_ALT"], padx=14, pady=10)
    key.pack(fill="x", pady=(14, 6))
    tk.Label(
        key, text="Color key", font=("Arial", 10, "bold"), bg=theme["CARD_ALT"], fg=theme["TEXT"]
    ).pack(anchor="w")
    for color, symbol, meaning in [
        (theme["COLOR_CORRECT"], "✓", "Correct: you found a lit tile"),
        (theme["COLOR_INCORRECT"], "✗", "Wrong: you picked a tile that was not lit"),
        (theme["COLOR_MISSED"], "!", "Missed: a lit tile you did not pick"),
    ]:
        line = tk.Frame(key, bg=theme["CARD_ALT"])
        line.pack(fill="x", pady=2)
        tk.Label(
            line, text=symbol, width=3, font=("Arial", 10, "bold"),
            bg=color, fg=theme["TEXT_ON_LIGHT"],
        ).pack(side="left")
        tk.Label(
            line, text=meaning, font=("Arial", 10), bg=theme["CARD_ALT"], fg=theme["TEXT"]
        ).pack(side="left", padx=10)

    tk.Label(
        win, text="Tip: wrong tiles lower your accuracy, so don't just select everything.",
        font=("Arial", 9, "italic"), bg=theme["CARD"], fg=theme["TEXT_MUTED"],
    ).pack(anchor="w", pady=(4, 12))

    close = tk.Button(
        win, text="Got it", command=win.destroy, font=("Arial", 10, "bold"),
        bg=theme["ACCENT"], fg="#ffffff", activebackground=theme["ACCENT_HOVER"],
        activeforeground="#ffffff", relief="flat", bd=0, highlightthickness=0,
        padx=22, pady=7, cursor="hand2",
    )
    close.pack(anchor="e")