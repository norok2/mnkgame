#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees

from util import VERB_LVL_NAMES, VERB_LVL, D_VERB_LVL
from util import msg

from Board import Board
from BoardGravity import BoardGravity
from GameAiRandom import GameAiRandom
from GameAiSearchTree import GameAiSearchTree


# ======================================================================
def handle_endgame(
        board,
        text,
        ask):
    result = True
    msg('\n' + str(board), sep='')
    board.reset()
    msg(text)
    if ask:
        choice = input('Play a new game ([Y]/n)? ')
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
        msg('Computer Move is: ' + str(coord))
    board.do_move(coord)
    if board.winner(board.turn) == board.turn:
        result = handle_endgame(
            board,
            'YOU LOST!\n' if is_computer else 'Congratulations! You WIN!\n',
            ask_continue)
    elif board.is_full():
        result = handle_endgame(
            board, 'The game ended in draw.\n', ask_continue)
    else:
        result = True
    return result


# ======================================================================
def get_human_move(board):
    is_valid = False
    coord = None
    msg('Available Moves: ' + str(sorted(board.avail_moves())))
    while not is_valid:
        try:
            typed = input('What is your move (q|Q to quit)? ').strip()
            if typed.lower() == 'q':
                quit()
            coord = ast.literal_eval(typed)
            is_valid = \
                board.is_valid_move(coord) and board.is_avail_move(coord)
        except (TypeError, SyntaxError, ValueError):
            pass
    return coord


# ======================================================================
def mnk_game_gui(
        board,
        game_ai_class,
        method,
        ai_time_limit,
        computer_plays,
        verbose):
    continue_game = True
    while continue_game:
        msg('\n' + str(board), sep='')
        if computer_plays:
            coord = game_ai_class().get_best_move(
                board, ai_time_limit, method, max_depth=-1,
                verbose=verbose >= D_VERB_LVL)
        else:
            coord = get_human_move(board)
        continue_game = handle_move(board, coord, computer_plays)
        computer_plays = not computer_plays
