"""
Quick demo of the game system with view integration.
Non-interactive test showing game controller + view.
"""

from engine.game import GameController
from engine.constants import Color
from players.base import Player
from view.terminal_view import TerminalView


class QuickPlayer(Player):
    """Auto-player for quick demo."""

    def __init__(self, color, name):
        super().__init__(color, name)
        self.move_count = 0

    def initialize(self, board_size):
        self.board_size = board_size
        return True

    def get_move(self, board):
        # Simple strategy: fill column by column
        for col in range(self.board_size):
            for row in range(self.board_size):
                if board.is_empty(row, col):
                    self.move_count += 1
                    return (row, col)
        return None


print("=" * 70)
print("HEX GAME SYSTEM DEMO".center(70))
print("Quick game with auto-players to demonstrate the system".center(70))
print("=" * 70)
print()

# Create small game for quick demo
game = GameController(board_size=5)

# Create auto-players
red = QuickPlayer(Color.RED, "Auto RED")
blue = QuickPlayer(Color.BLUE, "Auto BLUE")

# Create view
view = TerminalView(game)

# Display start
view.display_game_start()

# Start game
if not game.start_game(red, blue):
    print("Failed to start game!")
    exit(1)

input("Press Enter to run the game...")

# Run game with view updates every few turns
turn_count = 0
while game.play_turn():
    turn_count += 1

    # Show updates every 2 turns or at the end
    if turn_count % 2 == 0 or game.status.value != "ongoing":
        print("\n" + "─" * 70)
        view.display_board()
        view.display_stats()
        print("─" * 70)

        if turn_count < 10:  # Only pause for first few turns
            import time
            time.sleep(0.5)

# Show final results
view.display_game_end()

# Optional detailed logs
print()
choice = input("View full event log? (y/n): ").strip().lower()
if choice == 'y':
    view.display_full_log()

print()
choice = input("View move history? (y/n): ").strip().lower()
if choice == 'y':
    view.display_move_history()

print()
print("=" * 70)
print("Demo completed!".center(70))
print("=" * 70)
print()
print("Key features demonstrated:")
print("  ✓ Game Controller - manages game flow")
print("  ✓ Player abstraction - auto-players")
print("  ✓ Terminal View - displays state")
print("  ✓ Error tracking - monitors players")
print("  ✓ Event logging - records everything")
print("  ✓ Move validation - checks legality")
print("  ✓ Win detection - finds winner")
print()
print("Try: python main.py (for interactive play)")
print()
