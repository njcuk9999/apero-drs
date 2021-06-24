#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-06-24

@author: cook
"""
import sys
import os
import tkinter as tk
from tkinter import Tk as ThemedTk
from tkinter import ttk
from ttkthemes import ThemedTk

from apero.base import base
from apero.base import drs_db
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.gui import gen_gui
from apero.tools.module.gui import widgets

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'gui.gen_gui.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get instrument names
INSTRUMENTS = base.INSTRUMENTS
# Get start page
StartPage = gen_gui.StartPage


# =============================================================================
# Define functions
# =============================================================================
class ManageTables(ThemedTk):
    def __init__(self, *args, **kwargs):
        # run the super
        ThemedTk.__init__(self, themebg=True)
        self.set_theme('plastik')
        # set minimum size
        self.minsize(1024, 768)
        # store options
        self.page_settings = dict()
        # this container contains all the pages
        container = tk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0,  weight=1)
        container.grid_columnconfigure(0, weight=1)
        # the pages
        self.current = 0
        self.all_pages = [Page1]
        self.num_pages = len(self.all_pages)
        self.pages = dict()
        for it, F in enumerate(self.all_pages):
            page = F(container, self)
            self.pages[it] = page
            page.grid(row=0, column=0, sticky="NSEW")
        # show the first page
        self.pages[0].show()

    def update(self):
        for page in self.pages:
            if hasattr(self.pages[page], 'settings'):
                self.pages[page].settings.get_results()
                # use results
                results = self.pages[page].settings.results
                for key in results:
                    self.page_settings[key] = results[key]

    def execute(self):
        self.update()
        print('Settings Entered:')
        for key in self.page_settings:
            print('\n{0} = {1}'.format(key, self.page_settings[key]))



        if 'delete' in self.page_settings:
            # get full list of tables (again)
            all_tables = get_db_tables()


            if len(self.page_settings['delete']) > 0:
                tables = self.page_settings['delete']

                for table in tables:
                    if table in all_tables:
                        # only delete those that are Tru
                        if tables[table]:
                            # TODO: warn user (pop up)

                            # TODO: delete table
                            pass



        self.close()

    def close(self):
        self.destroy()


class Page1(StartPage):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        # page logo
        self.logo = widgets.PageLogo(self, logo_path=None)
        # page content
        self.space1 = ttk.Label(self, text='')
        self.space2 = ttk.Label(self, text='')
        self.label = ttk.Label(self, text='Delete Tables')
        self.label.config(font=('times', '48'))

        settings_dict = dict()

        # get tables
        db_tables = get_db_tables()
        # add the setting
        settings_dict['delete'] = dict(comment='Delete tables:',
                                       options=db_tables,
                                       kind='checkboxes',
                                       keyword=db_tables)

        self.settings = widgets.SettingsPage(self, settings_dict)
        # button frame
        self.buttonframe = widgets.PageButtonPanel(self, 1, controller)
        # fix locations
        self.logo.grid(row=1, column=0, sticky='NSWE')
        self.space1.grid(row=2, column=0)
        self.label.grid(row=3, column=0, sticky='NS')
        self.space2.grid(row=4, column=0)
        self.settings.grid(row=5, column=0, sticky='NS')
        self.buttonframe.grid(row=6, column=0, sticky='S')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        controller.update()


def get_db_tables():
    # get the database settings
    dparams = base.DPARAMS
    # if we are dealing with mysql we have tables to delete
    if dparams['USE_MYSQL']:
        # get generic database access
        db = drs_db.database_wrapper('None', path='None')
        # get the tables
        db_tables = db.execute('SHOW TABLES;', fetch=True)
        # clean up the output
        out_tables = []
        for db_table in db_tables:
            out_tables.append(db_table[0])
        # return these tables
        return out_tables
    else:
        return []


def run_app():
    """
    Main function - takes the instrument name, index the databases and python
    script (in real time due to any changes in code) and then runs the
    application to find errors

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get parameters from apero
    recipe, params = drs_startup.setup('None', __INSTRUMENT__, quiet=True)
    # Log that we are running indexing
    WLOG(params, '', 'Running generic app')
    # Main code here
    app = ManageTables()
    app.geometry("1024x768")
    app.mainloop()

    llmain = dict(params=params)
    # return a copy of locally defined variables in the memory
    # return core.end_main(params, llmain, recipe, True)
    return app


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    ll = run_app()

# =============================================================================
# End of code
# =============================================================================
