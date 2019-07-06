#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PIECE_X = {
    '1x1': r"""
X
""",
    '2x3': r"""
\_/
/ \
""",
    '4x6': r"""
__  __
\ \/ /
 )  ( 
/_/\_\
""",
    '5x7': r"""
__   __
\ \ / /
 \ ' / 
 / . \ 
/_/ \_\
"""}

PIECE_O = {
    '1x1': r"""
O
""",
    '2x3': r"""
/"\
\_/
""",
    '4x6': r"""
  ___  
 / _ \ 
| (_) |
 \___/ 
""",
    '5x7': r"""
  ____
 / __ \
| /  \ |
| \__/ |
 \____/
"""}

PIECES = dict(
    x={k: v[1:-1] for k, v in PIECE_X.items()},
    o={k: v[1:-1] for k, v in PIECE_O.items()})


import prompt_toolkit as pt
import prompt_toolkit.key_binding
import prompt_toolkit.buffer
import prompt_toolkit.layout

# ======================================================================
kb = pt.key_binding.KeyBindings()


# ======================================================================
@kb.add('c-q')
def exit_(event): event.app.exit()


# ======================================================================
def mnk_game_tui(
        board,
        game_ai_class,
        method,
        ai_timeout,
        computer_plays,
        verbose):
    buffer1 = pt.buffer.Buffer()  # Editable buffer.

    root_container = pt.layout.containers.VSplit([
        # One window that holds the BufferControl with the default buffer on
        # the left.
        pt.layout.containers.Window(
            content=pt.layout.controls.BufferControl(buffer=buffer1)),

        # A vertical line in the middle. We explicitly specify the width, to
        # make sure that the layout engine will not try to divide the whole
        # width by three for all these windows. The window will simply fill its
        # content by repeating this character.
        pt.layout.containers.Window(width=20, height=10, char='|'),

        # Display the text 'Hello world' on the right.
        pt.layout.containers.Window(
            content=pt.layout.controls.FormattedTextControl(
                text='<b>Hello</b> world')),
    ])

    lo = pt.layout.layout.Layout(root_container)

    app = pt.Application(
        layout=lo, key_bindings=kb, full_screen=False)
    app.run()


# ======================================================================
if __name__ == '__main__':
    from mnkgame.mnk_game import main

    main()
