#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-18 11:25

@author: cook
"""
import numpy as np
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from pandastable import Table, TableModel, applyStyle
from pandastable import dialogs

from apero.base import base
from apero.core import constants
from apero.base import drs_db
from apero.tools.module.database import create_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.database.database_gui.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

Database = drs_db.Database
# Define an empty table
EMPTY_DATABASE = pd.DataFrame()
EMPTY_DATABASE['NONE'] = ['No data found']

# define database 1
DATABASE1 = TableModel.getSampleData()
# define database 2
DATABASE2 = pd.DataFrame()
DATABASE2['NUM'] = np.linspace(0, 1, 100)
DATABASE2['X'] = np.random.uniform(0, 1, size=100)
DATABASE2['Y'] = np.sin(np.exp(DATABASE2['X']))
DATABASE2['Z'] = np.random.uniform(0, 1, size=100) * DATABASE2['Y']
DATABASE2['USE'] = np.ones_like(DATABASE2['X']).astype(bool)


# =============================================================================
# Define classes
# =============================================================================
class DatabaseHolder:
    def __init__(self, name, path=None, df=None):
        self.name = name
        self.path = path
        self.df = df
        self.empty = False
        self.changed = False

    def load_dataframe(self):
        # if we already have the dataframe don't load it
        if isinstance(self.df, pd.DataFrame):
            return
        # if we don't have path we have a problem
        if self.path is None:
            emsg = 'Database "{0}" must have path or df set'
            raise ValueError(emsg.format(self.name))

        if self.path.endswith('.csv'):
            self.df = pd.read_csv(self.path)
            if len(self.df) == 0:
                self.df = None
                self.empty = True
        elif self.path.endswith('.db'):
            # start database
            database = Database(self.path)
            dataframe = database.get('*', table='MAIN', return_pandas=True)
            if len(dataframe) == 0:
                self.df = None
                self.empty = True
            if dataframe is None:
                self.df = None
                self.empty = True
            else:
                self.df = dataframe

    def save_dataframe(self, df):
        # if dataframe is None do nothing
        if df is None:
            return
        # start database
        database = Database(self.path)
        # push dataframe to replace SQL table
        database.add_from_pandas(df, if_exists='replace', index=False,
                                 commit=True)
        # print we are saving database
        print('Saving database {0}'.format(self.name))


class DatabaseTable(Table):
    def __init__(self, parent=None, **kwargs):
        Table.__init__(self, parent, **kwargs)
        self.table_changed = False

    def popupMenu(self, event, rows=None, cols=None, outside=None):
        """
        Same as parent just without file/edit/plot/table menus on right click
        :param event:
        :param rows:
        :param cols:
        :param outside:
        :return:
        """
        defaultactions = {
                        "Copy" : lambda: self.copy(rows, cols),
                        "Undo" : lambda: self.undo(),
                        #"Paste" : lambda: self.paste(rows, cols),
                        "Fill Down" : lambda: self.fillDown(rows, cols),
                        #"Fill Right" : lambda: self.fillAcross(cols, rows),
                        "Add Row(s)" : lambda: self.addRows(),
                        #"Delete Row(s)" : lambda: self.deleteRow(),
                        "Add Column(s)" : lambda: self.addColumn(),
                        "Delete Column(s)" : lambda: self.deleteColumn(),
                        "Clear Data" : lambda: self.deleteCells(rows, cols),
                        "Select All" : self.selectAll,
                        #"Auto Fit Columns" : self.autoResizeColumns,
                        "Table Info" : self.showInfo,
                        "Set Color" : self.setRowColors,
                        "Show as Text" : self.showasText,
                        "Filter Rows" : self.queryBar,
                        "New": self.new,
                        "Open": self.load,
                        "Save": self.save,
                        "Save As": self.saveAs,
                        "Import Text/CSV": lambda: self.importCSV(dialog=True),
                        "Export": self.doExport,
                        "Plot Selected" : self.plotSelected,
                        "Hide plot" : self.hidePlot,
                        "Show plot" : self.showPlot,
                        "Preferences" : self.showPreferences,
                        "Table to Text" : self.showasText,
                        "Clean Data" : self.cleanData,
                        "Clear Formatting" : self.clearFormatting,
                        "Undo Last Change": self.undo,
                        "Copy Table": self.copyTable,
                        "Find/Replace": self.findText}

        main = ["Copy", "Undo", "Fill Down", #"Fill Right",
                "Clear Data", "Set Color"]
        general = ["Select All", "Filter Rows",
                   "Show as Text", "Table Info", "Preferences"]

        def add_commands(fieldtype):
            """Add commands to popup menu for column type and specific cell"""
            functions = self.columnactions[fieldtype]
            for f in list(functions.keys()):
                func = getattr(self, functions[f])
                popupmenu.add_command(label=f, command= lambda : func(row,col))
            return

        popupmenu = tk.Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()

        if outside == None:
            #if outside table, just show general items
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
            def add_defaultcommands():
                """now add general actions for all cells"""
                for action in main:
                    if action == 'Fill Down' and (rows == None or len(rows) <= 1):
                        continue
                    if action == 'Fill Right' and (cols == None or len(cols) <= 1):
                        continue
                    if action == 'Undo' and self.prevdf is None:
                        continue
                    else:
                        popupmenu.add_command(label=action, command=defaultactions[action])
                return

            if coltype in self.columnactions:
                add_commands(coltype)
            add_defaultcommands()

        for action in general:
            popupmenu.add_command(label=action, command=defaultactions[action])

        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        applyStyle(popupmenu)
        return popupmenu

    def getaColor(self, oldcolor):
        # TODO: may be removed if bug in pandas table fixed (Issue #183)
        return dialogs.pickColor(self, oldcolor=oldcolor)

    def handleCellEntry(self, row, col):
        """Callback for cell entry"""
        super().handleCellEntry(row, col)
        self.table_changed = True

class DatabaseExplorer(tk.Frame):

    def __init__(self, parent=None, databases=None):

        # deal with database
        if databases is None:
            database1 = DatabaseHolder('DATABASE1', df=DATABASE1)
            database2 = DatabaseHolder('DATABASE2', df=DATABASE2)
            self.databases = dict()
            self.databases[database1.name] = database1
            self.databases[database2.name] = database2
        else:
            self.databases = databases
        # set parent if defined
        self.parent = parent
        # start the super frame instance
        tk.Frame.__init__(self)
        # set the master to main
        self.main = self.master
        # set default window size
        self.main.geometry('1024x512+512+256')
        # set title
        self.main.title('APERO Database Explorer')
        # deal with window closes
        self.main.protocol('WM_DELETE_WINDOW', self.on_exit)
        # deal with changes to any table
        self.table_change = False
        # make database selector frame
        self.make_selector()
        # set initial properties
        self.current_dataframe = None
        self.current_database_name = None
        self.has_data = False
        # start with database1
        databasehldr = self.databases[list(self.databases.keys())[0]]
        # set up storage for table models loaded into memory
        self.all_databases = dict()
        # set current database name
        self.current_database_name = databasehldr.name
        # load new database
        databasehldr.load_dataframe()
        # remake the new dataframe
        self.make_table(databasehldr.df)
        # make menu
        self.menu()
        # cannot make menu until table defined
        self.main.config(menu=self.menubar)

    def make_selector(self):
        self.selector_frame = tk.Frame(self.main)
        self.selector_frame.pack(fill=tk.X, anchor=tk.N)
        # add text box
        selector_text = tk.Label(self.selector_frame, text='Database: ')
        selector_text.pack(side=tk.LEFT)
        # get list of databases
        database_names = list(self.databases.keys())
        # add option box
        self.database_option = tk.StringVar(self.selector_frame)
        self.database_option.set(database_names[0])
        option_menu = tk.OptionMenu(self.selector_frame, self.database_option,
                                    *database_names)
        option_menu.pack(side=tk.LEFT)
        # deal with a change in value
        self.database_option.trace('w', self.change_table)

    def make_table(self, dataframe):
        self.current_dataframe = dataframe
        self.has_data = True
        self.table_frame = tk.Frame(self.main)
        self.table_frame.pack(fill=tk.BOTH, expand=1)
        if self.current_dataframe is None or len(self.current_dataframe) == 0:
            self.current_dataframe = EMPTY_DATABASE
            self.has_data = False
        kwargs = dict(dataframe=self.current_dataframe, showtoolbar=False,
                      showstatusbar=True)
        self.table = DatabaseTable(self.table_frame, **kwargs)
        self.table.show()

    def change_table(self, *args):
        # do not ask if no changes were made
        if self.table.table_changed:
            self.table_change = True
            # need to make sure the previous table has been marked as changed
            self.databases[self.current_database_name].changed = True
            # get dataframe back from model
            prev_df = pd.DataFrame(self.table.model.df)
            # need to add to all databases
            self.all_databases[self.current_database_name] = prev_df
        # get the new database (based on database_option selector)
        database_name = self.database_option.get()
        databasehldr = self.databases[database_name]
        # set current database name
        self.current_database_name = databasehldr.name
        # destroy frame
        self.table_frame.destroy()
        # load new database
        databasehldr.load_dataframe()
        # remake the new dataframe
        self.make_table(databasehldr.df)

    def update_database(self):
        # update table_change
        if self.table.table_changed:
            self.table_change = True
            # need to make sure the previous table has been marked as changed
            self.databases[self.current_database_name].changed = True
            # get dataframe back from model
            prev_df = pd.DataFrame(self.table.model.df)
            # need to add to all databases
            self.all_databases[self.current_database_name] = prev_df
        # do not update if no changes have been made
        if not self.table_change:
            return

        # warn user
        if self.update_warning():
            # loop around databases and update
            for database_name in self.databases:
                # get the database holder
                databasehldr = self.databases[database_name]
                # do not save over empty data
                if not databasehldr.changed:
                    continue
                # get updated data
                if database_name in self.all_databases:
                    dataframe = self.all_databases[database_name]
                    # save dataframe
                    databasehldr.save_dataframe(dataframe)
                    # now we have saved it mark it as not changed
                    databasehldr.changed = False
            # now we have updated we can set table_changes to False
            self.table_change = False


    def menu(self):

        # modified from Table.core populMenu
        defaultactions = {
                        "Undo" : lambda: self.table.undo(),
                        #"Fill Right" : lambda: self.fillAcross(cols, rows),
                        "Add Row(s)" : lambda: self.table.addRows(),
                        #"Delete Row(s)" : lambda: self.deleteRow(),
                        "Add Column(s)" : lambda: self.table.addColumn(),
                        "Delete Column(s)" : lambda: self.table.deleteColumn(),
                        "Select All" : self.table.selectAll,
                        #"Auto Fit Columns" : self.autoResizeColumns,
                        "Table Info" : self.table.showInfo,
                        "Set Color" : self.table.setRowColors,
                        "Show as Text" : self.table.showasText,
                        "Filter Rows" : self.table.queryBar,
                        "New": self.table.new,
                        "Open": self.table.load,
                        "Save": self.table.save,
                        "Save As": self.table.saveAs,
                        "Import Text/CSV": lambda: self.table.importCSV(dialog=True),
                        "Export": self.table.doExport,
                        "Plot Selected" : self.table.plotSelected,
                        "Hide plot" : self.table.hidePlot,
                        "Show plot" : self.table.showPlot,
                        "Preferences" : self.table.showPreferences,
                        "Table to Text" : self.table.showasText,
                        "Clean Data" : self.table.cleanData,
                        "Clear Formatting" : self.table.clearFormatting,
                        "Undo Last Change": self.table.undo,
                        "Copy Table": self.table.copyTable,
                        "Find/Replace": self.table.findText,
                        "Update Database": self.update_database}

        filecommands = ['Open','Import Text/CSV','Save','Save As','Export',
                        'Preferences']
        editcommands = ['Undo Last Change','Copy Table','Find/Replace',
                        'Filter Rows', 'Add Row(s)', 'Add Column(s)',
                        'Select All']
        plotcommands = ['Plot Selected','Hide plot','Show plot']
        tablecommands = ['Update Database', 'Table to Text','Clean Data',
                         'Clear Formatting', 'Table Info']

        # top level menu bar
        self.menubar = tk.Menu(self.main)

        def createSubMenu(parent, label, commands):
            menu = tk.Menu(parent, tearoff = 0)
            self.menubar.add_cascade(label=label,menu=menu)
            for action in commands:
                menu.add_command(label=action, command=defaultactions[action])
            return menu

        # create sub menus
        createSubMenu(self.menubar, 'File', filecommands)
        createSubMenu(self.menubar, 'Edit', editcommands)
        # createSubMenu(self.menubar, 'Plot', plotcommands)
        createSubMenu(self.menubar, 'Table', tablecommands)

    def update_warning(self) -> bool:
        # set up message box
        title = 'Update ALL SQL database(s)?'
        message = ('Are you sure you want to commit changes '
                   'to database (This is permanent)?')
        msgbox = messagebox.askquestion(title, message, icon='warning')
        # return a bool
        if msgbox == 'yes':
            return True
        else:
            return False

    def on_exit(self):
        # do not ask if no changes were made
        if self.table_change:
            # set up message box
            title = 'Exit without updating database?'
            message = ('Are you sure you want to exit without committing '
                       'changes to the SQL database?')
            msgbox = messagebox.askquestion(title, message, icon='warning')
            # only exit if yes
            if msgbox == 'yes':
                self.main.destroy()
        else:
            self.main.destroy()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":

    # get params
    # TODO: get instrument from args
    params = constants.load('SPIROU')
    # TODO: remove - for tests only
    params.set('CALIB_DB_NAME', value='calib.db')
    params.set('TELLU_DB_NAME', value='tellu.db')
    # get database paths
    paths = create_databases.list_databases(params)
    # push into database holder
    databases = dict()
    for key in paths:
        databases[key] = DatabaseHolder(key, path=paths[key])
    # construct app
    app = DatabaseExplorer(databases=databases)
    # launch the app
    app.mainloop()

# =============================================================================
# End of code
# =============================================================================
