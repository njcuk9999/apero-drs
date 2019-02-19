#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-18 at 10:59

@author: cook
"""
import numpy as np
import os
from astropy.table import Table
from collections import OrderedDict
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from drsmodule import constants
from drsmodule import config
from drsmodule.locale import drs_text

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'file_explorer.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# -----------------------------------------------------------------------------
# define the program name
PROGRAM_NAME = 'DRS File Explorer'
# define the default path
ALLOWED_PATHS = ['DRS_DATA_WORKING', 'DRS_DATA_REDUC']
# Define allowed instruments
INSTRUMENTS = ['SPIROU', 'NIRPS']
# define min column length
MINLENGTH = 50
MAXLENGTH = 200

# =============================================================================
# Define new widgets
# =============================================================================
class DropDown(tk.OptionMenu):
    """
    Classic drop down entry

    Example use:
        # create the dropdown and grid
        dd = DropDown(root, ['one', 'two', 'three'])
        dd.grid()

        # define a callback function that retrieves the currently selected option
        def callback():
            print(dd.get())

        # add the callback function to the dropdown
        dd.add_callback(callback)
    """
    def __init__(self, parent, options: list, initial_value: str=None):
        """
        Constructor for drop down entry

        :param parent: the tk parent frame
        :param options: a list containing the drop down options
        :param initial_value: the initial value of the dropdown
        """
        self.var = tk.StringVar(parent)
        self.var.set(initial_value if initial_value else options[0])

        self.option_menu = tk.OptionMenu.__init__(self, parent, self.var,
                                                  *options)

        self.callback = None

    def add_callback(self, callback: callable):
        """
        Add a callback on change

        :param callback: callable function
        :return:
        """
        def internal_callback(*args):
            callback()

        self.var.trace("w", internal_callback)

    def get(self):
        """
        Retrieve the value of the dropdown

        :return:
        """
        return self.var.get()

    def set(self, value: str):
        """
        Set the value of the dropdown

        :param value: a string representing the
        :return:
        """
        self.var.set(value)


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


class LocationSection:

    def __init__(self, parent, master):
        self.master = master
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text='Location: ', anchor=tk.W)
        self.label.pack(side=tk.LEFT, anchor=tk.W)

        # define choices
        choices = []
        for path in ALLOWED_PATHS:
            choices.append(self.master.datastore.params[path])

        self.box = ttk.Combobox(self.frame, values=choices, state="readonly",
                                width=75)
        self.box.current(0)
        self.box.bind('<<ComboboxSelected>>', self.on_drop)
        self.box.pack(side=tk.LEFT, anchor=tk.W)

        # add frame
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                        side=tk.BOTTOM)

    def on_drop(self, *args):
        # get the value
        value = self.box.get()
        # update the data
        self.master.datastore.update_data(path=value)
        # unpopulate table
        self.master.table_element.unpopulate_table()
        self.master.table_element.populate_table()
        self.master.filter_element.remove_filters()
        self.master.filter_element.add_filters()


class FilterSection:
    def __init__(self, parent, master):
        self.master = master
        self.frame = tk.Frame(parent, relief=tk.SUNKEN)
        self.label = tk.Label(self.frame, text='Filters: ', anchor=tk.W)
        self.label.pack(side=tk.TOP, anchor=tk.W)
        # pack frame
        self.frame.pack(padx=10, pady=10, fill=tk.Y, side=tk.LEFT)
        # fill buttons
        self.add_filters()

    # def add_filters(self):
    #     # set up filter frame
    #     self.filter_frame = tk.Frame(self.frame)
    #     self.filter_frame.propagate(False)
    #     self.filter_frame.pack(padx=10, pady=10, fill=tk.Y, expand=tk.YES,
    #                            side=tk.LEFT)
    #     # get data and mask
    #     cols = self.master.datastore.cols
    #     sets = self.master.datastore.entries
    #     # grid depends on number of columns
    #     # rowlabels, collabels, rowbox, colbox = self.get_grid_positions()
    #
    #     # define dropdownbox storage
    #     self.boxes = dict()
    #     # loop around columns and add to filter grid
    #     for it, col in enumerate(cols):
    #         # set up choices and string variable
    #         choices = ['None'] + list(sets[col])
    #         label = tk.Label(self.filter_frame, text=col)
    #         dbox = DropDown(self.filter_frame, options=choices)
    #         # label.grid(row=rowlabels[it], column=collabels[it])
    #         # dbox.grid(row=rowbox[it], column=colbox[it])
    #         label.grid(row=it * 2, column=0)
    #         dbox.grid(row=(it * 2) + 1, column=0)
    #         dbox.add_callback(self.on_drop)
    #         self.boxes[col] = dbox

    def add_filters(self):
        # set up filter frame
        self.filter_frame = tk.Frame(self.frame)
        self.filter_frame.propagate(False)
        self.filter_frame.pack(padx=10, pady=10, fill=tk.Y, expand=tk.YES,
                               side=tk.LEFT)
        # get data and mask
        cols = self.master.datastore.cols
        sets = self.master.datastore.entries
        # grid depends on number of columns
        # rowlabels, collabels, rowbox, colbox = self.get_grid_positions()

        # define dropdownbox storage
        self.boxes = dict()
        # loop around columns and add to filter grid
        for it, col in enumerate(cols):
            # set up choices and string variable
            choices = ['None'] + list(sets[col])
            label = tk.Label(self.filter_frame, text=col)
            dbox = ttk.Combobox(self.filter_frame, values=choices,
                                state="readonly")
            dbox.current(0)
            label.grid(row=it * 2, column=0)
            dbox.grid(row=(it * 2) + 1, column=0)
            dbox.bind('<<ComboboxSelected>>', self.on_drop)
            self.boxes[col] = dbox

    def remove_filters(self):
        """
        Unpopulate the table (with widget.destroy())

        :return: None
        """
        for widget in self.frame.winfo_children():
            widget.destroy()

    def on_drop(self, *args):
        # get data and mask
        cols = self.master.datastore.cols
        for col in cols:
            value = self.boxes[col].get()
            if value is None or value == 'None':
                self.master.datastore.options[col] = None
            else:
                self.master.datastore.options[col] = [value]
        # update mask
        self.master.datastore.apply_filters()
        # unpopulate table
        self.master.table_element.unpopulate_table()
        self.master.table_element.populate_table()

    def get_grid_positions(self):
        FILTER_COLS = 6
        n_tot =len(self.master.datastore.cols)
        n_rows = int(np.ceil(n_tot / FILTER_COLS))
        # set up
        rowlabels = np.repeat(np.arange(0, n_rows), FILTER_COLS)
        collabels = np.tile(np.arange(0, FILTER_COLS * 2, 2), n_rows)
        rowboxs = np.repeat(np.arange(0, n_rows), FILTER_COLS)
        colboxs = np.tile(np.arange(1, FILTER_COLS * 2, 2), n_rows)

        # for it in range(n_tot):
        #      print(it, rowlabels[it], collabels[it], rowboxs[it], colboxs[it])

        # return
        return rowlabels, collabels, rowboxs, colboxs


class TableSection:
    def __init__(self, parent, master):
        self.master = master
        parent.update_idletasks()
        self.width = parent.winfo_width()
        self.frame = tk.Frame(parent)
        # pack frame
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                        side=tk.LEFT)

        self.label = tk.Label(self.frame, text='Table: ', anchor=tk.W)
        self.label.pack(side=tk.TOP, anchor=tk.W)
        # fill table
        self.populate_table()

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

    def populate_table(self):

        self.tableframe = tk.Frame(self.frame)
        self.tableframe.propagate(False)
        self.tableframe.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                             side=tk.TOP)
        # get data and mask
        data = self.master.datastore.data
        cols = self.master.datastore.cols
        mask = self.master.datastore.mask
        lens = self.master.datastore.lengths

        # figure out table size
        framewidth = self.width
        tablewidth = np.sum(list(lens.values()))
        scalefactor = framewidth/tablewidth
        # print(framewidth, tablewidth, scalefactor)

        # mask data
        masked_data = np.array(data)[mask]

        # make a style
        style = ttk.Style()
        style.configure('file_explorer.Treeview',
                        borderwidth=2,
                        relief=tk.SUNKEN)

        # make table
        self.tree = ttk.Treeview(self.tableframe, height=len(data),
                                 style=('file_explorer.Treeview'))

        ysb = ttk.Scrollbar(self.tableframe, orient='vertical',
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.tableframe, orient='horizontal',
                            command=self.tree.xview)

        self.tree.configure(yscrollcommand=lambda f, l: ysb.set,
                            xscrollcommand=lambda f, l: xsb.set)

        # set up columns
        self.tree['columns'] = cols
        for c_it, col in enumerate(cols):
            col_id = '#{0}'.format(c_it)
            self.tree.heading(col_id, text=col)
            colwidth = int(np.ceil(lens[col] * scalefactor)) * 10
            if colwidth > MAXLENGTH:
                colwidth = MAXLENGTH
            self.tree.column(col_id, minwidth=MINLENGTH, width=colwidth,
                             stretch=tk.YES)

        # insert data
        for row in range(len(masked_data)):

            tags = []
            if row % 2 == 0:
                tags.append("oddrow")
            else:
                tags.append("evenrow")

            self.tree.insert("", row, text=masked_data[row][0],
                             values=tuple(masked_data[row][1:]),
                             tags=tags)

        self.tree.tag_configure('oddrow', background='#E8E8E8')
        self.tree.tag_configure('evenrow', background='#99CCFF')

        ysb.pack(expand=tk.YES, fill=tk.Y, side=tk.RIGHT)
        xsb.pack(expand=tk.YES, fill=tk.X, side=tk.BOTTOM)
        self.tree.pack(fill=tk.BOTH)

    def unpopulate_table(self):
        """
        Unpopulate the table (with widget.destroy())

        :return: None
        """
        for widget in self.frame.winfo_children():
            widget.destroy()


class App(tk.Tk):
    """
    Main Application for file explorer
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
        # set minimum size
        self.minsize(512, 360)
        # set application title
        self.title(PROGRAM_NAME)
        # update the height and width(s) - need to update idle tasks to make
        #   sure we have correct height/width
        self.update_idletasks()
        self.height = self.winfo_height()
        self.width = self.winfo_width()
        # add full frames
        self.main_top = tk.Frame(self)
        self.main_middle = tk.Frame(self)
        self.main_bottom = tk.Frame(self)
        # set the location of main frames
        self.main_top.grid(column=0, row=0, columnspan=2,
                           sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_middle.grid(column=0, row=1, sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_bottom.grid(column=1, row=1, sticky=(tk.E, tk.W, tk.N, tk.S))

        # get app elements
        self.navbar = Navbar(self)
        self.loc_element = LocationSection(self.main_top, self)
        self.filter_element = FilterSection(self.main_middle, self)
        self.table_element = TableSection(self.main_bottom, self)
        # add menu master
        self.config(menu=self.navbar.menubar)
        # set up the grid weights (to make it expand to full size)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        #self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        # bindings
        # self.bind_all('<Configure>', self.table_element.on_frame_configure)
        # self.bind_all('<Button-4>', self.table_element.on_mouse_scroll)
        # self.bind_all('<Button-5>', self.table_element.on_mouse_scroll)


# =============================================================================
# Worker functions
# =============================================================================
def main(instrument=None):
    """
    Main function - takes the instrument name, index the databases and python
    script (in real time due to any changes in code) and then runs the
    application to find errors

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get parameters from drsmodule
    _, params = config.setup('None', instrument, quiet=True)
    # define allowed instruments
    if instrument not in INSTRUMENTS:
        emsgs = ['Instrument = "{0}" not valid.'.format(instrument),
                 '\nAllowed instruments: ']
        for instrument_option in INSTRUMENTS:
            emsgs.append('\n\t{0}'.format(instrument_option))
        WLOG(params, 'error', emsgs)
    # Log that we are running indexing
    WLOG(params, '', 'Indexing files at {0}'.format(params[ALLOWED_PATHS[0]]))
    # load data
    datastore = LoadData(instrument)
    # Log that we are running indexing
    WLOG(datastore.params, '', 'Running file explorer application')
    # Main code here
    app = App(datastore=datastore)
    app.geometry("1024x512")
    app.mainloop()
    # end with a log message
    WLOG(datastore.params, '', 'Program has completed successfully')
    # return a copy of locally defined variables in the memory
    return dict(locals())


class LoadData:
    def __init__(self, instrument):
        self.instrument = instrument
        # define empty storage
        self.params = None
        self.pconstant = None
        self.path = None
        self.index_filename = None
        self.index_files = []
        self.data = None
        self.mask = None
        self.cols = []
        self.entries = OrderedDict()
        self.lengths = OrderedDict()
        self.options = OrderedDict()
        # update data now
        self.update_data()

    def update_data(self, path=None):
        # empty storage
        self.params = None
        self.pconstant = None
        self.path = None
        self.index_filename = None
        self.index_files = []
        self.data = None
        self.mask = None
        self.cols = []
        self.entries = OrderedDict()
        self.lengths = OrderedDict()
        self.options = OrderedDict()
        # get parameters from drsmodule
        _, params = config.setup('None', self.instrument, quiet=True)
        self.params = params
        self.pconstant = constants.pload(self.instrument)
        # set path from parameters
        if path is None:
            self.path = self.params[ALLOWED_PATHS[0]]
        else:
            self.path = path
        self.index_filename = self.pconstant.INDEX_OUTPUT_FILENAME()
        # get index files
        self.get_index_files()
        # combine table
        self.combine_files()

    def get_index_files(self):
        # walk through all sub-directories
        for root, dirs, files in os.walk(self.path):
            # loop around files in current sub-directory
            for filename in files:
                # only save index files
                if filename == self.index_filename:
                    # append to storage
                    self.index_files.append(os.path.join(root, filename))

    def combine_files(self):
        # define storage
        storage = OrderedDict()
        storage['SOURCE'] = []
        # print that we are indexing
        print('Reading all index files (N={0})'.format(len(self.index_files)))
        # loop around file names
        for it, filename in enumerate(self.index_files):
            # get data from table
            data = Table.read(filename)
            # loop around columns and add to storage
            for col in data.colnames:
                if col not in storage:
                    storage[col] = list(np.array(data[col], dtype=str))
                else:
                    storage[col] += list(np.array(data[col], dtype=str))
            # full path
            abspath = os.path.dirname(filename)
            # get common source
            common = os.path.commonpath([abspath, self.path]) + os.sep
            outdir = filename.split(common)[-1]
            # remove the index filename
            outdir = outdir.split(self.index_filename)[0]
            # append source to file
            storage['SOURCE'] += [outdir] * len(data)
        # store storage as pandas dataframe
        self.data = pd.DataFrame(data=storage)

        self.clean_data = OrderedDict()

        self.mask = np.ones(len(self.data), dtype=bool)
        # get column names
        self.cols = list(self.data.columns)
        # get unique column entries
        for col in self.cols:
            # set the entries
            self.entries[col] = set(self.data[col])
            # set the lengths
            lengths = list(map(lambda x: len(str(x)), self.data[col]))
            self.lengths[col] = np.max([np.max(lengths), len(col)])
            # set the options
            self.options[col] = None
            # get clean data
            clean_list = list(map(self.clean, self.data[col]))
            self.clean_data[col] = np.array(clean_list)

    def clean(self, value):
        return str(value).upper().strip()

    def apply_filters(self):
        kwargs = self.options
        # filter
        self.mask = np.ones(len(self.data), dtype=bool)
        for kwarg in kwargs:
            if kwargs[kwarg] is not None:
                # get mask
                mask_k = np.zeros(len(self.data), dtype=bool)
                for element in kwargs[kwarg]:
                    if element is not None:
                        mask_k |= (self.clean_data[kwarg] == self.clean(element))
                self.mask &= mask_k


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run app
    ll = main('SPIROU')

# =============================================================================
# End of code
# =============================================================================
