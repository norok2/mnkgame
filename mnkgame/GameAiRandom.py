#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

import numpy as np

from mnkgame.GameAi import GameAi

random.seed()
np.random.seed()


class GameAiRandom(GameAi):
    def __init__(self, *_args, **_kws):
        GameAi.__init__(self, *_args, **_kws)

    def get_best_move(
            self,
            board=None,
            max_duration=0.1,
            method='more',
            verbose=True,
            callback=None,
            *_args,
            **_kws):
        if method == 'more':
            choices = list(board.avail_moves())
            i = random.randint(0, len(choices) - 1)
            choice = choices[i]
        elif method == 'less':
            choices = board.sorted_moves()
            weights = [2 ** (len(choices) - i) for i in range(len(choices))]
            weights = [weight / sum(weights) for weight in weights]
            i = np.random.choice(range(len(choices)), 1, True, weights)[0]
            choice = choices[i]
        else:  # if method == 'zero':
            choices = board.sorted_moves()
            choice = choices[0]
        if verbose:
            feedback = ', '.join([
                f'Method: {method}', f'Best: {choice}', f'Move(s): {choices}'])
            print(feedback)
        if callable(callback):
            callback(**vars())
        return choice
