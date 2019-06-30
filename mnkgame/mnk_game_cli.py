#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees

from mnkgame import D_VERB_LVL
from mnkgame import msg


# ======================================================================
def handle_endgame(
        board,
        text,
        ask,
        fmt):
    result = True
    print('\n' + str(board), sep='')
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
def get_human_move(board):
    is_valid = False
    coord = None
    msg('Available Moves: ' + str(sorted(board.avail_moves())), fmt='{t.cyan}')
    while not is_valid:
        try:
            msg('What is your move (q|Q to quit)? ', end='', fmt='{t.bold}')
            choice = input().strip().lower()
            if choice == 'q':
                quit()
            coord = ast.literal_eval(choice)
            is_valid = \
                board.is_valid_move(coord) and board.is_avail_move(coord)
        except (TypeError, SyntaxError, ValueError):
            pass
    return coord


# ======================================================================
def mnk_game_cli(
        board,
        game_ai_class,
        method,
        ai_time_limit,
        computer_plays,
        verbose):
    continue_game = True
    while continue_game:
        print('\n' + str(board), sep='')
        if computer_plays:
            coord = game_ai_class().get_best_move(
                board, ai_time_limit, method, max_depth=-1,
                verbose=verbose >= D_VERB_LVL)
        else:
            coord = get_human_move(board)
        continue_game = handle_move(board, coord, computer_plays)
        computer_plays = not computer_plays
