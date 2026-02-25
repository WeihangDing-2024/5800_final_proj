"""
Test cases for GameController class.

Tests game flow, turn management, move validation, error handling,
and win detection.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from engine.game import GameController, GameEvent, LogLevel
from engine.board import HexBoard
from engine.constants import Color, GameStatus, MoveResult, DEFAULT_BOARD_SIZE


class MockPlayer:
    """Mock player for testing."""

    def __init__(self, name, color, moves=None):
        """
        Initialize mock player.

        Args:
            name: Player name
            color: Player color
            moves: List of moves to return (can be tuples, "swap", or None for forfeit)
        """
        self.name = name
        self.color = color
        self.moves = moves or []
        self.move_index = 0
        self.initialized = False

    def initialize(self, board_size):
        """Initialize player."""
        self.initialized = True
        return True

    def get_move(self, board):
        """Get next move from the move list."""
        if self.move_index < len(self.moves):
            move = self.moves[self.move_index]
            self.move_index += 1
            return move
        return (0, 0)  # Default fallback


class TestGameControllerInitialization(unittest.TestCase):
    """Test GameController initialization."""

    def test_default_initialization(self):
        """Test creating controller with default board size."""
        controller = GameController()
        self.assertEqual(controller.board_size, DEFAULT_BOARD_SIZE)
        self.assertEqual(controller.status, GameStatus.ONGOING)
        self.assertIsNone(controller.winner)
        self.assertEqual(controller.current_turn, 0)

    def test_custom_board_size(self):
        """Test creating controller with custom board size."""
        controller = GameController(7)
        self.assertEqual(controller.board_size, 7)
        self.assertEqual(controller.board.size, 7)

    def test_initial_player_state(self):
        """Test initial player state."""
        controller = GameController()
        self.assertIsNone(controller.red_player)
        self.assertIsNone(controller.blue_player)
        self.assertIsNone(controller.current_player)

    def test_initial_error_tracking(self):
        """Test initial error counts."""
        controller = GameController()
        self.assertEqual(controller.player_errors[Color.RED], 0)
        self.assertEqual(controller.player_errors[Color.BLUE], 0)

    def test_initial_logs_empty(self):
        """Test that event log starts empty."""
        controller = GameController()
        self.assertEqual(len(controller.events), 0)
        self.assertEqual(len(controller.move_history), 0)


class TestGameStart(unittest.TestCase):
    """Test starting a game."""

    def setUp(self):
        self.controller = GameController(5)

    def test_start_game_success(self):
        """Test successfully starting a game."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)

        result = self.controller.start_game(red, blue)

        self.assertTrue(result)
        self.assertEqual(self.controller.red_player, red)
        self.assertEqual(self.controller.blue_player, blue)
        self.assertEqual(self.controller.current_player, red)  # RED starts

    def test_start_game_initializes_players(self):
        """Test that start_game calls initialize on both players."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        self.assertTrue(red.initialized)
        self.assertTrue(blue.initialized)

    def test_start_game_red_init_failure(self):
        """Test start_game fails if red player init fails."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)
        red.initialize = lambda size: False

        result = self.controller.start_game(red, blue)

        self.assertFalse(result)

    def test_start_game_blue_init_failure(self):
        """Test start_game fails if blue player init fails."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)
        blue.initialize = lambda size: False

        result = self.controller.start_game(red, blue)

        self.assertFalse(result)

    def test_start_game_logs_events(self):
        """Test that start_game logs initialization events."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        # Should have logged initialization for both players and game start
        self.assertGreaterEqual(len(self.controller.events), 3)


class TestPlayTurn(unittest.TestCase):
    """Test playing turns."""

    def setUp(self):
        self.controller = GameController(5)

    def test_play_turn_simple_move(self):
        """Test playing a simple valid turn."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(2, 2)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=[(1, 1)])

        self.controller.start_game(red, blue)

        # RED's turn
        result = self.controller.play_turn()

        self.assertTrue(result)
        self.assertEqual(self.controller.current_turn, 1)
        self.assertEqual(self.controller.board.get_cell(2, 2), Color.RED)
        self.assertEqual(self.controller.current_player,
                         blue)  # Switched to BLUE

    def test_play_turn_alternating_players(self):
        """Test that players alternate turns."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(0, 0), (1, 1)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=[(2, 2), (3, 3)])

        self.controller.start_game(red, blue)

        # RED's turn
        self.controller.play_turn()
        self.assertEqual(self.controller.board.get_cell(0, 0), Color.RED)
        self.assertEqual(self.controller.current_player, blue)

        # BLUE's turn
        self.controller.play_turn()
        self.assertEqual(self.controller.board.get_cell(2, 2), Color.BLUE)
        self.assertEqual(self.controller.current_player, red)

    def test_play_turn_updates_move_history(self):
        """Test that moves are recorded in history."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(1, 2)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=[(3, 4)])

        self.controller.start_game(red, blue)

        self.controller.play_turn()

        self.assertEqual(len(self.controller.move_history), 1)
        move_record = self.controller.move_history[0]
        self.assertEqual(move_record['turn'], 1)
        self.assertEqual(move_record['player'], "Red Bot")
        self.assertEqual(move_record['color'], 'RED')
        self.assertEqual(move_record['move'], (1, 2))

    def test_play_turn_swap_move(self):
        """Test swap move on second turn."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(2, 3)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=["swap"])

        self.controller.start_game(red, blue)

        # RED places first stone
        self.controller.play_turn()
        self.assertEqual(self.controller.board.get_cell(2, 3), Color.RED)

        # BLUE swaps
        result = self.controller.play_turn()

        self.assertTrue(result)
        self.assertEqual(self.controller.board.get_cell(2, 3), Color.EMPTY)
        self.assertEqual(self.controller.board.get_cell(3, 2), Color.BLUE)
        self.assertTrue(self.controller.board.swap_used)

    def test_play_turn_invalid_swap_forfeits(self):
        """Test that invalid swap causes forfeit."""
        # Invalid swap after retry limit - provide 3 invalid swaps to exceed retry limit
        red = MockPlayer("Red Bot", Color.RED, moves=["swap", "swap", "swap"])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        result = self.controller.play_turn()

        self.assertFalse(result)
        self.assertEqual(self.controller.status, GameStatus.ERROR)
        self.assertEqual(self.controller.winner, Color.BLUE)

    def test_play_turn_stops_when_game_ended(self):
        """Test that play_turn returns False when game already ended."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)
        self.controller.status = GameStatus.RED_WIN

        result = self.controller.play_turn()

        self.assertFalse(result)


class TestMoveValidation(unittest.TestCase):
    """Test move validation and retry logic."""

    def setUp(self):
        self.controller = GameController(5)

    def test_out_of_bounds_move_retries(self):
        """Test that out of bounds moves trigger retry."""
        # First two moves invalid, third valid
        red = MockPlayer("Red Bot", Color.RED, moves=[
                         (-1, 0), (10, 10), (2, 2)])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        result = self.controller.play_turn()

        self.assertTrue(result)
        self.assertEqual(self.controller.board.get_cell(2, 2), Color.RED)
        self.assertEqual(self.controller.player_errors[Color.RED], 2)

    def test_occupied_cell_move_retries(self):
        """Test that moves on occupied cells trigger retry."""
        # RED tries to place on (1,1) which RED already occupied, then tries valid (2,2)
        red = MockPlayer("Red Bot", Color.RED, moves=[(1, 1), (1, 1), (2, 2)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=[(3, 3)])

        self.controller.start_game(red, blue)

        # RED's first turn - places at (1,1)
        self.controller.play_turn()
        self.assertEqual(self.controller.board.get_cell(1, 1), Color.RED)

        # BLUE's turn
        self.controller.play_turn()

        # RED's second turn - tries occupied (1,1), then succeeds with (2,2)
        result = self.controller.play_turn()

        self.assertTrue(result)
        self.assertEqual(self.controller.board.get_cell(2, 2), Color.RED)
        # Should have 1 error from attempting occupied cell
        self.assertEqual(self.controller.player_errors[Color.RED], 1)

    def test_max_retries_causes_forfeit(self):
        """Test that exceeding max retries causes forfeit."""
        # Four invalid moves (exceeds MAX_INVALID_MOVES=3)
        red = MockPlayer("Red Bot", Color.RED, moves=[
                         (-1, 0), (-1, 1), (-1, 2), (-1, 3)])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        result = self.controller.play_turn()

        self.assertFalse(result)
        self.assertEqual(self.controller.status, GameStatus.ERROR)
        self.assertEqual(self.controller.winner, Color.BLUE)

    def test_player_returns_none_forfeits(self):
        """Test that returning None causes immediate forfeit."""
        red = MockPlayer("Red Bot", Color.RED, moves=[None])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)

        result = self.controller.play_turn()

        self.assertFalse(result)
        self.assertEqual(self.controller.winner, Color.BLUE)

    def test_player_exception_forfeits(self):
        """Test that player exception causes forfeit."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)

        # Make get_move raise exception
        red.get_move = Mock(side_effect=RuntimeError("Player crashed"))

        self.controller.start_game(red, blue)

        result = self.controller.play_turn()

        self.assertFalse(result)
        self.assertEqual(self.controller.winner, Color.BLUE)

    def test_total_errors_exceed_limit(self):
        """Test that exceeding total error limit causes forfeit."""
        # To accumulate errors across turns without forfeiting per turn,
        # each turn should have 2 invalid moves then 1 valid move
        # Turn 1: 2 errors + valid = total 2
        # Turn 2: 2 errors + valid = total 4
        # Turn 3: 2 errors + valid = total 6
        # Turn 4: 2 errors + valid = total 8
        # Turn 5: 2 errors + valid = total 10 -> forfeit during retry

        red_moves = []
        for i in range(6):  # 6 turns worth
            # 2 invalid moves, then 1 valid unique position
            red_moves.extend([(-1, 0), (-1, 1), (i, 0)])

        blue_moves = [(i, 1) for i in range(6)]  # Valid moves for BLUE

        red = MockPlayer("Red Bot", Color.RED, moves=red_moves)
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=blue_moves)

        self.controller.start_game(red, blue)

        # Play turns until RED forfeits
        turns_played = 0
        max_turns = 15  # Safety limit
        while turns_played < max_turns:
            result = self.controller.play_turn()
            turns_played += 1
            if not result:
                break

        # RED should have forfeited due to total errors
        self.assertEqual(self.controller.status, GameStatus.ERROR)
        self.assertEqual(self.controller.winner, Color.BLUE)
        self.assertGreaterEqual(
            self.controller.player_errors[Color.RED], GameController.MAX_TOTAL_ERRORS)


class TestWinDetection(unittest.TestCase):
    """Test win detection during gameplay."""

    def setUp(self):
        self.controller = GameController(5)

    def test_red_wins_vertically(self):
        """Test RED winning by connecting top to bottom."""
        # Create moves for RED to win vertically
        red_moves = [(i, 2) for i in range(5)]  # Column 2, all rows
        blue_moves = [(i, 0) for i in range(4)]  # Column 0, won't win

        red = MockPlayer("Red Bot", Color.RED, moves=red_moves)
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=blue_moves)

        self.controller.start_game(red, blue)

        # Play turns until RED wins
        for _ in range(9):  # 5 RED + 4 BLUE = 9 moves
            result = self.controller.play_turn()
            if not result:
                break

        self.assertEqual(self.controller.status, GameStatus.RED_WIN)
        self.assertEqual(self.controller.winner, Color.RED)

    def test_blue_wins_horizontally(self):
        """Test BLUE winning by connecting left to right."""
        # Create moves for BLUE to win horizontally
        # RED plays row 0, BLUE plays row 2
        red_moves = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        blue_moves = [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)]

        red = MockPlayer("Red Bot", Color.RED, moves=red_moves)
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=blue_moves)

        self.controller.start_game(red, blue)

        # Play turns until BLUE wins
        # RED goes first, so pattern is: R, B, R, B, R, B, R, B, R, B[win]
        for _ in range(10):  # 5 RED + 5 BLUE = 10 moves
            result = self.controller.play_turn()
            if not result:
                break

        self.assertEqual(self.controller.status, GameStatus.BLUE_WIN)
        self.assertEqual(self.controller.winner, Color.BLUE)


class TestEventLogging(unittest.TestCase):
    """Test event logging functionality."""

    def setUp(self):
        self.controller = GameController(5)

    def test_log_event_creates_event(self):
        """Test that log_event creates an event."""
        self.controller.log_event(LogLevel.INFO, "Test message")

        self.assertEqual(len(self.controller.events), 1)
        event = self.controller.events[0]
        self.assertEqual(event.level, LogLevel.INFO)
        self.assertEqual(event.message, "Test message")
        self.assertIsNotNone(event.timestamp)

    def test_log_event_appends_events(self):
        """Test that multiple events are appended."""
        self.controller.log_event(LogLevel.INFO, "First")
        self.controller.log_event(LogLevel.WARNING, "Second")
        self.controller.log_event(LogLevel.ERROR, "Third")

        self.assertEqual(len(self.controller.events), 3)
        self.assertEqual(self.controller.events[0].message, "First")
        self.assertEqual(self.controller.events[1].message, "Second")
        self.assertEqual(self.controller.events[2].message, "Third")

    def test_invalid_move_logs_warning(self):
        """Test that invalid moves log warnings."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(-1, 0), (1, 1)])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)
        self.controller.play_turn()

        # Check for warning about invalid move
        warnings = [
            e for e in self.controller.events if e.level == LogLevel.WARNING]
        self.assertGreater(len(warnings), 0)

    def test_forfeit_logs_critical(self):
        """Test that forfeit logs critical event."""
        red = MockPlayer("Red Bot", Color.RED, moves=[None])
        blue = MockPlayer("Blue Bot", Color.BLUE)

        self.controller.start_game(red, blue)
        self.controller.play_turn()

        # Check for critical event
        critical = [e for e in self.controller.events if e.level ==
                    LogLevel.CRITICAL]
        self.assertGreater(len(critical), 0)


class TestGameSummary(unittest.TestCase):
    """Test game summary generation."""

    def setUp(self):
        self.controller = GameController(5)

    def test_summary_initial_state(self):
        """Test summary for newly initialized game."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)
        self.controller.start_game(red, blue)

        summary = self.controller.get_game_summary()

        self.assertEqual(summary['status'], GameStatus.ONGOING.value)
        self.assertIsNone(summary['winner'])
        self.assertEqual(summary['total_turns'], 0)
        self.assertEqual(summary['red_player'], "Red Bot")
        self.assertEqual(summary['blue_player'], "Blue Bot")
        self.assertEqual(summary['red_errors'], 0)
        self.assertEqual(summary['blue_errors'], 0)
        self.assertEqual(summary['move_count'], 0)

    def test_summary_after_moves(self):
        """Test summary after some moves."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(0, 0)])
        blue = MockPlayer("Blue Bot", Color.BLUE, moves=[(1, 1)])
        self.controller.start_game(red, blue)

        self.controller.play_turn()
        self.controller.play_turn()

        summary = self.controller.get_game_summary()

        self.assertEqual(summary['total_turns'], 2)
        self.assertEqual(summary['move_count'], 2)

    def test_summary_with_errors(self):
        """Test summary includes error counts."""
        red = MockPlayer("Red Bot", Color.RED, moves=[(-1, 0), (0, 0)])
        blue = MockPlayer("Blue Bot", Color.BLUE)
        self.controller.start_game(red, blue)

        self.controller.play_turn()

        summary = self.controller.get_game_summary()

        self.assertEqual(summary['red_errors'], 1)
        self.assertEqual(summary['blue_errors'], 0)

    def test_summary_with_winner(self):
        """Test summary includes winner."""
        red = MockPlayer("Red Bot", Color.RED)
        blue = MockPlayer("Blue Bot", Color.BLUE)
        self.controller.start_game(red, blue)

        # Manually set winner
        self.controller.status = GameStatus.RED_WIN
        self.controller.winner = Color.RED

        summary = self.controller.get_game_summary()

        self.assertEqual(summary['status'], GameStatus.RED_WIN.value)
        self.assertEqual(summary['winner'], 'RED')


class TestHelperMethods(unittest.TestCase):
    """Test internal helper methods."""

    def setUp(self):
        self.controller = GameController(5)
        self.red = MockPlayer("Red Bot", Color.RED)
        self.blue = MockPlayer("Blue Bot", Color.BLUE)
        self.controller.start_game(self.red, self.blue)

    def test_switch_player(self):
        """Test switching between players."""
        self.assertEqual(self.controller.current_player, self.red)

        self.controller._switch_player()
        self.assertEqual(self.controller.current_player, self.blue)

        self.controller._switch_player()
        self.assertEqual(self.controller.current_player, self.red)

    def test_get_opponent(self):
        """Test getting opponent player."""
        self.assertEqual(self.controller._get_opponent(self.red), self.blue)
        self.assertEqual(self.controller._get_opponent(self.blue), self.red)

    def test_record_error(self):
        """Test recording player errors."""
        self.controller._record_error(self.red)
        self.assertEqual(self.controller.player_errors[Color.RED], 1)

        self.controller._record_error(self.red)
        self.assertEqual(self.controller.player_errors[Color.RED], 2)

        self.controller._record_error(self.blue)
        self.assertEqual(self.controller.player_errors[Color.BLUE], 1)

    def test_validate_move_success(self):
        """Test validating a valid move."""
        result = self.controller._validate_move(2, 2)
        self.assertEqual(result, MoveResult.SUCCESS)

    def test_validate_move_out_of_bounds(self):
        """Test validating out of bounds move."""
        result = self.controller._validate_move(-1, 0)
        self.assertEqual(result, MoveResult.OUT_OF_BOUNDS)

        result = self.controller._validate_move(10, 10)
        self.assertEqual(result, MoveResult.OUT_OF_BOUNDS)

    def test_validate_move_occupied(self):
        """Test validating move on occupied cell."""
        self.controller.board.make_move(2, 2, Color.RED)
        result = self.controller._validate_move(2, 2)
        self.assertEqual(result, MoveResult.CELL_OCCUPIED)

    def test_handle_win_red(self):
        """Test handling RED win."""
        self.controller._handle_win(self.red)

        self.assertEqual(self.controller.status, GameStatus.RED_WIN)
        self.assertEqual(self.controller.winner, Color.RED)

    def test_handle_win_blue(self):
        """Test handling BLUE win."""
        self.controller._handle_win(self.blue)

        self.assertEqual(self.controller.status, GameStatus.BLUE_WIN)
        self.assertEqual(self.controller.winner, Color.BLUE)

    def test_handle_forfeit(self):
        """Test handling player forfeit."""
        self.controller._handle_forfeit(self.red)

        self.assertEqual(self.controller.status, GameStatus.ERROR)
        self.assertEqual(self.controller.winner, Color.BLUE)


class TestGameEvent(unittest.TestCase):
    """Test GameEvent class."""

    def test_event_creation(self):
        """Test creating a game event."""
        event = GameEvent(LogLevel.INFO, "Test message")

        self.assertEqual(event.level, LogLevel.INFO)
        self.assertEqual(event.message, "Test message")
        self.assertIsNotNone(event.timestamp)
        self.assertIsInstance(event.timestamp, float)


if __name__ == '__main__':
    unittest.main()
