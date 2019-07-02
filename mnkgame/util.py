from mnkgame.GameAiSearchTree import GameAiSearchTree
from mnkgame.GameAiRandom import GameAiRandom

def prepare_game(
        rows,
        cols,
        aligned,
        gravity,
        ai_mode):
    if gravity:
        from mnkgame.BoardGravity import BoardGravity as BoardClass
    else:
        from mnkgame.Board import Board as BoardClass
    board = BoardClass(rows, cols, aligned)
    if ai_mode == 'random':
        pass
    else:
        pass
    game_ai_class = GameAiSearchTree
    if ai_mode == 'negamax':
        method = 'negamax'
    elif ai_mode == 'alphabeta':
        method = 'negamax_alphabeta'
    elif ai_mode == 'alphabeta_jit':
        method = 'negamax_alphabeta_jit'
    elif ai_mode == 'pvs':
        method = 'negamax_alphabeta_pvs'
    elif ai_mode == 'alphabeta_hashing':
        method = 'negamax_alphabeta_hashing'
    else:  # if ai_method == 'random':
        game_ai_class = GameAiRandom
        method = None
    return board, game_ai_class, method
