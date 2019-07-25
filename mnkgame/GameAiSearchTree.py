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

HASH_FLAG_LOWER = -1
HASH_FLAG_UPPER = 1
HASH_FLAG_EXACT = 0


def negamax(
        game,
        depth,
        max_duration=10.0):
    clock = time.time()
    if max_duration < 0:
        return np.nan
    if game.winner(game.turn) == game.turn:
        return -game.win_score
    elif depth == 0 or game.is_full():
        return -game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        value = -negamax(
            game, depth - 1, max_duration - (time.time() - clock))
        game.undo_move(move)
        # best_value = max(value, best_value)
        if value > best_value:
            best_value = value
    return best_value


def negamax_alphabeta(
        game,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True):
    clock = time.time()
    if max_duration < 0.0:
        return np.nan
    if game.winner(game.turn) == game.turn:
        return -game.win_score
    elif depth == 0 or game.is_full():
        return -game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        value = -negamax_alphabeta(
            game, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta, soft)
        game.undo_move(move)
        # best_value = max(value, best_value)
        # alpha = max(best_value, alpha)
        if value > best_value:
            best_value = value
        if best_value > alpha:
            alpha = best_value
        if alpha >= beta:
            break
    return best_value


def negamax_alphabeta_caching(
        game,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        cache=None):
    clock = time.time()
    if max_duration < 0.0:
        return np.nan
    key = repr(game)
    if cache is not None and key in cache:
        return -game.win_score
    if game.winner(game.turn) == game.turn:
        if cache:
            cache.add(repr(game))
        return -game.win_score
    elif depth == 0 or game.is_full():
        return -game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        value = -negamax_alphabeta_caching(
            game, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta, soft, cache)
        game.undo_move(move)
        # best_value = max(value, best_value)
        # alpha = max(best_value, alpha)
        if value > best_value:
            best_value = value
        if best_value > alpha:
            alpha = best_value
        if alpha >= beta:
            break
    return best_value


def negascout(
        game,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        window=3):
    clock = time.time()
    if max_duration < 0.0:
        depth = 0
    if game.winner(game.turn) == game.turn:
        return -game.win_score
    if depth == 0 or game.is_full():
        return game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        if window > 0:
            value = -negascout(
                game, depth - 1, max_duration - (time.time() - clock),
                -beta if soft else alpha, -alpha if soft else beta,
                soft, window - 1)
        else:
            value = -negascout(
                game, depth - 1, max_duration - (time.time() - clock),
                (-alpha - 1) if soft else alpha, -alpha if soft else beta,
                soft, window - 1)
            if alpha < value < beta:
                value = -negascout(
                    game, depth - 1, max_duration - (time.time() - clock),
                    -beta if soft else alpha, -alpha if soft else beta,
                    soft, window - 1)
        game.undo_move(move)
        # best_value = max(value, best_value)
        # alpha = max(best_value, alpha)
        if value > best_value:
            best_value = value
        if best_value > alpha:
            alpha = best_value
        if alpha >= beta:
            break
    return best_value


def negamax_alphabeta_hashing(
        game,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True,
        hash_=None):
    clock = time.time()
    if max_duration < 0:
        return np.nan
    alpha_zero = alpha
    if hash_ is not None:
        key = repr(game)
        if key in hash_:
            hash_value, hash_flag, hash_depth = hash_[key]
            if hash_depth > depth:
                if hash_flag == HASH_FLAG_EXACT:
                    return hash_value
                elif hash_flag == HASH_FLAG_LOWER and hash_value > alpha:
                    alpha = hash_value
                elif hash_flag == HASH_FLAG_UPPER and hash_value < beta:
                    beta = hash_value
                if alpha >= beta:
                    return hash_value
    if game.winner(game.turn) == game.turn:
        return -game.win_score
    if depth == 0 or game.is_full():
        return game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        value = -negamax_alphabeta_hashing(
            game, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta,
            soft, hash_)
        game.undo_move(move)
        # best_value = max(value, best_value)
        # alpha = max(best_value, alpha)
        if value > best_value:
            best_value = value
        if best_value > alpha:
            alpha = best_value
        if alpha >= beta:
            break
    if hash_ is not None:
        if best_value <= alpha_zero:
            hash_flag = HASH_FLAG_UPPER
        elif best_value >= beta:
            hash_flag = HASH_FLAG_LOWER
        else:
            hash_flag = HASH_FLAG_EXACT
        hash_[key] = best_value, hash_flag, depth
    return best_value


@jit(forceobj=True)
def negamax_alphabeta_jit(
        game,
        depth,
        max_duration=10.0,
        alpha=-np.inf,
        beta=np.inf,
        soft=True):
    clock = time.time()
    if max_duration < 0.0:
        return np.nan
    if game.winner(game.turn) == game.turn:
        return -game.win_score
    elif depth == 0 or game.is_full():
        return -game.get_score()
    best_value = -game.win_score
    for move in game.sorted_moves():
        game.do_move(move)
        value = -negamax_alphabeta_jit(
            game, depth - 1, max_duration - (time.time() - clock),
            -beta if soft else alpha, -alpha if soft else beta, soft)
        game.undo_move(move)
        # best_value = max(value, best_value)
        # alpha = max(best_value, alpha)
        if value > best_value:
            best_value = value
        if best_value > alpha:
            alpha = best_value
        if alpha >= beta:
            break
    return best_value


class GameAiSearchTree(GameAi):
    def __init__(self, *_args, **_kws):
        GameAi.__init__(self, *_args, **_kws)

    def get_best_move(
            self,
            game=None,
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
        if 'caching' in method:
            cache = set()
            method_kws.update(dict(cache=cache))
        if 'hashing' in method:
            hash_ = {}
            method_kws.update(dict(hash_=hash_))
        if not max_depth:
            max_depth = 0
        elif max_depth < 0:
            max_depth = game.num_moves_left() - (max_depth + 1)
        if verbose:
            feedback = ', '.join([
                f'Method: {method}',
                f'Min.Depth: {game.num_win}',
                f'Max.Depth: {max(game.num_win, max_depth)}'])
            print(feedback)
        clock = time.time()
        choices = game.sorted_moves()
        best_val = -np.inf
        for depth in range(1, max(game.num_moves_left(), max_depth) + 1):
            new_choices = []
            depth_clock = time.time()
            val = best_val
            for move in game.sorted_moves():
                game.do_move(move)
                val = -func(
                    game, depth, max_duration - (time.time() - clock),
                    **method_kws)
                game.undo_move(move)
                if val > best_val:
                    best_val = val
                    new_choices = [move]
                elif val == best_val and move not in new_choices:
                    new_choices.append(move)
            if not np.isnan(val) and new_choices:
                choices = new_choices
            if best_val in (np.inf, -np.inf):
                break
            if max_duration - (time.time() - clock) < 0.0:
                break
            else:
                if verbose:
                    feedback = ', '.join([
                        f'Time: {time.time() - depth_clock:.3f}',
                        f'Depth: {depth}', f'Best: {best_val}',
                        f'Move(s): {choices}'])
                    print(feedback)
                if callable(callback):
                    callback(**vars())
        if randomize and len(choices) > 1:
            return random.choice(choices)
        else:
            return choices[0]
