import random


def generate_pattern(grid_size, num_cells):
    """
    Returns a set of (row, col) tuples representing the highlighted cells
    for one round, given the grid size and how many cells should be active.
    """
    all_positions = [(r, c) for r in range(grid_size) for c in range(grid_size)]
    return set(random.sample(all_positions, num_cells))


def score_round(correct_pattern, selected_cells):
    """
    Compares what the user selected against the correct pattern.
    Returns a dict with correct_cells, incorrect_cells, missed_cells,
    total_errors, and accuracy (0-100).
    """
    correct_cells = len(correct_pattern & selected_cells)
    incorrect_cells = len(selected_cells - correct_pattern)
    missed_cells = len(correct_pattern - selected_cells)
    total_errors = incorrect_cells + missed_cells
    accuracy = (correct_cells / len(correct_pattern)) * 100 if correct_pattern else 0

    return {
        "correct_cells": correct_cells,
        "incorrect_cells": incorrect_cells,
        "missed_cells": missed_cells,
        "total_errors": total_errors,
        "accuracy": round(accuracy, 2),
    }