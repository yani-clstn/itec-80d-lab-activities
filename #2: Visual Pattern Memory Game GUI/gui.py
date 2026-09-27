import tkinter as tk
from config import ROUNDS, CELL_SIZE, COLOR_DEFAULT, COLOR_HIGHLIGHT
from game_logic import generate_pattern


class VisualPatternMemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Pattern Memory Game")

        self.current_round = 0
        self.results = []

        self.buttons = []
        self.correct_pattern = set()
        self.selected_cells = set()   # NEW: cells the user has clicked this round

        self.title_label = tk.Label(
            root, text="Visual Pattern Memory Game", font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=10)

        self.instructions_label = tk.Label(
            root,
            text="Memorize the highlighted cells, then click them after they disappear.",
            font=("Arial", 11),
        )
        self.instructions_label.pack(pady=5)

        self.status_label = tk.Label(root, text="Round 0 of 5", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.game_frame = tk.Frame(root)
        self.game_frame.pack(pady=10)

        self.feedback_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
        self.feedback_label.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=5)

        self.submit_button = tk.Button(
            root, text="Submit", state="disabled", command=self.submit_answer
        )
        self.submit_button.pack(pady=5)

        self.results_label = tk.Label(root, text="", font=("Arial", 10), justify="left")
        self.results_label.pack(pady=5)

        tk.Label(root, text="Recorded Interaction Data:").pack()
        self.listbox = tk.Listbox(root, width=50, height=6)
        self.listbox.pack(pady=5)

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)
        tk.Button(control_frame, text="Reset", command=self.reset_game).pack(side="left", padx=5)
        tk.Button(control_frame, text="Exit", command=root.quit).pack(side="left", padx=5)

    def start_game(self):
        self.current_round = 0
        self.results = []
        self.next_round()

    def next_round(self):
        if self.current_round >= len(ROUNDS):
            self.feedback_label.config(text="Game complete! (results screen comes in Step 6)")
            return

        round_config = ROUNDS[self.current_round]
        self.status_label.config(text=f"Round {self.current_round + 1} of {len(ROUNDS)}")
        self.feedback_label.config(text="Memorize the pattern...")
        self.selected_cells = set()
        self.submit_button.config(state="disabled")

        self.build_grid(round_config["grid"])
        self.correct_pattern = generate_pattern(round_config["grid"], round_config["cells"])
        self.show_pattern()

        self.root.after(round_config["display_time"], self.hide_pattern)

    def build_grid(self, grid_size):
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        for r in range(grid_size):
            row_buttons = []
            for c in range(grid_size):
                btn = tk.Button(
                    self.game_frame,
                    width=4, height=2,
                    bg=COLOR_DEFAULT,
                    state="disabled",
                )
                # NEW: bind the click to toggle_cell, capturing r and c correctly
                btn.config(command=lambda row=r, col=c: self.toggle_cell(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def show_pattern(self):
        for (r, c) in self.correct_pattern:
            self.buttons[r][c].config(bg=COLOR_HIGHLIGHT)

    def hide_pattern(self):
        for row in self.buttons:
            for btn in row:
                btn.config(bg=COLOR_DEFAULT, state="normal")   # NEW: re-enable clicking
        self.feedback_label.config(text="Now click the cells you remember!")
        self.submit_button.config(state="normal")              # NEW: allow submitting

    def toggle_cell(self, row, col):
        cell = (row, col)
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
            self.buttons[row][col].config(bg=COLOR_DEFAULT)
        else:
            self.selected_cells.add(cell)
            self.buttons[row][col].config(bg=COLOR_HIGHLIGHT)

    def submit_answer(self):
        # placeholder — scoring logic comes next
        print("Submitted:", self.selected_cells, "Correct was:", self.correct_pattern)

    def reset_game(self):
        print("Reset clicked")