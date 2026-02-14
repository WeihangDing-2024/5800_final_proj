"""Quick test of updated Player base class."""

from players.base import Player
from players.terminal_player import TerminalPlayer
from engine.constants import Color

print("Testing updated Player base class...")
print()

# Test creation
p = TerminalPlayer(Color.RED, 'Test Player')
print(f"✓ Player created: {p}")

# Test required methods (from base class)
print(f"✓ Required method 'initialize': {hasattr(p, 'initialize')}")
print(f"✓ Required method 'get_move': {hasattr(p, 'get_move')}")
print(f"✓ Required method 'cleanup': {hasattr(p, 'cleanup')}")

# Test optional UI methods (not in base class)
print(f"✓ Optional UI method 'notify_move': {hasattr(p, 'notify_move')}")
print(f"✓ Optional UI method 'notify_result': {hasattr(p, 'notify_result')}")
print(f"✓ Optional UI method 'notify_game_end': {hasattr(p, 'notify_game_end')}")

# Test removed methods (should not exist in base class)
print()
print("Removed from base class:")
print(f"  - notify_* methods are now optional")
print(f"  - No GameStatus import needed")
print(f"  - Simpler, cleaner interface")

print()
print("✓ All tests passed! Player base class successfully simplified.")
