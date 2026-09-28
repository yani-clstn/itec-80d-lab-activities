import os
import time
import tkinter as tk
from tkinter import messagebox

from config import (
    ROUNDS, FEEDBACK_PAUSE_MS, TILE_SIZES, AGE_GROUPS, EXPERIENCE_LEVELS,
    CSV_FOLDER, CSV_FILENAME,
    FONT, BG, CARD, CARD_ALT, BORDER, TEXT, TEXT_MUTED, TEXT_ON_LIGHT,
    ACCENT, ACCENT_HOVER, CELL_DEFAULT, CELL_HOVER, CELL_SHOWN,
    COLOR_CORRECT, COLOR_INCORRECT, COLOR_MISSED,
)
from game_logic import generate_pattern, score_round
from data_manager import DataManager
from help_dialog import show_help

WINDOW_W, WINDOW_H = 940, 640
PROGRESS_W = 340      # width of the memorize-time bar and the game area
GAME_AREA_H = 244     # fixed height so the layout never jumps between rounds

# (label shown to the user, key in DataManager.summary_stats())
STAT_ROWS = [
    ("Mean accuracy", "mean_accuracy"),
    ("Median accuracy", "median_accuracy"),
    ("Mean completion time", "mean_time"),
    ("Median completion time", "median_time"),
    ("Std. deviation (time)", "stdev_time"),
    ("Fastest round", "min_time"),
    ("Slowest round", "max_time"),
    ("Total errors", "total_errors"),
    ("Error rate", "error_rate"),
    ("Max tiles fully recalled", "max_complexity_success"),
]


# ---------------------------------------------------------------------
# Small styling helpers (kept at module level so every screen shares
# exactly the same look -> consistency)
# ---------------------------------------------------------------------
def style_button(btn, kind="secondary"):
    """Applies the shared button look. kind: 'primary' or 'secondary'."""
    if kind == "primary":
        bg, fg, hover = ACCENT, "#ffffff", ACCENT_HOVER
    else:
        bg, fg, hover = CARD_ALT, TEXT, BORDER
    btn._palette = (bg, fg, hover)
    btn.config(
        bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
        disabledforeground=TEXT_MUTED, relief="flat", bd=0,
        highlightthickness=0, cursor="hand2", font=(FONT, 10, "bold"),
        padx=16, pady=8,
    )


def set_enabled(btn, enabled):
    """Enables/disables a styled button and updates its look to match."""
    bg, fg, _ = btn._palette
    if enabled:
        btn.config(state="normal", bg=bg, fg=fg, cursor="hand2")
    else:
        btn.config(state="disabled", bg=CARD_ALT, cursor="arrow")


def make_button(parent, text, command, kind="secondary"):
    btn = tk.Button(parent, text=text, command=command)
    style_button(btn, kind)
    return btn


def style_entry(entry):
    entry.config(
        bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat",
        highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        font=(FONT, 11),
    )


def make_option_menu(parent, variable, options):
    menu = tk.OptionMenu(parent, variable, *options)
    menu.config(
        bg=CARD_ALT, fg=TEXT, activebackground=BORDER, activeforeground=TEXT,
        relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER,
        font=(FONT, 10), width=19, anchor="w",
    )
    menu["menu"].config(
        bg=CARD_ALT, fg=TEXT, activebackground=ACCENT, activeforeground="#ffffff",
        bd=0, font=(FONT, 10),
    )
    return menu


def make_card(parent, **pack_options):
    card = tk.Frame(
        parent, bg=CARD, padx=18, pady=12,
        highlightbackground=BORDER, highlightthickness=1,
    )
    card.pack(**pack_options)
    return card


class VisualPatternMemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Pattern Memory Game")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._center_window(WINDOW_W, WINDOW_H)

        self.data = DataManager()

        # participant/session info, collected once before testing starts
        self.participant_id = ""
        self.age_group = ""
        self.experience_level = ""
        self.session_number = 1

        # per-round state
        self.phase = "idle"          # idle | memorize | recall | feedback | done
        self.current_round = 0
        self.buttons = []
        self.correct_pattern = set()
        self.selected_cells = set()
        self.recall_start = None
        self._memorize_start = None

        # scheduled callbacks are tracked so Reset can cancel them safely
        self._tick_id = None
        self._flow_ids = []

        self._build_setup_screen()
        self._build_game_screen()
        self.root.bind("<Return>", self._on_return_key)

        self.setup_frame.pack(fill="both", expand=True)
        self.participant_entry.focus_set()

    def _center_window(self, width, height):
        x = (self.root.winfo_screenwidth() - width) // 2
        y = max(0, (self.root.winfo_screenheight() - height) // 2 - 20)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # -----------------------------------------------------------------
    # SETUP SCREEN: collects non-identifying participant info first
    # -----------------------------------------------------------------
    def _build_setup_screen(self):
        self.setup_frame = tk.Frame(self.root, bg=BG)

        card = tk.Frame(
            self.setup_frame, bg=CARD, padx=40, pady=32,
            highlightbackground=BORDER, highlightthickness=1,
        )
        card.pack(expand=True)

        tk.Label(
            card, text="Visual Pattern Memory", font=(FONT, 24, "bold"), bg=CARD, fg=TEXT
        ).pack()
        tk.Label(
            card, text="A quick memory test that takes about two minutes.",
            font=(FONT, 11), bg=CARD, fg=TEXT_MUTED,
        ).pack(pady=(4, 2))
        tk.Label(
            card, text="Enter the participant details below to begin. "
                       "No names or personal information are collected.",
            font=(FONT, 10), bg=CARD, fg=TEXT_MUTED, wraplength=400, justify="center",
        ).pack(pady=(0, 20))

        form = tk.Frame(card, bg=CARD)
        form.pack()

        def add_label(text, row):
            tk.Label(form, text=text, font=(FONT, 10), bg=CARD, fg=TEXT).grid(
                row=row, column=0, sticky="e", padx=(0, 14), pady=7
            )

        add_label("Participant code (e.g. P01)", 0)
        self.participant_entry = tk.Entry(form, width=23)
        style_entry(self.participant_entry)
        self.participant_entry.grid(row=0, column=1, sticky="ew", ipady=5)

        add_label("Age group", 1)
        self.age_var = tk.StringVar(value=AGE_GROUPS[0])
        make_option_menu(form, self.age_var, AGE_GROUPS).grid(row=1, column=1, sticky="ew")

        add_label("Experience with similar games", 2)
        self.experience_var = tk.StringVar(value=EXPERIENCE_LEVELS[0])
        make_option_menu(form, self.experience_var, EXPERIENCE_LEVELS).grid(
            row=2, column=1, sticky="ew"
        )

        add_label("Testing session number", 3)
        self.session_entry = tk.Entry(form, width=23)
        style_entry(self.session_entry)
        self.session_entry.insert(0, "1")
        self.session_entry.grid(row=3, column=1, sticky="ew", ipady=5)

        self.setup_error_label = tk.Label(
            card, text="", font=(FONT, 10, "bold"), bg=CARD, fg=COLOR_INCORRECT, height=2
        )
        self.setup_error_label.pack(pady=(10, 0))

        make_button(card, "Continue to Game", self._submit_setup, "primary").pack()

    def _submit_setup(self):
        pid = self.participant_entry.get().strip()
        session_text = self.session_entry.get().strip()

        # --- input validation (error prevention) ---
        if not pid:
            self.setup_error_label.config(text="Please enter a participant code, for example P01.")
            self.participant_entry.focus_set()
            return
        if not session_text.isdigit() or int(session_text) < 1:
            self.setup_error_label.config(text="Session number must be a whole number, 1 or higher.")
            self.session_entry.focus_set()
            return

        self.participant_id = pid.upper()
        self.age_group = self.age_var.get()
        self.experience_level = self.experience_var.get()
        self.session_number = int(session_text)

        self.setup_error_label.config(text="")
        self.setup_frame.pack_forget()
        self.game_screen.pack(fill="both", expand=True)

    # -----------------------------------------------------------------
    # MAIN GAME SCREEN
    # -----------------------------------------------------------------
    def _build_game_screen(self):
        self.game_screen = tk.Frame(self.root, bg=BG, padx=20, pady=16)

        # ---- header ----
        header = tk.Frame(self.game_screen, bg=BG)
        header.pack(fill="x")
        tk.Label(
            header, text="Visual Pattern Memory", font=(FONT, 20, "bold"), bg=BG, fg=TEXT
        ).pack(side="left")
        make_button(header, "?  How to Play", lambda: show_help(self.root)).pack(side="right")

        self.instructions_label = tk.Label(
            self.game_screen,
            text="Watch which tiles light up, then click the same tiles from memory.",
            font=(FONT, 11), bg=BG, fg=TEXT_MUTED, anchor="w",
        )
        self.instructions_label.pack(fill="x", pady=(2, 10))

        body = tk.Frame(self.game_screen, bg=BG)
        body.pack(fill="both", expand=True)

        self._build_play_card(body)
        self._build_data_card(body)

    def _build_play_card(self, parent):
        card = make_card(parent, side="left", fill="y")

        # phase badge + round info
        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x")
        self.phase_badge = tk.Label(
            top, text="READY", font=(FONT, 9, "bold"), bg=CARD_ALT, fg=TEXT_MUTED,
            padx=10, pady=3,
        )
        self.phase_badge.pack(side="left")
        self.round_label = tk.Label(
            top, text="Round 0 of 5", font=(FONT, 13, "bold"), bg=CARD, fg=TEXT
        )
        self.round_label.pack(side="right")

        self.detail_label = tk.Label(
            card, text="Press Start Game when you are ready.",
            font=(FONT, 10), bg=CARD, fg=TEXT_MUTED, anchor="w",
        )
        self.detail_label.pack(fill="x", pady=(6, 8))

        # memorize-time bar
        self.progress_canvas = tk.Canvas(
            card, width=PROGRESS_W, height=8, bg=CARD_ALT, highlightthickness=0
        )
        self.progress_canvas.pack()
        self.progress_fill = self.progress_canvas.create_rectangle(
            0, 0, 0, 8, fill=CELL_SHOWN, width=0
        )

        # live timer (counts down while memorizing, counts up while recalling)
        self.timer_caption = tk.Label(
            card, text="Timer", font=(FONT, 9), bg=CARD, fg=TEXT_MUTED
        )
        self.timer_caption.pack(pady=(8, 0))
        self.timer_label = tk.Label(
            card, text="0.00 s", font=(FONT, 24, "bold"), bg=CARD, fg=TEXT
        )
        self.timer_label.pack()

        # fixed-size game area: grids of any size are centered inside it
        area = tk.Frame(card, bg=CARD, width=PROGRESS_W, height=GAME_AREA_H)
        area.pack(pady=(4, 4))
        area.pack_propagate(False)
        self.game_frame = tk.Frame(area, bg=CARD)
        self.game_frame.place(relx=0.5, rely=0.5, anchor="center")

        # feedback area
        self.feedback_label = tk.Label(
            card, text="", font=(FONT, 11, "bold"), bg=CARD, fg=TEXT_MUTED,
            wraplength=PROGRESS_W, height=2, justify="center",
        )
        self.feedback_label.pack()

        self._build_legend(card)

        # main controls (same place every round)
        controls = tk.Frame(card, bg=CARD)
        controls.pack(pady=(10, 0))
        self.start_button = make_button(controls, "Start Game", self.start_game, "primary")
        self.start_button.pack(side="left", padx=6)
        self.submit_button = make_button(controls, "Submit Answer", self.submit_answer, "primary")
        self.submit_button.pack(side="left", padx=6)
        set_enabled(self.submit_button, False)

    def _build_legend(self, parent):
        legend = tk.Frame(parent, bg=CARD)
        legend.pack(pady=(2, 0))
        for color, symbol, label in [
            (COLOR_CORRECT, "✓", "Correct"),
            (COLOR_INCORRECT, "✗", "Wrong"),
            (COLOR_MISSED, "!", "Missed"),
        ]:
            tk.Label(
                legend, text=symbol, width=2, font=(FONT, 9, "bold"),
                bg=color, fg=TEXT_ON_LIGHT,
            ).pack(side="left", padx=(8, 3))
            tk.Label(legend, text=label, font=(FONT, 9), bg=CARD, fg=TEXT_MUTED).pack(side="left")

    def _build_data_card(self, parent):
        card = make_card(parent, side="left", fill="both", expand=True, padx=(14, 0))

        tk.Label(
            card, text="Recorded interaction data", font=(FONT, 12, "bold"),
            bg=CARD, fg=TEXT, anchor="w",
        ).pack(fill="x")
        self.listbox = tk.Listbox(
            card, height=5, bg=CARD_ALT, fg=TEXT, selectbackground=ACCENT,
            selectforeground="#ffffff", relief="flat", bd=0, font=("Courier", 10),
            activestyle="none", highlightthickness=8,
            highlightbackground=CARD_ALT, highlightcolor=CARD_ALT,
        )
        self.listbox.pack(fill="x", pady=(6, 12))

        tk.Label(
            card, text="Session summary", font=(FONT, 12, "bold"),
            bg=CARD, fg=TEXT, anchor="w",
        ).pack(fill="x")
        stats = tk.Frame(card, bg=CARD)
        stats.pack(fill="x", pady=(6, 0))
        stats.columnconfigure(1, weight=1)
        self.stat_vars = {}
        for row, (label, key) in enumerate(STAT_ROWS):
            self.stat_vars[key] = tk.StringVar(value="—")
            tk.Label(stats, text=label, font=(FONT, 10), bg=CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=0, sticky="w", pady=2
            )
            tk.Label(
                stats, textvariable=self.stat_vars[key], font=(FONT, 10, "bold"),
                bg=CARD, fg=TEXT, anchor="e",
            ).grid(row=row, column=1, sticky="e", pady=2)

        bottom = tk.Frame(card, bg=CARD)
        bottom.pack(side="bottom", fill="x", pady=(12, 0))
        make_button(bottom, "Reset / New Participant", self.reset_game).pack(side="left")
        make_button(bottom, "Export CSV", self.export_data).pack(side="left", padx=8)
        make_button(bottom, "Exit", self.root.destroy).pack(side="right")

    # -----------------------------------------------------------------
    # SMALL UI HELPERS
    # -----------------------------------------------------------------
    def _set_phase(self, text, bg, fg):
        self.phase_badge.config(text=text, bg=bg, fg=fg)

    def _draw_progress(self, fraction):
        self.progress_canvas.coords(self.progress_fill, 0, 0, PROGRESS_W * fraction, 8)

    def _clear_stats(self):
        for var in self.stat_vars.values():
            var.set("—")

    def _clear_game_area(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.buttons = []

    def _cancel_tick(self):
        if self._tick_id is not None:
            self.root.after_cancel(self._tick_id)
            self._tick_id = None

    def _cancel_pending(self):
        """Stops every scheduled timer/callback (used by Reset and Start)."""
        self._cancel_tick()
        for after_id in self._flow_ids:
            self.root.after_cancel(after_id)
        self._flow_ids = []

    def _on_return_key(self, event):
        # Keyboard shortcut: Enter submits during the recall phase
        if self.phase == "recall":
            self.submit_answer()

    # -----------------------------------------------------------------
    # GAME FLOW
    # -----------------------------------------------------------------
    def start_game(self):
        self._cancel_pending()
        self.current_round = 0
        self.data.clear()
        self.listbox.delete(0, tk.END)
        self._clear_stats()
        set_enabled(self.start_button, False)
        self.next_round()

    def next_round(self):
        if self.current_round >= len(ROUNDS):
            self._finish_game()
            return

        config = ROUNDS[self.current_round]
        self.phase = "memorize"
        self.selected_cells = set()
        set_enabled(self.submit_button, False)

        self.round_label.config(text=f"Round {self.current_round + 1} of {len(ROUNDS)}")
        self.detail_label.config(
            text=f"{config['grid']}×{config['grid']} grid  ·  {config['cells']} tiles to remember"
        )
        self._set_phase("MEMORIZE", CELL_SHOWN, TEXT_ON_LIGHT)
        self.timer_caption.config(text="Memorize: time left")
        self.feedback_label.config(text="Remember which tiles light up…", fg=TEXT_MUTED)

        self._build_grid(config["grid"])
        self.correct_pattern = generate_pattern(config["grid"], config["cells"])
        for (r, c) in self.correct_pattern:
            self.buttons[r][c].config(bg=CELL_SHOWN)

        self._memorize_start = time.perf_counter()
        self._tick_memorize(config["display_time"])
        self._flow_ids.append(self.root.after(config["display_time"], self._begin_recall))

    def _build_grid(self, grid_size):
        self._clear_game_area()
        size = TILE_SIZES.get(grid_size, 46)
        for r in range(grid_size):
            row_buttons = []
            for c in range(grid_size):
                # A fixed-size frame holds the button, so a tile never changes
                # size when a symbol appears on it and the grid never shifts.
                tile = tk.Frame(self.game_frame, width=size, height=size, bg=CARD)
                tile.grid(row=r, column=c, padx=3, pady=3)
                tile.pack_propagate(False)
                btn = tk.Button(
                    tile, text="", bg=CELL_DEFAULT, activebackground=CELL_DEFAULT,
                    fg=TEXT_ON_LIGHT, disabledforeground=TEXT_ON_LIGHT,
                    relief="flat", bd=0, highlightthickness=0,
                    font=(FONT, 16, "bold"), state="disabled",
                    command=lambda row=r, col=c: self._toggle_cell(row, col),
                )
                btn.pack(fill="both", expand=True)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def _tick_memorize(self, duration_ms):
        """Updates the countdown and progress bar while the pattern is visible."""
        if self.phase != "memorize":
            return
        elapsed_ms = (time.perf_counter() - self._memorize_start) * 1000
        remaining_ms = max(0.0, duration_ms - elapsed_ms)
        self._draw_progress(remaining_ms / duration_ms)
        self.timer_label.config(text=f"{remaining_ms / 1000:.1f} s")
        self._tick_id = self.root.after(50, lambda: self._tick_memorize(duration_ms))

    def _begin_recall(self):
        self._cancel_tick()
        self.phase = "recall"
        self._draw_progress(0)

        for row in self.buttons:
            for btn in row:
                btn.config(
                    bg=CELL_DEFAULT, activebackground=CELL_HOVER, state="normal",
                    cursor="hand2", text="",
                )

        self._set_phase("RECALL", ACCENT, "#ffffff")
        self.timer_caption.config(text="Recall: your time")
        self._update_selection_hint()
        set_enabled(self.submit_button, True)

        self.recall_start = time.perf_counter()
        self._tick_recall()

    def _tick_recall(self):
        """Live stopwatch shown while the user is clicking tiles."""
        if self.phase != "recall":
            return
        elapsed = time.perf_counter() - self.recall_start
        self.timer_label.config(text=f"{elapsed:.2f} s")
        self._tick_id = self.root.after(50, self._tick_recall)

    def _update_selection_hint(self):
        needed = ROUNDS[self.current_round]["cells"]
        chosen = len(self.selected_cells)
        self.feedback_label.config(
            text=f"Selected {chosen} of {needed} tiles.\nPress Submit (or Enter) when ready.",
            fg=TEXT,
        )

    def _toggle_cell(self, row, col):
        if self.phase != "recall":
            return
        cell = (row, col)
        btn = self.buttons[row][col]
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
            btn.config(bg=CELL_DEFAULT, activebackground=CELL_HOVER)
        else:
            self.selected_cells.add(cell)
            btn.config(bg=CELL_SHOWN, activebackground=CELL_SHOWN)
        self._update_selection_hint()

    def submit_answer(self):
        if self.phase != "recall":
            return

        # --- input validation: an empty answer is almost certainly a mis-click ---
        if not self.selected_cells:
            self.feedback_label.config(
                text="Select at least one tile before submitting.", fg=COLOR_MISSED
            )
            return

        completion_time = time.perf_counter() - self.recall_start
        self._cancel_tick()
        self.phase = "feedback"
        self.timer_label.config(text=f"{completion_time:.2f} s")
        self.timer_caption.config(text="Your time")
        set_enabled(self.submit_button, False)

        score = score_round(self.correct_pattern, self.selected_cells)
        self._show_round_feedback(score)

        config = ROUNDS[self.current_round]
        record = {
            "participant_id": self.participant_id,
            "age_group": self.age_group,
            "experience_level": self.experience_level,
            "session": self.session_number,
            "round": self.current_round + 1,
            "grid_size": config["grid"],
            "pattern_complexity": config["cells"],
            "display_time_ms": config["display_time"],
            "completion_time": round(completion_time, 3),
            **score,
        }
        self.data.add_record(record)
        self.listbox.insert(tk.END, self.data.listbox_line(record))
        self.listbox.see(tk.END)

        self.current_round += 1
        self._flow_ids.append(self.root.after(FEEDBACK_PAUSE_MS, self.next_round))

    def _show_round_feedback(self, score):
        """Colors every tile and shows a plain-language result message."""
        for row in self.buttons:
            for btn in row:
                btn.config(state="disabled", cursor="arrow")  # no edits after submit

        # symbols as well as colors, so the result never depends on color alone
        for (r, c) in self.correct_pattern & self.selected_cells:
            self.buttons[r][c].config(bg=COLOR_CORRECT, text="✓")
        for (r, c) in self.selected_cells - self.correct_pattern:
            self.buttons[r][c].config(bg=COLOR_INCORRECT, text="✗")
        for (r, c) in self.correct_pattern - self.selected_cells:
            self.buttons[r][c].config(bg=COLOR_MISSED, text="!")

        total = len(self.correct_pattern)
        if score["total_errors"] == 0:
            self._set_phase("PERFECT", COLOR_CORRECT, TEXT_ON_LIGHT)
            self.feedback_label.config(
                text=f"Perfect! All {total} tiles correct.", fg=COLOR_CORRECT
            )
        else:
            self._set_phase("RESULT", COLOR_INCORRECT, TEXT_ON_LIGHT)
            self.feedback_label.config(
                text=f"{score['correct_cells']} of {total} found  ·  "
                     f"{score['incorrect_cells']} wrong  ·  {score['missed_cells']} missed\n"
                     f"Accuracy: {score['accuracy']:.0f}%",
                fg=COLOR_INCORRECT,
            )
        self.root.bell()  # simple audio feedback

    # -----------------------------------------------------------------
    # RESULTS / STATISTICS
    # -----------------------------------------------------------------
    def _finish_game(self):
        self.phase = "done"
        stats = self.data.summary_stats()

        self._set_phase("COMPLETE", COLOR_CORRECT, TEXT_ON_LIGHT)
        self.round_label.config(text="All rounds done")
        self.detail_label.config(text="Your results are in the summary on the right.")
        self.timer_caption.config(text="")
        self.timer_label.config(text="")
        self._draw_progress(0)
        self._clear_game_area()

        if stats:
            tk.Label(
                self.game_frame, text=f"{stats['mean_accuracy']:.0f}%",
                font=(FONT, 44, "bold"), bg=CARD, fg=COLOR_CORRECT,
            ).pack()
            tk.Label(
                self.game_frame, text="average accuracy", font=(FONT, 11),
                bg=CARD, fg=TEXT_MUTED,
            ).pack()
            self._show_stats(stats)

        self.feedback_label.config(
            text="Great job! Export the CSV, then start a new participant.", fg=TEXT
        )
        self.start_button.config(text="Play Again")
        set_enabled(self.start_button, True)

    def _show_stats(self, stats):
        text_values = {
            "mean_accuracy": f"{stats['mean_accuracy']:.1f}%",
            "median_accuracy": f"{stats['median_accuracy']:.1f}%",
            "mean_time": f"{stats['mean_time']:.2f} s",
            "median_time": f"{stats['median_time']:.2f} s",
            "stdev_time": f"{stats['stdev_time']:.2f} s",
            "min_time": f"{stats['min_time']:.2f} s",
            "max_time": f"{stats['max_time']:.2f} s",
            "total_errors": str(stats["total_errors"]),
            "error_rate": f"{stats['error_rate']:.2f} per round",
            "max_complexity_success": f"{stats['max_complexity_success']} tiles",
        }
        for key, value in text_values.items():
            self.stat_vars[key].set(value)

    def export_data(self):
        if not self.data.results:
            messagebox.showinfo("No data yet", "Play at least one round before exporting.")
            return
        path = os.path.join(os.getcwd(), CSV_FOLDER, CSV_FILENAME)
        self.data.export_csv(path)
        messagebox.showinfo("Exported", f"Data saved to:\n{path}")

    def reset_game(self):
        self._cancel_pending()
        self.phase = "idle"
        self.data.clear()
        self.listbox.delete(0, tk.END)
        self._clear_stats()
        self._clear_game_area()
        self._draw_progress(0)

        self._set_phase("READY", CARD_ALT, TEXT_MUTED)
        self.round_label.config(text="Round 0 of 5")
        self.detail_label.config(text="Press Start Game when you are ready.")
        self.timer_caption.config(text="Timer")
        self.timer_label.config(text="0.00 s")
        self.feedback_label.config(text="")
        self.start_button.config(text="Start Game")
        set_enabled(self.start_button, True)
        set_enabled(self.submit_button, False)

        self.game_screen.pack_forget()
        self.participant_entry.delete(0, tk.END)
        self.session_entry.delete(0, tk.END)
        self.session_entry.insert(0, "1")
        self.setup_error_label.config(text="")
        self.setup_frame.pack(fill="both", expand=True)
        self.participant_entry.focus_set()