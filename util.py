#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
# :: Version
__version__ = '0.0.0.4'

# ======================================================================
# :: Script details
INFO = {
    'name': 'Auto m3u',
    'author': 'Riccardo Metere <rick@metere.it>',
    'copyright': 'Copyright (C) 2018-2019',
    'license': 'License: GNU General Public License version 3 (GPLv3)',
    'notice':
        """
This program is free software and it comes with ABSOLUTELY NO WARRANTY.
It is covered by the GNU General Public License version 3 (GPLv3).
You are welcome to redistribute it under its terms and conditions.
        """,
    'version': __version__
}

# ======================================================================
# :: supported verbosity levels
VERB_LVL_NAMES = (
    'none', 'lowest', 'lower', 'low', 'medium', 'high', 'higher', 'highest',
    'warning', 'debug')
VERB_LVL = dict(zip(VERB_LVL_NAMES, range(len(VERB_LVL_NAMES))))
D_VERB_LVL = VERB_LVL['lowest']


# ======================================================================
def msg(
        text,
        verb_lvl=D_VERB_LVL,
        verb_threshold=D_VERB_LVL,
        fmt=None,
        *_args,
        **_kws):
    """
    Display a feedback message to the standard output.

    Args:
        text (str|Any): Message to display or object with `__repr__`.
        verb_lvl (int): Current level of verbosity.
        verb_threshold (int): Threshold level of verbosity.
        fmt (str): Format of the message (if `blessed` supported).
            If None, a standard formatting is used.
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
        >>> msg(s, fmt='{t.green}')  # if ANSI Terminal, green text
        Hello World!
        >>> msg('   :  a b c', fmt='{t.red}{}')  # if ANSI Terminal, red text
           :  a b c
        >>> msg(' : a b c', fmt='cyan')  # if ANSI Terminal, cyan text
         : a b c
    """
    if verb_lvl >= verb_threshold and text is not None:
        # if blessed/blessings is not present, no coloring
        try:
            import blessed
        except ImportError:
            try:
                import blessings as blessed
            except ImportError:
                blessed = None

        try:
            t = blessed.Terminal()
        except (ValueError, AttributeError):
            t = None

        if blessed and t:
            text = str(text)
            if not fmt:
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
                txt1 = text.split(None, 1)[0] if len(text) > 0 else ''
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
                if 't.' not in fmt:
                    fmt = '{{t.{}}}'.format(fmt)
                if '{}' not in fmt:
                    fmt += '{}'
                text = fmt.format(text, t=t) + t.normal
        print(text, *_args, **_kws)


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
