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
import sys
import threading

# try to deal with python 2/3 compatibility
if sys.version_info.major > 2:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import tkinter.font as tkFont
else:
    import Tkinter as tk
    import tkFont
    import ttk

from terrapipe.core import constants
from terrapipe.core import math as mp
from terrapipe import core


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
WLOG = core.wlog
# -----------------------------------------------------------------------------
# define the program name
PROGRAM_NAME = 'DRS File Explorer'
# define the default path
ALLOWED_PATHS = ['DRS_DATA_WORKING', 'DRS_DATA_REDUC']
# Define allowed instruments
INSTRUMENTS = ['SPIROU', 'NIRPS']
# define min column length
MIN_TABLE_COL_WIDTH = 25
# TODO: This needs moving to some setup file to work per installation
DS9PATH = '~/bin/ds9/ds9'


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


class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.frame = tk.Frame(self, relief=tk.SUNKEN)

        self.status=tk.StringVar()
        self.label=tk.Label(self.frame, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                           textvariable=self.status,
                           font=('arial',10,'normal'))
        self.status.set('')
        self.label.pack(side=tk.LEFT)

        self.frame.pack(fill=tk.X, expand=tk.YES, side=tk.BOTTOM)

        self.pack(fill=tk.X, expand=tk.YES, side=tk.BOTTOM)


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
        # ---------------------------------------------------------------------
        # add file menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Quit', command=self.quit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.clickmenu = tk.Menu(self.menubar, tearoff=0)
        # ---------------------------------------------------------------------
        # add settings menu
        self.master.command_plot = tk.BooleanVar()
        self.master.command_ds9 = tk.BooleanVar()
        self.settingsmenu = tk.Menu(self.menubar, tearoff=0)
        self.settingsmenu.add_cascade(label='Select',
                                      menu=self.clickmenu)
        self.clickmenu.add_checkbutton(label='plot',
                                       onvalue=True,
                                       offvalue=False,
                                       variable=self.master.command_plot,
                                       command=self.activate_plot_check)
        self.clickmenu.add_checkbutton(label='ds9',
                                       onvalue=True,
                                       offvalue=False,
                                       variable=self.master.command_ds9,
                                       command=self.activate_ds9_check)
        self.menubar.add_cascade(label='Settings', menu=self.settingsmenu)
        # ---------------------------------------------------------------------
        # add help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='About', command=self.about)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

    def activate_plot_check(self):
        print('Clicked plot check')
        if self.master.command_plot.get():
            self.master.command_ds9.set(False)

    def activate_ds9_check(self):
        print('Clicked ds9 check')
        if self.master.command_ds9.get():
            self.master.command_plot.set(False)

    def about(self):
        """
        Make the about message box

        :return:
        """
        # set title
        abouttitle = 'About {0}'.format(PROGRAM_NAME)
        # write about message
        message = ('File Explorer for the DRS. \n'
                   'Choose the Location to explore (TMP or REDUCED) \n'
                   'Choose filters to filter the files by.')
        # make message box
        messagebox.showinfo(abouttitle, message)

    def quit(self):
        """
        Quits the app
        :return:
        """
        self.master.destroy()


class LocationSection:

    def __init__(self, parent, master):
        self.master = master
        # set up frames
        self.frame1 = tk.Frame(parent)
        self.frame2 = tk.Frame(parent)
        # -----------------------------------------------------------------
        # add instrument element
        self.label1 = tk.Label(self.frame1, text='Instrument: ',
                               anchor=tk.W)
        self.label1.pack(side=tk.LEFT, anchor=tk.W)
        # define choices
        choices = INSTRUMENTS
        self.box1 = ttk.Combobox(self.frame1, values=choices,
                                 state="readonly", width=20)
        self.box1.current(0)
        self.box1.bind('<<ComboboxSelected>>', self.on_drop_instrument)
        self.box1.pack(side=tk.LEFT, anchor=tk.W)
        # -----------------------------------------------------------------
        # add location element
        self.label2 = tk.Label(self.frame2, text='Location: ', anchor=tk.W)
        self.label2.pack(side=tk.LEFT, anchor=tk.W)
        # define choices
        choices = []
        for path in ALLOWED_PATHS:
            choices.append(self.master.datastore.params[path])
        self.box2 = ttk.Combobox(self.frame2, values=choices,
                                 state="readonly", width=75)
        self.box2.current(0)
        self.box2.bind('<<ComboboxSelected>>', self.on_drop_location)
        self.box2.pack(side=tk.LEFT, anchor=tk.W)
        # -----------------------------------------------------------------
        # add frames
        self.frame1.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                        side=tk.TOP)
        self.frame2.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                        side=tk.TOP)

    def on_drop_instrument(self, *args):
        # update status
        self.master.status_bar.status.set('Changing instruments...')
        # get the value
        value = self.box1.get()
        # update the data
        self.master.instrument = value
        self.master.datastore.instrument = value
        # update the instrument
        self.update_instrument()
        # unpopulate table
        if self.master.datastore.success:
            self.master.table_element.unpopulate_table()
            self.master.table_element.populate_table()
            self.master.filter_element.remove_filters()
            self.master.datastore.apply_filters()
            self.master.datastore.calculate_lengths()
            self.master.filter_element.add_filters()
        else:
            self.master.table_element.unpopulate_table()
            self.master.filter_element.remove_filters()

    def update_instrument(self):
        def update():
            print('UPDATE INSTRUMENT')
            self.master.datastore.get_data()
            self.master.datastore.combine_files()
        # update mask
        tprocess = threading.Thread(target=update)
        #self.master.config(cursor="wait")
        self.master.progress.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.master.progress.start()
        tprocess.start()
        while tprocess.is_alive():
            tprocess.join(0.1)
        #self.master.config(cursor="")
        self.master.progress.stop()
        self.master.progress.pack_forget()
        # reset status
        self.master.status_bar.status.set('')
        # set title
        self.master.set_title()

    def on_drop_location(self, *args):
        # update status
        self.master.status_bar.status.set('Changing locations...')
        # update the data
        self.update_location()
        # unpopulate table
        if self.master.datastore.success:
            self.master.table_element.unpopulate_table()
            self.master.table_element.populate_table()
            self.master.filter_element.remove_filters()
            self.master.datastore.apply_filters()
            self.master.datastore.calculate_lengths()
            self.master.filter_element.add_filters()
        else:
            self.master.table_element.unpopulate_table()
            self.master.filter_element.remove_filters()

    def update_location(self):
        # get the value
        value = self.box2.get()
        def update():
            print('UPDATE LOCATION')
            self.master.datastore.get_data(path=value)
            self.master.datastore.combine_files()
        # update mask
        tprocess = threading.Thread(target=update)
        #self.master.config(cursor="wait")
        self.master.progress.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.master.progress.start()
        tprocess.start()
        while tprocess.is_alive():
            self.master.progress.step(2)
            self.master.update_idletasks()
            tprocess.join(0.1)
        #self.master.config(cursor="")
        # reset status
        self.master.progress.stop()
        self.master.progress.pack_forget()
        self.master.status_bar.status.set('')


class FilterSection:
    def __init__(self, parent, master):
        self.master = master
        self.frame = tk.Frame(parent)
        # do not populate if datastore is empty
        if self.master.datastore.success:
            # -----------------------------------------------------------------
            self.label = tk.Label(self.frame, text='Filters: ', anchor=tk.W)
            self.label.pack(side=tk.TOP, anchor=tk.W)
            # fill buttons
            self.add_filters()
        # pack frame
        self.frame.pack(padx=10, pady=10, fill=tk.Y, side=tk.LEFT)

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
            choices = ['None'] + list(np.sort(list(sets[col])))
            label = tk.Label(self.filter_frame, text=col)
            dbox = ttk.Combobox(self.filter_frame, values=choices,
                                state="readonly")
            dbox.current(0)
            label.grid(row=it, column=0, sticky=tk.W)
            dbox.grid(row=it, column=1)
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
        # update status
        self.master.status_bar.status.set('Appying filters...')
        # get data and mask
        cols = self.master.datastore.cols
        for col in cols:
            value = self.boxes[col].get()
            if value is None or value == 'None':
                self.master.datastore.options[col] = None
            else:
                self.master.datastore.options[col] = [value]
        # update
        self.update_filters()
        # unpopulate table
        if self.master.datastore.success:
            self.master.table_element.unpopulate_table()
            self.master.table_element.populate_table()

    def update_filters(self):
        def update():
            print('UPDATE FILTERS')
            self.master.datastore.apply_filters()
            self.master.datastore.calculate_lengths()
        # update mask
        tprocess = threading.Thread(target=update)
        #self.master.config(cursor="wait")
        self.master.progress.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.master.progress.start()
        tprocess.start()
        while tprocess.is_alive():
            self.master.progress.step(2)
            self.master.update_idletasks()
            tprocess.join(0.1)
        #self.master.config(cursor="")
        self.master.progress.stop()
        self.master.progress.pack_forget()
        # reset status
        self.master.status_bar.status.set('')

    def get_grid_positions(self):
        FILTER_COLS = 6
        n_tot =len(self.master.datastore.cols)
        n_rows = int(np.ceil(n_tot / FILTER_COLS))
        # set up
        rowlabels = np.repeat(np.arange(0, n_rows), FILTER_COLS)
        collabels = np.tile(np.arange(0, FILTER_COLS * 2, 2), n_rows)
        rowboxs = np.repeat(np.arange(0, n_rows), FILTER_COLS)
        colboxs = np.tile(np.arange(1, FILTER_COLS * 2, 2), n_rows)
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
        # do not populate if datastore is empty
        if self.master.datastore.success:
            self.label = tk.Label(self.frame, text='Table: ', anchor=tk.W)
            self.label.pack(side=tk.TOP, anchor=tk.W)
            # fill table
            self.populate_table()

    def populate_table(self):

        self.tableframe = tk.Frame(self.frame)
        self.tableframe.propagate(False)
        self.tableframe.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.YES,
                             side=tk.TOP)
        # get data, cols and mask
        data = self.master.datastore.data
        cols = self.master.datastore.cols
        mask = self.master.datastore.mask
        # ---------------------------------------------------------------------
        # work out the column widths
        max_column_widths = self.get_widths()
        # ---------------------------------------------------------------------
        # mask data
        masked_data = np.array(data)[mask]
        # make a style for the table
        style = ttk.Style()
        style.configure('file_explorer.Treeview',
                        borderwidth=2,
                        relief=tk.SUNKEN)
        # ---------------------------------------------------------------------
        # make table
        self.tree = ttk.Treeview(self.tableframe, height=len(data),
                                 style=('file_explorer.Treeview'))
        # ---------------------------------------------------------------------
        # add scroll bar
        ysb = ttk.Scrollbar(self.tableframe, orient='vertical',
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.tableframe, orient='horizontal',
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set,
                            xscrollcommand=xsb.set)
        # ---------------------------------------------------------------------
        # set up columns
        self.tree['columns'] = [''] + list(cols)
        # add id column
        self.tree.heading('#0')
        self.tree.column('#0', stretch=tk.NO, width=50)
        # add data columns
        for c_it, col in enumerate(list(cols)):
            col_id = '#{0}'.format(c_it + 1)
            self.tree.heading(col_id, text=col)
            self.tree.column(col_id, stretch=tk.YES,
                             width=max_column_widths[c_it])
        # ---------------------------------------------------------------------
        # insert data
        for row in range(len(masked_data)):

            tags = []
            if row % 2 == 0:
                tags.append("oddrow")
            else:
                tags.append("evenrow")

            self.tree.insert("", row, text=str(row),
                             values=tuple(masked_data[row]),
                             tags=tags)
        # ---------------------------------------------------------------------
        # style for tagged elements
        self.tree.tag_configure('oddrow', background='#E8E8E8')
        self.tree.tag_configure('evenrow', background='#99CCFF')
        # ---------------------------------------------------------------------
        # pack into frame
        ysb.pack(fill=tk.Y, side=tk.RIGHT)
        xsb.pack(fill=tk.X, side=tk.BOTTOM)
        self.tree.pack(fill=tk.BOTH)

        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        # get data, cols and mask
        data = np.array(self.master.datastore.data)
        mask = self.master.datastore.mask
        path = self.master.datastore.path
        # ---------------------------------------------------------------------
        # get item
        item = self.tree.identify('item', event.x, event.y)
        rownumber = self.tree.item(item, 'text')
        # ---------------------------------------------------------------------
        # try to get absolute path
        try:
            row = int(rownumber)
            night = data[mask][row][0]
            filename = data[mask][row][1]
            # check path exists
            if os.path.exists(filename):
                abspath = filename
            elif os.path.exists(os.path.join(night, filename)):
                abspath = os.path.join(night, filename)
            elif os.path.exists(os.path.join(path, night, filename)):
                abspath = os.path.join(path, night, filename)
            else:
                emsg = 'Could not construct filename from {0}/{1}/{2}'
                eargs = [path, night, filename]
                raise ValueError(emsg.format(*eargs))
        except Exception as e:
            print('Error constructing absolute path for row={0}'
                  ''.format(rownumber))
            print('\tError {0}: {1}'.format(type(e), e))
            return 0
        # ---------------------------------------------------------------------
        # if open in ds9 open in ds9
        if self.master.command_ds9.get():
            self.open_ds9(abspath)
        if self.master.command_plot.get():
            self.open_plot(abspath)

    def open_ds9(self, abspath):
        # update status
        self.master.status_bar.status.set('Opening DS9...')
        # construct command
        ds9path = DS9PATH
        command = '{0} {1} &'.format(ds9path, abspath)
        try:
            os.system(command)
        except Exception as e:
            print('Cannot run command:')
            print('\t{0}'.format(command))
            print('\tError {0}: {1}'.format(type(e), e))
        # reset status
        self.master.status_bar.status.set('')

    # TODO: Move plot to plotting
    def open_plot(self, abspath):
        # update status
        self.master.status_bar.status.set('Opening Plot interface...')
        try:
            import matplotlib.pyplot as plt
            from astropy.io import fits
            data = fits.getdata(abspath)
            plt.imshow(data, origin='lower', aspect='auto')
            plt.show()
            plt.close()
        except Exception as e:
            print('Error cannot plot {0}'.format(abspath))
            print('\tError {0}: {1}'.format(type(e), e))
        # reset status
        self.master.status_bar.status.set('')

    def get_widths(self):
        cols = self.master.datastore.cols
        lens = self.master.datastore.lengths
        # define font
        self.myFont = tkFont.Font(self.frame, font='TkDefaultFont')
        # loop around columns and work out width
        max_column_widths = [0] * len(cols)

        for it, col in enumerate(cols):
            test_string = '_'*lens[col]
            new_length1 = self.myFont.measure(str(test_string))
            new_length2 = self.myFont.measure(str(col))
            new_length3 = MIN_TABLE_COL_WIDTH
            new_length = mp.nanmax([new_length1, new_length2, new_length3])
            if new_length > max_column_widths[it]:
                max_column_widths[it] = int(new_length * 1.10)
        return max_column_widths

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

        # self.style = ttk.Style()
        # self.style.theme_use('alt')
        # set minimum size
        self.minsize(1024, 768)
        # set application title
        self.set_title()
        # update the height and width(s) - need to update idle tasks to make
        #   sure we have correct height/width
        self.update_idletasks()
        self.height = self.winfo_height()
        self.width = self.winfo_width()
        # ---------------------------------------------------------------------
        # add full frames
        self.main_top = tk.Frame(self)
        self.main_middle = tk.Frame(self, relief=tk.RAISED)
        self.main_bottom = tk.Frame(self)
        self.main_end = tk.Frame(self)
        # ---------------------------------------------------------------------
        # set the location of main frames
        self.main_top.grid(column=0, row=0, columnspan=2,
                           sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_middle.grid(column=0, row=1, sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_bottom.grid(column=1, row=1, sticky=(tk.E, tk.W, tk.N, tk.S))
        self.main_end.grid(column=0, row=2, columnspan=2,
                           sticky=(tk.E, tk.W, tk.N, tk.S))
        # ---------------------------------------------------------------------
        # add status bar
        self.status_bar = StatusBar(self.main_end)
        # ---------------------------------------------------------------------
        # add progress bar to status bar
        self.progress = ttk.Progressbar(self.status_bar.frame,
                                        orient=tk.HORIZONTAL,
                                        mode='indeterminate')
        # add nav bar
        self.navbar = Navbar(self)
        # add menu master
        self.config(menu=self.navbar.menubar)
        # ---------------------------------------------------------------------
        # set up the grid weights (to make it expand to full size)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        #self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        # ---------------------------------------------------------------------
        # save datastore
        self.datastore = datastore
        # now load in the data
        self.update_data()
        # set the instrument
        self.instrument = self.datastore.instrument
        # set application title
        self.set_title()
        # add other elements
        self.loc_element = LocationSection(self.main_top, self)
        self.filter_element = FilterSection(self.main_middle, self)
        self.table_element = TableSection(self.main_bottom, self)

        self.frames = [self.main_middle, self.main_bottom]


    def set_title(self):
        if hasattr(self, 'instrument'):
            self.title('{0} ({1})'.format(PROGRAM_NAME, self.instrument))
        else:
            self.title('{0}'.format(PROGRAM_NAME))

    def update_data(self):
        # update status
        self.status_bar.status.set('Loading data...')
        def update():
            print('UPDATE DATA')
            # update data now
            self.datastore.get_data()
            # combine table
            self.datastore.combine_files()
        # update mask
        tprocess = threading.Thread(target=update)
        #self.config(cursor="wait")
        tprocess.start()
        self.progress.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.progress.start()
        while tprocess.is_alive():
            self.progress.step(2)
            self.update_idletasks()
            tprocess.join(0.1)
        #self.config(cursor="")
        # finish
        self.progress.stop()
        self.progress.pack_forget()
        # reset status
        self.status_bar.status.set('')


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
    # get parameters from terrapipe
    _, params = core.setup('None', instrument, quiet=True)
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
    WLOG(params, '', 'Running file explorer application')
    # Main code here
    app = App(datastore=datastore)
    app.geometry("1024x768")
    app.mainloop()
    # end with a log message
    WLOG(datastore.params, '', 'Program has completed successfully')
    # return a copy of locally defined variables in the memory
    return core.return_locals(params, locals())


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
        self.success = False

    def get_data(self, path=None):
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
        # get parameters from terrapipe
        _, params = core.setup('None', self.instrument, quiet=True)
        self.params = params
        self.pconstant = constants.pload(self.instrument)
        # set path from parameters
        if (path is None) and (self.path is None):
            self.path = self.params[ALLOWED_PATHS[0]]
        elif (path is None) and (self.path is not None):
            pass
        else:
            self.path = path
        self.index_filename = self.pconstant.INDEX_OUTPUT_FILENAME()
        # get index files
        self.get_index_files()

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

        # deal with column names being different lengths
        current_length = 0
        for col in storage.keys():
            if current_length == 0:
                current_length = len(storage[col])
            if len(storage[col]) != current_length:
                print('Index columns have wrong lengths')
                self.data = None
                self.clean_data = OrderedDict()
                self.mask = None
                self.cols = []
                self.success = False
                return 0

        # store storage as pandas dataframe
        self.data = pd.DataFrame(data=storage)

        self.clean_data = OrderedDict()

        self.mask = np.ones(len(self.data), dtype=bool)
        # get column names
        self.cols = list(self.data.columns)
        # get unique column entries
        for col in self.cols:
            # get clean data
            clean_list = list(map(self.clean, self.data[col]))
            self.clean_data[col] = np.array(clean_list)
            # set the entries
            self.entries[col] = set(np.array(clean_list))
            # set the options
            self.options[col] = None

        # calculate lengths
        self.calculate_lengths()
        # mark as successful if we have 1 or more rows
        if len(self.data) > 0:
            self.success = True
        else:
            self.success = False

    def calculate_lengths(self):
        # mask data with current mask
        print('Number Masked = {0}'.format(np.sum(self.mask)))
        masked_data = self.data[self.mask]
        # loop through columns and update self.lengths
        for col in self.cols:
            # set the lengths
            clens = list(map(lambda x: len(str(x)), masked_data[col]))

            if len(clens) == 0:
                self.lengths[col] = 0
            else:
                self.lengths[col] = mp.nanmax([mp.nanmax(clens), len(col)])

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
