import os
import time
import tkinter as tk
from tkinter import messagebox

from config import (
    ROUNDS, FEEDBACK_PAUSE_MS, TILE_SIZES, AGE_GROUPS, EXPERIENCE_LEVELS,
    CSV_FOLDER, CSV_FILENAME, FONT, FONT_SCALES, THEMES, DEFAULT_THEME,
)
from game_logic import generate_pattern, score_round
from data_manager import DataManager
from help_dialog import show_help
from chart import draw_round_chart

WINDOW_W, WINDOW_H = 980, 660
MIN_W, MIN_H = 900, 660
PROGRESS_W = 340       # width of the play card's inner content
GAME_AREA_H = 244      # fixed height so the grid area never jumps between rounds
CHART_H = 100

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


class VisualPatternMemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Pattern Memory Game")
        self.root.minsize(MIN_W, MIN_H)
        self.root.resizable(True, True)
        self._center_window(WINDOW_W, WINDOW_H)

        # ---- theme / text-size state ----
        self.theme_name = DEFAULT_THEME
        self.font_scale_idx = FONT_SCALES.index(1.0)
        self._themed = []   # widgets registered for re-coloring on theme toggle
        self._sized = []    # widgets registered for re-scaling on font change

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
        self.data_visible = False

        # scheduled callbacks are tracked so Reset can cancel them safely
        self._tick_id = None
        self._flow_ids = []

        self._build_setup_screen()
        self._build_game_screen()
        self.root.bind("<Return>", self._on_return_key)

        self.setup_frame.pack(fill="both", expand=True)
        self.participant_entry.focus_set()

        self._apply_theme()
        self._apply_font_scale()

    def _center_window(self, width, height):
        x = (self.root.winfo_screenwidth() - width) // 2
        y = max(0, (self.root.winfo_screenheight() - height) // 2 - 20)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ===================================================================
    # THEME + FONT-SCALE ENGINE
    # Every themed/sized widget is registered once at creation time, and
    # these two apply-methods repaint / rescale the whole registry when
    # the user toggles the theme or the text size.
    # ===================================================================
    def theme(self):
        return THEMES[self.theme_name]

    def track(self, widget, kind, **extra):
        item = {"widget": widget, "kind": kind, **extra}
        self._themed.append(item)
        self._restyle_item(item)  # style immediately - don't wait for the next toggle
        return widget

    def track_font(self, widget, size, weight="normal"):
        item = {"widget": widget, "size": size, "weight": weight}
        self._sized.append(item)
        scale = FONT_SCALES[self.font_scale_idx]
        widget.config(font=(FONT, max(7, round(size * scale)), weight))
        return widget

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self._apply_theme()
        self._retheme_grid()
        if self.phase == "done":
            self._draw_chart()

    def adjust_font(self, delta):
        idx = max(0, min(len(FONT_SCALES) - 1, self.font_scale_idx + delta))
        if idx == self.font_scale_idx:
            return
        self.font_scale_idx = idx
        self._apply_font_scale()

    def _apply_font_scale(self):
        scale = FONT_SCALES[self.font_scale_idx]
        alive = []
        for item in self._sized:
            w = item["widget"]
            if not w.winfo_exists():
                continue  # widget was destroyed (e.g. a grid tile from a past round)
            alive.append(item)
            size = max(7, round(item["size"] * scale))
            w.config(font=(FONT, size, item["weight"]))
        self._sized = alive
        self.font_scale_label.config(text=f"{int(round(scale * 100))}%")

    def _restyle_item(self, item):
        w, kind = item["widget"], item["kind"]
        if not w.winfo_exists():
            return
        t = self.theme()
        if kind == "bg":
            w.config(bg=t["BG"])
        elif kind == "card":
            w.config(bg=t["CARD"], highlightbackground=t["BORDER"])
        elif kind == "card_alt":
            w.config(bg=t["CARD_ALT"])
        elif kind == "text":
            w.config(bg=t[item.get("bg_key", "CARD")], fg=t["TEXT"])
        elif kind == "muted":
            w.config(bg=t[item.get("bg_key", "CARD")], fg=t["TEXT_MUTED"])
        elif kind == "entry":
            w.config(
                bg=t["CARD_ALT"], fg=t["TEXT"], insertbackground=t["TEXT"],
                highlightbackground=t["BORDER"], highlightcolor=t["ACCENT"],
            )
        elif kind == "optionmenu":
            w.config(
                bg=t["CARD_ALT"], fg=t["TEXT"], activebackground=t["BORDER"],
                activeforeground=t["TEXT"], highlightbackground=t["BORDER"],
            )
            w["menu"].config(
                bg=t["CARD_ALT"], fg=t["TEXT"],
                activebackground=t["ACCENT"], activeforeground="#ffffff",
            )
        elif kind == "listbox":
            w.config(
                bg=t["CARD_ALT"], fg=t["TEXT"], selectbackground=t["ACCENT"],
                selectforeground="#ffffff", highlightbackground=t["CARD_ALT"],
                highlightcolor=t["CARD_ALT"],
            )
        elif kind == "canvas_track":
            w.config(bg=t["CARD_ALT"])
        elif kind == "button_primary":
            self._style_button(w, t["ACCENT"], "#ffffff", t["ACCENT_HOVER"])
        elif kind == "button_secondary":
            self._style_button(w, t["CARD_ALT"], t["TEXT"], t["BORDER"])

    def _apply_theme(self):
        alive = []
        for item in self._themed:
            if not item["widget"].winfo_exists():
                continue  # widget was destroyed (e.g. a grid tile from a past round)
            alive.append(item)
            self._restyle_item(item)
        self._themed = alive
        self.theme_button.config(
            text="\u2600  Light" if self.theme_name == "dark" else "\u263e  Dark"
        )

    def _style_button(self, btn, bg, fg, hover):
        btn._palette = (bg, fg, hover)
        enabled = str(btn.cget("state")) != "disabled"
        if enabled:
            btn.config(bg=bg, fg=fg, activebackground=hover, activeforeground=fg)
        else:
            t = self.theme()
            btn.config(bg=t["CARD_ALT"], fg=t["TEXT_MUTED"])

    def set_enabled(self, btn, enabled):
        t = self.theme()
        if enabled:
            bg, fg, _ = btn._palette
            btn.config(state="normal", bg=bg, fg=fg, cursor="hand2")
        else:
            btn.config(state="disabled", bg=t["CARD_ALT"], fg=t["TEXT_MUTED"], cursor="arrow")

    # ---- small widget-creation helpers, all theme/font aware ----
    def make_frame(self, parent, kind="bg", **kwargs):
        frame = tk.Frame(parent, **kwargs)
        self.track(frame, kind)
        return frame

    def make_card(self, parent, padx=18, pady=12, **pack_options):
        card = self.make_frame(
            parent, kind="card", padx=padx, pady=pady, highlightthickness=1
        )
        card.pack(**pack_options)
        return card

    def make_label(self, parent, text, kind="text", size=10, weight="normal", bg_key="CARD", **kwargs):
        lbl = tk.Label(parent, text=text, **kwargs)
        self.track(lbl, kind, bg_key=bg_key)
        self.track_font(lbl, size, weight)
        return lbl

    def make_button(self, parent, text, command, kind="secondary", size=10, padx=16, pady=8):
        btn = tk.Button(
            parent, text=text, command=command, relief="flat", bd=0,
            highlightthickness=0, cursor="hand2", padx=padx, pady=pady,
        )
        self.track_font(btn, size, "bold")
        self.track(btn, f"button_{kind}")
        return btn

    def make_entry(self, parent, width=23):
        entry = tk.Entry(parent, width=width, relief="flat", highlightthickness=1)
        self.track(entry, "entry")
        self.track_font(entry, 11)
        return entry

    def make_option_menu(self, parent, variable, options):
        menu = tk.OptionMenu(parent, variable, *options)
        menu.config(relief="flat", bd=0, highlightthickness=1, width=19, anchor="w")
        self.track(menu, "optionmenu")
        self.track_font(menu, 10)
        return menu

    # -----------------------------------------------------------------
    # SETUP SCREEN: collects non-identifying participant info first
    # -----------------------------------------------------------------
    def _build_setup_screen(self):
        self.setup_frame = self.make_frame(self.root, kind="bg")
        card = self.make_card(self.setup_frame, padx=40, pady=32, expand=True)

        self.make_label(card, "Visual Pattern Memory", "text", 24, "bold").pack()
        self.make_label(
            card, "A quick memory test that takes about two minutes.", "muted", 11
        ).pack(pady=(4, 2))
        self.make_label(
            card,
            "Enter the participant details below to begin. No names or personal "
            "information are collected.",
            "muted", 10, wraplength=400, justify="center",
        ).pack(pady=(0, 20))

        form = self.make_frame(card, kind="card")
        form.pack()
        form.columnconfigure(1, weight=1)

        def add_row_label(text, row):
            self.make_label(form, text, "text", 10).grid(
                row=row, column=0, sticky="e", padx=(0, 14), pady=7
            )

        add_row_label("Participant code (e.g. P01)", 0)
        self.participant_entry = self.make_entry(form)
        self.participant_entry.grid(row=0, column=1, sticky="ew", ipady=5)

        add_row_label("Age group", 1)
        self.age_var = tk.StringVar(value=AGE_GROUPS[0])
        self.make_option_menu(form, self.age_var, AGE_GROUPS).grid(row=1, column=1, sticky="ew")

        add_row_label("Experience with similar games", 2)
        self.experience_var = tk.StringVar(value=EXPERIENCE_LEVELS[0])
        self.make_option_menu(form, self.experience_var, EXPERIENCE_LEVELS).grid(
            row=2, column=1, sticky="ew"
        )

        add_row_label("Testing session number", 3)
        self.session_entry = self.make_entry(form)
        self.session_entry.insert(0, "1")
        self.session_entry.grid(row=3, column=1, sticky="ew", ipady=5)

        self.setup_error_label = self.make_label(
            card, "", "text", 10, "bold", height=2
        )
        self.setup_error_label.pack(pady=(10, 0))

        self.make_button(card, "Continue to Game", self._submit_setup, "primary").pack()

    def _submit_setup(self):
        pid = self.participant_entry.get().strip()
        session_text = self.session_entry.get().strip()
        t = self.theme()

        # --- input validation (error prevention) ---
        if not pid:
            self.setup_error_label.config(
                text="Please enter a participant code, for example P01.", fg=t["COLOR_INCORRECT"]
            )
            self.participant_entry.focus_set()
            return
        if not session_text.isdigit() or int(session_text) < 1:
            self.setup_error_label.config(
                text="Session number must be a whole number, 1 or higher.", fg=t["COLOR_INCORRECT"]
            )
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
        self.game_screen = self.make_frame(self.root, kind="bg", padx=20, pady=16)

        self._build_header(self.game_screen)

        self.instructions_label = self.make_label(
            self.game_screen,
            "Watch which tiles light up, then click the same tiles from memory.",
            "muted", 11, bg_key="BG", anchor="w",
        )
        self.instructions_label.pack(fill="x", pady=(2, 10))

        self.body = self.make_frame(self.game_screen, kind="bg")
        self.body.pack(fill="both", expand=True)
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        self._build_play_card(self.body)
        self._build_data_card(self.body)

        # data panel starts collapsed; game area starts centered
        self.play_card.grid(row=0, column=0, sticky="n")
        self.body.grid_columnconfigure(0, weight=1)

    def _build_header(self, parent):
        header = self.make_frame(parent, kind="bg")
        header.pack(fill="x")

        self.make_label(
            header, "Visual Pattern Memory", "text", 20, "bold", bg_key="BG"
        ).pack(side="left")

        controls = self.make_frame(header, kind="bg")
        controls.pack(side="right")

        self.help_button = self.make_button(
            controls, "?  Help", lambda: show_help(self.root, self.theme()),
            padx=10, pady=6,
        )
        self.help_button.pack(side="right")

        self.view_data_button = self.make_button(
            controls, "Data  \u25be", self.toggle_data_view, padx=10, pady=6
        )
        self.view_data_button.pack(side="right", padx=8)

        self.theme_button = self.make_button(
            controls, "\u2600  Light", self.toggle_theme, padx=10, pady=6
        )
        self.theme_button.pack(side="right", padx=(0, 8))

        font_group = self.make_frame(controls, kind="card_alt", padx=2, pady=2)
        font_group.pack(side="right", padx=(0, 8))
        self.make_button(
            font_group, "A-", lambda: self.adjust_font(-1), padx=8, pady=4
        ).pack(side="left")
        self.font_scale_label = self.make_label(
            font_group, "100%", "muted", 9, bg_key="CARD_ALT"
        )
        self.font_scale_label.pack(side="left", padx=6)
        self.make_button(
            font_group, "A+", lambda: self.adjust_font(1), padx=8, pady=4
        ).pack(side="left")

    def _build_play_card(self, parent):
        card = self.make_card(parent)
        self.play_card = card

        top = self.make_frame(card, kind="card")
        top.pack(fill="x")
        self.phase_badge = self.make_label(
            top, "READY", "muted", 9, "bold", bg_key="CARD_ALT", padx=10, pady=3
        )
        self.phase_badge.pack(side="left")
        self.round_label = self.make_label(top, "Round 0 of 5", "text", 13, "bold")
        self.round_label.pack(side="right")

        self.detail_label = self.make_label(
            card, "Press Start Game when you are ready.", "muted", 10, anchor="w"
        )
        self.detail_label.pack(fill="x", pady=(6, 8))

        self.progress_canvas = tk.Canvas(card, width=PROGRESS_W, height=8, highlightthickness=0)
        self.track(self.progress_canvas, "canvas_track")
        self.progress_canvas.pack()
        self.progress_fill = self.progress_canvas.create_rectangle(
            0, 0, 0, 8, fill=self.theme()["CELL_SHOWN"], width=0
        )

        self.timer_caption = self.make_label(card, "Timer", "muted", 9)
        self.timer_caption.pack(pady=(8, 0))
        self.timer_label = self.make_label(card, "0.00 s", "text", 24, "bold")
        self.timer_label.pack()

        area = self.make_frame(card, kind="card", width=PROGRESS_W, height=GAME_AREA_H)
        area.pack(pady=(4, 4))
        area.pack_propagate(False)
        self.game_frame = self.make_frame(area, kind="card")
        self.game_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.feedback_label = self.make_label(
            card, "", "muted", 11, "bold", wraplength=PROGRESS_W, height=2, justify="center"
        )
        self.feedback_label.pack()

        self._build_legend(card)

        controls = self.make_frame(card, kind="card")
        controls.pack(pady=(10, 0))
        self.start_button = self.make_button(controls, "Start Game", self.start_game, "primary")
        self.start_button.pack(side="left", padx=6)
        self.submit_button = self.make_button(
            controls, "Submit Answer", self.submit_answer, "primary"
        )
        self.submit_button.pack(side="left", padx=6)
        self.set_enabled(self.submit_button, False)

    def _build_legend(self, parent):
        legend = self.make_frame(parent, kind="card")
        legend.pack(pady=(2, 0))
        t = self.theme()
        for color_key, symbol, label in [
            ("COLOR_CORRECT", "\u2713", "Correct"),
            ("COLOR_INCORRECT", "\u2717", "Wrong"),
            ("COLOR_MISSED", "!", "Missed"),
        ]:
            tk.Label(
                legend, text=symbol, width=2, font=(FONT, 9, "bold"),
                bg=t[color_key], fg=t["TEXT_ON_LIGHT"],
            ).pack(side="left", padx=(8, 3))
            self.make_label(legend, label, "muted", 9).pack(side="left")

    def _build_data_card(self, parent):
        # Outer frame is what gets shown/hidden by the View Data toggle.
        # Its content is scrollable, so it never clips - no matter how tall
        # the text size or how short the window gets.
        outer = self.make_frame(parent, kind="card", padx=0, pady=0, highlightthickness=1)
        self.data_card = outer

        scroll_canvas = tk.Canvas(outer, highlightthickness=0)
        self.track(scroll_canvas, "card")
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        card = self.make_frame(scroll_canvas, kind="card", padx=18, pady=12)
        card_id = scroll_canvas.create_window((0, 0), window=card, anchor="nw")

        def on_card_resize(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def on_canvas_resize(event):
            scroll_canvas.itemconfig(card_id, width=event.width)

        card.bind("<Configure>", on_card_resize)
        scroll_canvas.bind("<Configure>", on_canvas_resize)

        def scroll(event, direction=None):
            amount = direction if direction is not None else int(-1 * (event.delta / 120))
            scroll_canvas.yview_scroll(amount, "units")

        def bind_wheel(widget):
            widget.bind("<MouseWheel>", scroll)
            widget.bind("<Button-4>", lambda e: scroll(e, -1))
            widget.bind("<Button-5>", lambda e: scroll(e, 1))

        self.make_label(card, "Accuracy per round", "text", 12, "bold", anchor="w").pack(fill="x")
        self.chart_canvas = tk.Canvas(card, height=CHART_H, highlightthickness=0)
        self.track(self.chart_canvas, "canvas_track")
        self.chart_canvas.pack(fill="x", pady=(6, 14))
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart())

        self.make_label(card, "Recorded interaction data", "text", 12, "bold", anchor="w").pack(fill="x")
        self.listbox = tk.Listbox(
            card, height=5, relief="flat", bd=0, font=("Courier", 10), activestyle="none",
            highlightthickness=8,
        )
        self.track(self.listbox, "listbox")
        self.listbox.pack(fill="x", pady=(6, 14))

        self.make_label(card, "Session summary", "text", 12, "bold", anchor="w").pack(fill="x")
        stats = self.make_frame(card, kind="card")
        stats.pack(fill="x", pady=(6, 0))
        stats.columnconfigure(1, weight=1)
        self.stat_vars = {}
        for row, (label, key) in enumerate(STAT_ROWS):
            self.stat_vars[key] = tk.StringVar(value="\u2014")
            self.make_label(stats, label, "muted", 10, anchor="w").grid(
                row=row, column=0, sticky="w", pady=2
            )
            self.make_label(
                stats, "", "text", 10, "bold", anchor="e", textvariable=self.stat_vars[key]
            ).grid(row=row, column=1, sticky="e", pady=2)

        bottom = self.make_frame(card, kind="card")
        bottom.pack(fill="x", pady=(14, 0))
        self.make_button(bottom, "Reset / New Participant", self.reset_game).pack(side="left")
        self.make_button(bottom, "Export CSV", self.export_data).pack(side="left", padx=8)
        self.make_button(bottom, "Exit", self.root.destroy).pack(side="right")

        # Mouse-wheel scrolling works no matter which child widget is hovered
        for widget in [scroll_canvas, card, stats, bottom]:
            bind_wheel(widget)
        for widget in card.winfo_children():
            bind_wheel(widget)
        for widget in stats.winfo_children():
            bind_wheel(widget)

    # -----------------------------------------------------------------
    # DATA PANEL VISIBILITY (keeps gameplay uncluttered by default)
    # -----------------------------------------------------------------
    def _set_data_visible(self, visible):
        self.data_visible = visible
        if visible:
            self.data_card.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
            self.body.grid_columnconfigure(0, weight=0)
            self.play_card.grid_configure(sticky="ns")
            self.view_data_button.config(text="Data  \u25b4")
            self._draw_chart()
        else:
            self.data_card.grid_remove()
            self.body.grid_columnconfigure(0, weight=1)
            self.play_card.grid_configure(sticky="n")
            self.view_data_button.config(text="Data  \u25be")

    def toggle_data_view(self):
        self._set_data_visible(not self.data_visible)

    # -----------------------------------------------------------------
    # SMALL UI HELPERS
    # -----------------------------------------------------------------
    def _set_phase(self, text, color_key):
        t = self.theme()
        self.phase_badge.config(text=text, bg=t[color_key], fg=t["TEXT_ON_LIGHT"])

    def _draw_progress(self, fraction):
        width = self.progress_canvas.winfo_width() or PROGRESS_W
        self.progress_canvas.coords(self.progress_fill, 0, 0, width * fraction, 8)

    def _draw_chart(self):
        draw_round_chart(self.chart_canvas, self.data.results, self.theme())

    def _clear_stats(self):
        for var in self.stat_vars.values():
            var.set("\u2014")

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
        if self.phase == "recall":
            self.submit_answer()

    def _paint_tile(self, btn, state):
        """Colors a grid tile according to its semantic state, so retheming
        can repaint every tile correctly without guessing its previous color."""
        t = self.theme()
        btn._tile_state = state
        btn.config(fg=t["TEXT_ON_LIGHT"], disabledforeground=t["TEXT_ON_LIGHT"])
        if state == "default":
            btn.config(bg=t["CELL_DEFAULT"], activebackground=t["CELL_HOVER"], text="")
        elif state == "shown":
            btn.config(bg=t["CELL_SHOWN"], activebackground=t["CELL_SHOWN"], text="")
        elif state == "correct":
            btn.config(bg=t["COLOR_CORRECT"], text="\u2713")
        elif state == "incorrect":
            btn.config(bg=t["COLOR_INCORRECT"], text="\u2717")
        elif state == "missed":
            btn.config(bg=t["COLOR_MISSED"], text="!")

    def _retheme_grid(self):
        for row in self.buttons:
            for btn in row:
                self._paint_tile(btn, getattr(btn, "_tile_state", "default"))

    # -----------------------------------------------------------------
    # GAME FLOW
    # -----------------------------------------------------------------
    def start_game(self):
        self._cancel_pending()
        self.current_round = 0
        self.data.clear()
        self.listbox.delete(0, tk.END)
        self._clear_stats()
        self._draw_chart()
        self.set_enabled(self.start_button, False)
        self.next_round()

    def next_round(self):
        if self.current_round >= len(ROUNDS):
            self._finish_game()
            return

        config = ROUNDS[self.current_round]
        self.phase = "memorize"
        self.selected_cells = set()
        self.set_enabled(self.submit_button, False)

        self.round_label.config(text=f"Round {self.current_round + 1} of {len(ROUNDS)}")
        self.detail_label.config(
            text=f"{config['grid']}\u00d7{config['grid']} grid  \u00b7  "
                 f"{config['cells']} tiles to remember"
        )
        self._set_phase("MEMORIZE", "CELL_SHOWN")
        self.timer_caption.config(text="Memorize: time left")
        t = self.theme()
        self.feedback_label.config(text="Remember which tiles light up\u2026", fg=t["TEXT_MUTED"])

        self._build_grid(config["grid"])
        self.correct_pattern = generate_pattern(config["grid"], config["cells"])
        for (r, c) in self.correct_pattern:
            self._paint_tile(self.buttons[r][c], "shown")

        self._memorize_start = time.perf_counter()
        self._tick_memorize(config["display_time"])
        self._flow_ids.append(self.root.after(config["display_time"], self._begin_recall))

    def _build_grid(self, grid_size):
        self._clear_game_area()
        size = TILE_SIZES.get(grid_size, 46)
        for r in range(grid_size):
            row_buttons = []
            for c in range(grid_size):
                tile = self.make_frame(self.game_frame, kind="card", width=size, height=size)
                tile.grid(row=r, column=c, padx=3, pady=3)
                tile.pack_propagate(False)
                btn = tk.Button(
                    tile, text="", relief="flat", bd=0, highlightthickness=0,
                    state="disabled", command=lambda row=r, col=c: self._toggle_cell(row, col),
                )
                self.track_font(btn, 16, "bold")
                btn.pack(fill="both", expand=True)
                self._paint_tile(btn, "default")
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def _tick_memorize(self, duration_ms):
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
                btn.config(state="normal", cursor="hand2")
                self._paint_tile(btn, "default")

        self._set_phase("RECALL", "ACCENT")
        self.timer_caption.config(text="Recall: your time")
        self._update_selection_hint()
        self.set_enabled(self.submit_button, True)

        self.recall_start = time.perf_counter()
        self._tick_recall()

    def _tick_recall(self):
        if self.phase != "recall":
            return
        elapsed = time.perf_counter() - self.recall_start
        self.timer_label.config(text=f"{elapsed:.2f} s")
        self._tick_id = self.root.after(50, self._tick_recall)

    def _update_selection_hint(self):
        needed = ROUNDS[self.current_round]["cells"]
        chosen = len(self.selected_cells)
        t = self.theme()
        self.feedback_label.config(
            text=f"Selected {chosen} of {needed} tiles.\nPress Submit (or Enter) when ready.",
            fg=t["TEXT"],
        )

    def _toggle_cell(self, row, col):
        if self.phase != "recall":
            return
        cell = (row, col)
        btn = self.buttons[row][col]
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
            self._paint_tile(btn, "default")
        else:
            self.selected_cells.add(cell)
            self._paint_tile(btn, "shown")
        self._update_selection_hint()

    def submit_answer(self):
        if self.phase != "recall":
            return

        t = self.theme()
        if not self.selected_cells:
            self.feedback_label.config(
                text="Select at least one tile before submitting.", fg=t["COLOR_MISSED"]
            )
            return

        completion_time = time.perf_counter() - self.recall_start
        self._cancel_tick()
        self.phase = "feedback"
        self.timer_label.config(text=f"{completion_time:.2f} s")
        self.timer_caption.config(text="Your time")
        self.set_enabled(self.submit_button, False)

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
        if self.data_visible:
            self._draw_chart()

        self.current_round += 1
        self._flow_ids.append(self.root.after(FEEDBACK_PAUSE_MS, self.next_round))

    def _show_round_feedback(self, score):
        for row in self.buttons:
            for btn in row:
                btn.config(state="disabled", cursor="arrow")

        for (r, c) in self.correct_pattern & self.selected_cells:
            self._paint_tile(self.buttons[r][c], "correct")
        for (r, c) in self.selected_cells - self.correct_pattern:
            self._paint_tile(self.buttons[r][c], "incorrect")
        for (r, c) in self.correct_pattern - self.selected_cells:
            self._paint_tile(self.buttons[r][c], "missed")

        total = len(self.correct_pattern)
        t = self.theme()
        if score["total_errors"] == 0:
            self._set_phase("PERFECT", "COLOR_CORRECT")
            self.feedback_label.config(
                text=f"Perfect! All {total} tiles correct.", fg=t["COLOR_CORRECT"]
            )
        else:
            self._set_phase("RESULT", "COLOR_INCORRECT")
            self.feedback_label.config(
                text=f"{score['correct_cells']} of {total} found  \u00b7  "
                     f"{score['incorrect_cells']} wrong  \u00b7  {score['missed_cells']} missed\n"
                     f"Accuracy: {score['accuracy']:.0f}%",
                fg=t["COLOR_INCORRECT"],
            )
        self.root.bell()

    # -----------------------------------------------------------------
    # RESULTS / STATISTICS
    # -----------------------------------------------------------------
    def _finish_game(self):
        self.phase = "done"
        stats = self.data.summary_stats()

        self._set_phase("COMPLETE", "COLOR_CORRECT")
        self.round_label.config(text="All rounds done")
        self.detail_label.config(text="Your results are in the summary on the right.")
        self.timer_caption.config(text="")
        self.timer_label.config(text="")
        self._draw_progress(0)
        self._clear_game_area()

        t = self.theme()
        if stats:
            self.make_label(
                self.game_frame, f"{stats['mean_accuracy']:.0f}%", "text", 44, "bold"
            ).pack()
            self.make_label(self.game_frame, "average accuracy", "muted", 11).pack()
            self._show_stats(stats)

        self.feedback_label.config(
            text="Great job! Export the CSV, then start a new participant.", fg=t["TEXT"]
        )
        self.start_button.config(text="Play Again")
        self.set_enabled(self.start_button, True)

        # Reveal the data panel automatically once there's something to show
        if not self.data_visible:
            self._set_data_visible(True)
        else:
            self._draw_chart()

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
        self._set_data_visible(False)

        self._set_phase("READY", "CARD_ALT")
        self.round_label.config(text="Round 0 of 5")
        self.detail_label.config(text="Press Start Game when you are ready.")
        self.timer_caption.config(text="Timer")
        self.timer_label.config(text="0.00 s")
        self.feedback_label.config(text="")
        self.start_button.config(text="Start Game")
        self.set_enabled(self.start_button, True)
        self.set_enabled(self.submit_button, False)

        self.game_screen.pack_forget()
        self.participant_entry.delete(0, tk.END)
        self.session_entry.delete(0, tk.END)
        self.session_entry.insert(0, "1")
        self.setup_error_label.config(text="")
        self.setup_frame.pack(fill="both", expand=True)
        self.participant_entry.focus_set()