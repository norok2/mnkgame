import random
import copy
import numpy as np
from GameAi import GameAi


def alphabeta(
        board,
        depth=None,
        alpha=-np.inf,
        beta=np.inf,
        turn=None):
    if depth is None:
        depth = board.num_moves_left()
    if turn is None:
        turn = board.last_turn
    board_winner = board.winner()
    if depth == 0 or board_winner != board.EMPTY:
        return board.heuristic() if board_winner == board.EMPTY else (
            np.inf if board_winner == turn else -np.inf)
    best_value = -np.inf if board.last_turn == turn else np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = alphabeta(board, depth - 1, alpha, beta, next(board.turn))
        board.undo_move(coord)
        if board.last_turn == turn:
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
        else:
            best_value = min(best_value, value)
            beta = min(beta, best_value)
        if alpha >= beta:
            break
    return best_value


class GameAiSearchTree(GameAi):
    def __init__(self, *args, **kwargs):
        GameAi.__init__(self, *args, **kwargs)

    def get_best_move(self, board=None, randomize=False):
        board.heuristic = board.num_moves_left
        best_val = -np.inf
        choices = []
        for coord in board.sorted_moves():
            board.do_move(coord)
            val = alphabeta(copy.deepcopy(board), 9)
            board.undo_move(coord)
            if val > best_val:
                best_val = val
                choices = [coord]
            elif val == best_val:
                choices.append(coord)
        if randomize:
            return random.choice(choices)
        else:
            return choices[0]
