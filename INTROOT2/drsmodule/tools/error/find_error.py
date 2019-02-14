#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-02-13 11:47
@author: ncook
Version 0.0.1
"""
import tkinter as tk
from tkinter.ttk import Progressbar

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = './'

DEBUG = True

# -----------------------------------------------------------------------------

# =============================================================================
# Define classes
# =============================================================================
class Navbar:
    def __init__(self, master):
        self.master = master
        self.menubar = tk.Menu(master)
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
        pass

    def quit(self):
        self.master.destroy()

    def open(self):
        pass

class Search:
    def __init__(self, parent, titlebar, rbox1, rbox2):
        self.frame = tk.Frame(parent)
        self.entry = None
        self.button = None
        self.titlebar = titlebar
        self.rbox1 = rbox1
        self.rbox2 = rbox2

        self.search_entry(self.frame)
        # add frame
        self.frame.pack( padx=10, pady=10)
        # set up the grid weights (to make it expand to full size)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)


    def search_entry(self, frame):

        # add the search box
        self.entry = tk.Entry(frame, width=64, background='white')
        self.entry.grid(row=0, padx=10, sticky=tk.E)
        if DEBUG:
            print('Making search entry')
        # add the search button
        self.button = tk.Button(frame, text='Search',
                                command=self.execute_search)
        self.button.grid(row=0, column=1, padx=10, sticky=tk.W)
        if DEBUG:
            print('Making search search button')

    def execute_search(self):
        if DEBUG:
            print('Searched for')
            print(self.entry.get())

        search_text = self.entry.get()

        # set searching text
        self.titlebar.title0.set('Please wait. Searching for: ')
        self.titlebar.title1.set(search_text)


        # search for entries
        r1, r2 = search_for_entry(search_text)

        # update tables
        self.update_tables(r1, r2)

        # set complet text
        self.titlebar.title0.set('Complete. Error text searched for: ')
        self.titlebar.title1.set(search_text)

    def update_tables(self, r1, r2):

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
    def __init__(self, frame):
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
    def __init__(self, frame):
        self.table = None
        self.frame = tk.Frame(frame, borderwidth=1, relief="sunken")
        self.result_entry(self.frame)
        # add frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


    def result_entry(self, frame):
        labels = ['Entry Sheet:', 'Error text:', 'Arguments:', 'Comment']
        values = ['', 'Test1', '', 'Test2']
        self.table = None
        self.table = Table(frame)
        self.table.populate_table(labels, values)


class Results2:
    def __init__(self, frame):
        self.frame = tk.Frame(frame, borderwidth=1, relief=tk.SUNKEN)
        self.result_entry(self.frame)
        # add frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def result_entry(self, frame):
        labels = ['Filename:', 'Line number:']
        values = ['', 'Really longgggggggggggggggggggg longgggggggggger '
                      '\nentryyyyyyyyyy']

        self.table = Table(frame)
        self.table.populate_table(labels, values)


class Table:
    def __init__(self, frame):
        self.frame = frame
        self.values = []

    def populate_table(self, labels, values):
        for it in range(len(labels)):
            fm = tk.Frame(self.frame)

            text = tk.StringVar()
            text.set(values[it])
            self.values.append(text)

            fm1, fm2 = tk.Frame(fm), tk.Frame(fm)
            l_a = tk.Label(fm1, text=labels[it])
            l_b = tk.Label(fm2, textvariable=text)
            l_a.pack(side=tk.LEFT, fill=tk.X)
            l_b.pack(side=tk.RIGHT, fill=tk.X)

            fm1.pack(expand=tk.YES, side=tk.TOP, fill=tk.X)
            fm2.pack(expand=tk.YES, side=tk.TOP, fill=tk.X)

            fm.pack(expand=tk.YES, fill=tk.X, side=tk.TOP, padx=2)

    def unpopulated_table(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # set minimum size
        self.minsize(512, 256)
        # set title
        self.title("Error locator")

        self.height = 512
        self.width = 512

        # add full frames
        self.main_top = tk.Frame(self, borderwidth=1, relief=tk.GROOVE)
        self.main_middle = tk.Frame(self)
        self.main_bottom1 = tk.Frame(self)
        self.main_bottom2 = tk.Frame(self)

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
        self.search = Search(self.main_top, self.s1, self.r1, self.r2)
        # add menu master
        self.config(menu=self.navbar.menubar)

        # set up the grid weights (to make it expand to full size)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


def main():
    # Main code here
    app = App()
    app.geometry("512x256")
    app.mainloop()
    return app


def search_for_entry(values):
    labels1 = ['Entry Sheet:', 'Error text:', 'Arguments:', 'Comment']
    labels2 = ['Filename:', 'Line number:']


    r1 = dict()
    r2 = dict()

    r1['labels'] = labels1
    r1['values'] = [values] * len(labels1)
    r2['labels'] = labels2
    r2['values'] = [values] * len(labels2)


    return r1, r2


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    ll = main()


# =============================================================================
# End of code
# =============================================================================