#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(m,n,k)-game: graphical user interface.
"""
import os
import multiprocessing
import collections
import json
import warnings

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font
    import tkinter.messagebox as messagebox
    import tkinter.filedialog as filedialog
    import tkinter.simpledialog as simpledialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkFont

    tk.font = tkFont

import numpy as np

from mnkgame import D_VERB_LVL, VERB_LVL, VERB_LVL_NAMES
from mnkgame import msg
from mnkgame import INFO, PATH
from mnkgame import print_greetings, prettify, MY_GREETINGS
from mnkgame.util import make_board, guess_alias
from mnkgame.util import AI_MODES, ALIASES, USER_INTERFACES

# ======================================================================
# :: determine initial configuration
try:
    import appdirs

    _app_dirs = appdirs.AppDirs(INFO['name'].lower(), INFO['author'])
    _PATHS = {
        'usr_cfg': _app_dirs.user_config_dir,
        'sys_cfg': _app_dirs.site_config_dir,
    }
except ImportError:
    _PATHS = {
        'usr_cfg': os.path.realpath('.'),
        'sys_cfg': os.path.dirname(__file__),
    }

CFG_FILENAME = 'config.json'
CFG_DIRPATHS = (
    _PATHS['usr_cfg'],
    os.path.realpath('.'),
    os.getenv('HOME'),
    os.path.dirname(__file__),
    _PATHS['sys_cfg'])


# ======================================================================
def default_config():
    cfg = dict(
        verbose=D_VERB_LVL,
        use_mp=False,
        num_processes=multiprocessing.cpu_count(),
        gui_style_tk='default',
        save_on_exit=True,
    )
    return cfg


# ======================================================================
def load_config(
        cfg_filepath=CFG_FILENAME):
    cfg = {}
    if os.path.exists(cfg_filepath):
        msg('Load configuration from `{}`.'.format(cfg_filepath))
        try:
            with open(cfg_filepath, 'r') as cfg_file:
                cfg = json.load(cfg_file)
        except json.JSONDecodeError:
            pass
    return cfg


# ======================================================================
def save_config(
        config,
        cfg_filepath=CFG_FILENAME):
    msg('Save configuration from `{}`.'.format(cfg_filepath))
    dirpath = os.path.dirname(cfg_filepath)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    with open(cfg_filepath, 'w') as cfg_file:
        json.dump(config, cfg_file, sort_keys=True, indent=4)


# ======================================================================
def has_decorator(
        text,
        pre_decor='"',
        post_decor='"'):
    """
    Determine if a string is delimited by some characters (decorators).

    Args:
        text (str): The text input string.
        pre_decor (str): initial string decorator.
        post_decor (str): final string decorator.

    Returns:
        has_decorator (bool): True if text is delimited by the specified chars.

    Examples:
        >>> has_decorator('"test"')
        True
        >>> has_decorator('"test')
        False
        >>> has_decorator('<test>', '<', '>')
        True
    """
    return text.startswith(pre_decor) and text.endswith(post_decor)


# ======================================================================
def strip_decorator(
        text,
        pre_decor='"',
        post_decor='"'):
    """
    Strip initial and final character sequences (decorators) from a string.

    Args:
        text (str): The text input string.
        pre_decor (str): initial string decorator.
        post_decor (str): final string decorator.

    Returns:
        text (str): the text without the specified decorators.

    Examples:
        >>> strip_decorator('"test"')
        'test'
        >>> strip_decorator('"test')
        'test'
        >>> strip_decorator('<test>', '<', '>')
        'test'
    """
    begin = len(pre_decor) if text.startswith(pre_decor) else None
    end = -len(post_decor) if text.endswith(post_decor) else None
    return text[begin:end]


# ======================================================================
def auto_convert(
        text,
        pre_decor=None,
        post_decor=None):
    """
    Convert value to numeric if possible, or strip delimiters from string.

    Args:
        text (str|int|float|complex): The text input string.
        pre_decor (str): initial string decorator.
        post_decor (str): final string decorator.

    Returns:
        val (int|float|complex): The numeric value of the string.

    Examples:
        >>> auto_convert('<100>', '<', '>')
        100
        >>> auto_convert('<100.0>', '<', '>')
        100.0
        >>> auto_convert('100.0+50j')
        (100+50j)
        >>> auto_convert('1e3')
        1000.0
        >>> auto_convert(1000)
        1000
        >>> auto_convert(1000.0)
        1000.0
    """
    if isinstance(text, str):
        if pre_decor and post_decor and \
                has_decorator(text, pre_decor, post_decor):
            text = strip_decorator(text, pre_decor, post_decor)
        try:
            val = int(text)
        except (TypeError, ValueError):
            try:
                val = float(text)
            except (TypeError, ValueError):
                try:
                    val = complex(text)
                except (TypeError, ValueError):
                    val = text
    else:
        val = text
    return val


# ======================================================================
def get_screen_geometry(from_all=False):
    """
    Workaround to get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]
    """
    root = tk.Tk()
    if from_all:
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        geometry = str(Geometry(width=width, height=height))
    else:
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        geometry = root.winfo_geometry()
    root.destroy()
    return geometry


# ======================================================================
def set_icon(
        root,
        basename,
        dirpath=os.path.abspath(os.path.dirname(__file__))):
    basepath = os.path.join(dirpath, basename) if dirpath else basename

    # first try modern file formats
    for file_ext in ['png', 'gif']:
        if not basepath.endswith('.' + file_ext):
            filepath = basepath + '.' + file_ext
        else:
            filepath = basepath
        try:
            icon = tk.PhotoImage(file=filepath)
            root.tk.call('wm', 'iconphoto', root._w, icon)
        except tk.TclError:
            warnings.warn('E: Could not use icon `{}`'.format(filepath))
        else:
            return

    # fall back to ico/xbm format
    tk_sys = root.tk.call('tk', 'windowingsystem')
    if tk_sys.startswith('win'):
        filepath = basepath + '.ico'
    else:  # if tk_sys == 'x11':
        filepath = '@' + basepath + '.xbm'
    try:
        root.iconbitmap(filepath)
    except tk.TclError:
        warnings.warn('E: Could not use icon `{}`.'.format(filepath))
    else:
        return


# ======================================================================
def center(target, reference=None):
    target.update_idletasks()
    if reference is None:
        geometry = get_curr_screen_geometry()
    elif not isinstance(reference, (str, Geometry)):
        reference.update_idletasks()
        geometry = reference.winfo_geometry()
    else:
        geometry = reference
    if isinstance(geometry, str):
        geometry = Geometry(geometry)
    target_geometry = Geometry(target.winfo_geometry())
    target.geometry(str(target_geometry.set_to_center(geometry)))


# ======================================================================
class Geometry(object):
    def __init__(
            self,
            text=None,
            width=0,
            height=0,
            left=0,
            top=0):
        """
        Generate a geometry object from the standard Tk geometry string.

        Args:
            text (str): The standard Tk geometry string.
                If str, Must be: `[width]x[height]+[left]+[top]` (integers).
            width (int): The width value.
                If this can be extracted from `text`, this parameter is
                ignored.
            height (int): The height value.
                If this can be extracted from `text`, this parameter is
                ignored.
            left (int): The left value.
                If this can be extracted from `text`, this parameter is
                ignored.
            top (int): The top value.
                If this can be extracted from `text`, this parameter is
                ignored.
        Returns:
            None.

        Examples:
            >>> print(Geometry('1x2+3+4'))
            1x2+3+4
            >>> print(Geometry())
            0x0+0+0
            >>> print(Geometry('1x2'))
            1x2+0+0
            >>> print(Geometry('+1+2'))
            0x0+1+2
            >>> print(Geometry('1+2+3'))
            1x0+2+3
            >>> print(Geometry('1x2+1'))
            1x2+1+0
            >>> print(Geometry('.'))
        """
        self.width, self.height, self.left, self.top = width, height, left, top
        if isinstance(text, str):
            tokens1 = text.split('+')
            tokens2 = tokens1[0].split('x')
            try:
                self.width = int(tokens2[0])
            except (ValueError, IndexError):
                pass
            try:
                self.height = int(tokens2[1])
            except (ValueError, IndexError):
                pass
            try:
                self.left = int(tokens1[1])
            except (ValueError, IndexError):
                pass
            try:
                self.top = int(tokens1[2])
            except (ValueError, IndexError):
                pass

    def __iter__(self):
        k = 'w', 'h', 'l', 't'
        v = self.width, self.height, self.left, self.top
        for k, v, in zip(k, v):
            yield k, v

    def __str__(self):
        return '{w:d}x{h:d}+{l:d}+{t:d}'.format(**dict(self.items()))

    def __repr__(self):
        return ', '.join([k + '=' + str(v) for k, v in self])

    items = __iter__

    def values(self):
        for k, v in self:
            yield v

    def keys(self):
        for k, v in self:
            yield k

    def set_to_center(self, parent):
        """
        Update the geometry to be centered with respect to a container.

        Args:
            parent (Geometry): The geometry of the container.

        Returns:
            geometry (Geometry): The updated geometry.
        """
        self.left = parent.width // 2 - self.width // 2 + parent.left
        self.top = parent.height // 2 - self.height // 2 + parent.top
        return self


# ======================================================================
class FrameBoard(tk.Frame):
    def __init__(
            self, parent, cell_size=100, border=0.06,
            **_kws):
        tk.Frame.__init__(
            self, parent, highlightthickness=10, highlightbackground='black')
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.parent = parent
        self.board = self.parent.board
        self.border = border
        self.height = self.winfo_height()
        self.width = self.winfo_width()
        self.rows = self.parent.board.rows
        self.cols = self.parent.board.cols
        self.enabled = True
        linewidth = 0.5 * (self.border * (
                (self.height / self.rows) + (self.width / self.cols)))
        self.config(dict(highlightthickness=linewidth))
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.cvsMatrix = np.zeros((self.rows, self.cols), dtype='object')
        for i in range(self.rows):
            for j in range(self.cols):
                cvs = CanvasCell(
                    self, i, j,
                    width=cell_size, height=cell_size,
                    background='white', highlightbackground='black',
                    border=border / 2)
                cvs.grid(column=j, row=i, sticky=tk.N + tk.S + tk.E + tk.W)
                self.cvsMatrix[i, j] = cvs
        for k in range(self.rows):
            self.rowconfigure(k, weight=1)
        for k in range(self.cols):
            self.columnconfigure(k, weight=1)
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, event=None):
        self.width = event.width
        self.height = event.height
        linewidth = 0.5 * (self.border * (
                (self.height / self.rows) + (self.width / self.cols)))
        self.config(dict(highlightthickness=linewidth))

    def reset(self, event=None):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cvsMatrix[i, j].clear()
        self.unfreeze()
        self.refresh()

    def refresh(self, event=None):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board.matrix[i, j] == self.board.TURNS[0] \
                        and not self.cvsMatrix[i, j].content:
                    self.cvsMatrix[i, j].draw_x()
                elif self.board.matrix[i, j] == self.board.TURNS[1] \
                        and not self.cvsMatrix[i, j].content:
                    self.cvsMatrix[i, j].draw_o()
                elif self.board.matrix[i, j] == self.board.EMPTY \
                        and self.cvsMatrix[i, j].content:
                    self.cvsMatrix[i, j].clear()

    def freeze(self, event=None):
        self.enabled = False

    def unfreeze(self, event=None):
        self.enabled = True

    def show_wins(self, event=None):
        winning_series = self.board.winning_series()
        for winning_serie in winning_series:
            coords = self.board.extrema_to_coords(*winning_serie)
            for (i, j) in coords:
                self.cvsMatrix[i, j].highlight()

    def hide_wins(self, event=None):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cvsMatrix[i, j].normal()


# ======================================================================
class CanvasCell(tk.Canvas):
    def __init__(self, parent, row, col, **_kws):
        self.parent = parent
        self.board = self.parent.board
        self.row = row
        self.col = col
        self.background = _kws['background']
        self.hover_background = 'cyan'
        self.highlight_background = 'yellow'
        self.border = _kws.pop('border')
        self.height = _kws['height']
        self.width = _kws['width']
        linewidth = (self.border * (self.height + self.width)) / 2
        _kws['highlightthickness'] = linewidth
        tk.Canvas.__init__(self, parent, **_kws)
        self.drawings = []
        self.content = None
        self.bind('<Button-1>', self.on_click)
        self.bind('<Button-3>', self.clear)
        self.bind('<Configure>', self.on_resize)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_resize(self, event=None):
        self.delete('all')
        self.width = event.width
        self.height = event.height
        linewidth = (self.border * (self.height + self.width)) / 2
        self.config(dict(highlightthickness=linewidth))
        if self.content == 'o':
            self.draw_o()
        elif self.content == 'x':
            self.draw_x()

    def on_enter(self, event=None):
        if self.parent.enabled:
            if not hasattr(self.board, 'has_gravity'):
                self.config(background=self.hover_background)
            else:
                for i in range(self.parent.rows):
                    self.parent.cvsMatrix[i, self.col].config(
                        background=self.hover_background)

    def on_leave(self, event=None):
        if self.parent.enabled:
            if not hasattr(self.board, 'has_gravity'):
                self.normal()
            else:
                for i in range(self.parent.rows):
                    self.parent.cvsMatrix[i, self.col].normal()

    def clear(self, event=None):
        if self.content:
            self.delete('all')
            self.content = None
            self.config(background=self.background)

    def draw_o(self, color='red', weight=0.175, k=0.8):
        self.content = 'o'
        linewidth = (weight * (self.height + self.width)) / 2
        self.drawings = [
            self.create_oval(
                self.width * (1 - k), self.height * (1 - k),
                self.width * k, self.height * k,
                outline=color, width=linewidth)]

    def draw_x(self, color='blue', weight=0.175, k=0.8):
        self.content = 'x'
        linewidth = (weight * (self.height + self.width)) / 2
        self.drawings = [
            self.create_line(
                self.width * (1 - k), self.height * (1 - k),
                self.width * k, self.height * k,
                fill=color, width=linewidth),
            self.create_line(
                self.width * (1 - k), self.height * k,
                self.width * k, self.height * (1 - k),
                fill=color, width=linewidth)]

    def highlight(self, event=None):
        self.config(background=self.highlight_background)

    def normal(self, event=None):
        self.config(background=self.background)

    def on_click(self, event=None):
        if self.parent.enabled:
            if not hasattr(self.board, 'has_gravity'):
                coord = self.row, self.col
            else:
                coord = self.col
            if self.board.do_move(coord):
                self.parent.parent.computer_plays = True
                self.parent.parent.undo_history.append(coord)
                if self.parent.parent.redo_history and \
                        coord == self.parent.parent.redo_history[-1]:
                    self.parent.parent.redo_history.pop()
                else:
                    self.parent.parent.redo_history = []
                self.parent.parent.check_win()
                self.parent.refresh()
        if self.parent.enabled and self.parent.parent.computer_plays:
            self.parent.parent.computer_moves()


# ======================================================================
class WinAbout(tk.Toplevel):
    def __init__(self, parent):
        super(WinAbout, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title('About {}'.format(INFO['name']))
        self.resizable(False, False)
        self.frm = ttk.Frame(self)
        self.frm.pack(fill=tk.BOTH, expand=True)
        self.frmMain = ttk.Frame(self.frm)
        self.frmMain.pack(fill=tk.BOTH, padx=1, pady=1, expand=True)

        about_txt = '\n'.join((
            prettify(MY_GREETINGS[1:]),
            __doc__,
            '{} - ver. {}\n{} {}\n{}'.format(
                INFO['name'], INFO['version'],
                INFO['copyright'], INFO['author'], INFO['notice'])
        ))
        msg(about_txt)
        self.lblInfo = ttk.Label(
            self.frmMain, text=about_txt, anchor=tk.CENTER,
            background='#333', foreground='#ccc', font='TkFixedFont')
        self.lblInfo.pack(padx=8, pady=8, ipadx=8, ipady=8)

        self.btnClose = ttk.Button(
            self.frmMain, text='Close', command=self.destroy)
        self.btnClose.pack(side=tk.BOTTOM, padx=8, pady=8)
        self.bind('<Return>', self.close)
        self.bind('<Escape>', self.close)

        center(self, self.parent)

        self.grab_set()
        self.wait_window(self)

    def close(self, event=None):
        self.destroy()


# ======================================================================
class WinSettings(tk.Toplevel):
    def __init__(self, parent, app):
        self.settings = collections.OrderedDict((
            ('use_mp', {'label': 'Use parallel processing', 'dtype': bool, }),
            ('num_processes', {
                'label': 'Number of parallel processes',
                'dtype': int,
                'values': {'start': 1,
                           'stop': 2 * multiprocessing.cpu_count()},
            }),
            ('gui_style_tk', {
                'label': 'GUI Style (Tk)',
                'dtype': tuple,
                'values': app.style.theme_names()
            }),
        ))
        for name, info in self.settings.items():
            self.settings[name]['default'] = app.cfg[name]
        self.result = None

        super(WinSettings, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.app = app
        self.title('{} Advanced Settings'.format(INFO['name']))
        self.frm = ttk.Frame(self)
        self.frm.pack(fill=tk.BOTH, expand=True)
        self.frmMain = ttk.Frame(self.frm)
        self.frmMain.pack(fill=tk.BOTH, padx=8, pady=8, expand=True)

        self.frmSpacers = []

        self.wdgOptions = {}
        for name, info in self.settings.items():
            if info['dtype'] == bool:
                chk = ttk.Checkbutton(
                    self.frmMain, text=info['label'])
                chk.pack(fill=tk.X, padx=1, pady=1)
                chk.set_val(info['default'])
                self.wdgOptions[name] = {'chk': chk}
            elif info['dtype'] == int:
                frm = ttk.Frame(self.frmMain)
                frm.pack(fill=tk.X, padx=1, pady=1)
                lbl = ttk.Label(frm, text=info['label'])
                lbl.pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=True)
                spb = ttk.Spinbox(frm, **info['values'])
                spb.set_val(info['default'])
                spb.pack(
                    side=tk.LEFT, fill=tk.X, anchor=tk.W, padx=1, pady=1)
                self.wdgOptions[name] = {'frm': frm, 'lbl': lbl, 'spb': spb}
            elif info['dtype'] == tuple:
                frm = ttk.Frame(self.frmMain)
                frm.pack(fill=tk.X, padx=1, pady=1)
                lbl = ttk.Label(frm, text=info['label'])
                lbl.pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=True)
                lst = ttk.Listbox(frm, values=info['values'])
                lst.set_val(info['default'])
                lst.pack(
                    side=tk.LEFT, fill=tk.X, anchor=tk.W, padx=1, pady=1)
                self.wdgOptions[name] = {'frm': frm, 'lbl': lbl, 'lst': lst}

        self.frmButtons = ttk.Frame(self.frmMain)
        self.frmButtons.pack(side=tk.BOTTOM, padx=4, pady=4)
        spacer = ttk.Frame(self.frmButtons)
        spacer.pack(side=tk.LEFT, anchor='e', expand=True)
        self.frmSpacers.append(spacer)
        self.btnOK = ttk.Button(
            self.frmButtons, text='OK', compound=tk.LEFT,
            command=self.ok)
        self.btnOK.pack(side=tk.LEFT, padx=4, pady=4)
        self.btnReset = ttk.Button(
            self.frmButtons, text='Reset', compound=tk.LEFT,
            command=self.reset)
        self.btnReset.pack(side=tk.LEFT, padx=4, pady=4)
        self.btnCancel = ttk.Button(
            self.frmButtons, text='Cancel', compound=tk.LEFT,
            command=self.cancel)
        self.btnCancel.pack(side=tk.LEFT, padx=4, pady=4)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)

        center(self, self.parent)

        self.grab_set()
        self.wait_window(self)

    # --------------------------------
    def ok(self, event=None):
        if not self.validate():
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def reset(self, event=None):
        for name, info in self.settings.items():
            if info['dtype'] == bool:
                self.wdgOptions[name]['chk'].set_val(self.app.cfg[name])
            elif info['dtype'] == int:
                self.wdgOptions[name]['spb'].set_val(self.app.cfg[name])
            elif info['dtype'] == str:
                self.wdgOptions[name]['ent'].set_val(self.app.cfg[name])
            elif info['dtype'] == tuple:
                self.wdgOptions[name]['lst'].set_val(self.app.cfg[name])

    def validate(self, event=None):
        return True

    def apply(self, event=None):
        self.result = {}
        for name, info in self.settings.items():
            if info['dtype'] == bool:
                self.result[name] = self.wdgOptions[name]['chk'].get_val()
            elif info['dtype'] == int:
                self.result[name] = self.wdgOptions[name]['spb'].get_val()
            elif info['dtype'] == str:
                self.result[name] = self.wdgOptions[name]['ent'].get_val()
            elif info['dtype'] == tuple:
                self.result[name] = self.wdgOptions[name]['lst'].get_val()


# ======================================================================
class WinMain(ttk.Frame):
    def __init__(self, parent, screen_size, *_args, **_kws):
        super(WinMain, self).__init__(parent)
        self.parent = parent
        self.rows = tk.IntVar(None, _kws['rows'])
        self.cols = tk.IntVar(None, _kws['cols'])
        self.num_win = tk.IntVar(None, _kws['num_win'])
        self.gravity = tk.BooleanVar(None, _kws['gravity'])
        self.ai_mode = tk.StringVar(None, _kws['ai_mode'])
        self.game_alias = tk.StringVar(None, guess_alias(**_kws))
        self.ai_timeout = tk.DoubleVar(None, _kws['ai_timeout'])
        self.verbose = _kws['verbose']
        self.computer_plays = _kws['computer_plays']
        self.ai_class = AI_MODES[self.ai_mode.get()]['ai_class']
        self.ai_method = AI_MODES[self.ai_mode.get()]['ai_method']
        self.board = make_board(
            self.rows.get(), self.cols.get(), self.num_win.get(),
            self.gravity.get())
        self.first_computer_plays = self.computer_plays
        self.computer_plays = self.first_computer_plays
        self.undo_history = []
        self.redo_history = []

        self.screen_size = screen_size

        # get_val config data
        cfg = {}
        self.cfg = default_config()
        for dirpath in CFG_DIRPATHS:
            self.cfg_filepath = os.path.join(dirpath, CFG_FILENAME)
            cfg = load_config(self.cfg_filepath)
            if cfg:
                break
        if cfg:
            self.cfg.update(cfg)
        else:
            self.cfg_filepath = os.path.join(_PATHS['usr_cfg'], CFG_FILENAME)

        # :: initialization of the UI
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('(m,n,k)+g-Game')
        self.parent.protocol('WM_DELETE_WINDOW', self.exit)

        self.style = ttk.Style()
        # print(self.style.theme_names())
        self.style.theme_use(self.cfg['gui_style_tk'])
        self.pack(fill=tk.BOTH, expand=True)

        # print(tk.font.families())
        self._make_menu(tk.font.Font(family='lucida', size=10))
        self.menu_font = tk.font.Font(font=self.mnuMain['font'])

        # :: define UI items
        self.frmBoard = FrameBoard(self, self.optim_cell_size)

        self.parent.minsize(
            self.cols.get() * self.optim_cell_size // 5,
            self.rows.get() * self.optim_cell_size // 5
            + 4 * self.menu_font.actual()['size'])

        center(self.parent, self.screen_size)

    @property
    def optim_cell_size(self):
        return int(
            ((self.screen_size.width / self.board.cols / 3)
             + (self.screen_size.height / self.board.rows / 3)) / 2)

    # --------------------------------
    def _ui_to_cfg(self):
        """Update the config information from the UI."""
        cfg = self.cfg
        return cfg

    def _cfg_to_ui(self):
        """Update the config information to the UI."""
        for target in self.cfg['input_paths']:
            self.lsvInput.add_item(target, unique=True)
        self.entPath.set_val(self.cfg['output_path'])
        self.entSubpath.set_val(self.cfg['output_subpath'])
        self.save_on_exit.set(self.cfg['save_on_exit'])
        self.style.theme_use(self.cfg['gui_style_tk'])
        for name, items in self.wdgModules.items():
            items['chk'].set_val(True if self.cfg[name] else False)
            items['ent'].set_val(self.cfg[name])
        for name, items in self.wdgOptions.items():
            if 'chk' in items:
                items['chk'].set_val(self.cfg[name])
            elif 'spb' in items:
                items['spb'].set_val(self.cfg[name])
        self.activateModules()

    def _make_menu(self, font=None):
        self.save_on_exit = tk.BooleanVar(value=self.cfg['save_on_exit'])

        self.mnuMain = tk.Menu(self.parent, tearoff=False, font=font)
        self.parent.config(menu=self.mnuMain)

        self.mnuGame = tk.Menu(self.mnuMain, tearoff=False, font=font)
        self.mnuMain.add_cascade(
            label='Game', underline=0, menu=self.mnuGame)
        self.mnuNewGame = tk.Menu(self.mnuGame, tearoff=False, font=font)
        self.mnuGame.add_cascade(
            label='New', underline=0, menu=self.mnuNewGame)
        self.mnuNewGame.add_command(
            label='...as current', underline=3, command=self.new_game,
            accelerator='Ctrl+N')
        self.mnuNewGame.add_separator()
        for alias, info in ALIASES.items():
            if info:
                title = alias.replace('_', ' ').title()
                self.mnuNewGame.add_radiobutton(
                    label=title, underline=0, command=self.new_aliased,
                    value=alias, variable=self.game_alias)
        self.mnuNewGame.add_radiobutton(
            label='Custom...', underline=1, command=self.new_custom,
            value='custom', variable=self.game_alias)
        self.mnuGame.add_separator()
        self.mnuGame.add_command(
            label='Load...', underline=0, command=self.load_game,
            accelerator='Ctrl+O')
        self.mnuGame.add_command(
            label='Save...', underline=0, command=self.save_game,
            accelerator='Ctrl+S')
        self.mnuGame.add_separator()
        self.mnuGame.add_command(
            label='Exit', underline=1, command=self.exit,
            accelerator='Ctrl+X')

        self.mnuGame = tk.Menu(self.mnuMain, tearoff=False, font=font)
        self.mnuMain.add_cascade(
            label='Move', underline=1, menu=self.mnuGame)
        self.mnuGame.add_command(
            label='Undo', underline=0, command=self.undo_move,
            accelerator='Ctrl+Z')
        self.mnuGame.add_command(
            label='Redo', underline=0, command=self.redo_move,
            accelerator='Ctrl+Shift+Z')
        self.mnuGame.add_separator()
        self.mnuGame.add_command(
            label='Switch Sides', underline=1, command=self.switch_sides,
            accelerator='Ctrl-W')
        self.mnuGame.add_command(
            label='Hint', underline=0, command=self.hint,
            accelerator='Ctrl-H')

        self.mnuSettings = tk.Menu(self.mnuMain, tearoff=False, font=font)
        self.mnuMain.add_cascade(
            label='Settings', underline=0, menu=self.mnuSettings)
        self.mnuAiMode = tk.Menu(self.mnuSettings, tearoff=False, font=font)
        self.mnuSettings.add_cascade(
            label='AI Mode', underline=0, menu=self.mnuAiMode)
        for ai_mode in AI_MODES.keys():
            title = ai_mode.replace('_', ' ').title()
            self.mnuAiMode.add_radiobutton(
                label=title, underline=0, command=self.change_ai_mode,
                value=ai_mode, variable=self.ai_mode)
        self.mnuAiTimeout = tk.Menu(self.mnuSettings, tearoff=False, font=font)
        self.mnuSettings.add_cascade(
            label='AI Timeout', underline=0, menu=self.mnuAiTimeout)
        for value in (0.5, 1.0, 5.0, 10.0, 60.0):
            self.mnuAiTimeout.add_radiobutton(
                label='{:.0f} sec'.format(value), underline=0, command=None,
                value=value, variable=self.ai_timeout)
        self.mnuAiTimeout.add_command(
            label='Custom...', underline=0, command=self.change_ai_timeout)
        self.mnuSettings.add_separator()
        self.mnuSettings.add_command(
            label='Restore View', underline=4, command=self.restore_view)
        self.mnuSettings.add_command(
            label='Advanced', underline=0, command=self.advanced_settings)
        self.mnuSettings.add_separator()
        self.mnuSettings.add_command(
            label='Load Settings', underline=0, command=self.load_settings)
        self.mnuSettings.add_command(
            label='Save Settings', underline=0, command=self.save_settings)
        self.mnuSettings.add_separator()
        self.mnuSettings.add_checkbutton(
            label='Save on Exit', underline=2, variable=self.save_on_exit)
        self.mnuSettings.add_command(
            label='Reset Defaults', underline=0, command=self.reset_defaults)

        self.mnuHelp = tk.Menu(self.mnuMain, tearoff=False, font=font)
        self.mnuMain.add_cascade(
            label='Help', menu=self.mnuHelp, underline=0)
        self.mnuHelp.add_command(
            label='About', command=self.about, underline=0,
            accelerator='Ctrl+?')

        self.bind_all("<Control-n>", self.new_game)
        self.bind_all("<Control-o>", self.load_game)
        self.bind_all("<Control-s>", self.save_game)
        self.bind_all("<Control-x>", self.exit)
        self.bind_all("<Control-z>", self.undo_move)
        self.bind_all("<Control-Z>", self.redo_move)
        self.bind_all("<Control-w>", self.switch_sides)
        self.bind_all("<Control-h>", self.hint)
        self.bind_all("<Control-question>", self.about)

    def new_game(self, event=None):
        self.first_computer_plays = not self.first_computer_plays
        self.computer_plays = self.first_computer_plays
        self.board.reset()
        self.undo_history = []
        self.redo_history = []
        self.frmBoard.reset()
        if self.computer_plays:
            self.computer_moves()

    def _new_game(self, **_kws):
        self.board = make_board(**_kws)
        self.rows.set(self.board.rows)
        self.cols.set(self.board.cols)
        self.num_win.set(self.board.num_win)
        self.gravity.set(hasattr(self.board, 'has_gravity'))
        self.frmBoard = FrameBoard(self, self.optim_cell_size)
        self.restore_view()
        self.new_game()

    def new_aliased(self, event=None):
        if self.board.is_empty() or messagebox.askokcancel(
                'Continue', 'This will start a new game. Are you sure?'):
            alias = self.game_alias.get()
            self._new_game(**ALIASES[alias])

    def new_custom(self, event=None):
        if self.board.is_empty() or messagebox.askokcancel(
                'Continue', 'This will start a new game. Are you sure?'):
            rows = simpledialog.askinteger(
                'Rows', 'Number of Rows', initialvalue=self.rows.get(),
                minvalue=1, maxvalue=32)
            cols = simpledialog.askinteger(
                'Columns', 'Number of Columns', initialvalue=self.cols.get(),
                minvalue=1, maxvalue=32)
            num_win = simpledialog.askinteger(
                'Num.Winning', 'Number for Winning',
                initialvalue=self.num_win.get(),
                minvalue=min(3, rows, cols), maxvalue=max(rows, cols))
            gravity = bool(simpledialog.askinteger(
                'Gravity', 'Has Gravity', initialvalue=self.gravity.get(),
                minvalue=0, maxvalue=1))
            kws = dict(
                rows=rows if rows is not None else self.rows.get(),
                cols=cols if cols is not None else self.cols.get(),
                num_win=num_win if num_win is not None else self.num_win.get(),
                gravity=gravity if gravity is not None else self.gravity.get())
            alias = guess_alias(**kws)
            self.game_alias.set(alias)
            self._new_game(**kws)

    def load_game(self, event=None):
        pass

    def save_game(self, event=None):
        pass

    def exit(self, event=None):
        """Action on Exit."""
        if messagebox.askokcancel('Exit', 'Are you sure you want to exit?'):
            self.cfg = self._ui_to_cfg()
            if self.cfg['save_on_exit']:
                save_config(self.cfg, self.cfg_filepath)
            self.parent.destroy()

    def undo_move(self, event=None):
        if self.undo_history:
            coord = self.undo_history.pop(-1)
            self.board.undo_move(coord)
            self.redo_history.append(coord)
            self.frmBoard.hide_wins()
            self.frmBoard.unfreeze()
            self.frmBoard.refresh()

    def redo_move(self, event=None):
        if self.redo_history:
            coord = self.redo_history.pop(-1)
            self.board.do_move(coord)
            self.undo_history.append(coord)
            self.frmBoard.refresh()
            self.check_win()

    def switch_sides(self, event=None):
        if self.frmBoard.enabled:
            self.computer_plays = not self.computer_plays
            self.computer_moves()

    def hint(self, event=None):
        pass

    def change_ai_mode(self, event=None):
        self.ai_class = AI_MODES[self.ai_mode.get()]['ai_class']
        self.ai_method = AI_MODES[self.ai_mode.get()]['ai_method']

    def change_ai_timeout(self, event=None):
        ai_timeout = simpledialog.askfloat(
            'AI Timeout', 'AI Timeout in sec?',
            initialvalue=self.ai_timeout.get(),
            minvalue=0.1, maxvalue=60000.0)
        if ai_timeout is not None:
            self.ai_timeout.set(ai_timeout)

    def about(self, event=None):
        """Action on About."""
        self.winAbout = WinAbout(self.parent)

    def restore_view(self, event=None):
        new_geometry = Geometry(self.parent.geometry())
        new_geometry.width = int(self.cols.get() * self.optim_cell_size)
        new_geometry.height = int(
            self.rows.get() * self.optim_cell_size
                   + 2 * self.menu_font.actual()['size'])
        self.parent.geometry(new_geometry)
        print(new_geometry)
        center(self.parent, self.screen_size)

    def advanced_settings(self, event=None):
        self.winSettings = WinSettings(self.parent, self)
        if self.winSettings.result:
            self.cfg.update(self.winSettings.result)
        self._cfg_to_ui()
        # force resize for redrawing widgets correctly
        # w, h = self.parent.winfo_width(), self.parent.winfo_height()
        self.parent.update_idletasks()

    def load_settings(self):
        self.cfg = load_config(self.cfg_filepath)
        self._cfg_to_ui()

    def save_settings(self):
        self.cfg = self._ui_to_cfg()
        save_config(self.cfg, self.cfg_filepath)

    def reset_defaults(self, event=None):
        self.cfg = default_config()
        self._cfg_to_ui()

    def computer_moves(self):
        if not self.board.is_full() and self.computer_plays:
            coord = self.ai_class().get_best_move(
                self.board,
                self.ai_timeout.get(), self.ai_method, max_depth=-1,
                verbose=self.verbose >= D_VERB_LVL)
            if self.board.do_move(coord):
                self.computer_plays = False
                self.undo_history.append(coord)
                if self.redo_history and coord == self.redo_history[-1]:
                    self.redo_history.pop()
                else:
                    self.redo_history = []
                self.frmBoard.refresh()
                self.check_win()

    def check_win(self):
        ask_new = True
        if self.board.winner(self.board.turn) == self.board.turn:
            self.frmBoard.refresh()
            self.frmBoard.freeze()
            self.frmBoard.show_wins()
            title = 'Victory!'
            text = 'You LOST!' if not self.computer_plays else 'You WON!'
            icon = 'error' if not self.computer_plays else 'info'
        elif self.board.is_full():
            self.frmBoard.refresh()
            self.frmBoard.freeze()
            title = 'Draw!'
            text = 'The game ended with a draw!'
            icon = 'question'
        else:
            ask_new = False
        if ask_new:
            answer = messagebox.askquestion(
                title=title,
                message='\n\n'.join([text, 'Do you want to play a new game?']),
                icon=icon)
            if answer == 'yes':
                self.new_game()


# ======================================================================
def mnk_game_gui(*_args, **_kws):
    screen_size = Geometry(get_screen_geometry(True))
    root = tk.Tk()
    app = WinMain(root, screen_size, *_args, **_kws)
    resources_path = PATH['resources']
    set_icon(root, 'icon', resources_path)
    root.mainloop()


if __name__ == '__main__':
    mnk_game_gui(
        # rows=6, cols=7, num_win=4, gravity=True,
        rows=3, cols=3, num_win=3, gravity=False,
        ai_mode='alphabeta', computer_plays=False,
        ai_timeout=0.5, verbose=VERB_LVL['lowest'])
