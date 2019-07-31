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
        self._rows = rows
        self._cols = cols
        self._num_win = num_win
        self._reprs = reprs
        self._matrix = None
        self._turn = None
        self._max_num_moves = rows * cols
        self.reset()

    def reset(self):
        self._matrix = np.full(
            (self._rows, self._cols), self.EMPTY, dtype=np.uint8)
        self._turn = self.TURNS[-1]

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def num_win(self):
        return self._num_win

    @property
    def matrix(self):
        return self._matrix

    @property
    def turn(self):
        return self._turn

    @property
    def max_num_moves(self):
        return self._max_num_moves

    @property
    def _win_score(self):
        return self.max_num_moves * self.max_num_moves * self._num_win

    @property
    def win_score(self):
        # return (self.max_num_moves - self.num_moves()) * self._win_score
        return np.inf

    def __repr__(self):
        text = ''
        for i in range(self._rows):
            text += ''.join(
                [self._reprs[x] for x in self._matrix[i, :]]) + '\n'
        text += self._reprs[self._turn]
        return text

    def __str__(self):
        text = ''
        hor, ver, cross = self._STR_BORDERS
        reprs = (' ',) + self._reprs[1:]
        hor_sep = cross + (hor + cross) * self._cols + '\n'
        if self._STR_SHOW_COL_COORDS:
            header = cross \
                     + cross.join(
                [str(i % NUM_DIGITS) for i in range(self._cols)]) \
                     + cross + '\n'
        else:
            header = hor_sep
        text += header
        for i in range(self._rows):
            text += \
                (str(i % NUM_DIGITS) if self._STR_SHOW_ROW_COORDS else ver) \
                + ver.join([reprs[x] for x in self._matrix[i, :]]) \
                + ver + '\n' + hor_sep
        return text[:-1]

    def next_turn(self, turn=None):
        if turn is None:
            turn = self._turn

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
        return np.all(self._matrix == self.EMPTY)

    def is_valid(self):
        raise abs(
            np.sum(self._matrix == self.TURNS[0])
            - np.sum(self._matrix == self.TURNS[1])) in {0, 1}

    def is_full(self):
        return not np.any(self._matrix == self.EMPTY)

    def is_valid_move(self, move):
        return 0 <= move[0] < self._rows and 0 <= move[1] < self._cols

    def is_avail_move(self, coord):
        return self._matrix[coord] == self.EMPTY

    def avail_moves(self):
        return set(zip(
            *[idx.tolist() for idx in np.where(self._matrix == self.EMPTY)]))

    def sorted_moves(self):
        return sorted(
            self.avail_moves(),
            key=lambda x: (
                ((x[0] - self._rows // 2) ** 2
                 + (x[1] - self._cols // 2) ** 2)))

    def do_move(self, coord):
        if coord in self.avail_moves():
            self._turn = self.next_turn()
            self._matrix[coord] = self._turn
            return True
        else:
            return False

    def undo_move(self, move):
        if self.is_valid_move(move) and self._matrix[move] != self.EMPTY:
            self._turn = self.prev_turn()
            self._matrix[move] = self.EMPTY
            return True
        else:
            return False

    def do_moves(self, moves, reset=True):
        if reset:
            self.reset()
        result = all(self.do_move(move) for move in moves)
        if not result:
            self.undo_moves(moves[::-1])
        return result

    def undo_moves(self, moves):
        return all(self.undo_move(move) for move in moves)

    def num_moves(self):
        return int(np.sum(self._matrix != self.EMPTY))

    def num_moves_left(self):
        return int(np.sum(self._matrix == self.EMPTY))

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
            matrix = self._matrix
            rows, cols = self._rows, self._cols
            num_win = self._num_win
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
            matrix = self._matrix
            rows, cols = self._rows, self._cols
            num_win = self._num_win
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
               * (1 if self._turn == self.TURNS[0] else -1)

    @staticmethod
    def extrema_to_moves(begin, end):
        diff = tuple(y - x for x, y in zip(begin, end))
        result = []
        if abs(diff[0]) == abs(diff[1]) or diff[0] == 0 or diff[1] == 0:
            move = begin
            for _ in range(max(abs(x) for x in diff) + 1):
                result.append(move)
                move = tuple(
                    x + (1 if d > 0 else -1 if d < 0 else 0)
                    for x, d in zip(move, diff))
        return result
