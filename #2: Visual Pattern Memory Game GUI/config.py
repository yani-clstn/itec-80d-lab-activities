# Configuration constants for the Visual Pattern Memory Game
# Keeping these in one place makes it easy to tune difficulty without
# touching any of the game or GUI logic.

ROUNDS = [
    {"grid": 3, "cells": 3, "display_time": 2000},
    {"grid": 3, "cells": 4, "display_time": 2200},
    {"grid": 4, "cells": 5, "display_time": 2500},
    {"grid": 4, "cells": 6, "display_time": 2800},
    {"grid": 5, "cells": 7, "display_time": 3200},
]

# Colors (portable hex values — avoid Windows-only Tk color names)
COLOR_DEFAULT = "#d9d9d9"
COLOR_HIGHLIGHT = "#4A90D9"
COLOR_CORRECT = "#4CAF50"
COLOR_MISSED = "#FFB300"
COLOR_INCORRECT = "#E53935"

FEEDBACK_PAUSE_MS = 2200  # how long per-round feedback stays on screen before the next round

AGE_GROUPS = ["Under 18", "18-20", "21-23", "24-26", "27 and above"]
EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]

CSV_FOLDER = "raw_interaction_data"
CSV_FILENAME = "raw_data.csv"