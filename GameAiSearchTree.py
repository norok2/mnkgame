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
        turn = board.curr_turn
    board_winner = board.winner()
    if depth == 0 or board_winner != board.EMPTY:
        return board.heuristic() if board_winner == board.EMPTY else (
            np.inf if board_winner == turn else -np.inf)
    best_value = alpha if board.curr_turn == turn else beta
    print(turn, depth)
    for coord in board.sorted_moves():
        board.do_move(coord)
        deeper_turn = board.curr_turn \
            if board.curr_turn != turn else next(copy.copy(board.turn))
        value = alphabeta(board, depth - 1, alpha, beta, deeper_turn)
        board.undo_move(coord)
        if board.curr_turn == turn:
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

    def get_best_move(self, board=None, randomize=False, max_depth=12):
        board.heuristic = board.num_moves_left
        best_val = -np.inf
        choices = []
        for depth in range(1, max_depth + 1):
            for coord in board.sorted_moves():
                board.do_move(coord)
                val = alphabeta(copy.deepcopy(board), depth)
                board.undo_move(coord)
                if val > best_val:
                    best_val = val
                    choices = [coord]
                elif val == best_val and coord not in choices:
                    choices.append(coord)
            print(f'Depth: {depth}, Best: {best_val}, Move: {choices}')
        if randomize and len(choices) > 1:
            return random.choice(list(choices))
        else:
            return list(choices)[0]
