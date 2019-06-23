#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from GameAi import GameAi

random.seed()


class GameAiRandom(GameAi):
    def __init__(self, *_args, **_kws):
        GameAi.__init__(self, *_args, **_kws)

    def get_best_move(
            self,
            board=None,
            *_args,
            **_kws):
        avail_moves = board.avail_moves()
        num_moves = len(avail_moves)
        return list(avail_moves)[random.randint(0, num_moves - 1)]
