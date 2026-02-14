"""
Terminal-based view for Hex game.

Displays game state, moves, and logs in the terminal.
"""

import time
from datetime import datetime
from typing import List
from engine.board import HexBoard
from engine.game import GameController, GameEvent, LogLevel
from engine.constants import Color


class TerminalView:
    """
    Terminal-based view for displaying game state.

    Shows:
    - Game board
    - Move history
    - Event log (errors, warnings, info)
    - Player statistics
    - Game status
    """

    def __init__(self, game_controller: GameController):
        """
        Initialize terminal view.

        Args:
            game_controller: The game controller to display
        """
        self.controller = game_controller
        self.show_log = True
        self.show_stats = True

    def display_game_start(self):
        """Display game start banner."""
        width = 70
        print("\n" + "=" * width)
        print("HEX GAME".center(width))
        print("=" * width)
        print()
        print(
            f"Board Size: {self.controller.board_size}x{self.controller.board_size}")

        if self.controller.red_player and self.controller.blue_player:
            print(f"RED Player: {self.controller.red_player.name}")
            print(f"BLUE Player: {self.controller.blue_player.name}")

        print()
        print("RED Goal: Connect TOP to BOTTOM")
        print("BLUE Goal: Connect LEFT to RIGHT")
        print("=" * width)
        print()

    def display_board(self):
        """Display the current board state."""
        print(self.controller.board.to_string())

    def display_turn_start(self):
        """Display turn information."""
        player = self.controller.current_player
        if player:
            print(f"\n{'─' * 70}")
            print(
                f"Turn {self.controller.current_turn}: {player.name}'s turn ({player.color.name})")
            print(f"{'─' * 70}")

    def display_move(self, row: int, col: int, color: Color):
        """Display a move that was made."""
        color_symbol = "🔴" if color == Color.RED else "🔵"
        print(f"\n{color_symbol} {color.name} played: ({row}, {col})")

    def display_log(self, recent_count: int = 5):
        """
        Display recent log events.

        Args:
            recent_count: Number of recent events to show
        """
        if not self.show_log:
            return

        print("\n┌─ RECENT EVENTS " + "─" * 52 + "┐")

        recent_events = self.controller.events[-recent_count:
                                               ] if self.controller.events else []

        if not recent_events:
            print("│ No events yet" + " " * 54 + "│")
        else:
            for event in recent_events:
                self._print_log_entry(event)

        print("└" + "─" * 68 + "┘")

    def _print_log_entry(self, event: GameEvent):
        """Print a single log entry."""
        timestamp = datetime.fromtimestamp(
            event.timestamp).strftime("%H:%M:%S")

        # Color code by level
        level_prefix = {
            LogLevel.INFO: "ℹ",
            LogLevel.WARNING: "⚠",
            LogLevel.ERROR: "✗",
            LogLevel.CRITICAL: "🔥"
        }.get(event.level, "·")

        message = f"{level_prefix} [{timestamp}] {event.message}"

        # Truncate if too long
        max_len = 66
        if len(message) > max_len:
            message = message[:max_len-3] + "..."

        # Pad to fit in box
        message = message.ljust(66)

        print(f"│ {message} │")

    def display_stats(self):
        """Display player statistics."""
        if not self.show_stats:
            return

        print("\n┌─ PLAYER STATS " + "─" * 53 + "┐")

        # RED player stats
        self._print_player_stats(
            self.controller.red_player,
            self.controller.player_errors[Color.RED]
        )

        print("├" + "─" * 68 + "┤")

        # BLUE player stats
        self._print_player_stats(
            self.controller.blue_player,
            self.controller.player_errors[Color.BLUE]
        )

        print("└" + "─" * 68 + "┘")

    def _print_player_stats(self, player, error_count: int):
        """Print stats for one player."""
        color_symbol = "🔴" if player.color == Color.RED else "🔵"

        # Count moves
        moves = [m for m in self.controller.move_history if m['color']
                 == player.color.name]
        move_count = len(moves)

        # Status indicator
        status = "✓ Active" if error_count < GameController.MAX_TOTAL_ERRORS else "✗ Error Limit"

        line1 = f"│ {color_symbol} {player.name}".ljust(67) + "│"
        line2 = f"│    Moves: {move_count}  |  Errors: {error_count}/{GameController.MAX_TOTAL_ERRORS}  |  Status: {status}".ljust(
            67) + "│"

        print(line1)
        print(line2)

    def display_game_end(self):
        """Display game over screen."""
        summary = self.controller.get_game_summary()

        width = 70
        print("\n" + "=" * width)
        print("GAME OVER".center(width))
        print("=" * width)
        print()

        # Winner
        if summary['winner']:
            winner_symbol = "🔴" if summary['winner'] == 'RED' else "🔵"
            print(
                f"{winner_symbol} WINNER: {summary['winner']} ({summary[summary['winner'].lower() + '_player']})")
        else:
            print("Result: Draw")

        print()
        print(f"Total Turns: {summary['total_turns']}")
        print(f"Total Moves: {summary['move_count']}")
        print()
        print(f"RED Errors: {summary['red_errors']}")
        print(f"BLUE Errors: {summary['blue_errors']}")
        print()

        # Final board
        print("Final Board:")
        self.display_board()

        print("\n" + "=" * width)

    def display_full_log(self):
        """Display all log events."""
        print("\n" + "=" * 70)
        print("FULL EVENT LOG".center(70))
        print("=" * 70)

        for event in self.controller.events:
            timestamp = datetime.fromtimestamp(
                event.timestamp).strftime("%H:%M:%S.%f")[:-3]
            level_str = event.level.value.upper().ljust(8)
            print(f"[{timestamp}] {level_str} {event.message}")

        print("=" * 70)

    def display_move_history(self):
        """Display complete move history."""
        print("\n" + "=" * 70)
        print("MOVE HISTORY".center(70))
        print("=" * 70)

        for move in self.controller.move_history:
            turn = move['turn']
            player = move['player']
            color = move['color']
            pos = move['move']

            color_symbol = "🔴" if color == 'RED' else "🔵"
            print(
                f"Turn {turn:3d}: {color_symbol} {player:20s} → ({pos[0]:2d}, {pos[1]:2d})")

        print("=" * 70)

    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self, message: str = "Press Enter to continue..."):
        """Pause for user input."""
        input(f"\n{message}")
