"""
Test cases for HexBoard class.

Tests board initialization, move validation, swap moves, win detection,
and other board functionality.
"""

import unittest
from engine.board import HexBoard
from engine.constants import Color, MoveResult, MIN_BOARD_SIZE, MAX_BOARD_SIZE, DEFAULT_BOARD_SIZE


class TestBoardInitialization(unittest.TestCase):
    """Test board initialization and basic properties."""

    def test_default_board_size(self):
        """Test creating board with default size."""
        board = HexBoard()
        self.assertEqual(board.size, DEFAULT_BOARD_SIZE)

    def test_custom_board_size(self):
        """Test creating board with custom size."""
        board = HexBoard(7)
        self.assertEqual(board.size, 7)

    def test_min_board_size(self):
        """Test creating board with minimum valid size."""
        board = HexBoard(MIN_BOARD_SIZE)
        self.assertEqual(board.size, MIN_BOARD_SIZE)

    def test_max_board_size(self):
        """Test creating board with maximum valid size."""
        board = HexBoard(MAX_BOARD_SIZE)
        self.assertEqual(board.size, MAX_BOARD_SIZE)

    def test_too_small_board_size(self):
        """Test that board size below minimum raises error."""
        with self.assertRaises(ValueError) as context:
            HexBoard(MIN_BOARD_SIZE - 1)
        self.assertIn("at least", str(context.exception))

    def test_too_large_board_size(self):
        """Test that board size above maximum raises error."""
        with self.assertRaises(ValueError) as context:
            HexBoard(MAX_BOARD_SIZE + 1)
        self.assertIn("at most", str(context.exception))

    def test_initial_board_empty(self):
        """Test that all cells are initially empty."""
        board = HexBoard(5)
        for row in range(5):
            for col in range(5):
                self.assertEqual(board.get_cell(row, col), Color.EMPTY)

    def test_initial_move_history_empty(self):
        """Test that move history starts empty."""
        board = HexBoard()
        self.assertEqual(len(board.move_history), 0)
        self.assertEqual(board.get_move_count(), 0)

    def test_initial_swap_not_used(self):
        """Test that swap_used is initially False."""
        board = HexBoard()
        self.assertFalse(board.swap_used)


class TestPositionValidation(unittest.TestCase):
    """Test position validation methods."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_valid_positions(self):
        """Test that valid positions are recognized."""
        valid_positions = [(0, 0), (0, 4), (4, 0), (4, 4), (2, 2)]
        for row, col in valid_positions:
            self.assertTrue(self.board.is_valid_position(row, col))

    def test_negative_positions(self):
        """Test that negative positions are invalid."""
        invalid_positions = [(-1, 0), (0, -1), (-1, -1)]
        for row, col in invalid_positions:
            self.assertFalse(self.board.is_valid_position(row, col))

    def test_out_of_bounds_positions(self):
        """Test that positions beyond board size are invalid."""
        invalid_positions = [(5, 0), (0, 5), (5, 5), (10, 10)]
        for row, col in invalid_positions:
            self.assertFalse(self.board.is_valid_position(row, col))


class TestCellAccess(unittest.TestCase):
    """Test getting and checking cell values."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_get_cell_valid(self):
        """Test getting cell value for valid position."""
        self.assertEqual(self.board.get_cell(0, 0), Color.EMPTY)

    def test_get_cell_invalid(self):
        """Test getting cell value for invalid position raises error."""
        with self.assertRaises(ValueError):
            self.board.get_cell(10, 10)

    def test_is_empty_on_empty_cell(self):
        """Test is_empty returns True for empty cell."""
        self.assertTrue(self.board.is_empty(0, 0))

    def test_is_empty_on_occupied_cell(self):
        """Test is_empty returns False after placing stone."""
        self.board.make_move(0, 0, Color.RED)
        self.assertFalse(self.board.is_empty(0, 0))


class TestMakingMoves(unittest.TestCase):
    """Test making moves on the board."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_make_valid_move(self):
        """Test making a valid move succeeds."""
        result = self.board.make_move(2, 3, Color.RED)
        self.assertEqual(result, MoveResult.SUCCESS)
        self.assertEqual(self.board.get_cell(2, 3), Color.RED)

    def test_move_updates_history(self):
        """Test that moves are added to history."""
        self.board.make_move(1, 1, Color.RED)
        self.board.make_move(2, 2, Color.BLUE)
        self.assertEqual(len(self.board.move_history), 2)
        self.assertEqual(self.board.move_history[0], (1, 1, Color.RED))
        self.assertEqual(self.board.move_history[1], (2, 2, Color.BLUE))

    def test_move_out_of_bounds(self):
        """Test that out of bounds move fails."""
        result = self.board.make_move(10, 10, Color.RED)
        self.assertEqual(result, MoveResult.OUT_OF_BOUNDS)

    def test_move_on_occupied_cell(self):
        """Test that move on occupied cell fails."""
        self.board.make_move(2, 2, Color.RED)
        result = self.board.make_move(2, 2, Color.BLUE)
        self.assertEqual(result, MoveResult.CELL_OCCUPIED)

    def test_move_with_empty_color(self):
        """Test that move with EMPTY color fails."""
        result = self.board.make_move(2, 2, Color.EMPTY)
        self.assertEqual(result, MoveResult.INVALID_FORMAT)

    def test_alternating_moves(self):
        """Test making alternating moves."""
        self.board.make_move(0, 0, Color.RED)
        self.board.make_move(1, 1, Color.BLUE)
        self.board.make_move(0, 1, Color.RED)

        self.assertEqual(self.board.get_cell(0, 0), Color.RED)
        self.assertEqual(self.board.get_cell(1, 1), Color.BLUE)
        self.assertEqual(self.board.get_cell(0, 1), Color.RED)


class TestSwapMove(unittest.TestCase):
    """Test swap move functionality (pie rule)."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_swap_not_allowed_on_empty_board(self):
        """Test swap fails when no moves have been made."""
        result = self.board.swap_move()
        self.assertEqual(result, MoveResult.SWAP_NOT_ALLOWED)

    def test_swap_successful_after_first_move(self):
        """Test swap succeeds after exactly one move."""
        self.board.make_move(2, 3, Color.RED)
        result = self.board.swap_move()
        self.assertEqual(result, MoveResult.SUCCESS)

    def test_swap_swaps_position(self):
        """Test that swap correctly swaps row and column."""
        self.board.make_move(2, 3, Color.RED)
        self.board.swap_move()

        # Original position should be empty, swapped position occupied
        self.assertEqual(self.board.get_cell(2, 3), Color.EMPTY)
        self.assertEqual(self.board.get_cell(3, 2), Color.BLUE)

    def test_swap_swaps_color(self):
        """Test that swap changes color to opponent."""
        # RED places stone
        self.board.make_move(1, 4, Color.RED)
        self.board.swap_move()
        # Should become BLUE at swapped position
        self.assertEqual(self.board.get_cell(4, 1), Color.BLUE)

        # Test with BLUE
        board2 = HexBoard(5)
        board2.make_move(3, 1, Color.BLUE)
        board2.swap_move()
        # Should become RED at swapped position
        self.assertEqual(board2.get_cell(1, 3), Color.RED)

    def test_swap_not_allowed_after_two_moves(self):
        """Test swap fails when more than one move exists."""
        self.board.make_move(0, 0, Color.RED)
        self.board.make_move(1, 1, Color.BLUE)
        result = self.board.swap_move()
        self.assertEqual(result, MoveResult.SWAP_NOT_ALLOWED)

    def test_swap_only_works_once(self):
        """Test that swap can only be used once."""
        self.board.make_move(2, 2, Color.RED)
        self.board.swap_move()

        # Try to swap again should fail
        result = self.board.swap_move()
        self.assertEqual(result, MoveResult.SWAP_NOT_ALLOWED)

    def test_swap_updates_history(self):
        """Test that swap updates move history correctly."""
        self.board.make_move(1, 2, Color.RED)
        self.board.swap_move()

        self.assertEqual(len(self.board.move_history), 1)
        self.assertEqual(self.board.move_history[0], (2, 1, Color.BLUE))

    def test_swap_marks_swap_used(self):
        """Test that swap sets swap_used flag."""
        self.board.make_move(0, 1, Color.RED)
        self.assertFalse(self.board.swap_used)
        self.board.swap_move()
        self.assertTrue(self.board.swap_used)


class TestNeighbors(unittest.TestCase):
    """Test getting neighboring cells."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_corner_neighbors(self):
        """Test that corner cells have 2 neighbors."""
        # Top-left corner
        neighbors = self.board.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 2)
        self.assertIn((0, 1), neighbors)
        self.assertIn((1, 0), neighbors)

    def test_edge_neighbors(self):
        """Test that edge cells have correct number of neighbors."""
        # Top edge (not corner)
        neighbors = self.board.get_neighbors(0, 2)
        self.assertEqual(len(neighbors), 4)

    def test_center_neighbors(self):
        """Test that center cells have 6 neighbors."""
        neighbors = self.board.get_neighbors(2, 2)
        self.assertEqual(len(neighbors), 6)

    def test_neighbors_are_valid(self):
        """Test that all returned neighbors are valid positions."""
        for row in range(self.board.size):
            for col in range(self.board.size):
                neighbors = self.board.get_neighbors(row, col)
                for n_row, n_col in neighbors:
                    self.assertTrue(self.board.is_valid_position(n_row, n_col))


class TestWinDetection(unittest.TestCase):
    """Test win condition detection."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_no_win_on_empty_board(self):
        """Test that empty board has no winner."""
        self.assertFalse(self.board.check_win(Color.RED))
        self.assertFalse(self.board.check_win(Color.BLUE))

    def test_empty_color_never_wins(self):
        """Test that EMPTY color never wins."""
        self.assertFalse(self.board.check_win(Color.EMPTY))

    def test_red_vertical_win(self):
        """Test RED wins by connecting top to bottom."""
        # Create a vertical path for RED
        for row in range(5):
            self.board.make_move(row, 2, Color.RED)

        self.assertTrue(self.board.check_win(Color.RED))
        self.assertFalse(self.board.check_win(Color.BLUE))

    def test_blue_horizontal_win(self):
        """Test BLUE wins by connecting left to right."""
        # Create a horizontal path for BLUE
        for col in range(5):
            self.board.make_move(2, col, Color.BLUE)

        self.assertTrue(self.board.check_win(Color.BLUE))
        self.assertFalse(self.board.check_win(Color.RED))

    def test_red_diagonal_win(self):
        """Test RED wins with diagonal path."""
        # Create a diagonal winning path for RED from top to bottom
        # Path: (0,2) -> (1,2) -> (2,1) -> (3,1) -> (4,1)
        self.board.make_move(0, 2, Color.RED)
        self.board.make_move(1, 2, Color.RED)  # bottom from (0,2)
        self.board.make_move(2, 1, Color.RED)  # bottom-left from (1,2)
        self.board.make_move(3, 1, Color.RED)  # bottom from (2,1)
        self.board.make_move(4, 1, Color.RED)  # bottom from (3,1)

        self.assertTrue(self.board.check_win(Color.RED))

    def test_blue_diagonal_win(self):
        """Test BLUE wins with diagonal path."""
        # Create a diagonal winning path for BLUE from left to right
        # Path: (2,0) -> (2,1) -> (1,2) -> (1,3) -> (1,4)
        self.board.make_move(2, 0, Color.BLUE)
        self.board.make_move(2, 1, Color.BLUE)  # right from (2,0)
        self.board.make_move(1, 2, Color.BLUE)  # top-right from (2,1)
        self.board.make_move(1, 3, Color.BLUE)  # right from (1,2)
        self.board.make_move(1, 4, Color.BLUE)  # right from (1,3)

        self.assertTrue(self.board.check_win(Color.BLUE))

    def test_incomplete_path_no_win(self):
        """Test that incomplete paths don't win."""
        # RED path missing one cell
        self.board.make_move(0, 0, Color.RED)
        self.board.make_move(1, 0, Color.RED)
        # Gap at row 2
        self.board.make_move(3, 0, Color.RED)
        self.board.make_move(4, 0, Color.RED)

        self.assertFalse(self.board.check_win(Color.RED))

    def test_blocked_path_no_win(self):
        """Test that blocked paths don't win."""
        # RED tries to go top to bottom but is blocked
        for row in range(4):
            self.board.make_move(row, 2, Color.RED)
        # BLUE blocks
        self.board.make_move(4, 2, Color.BLUE)

        self.assertFalse(self.board.check_win(Color.RED))

    def test_complex_winning_path(self):
        """Test a complex winding path wins."""
        board = HexBoard(7)
        # Create a winding RED path from top to bottom
        # Valid connected path where each cell is a neighbor of the next
        path = [(0, 3), (1, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3)]
        for row, col in path:
            board.make_move(row, col, Color.RED)

        self.assertTrue(board.check_win(Color.RED))


class TestBoardState(unittest.TestCase):
    """Test board state query methods."""

    def setUp(self):
        self.board = HexBoard(5)

    def test_empty_board_not_full(self):
        """Test that empty board is not full."""
        self.assertFalse(self.board.is_full())

    def test_full_board(self):
        """Test that completely filled board is full."""
        for row in range(5):
            for col in range(5):
                color = Color.RED if (row + col) % 2 == 0 else Color.BLUE
                self.board.make_move(row, col, color)

        self.assertTrue(self.board.is_full())

    def test_almost_full_board(self):
        """Test that board with one empty cell is not full."""
        for row in range(5):
            for col in range(5):
                if row != 2 or col != 2:
                    color = Color.RED if (row + col) % 2 == 0 else Color.BLUE
                    self.board.make_move(row, col, color)

        self.assertFalse(self.board.is_full())

    def test_get_empty_cells_on_empty_board(self):
        """Test getting empty cells on empty board."""
        empty_cells = self.board.get_empty_cells()
        self.assertEqual(len(empty_cells), 25)  # 5x5 board

    def test_get_empty_cells_after_moves(self):
        """Test getting empty cells after some moves."""
        self.board.make_move(0, 0, Color.RED)
        self.board.make_move(1, 1, Color.BLUE)

        empty_cells = self.board.get_empty_cells()
        self.assertEqual(len(empty_cells), 23)
        self.assertNotIn((0, 0), empty_cells)
        self.assertNotIn((1, 1), empty_cells)

    def test_get_empty_cells_on_full_board(self):
        """Test getting empty cells on full board."""
        for row in range(5):
            for col in range(5):
                self.board.make_move(row, col, Color.RED)

        empty_cells = self.board.get_empty_cells()
        self.assertEqual(len(empty_cells), 0)

    def test_get_move_count(self):
        """Test getting move count."""
        self.assertEqual(self.board.get_move_count(), 0)

        self.board.make_move(0, 0, Color.RED)
        self.assertEqual(self.board.get_move_count(), 1)

        self.board.make_move(1, 1, Color.BLUE)
        self.assertEqual(self.board.get_move_count(), 2)


class TestStringRepresentation(unittest.TestCase):
    """Test board string representation."""

    def setUp(self):
        self.board = HexBoard(3)

    def test_to_string_empty_board(self):
        """Test string representation of empty board."""
        board_str = self.board.to_string()
        self.assertIn(".", board_str)
        self.assertNotIn("R", board_str)
        self.assertNotIn("B", board_str)

    def test_to_string_with_moves(self):
        """Test string representation with moves."""
        self.board.make_move(0, 0, Color.RED)
        self.board.make_move(1, 1, Color.BLUE)

        board_str = self.board.to_string()
        self.assertIn("R", board_str)
        self.assertIn("B", board_str)

    def test_str_method(self):
        """Test __str__ method."""
        self.board.make_move(0, 1, Color.RED)
        str_result = str(self.board)
        to_string_result = self.board.to_string()
        self.assertEqual(str_result, to_string_result)

    def test_string_has_coordinates(self):
        """Test that string representation includes coordinates."""
        board_str = self.board.to_string()
        # Should have column headers
        self.assertIn("0", board_str)
        self.assertIn("1", board_str)
        self.assertIn("2", board_str)


if __name__ == '__main__':
    unittest.main()
