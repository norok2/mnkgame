#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast  # Abstract Syntax Trees
import prompt_toolkit as pt
import prompt_toolkit.key_binding
import prompt_toolkit.buffer
import prompt_toolkit.layout

from util import VERB_LVL_NAMES, VERB_LVL, D_VERB_LVL
from util import msg

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
        ai_time_limit,
        computer_plays,
        verbose):
    buffer1 = pt.buffer.Buffer()  # Editable buffer.

    root_container = pt.layout.containers.VSplit([
        # One window that holds the BufferControl with the default buffer on
        # the left.
        pt.layout.containers.Window(content=pt.layout.controls.BufferControl(buffer=buffer1)),

        # A vertical line in the middle. We explicitly specify the width, to
        # make sure that the layout engine will not try to divide the whole
        # width by three for all these windows. The window will simply fill its
        # content by repeating this character.
        pt.layout.containers.Window(width=20, height=10, char='|'),

        # Display the text 'Hello world' on the right.
        pt.layout.containers.Window(content=pt.layout.controls.FormattedTextControl(text='<b>Hello</b> world')),
    ])

    lo = pt.layout.layout.Layout(root_container)

    app = pt.Application(
        layout=lo, key_bindings=kb, full_screen=False)
    app.run()
