#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlyingCircus - Everything you always wanted to have in Python.*
"""

# Copyright (c) Riccardo Metere <rick@metere.it>

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

# ======================================================================
# :: Python Standard Library Imports
import itertools  # Functions creating iterators for efficient looping
import os  # Miscellaneous operating system interfaces
import sys  # System-specific parameters and functions
import re  # Regular expression operations
import appdirs  # Determine appropriate platform-specific dirs
import pkg_resources  # Manage package resource (from setuptools module)

# ======================================================================
# :: External Imports

# ======================================================================
# :: Version
from mnkgame._version import __version__

# ======================================================================
# :: Project Details
INFO = {
    'name': 'mnkgame',
    'author': 'Riccardo Metere <rick@metere.it>',
    'contrib': (
        'Riccardo Metere <rick@metere.it>',
    ),
    'copyright': 'Copyright (C) 2019',
    'license': 'GNU General Public License version 3 or later (GPLv3+)',
    'notice':
        """
This program is free software and it comes with ABSOLUTELY NO WARRANTY.
It is covered by the GNU General Public License version 3 (GPLv3+).
You are welcome to redistribute it under its terms and conditions.
        """,
    'version': __version__
}

# ======================================================================
# :: Supported Verbosity Levels
VERB_LVL_NAMES = (
    'none', 'lowest', 'lower', 'low', 'medium', 'high', 'higher', 'highest',
    'warning', 'debug')
VERB_LVL = {k: v for v, k in enumerate(VERB_LVL_NAMES)}
D_VERB_LVL = VERB_LVL['lowest']

# ======================================================================
# : Colored terminal
# if blessed/blessings is not present, no coloring
try:
    from blessed import Terminal
except ImportError:
    try:
        from blessed import Terminal
    except ImportError:
        Terminal = None

IS_TTY = not os.isatty(sys.stdout.fileno())

# ======================================================================
# Greetings and Logos
# MY_GREETINGS = r"""
#                  _
#  _ __ ___  _ __ | | __      __ _  __ _ _ __ ___   ___
# | '_ ` _ \| '_ \| |/ /____ / _` |/ _` | '_ ` _ \ / _ \
# | | | | | | | | |   <_____| (_| | (_| | | | | | |  __/
# |_| |_| |_|_| |_|_|\_\     \__, |\__,_|_| |_| |_|\___|
#                            |___/
# """
#
# # generated with: figlet 'mnk-game' -f standard
#
# MY_LOGO = r"""
#           _
#   __  __ | |   ___
#   \ \/ / | |  / _ \
#    )  (  | | | (_) |
#   /_/\_\ | |  \___/
#   _______| |_______
#  |_______   _______|
#    ___   | | __  __
#   / _ \  | | \ \/ /
#  | (_) | | |  )  (
#   \___/  | | /_/\_\
#          |_|
# """
#
# MY_LOGO_SMALL = r"""
#  \/ | /\
#  /\ | \/
# ----+----
#  /\ | \/
#  \/ | /\
# """
#
# MY_LOGO_TINY = r"""
# X|O
# -+-
# O|X
# """

MY_GREETINGS = r"""
{o}                 _                                    {x}
{o} _ __ ___  _ __ | | __      __ _  __ _ _ __ ___   ___ {x}
{o}| '_ ` _ \| '_ \| |/ /____ / _` |/ _` | '_ ` _ \ / _ \{x}
{o}| | | | | | | | |   <_____| (_| | (_| | | | | | |  __/{x}
{o}|_| |_| |_|_| |_|_|\_\     \__, |\__,_|_| |_| |_|\___|{x}
{o}                           |___/                      {x}
"""

MY_LOGO = r"""
          {o}_{x}         
  {o}{B}__  __{x} {o}| |{x} {o}{R}  ___  {x}
  {o}{B}\ \/ /{x} {o}| |{x} {o}{R} / _ \ {x}
  {o}{B} )  ( {x} {o}| |{x} {o}{R}| (_) |{x}
  {o}{B}/_/\_\{x} {o}| |{x} {o}{R} \___/ {x}
 {o} _______| |_______ {x}
 {o}|_______   _______|{x}
 {o}{R}  ___  {x} {o}| |{x} {o}{B}__  __{x} 
 {o}{R} / _ \ {x} {o}| |{x} {o}{B}\ \/ /{x} 
 {o}{R}| (_) |{x} {o}| |{x} {o}{B} )  ( {x} 
 {o}{R} \___/ {x} {o}| |{x} {o}{B}/_/\_\{x} 
         {o}|_|{x}        
"""

MY_LOGO_SMALL = r"""
 {o}{B}\_/{x} {o}|{x} {o}{R}/"\{x} 
 {o}{B}/ \{x} {o}|{x} {o}{R}\_/{x} 
{o}-----+-----{x}
 {o}{R}/"\{x} {o}|{x} {o}{B}\_/{x} 
 {o}{R}\_/{x} {o}|{x} {o}{B}/ \{x} 
"""

MY_LOGO_TINY = r"""
{o}{B}X{x}{o}|{x}{o}{R}O{x}
{o}-+-{x}
{o}{R}O{x}{o}|{x}{o}{B}X{x}
"""


# :: Causes the greetings to be printed any time the library is loaded.
# print(MY_GREETINGS)

# ======================================================================


def do_nothing_decorator(*_args, **_kws):
    """
    Callable decorator that does nothing.

    Arguments are catched, but ignored.
    This is very useful to provide proxy for decorators that may not be
    defined.

    Args:
        *_args: Positional arguments.
        **_kws: Keyword arguments.

    Returns:
        result (callable): The unmodified callable.
    """

    def wrapper(f):
        return f

    if len(_args) > 0 and not callable(_args[0]) or len(_kws) > 0:
        return wrapper
    elif len(_args) == 0:
        return wrapper
    else:
        return _args[0]


# ======================================================================
# Numba import
try:
    from numba import jit
except ImportError:
    HAS_JIT = False
    jit = do_nothing_decorator
else:
    HAS_JIT = True


# ======================================================================
def msg(
        text,
        verb_lvl=D_VERB_LVL,
        verb_threshold=D_VERB_LVL,
        fmtt=True,
        *_args,
        **_kws):
    """
    Display a feedback message to the standard output.

    Args:
        text (str|Any): Message to display or object with `__str__`.
        verb_lvl (int): Current level of verbosity.
        verb_threshold (int): Threshold level of verbosity.
        fmtt (str|bool|None): Format of the message (if `blessed` supported).
            If True, a standard formatting is used.
            If False, empty string or None, no formatting is applied.
            If str, the specified formatting is used.
            This must be in the form of `{t.NAME}` where `NAME` refer to
            a formatting supported by `Terminal()` from `blessed`/`blessings`.
        *_args: Positional arguments for `print()`.
        **_kws: Keyword arguments for `print()`.

    Returns:
        None.

    Examples:
        >>> s = 'Hello World!'
        >>> msg(s)
        Hello World!
        >>> msg(s, VERB_LVL['medium'], VERB_LVL['low'])
        Hello World!
        >>> msg(s, VERB_LVL['low'], VERB_LVL['medium'])  # no output
        >>> msg(s, fmtt='{t.green}')  # if ANSI Terminal, green text
        Hello World!
        >>> msg('   :  a b c', fmtt='{t.red}{}')  # if ANSI Terminal, red text
           :  a b c
        >>> msg(' : a b c', fmtt='cyan')  # if ANSI Terminal, cyan text
         : a b c
    """
    if verb_lvl >= verb_threshold and text is not None:
        # if blessed/blessings is not present, no coloring
        try:
            from blessed import Terminal
        except ImportError:
            try:
                from blessings import Terminal
            except ImportError:
                Terminal = False

        t = Terminal() if callable(Terminal) else None
        if t is not None and fmtt:
            text = str(text)
            if fmtt is True:
                if VERB_LVL['low'] < verb_threshold <= VERB_LVL['medium']:
                    e = t.cyan
                elif VERB_LVL['medium'] < verb_threshold < VERB_LVL['debug']:
                    e = t.magenta
                elif verb_threshold >= VERB_LVL['debug']:
                    e = t.blue
                elif text.startswith('I:'):
                    e = t.green
                elif text.startswith('W:'):
                    e = t.yellow
                elif text.startswith('E:'):
                    e = t.red
                else:
                    e = t.white
                # first non-whitespace word
                txt1 = text.split(None, 1)[0] if len(text.strip()) > 0 else ''
                # initial whitespaces
                n = text.find(txt1)
                txt0 = text[:n]
                # rest
                txt2 = text[n + len(txt1):]
                txt_kws = dict(
                    e1=e + (t.bold if e == t.white else ''),
                    e2=e + (t.bold if e != t.white else ''),
                    t0=txt0, t1=txt1, t2=txt2, n=t.normal)
                text = '{t0}{e1}{t1}{n}{e2}{t2}{n}'.format_map(txt_kws)
            else:
                if 't.' not in fmtt:
                    fmtt = '{{t.{}}}'.format(fmtt)
                if '{}' not in fmtt:
                    fmtt += '{}'
                text = fmtt.format(text, t=t) + t.normal
        print(text, *_args, **_kws)


# ======================================================================
def pkg_paths(
        current_filepath=__file__,
        name=INFO['name'],
        author=INFO['author'],
        version=INFO['version']):
    """
    Generate application directories.

    Args:
        current_filepath (str): The current filepath.
        name (str): Application name.
        author (str): Application author.
        version (str): Application version.

    Returns:
        dirs (dict): The package directories.
            - 'config': directory for configuration files.
            - 'cache': directory for caching files.
            - 'data': directory for data files.
            - 'log': directory for log files.
            - 'base': base directory of the module.
            - 'resources': directory for the data resources.

    Examples:
        >>> sorted(pkg_paths().keys())
        ['base', 'cache', 'config', 'data', 'log', 'resources']
    """
    dirpaths = dict((
        # todo: fix for pyinstaller
        ('config', appdirs.user_config_dir(name, author, version)),
        ('cache', appdirs.user_cache_dir(name, author, version)),
        ('data', appdirs.user_data_dir(name, author, version)),
        ('log', appdirs.user_data_dir(name, author, version)),
    ))
    for name, dirpath in dirpaths.items():
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
    dirpaths['base'] = os.path.dirname(current_filepath)
    dirpaths['resources'] = os.path.join(dirpaths['base'], 'resources')
    return dirpaths


# ======================================================================
def blessify(
        text,
        pretty=False):
    """
    Preprocess text to be used with `blessed` / `blessings`.

    Args:
        text (str): The input text.
        pretty (bool): Use terminal effects (if available).

    Returns:
        text (str): The output text.
    """
    substs = dict(
        o='bold', v='reverse', x='normal',
        K='black', R='red', G='green', Y='yellow', B='blue', M='magenta',
        C='cyan', W='white')
    if pretty:
        for key, val in substs.items():
            text = text.replace('{' + key + '}', '{t.' + val + '}')
    else:
        for key in substs.keys():
            text = text.replace('{' + key + '}', '')
    return text


# ======================================================================
def prettify(text, pretty=False):
    """
    Apply terminal effects.

    Args:
        text (str): The input text.
        pretty (bool): Use terminal effects (if available).

    Returns:
        text (str): The output text.
    """
    t = Terminal() if callable(Terminal) else None

    if t is not None and pretty:
        text = blessify(text, True).format(t=t)
    else:
        text = blessify(text, False)
    return text


# ======================================================================
def print_logo(
        size='normal',
        pretty=IS_TTY,
        **_kws):
    """
    Print the standard logo.

    Args:
        size (str): The size of the logo.
            Possible values are: 'normal', 'small', 'tiny'.
            Other values are coerced to 'normal'.
        pretty (bool): Use terminal effects (if available).
        **_kws: Keyword arguments for `print()`.

    Returns:
        None.
    """
    if size.lower() not in {'small', 'tiny'}:
        size = ''
    the_size = ('_' + size.upper()) if size else ''
    text = blessify(globals()['MY_LOGO' + the_size], pretty=pretty)
    print(prettify(text, pretty))


# ======================================================================
def print_greetings(
        mode='inline',
        pretty=IS_TTY,
        **_kws):
    """
    Print the standard greeting.

    Args:
        mode (str): Define the greetings mode.
            Possible values are: 'normal', 'small', 'tiny', 'inline'.
            If 'inline', prints the logo and the greetings side by side.
            Otherwise, prints the logo (with corresponding size) followed by
            the greetings.
        pretty (bool): Use terminal effects (if available).
        **_kws: Keyword arguments for `print()`.

    Returns:
        None.
    """
    if mode.lower() == 'inline':
        logo_width = max(len(s) for s in blessify(MY_LOGO_SMALL).splitlines())
        text_logo = '\n' + ' ' * logo_width + '\n' + MY_LOGO_SMALL[1:]
        text = ''
        for line_logo, line_greetings in \
                itertools.zip_longest(
                    text_logo[1:].splitlines(), MY_GREETINGS[1:].splitlines()):
            text += '  '.join([line_logo, line_greetings]) + '\n'
        print(prettify(text, pretty))
    else:
        print_logo(mode, pretty, end='')
        if mode != 'tiny':
            print(prettify(MY_GREETINGS[1:], pretty))
        else:
            print(prettify('{o}{x}', pretty))


# ======================================================================
PATH = pkg_paths(__file__, INFO['name'], INFO['author'], INFO['version'])

# ======================================================================
if __name__ == '__main__':
    import doctest  # Test interactive Python examples

    msg(__doc__.strip())
    msg('Running `doctest.testmod()`... ', fmtt='{t.bold}')
    results = doctest.testmod()  # RUN TESTS HERE!
    results_ok = results.attempted - results.failed
    results_fmt = '{t.bold}{t.red}' \
        if results.failed > 0 else '{t.bold}{t.green}'
    msg('Tests = {results.attempted}; '.format_map(vars()),
        fmtt='{t.bold}{t.cyan}', end='')
    msg('OK = {results_ok}; '.format_map(vars()),
        fmtt='{t.bold}{t.green}', end='')
    msg('Fail = {results.failed}'.format_map(vars()), fmtt=results_fmt)
