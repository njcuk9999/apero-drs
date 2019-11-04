#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-02 10:11
@author: ncook
Version 0.0.1
"""
import sys
import os

if sys.version_info.major == 3:
    import tkinter as tk
    from tkinter import Tk as ThemedTk
    from tkinter import ttk
else:
    import Tkinter as tk
from ttkthemes import ThemedTk


from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.tools.module.gui import widgets

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'gui.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict

INSTRUMENTS = ['SPIROU', 'NIRPS']



# =============================================================================
# Define classes
# =============================================================================
class TestApp(ThemedTk):
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
        self.all_pages = [Page1, Page2, Page3]
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
                results = self.pages[page].settings.results
                for key in results:
                    self.page_settings[key] = results[key]

    def execute(self):

        print('Settings Entered:')
        for key in self.page_settings:
            print('\n{0} = {1}'.format(key, self.page_settings[key]))
        self.close()

    def close(self):
        self.destroy()


class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

    def show(self):
        self.tkraise()


class Page1(StartPage):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        # page logo
        self.logo = widgets.PageLogo(self, logo_path=None)
        # page content
        self.label = ttk.Label(self, text='This is page 1', background='white')
        # button frame
        self.buttonframe = widgets.PageButtonPanel(self, 0, controller)
        # fix locations
        self.logo.grid(row=1, column=0, sticky='NSWE')
        self.label.grid(row=2, column=0, sticky='NSWE')
        self.buttonframe.grid(row=3, column=0, sticky='S')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        controller.update()


class Page2(StartPage):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        # page logo
        self.logo = widgets.PageLogo(self, logo_path=None)
        # page content
        self.space1 = ttk.Label(self, text='')
        self.space2 = ttk.Label(self, text='')
        self.label = ttk.Label(self, text='General Settings')
        self.label.config(font=('times', '48'))

        settings_dict = dict()
        settings_dict['uconfig'] = dict(name='uconfig',
                                      kind='browse',
                                      keyword='DRS_UCONFIG',
                                      default='~',
                                      comment='User config path',
                                      initialdir='~')

        settings_dict['instruments'] = dict(name='instruments',
                                            kind='checkboxes',
                                            options=INSTRUMENTS,
                                            comment='Choose instruments:')
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


class Page3(StartPage):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        # page logo
        self.logo = widgets.PageLogo(self, logo_path=None)
        # page content
        self.space1 = ttk.Label(self, text='')
        self.space2 = ttk.Label(self, text='')
        self.label = ttk.Label(self, text='Settings')
        self.label.config(font=('times', '48'))

        settings_dict = dict()
        settings_dict['path1'] = dict(name='path1',
                                      kind='browse',
                                      keyword='DRS_PATH1',
                                      default='/',
                                      comment='Set default path 1',
                                      initialdir='/')
        settings_dict['path2'] = dict(name='path2',
                                      kind='browse',
                                      keyword='DRS_PATH2',
                                      default='/',
                                      comment='Set default path 2',
                                      initialdir='/')
        settings_dict['plot1'] = dict(name='plot1',
                                      kind='dropdown',
                                      keyword='DRS_PLOT',
                                      options=['a', 'b', 'c'],
                                      comment='Set the plotting option')
        self.settings = widgets.SettingsPage(self, settings_dict)
        # button frame
        self.buttonframe = widgets.PageButtonPanel(self, 2, controller)
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


# =============================================================================
# Define functions
# =============================================================================
def test(instrument=None):
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
    recipe, params = core.setup('None', instrument, quiet=True)
    # Log that we are running indexing
    WLOG(params, '', 'Running file explorer application')
    # Main code here
    app = TestApp()
    app.geometry("1024x768")
    app.mainloop()

    llmain = dict(params=params)
    # return a copy of locally defined variables in the memory
    # return core.end_main(params, llmain, recipe, True)
    return app



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main with no arguments (get from command line - sys.argv)
    ll = test()

# =============================================================================
# End of code
# =============================================================================