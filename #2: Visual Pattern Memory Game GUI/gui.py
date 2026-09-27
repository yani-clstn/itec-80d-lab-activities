import os
import time
import tkinter as tk
from tkinter import messagebox

from config import (
    ROUNDS, COLOR_DEFAULT, COLOR_HIGHLIGHT, COLOR_CORRECT, COLOR_MISSED,
    COLOR_INCORRECT, FEEDBACK_PAUSE_MS, AGE_GROUPS, EXPERIENCE_LEVELS,
    CSV_FOLDER, CSV_FILENAME,
)
from game_logic import generate_pattern, score_round
from data_manager import DataManager
from help_dialog import show_help


class VisualPatternMemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Pattern Memory Game")
        self.root.resizable(False, False)

        self.data = DataManager()

        # participant/session info, collected once before testing starts
        self.participant_id = ""
        self.age_group = ""
        self.experience_level = ""
        self.session_number = 1

        # per-round state
        self.current_round = 0
        self.buttons = []
        self.correct_pattern = set()
        self.selected_cells = set()
        self.selection_start_time = None

        self._build_setup_screen()
        self._build_game_screen()

        self.setup_frame.pack(fill="both", expand=True)

    # -----------------------------------------------------------------
    # SETUP SCREEN — collects non-identifying participant info first
    # -----------------------------------------------------------------
    def _build_setup_screen(self):
        self.setup_frame = tk.Frame(self.root, padx=20, pady=20)

        tk.Label(
            self.setup_frame, text="Visual Pattern Memory Game",
            font=("Arial", 18, "bold"),
        ).pack(pady=(0, 5))
        tk.Label(
            self.setup_frame,
            text="Please enter participant details before starting.\n"
                 "(No personally identifying information is collected.)",
            font=("Arial", 10), justify="center",
        ).pack(pady=(0, 15))

        form = tk.Frame(self.setup_frame)
        form.pack()

        tk.Label(form, text="Participant Code (e.g. P01):").grid(
            row=0, column=0, sticky="e", pady=4, padx=5
        )
        self.participant_entry = tk.Entry(form)
        self.participant_entry.grid(row=0, column=1, pady=4, padx=5)

        tk.Label(form, text="Age Group:").grid(row=1, column=0, sticky="e", pady=4, padx=5)
        self.age_var = tk.StringVar(value=AGE_GROUPS[0])
        tk.OptionMenu(form, self.age_var, *AGE_GROUPS).grid(
            row=1, column=1, pady=4, padx=5, sticky="w"
        )

        tk.Label(form, text="Experience with similar games:").grid(
            row=2, column=0, sticky="e", pady=4, padx=5
        )
        self.experience_var = tk.StringVar(value=EXPERIENCE_LEVELS[0])
        tk.OptionMenu(form, self.experience_var, *EXPERIENCE_LEVELS).grid(
            row=2, column=1, pady=4, padx=5, sticky="w"
        )

        tk.Label(form, text="Testing Session Number:").grid(
            row=3, column=0, sticky="e", pady=4, padx=5
        )
        self.session_entry = tk.Entry(form)
        self.session_entry.insert(0, "1")
        self.session_entry.grid(row=3, column=1, pady=4, padx=5, sticky="w")

        self.setup_error_label = tk.Label(self.setup_frame, text="", fg=COLOR_INCORRECT)
        self.setup_error_label.pack(pady=(10, 0))

        tk.Button(
            self.setup_frame, text="Continue to Game", command=self._submit_setup
        ).pack(pady=15)

    def _submit_setup(self):
        pid = self.participant_entry.get().strip()
        session_text = self.session_entry.get().strip()

        # --- input validation (error prevention) ---
        if not pid:
            self.setup_error_label.config(text="Please enter a participant code (e.g. P01).")
            return
        if not session_text.isdigit():
            self.setup_error_label.config(text="Session number must be a whole number.")
            return

        self.participant_id = pid
        self.age_group = self.age_var.get()
        self.experience_level = self.experience_var.get()
        self.session_number = int(session_text)

        self.setup_frame.pack_forget()
        self.game_frame_outer.pack(fill="both", expand=True)

    # -----------------------------------------------------------------
    # MAIN GAME SCREEN
    # -----------------------------------------------------------------
    def _build_game_screen(self):
        self.game_frame_outer = tk.Frame(self.root, padx=15, pady=15)

        self.title_label = tk.Label(
            self.game_frame_outer, text="Visual Pattern Memory Game",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=(0, 5))

        top_row = tk.Frame(self.game_frame_outer)
        top_row.pack(fill="x")

        self.instructions_label = tk.Label(
            top_row,
            text="Memorize the highlighted cells, then click the same cells after they disappear.",
            font=("Arial", 10), wraplength=420, justify="left",
        )
        self.instructions_label.pack(side="left", pady=5)

        tk.Button(top_row, text="Help", width=6, command=lambda: show_help(self.root)).pack(
            side="right"
        )

        self.status_label = tk.Label(
            self.game_frame_outer, text="Round 0 of 0", font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=5)

        # Countdown/progress bar shown during the memorize phase (visibility enhancement)
        self.progress_canvas = tk.Canvas(
            self.game_frame_outer, width=300, height=10, bg="white", highlightthickness=1
        )
        self.progress_canvas.pack(pady=(0, 10))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 10, fill=COLOR_HIGHLIGHT, width=0
        )

        self.game_frame = tk.Frame(self.game_frame_outer)
        self.game_frame.pack(pady=5)

        self.feedback_label = tk.Label(self.game_frame_outer, text="", font=("Arial", 12, "bold"))
        self.feedback_label.pack(pady=5)

        button_row = tk.Frame(self.game_frame_outer)
        button_row.pack(pady=5)
        self.start_button = tk.Button(button_row, text="Start Game", command=self.start_game)
        self.start_button.pack(side="left", padx=5)
        self.submit_button = tk.Button(
            button_row, text="Submit", state="disabled", command=self.submit_answer
        )
        self.submit_button.pack(side="left", padx=5)

        self.results_label = tk.Label(
            self.game_frame_outer, text="", font=("Arial", 10), justify="left", anchor="w"
        )
        self.results_label.pack(pady=10, fill="x")

        tk.Label(
            self.game_frame_outer, text="Recorded Interaction Data:", font=("Arial", 10, "bold")
        ).pack(anchor="w")
        self.listbox = tk.Listbox(self.game_frame_outer, width=60, height=6)
        self.listbox.pack(pady=5, fill="x")

        control_frame = tk.Frame(self.game_frame_outer)
        control_frame.pack(pady=5)
        tk.Button(
            control_frame, text="Reset / New Participant", command=self.reset_game
        ).pack(side="left", padx=5)
        tk.Button(
            control_frame, text="Export Data to CSV", command=self.export_data
        ).pack(side="left", padx=5)
        tk.Button(control_frame, text="Exit", command=self.root.quit).pack(side="left", padx=5)

    # -----------------------------------------------------------------
    # GAME FLOW
    # -----------------------------------------------------------------
    def start_game(self):
        self.current_round = 0
        self.data.clear()
        self.listbox.delete(0, tk.END)
        self.results_label.config(text="")
        self.start_button.config(state="disabled")
        self.next_round()

    def next_round(self):
        if self.current_round >= len(ROUNDS):
            self._show_final_results()
            return

        round_config = ROUNDS[self.current_round]
        self.status_label.config(
            text=f"Round {self.current_round + 1} of {len(ROUNDS)} "
                 f"(Grid {round_config['grid']}x{round_config['grid']}, "
                 f"{round_config['cells']} cells)"
        )
        self.feedback_label.config(text="Memorize the pattern...", fg="black")
        self.selected_cells = set()
        self.submit_button.config(state="disabled")

        self._build_grid(round_config["grid"])
        self.correct_pattern = generate_pattern(round_config["grid"], round_config["cells"])
        self._show_pattern()

        self._animate_progress(round_config["display_time"])
        self.root.after(round_config["display_time"], self._hide_pattern)

    def _build_grid(self, grid_size):
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        for r in range(grid_size):
            row_buttons = []
            for c in range(grid_size):
                btn = tk.Button(
                    self.game_frame, width=4, height=2, bg=COLOR_DEFAULT, state="disabled",
                )
                btn.config(command=lambda row=r, col=c: self._toggle_cell(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def _show_pattern(self):
        for (r, c) in self.correct_pattern:
            self.buttons[r][c].config(bg=COLOR_HIGHLIGHT)

    def _animate_progress(self, duration_ms, elapsed=0, step=50):
        # Visibility enhancement: shrinking bar shows how much memorize-time is left
        if elapsed >= duration_ms:
            self.progress_canvas.coords(self.progress_bar, 0, 0, 0, 10)
            return
        remaining_fraction = 1 - (elapsed / duration_ms)
        self.progress_canvas.coords(self.progress_bar, 0, 0, 300 * remaining_fraction, 10)
        self.root.after(step, lambda: self._animate_progress(duration_ms, elapsed + step, step))

    def _hide_pattern(self):
        for row in self.buttons:
            for btn in row:
                btn.config(bg=COLOR_DEFAULT, state="normal")
        self.feedback_label.config(
            text="Now click the cells you remember, then press Submit.", fg="black"
        )
        self.submit_button.config(state="normal")
        self.selection_start_time = time.time()

    def _toggle_cell(self, row, col):
        cell = (row, col)
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
            self.buttons[row][col].config(bg=COLOR_DEFAULT)
        else:
            self.selected_cells.add(cell)
            self.buttons[row][col].config(bg=COLOR_HIGHLIGHT)

    def submit_answer(self):
        self.submit_button.config(state="disabled")
        for row in self.buttons:
            for btn in row:
                btn.config(state="disabled")  # error prevention: no edits after submit

        completion_time = time.time() - self.selection_start_time
        score = score_round(self.correct_pattern, self.selected_cells)

        # Per-cell feedback: green = correct, red = wrongly selected, orange = missed
        for (r, c) in self.correct_pattern & self.selected_cells:
            self.buttons[r][c].config(bg=COLOR_CORRECT)
        for (r, c) in self.selected_cells - self.correct_pattern:
            self.buttons[r][c].config(bg=COLOR_INCORRECT)
        for (r, c) in self.correct_pattern - self.selected_cells:
            self.buttons[r][c].config(bg=COLOR_MISSED)

        if score["accuracy"] == 100.0:
            self.feedback_label.config(text="CORRECT! Accuracy: 100%", fg=COLOR_CORRECT)
        else:
            self.feedback_label.config(
                text=f"{score['correct_cells']} correct, {score['total_errors']} error(s). "
                     f"Accuracy: {score['accuracy']:.0f}%",
                fg=COLOR_INCORRECT,
            )
        self.root.bell()  # simple audio feedback

        round_config = ROUNDS[self.current_round]
        record = {
            "participant_id": self.participant_id,
            "age_group": self.age_group,
            "experience_level": self.experience_level,
            "session": self.session_number,
            "round": self.current_round + 1,
            "grid_size": round_config["grid"],
            "pattern_complexity": round_config["cells"],
            "display_time_ms": round_config["display_time"],
            "completion_time": round(completion_time, 3),
            **score,
        }
        self.data.add_record(record)
        self.listbox.insert(tk.END, self.data.listbox_line(record))

        self.current_round += 1
        self.root.after(FEEDBACK_PAUSE_MS, self.next_round)

    # -----------------------------------------------------------------
    # RESULTS / STATISTICS
    # -----------------------------------------------------------------
    def _show_final_results(self):
        stats = self.data.summary_stats()
        self.status_label.config(text="Game complete!")
        self.feedback_label.config(text="See your results below.", fg="black")
        self.start_button.config(state="normal", text="Play Again")

        for widget in self.game_frame.winfo_children():
            widget.destroy()

        if stats:
            self.results_label.config(text=(
                f"Mean accuracy: {stats['mean_accuracy']:.1f}%   |   "
                f"Median accuracy: {stats['median_accuracy']:.1f}%\n"
                f"Mean completion time: {stats['mean_time']:.2f}s   |   "
                f"Median: {stats['median_time']:.2f}s   |   "
                f"Std. dev: {stats['stdev_time']:.2f}s\n"
                f"Fastest: {stats['min_time']:.2f}s   |   Slowest: {stats['max_time']:.2f}s\n"
                f"Total errors: {stats['total_errors']}   |   "
                f"Error rate: {stats['error_rate']:.2f} per round\n"
                f"Max pattern complexity fully recalled: {stats['max_complexity_success']} cells"
            ))

    def export_data(self):
        if not self.data.results:
            messagebox.showinfo("No Data", "There is no data to export yet. Play a round first.")
            return
        path = os.path.join(os.getcwd(), CSV_FOLDER, CSV_FILENAME)
        self.data.export_csv(path)
        messagebox.showinfo("Exported", f"Data appended to:\n{path}")

    def reset_game(self):
        self.data.clear()
        self.listbox.delete(0, tk.END)
        self.results_label.config(text="")
        self.status_label.config(text="Round 0 of 0")
        self.feedback_label.config(text="")
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.start_button.config(state="normal", text="Start Game")
        self.game_frame_outer.pack_forget()

        self.participant_entry.delete(0, tk.END)
        self.session_entry.delete(0, tk.END)
        self.session_entry.insert(0, "1")
        self.setup_error_label.config(text="")
        self.setup_frame.pack(fill="both", expand=True)