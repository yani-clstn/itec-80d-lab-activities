# Configuration constants for the Visual Pattern Memory Game.
# Keeping these in one place makes it easy to tune difficulty, add themes,
# or restyle the interface without touching any game or GUI logic.

# ---------------------------------------------------------------
# Difficulty: one dict per round (5 progressively harder rounds)
# ---------------------------------------------------------------
ROUNDS = [
    {"grid": 3, "cells": 3, "display_time": 2000},
    {"grid": 3, "cells": 4, "display_time": 2200},
    {"grid": 4, "cells": 5, "display_time": 2500},
    {"grid": 4, "cells": 6, "display_time": 2800},
    {"grid": 5, "cells": 7, "display_time": 3200},
]

FEEDBACK_PAUSE_MS = 2200   # how long per-round feedback stays on screen
TILE_SIZES = {3: 62, 4: 52, 5: 42}   # pixel size of a grid tile, by grid size

# ---------------------------------------------------------------
# Fonts and text scaling ("resizable text" via A-/A+ buttons)
# ---------------------------------------------------------------
FONT = "Arial"
FONT_SCALES = [0.85, 1.0, 1.15, 1.3, 1.5]   # cycled through by the A-/A+ buttons

# ---------------------------------------------------------------
# Colors that stay the same in both themes (bright, work on light or dark)
# ---------------------------------------------------------------
_SHARED_COLORS = dict(
    ACCENT="#6c63ff",
    ACCENT_HOVER="#8a83ff",
    CELL_SHOWN="#4cc9f0",
    TEXT_ON_LIGHT="#10121f",     # dark text used on bright tiles/badges
    COLOR_CORRECT="#2fbf71",
    COLOR_INCORRECT="#ef4a5f",
    COLOR_MISSED="#f4a621",
)

# ---------------------------------------------------------------
# Theme palettes: everything a widget needs is in one dict, so any
# function can just do theme["KEY"] without knowing which theme is active
# ---------------------------------------------------------------
THEMES = {
    "dark": {
        **_SHARED_COLORS,
        "BG": "#141626",
        "CARD": "#1e2136",
        "CARD_ALT": "#2a2e4a",
        "BORDER": "#3a4066",
        "TEXT": "#eef0fb",
        "TEXT_MUTED": "#9ba1c7",
        "CELL_DEFAULT": "#2f3556",
        "CELL_HOVER": "#414970",
    },
    "light": {
        **_SHARED_COLORS,
        "BG": "#f3f4fb",
        "CARD": "#ffffff",
        "CARD_ALT": "#eef0fa",
        "BORDER": "#d7dbee",
        "TEXT": "#181a2b",
        "TEXT_MUTED": "#5c6088",
        "CELL_DEFAULT": "#e3e6f6",
        "CELL_HOVER": "#ccd2ef",
    },
}
DEFAULT_THEME = "dark"

# ---------------------------------------------------------------
# Participant form options
# ---------------------------------------------------------------
AGE_GROUPS = ["Under 18", "18-20", "21-23", "24-26", "27 and above"]
EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]

# ---------------------------------------------------------------
# Data export
# ---------------------------------------------------------------
CSV_FOLDER = "raw_interaction_data"
CSV_FILENAME = "raw_data.csv"