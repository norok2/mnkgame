#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from mnkgame.Board import Board


class BoardGravity(Board):
    _STR_SHOW_ROW_COORDS = False

    def __init__(self, *_args, **_kws):
        self._column_heights = None
        Board.__init__(self, *_args, **_kws)

    @property
    def has_gravity(self):
        return True

    def reset(self):
        super(BoardGravity, self).reset()
        self._column_heights = [0] * self._cols

    def is_valid(self):
        result = True
        for j in list(self.avail_moves()):
            prev = self.EMPTY
            for i in range(self._rows):
                if self._matrix[i, j] == self.EMPTY:
                    if prev != self.EMPTY:
                        result = False
                        break
                    else:
                        prev = self.EMPTY
        return result and Board.is_valid(self)

    def is_full(self):
        return not np.any(self._matrix[0, :] == self.EMPTY)

    def is_valid_move(self, col):
        return 0 <= col < self._cols

    def is_avail_move(self, col):
        return self._matrix[0, col] == self.EMPTY

    def avail_moves(self):
        return set(np.where(self._matrix[0, :] == self.EMPTY)[0].tolist())

    def sorted_moves(self):
        return sorted(
            self.avail_moves(), key=lambda x: abs(x - self._cols / 2))

    def do_move(self, col):
        if col in self.avail_moves():
            self._turn = self.next_turn()
            row = self._rows - self._column_heights[col] - 1
            self._matrix[row, col] = self.turn
            self._column_heights[col] += 1
            return True
        else:
            return False

    def undo_move(self, col):
        if self.is_valid_move(col) and self._matrix[-1, col] != self.EMPTY:
            self._turn = self.prev_turn()
            row = self._rows - self._column_heights[col]
            self._matrix[row, col] = self.EMPTY
            self._column_heights[col] -= 1
            return True
        else:
            return False

    def winning_move(self, col):
        rows, cols, num_win, matrix = \
            self._rows, self._cols, self._num_win, self._matrix
        row = self._rows - self._column_heights[col]
        turn = matrix[row, col]
        min_row = max(0, row - num_win)
        max_row = min(rows - num_win, row)
        min_col = max(0, col - num_win)
        max_col = min(cols - num_win, col)
        # check diagonals
        for i in range(min_row, max_row + 1):
            for j in range(min_col, max_col + 1):
                square = matrix[i:i + num_win, j:j + num_win]
                if np.all(np.diag(np.fliplr(square)) == turn) \
                        or np.all(np.diag(square) == turn):
                    return turn
        # check horizontal
        for j in range(min_col, max_col + 1):
            if np.all(matrix[row, j:j + num_win] == turn):
                return turn
        # check vertical
        for i in range(min_row, max_row + 1):
            if np.all(matrix[i:i + num_win, col] == turn):
                return turn
