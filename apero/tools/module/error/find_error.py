#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-02-13 11:47
@author: ncook
Version 0.0.1
"""
import numpy as np
import os
import tkinter as tk
from tkinter import font
from tkinter import messagebox
import re

from apero.base import base
from apero.base import drs_db
from apero.core.core import drs_misc
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.testing import drs_dev


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'find_error.py'
__INSTRUMENT__ = base.IPARAMS['INSTRUMENT']
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog

# -----------------------------------------------------------------------------
# define the program name
PROGRAM_NAME = 'APERO language Code Locator'
# define the small, normal and large text size
LARGE = 16
NORMAL = 12
SMALL = 10
# define internal path to database explorer
EXPLORER_PATH = os.path.join('tools', 'recipes', 'bin', 'apero_explorer.py')
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
find_error = drs_dev.TmpRecipe()
find_error.name = __NAME__
find_error.shortname = 'FIND_ERROR'
find_error.instrument = __INSTRUMENT__
find_error.in_block_str = 'red'
find_error.out_block_str = 'red'
find_error.extension = 'fits'
find_error.description = 'GUI for locating APERO language codes'
find_error.kind = 'misc'
find_error.set_debug_plots()
find_error.set_summary_plots()
# add recipe to recipe definition
RMOD.add(find_error)


# =============================================================================
# Define new widgets
# =============================================================================
class WrappingLabel(tk.Label):
    """
    a type of Label that automatically adjusts the wrap to the size

    From here:
    https://www.reddit.com/r/learnpython/comments/6dndqz/
         how_would_you_make_text_that_automatically_wraps/
    """

    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>',
                  lambda e: self.config(wraplength=self.winfo_width()))


class AutocompleteEntry(tk.Entry):
    """
    a autocomplete entry form which uses a list

    From here:
    http://code.activestate.com/recipes/
        578253-an-entry-with-autocompletion-for-the-tkinter-gui/
    """

    def __init__(self, lista, *args, **kwargs):

        tk.Entry.__init__(self, *args, **kwargs)
        self.lista = lista
        self.lb = None
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)

        self.lb_up = False

    def changed(self, name, index, mode):

        if self.var.get() == '':
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(),
                                  y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True

                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):

        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def up(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != tk.END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.lista if re.match(pattern, w)]

    def destroy_tab(self, event=None):
        if self.lb is not None:
            self.lb.destroy()
            self.lb_up = False


# =============================================================================
# Define classes
# =============================================================================
class Navbar:
    """
    Navigation bar widget
    """

    def __init__(self, master):
        """
        Navigation bar constructor

        :param master: tk.TK parent app/frame

        :type master: tk.TK
        """
        self.master = master
        self.menubar = tk.Menu(master)
        # set title
        self.title = 'About {0}'.format(PROGRAM_NAME)
        # add file menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Open database folder',
                                  command=self.open)
        self.filemenu.add_command(label='Quit', command=self.quit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        # add help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='About', command=self.about)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

    def about(self):
        """
        Make the about message box

        :return:
        """
        # write about message
        message = ('Search for an error code or a help code. \nDisplay '
                   'information about this code including location, '
                   'arguments, comments, and python script location.')
        # make message box
        messagebox.showinfo(self.title, message)

    def quit(self):
        """
        Quits the app
        :return:
        """
        self.master.destroy()

    def open(self):
        """
        Opens the database folder (requires web browser)

        :return:
        """
        root = self.master.datastore.drs_params['DRS_ROOT']
        explorer = os.path.join(root, EXPLORER_PATH)
        os.system('python {0}'.format(explorer))


class Search:
    """
    The search widget - has the autocomplete search feature, search button
    and instrument
    """

    def __init__(self, parent, appobj):
        """
        Search widget constructor
        :param parent: tk.TK parent app/frame
        :param appobj: tk.TK root app
        """
        self.frame = tk.Frame(parent)
        self.master = parent
        self.entry = None
        self.button = None
        self.ilabel = None
        self.tkvar = None
        self.popup_menu = None
        self.titlebar = appobj.s1
        self.rbox1 = appobj.r1
        self.rbox2 = appobj.r2
        self.dataobj = appobj.datastore

        self.search_entry(self.frame)
        # add frame
        self.frame.pack(padx=10, pady=10)
        # set up the grid weights (to make it expand to full size)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=0)
        self.frame.grid_columnconfigure(3, weight=0)

    def search_entry(self, frame):
        """
        Populate the widget with the entry/button/label/drop down box
        :param frame: tk.Frame, the parent frame
        :type frame: tk.Frame
        :return:
        """
        # get all keys
        lista = list(self.dataobj.dict.keys())
        # add the search box
        self.entry = AutocompleteEntry(lista=lista, master=frame, width=32,
                                       background='white',
                                       font="-size {0}".format(LARGE))

        self.entry.bind('<Return>', self.execute_search)

        self.entry.grid(row=0, padx=10, sticky=tk.E)
        # add the search button
        self.button = tk.Button(frame, text='Search',
                                command=self.execute_search,
                                font="-size {0}".format(LARGE))
        self.button.grid(row=0, column=1, padx=10, sticky=tk.W)

    def execute_search(self, event=None):
        """
        Event: start a search (and destory the autocomplete tab)
        Also updates the tables

        :param event: tk Event or None
        :return:
        """
        # destroy autocomplete box
        self.entry.destroy_tab()
        # get search text
        search_text = self.entry.get()
        # set searching text
        self.titlebar.title0.set('Please wait. Searching for: ')
        self.titlebar.title1.set(search_text)
        # search for entries
        found, r1, r2 = self.search_for_entry(search_text)
        # update tables
        self.update_tables(r1, r2)
        # set complete text
        if found:
            # log message to console
            wmsg = 'Complete. APERO code searched for:  {0}'
            wargs = [search_text]
            WLOG(self.dataobj.drs_params, '', wmsg.format(*wargs))
            # log to application
            self.titlebar.title0.set('Complete. APERO code searched for: ')
            self.titlebar.title1.set(search_text)
        else:
            # log message to console
            wmsg = 'Cannot find APERO code: {0}'
            wargs = [search_text]
            WLOG(self.dataobj.drs_params, '', wmsg.format(*wargs))
            # log to application
            self.titlebar.title0.set('Cannot find APERO code: ')
            self.titlebar.title1.set(search_text)

    def search_for_entry(self, value):
        """
        Search for a "value" in database (via self.dataobj)
        :param value: string, the value to search for
        :type value: str
        :returns: returns a tuple containing whether the "value" was found,
                  and the label/values dictionary for both tables (r1 and r2)
        :rtype: tuple[bool, dict, dict]
        """
        # set up dictionaries
        r1 = dict()
        r2 = dict()
        # ---------------------------------------------------------------------
        # set up label1
        r1['labels'] = ['Entry Sheet:', 'Error text:', 'Arguments:', 'Comment']
        # ---------------------------------------------------------------------
        found = False
        # get values 1 from dataobj.dict
        if value in self.dataobj.dict.keys():
            r1['values'] = [self.dataobj.source[value],
                            self.dataobj.dict[value],
                            self.dataobj.args[value],
                            self.dataobj.comments[value]]
            found = True
        else:
            r1['values'] = [''] * len(r1['labels'])
        # ---------------------------------------------------------------------
        # get values 2 from lines/ files
        if value in self.dataobj.lines.keys():

            files = self.dataobj.files[value]
            lines = self.dataobj.lines[value]
            labels, values = [], []
            # loop around files
            for it, filename in enumerate(files):
                labels += ['{0} Filename'.format(it + 1),
                           '{0} Line number'.format(it + 1)]
                values += [files[it], lines[it]]
            # set to r2
            r2['labels'] = labels
            r2['values'] = values
        else:
            r2['labels'] = ['Filename:', 'Line number:']
            r2['values'] = ['', '']
        # ---------------------------------------------------------------------
        # return r1 and r2
        return found, r1, r2

    def update_tables(self, r1, r2):
        """
        Updates the tables "r1" and "r2" with the dictionary values.
        First unpopulates table and then repopulates it with new data.

        :param r1: dictionary, the r1 parameter dictionary (labels and values)
                   to populate the table
        :param r2: dictionary, the r2 parameter dictionary (labels and values)
                   to populate the table
        :type r1: dict
        :type r2: dict
        :return: None
        """
        # destroy current entries
        self.rbox1.table.unpopulated_table()
        self.rbox2.table.unpopulated_table()
        # populate box1
        labels1 = r1['labels']
        values1 = r1['values']
        self.rbox1.table.populate_table(labels1, values1)
        # populate box2
        labels2 = r2['labels']
        values2 = r2['values']
        self.rbox2.table.populate_table(labels2, values2)


class SearchTitle:
    """
    Search title widget
    """

    def __init__(self, frame):
        """
        Search title widget constructor. Adds two labels that can be updated
        with calls to "self.title0" and "self.title1"

        :param frame: tk.Frame, the parent frame to attach this to
        :type: tk.Frame

        :return: None
        """
        self.title0 = tk.StringVar()
        self.title0.set(' ')
        self.title1 = tk.StringVar()
        self.title1.set(' ')
        self.frame = tk.Frame(frame)
        self.label0 = tk.Label(self.frame, textvariable=self.title0)
        self.label1 = tk.Label(self.frame, textvariable=self.title1)
        self.label0.pack()
        self.label1.pack()
        # add frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


class Results1:
    """
    The Results 1 (a.k.a r1) results widget

    This is the left side widget to hold one of the results table
    """

    def __init__(self, frame):
        """
        The r1 widget constructor. Adds internal frame and table widget
        :param frame: tk.Frame, the parent frame
        :type frame: tk.Frame

        :returns: None
        """
        # storage of table
        self.table = None
        # frame
        self.frame = tk.Frame(frame, borderwidth=1, relief=tk.SUNKEN,
                              bg='black')
        # add table
        self.result_entry(self.frame)
        # add frame
        self.frame.pack_propagate(0)
        self.frame.pack(expand=tk.YES, fill=tk.BOTH, padx=10, pady=10)

    def result_entry(self, frame):
        """
        Result table widget for r1
        :param frame: tk.Frame, the parent frame
        :type frame: tk.Frame

        :returns: None
        """
        labels = ['Entry Sheet:', 'Error text:', 'Arguments:', 'Comment']
        values = ['', '', '', '']
        self.table = None
        self.table = Table(frame, scroll=False)
        self.table.populate_table(labels, values)


class Results2:
    """
    The Results 2 (a.k.a r2) results widget

    This is the right side widget to hold one of the results table
    """

    def __init__(self, frame):
        """
        The r2 widget constructor. Adds internal frame and table widget
        :param frame: tk.Frame, the parent frame
        :type frame: tk.Frame

        :returns: None
        """
        self.table = None

        self.frame = tk.Frame(frame, borderwidth=1, relief=tk.SUNKEN,
                              bg='black')

        self.result_entry(self.frame)
        # add frame
        self.frame.pack_propagate(0)
        self.frame.pack(expand=tk.YES, fill=tk.BOTH, padx=10, pady=10)

    def result_entry(self, frame):
        """
        Result table widget for r2
        :param frame: tk.Frame, the parent frame
        :type frame: tk.Frame

        :returns: None
        """
        labels = ['1 Filename:', '1 Line number:']
        values = ['', '']

        self.table = Table(frame, scroll=True)
        self.table.populate_table(labels, values)


class Table:
    """
    Results Table widget
    """

    def __init__(self, frame, scroll):
        """
        Results table widget constructor. Chooses whether to add scroll bar
        If we add a scroll bar we have to use a canvas that is movable.

        :param frame: tk.Frame, the parent frame
        :param scroll: bool, whether or not to add a scroll bar (True = add)

        :type frame: tk.Frame
        :type scroll: bool

        :returns: None
        """
        if scroll:
            self.canvas = tk.Canvas(frame, bg='black')
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
            self.frame = tk.Frame(self.canvas)
            self.canvas_frame = self.canvas.create_window((4, 4),
                                                          window=self.frame)
            scrollbar = tk.Scrollbar(self.canvas, command=self.canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.canvas.bind('<Configure>', self.frame_width)
        else:
            self.frame = tk.Frame(frame, bg='black')
            self.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.values = []

    def on_frame_configure(self, event=None):
        """
        Event: Define the scroll region when <Configure> is used.
        :param event: tk.Event
        :return: None
        """
        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_mouse_scroll(self, event=None):
        """
        Event: Define the mouse scroll event and how to scroll
        :param event: tk.Event
        :return: None
        """
        if event.delta:
            self.canvas.yview_scroll(-1 * (event.delta / 120), 'units')
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1
            self.canvas.yview_scroll(move, 'units')

    def frame_width(self, event=None):
        """
        Event: Deal with the canvas width
        :param event: tk.Event
        :return: None
        """
        if event is None:
            canvas_width = self.canvas.winfo_width()
        else:
            canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def populate_table(self, labels, values):
        """
        Populate table with frames/labels/values from "labels" and "values"
        in a set of rows

        :param labels: list, the list of "category labels" - first row of each
                       element
        :param values: list, the list of "category values" - second row of
                       each element

        :type labels: list
        :type values: list

        :return: None
        """
        for it in range(len(labels)):
            fm = tk.Frame(self.frame, bg='black')

            text = tk.StringVar()
            text.set(values[it])
            self.values.append(text)

            fm1 = tk.Frame(fm, bg='black')
            fm2 = tk.Frame(fm, bg='white')

            l_a = WrappingLabel(fm1, text=labels[it])
            l_b = WrappingLabel(fm2, textvariable=text)

            l_a.config(bg='black', fg='white',
                       font="-size {0}".format(NORMAL))
            l_b.config(bg='white', fg='black',
                       font="-size {0}".format(SMALL))

            l_a.pack(side=tk.LEFT, fill=tk.X)
            l_b.pack(side=tk.LEFT, fill=tk.X)

            fm1.pack(expand=tk.YES, side=tk.TOP, fill=tk.X)
            fm2.pack(expand=tk.YES, side=tk.TOP, fill=tk.X)

            fm.pack(fill=tk.X, side=tk.TOP, padx=2)

    def unpopulated_table(self):
        """
        Unpopulate the table (with widget.destroy())

        :return: None
        """
        for widget in self.frame.winfo_children():
            widget.destroy()


class App(tk.Tk):
    """
    Main Application for error finder
    """

    def __init__(self, datastore, *args, **kwargs):
        """
        Main application constructor

        :param datastore: LoadData instance, storage of the indexed database
                          and python code line references
        :param args: arguments to pass to tk.Tk.__init__
        :param kwargs: keyword arguments to pass to tk.Tk.__init__

        :type datastore: LoadData

        :returns None:
        """
        # run the super
        tk.Tk.__init__(self, *args, **kwargs)
        # save datastore
        self.datastore = datastore
        # get the family font
        self.fontfamily = font.Font(font='TkTextFont').actual()['family']
        # set minimum size
        self.minsize(512, 360)
        # set application title
        self.title(PROGRAM_NAME)
        # update the height and width(s) - need to update idle tasks to make
        #   sure we have correct height/width
        self.update_idletasks()
        self.height = self.winfo_height()
        self.width = self.winfo_width()
        self.table_width = (self.width / 2) - 20
        # add full frames
        self.main_top = tk.Frame(self, borderwidth=1, relief=tk.GROOVE)
        self.main_middle = tk.Frame(self)
        self.main_bottom1 = tk.Frame(self, width=self.table_width)
        self.main_bottom2 = tk.Frame(self, width=self.table_width)
        # set the location of main frames
        self.main_top.grid(column=0, row=0, columnspan=2,
                           sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_middle.grid(column=0, row=1, columnspan=2,
                              sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_bottom1.grid(column=0, row=2, sticky=(tk.W, tk.S, tk.N, tk.E))
        self.main_bottom2.grid(column=1, row=2, sticky=(tk.W, tk.S, tk.N, tk.E))
        # get app elements
        self.navbar = Navbar(self)
        self.r1 = Results1(self.main_bottom1)
        self.r2 = Results2(self.main_bottom2)
        self.s1 = SearchTitle(self.main_middle)
        self.search = Search(self.main_top, self)
        # add menu master
        self.config(menu=self.navbar.menubar)
        # set up the grid weights (to make it expand to full size)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # bindings
        self.bind_all('<Configure>', self.r2.table.on_frame_configure)
        self.bind_all('<Button-4>', self.r2.table.on_mouse_scroll)
        self.bind_all('<Button-5>', self.r2.table.on_mouse_scroll)


# =============================================================================
# Worker functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    """
    Main function - takes the instrument name, index the databases and python
    script (in real time due to any changes in code) and then runs the
    application to find errors

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get datastore
    datastore = LoadData(params, instrument=recipe.instrument)
    WLOG(params, '', 'Running Error finding application')
    # Main code here
    app = App(datastore)
    app.geometry("1024x512")
    app.mainloop()
    # end with a log message
    WLOG(params, '', 'Program has completed successfully')
    # return a copy of locally defined variables in the memory
    return drs_startup.return_locals(params, locals())


class LoadData:
    """
    Object that indexes both the language databases and all drs python files
    (giving all line numbers and file references for every key in the language
    database)
    """

    def __init__(self, params, instrument=None, language=None):
        """
        LoadData constructor - loads both database and lines

        Stores database values in the following:
            - self.dict: dictionary, the printed error value
            - self.source: dictionary, the database source file
            - self.args: dictionary, the error value expected arguments
            - self.kinds: dictionary, the error value type
            - self.comments: dictionary, the error value comment

        Stores python script values in the following:
            - self.lines: dictionary, the line number references
            - self.files: dictionary, the file references

        :param instrument: string, the instrument name

        :type instrument: str
        """
        # set instrument
        self.instrument = instrument
        # deal with language
        if language is None:
            language = base.DEFAULT_LANG
        self.language = language
        self.drs_params = params
        # storage of outputs
        self.dict, self.source = None, None
        self.args, self.kinds, self.comments = None, None, None
        self.lines, self.files = None, None
        # update database
        self.update_database(self.instrument)

    def update_database(self, instrument):
        """
        Update the database with the given instrument

        :param instrument: string, the instrument name

        :type instrument: str
        """
        self.instrument = instrument
        # get database
        dout = self.load_databases()
        self.dict, self.source, self.args, self.kinds, self.comments = dout
        # find line numbers for all entries
        self.lines, self.files = self.load_lines()

    def load_databases(self):
        """
        Loads the language databases into dictionaries

        tuple returned:
            - dict: dictionary, the printed error value
            - source: dictionary, the database source file
            - args: dictionary, the error value expected arguments
            - kinds: dictionary, the error value type
            - comments: dictionary, the error value comment

        :return: a tuple of dictionaries
        :rtype: tuple[dict, dict, dict, dict, dict]
        """
        # get langudate database
        langdbm = drs_db.LanguageDatabase()
        # load database
        langdbm.load_db()
        # get language table name
        tablename = langdbm.database.tname
        # get pandas table
        df = langdbm.database.get('*', return_pandas=True)
        # storage
        values = dict()
        source = dict()
        args = dict()
        kinds = dict()
        comments = dict()
        # need to convert all to dictionary
        for row, key in enumerate(df['KEYNAME']):
            values[key] = df[self.language].iloc[row]
            source[key] = '{0}+{1}'.format(str(langdbm), tablename)
            args[key] = df['ARGUMENTS'].iloc[row]
            kinds[key] = df['KIND'].iloc[row]
            comments[key] = df['KEYDESC'].iloc[row]
        # return databases
        return values, source, args, kinds, comments

    def load_lines(self):
        """
        Loads the python script line number and file references into
        dictionaries

        tuple returned:
            - lines: dictionary, the line number references
            - files: dictionary, the file references

        :return: a tuple of dictionaries
        :rtype: tuple[dict, dict]
        """
        # log progress
        wmsg = 'Generating line list for instrument = "{0}"'
        WLOG(self.drs_params, 'info', wmsg.format(self.instrument))
        # get package (from drs_text)
        package = __PACKAGE__
        # get level above package
        modpath = drs_misc.get_relative_folder(package, '..')
        # get python scripts in modpath
        pyfiles = find_all_py_files(modpath)
        # open and combine in to single list of lines
        pargs = open_all_py_files(pyfiles)
        # -----------------------------------------------------------------
        # now search through pentry for each database entry
        lines = dict()
        files = dict()
        # loop through keys
        for it, key in enumerate(self.dict.keys()):
            # search for entry
            found, pnum, pfile = search_for_database_entry(key, *pargs)
            # if found add to storage
            if found:
                if key in lines:
                    lines[key] += pnum
                    files[key] += pfile
                else:
                    lines[key] = pnum
                    files[key] = pfile
        # return storage dictionaries
        return lines, files


def find_all_py_files(path):
    """
    Find all python files within a given path

    :param path: string, the path (including sub-directory) to search for
                 ".py" files
    :returns: a list of python file absolute paths
    :rtype: list[str]
    """
    # empty storage
    pyfiles = []
    # walk through path to file python files
    for root, dirs, files in os.walk(path, followlinks=True):
        for filename in files:
            if filename.endswith('.py'):
                pyfiles.append(os.path.join(root, filename))
    # return python files
    return np.sort(pyfiles)


def open_all_py_files(files):
    """
    Opens all python files (one by one) and adds info to lists

    list returned are:
    - python line text
    - python line numbers
    - python file source

    :param files: list of strings, the list of absolute paths to find
    :type files: list[str]

    :return: tuple of lists containing python script information
    :rtype: tuple[list[str], list[str], list[str]]
    """
    # get package and relative path to database (basaed on drs_text values)
    package = __PACKAGE__
    path = drs_misc.get_relative_folder(package, '..')
    # set up storage
    all_entries = []
    all_line_numbers = []
    all_filenames = []
    # loop around files
    for filename in files:
        # read the lines
        with open(filename, 'r') as f:
            flines = f.readlines()
        # add entries
        all_entries += flines
        # add line numbers
        all_line_numbers += list(np.arange(len(flines)))
        # get relative filepath (for printing)
        common = os.path.commonpath([filename, path]) + os.sep
        outfile = filename.split(common)[-1]
        all_filenames += [outfile] * len(flines)

    # return all entries/numbers and filenames
    return all_entries, all_line_numbers, all_filenames


def search_for_database_entry(key, entries, line_nums, files):
    """
    Searches for a key in "entries" and notes down the "line number" and
    "filename"

    :param key: string, the key to search for
    :param entries: list of strings, entries to search
    :param line_nums: list of integers, the line numbers for each entry
    :param files: list of strings, the file source for each entry

    :type key: str
    :type entries: list[str]
    :type line_nums: list[int]
    :type files: list[str]

    :returns: a tuple containing whether key was found, the line numbers and
    file references for all found entries for this key
    :rtype: tuple[bool, list[int], list[str]]
    """
    found_files, found_nums = [], []
    found = False
    # loop around entires and search for keys
    for it, entry in enumerate(entries):
        # if key in entry then we have found this entry (but need to check
        #    for multiple entries)
        if key in entry:
            found_files.append(files[it])
            found_nums.append(line_nums[it])
            found = True
    # return found params
    return found, found_nums, found_files


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run app
    ll = main()

# =============================================================================
# End of code
# =============================================================================
