#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees
import pickle

from mnkgame import prettify
from mnkgame import D_VERB_LVL
from mnkgame import msg

from mnkgame.util import make_board
from mnkgame.util import AI_MODES, ALIASES, USER_INTERFACES


# ======================================================================
def colorized_board(board, pretty=True, pieces=True, grid=True):
    text = str(board)
    if pretty:
        substs = dict()
        if pieces:
            substs.update({'X': '{o}{B}X{x}', 'O': '{o}{R}O{x}'})
        if grid:
            substs.update({x: '{o}' + x + '{x}' for x in ('|', '+', '-')})
        for key, val in substs.items():
            text = text.replace(key, val)
    return prettify(text, pretty)


# ======================================================================
def handle_endgame(
        board,
        text,
        ask,
        formatting):
    result = True
    print('\n' + colorized_board(board, bool(formatting)), sep='')
    board.reset()
    msg(text, fmtt=formatting)
    if ask:
        msg('Play a new game ([Y]/n)? ', end='',
            fmtt='{t.bold}' if bool(formatting) else False)
        choice = input()
        if choice.strip().lower() == 'n':
            result = False
    return result


# ======================================================================
def handle_move(
        board,
        move,
        is_computer,
        undo_history,
        redo_history,
        ask_continue=True,
        pretty=True):
    if is_computer:
        msg('Computer Move is: ' + str(move),
            fmtt='{t.magenta}' if pretty else False)
    if board.do_move(move):
        undo_history.append(move)
    if board.winner(board.turn) == board.turn:
        result = handle_endgame(
            board,
            'YOU LOST!\n' if is_computer else 'Congratulations! You WIN!\n',
            ask_continue,
            ('{t.bold}{t.red}' if is_computer else '{t.bold}{t.green}')
            if pretty else False)
    elif board.is_full():
        result = handle_endgame(
            board, 'The game ended in draw.\n', ask_continue,
            '{t.bold}{t.yellow}' if pretty else False)
    else:
        result = True
    return result


# ======================================================================
def get_human_move(
        board,
        menu_choices,
        max_avail=6,
        show_menu=True,
        pretty=True):
    is_valid = False
    choice = None
    if max_avail:
        avail_moves = board.avail_moves()
        if hasattr(board, 'has_gravity'):
            max_avail = max_avail * 3
        too_many = len(board.avail_moves()) > max_avail
        msg('Available Moves: '
            + str(sorted(avail_moves)[:max_avail if too_many else None]) \
                [:-1 if too_many else None]
            + (', ...]' if too_many else ''),
            fmtt='{t.cyan}' if pretty else False)
    if show_menu:
        print(prettify('Menu: ' + ', '.join(
            [':'.join(['{o}' + k + '{x}', v])
             for k, v in menu_choices.items()]), pretty=pretty))
    while not is_valid:
        msg(' > ', end='', fmtt='{t.bold}' if pretty else False)
        choice = input().strip().lower()
        if choice in menu_choices:
            is_valid = True
        else:
            try:
                choice = ast.literal_eval(choice)
            except (SyntaxError, ValueError):
                pass
            if (isinstance(choice, int) and hasattr(board, 'has_gravity')) or (
                    isinstance(choice, tuple) and len(choice) == 2
                    and all(isinstance(move, int) for move in choice)
                    and not hasattr(board, 'has_gravity')):
                is_valid = \
                    board.is_valid_move(choice) and board.is_avail_move(choice)
            else:
                is_valid = False
        if not is_valid:
            msg('W: Invalid input. Must be a moveinate / menu choice.',
                fmtt=pretty)
    return choice


# ======================================================================
def mnk_game_cli(
        rows,
        cols,
        num_win,
        gravity,
        ai_mode,
        ai_timeout,
        computer_plays,
        pretty,
        verbose):
    ai_class = AI_MODES[ai_mode]['ai_class']
    ai_method = AI_MODES[ai_mode]['ai_method']
    board = make_board(rows, cols, num_win, gravity)
    undo_history = []
    redo_history = []
    filepath = 'mnkgame-saved.pickle'
    choice = 'n'
    continue_game = True
    first_computer_plays = computer_plays
    while continue_game:
        if choice not in {None, 's'}:
            print('\n' + colorized_board(board, pretty), sep='')
        if computer_plays:
            choice = ai_class().get_best_move(
                board, ai_timeout, ai_method, max_depth=-1,
                verbose=verbose >= D_VERB_LVL)
        else:
            menu_choices = dict(
                q='quit', n='new game', l='load game', s='save game',
                u='undo', r='redo', w='switch sides', h='hint')
            if choice is not None:
                choice = get_human_move(
                    board, menu_choices, pretty=pretty)
            else:
                choice = get_human_move(
                    board, menu_choices, 0, False, pretty=pretty)
            if choice == 'q':
                break
            elif choice == 'n':
                msg('I: New game started!', fmtt=pretty)
                first_computer_plays = not first_computer_plays
                computer_plays = first_computer_plays
                board.reset()
            elif choice == 'l':
                data = pickle.load(open(filepath, 'rb'))
                undo_history = data.pop('undo_history')
                redo_history = data.pop('redo_history')
                computer_plays = data.pop('computer_plays')
                board = make_board(**data)
                board.do_moves(undo_history)
                board.undo_moves(redo_history)
                msg('Load data from: `{}`'.format(filepath))
            elif choice == 's':
                data = dict(
                    rows=board.rows, cols=board.cols,
                    num_win=board.num_win, gravity=board.gravity,
                    undo_history=undo_history, redo_history=redo_history,
                    computer_plays=computer_plays)
                pickle.dump(data, open(filepath, 'wb+'))
                msg('Save data to: `{}`'.format(filepath))
            elif choice == 'u':
                if undo_history:
                    move = undo_history.pop()
                    redo_history.append(move)
                    board.undo_move(move)
                else:
                    msg('W: No moves to undo!')
            elif choice == 'r':
                if redo_history:
                    move = redo_history.pop()
                    undo_history.append(move)
                    board.do_move(move)
                else:
                    msg('W: No moves to redo!')
            elif choice == 'w':
                msg('I: switching sides (computer plays)!', fmtt=pretty)
            elif choice == 'h':
                move = ai_class().get_best_move(
                    board, ai_timeout, ai_method, max_depth=-1,
                    verbose=True)
                msg('I: Best move for computer: ' + str(move), fmtt=pretty)
                choice = None
        if not isinstance(choice, str) or choice not in 'lsur':
            continue_game = handle_move(
                board, choice, computer_plays, undo_history, redo_history,
                True, pretty)
            computer_plays = not computer_plays
