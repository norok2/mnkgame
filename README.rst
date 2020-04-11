(m,n,k)-Game
============

**mnkgame** - Library and user interfaces for (m,n,k)+g?-games.


Overview
--------

This software provides a library and user interfaces for `(m,n,k)-games <https://en.wikipedia.org/wiki/M,n,k-game>`__, including optional *gravity* and simple search-tree algorithms.

The **(m,n,k)-game** family of games are played in a rectangular grid of size ``m x n`` (where *m* is the number of rows and *n* is the number of columns).
Each player position a piece (typically **X** and **O**) on the grid in alternating turns until one of the player manages to align *k* pieces either horizontally, vertically or diagonally.
The first player to achieve this wins the game.

A variant of this game, called **gravity**, is when the pieces cannot be put anywhere in the grid but must *fall* toward the lower horizontal edge of the grid, so that each piece must be placed either at such edge or on top of another piece.


Popular such games are:

 - (m=3, n=3, k=3): `tic-tac-toe <https://en.wikipedia.org/wiki/tic-tac-toe>`__
 - (m=15, n=15, k=5): `gomoku <https://en.wikipedia.org/wiki/gomoku>`__
 - (m=6, n=7, k=4, gravity): `connect4 <https://en.wikipedia.org/wiki/connect_four>`__

The following user interfaces are provided:

 - a Command-Line Interface (CLI) - with optional coloring from `blessed <https://pypi.python.org/pypi/blessed>`__ / `blessings <https://pypi.python.org/pypi/blessings>`__.
 - a Text User Interface (TUI) - planned to be implemented with `asciimatics <https://pypi.python.org/pypi/asciimatics>`__.
 - a Graphical User Interface (GUI) - implemented with `tkinter <https://docs.python.org/3/library/tkinter.html>`__.

For a more comprehensive list of changes see ``CHANGELOG.rst`` (automatically
generated from the version control system).


Quick Start
-----------

Once installed on a properly set-up system, running the software is as simple as typing:

.. code:: bash

    $ mnk-game

which will default to the best user interface (UI) the system can handle.

To specify a certain UI, just use the first positional argument, e.g. for the CLI:

.. code:: bash

    $ mnk-game cli


To get information on the command-line option, just type:

.. code:: bash

    $ mnk-game --help

which produces:

.. code::

    usage: mnk-game.py [-h] [--ver] [-v] [-q] [-m N] [-n N] [-k N] [-g] [-a MODE]
                       [-t X] [-c]
                       [USER_INTERFACE]

    (m,n,k)-game: command-line interface.

    positional arguments:
      USER_INTERFACE        select the user interfact [auto|(auto, gui, tui, cli)]

    optional arguments:
      -h, --help            show this help message and exit
      --ver, --version      show program's version number and exit
      -v, --verbose         increase the level of verbosity [1]
      -q, --quiet           override verbosity settings to suppress output [False]
      -m N, --rows N        number of rows for the board [3]
      -n N, --cols N        number of cols for the board [3]
      -k N, --aligned N     number of aligned pieces required for winning [3]
      -g, --gravity         use gravitataion-rule variant [False]
      -a MODE, --ai_mode MODE
                            AI mode [alphabeta_jit|(alphabeta_jit, alphabeta,
                            negamax, pvs, alphabeta_hashing, random)]
      -t X, --ai_time_limit X
                            time limit for AI move in sec [4.0]
      -c, --computer_plays  computer plays first move of first game [False]

    v.0.0.0.4 - Riccardo Metere <rick@metere.it>
    License: GNU General Public License version 3 (GPLv3)


Installation
------------

The recommended way of installing the software is through `PyPI <https://pypi.python.org/pypi/mnkgame>`__:

.. code:: bash

    $ pip install mnkgame

Alternatively, you can clone the source repository from `GitHub <https://github.com/norok2/mnkgame>`__:

.. code:: bash

    $ git clone git@github.com:norok2/mnkgame.git
    $ cd mnkgame
    $ pip install -e .


License
-------

This work is licensed through the terms and conditions of the `GPLv3+ <http://www.gnu.org/licenses/gpl-3.0.html>`__.
See the accompanying ``LICENSE.rst`` for more details.


Acknowledgements
----------------

This software is a spin-off of a Python course held in 2018 at the `Donders Institute <https://www.ru.nl/donders/>`__, part of the `Radboud University Nijmegen <https://www.ru.nl/en/>`__ (neither of which is involved or in any way affiliated with this).

