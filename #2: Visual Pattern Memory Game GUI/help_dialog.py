import tkinter as tk


def show_help(parent):
    """Displays an instructions popup. Called from the Help button in the GUI."""
    win = tk.Toplevel(parent)
    win.title("How to Play")
    win.resizable(False, False)

    text = (
        "VISUAL PATTERN MEMORY GAME\n\n"
        "1. Click 'Start Game' to begin Round 1.\n"
        "2. A grid will appear with some cells highlighted in blue.\n"
        "   Memorize their positions before they disappear.\n"
        "3. Once the cells return to their normal color, click the\n"
        "   cells you remember being highlighted.\n"
        "4. Click 'Submit' to lock in your answer for the round.\n"
        "5. Green = correctly remembered, Red = wrongly selected,\n"
        "   Orange = a cell you missed.\n"
        "6. The grid size and number of cells get harder each round.\n"
        "7. After 5 rounds, your results and statistics will be shown.\n\n"
        "Use 'Export Data to CSV' to save your results, and\n"
        "'Reset / New Participant' to run the test again."
    )

    tk.Label(win, text=text, justify="left", padx=15, pady=15, font=("Arial", 10)).pack()
    tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))