#!/usr/bin/env python3
"""
Main entry point for Hex game.

Usage:
    python main.py                    # Two terminal players (interactive)
    python main.py --board-size 7     # Custom board size
    python main.py --help             # Show help
"""

import sys
import argparse
from engine.game import GameController
from engine.constants import Color, DEFAULT_BOARD_SIZE
from players.terminal_player import TerminalPlayer
from view.terminal_view import TerminalView


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Hex Game - Terminal Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                        # Two human players
  python main.py --board-size 7         # Smaller board
  python main.py --no-stats             # Hide player stats
  python main.py --show-full-log        # Show complete log at end
        """
    )

    parser.add_argument(
        '--board-size',
        type=int,
        default=DEFAULT_BOARD_SIZE,
        metavar='N',
        help=f'Board size (default: {DEFAULT_BOARD_SIZE})'
    )

    parser.add_argument(
        '--red-name',
        type=str,
        default='Red Player',
        metavar='NAME',
        help='Name for RED player (default: Red Player)'
    )

    parser.add_argument(
        '--blue-name',
        type=str,
        default='Blue Player',
        metavar='NAME',
        help='Name for BLUE player (default: Blue Player)'
    )

    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Hide player statistics during game'
    )

    parser.add_argument(
        '--show-full-log',
        action='store_true',
        help='Show complete event log at end of game'
    )

    parser.add_argument(
        '--show-move-history',
        action='store_true',
        help='Show complete move history at end of game'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Validate board size
    if args.board_size < 3 or args.board_size > 26:
        print("Error: Board size must be between 3 and 26")
        sys.exit(1)

    print("=" * 70)
    print("HEX GAME - Terminal Edition".center(70))
    print("=" * 70)
    print()

    # Create game controller
    game = GameController(board_size=args.board_size)

    # Create players (both terminal players for now)
    red_player = TerminalPlayer(Color.RED, args.red_name)
    blue_player = TerminalPlayer(Color.BLUE, args.blue_name)

    # Create view
    view = TerminalView(game)
    view.show_stats = not args.no_stats

    # Start game
    view.display_game_start()

    if not game.start_game(red_player, blue_player):
        print("\nError: Failed to start game")
        sys.exit(1)

    print("\nGame initialized successfully!")
    print()

    # Game loop with view updates
    while True:
        # Display current state
        view.display_board()

        if view.show_stats:
            view.display_stats()

        view.display_log(recent_count=5)

        # Play one turn
        view.display_turn_start()

        continue_game = game.play_turn()

        if not continue_game:
            # Game ended
            break

        # Small pause to make it readable
        print()

    # Game ended - show final state
    view.display_game_end()

    # Optional: show detailed logs
    if args.show_full_log:
        print()
        input("Press Enter to view full event log...")
        view.display_full_log()

    if args.show_move_history:
        print()
        input("Press Enter to view move history...")
        view.display_move_history()

    print("\nThank you for playing!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
