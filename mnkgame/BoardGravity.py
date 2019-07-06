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

    def is_valid_move(self, coord):
        return 0 <= coord < self._cols

    def is_avail_move(self, coord):
        return self._matrix[0, coord] == self.EMPTY

    def avail_moves(self):
        return set(np.where(self._matrix[0, :] == self.EMPTY)[0].tolist())

    def sorted_moves(self):
        return sorted(self.avail_moves(), key=lambda x: abs(x - self._cols / 2))

    def do_move(self, coord):
        if coord in self.avail_moves():
            self._turn = self.next_turn()
            row = self._rows - self._column_heights[coord] - 1
            self._matrix[row, coord] = self.turn
            self._column_heights[coord] += 1
            return True
        else:
            return False

    def undo_move(self, coord):
        if self.is_valid_move(coord) and self._matrix[-1, coord] != self.EMPTY:
            self._turn = self.prev_turn()
            row = self._rows - self._column_heights[coord]
            self._matrix[row, coord] = self.EMPTY
            self._column_heights[coord] -= 1
            return True
        else:
            return False
