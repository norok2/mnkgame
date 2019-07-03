#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(m,n,k)-game: graphical user interface.
"""
import os
import multiprocessing
import collections
import json

import pytk.util
import pytk.widgets
from pytk import tk, ttk
from pytk import messagebox
from pytk import filedialog
from pytk import simpledialog

from mnkgame import D_VERB_LVL
from mnkgame import msg
from mnkgame import INFO, PATH
from mnkgame import print_greetings, prettify, MY_GREETINGS
from mnkgame.util import prepare_game

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
class WinAbout(pytk.Window):
    def __init__(self, parent):
        self.win = super(WinAbout, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title('About {}'.format(INFO['name']))
        self.resizable(False, False)
        self.frm = pytk.widgets.Frame(self)
        self.frm.pack(fill=tk.BOTH, expand=True)
        self.frmMain = pytk.widgets.Frame(self.frm)
        self.frmMain.pack(fill=tk.BOTH, padx=1, pady=1, expand=True)

        about_txt = '\n'.join((
            prettify(MY_GREETINGS[1:]),
            __doc__,
            '{} - ver. {}\n{} {}\n{}'.format(
                INFO['name'], INFO['version'],
                INFO['copyright'], INFO['author'], INFO['notice'])
        ))
        msg(about_txt)
        self.lblInfo = pytk.widgets.Label(
            self.frmMain, text=about_txt, anchor=tk.CENTER,
            background='#333', foreground='#ccc', font='TkFixedFont')
        self.lblInfo.pack(padx=8, pady=8, ipadx=8, ipady=8)

        self.btnClose = pytk.widgets.Button(
            self.frmMain, text='Close', command=self.destroy)
        self.btnClose.pack(side=tk.BOTTOM, padx=8, pady=8)
        self.bind('<Return>', self.destroy)
        self.bind('<Escape>', self.destroy)

        pytk.util.center(self, self.parent)

        self.grab_set()
        self.wait_window(self)


# ======================================================================
class WinSettings(pytk.Window):
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

        self.win = super(WinSettings, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.app = app
        self.title('{} Advanced Settings'.format(INFO['name']))
        self.frm = pytk.widgets.Frame(self)
        self.frm.pack(fill=tk.BOTH, expand=True)
        self.frmMain = pytk.widgets.Frame(self.frm)
        self.frmMain.pack(fill=tk.BOTH, padx=8, pady=8, expand=True)

        self.frmSpacers = []

        self.wdgOptions = {}
        for name, info in self.settings.items():
            if info['dtype'] == bool:
                chk = pytk.widgets.Checkbutton(
                    self.frmMain, text=info['label'])
                chk.pack(fill=tk.X, padx=1, pady=1)
                chk.set_val(info['default'])
                self.wdgOptions[name] = {'chk': chk}
            elif info['dtype'] == int:
                frm = pytk.widgets.Frame(self.frmMain)
                frm.pack(fill=tk.X, padx=1, pady=1)
                lbl = pytk.widgets.Label(frm, text=info['label'])
                lbl.pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=True)
                spb = pytk.widgets.Spinbox(frm, **info['values'])
                spb.set_val(info['default'])
                spb.pack(
                    side=tk.LEFT, fill=tk.X, anchor=tk.W, padx=1, pady=1)
                self.wdgOptions[name] = {'frm': frm, 'lbl': lbl, 'spb': spb}
            elif info['dtype'] == tuple:
                frm = pytk.widgets.Frame(self.frmMain)
                frm.pack(fill=tk.X, padx=1, pady=1)
                lbl = pytk.widgets.Label(frm, text=info['label'])
                lbl.pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=True)
                lst = pytk.widgets.Listbox(frm, values=info['values'])
                lst.set_val(info['default'])
                lst.pack(
                    side=tk.LEFT, fill=tk.X, anchor=tk.W, padx=1, pady=1)
                self.wdgOptions[name] = {'frm': frm, 'lbl': lbl, 'lst': lst}

        self.frmButtons = pytk.widgets.Frame(self.frmMain)
        self.frmButtons.pack(side=tk.BOTTOM, padx=4, pady=4)
        spacer = pytk.widgets.Frame(self.frmButtons)
        spacer.pack(side=tk.LEFT, anchor='e', expand=True)
        self.frmSpacers.append(spacer)
        self.btnOK = pytk.widgets.Button(
            self.frmButtons, text='OK', compound=tk.LEFT,
            command=self.ok)
        self.btnOK.pack(side=tk.LEFT, padx=4, pady=4)
        self.btnReset = pytk.widgets.Button(
            self.frmButtons, text='Reset', compound=tk.LEFT,
            command=self.reset)
        self.btnReset.pack(side=tk.LEFT, padx=4, pady=4)
        self.btnCancel = pytk.widgets.Button(
            self.frmButtons, text='Cancel', compound=tk.LEFT,
            command=self.cancel)
        self.btnCancel.pack(side=tk.LEFT, padx=4, pady=4)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)

        pytk.util.center(self, self.parent)

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
class WinMain(pytk.widgets.Frame):
    def __init__(self, parent, *_args, **_kws):
        super(WinMain, self).__init__()

        self.rows = _kws['rows']
        self.cols = _kws['cols']
        self.aligned = _kws['aligned']
        self.gravity = _kws['gravity']
        self.ai_mode = _kws['ai_mode']
        self.computer_plays = _kws['computer_plays']
        self.board, self.game_ai_class, self.method = prepare_game(
            self.rows, self.cols, self.aligned, self.gravity, self.ai_mode)
        self.first_computer_plays = self.computer_plays

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
        pytk.widgets.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('(m,n,k)+g-Game')
        self.parent.protocol('WM_DELETE_WINDOW', self.actionExit)

        self.style = pytk.Style()
        # print(self.style.theme_names())
        self.style.theme_use(self.cfg['gui_style_tk'])
        self.pack(fill=tk.BOTH, expand=True)

        self._make_menu()

        # :: define UI items
        self.frmMain = pytk.widgets.Frame(self)
        self.frmMain.pack(fill=tk.BOTH, padx=2, pady=2, expand=True)
        self.frmBoard = pytk.widgets.Frame(self.frmMain)

        self.cvsBoard = []
        for i in range(self.board.rows):
            for j in range(self.board.cols):
                canvas = tk.Canvas(
                    self.frmBoard, width=50, height=50, borderwidth=2, highlightthickness=0, bg='black')
                canvas.grid(row=i, column=j)
                self.cvsBoard.append(canvas)

        pytk.util.center(self.parent)
        # self._cfg_to_ui()

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

    def _make_menu(self):
        self.save_on_exit = tk.BooleanVar(value=self.cfg['save_on_exit'])

        self.mnuMain = tk.Menu(self.parent, tearoff=False)
        self.parent.config(menu=self.mnuMain)
        self.mnuFile = tk.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='File', menu=self.mnuFile)
        self.mnuFileInput = tk.Menu(self.mnuFile, tearoff=False)
        self.mnuFile.add_cascade(label='Input', menu=self.mnuFileInput)
        self.mnuFileInput.add_command(label='Add...', command=self.actionAdd)
        self.mnuFileInput.add_command(
            label='Remove', command=self.actionRemove)
        self.mnuFileInput.add_command(
            label='Clear', command=self.actionClear)
        self.mnuFileInput.add_separator()
        self.mnuFileInput.add_command(
            label='Import...', command=self.actionImport)
        self.mnuFileInput.add_command(
            label='Export...', command=self.actionExport)
        self.mnuFileOutput = tk.Menu(self.mnuFile, tearoff=False)
        self.mnuFile.add_cascade(label='Output', menu=self.mnuFileOutput)
        self.mnuFileOutput.add_command(
            label='Path...', command=self.actionPath)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label='Run', command=self.actionRun)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label='Exit', command=self.actionExit)
        self.mnuSettings = tk.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='Settings', menu=self.mnuSettings)
        self.mnuSettings.add_command(
            label='Advanced', command=self.actionAdvancedSettings)
        self.mnuSettings.add_separator()
        self.mnuSettings.add_command(
            label='Load Settings', command=self.actionLoadSettings)
        self.mnuSettings.add_command(
            label='Save Settings', command=self.actionSaveSettings)
        self.mnuSettings.add_separator()
        self.mnuSettings.add_checkbutton(
            label='Save on Exit', variable=self.save_on_exit)
        self.mnuSettings.add_command(
            label='Reset Defaults', command=self.actionResetDefaults)
        self.mnuHelp = tk.Menu(self.mnuMain, tearoff=False)
        self.mnuMain.add_cascade(label='Help', menu=self.mnuHelp)
        self.mnuHelp.add_command(label='About', command=self.actionAbout)

    def actionRun(self, event=None):
        """Action on Click Button Run."""
        # TODO: redirect stdout to some log box / use progressbar
        # extract options
        force = self.wdgOptions['force']['chk'].get_val()
        msg('Force: {}'.format(force))
        verbose = VERB_LVL[self.wdgOptions['verbose']['spb'].get_val()]
        msg('Verb.: {}'.format(verbose))
        if self.cfg['use_mp']:
            # parallel
            pool = multiprocessing.Pool(processes=self.cfg['num_processes'])
            proc_result_list = []
        for in_dirpath in self.lsvInput.get_items():
            kws = {
                name: info['ent'].get_val()
                for name, info in self.wdgModules.items()}
            kws.update({
                'in_dirpath': in_dirpath,
                'out_dirpath': os.path.expanduser(self.entPath.get()),
                'subpath': self.entSubpath.get(),
                'force': force,
                'verbose': verbose,
            })
            # print(kws)
            if self.cfg['use_mp']:
                proc_result = pool.apply_async(
                    dcmpi_run, kwds=kws)
                proc_result_list.append(proc_result)
            else:
                dcmpi_run(**kws)
        # print(proc_result_list)
        if self.cfg['use_mp']:
            res_list = []
            for proc_result in proc_result_list:
                res_list.append(proc_result.get())
        return

    def actionImport(self, event=None):
        """Action on Click Button Import."""
        title = '{} {} List'.format(
            self.btnImport.cget('text'), self.lblInput.cget('text'))
        in_filepath = filedialog.askopenfilename(
            parent=self, title=title, defaultextension='.json',
            initialdir=self.cfg['import_path'],
            filetypes=[('JSON Files', '*.json')])
        if in_filepath:
            try:
                with open(in_filepath, 'r') as in_file:
                    targets = json.load(in_file)
                for target in targets:
                    self.lsvInput.add_item(target, unique=True)
            except ValueError:
                title = self.btnImport.cget('text') + ' Failed'
                msg = 'Could not import input list from `{}`'.format(
                    in_filepath)
                messagebox.showerror(title=title, message=msg)
            finally:
                self.cfg['import_path'] = os.path.dirname(in_filepath)

    def actionExport(self, event=None):
        """Action on Click Button Export."""
        title = '{} {} List'.format(
            self.btnExport.cget('text'), self.lblInput.cget('text'))
        out_filepath = filedialog.asksaveasfilename(
            parent=self, title=title, defaultextension='.json',
            initialdir=self.cfg['export_path'],
            filetypes=[('JSON Files', '*.json')], confirmoverwrite=True)
        if out_filepath:
            targets = self.lsvInput.get_items()
            if not targets:
                title = self.btnExport.cget('text')
                msg = 'Empty {} list.\n'.format(self.lblInput.cget('text')) + \
                      'Do you want to proceed exporting?'
                proceed = messagebox.askyesno(title=title, message=msg)
            else:
                proceed = True
            if proceed:
                with open(out_filepath, 'w') as out_file:
                    json.dump(targets, out_file, sort_keys=True, indent=4)
                self.cfg['export_path'] = os.path.dirname(out_filepath)

    def actionAdd(self, event=None):
        """Action on Click Button Add."""
        title = self.btnAdd.cget('text') + ' ' + self.lblInput.cget('text')
        target = filedialog.askdirectory(
            parent=self, title=title, initialdir=self.cfg['add_path'],
            mustexist=True)
        if target:
            self.lsvInput.add_item(target, unique=True)
            self.cfg['add_path'] = target
        return target

    def actionRemove(self, event=None):
        """Action on Click Button Remove."""
        items = self.lsvInput.get_children('')
        selected = self.lsvInput.selection()
        if selected:
            for item in selected:
                self.lsvInput.delete(item)
        elif items:
            self.lsvInput.delete(items[-1])
        else:
            msg('Empty input list!')

    def actionClear(self, event=None):
        """Action on Click Button Clear."""
        self.lsvInput.clear()

    def actionPath(self, event=None):
        """Action on Click Text Output."""
        title = self.lblOutput.cget('text') + ' ' + self.lblPath.cget('text')
        target = filedialog.askdirectory(
            parent=self, title=title, initialdir=self.cfg['output_path'],
            mustexist=True)
        if target:
            self.entPath.set_val(target)
        return target

    def activateModules(self, event=None):
        """Action on Change Checkbox Import."""
        for name, items in self.wdgModules.items():
            active = items['chk'].get_val()
            if items['ent']:
                items['ent']['state'] = 'enabled' if active else 'disabled'

    def actionExit(self, event=None):
        """Action on Exit."""
        if messagebox.askokcancel('Quit', 'Are you sure you want to quit?'):
            self.cfg = self._ui_to_cfg()
            if self.cfg['save_on_exit']:
                save_config(self.cfg, self.cfg_filepath)
            self.parent.destroy()

    def actionAbout(self, event=None):
        """Action on About."""
        self.winAbout = WinAbout(self.parent)

    def actionAdvancedSettings(self, event=None):
        self.winSettings = WinSettings(self.parent, self)
        if self.winSettings.result:
            self.cfg.update(self.winSettings.result)
        self._cfg_to_ui()
        # force resize for redrawing widgets correctly
        # w, h = self.parent.winfo_width(), self.parent.winfo_height()
        self.parent.update()

    def actionLoadSettings(self):
        self.cfg = load_config(self.cfg_filepath)
        self._cfg_to_ui()

    def actionSaveSettings(self):
        self.cfg = self._ui_to_cfg()
        save_config(self.cfg, self.cfg_filepath)

    def actionResetDefaults(self, event=None):
        self.cfg = default_config()
        self._cfg_to_ui()


# ======================================================================
def mnk_game_gui(*_args, **_kws):
    root = pytk.tk.Tk()
    app = WinMain(root, *_args, **_kws)
    resources_path = PATH['resources']
    pytk.util.set_icon(root, 'icon', resources_path)
    root.mainloop()
