#!/usr/bin/env python3
"""
Memory Hog Hex agent - Python example.

This agent plays randomly like random_agent.py but deliberately
consumes a large amount of memory (>100MB) to test memory limit enforcement.

Usage: Same as random_agent.py
"""

import sys
import random


# Deliberately allocate large memory structures
# Each list of 1 million integers takes ~8MB (on 64-bit Python)
# We'll create multiple to exceed 100MB
MEMORY_HOGS = []


def allocate_memory(target_mb=120):
    """
    Allocate approximately target_mb of memory.

    Args:
        target_mb: Target memory in megabytes
    """
    global MEMORY_HOGS

    # Each million integers takes ~8 MB
    # To get 120 MB, we need about 15 million integers
    num_elements = (target_mb * 1024 * 1024) // 8

    # Create large lists
    print(
        f"[Memory Hog] Allocating ~{target_mb} MB of memory...", file=sys.stderr)
    MEMORY_HOGS.append(list(range(num_elements)))
    print(
        f"[Memory Hog] Memory allocated. List size: {len(MEMORY_HOGS[0])} elements", file=sys.stderr)


def parse_board(line):
    """
    Parse the board state from one line.

    Args:
        line: Input line in format "SIZE COLOR MOVES"

    Returns:
        Tuple of (size, my_color, board_dict)
        where board_dict is {(row, col): 'R' or 'B'}
    """
    parts = line.strip().split(maxsplit=2)

    size = int(parts[0])
    my_color = parts[1]  # "RED" or "BLUE"

    # Parse existing moves
    board = {}
    if len(parts) == 3 and parts[2]:
        moves_str = parts[2]
        for move in moves_str.split(','):
            row, col, color = move.split(':')
            board[(int(row), int(col))] = color

    return size, my_color, board


def get_empty_cells(size, board):
    """Get all empty cells on the board."""
    empty = []
    for row in range(size):
        for col in range(size):
            if (row, col) not in board:
                empty.append((row, col))
    return empty


def choose_move(size, my_color, board):
    """
    Choose your move. This is where your AI logic goes!

    Args:
        size: Board size
        my_color: Your color ("RED" or "BLUE")
        board: Dictionary of existing moves

    Returns:
        Tuple of (row, col) for your move
    """
    # Simple strategy: pick a random empty cell
    empty_cells = get_empty_cells(size, board)

    if not empty_cells:
        return (0, 0)  # Shouldn't happen

    return random.choice(empty_cells)


def main():
    """Loop version - handles multiple moves, but uses lots of memory!"""

    # Allocate a large amount of memory at startup
    allocate_memory(target_mb=120)

    while True:
        try:
            # Read the board state (one line per turn)
            line = input()

            # Parse it
            size, my_color, board = parse_board(line)

            # Choose your move
            row, col = choose_move(size, my_color, board)

            # Output your move
            print(f"{row} {col}")
            sys.stdout.flush()

        except EOFError:
            # Game ended - controller closed our stdin
            break


if __name__ == "__main__":
    main()
