from mnkgame import IS_TTY

from mnkgame.GameAiSearchTree import GameAiSearchTree
from mnkgame.GameAiRandom import GameAiRandom

AI_MODES = dict(
    alphabeta=dict(
        ai_class=GameAiSearchTree, ai_method='negamax_alphabeta'),
    negamax=dict(
        ai_class=GameAiSearchTree, ai_method='negamax'),
    scout=dict(
        ai_class=GameAiSearchTree, ai_method='negascout'),
    caching=dict(
        ai_class=GameAiSearchTree, ai_method='negamax_alphabeta_caching'),
    hashing=dict(
        ai_class=GameAiSearchTree, ai_method='negamax_alphabeta_hashing'),
    more_random=dict(
        ai_class=GameAiRandom, ai_method='more'),
    less_random=dict(
        ai_class=GameAiRandom, ai_method='less'),
    zero_random=dict(
        ai_class=GameAiRandom, ai_method='zero'),
)
USER_INTERFACES = (
    'auto',
    'gui',
    # 'tui',
    'cli')
ALIASES = dict(
    custom=None,
    tic_tac_toe=dict(rows=3, cols=3, num_win=3, gravity=False),
    connect4=dict(rows=6, cols=7, num_win=4, gravity=True),
    gomoku=dict(rows=15, cols=15, num_win=5, gravity=False),
)


def guess_alias(**_kws):
    labels = 'rows', 'cols', 'num_win', 'gravity'
    for alias, info in ALIASES.items():
        if info and all(
                k in _kws and k in info and _kws[k] == info[k]
                for k in labels):
            return alias
    return 'custom'


def make_board(
        rows,
        cols,
        num_win,
        gravity):
    if gravity:
        from mnkgame.BoardGravity import BoardGravity as BoardClass
    else:
        from mnkgame.Board import Board as BoardClass
    return BoardClass(rows, cols, num_win)


def is_gui_available():
    tk = None
    try:
        import tkinter as tk
    except ImportError:
        try:
            import Tkinter as tk
        except ImportError:
            pass

    if tk is not None:
        root = None
        try:
            root = tk.Tk()
        except tk.TclError:
            result = False
        else:
            result = True
        finally:
            if root is not None:
                root.destroy()
    else:
        result = False
    return result


def is_tui_available():
    return IS_TTY
