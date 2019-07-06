#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees

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
        fmt):
    result = True
    print('\n' + colorized_board(board, bool(fmt)), sep='')
    board.reset()
    msg(text, fmt=fmt)
    if ask:
        msg('Play a new game ([Y]/n)? ', end='',
            fmt='{t.bold}' if bool(fmt) else False)
        choice = input()
        if choice.strip().lower() == 'n':
            result = False
    return result


# ======================================================================
def handle_move(
        board,
        coord,
        is_computer,
        ask_continue=True,
        pretty=True):
    if is_computer:
        msg('Computer Move is: ' + str(coord),
            fmt='{t.magenta}' if pretty else False)
    board.do_move(coord)
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
            fmt='{t.cyan}' if pretty else False)
    if show_menu:
        print(prettify('Menu: ' + ', '.join(
            [':'.join(['{o}' + k + '{x}', v])
             for k, v in menu_choices.items()]), pretty=pretty))
    while not is_valid:
        msg(' > ', end='', fmt='{t.bold}' if pretty else False)
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
                    and all(isinstance(coord, int) for coord in choice)
                    and not hasattr(board, 'has_gravity')):
                is_valid = \
                    board.is_valid_move(choice) and board.is_avail_move(choice)
            else:
                is_valid = False
        if not is_valid:
            msg('W: Invalid input. Must be a coordinate / menu choice.',
                fmt=pretty)
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
    choice = 'n'
    continue_game = True
    first_computer_plays = computer_plays
    while continue_game:
        if choice not in {None, 's'}:
            print('\n' + colorized_board(board, pretty), sep='')
        if computer_plays:
            choice = ai_class().get_best_move(
                board, ai_timeout, method, max_depth=-1,
                verbose=verbose >= D_VERB_LVL)
        else:
            menu_choices = dict(
                q='quit', n='new game', s='switch sides', h='hint')
            if choice is not None:
                choice = get_human_move(
                    board, menu_choices, pretty=pretty)
            else:
                choice = get_human_move(
                    board, menu_choices, 0, False, pretty=pretty)
            if choice == 'q':
                break
            elif choice == 'n':
                msg('I: New game started!', fmt=pretty)
                first_computer_plays = not first_computer_plays
                computer_plays = first_computer_plays
                board.reset()
            elif choice == 's':
                msg('I: switching sides (computer plays)!', fmt=pretty)
            elif choice == 'h':
                coord = ai_class().get_best_move(
                    board, ai_timeout, method, max_depth=-1,
                    verbose=True)
                msg('I: Best move for computer: ' + str(coord), fmt=pretty)
                choice = None
        if choice is not None:
            continue_game = handle_move(
                board, choice, computer_plays, True, pretty)
            computer_plays = not computer_plays
