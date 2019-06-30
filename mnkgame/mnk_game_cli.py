#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees

from mnkgame import colorize
from mnkgame import D_VERB_LVL
from mnkgame import msg


# ======================================================================
def colorized_board(board, pieces=True, grid=True):
    text = str(board)
    substs = dict()
    if pieces:
        substs.update({'X': '{o}{B}X{x}', 'O': '{o}{R}O{x}'})
    if board:
        substs.update({x: '{o}' + x + '{x}' for x in ('|', '+', '-')})
    for key, val in substs.items():
        text = text.replace(key, val)
    return colorize(text)


# ======================================================================
def handle_endgame(
        board,
        text,
        ask,
        fmt):
    result = True
    print('\n' + colorized_board(board), sep='')
    board.reset()
    msg(text, fmt=fmt)
    if ask:
        msg('Play a new game ([Y]/n)? ', end='', fmt='{t.bold}')
        choice = input()
        if choice.strip().lower() == 'n':
            result = False
    return result


# ======================================================================
def handle_move(
        board,
        coord,
        is_computer,
        ask_continue=True):
    if is_computer:
        msg('Computer Move is: ' + str(coord), fmt='{t.magenta}')
    board.do_move(coord)
    if board.winner(board.turn) == board.turn:
        result = handle_endgame(
            board,
            'YOU LOST!\n' if is_computer else 'Congratulations! You WIN!\n',
            ask_continue,
            '{t.bold}{t.red}' if is_computer else '{t.bold}{t.green}')
    elif board.is_full():
        result = handle_endgame(
            board, 'The game ended in draw.\n', ask_continue,
            '{t.bold}{t.yellow}')
    else:
        result = True
    return result


# ======================================================================
def get_human_move(board, menu_choices, max_avail=6, show_menu=True):
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
            + (', ...]' if too_many else ''), fmt='{t.cyan}')
    while not is_valid:
        try:
            if show_menu:
                print(colorize('Menu: ' + ', '.join(
                    [':'.join(['{o}' + k + '{x}', v])
                     for k, v in menu_choices.items()])))
            msg(' > ', end='', fmt='{t.bold}')
            choice = input().strip().lower()
            if choice in menu_choices:
                is_valid = True
            else:
                choice = ast.literal_eval(choice)
                is_valid = \
                    board.is_valid_move(choice) and board.is_avail_move(choice)
        except (TypeError, SyntaxError, ValueError):
            pass
    return choice


# ======================================================================
def mnk_game_cli(
        board,
        game_ai_class,
        method,
        ai_time_limit,
        computer_plays,
        verbose):
    choice = 'n'
    continue_game = True
    first_computer_plays = computer_plays
    while continue_game:
        if choice is not None:
            print('\n' + colorized_board(board), sep='')
        if computer_plays:
            choice = game_ai_class().get_best_move(
                board, ai_time_limit, method, max_depth=-1,
                verbose=verbose >= D_VERB_LVL)
        else:
            menu_choices = dict(
                q='quit', n='new game', s='switch sides', h='hint')
            if choice is not None:
                choice = get_human_move(board, menu_choices)
            else:
                choice = get_human_move(board, menu_choices, 0, False)
            if choice == 'q':
                quit()
            elif choice == 'n':
                msg('I: New game started!')
                first_computer_plays = not first_computer_plays
                computer_plays = first_computer_plays
                board.reset()
            elif choice == 's':
                msg('I: switching sides (computer plays)!')
            elif choice == 'h':
                coord = game_ai_class().get_best_move(
                    board, ai_time_limit, method, max_depth=-1,
                    verbose=True)
                msg('I: Best move for computer: ' + str(coord))
                choice = None
        if choice is not None:
            continue_game = handle_move(board, choice, computer_plays)
            computer_plays = not computer_plays
