Ask students to install tkinter

# Hex Game - GUI Version

## Quick Start

To run the GUI version of the Hex game:

```bash
python3 gui_main.py
```

This will launch a graphical window with an 11x11 Hex board where two human players can play by clicking on cells.

## Command Line Options

### Board Size

```bash
python3 gui_main.py --board-size 7      # Smaller 7x7 board
python3 gui_main.py --board-size 15     # Larger 15x15 board
```

### Player Names

```bash
python3 gui_main.py --red-name "Alice" --blue-name "Bob"
```

## How to Play

### Game Rules

- **RED player** must connect the **TOP** edge to the **BOTTOM** edge
- **BLUE player** must connect the **LEFT** edge to the **RIGHT** edge
- Players alternate turns placing stones on empty hexagons
- Click on any empty hexagon to place your stone
- The first player to create a connected path wins

### GUI Controls

1. **Board**: Click on any empty hexagon to place your stone
2. **Swap Move Button**: Available after the first move (pie rule - second player can swap positions)
3. **Forfeit Button**: Give up the current game

### Display Elements

- **Turn Indicator**: Shows whose turn it is and the current turn number
- **Player Stats**: Displays move count and error count for each player
- **Event Log**: Shows recent game events and actions

## Files Created

### Core Files

1. **gui_main.py** - Main entry point for GUI version
2. **view/tkinter_view.py** - Tkinter-based graphical interface
3. **players/gui_player.py** - Player that receives input from GUI clicks

### Architecture

```
┌─────────────┐
│  gui_main.py│
└──────┬──────┘
       │
       ├── Creates ──> GameController (engine/game.py)
       │
       ├── Creates ──> GUIPlayer × 2 (players/gui_player.py)
       │
       └── Creates ──> TkinterView (view/tkinter_view.py)
                            │
                            └── Displays hexagonal board
                            └── Handles user clicks
                            └── Shows stats and logs
```

## Features Implemented

✅ Hexagonal board visualization  
✅ Click-to-place move input  
✅ Swap move support (pie rule)  
✅ Player statistics display  
✅ Event log display  
✅ Win detection with popup  
✅ Hover effects on empty cells  
✅ Coordinate labels on cells  
✅ Forfeit option  

## Future Enhancements

The current implementation supports:
- ✅ Human vs Human (GUI)

Planned for future:
- ⏳ Human (GUI) vs AI (subprocess)
- ⏳ AI vs AI with GUI visualization
- ⏳ Save/Load game state
- ⏳ Move history replay
- ⏳ Undo/Redo functionality

## Technical Details

### HexBoardCanvas Class

The hexagonal grid is drawn using:
- Polygon-based hexagons (6-sided)
- Axial coordinate system with row offset
- 25px hexagon radius (configurable)
- Color coding: Red (#FF6B6B), Blue (#4ECDC4), Empty (#F0F0F0)

### GUIPlayer Class

- Inherits from `Player` base class
- Uses callback pattern to receive moves from GUI
- Supports normal moves (row, col), swap moves, and forfeit (None)

### Game Loop Integration

The game loop runs using tkinter's `after()` method:
- Checks for player input every 50ms
- Updates display after each move
- Processes moves through GameController
