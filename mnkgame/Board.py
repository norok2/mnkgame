#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

NUM_DIGITS = 10


class Board:
    EMPTY = 0
    TURNS = (1, 2)
    _STR_BORDERS = '-', '|', '+'
    _STR_SHOW_ROW_COORDS = True
    _STR_SHOW_COL_COORDS = True

    def __init__(
            self,
            rows,
            cols,
            win_len,
            reprs=('-', 'X', 'O')):
        self.rows = rows
        self.cols = cols
        self.win_len = win_len
        self._REPRS = reprs
        self.matrix = None
        self.turn = None
        self.reset()

    def reset(self):
        self.matrix = np.full(
            (self.rows, self.cols), self.EMPTY, dtype=np.uint8)
        self.turn = self.TURNS[-1]

    @property
    def _STR_ROW_RANGE(self):
        return range(self.rows)

    def __repr__(self):
        text = ''
        for i in self._STR_ROW_RANGE:
            text += ''.join([self._REPRS[x] for x in self.matrix[i, :]]) + '\n'
        return text[:-1]

    def __str__(self):
        text = ''
        hor, ver, cross = self._STR_BORDERS
        reprs = (' ',) + self._REPRS[1:]
        hor_sep = cross + (hor + cross) * self.cols + '\n'
        if self._STR_SHOW_COL_COORDS:
            header = cross \
                     + cross.join(
                [str(i % NUM_DIGITS) for i in range(self.cols)]) \
                     + cross + '\n'
        else:
            header = hor_sep
        text += header
        for i in self._STR_ROW_RANGE:
            text += \
                (str(i % NUM_DIGITS) if self._STR_SHOW_ROW_COORDS else ver) \
                + ver.join([reprs[x] for x in self.matrix[i, :]]) \
                + ver + '\n' + hor_sep
        return text[:-1]

    def next_turn(self, turn=None):
        if turn is None:
            turn = self.turn

        # : more general implementation
        # if turn in self.TURNS:
        #     return self.TURNS[self.TURNS.index(turn) + 1 % len(self.TURNS)]
        # else:
        #     return self.EMPTY

        # : faster implementation
        if turn == self.TURNS[0]:
            return self.TURNS[1]
        elif turn == self.TURNS[1]:
            return self.TURNS[0]
        else:
            return self.EMPTY

    prev_turn = next_turn

    def is_empty(self):
        return np.all(self.matrix == self.EMPTY)

    def is_valid(self):
        raise abs(
            np.sum(self.matrix == self.TURNS[0])
            - np.sum(self.matrix == self.TURNS[1])) in {0, 1}

    def is_full(self):
        return not np.any(self.matrix == self.EMPTY)

    def is_valid_move(self, coord):
        return 0 <= coord[0] < self.rows and 0 <= coord[1] < self.cols

    def is_avail_move(self, coord):
        return self.matrix[coord] == self.EMPTY

    def avail_moves(self):
        return set(zip(
            *[idx.tolist() for idx in np.where(self.matrix == self.EMPTY)]))

    def sorted_moves(self):
        return sorted(
            self.avail_moves(),
            key=lambda x: (
                ((x[0] - self.rows // 2) ** 2
                 + (x[1] - self.cols // 2) ** 2)))

    def do_move(self, coord):
        if coord in self.avail_moves():
            self.turn = self.next_turn()
            self.matrix[coord] = self.turn
            return True
        else:
            return False

    def undo_move(self, coord):
        if self.is_valid_move(coord) and self.matrix[coord] != self.EMPTY:
            self.matrix[coord] = self.EMPTY
            self.turn = self.next_turn()
            return True
        else:
            return False

    def do_moves(self, coords, reset=True):
        if reset:
            self.reset()
        result = all([self.do_move(coord) for coord in coords])
        if not result:
            self.undo_moves(coords[::-1])
        return result

    def undo_moves(self, coords):
        return all([self.undo_move(coord) for coord in coords])

    def num_moves(self):
        return int(np.sum(self.matrix != self.EMPTY))

    def num_moves_left(self):
        return int(np.sum(self.matrix == self.EMPTY))

    def winner(self, turn=None):
        if self.is_empty():
            return self.EMPTY
        elif turn is None:
            result = None
            for turn in self.TURNS:
                result = self.winner(turn)
                if result != self.EMPTY:
                    break
            return result
        else:
            matrix = self.matrix
            rows, cols = self.rows, self.cols
            win_len = self.win_len
            # check diagonals
            for i in range(rows - win_len + 1):
                for j in range(cols - win_len + 1):
                    square = matrix[i:i + win_len, j:j + win_len]
                    if np.all(np.diag(np.fliplr(square)) == turn) \
                            or np.all(np.diag(square) == turn):
                        return turn
            # check horizontal
            for i in range(rows):
                for j in range(cols - win_len + 1):
                    if np.all(matrix[i, j:j + win_len] == turn):
                        return turn
            # check vertical
            for i in range(rows - win_len + 1):
                for j in range(cols):
                    if np.all(matrix[i:i + win_len, j] == turn):
                        return turn
            return self.EMPTY

    def get_victory_coords(self):
        if self.winner(None):
            pass
        raise NotImplementedError

    def get_score(self):
        return self.num_moves() * (-1) ** self.turn