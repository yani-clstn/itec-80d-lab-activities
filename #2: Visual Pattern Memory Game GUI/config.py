# Configuration constants for the Visual Pattern Memory Game
# Keeping these in one place makes it easy to tune difficulty and restyle
# the interface without touching any of the game or GUI logic.

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

# Tile size in pixels for each grid size (bigger grid -> smaller tiles so the
# game area stays the same size and nothing jumps around between rounds)
TILE_SIZES = {3: 62, 4: 52, 5: 42}

# ---------------------------------------------------------------
# Theme: dark palette with high-contrast text
# ---------------------------------------------------------------
FONT = "Arial"

BG = "#141626"            # window background
CARD = "#1e2136"          # panels
CARD_ALT = "#2a2e4a"      # inputs, secondary buttons, empty progress track
BORDER = "#3a4066"
TEXT = "#eef0fb"
TEXT_MUTED = "#9ba1c7"
TEXT_ON_LIGHT = "#10121f"  # dark text used on bright tiles/badges

ACCENT = "#7c83ff"         # primary buttons, RECALL badge
ACCENT_HOVER = "#969cff"

CELL_DEFAULT = "#2f3556"
CELL_HOVER = "#414970"
CELL_SHOWN = "#4cc9f0"     # a lit tile: pattern being memorized AND a tile
                           # the user picked (same look = consistency)

COLOR_CORRECT = "#3ddc84"
COLOR_INCORRECT = "#ff5c72"
COLOR_MISSED = "#ffb347"

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