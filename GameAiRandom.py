import random
from GameAi import GameAi

random.seed()


class GameAiRandom(GameAi):
    def __init__(self, *args, **kwargs):
        GameAi.__init__(self, *args, **kwargs)

    def get_best_move(self, board=None):
        avail_moves = board.avail_moves()
        num_moves = len(avail_moves)
        return list(avail_moves)[random.randint(0, num_moves - 1)]
