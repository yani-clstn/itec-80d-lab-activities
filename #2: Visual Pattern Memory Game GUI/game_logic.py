import random


def generate_pattern(grid_size, num_cells):
    """
    Returns a set of (row, col) tuples representing the highlighted cells
    for one round, given the grid size and how many cells should be active.
    """
    all_positions = [(r, c) for r in range(grid_size) for c in range(grid_size)]
    return set(random.sample(all_positions, num_cells))