# Hex Game - Complete System

A complete Hex game implementation with game controller, player abstraction, and terminal UI.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              main.py (Entry Point)              │
│  - Parse arguments                              │
│  - Setup players                                │
│  - Initialize game and view                     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          GameController (engine/game.py)        │
│  - Game loop management                         │
│  - Move validation with retry logic             │
│  - Error tracking and limits                    │
│  - Win detection                                │
│  - Event logging                                │
└────────┬────────────────────────┬────────────────┘
         │                        │
         │ get_move()             │ Display updates
         ▼                        ▼
┌──────────────────┐    ┌──────────────────────┐
│  Player Classes  │    │  TerminalView        │
│  (players/)      │    │  (view/)             │
│  - TerminalPlayer│    │  - Board display     │
│  - SubprocessPr. │    │  - Event log         │
│  - AI Players    │    │  - Player stats      │
└──────────────────┘    └──────────────────────┘
```

## Quick Start

### Play a Game (Two Human Players)

```bash
python main.py
```

### Custom Board Size

```bash
python main.py --board-size 7
```

### Custom Player Names

```bash
python main.py --red-name Alice --blue-name Bob
```

### Hide Statistics

```bash
python main.py --no-stats
```

### Show Full Logs After Game

```bash
python main.py --show-full-log --show-move-history
```

## Components

### 1. Game Controller (`engine/game.py`)

The brain of the game. Handles:

- **Turn Management**: Alternates between players
- **Move Validation**: Checks if moves are legal
- **Retry Logic**: Allows 3 invalid moves per turn
- **Error Tracking**: Monitors player errors (max 10 total)
- **Win Detection**: Checks after each move
- **Event Logging**: Records everything

**Configuration:**
```python
MAX_INVALID_MOVES = 3   # Retries per turn
MAX_TOTAL_ERRORS = 10   # Total errors before forfeit
```

**Example Usage:**
```python
from engine.game import GameController
from players.terminal_player import TerminalPlayer
from engine.constants import Color

# Create game
game = GameController(board_size=11)

# Setup players
red = TerminalPlayer(Color.RED, "Player 1")
blue = TerminalPlayer(Color.BLUE, "Player 2")

# Start and run
game.start_game(red, blue)
status = game.run_game()
```

### 2. Terminal View (`view/terminal_view.py`)

Displays game state in terminal:

- **Board**: ASCII art representation
- **Stats**: Player moves and error counts
- **Log**: Recent events (color-coded)
- **Turn Info**: Current player and turn number
- **Game End**: Final results and summary

**Features:**
- Configurable log size
- Optional statistics display
- Full log export
- Move history export

### 3. Player Classes (`players/`)

#### Base Class (`players/base.py`)
```python
class Player(ABC):
    def initialize(board_size) -> bool:
        """Setup before game starts."""
        
    def get_move(board) -> Optional[Tuple[int, int]]:
        """Return (row, col) or None to forfeit."""
        
    def cleanup():
        """Cleanup resources."""
```

#### Terminal Player (`players/terminal_player.py`)
- Interactive human player
- Prompts for input via terminal
- Local validation with helpful error messages
- Supports multiple input formats: `5 7`, `5,7`, `(5,7)`

### 4. Main Entry Point (`main.py`)

Command-line interface with arguments:

```
--board-size N         Board size (default: 11)
--red-name NAME        RED player name
--blue-name NAME       BLUE player name
--no-stats             Hide player statistics
--show-full-log        Show complete log at end
--show-move-history    Show all moves at end
```

## Game Flow

1. **Initialization**
   - Parse arguments
   - Create GameController
   - Create players
   - Create TerminalView
   - Display start banner

2. **Game Loop** (per turn)
   - Display board
   - Display stats
   - Display recent events
   - Get move from current player (with retry logic)
   - Validate move
   - Update board
   - Check for win
   - Switch player

3. **Game End**
   - Display final board
   - Show winner
   - Show statistics
   - Optional: full log
   - Optional: move history

## Error Handling

### Retry Logic

Per turn: **3 attempts** for invalid moves
- Out of bounds
- Cell occupied
- Invalid format

### Forfeit Conditions

Immediate forfeit on:
- Player returns None
- Player crashes/exception
- Player exceeds 10 total errors

### Error Tracking

```
Turn 5: Player BLUE's turn
  Attempt 1: (5, 5) → cell_occupied
  Attempt 2: (-1, 3) → out_of_bounds
  Attempt 3: (4, 6) → SUCCESS!

Player errors: BLUE 2/10
```

## Event Logging

All events are logged with timestamps and severity:

- **INFO**: Normal game events (moves, turn start)
- **WARNING**: Recoverable errors (invalid moves)
- **ERROR**: Serious errors (repeated failures)
- **CRITICAL**: Game-ending events (forfeit, win)

## Testing

### Test Game Controller

```bash
python test_game_controller.py
```

Automated test with predetermined moves.

### Test Player Classes

```bash
python test_player_update.py
```

Verify player interface.

## Future Extensions

### Add AI Player

```python
class RandomPlayer(Player):
    def get_move(self, board):
        empty = board.get_empty_cells()
        return random.choice(empty) if empty else None
```

### Add Subprocess Player

```python
class SubprocessPlayer(Player):
    def get_move(self, board):
        # Send board state to subprocess
        # Read move from subprocess
        # Parse and return
```

### Add Web Player

```python
class WebSocketPlayer(Player):
    def get_move(self, board):
        # Send board state via WebSocket
        # Wait for move from web client
        # Return move
```

## Examples

See also:
- `demo_player.py` - Player class demos
- `demo_board.py` - Board model demos
- `test_game_controller.py` - Automated game test

## Notes

- RED always goes first
- RED connects TOP ↔ BOTTOM
- BLUE connects LEFT ↔ RIGHT
- No draws possible in Hex
- Coordinates are 0-indexed

## Help

```bash
python main.py --help
```
