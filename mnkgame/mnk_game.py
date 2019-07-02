#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(m,n,k)-game: command-line interface.
"""

# ======================================================================
# :: Future Imports (including `future` PyPI package, if available)
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

try:
    from builtins import (
        bytes, dict, int, list, object, range, str, ascii, chr, hex,
        input, next, oct, open, pow, round, super, filter, map, zip)
except ImportError:
    pass

# ======================================================================
# :: Python Standard Library Imports
import datetime  # Basic date and time types
import argparse  # Parser for command-line options, arguments and subcommands
import importlib  # The implementation of `import`

# :: External Imports

# :: External Imports Submodules

# :: Internal Imports
from mnkgame import print_greetings
from mnkgame import INFO
from mnkgame import VERB_LVL, D_VERB_LVL
from mnkgame import msg

from mnkgame.GameAiSearchTree import GameAiSearchTree

# ======================================================================
AI_MODES = (
    # 'alphabeta_jit',
    'alphabeta',
    'negamax',
    # 'pvs',
    # 'alphabeta_hashing',
    'random')
USER_INTERFACES = (
    'auto',
    # 'gui',
    # 'tui',
    'cli')


# ======================================================================
def prepare_game(
        rows,
        cols,
        aligned,
        gravity,
        ai_mode,
        **_kws):
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
        method = None
    return board, game_ai_class, method


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{} - {}\n{}'.format(
            INFO['version'], INFO['author'], INFO['license']),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version='%(prog)s - ver. {}\n{}\n{} {}\n{}'.format(
            INFO['version'],
            next(line for line in __doc__.splitlines() if line),
            INFO['copyright'], INFO['author'], INFO['notice']),
        action='version')
    arg_parser.add_argument(
        '-v', '--verbose',
        action='count', default=D_VERB_LVL,
        help='increase the level of verbosity [%(default)s]')
    arg_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='override verbosity settings to suppress output [%(default)s]')
    # :: Add additional arguments
    arg_parser.add_argument(
        'ui', metavar='USER_INTERFACE',
        nargs='?', choices=USER_INTERFACES,
        type=str, default=USER_INTERFACES[0],
        help='select the user interfact [%(default)s|(%(choices)s)]')
    arg_parser.add_argument(
        '-m', '--rows', metavar='N',
        type=int, default=3,
        help='number of rows for the board [%(default)s]')
    arg_parser.add_argument(
        '-n', '--cols', metavar='N',
        type=int, default=3,
        help='number of cols for the board [%(default)s]')
    arg_parser.add_argument(
        '-k', '--aligned', metavar='N',
        type=int, default=3,
        help='number of aligned pieces required for winning [%(default)s]')
    arg_parser.add_argument(
        '-g', '--gravity',
        action='store_true',
        help='use gravitataion-rule variant [%(default)s]')
    arg_parser.add_argument(
        '-a', '--ai_mode', metavar='MODE',
        choices=AI_MODES, type=str, default=AI_MODES[0],
        help='AI mode [%(default)s|(%(choices)s)]')
    arg_parser.add_argument(
        '-t', '--ai_time_limit', metavar='X',
        type=float, default=4.0,
        help='time limit for AI move in sec [%(default)s]')
    arg_parser.add_argument(
        '-c', '--computer_plays',
        action='store_true',
        help='computer plays first move of first game [%(default)s]')
    arg_parser.add_argument(
        '-u', '--ugly',
        action='store_true',
        help='do not use terminal formatting [%(default)s]')
    return arg_parser


# ======================================================================
def main():
    begin_time = datetime.datetime.now()

    # :: handle program parameters
    arg_parser = handle_arg()
    args = arg_parser.parse_args()
    # fix verbosity in case of 'quiet'
    if args.quiet:
        args.verbose = VERB_LVL['none']
    # print greetings
    print_greetings('inline', not args.ugly)
    # print help info
    if args.verbose >= VERB_LVL['debug']:
        arg_parser.print_help()
    msg('\nARGS: ' + str(vars(args)), args.verbose, VERB_LVL['debug'],
        fmt=not args.ugly)
    msg(__doc__.strip(), args.verbose, VERB_LVL['lower'],
        fmt=not args.ugly)

    kws = vars(args)
    kws.pop('quiet')

    if args.verbose >= D_VERB_LVL:
        msg('I: m={rows} (rows),  n={cols} (cols),  k={aligned} (aligned),'
            '  g={gravity} (gravity)\n   ai_mode={ai_mode}'.format(**kws),
            fmt=not args.ugly)
    ui_args = prepare_game(**kws)
    kws['pretty'] = not args.ugly
    for k in ('rows', 'cols', 'aligned', 'gravity', 'ai_mode', 'ugly'):
        kws.pop(k)


    ui = kws.pop('ui')
    if ui == 'auto':
        ui = 'cli'
    if ui in USER_INTERFACES[1:]:
        ui_module_name = ui_name = 'mnk_game_' + ui
        ui_module = importlib.import_module('mnkgame.' + ui_module_name)
        mnk_game_ui = getattr(ui_module, ui_name)
        mnk_game_ui(*ui_args, **kws)

    exec_time = datetime.datetime.now() - begin_time
    msg('ExecTime: {}'.format(exec_time), args.verbose, VERB_LVL['debug'],
        fmt=kws['pretty'])


# ======================================================================
if __name__ == '__main__':
    main()
