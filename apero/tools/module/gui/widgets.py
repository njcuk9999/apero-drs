#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-02 12:51
@author: ncook
Version 0.0.1
"""
import os
import sys

# try to deal with python 2/3 compatibility
if sys.version_info.major > 2:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox
    import tkinter.font as tkFont
else:
    import Tkinter as tk
    import tkFont
    import ttk
    import tkFileFialog as filedialog

from PIL import Image, ImageTk

from apero.base import base
from apero .core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'file_explorer.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define widget classes
# =============================================================================
class DropDown(ttk.OptionMenu):
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
    def __init__(self, parent, options:list, initial_value:str=None):
        """
        Constructor for drop down entry

        :param parent: the tk parent frame
        :param options: a list containing the drop down options
        :param initial_value: the initial value of the dropdown
        """
        # must duplicate the first option
        options = [options[0]] + options
        self.var = tk.StringVar(parent)
        self.var.set(initial_value if initial_value else options[0])
        self.option_menu = ttk.OptionMenu.__init__(self, parent, self.var,
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


class StatusBar(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.frame = tk.Frame(self, relief=tk.SUNKEN)

        self.status=tk.StringVar()
        self.label=tk.Label(self.frame, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                           textvariable=self.status,
                           font=('arial',10,'normal'))
        self.status.set('')
        self.label.pack(side=tk.LEFT)

        self.frame.pack(fill=tk.X, expand=tk.YES, side=tk.BOTTOM)

        self.pack(fill=tk.X, expand=tk.YES, side=tk.BOTTOM)


class PageButtonPanel(ttk.Frame):
    def __init__(self, parent, number, controller):
        """

        :param parent:
        :param controller:

        controller must have the following attributes
            - current: int, the current page
            - num_pages: int, the number of pages
            - pages: list of page instances, the list of instances
            - close: method, method to close the application
        """
        ttk.Frame.__init__(self, parent)
        self.num_pages = controller.num_pages
        self.parent = parent
        self.controller = controller
        self.button_panel(number)

    def button_panel(self, number=0):
        if number != 0:
            self.button1 = ttk.Button(self, text='Previous',
                                      command=self.__previouspage)
            self.button1.grid(row=0, column=0)
        if number != (self.num_pages - 1):
            self.button2 = ttk.Button(self, text='Next',
                                      command=self.__nextpage)
            self.button2.grid(row=0, column=1)

        if number == (self.num_pages - 1):
            self.button3 = ttk.Button(self, text='Finish',
                                      command=self.controller.execute)
            self.button3.grid(row=0, column=2)

        # exit button
        self.button4 = ttk.Button(self, text='Exit',
                                  command=self.controller.close)
        self.button4.grid(row=0, column=3)

    def __nextpage(self):
        current = self.controller.current
        current += 1
        if current < 0:
            current = 0
        elif current > self.num_pages - 1:
            current = self.num_pages - 1
        self.controller.current = current
        self._goto_page(current)


    def __previouspage(self):
        current = self.controller.current
        current -= 1
        if current < 0:
            current = 0
        elif current > self.num_pages - 1:
            current = self.num_pages - 1
        self.controller.current = current
        self._goto_page(current)

    def _goto_page(self, page):
        self.controller.update()
        frame = self.controller.pages[page]
        frame.show()


class PageLogo(ttk.Frame):
    def __init__(self, parent, logo_path=None):
        # TODO: remove with full path
        if logo_path is None:
            IMAGEDIR = './tools/resources/images'
            logo_path = os.path.join(IMAGEDIR, 'terrapipe_logo.png')
        ttk.Frame.__init__(self, parent)
        self.image = Image.open(logo_path)
        self.logo = ImageTk.PhotoImage(master=self, image=self.image)
        self.label = tk.Label(self, image=self.logo, background='black')
        self.label.image = self.logo
        self.label.pack(fill='x')


class SettingsPage(ttk.Frame):
    def __init__(self, parent, settings_dict):
        # intialise scrolled window
        ttk.Frame.__init__(self, parent)
        # storage for outputs
        self.elements = dict()
        self.results = dict()
        # get list of settings name
        keys = list(settings_dict.keys())
        # for setting in settings
        for it, setting in enumerate(keys):
            # get properties for this setting
            props = settings_dict[setting]
            # get properties
            kind = props['kind']
            if kind == 'browse':
                element = BrowseSetting(self, props)
            elif kind == 'dropdown':
                element = DropDownSetting(self, props)
            elif kind == 'checkboxes':
                element = CheckBoxes(self, props)
            else:
                element = None
            # append element to list for later
            self.elements[setting] = element
            self.results[setting] = None
            # push into frame
            element.grid(row=it, column=0)

    def get_results(self):
        # loop around elements and update results
        for name in self.elements:
            # get element
            element = self.elements[name]
            self.results[name] = element.get()


class BrowseSetting(ttk.Frame):
    def __init__(self, parent, props):
        """

        :param parent:
        :param props: propeties

        properties requires the following keys:
            - keyword
            - default
            - comment
            - initialdir

        """
        ttk.Frame.__init__(self, parent)
        self.props = props
        self.keyword = props['keyword']
        self.default = props['default']
        self.comment = props['comment']
        self.rvalue = tk.StringVar(value=self.default)
        # set the comment
        comment = ttk.Label(self, text=self.comment)
        # set keyword
        label = ttk.Label(self, text='{0}:'.format(self.keyword))
        # set entry
        self.entry = ttk.Entry(self, textvariable=self.rvalue)
        # set button to browse
        button = ttk.Button(self, text='Browse', command=self.browse)
        # populate frame
        comment.grid(row=0, column=0, columnspan=3)
        label.grid(row=1, column=0)
        self.entry.grid(row=1, column=1)
        button.grid(row=1, column=2)

    def get(self):
        return self.rvalue.get()

    def browse(self):
        initialdir = self.props.get('initialdir', '/')
        directory = filedialog.askdirectory(initialdir=initialdir)
        self.rvalue.set(directory)


class DropDownSetting(ttk.Frame):
    def __init__(self, parent, props):
        ttk.Frame.__init__(self, parent)
        self.props = props
        self.keyword = props['keyword']
        self.options = props['options']
        self.comment = props['comment']
        if isinstance(self.options, str):
            self.options = [self.options]
        # set the comment
        comment = ttk.Label(self, text=self.comment)
        # set keyword
        label = ttk.Label(self, text='{0}:'.format(self.keyword))
        # set entry
        self.dropdown = DropDown(self, options=self.options)
        # populate frame
        comment.grid(row=0, column=0, columnspan=2)
        label.grid(row=1, column=0)
        self.dropdown.grid(row=1, column=1)

    def get(self):
        return self.dropdown.get()


class CheckBoxes(ttk.Frame):
    def __init__(self, parent, props):
        ttk.Frame.__init__(self, parent)
        self.props = props
        self.comment = props['comment']
        self.options = props['options']
        self.checkboxes = dict()

        if isinstance(self.options, str):
            self.options = [self.options]
        # set the comment
        comment = ttk.Label(self, text=self.comment)
        comment.grid(row=0, column=0, columnspan=2)
        # loop around check box options and add
        for it in range(len(self.options)):
            rvalue = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(self, text=self.options[it],
                                       variable=rvalue)
            checkbox.grid(row=it + 1, column=1)
            self.checkboxes[self.options[it]] = rvalue

    def get(self):
        values = dict()
        for option in self.options:
            rvalue = self.checkboxes[option]
            values[option] = rvalue.get()
        return values



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================