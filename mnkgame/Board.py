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
            num_win,
            reprs=('-', 'X', 'O')):
        self.rows = rows
        self.cols = cols
        self.num_win = num_win
        self._REPRS = reprs
        self.matrix = None
        self.turn = None
        self.reset()

    def reset(self):
        self.matrix = np.full(
            (self.rows, self.cols), self.EMPTY, dtype=np.uint8)
        self.turn = self.TURNS[-1]

    @property
    def max_num_moves(self):
        return self.rows * self.cols

    @property
    def _win_score(self):
        return self.max_num_moves * self.max_num_moves * self.num_win

    @property
    def win_score(self):
        return (self.max_num_moves - self.num_moves()) * self._win_score

    def __repr__(self):
        text = ''
        for i in range(self.rows):
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
        for i in range(self.rows):
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
            self.turn = self.prev_turn()
            self.matrix[coord] = self.EMPTY
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
            num_win = self.num_win
            # check diagonals
            for i in range(rows - num_win + 1):
                for j in range(cols - num_win + 1):
                    square = matrix[i:i + num_win, j:j + num_win]
                    if np.all(np.diag(np.fliplr(square)) == turn) \
                            or np.all(np.diag(square) == turn):
                        return turn
            # check horizontal
            for i in range(rows):
                for j in range(cols - num_win + 1):
                    if np.all(matrix[i, j:j + num_win] == turn):
                        return turn
            # check vertical
            for i in range(rows - num_win + 1):
                for j in range(cols):
                    if np.all(matrix[i:i + num_win, j] == turn):
                        return turn
            return self.EMPTY

    def winning_series(self, turn=None):
        if self.is_empty():
            return []
        elif turn is None:
            result = []
            for turn in self.TURNS:
                result = self.winning_series(turn)
                if len(result) > 0:
                    break
            return result
        else:
            result = []
            matrix = self.matrix
            rows, cols = self.rows, self.cols
            num_win = self.num_win
            # check diagonals
            for i in range(rows - num_win + 1):
                for j in range(cols - num_win + 1):
                    square = matrix[i:i + num_win, j:j + num_win]
                    if np.all(np.diag(np.fliplr(square)) == turn):
                        result.append(
                            ((i + num_win - 1, j), (i, j + num_win - 1)))
                    if np.all(np.diag(square) == turn):
                        result.append(
                            ((i, j), (i + num_win - 1, j + num_win - 1)))
            # check horizontal
            for i in range(rows):
                for j in range(cols - num_win + 1):
                    if np.all(matrix[i, j:j + num_win] == turn):
                        result.append(((i, j), (i, j + num_win - 1)))
            # check vertical
            for i in range(rows - num_win + 1):
                for j in range(cols):
                    if np.all(matrix[i:i + num_win, j] == turn):
                        result.append(((i, j), (i + num_win - 1, j)))
            return result

    def get_score(self):
        return (self.max_num_moves - self.num_moves() - 1) \
               * (1 if self.turn == self.TURNS[0] else -1)

    @staticmethod
    def extrema_to_coords(begin, end):
        diff = tuple(y - x for x, y in zip(begin, end))
        result = []
        if abs(diff[0]) == abs(diff[1]) or diff[0] == 0 or diff[1] == 0:
            coord = begin
            for _ in range(max(abs(x) for x in diff) + 1):
                result.append(coord)
                coord = tuple(
                    x + (1 if d > 0 else -1 if d < 0 else 0)
                    for x, d in zip(coord, diff))
        return result
