import numpy as np
import itertools

from Board import Board


class BoardGravity(Board):
    def __init__(self, *args, **kwargs):
        Board.__init__(self, *args, **kwargs)

    def _str_row_range(self):
        return range(self.rows - 1, -1, -1)

    def is_valid(self):
        # todo: include gravity
        return Board.is_valid(self)

    def is_full(self):
        return not np.any(self.matrix == self.EMPTY)

    def is_valid_move(self, coord):
        return 0 <= coord < self.cols

    def is_avail_move(self, coord):
        return self.matrix[-1, coord] == self.EMPTY

    def avail_moves(self):
        return set(np.where(self.matrix[-1, :] == self.EMPTY)[0].tolist())

    def sorted_moves(self):
        return sorted(self.avail_moves(), key=lambda x: abs(x - self.cols / 2))

    def do_move(self, coord):
        if coord in self.avail_moves():
            self.last_turn = next(self.turn)
            empty_row = np.where(self.matrix[:, coord] == self.EMPTY)[0][0]
            self.matrix[empty_row, coord] = self.last_turn
            return True
        else:
            return False

    def undo_move(self, coord):
        if self.is_valid_move(coord) and self.matrix[0, coord] != self.EMPTY:
            empty_row = np.where(self.matrix[:, coord] == self.EMPTY)[0]
            empty_row = empty_row[0] if len(empty_row) > 0 else self.rows
            self.matrix[empty_row - 1, coord] = self.EMPTY
            self.last_turn = next(self.turn)
            return True
        else:
            return False

    def get_victory_coords(self):
        if self.winner(None):
            pass
        raise NotImplementedError
