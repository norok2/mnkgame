#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import numpy as np
from mnkgame.GameAi import GameAi
from mnkgame import do_nothing_decorator

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
        return np.nan
    if board.winner(board.turn) == board.turn:
        return -board.win_score
    elif depth == 0 or board.is_full():
        return -board.get_score()
    best_value = -board.win_score
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
    if max_duration < 0.0:
        return np.nan
    if board.winner(board.turn) == board.turn:
        return -board.win_score
    elif depth == 0 or board.is_full():
        return -board.get_score()
    best_value = -board.win_score
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha,
            -alpha if soft else beta, soft)
        board.undo_move(coord)
        best_value = max(value, best_value)
        alpha = max(best_value, alpha)
        if alpha >= beta:
            break
    return best_value


@jit(forceobj=True)
def negamax_alphabeta_jit(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True):
    clock = time.time()
    if max_duration < 0.0:
        return np.nan
    if board.winner(board.turn) == board.turn:
        return -board.win_score
    elif depth == 0 or board.is_full():
        return -board.get_score()
    best_value = -board.win_score
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta_jit(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta, soft)
        board.undo_move(coord)
        best_value = max(value, best_value)
        alpha = max(best_value, alpha)
        if alpha >= beta:
            break
    return best_value


def negascout(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        is_first=True):
    clock = time.time()
    if max_duration < 0.0:
        depth = 0
    if board.winner(board.turn) == board.turn:
        return -board.win_score
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -board.win_score
    for coord in board.sorted_moves():
        board.do_move(coord)
        if is_first:
            value = -negascout(
                board, depth - 1, max_duration - (time.time() - clock),
                -beta if soft else alpha, -alpha if soft else beta, soft,
                not is_first)
        else:
            value = -negascout(
                board, depth - 1, max_duration - (time.time() - clock),
                (-alpha - 1) if soft else alpha, -alpha if soft else beta,
                soft, not is_first)
            if alpha < value < beta:
                value = -negascout(
                    board, depth - 1, max_duration - (time.time() - clock),
                    -beta if soft else alpha, -alpha if soft else beta,
                    soft, not is_first)
        board.undo_move(coord)
        best_value = max(value, best_value)
        alpha = max(best_value, alpha)
        if alpha >= beta:
            break
    return best_value


def negamax_alphabeta_hashing(
        board,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        hash_table=None):
    clock = time.time()
    if max_duration < 0:
        return np.nan
    if hash_table is None:
        hash_table = {}
    if (repr(board), board.turn, depth) in hash_table:
        return -hash_table[(repr(board), board.turn, depth)]
    if board.winner(board.turn) == board.turn:
        return -board.win_score
    if depth == 0 or board.is_full():
        return board.get_score()
    best_value = -board.win_score
    for coord in board.sorted_moves():
        board.do_move(coord)
        value = -negamax_alphabeta_hashing(
            board, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta,
            soft, hash_table)
        board.undo_move(coord)
        best_value = max(value, best_value)
        alpha = max(best_value, alpha)
        if alpha >= beta:
            break
    if (repr(board), board.turn, depth) not in hash_table:
        hash_table[(repr(board), board.turn, depth)] = best_value
    return best_value


class GameAiSearchTree(GameAi):
    def __init__(self, *_args, **_kws):
        GameAi.__init__(self, *_args, **_kws)

    def get_best_move(
            self,
            board=None,
            max_duration=10.0,
            method='negamax_alphabeta',
            method_kws=None,
            randomize=False,
            max_depth=None,
            verbose=True,
            callback=None,
            *_args,
            **_kws):
        if method in globals():
            func = globals()[method]
        else:
            func = None
        if not callable(func):
            raise ValueError('Unknown search-tree method.')
        method_kws = dict(method_kws) if method_kws is not None else {}
        if 'hashing' in method:
            hash_table = {}
            method_kws.update(dict(hash_table=hash_table))
        if not max_depth:
            max_depth = 0
        elif max_depth < 0:
            max_depth = board.num_moves_left() - (max_depth + 1)
        if verbose:
            feedback = ', '.join([
                f'Method: {method}',
                f'Min.Depth: {board.num_win}',
                f'Max.Depth: {max(board.num_win, max_depth)}'])
            print(feedback)
        clock = time.time()
        choices = board.sorted_moves()
        best_val = -np.inf
        for depth in range(1, max(board.num_moves_left(), max_depth) + 1):
            new_choices = []
            depth_clock = time.time()
            val = best_val
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
            if not np.isnan(val) and new_choices:
                choices = new_choices
            if verbose:
                feedback = ', '.join([
                    f'Depth: {depth}', f'Best: {best_val}',
                    f'Move(s): {choices}',
                    f'Time: {time.time() - depth_clock:.3f}'])
                print(feedback)
            if callable(callback):
                callback(**locals())
            if best_val in (np.inf, -np.inf):
                break
            if max_duration - (time.time() - clock) < 0.0:
                break
        if randomize and len(choices) > 1:
            return random.choice(choices)
        else:
            return choices[0]
