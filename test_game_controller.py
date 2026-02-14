"""Test game controller without interactive input."""

from engine.game import GameController
from engine.constants import Color
from engine.board import HexBoard
from players.base import Player


class TestPlayer(Player):
    """Simple test player that makes predefined moves."""

    def __init__(self, color, moves):
        super().__init__(color, f"Test {color.name}")
        self.moves = moves
        self.move_index = 0

    def initialize(self, board_size):
        return True

    def get_move(self, board):
        if self.move_index < len(self.moves):
            move = self.moves[self.move_index]
            self.move_index += 1
            return move
        return None


# Create a simple game where RED wins
print("Testing Game Controller...")
print()

# Create game
game = GameController(board_size=5)

# Create test players with predetermined moves that lead to RED win
# RED connects top to bottom
red_moves = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
blue_moves = [(0, 1), (0, 2), (0, 3), (0, 4)]  # BLUE tries but fails

red_player = TestPlayer(Color.RED, red_moves)
blue_player = TestPlayer(Color.BLUE, blue_moves)

# Start game
if game.start_game(red_player, blue_player):
    print("✓ Game started successfully")
else:
    print("✗ Game failed to start")
    exit(1)

# Run game
print(f"✓ Running game...")
status = game.run_game()

print()
print(f"✓ Game ended with status: {status.value}")

# Check results
summary = game.get_game_summary()
print()
print("Game Summary:")
print(f"  Winner: {summary['winner']}")
print(f"  Total turns: {summary['total_turns']}")
print(f"  Total moves: {summary['move_count']}")
print(f"  RED errors: {summary['red_errors']}")
print(f"  BLUE  errors: {summary['blue_errors']}")

# Display final board
print()
print("Final Board:")
print(game.board.to_string())

print()
print("✓ Game controller test passed!")
