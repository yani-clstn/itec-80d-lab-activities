# Round configuration and shared constants for the Visual Pattern Memory Game

ROUNDS = [
    {"grid": 3, "cells": 3, "display_time": 2000},
    {"grid": 3, "cells": 4, "display_time": 2200},
    {"grid": 4, "cells": 5, "display_time": 2500},
    {"grid": 4, "cells": 6, "display_time": 2800},
    {"grid": 5, "cells": 7, "display_time": 3200},
]

CELL_SIZE = 60          # pixels, button width/height
COLOR_DEFAULT = "#d9d9d9"
COLOR_HIGHLIGHT = "#4A90D9"
COLOR_CORRECT = "#4CAF50"
COLOR_INCORRECT = "#E53935"