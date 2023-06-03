"""This Python module contains multiple implementations of Player object of Connected4 project.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of TA's
responsible for grading works of the CSC111 students at the University
of Toronto St. George campus. All forms of distribution of this code,
whether as given or with any changes, are expressly prohibited. For
more information on copyright for Connect N materials, please consult
one of our team members eaither face-to-face or via email.

EMAILS:
Ahmad Abugharbieh: ahmad.abugharbieh@mail.utoronto.ca
Jerry YAN: jerryzhixi.yan@mail.utoronto.ca
Burak UNAT: burak.unat@mail.utoronto.ca
Tim Shen: shutian.shen@mail.utoronto.ca

This file is Copyright (c) 2023 Jerry Yan, Burak Unat, Ahmad Abugharbieh
and Tim Shen.
"""

from __future__ import annotations

from copy import deepcopy
import random
from typing import Optional

import components
import constants


class Player:
    """Player object

    Instance Attributes:
    - name: the name of this Player
    - color: an RGB tuple representing this Player's color
    """

    name: int
    color: tuple[int, int, int]

    def __init__(self, name: int) -> None:
        """ Initialization of Player class"""
        self.name = name
        self.color = constants.RED if self.name == constants.PLAYER1 else constants.YELLOW

    def make_move(self, row: int, col: int, board: components.Board) -> components.Node:
        """Make move by filling the node at (row, col) with self.name on board. Also, re-draw that node with
        self.color. Finally, return that node."""
        node_to_occupy = board.nodes[(row, col)]
        node_to_occupy.fill = self.name
        node_to_occupy.draw(board.screen, node_to_occupy.rect.center, constants.RAD, self.color)
        return node_to_occupy

    def is_winning_move(self, node: components.Node) -> bool:
        """Find the sequences that this player has formed with node. Then, return whether any of the sequences has
        length >= CONNECT_N."""
        vertical_sequence = node.find_sequence(self, constants.VERTICAL, set())
        horiz_sequence = node.find_sequence(self, constants.HORIZ, set())
        top_right_sequence = node.find_sequence(self, constants.TOP_RIGHT, set())
        top_left_sequence = node.find_sequence(self, constants.TOP_LEFT, set())
        if any(len(seq) >= constants.CONNECT_N for seq in
               [vertical_sequence, horiz_sequence, top_left_sequence, top_right_sequence]):
            return True
        return False

    def pick_best_move(self, piece: int) -> int:
        """Pick the best move available and return the column"""
        raise NotImplementedError


class AIPlayer(Player):
    """AI implementation of Player

    Instance Attributes:
    - board: this is initially the actual game board that this AIPlayer takes in, but before this AIPlayer places a test
      move to evaluate the scores of different potential moves, board is switched to a deepcopy of itself so that
      the test moves do not mutate the actual game board. Every time a move has been evaluated, board is reassigned back
      to the initial game board.
    - temp_board: initially set to None, this attribute is the temporary location to store the original game board when
      self.board is assigned to its copy. temp_board is reassigned back to None every time a move has been evaluated.
    """
    board: components.Board
    temp_board: Optional[components.Board]

    def __init__(self, board: components.Board, name: int) -> None:
        """ Initialization of AIPlayer class"""
        super().__init__(name)
        self.board = board
        self.temp_board = None

    def score_position(self, piece: int) -> int:
        """Evaluate the state of the copy board by accumulating the scores of every
        window (vertically, horizontally, and diagonally) of length CONNECT_N
        on this board (after the AI Player has placed a test move on its copy board).
        In addition, accumulate to the score the number of self's center pieces * 6.
        This is to indicate that the centercolumn is prefered over other columns
        (since more opportunity lie in the center).
        """
        score = 0
        # Score center column
        center_array = self.board.get_nodes_fill_for_column(self.board.side_length // 2)
        center_count = center_array.count(piece)
        score += center_count * 6

        score += self._score_horizontal(piece)
        score += self._score_vertical(piece)
        score += self._score_positive_diagonal(piece)
        score += self._score_neagtive_diagonal(piece)

        return int(score)

    def _score_horizontal(self, piece: int) -> int:
        """Score horizantally for every possible horizontal partial row with length CONNECT_N"""
        temp_score = 0
        for row in range(self.board.side_length):
            row_array = self.board.get_nodes_fill_for_row(row)
            for col in range(self.board.side_length - constants.CONNECT_N + 1):
                window = row_array[col:col + constants.CONNECT_N]
                temp_score += self.evaluate_window(window, piece)
        return int(temp_score)

    def _score_vertical(self, piece: int) -> int:
        """Score vertically for every possible vertical partial column of nodes with length CONNECT_N"""
        temp_score = 0
        for col in range(self.board.side_length):
            col_array = self.board.get_nodes_fill_for_column(col)
            for row in range(self.board.side_length - constants.CONNECT_N + 1):
                window = col_array[row:row + constants.CONNECT_N]
                temp_score += self.evaluate_window(window, piece)
        return int(temp_score)

    def _score_positive_diagonal(self, piece: int) -> int:
        """Score every positive diagonal (shape of f(x) = x) window of length CONNECT_N on the board"""
        temp_score = 0
        for r in range(self.board.side_length - constants.CONNECT_N + 1):
            for c in range(self.board.side_length - constants.CONNECT_N + 1):
                window = self.board.get_positive_diagonal(r, c, set())
                temp_score += self.evaluate_window(window, piece)
        return int(temp_score)

    def _score_neagtive_diagonal(self, piece: int) -> int:
        """Score every negative sloped diagonal (shape of f(x) = -x) window of length CONNECT_N on the board"""
        temp_score = 0
        for r in range(self.board.side_length - constants.CONNECT_N + 1):
            for c in range(self.board.side_length - constants.CONNECT_N + 1):
                # window = [self.board[r + 3 - i][c + i] for i in range(CONNECT_N)]
                window = self.board.get_negative_diagonal(r + constants.CONNECT_N - 1, c, set())
                temp_score += self.evaluate_window(window, piece)
        return int(temp_score)

    def make_move(self, row: int, col: int, board: components.Board, with_display: bool = True) -> components.Node:
        """Make move that fills node with coordinate (row, col) with player.name"""
        node_to_occupy = board.nodes[(row, col)]
        node_to_occupy.fill = self.name
        if with_display:
            node_to_occupy.draw(board.screen, node_to_occupy.rect.center, constants.RAD, self.color)
        return node_to_occupy

    def pick_best_move(self, piece: int) -> int:
        """Choose the best, highest-score possible move (column).
        """
        valid_locations = self.board.get_valid_locations()
        best_score = -10000
        best_col = random.choice(valid_locations)
        screen = self.board.screen
        self.board.screen = None
        for col in valid_locations:
            row = self.board.get_next_open_row(col)
            temp_board = deepcopy(self.board)
            self.board, self.temp_board = temp_board, self.board
            self.make_move(row, col, self.board, with_display=False)
            score = self.score_position(piece)
            if score > best_score:
                best_score = score
                best_col = col
            self.board, self.temp_board = self.temp_board, None
        self.board.screen = screen

        return best_col

    def evaluate_window(self, window: list[int], piece: int) -> int:
        """Evaluate the current situation (i.e. after the AI piece is placed on its copy board)
        of the window of length CONNECT_N by applying the following rules:
         - If the number of self's pieces == CONNECT_N, then increase the score to 1000000—i.e. this is THE move to win.
         - elif the number of self's pieces == CONNECT_N - 1 and there still has one empty slot,
           then increase the score by 40, etc.

        For the opponent's pieces, AIPlayer does not want it to have long connected sequences. So,
        - if the number of opp_piece is CONNECT_N - 1 and there is an empty slot, then it means that after self's move
        to this piece's location on the copy board, the opponent will win.
        This means that AIPlayer does NOT want to move there. So, in that case, decrease the score by 800
        - elif ... the rest of the code follows the same logic as above

        Preconditions:
        - len(window) == CONNECT_N
        - piece == PLAYER2
        """
        score = 0
        opp_piece = constants.PLAYER1

        if window.count(piece) == constants.CONNECT_N:
            score += 1000
        elif window.count(piece) == constants.CONNECT_N - 1 and window.count(constants.EMPTY) == 1:
            score += 40
        elif window.count(piece) == constants.CONNECT_N - 2 and window.count(constants.EMPTY) == 2:
            score += 10
        else:
            score += 1

        if window.count(opp_piece) == constants.CONNECT_N - 1 and window.count(constants.EMPTY) == 1:
            score -= 800
        elif window.count(opp_piece) == constants.CONNECT_N - 2 and window.count(constants.EMPTY) == 2:
            score -= 400
        elif window.count(opp_piece) == constants.CONNECT_N - 3 and window.count(constants.EMPTY) == 3:
            score -= 10
        else:
            score -= 1

        return int(score)


class EasyAIPlayer(AIPlayer):
    """Easy AI Player that just chooses a random valid move every turn"""

    def pick_best_move(self, piece: int) -> int:
        """Pick a "best"—random and valid—move and return its column"""
        valid_moves = self.board.get_valid_locations()
        return random.choice(valid_moves)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['constants', 'components', 'random', 'copy', 'typing'],  # the names (strs)
        # of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
