import random
import time
import numpy as np
from GameAi import GameAi
from util import do_nothing_decorator

# Numba import
try:
    from numba import jit
except ImportError:
    HAS_JIT = False
    jit = do_nothing_decorator
else:
    HAS_JIT = True


def negamax(
        board,
        depth,
        max_duration=10.0):
    clock = time.time()
    if max_duration < 0:
        depth = 0
    if board.winner(board.turn) == board.turn:
        return -np.inf
    if depth == 0 or board.is_full():
        return board.get_score() * (-1) ** board.turn
    best_value = -np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax(
            board, depth - 1, max_duration - (time.time() - clock))
        board.undo_move(coord)
        best_value = max(value, best_value)
    return best_value


def negamax_alphabeta(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True):
    clock = time.time()
    if max_duration < 0:
        depth = 0
    if board.winner(board.turn) == board.turn:
        return -np.inf
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta)
        board.undo_move(coord)
        best_value = max(value, best_value)
        if best_value >= beta:
            break
        if best_value > alpha:
            alpha = best_value
    return best_value


@jit
def negamax_alphabeta_jit(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True):
    clock = time.time()
    if max_duration < 0:
        depth = 0
    if board.winner(board.turn) == board.turn:
        return -np.inf
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta_jit(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta)
        board.undo_move(coord)
        best_value = max(value, best_value)
        if best_value >= beta:
            break
        if best_value > alpha:
            alpha = best_value
    return best_value


def negamax_alphabeta_pvs(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        is_first=True):
    clock = time.time()
    if max_duration < 0:
        depth = 0
    if board.winner(board.turn) == board.turn:
        return -np.inf
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        if is_first:
            value = -negamax_alphabeta_pvs(
                board, depth - 1, max_duration - (time.time() - clock),
                -beta if soft else alpha, -alpha if soft else beta, soft,
                not is_first)
        else:
            value = -negamax_alphabeta_pvs(
                board, depth - 1, max_duration - (time.time() - clock),
                (-alpha - 1) if soft else alpha, -alpha if soft else beta,
                soft, not is_first)
            if alpha < value < beta:
                value = -negamax_alphabeta_pvs(
                    board, depth - 1, max_duration - (time.time() - clock),
                    -beta if soft else alpha, -alpha if soft else beta,
                    soft, not is_first)
        board.undo_move(coord)
        best_value = max(value, best_value)
        if best_value >= beta:
            break
        if best_value > alpha:
            alpha = best_value
    return best_value


def negamax_alphabeta_hashing(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        hashtable=None):
    # todo: fix hashing
    clock = time.time()
    if max_duration < 0:
        depth = 0
    if hashtable is None:
        hashtable = {}
    if (board, depth) in hashtable:
        return hashtable[(board, depth)]
    if board.winner(board.turn) == board.turn:
        return -np.inf
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -np.inf
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta_hashing(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta)
        board.undo_move(coord)
        best_value = max(value, best_value)
        if best_value >= beta:
            break
        if best_value > alpha:
            alpha = best_value
    hashtable[(board, depth)] = best_value
    return best_value


class GameAiSearchTree(GameAi):
    def __init__(self, *args, **kwargs):
        GameAi.__init__(self, *args, **kwargs)

    def get_best_move(
            self,
            board=None,
            max_duration=10.0,
            method='negamax_alphabeta_jit',
            method_kws=None,
            randomize=False,
            max_depth=None,
            verbose=True):
        if method in globals():
            func = globals()[method]
        else:
            func = None
        if not callable(func):
            raise ValueError('Unknown search-tree method.')
        method_kws = dict(method_kws) if method_kws is not None else {}
        if 'hashing' in method:
            hashtable = {}
            method_kws.update(dict(hashtable=hashtable))
        if not max_depth:
            max_depth = 0
        elif max_depth < 0:
            max_depth = board.num_moves_left() - (max_depth + 1)
        if verbose:
            print(
                f'Method: {method},'
                f' Min. Depth: {board.win_len},'
                f' Max. Depth: {max(board.win_len, max_depth)}')
        clock = time.time()
        choices = board.sorted_moves()
        for depth in range(board.win_len, max(board.win_len, max_depth) + 1):
            best_val = -np.inf
            new_choices = []
            begin_time = time.time()
            for coord in board.sorted_moves():
                board.do_move(coord)
                val = -func(
                    board, depth, max_duration - (time.time() - clock),
                    **method_kws)
                board.undo_move(coord)
                if val > best_val:
                    best_val = val
                    new_choices = [coord]
                elif val == best_val and coord not in new_choices:
                    new_choices.append(coord)
            if verbose:
                print(
                    f'Depth: {depth}, Best: {best_val},'
                    f' Move: {choices}, Time: {time.time() - begin_time:.3f}')
            if max_duration - (time.time() - clock) > 0:
                choices = new_choices
            else:
                break
        if randomize and len(choices) > 1:
            return random.choice(choices)
        else:
            return choices[0]
