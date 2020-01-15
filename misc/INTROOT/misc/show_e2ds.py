#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-11 11:47
@author: ncook
Version 0.0.1
"""
import tkinter
import numpy as np
import os
import sys
from astropy.io import fits
import matplotlib
matplotlib.use("TkAgg")
# noinspection PyPep8
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# noinspection PyPep8
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
# noinspection PyPep8
from matplotlib.figure import Figure


# =============================================================================
# Define variables
# =============================================================================
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'bob.txt'

PATH = '/home/ncook/Downloads/data_h4rg/reduced/AT5/20180409'

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    root = tkinter.Tk()
    root.title("Show E2DS SPIRou")
    root.resizable(True, True)

    # Add a grid
    mainframe = tkinter.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W,
                                            tkinter.E, tkinter.S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    mainframe.pack(pady=50, padx=50)

    # Create a Tkinter variable
    tkvar = tkinter.StringVar(root)
    tkvar2 = tkinter.StringVar(root)

    # Dictionary with options
    f = open(filename)
    lines = f.readlines()
    f.close()
    # clean lines
    choices = []
    for line in lines:
        if line.endswith('\n'):
            choices.append(line[:-1].strip())
        else:
            choices.append(line.strip())

    current_order = 0
    current_int = 0
    current_file = choices[current_int]

    tkvar.set(choices[current_int])  # set the default option
    filename = tkvar.get().strip()
    absfilename = os.path.join(PATH, filename)

    data = fits.getdata(absfilename)

    nbo, xdim = data.shape
    orders = np.arange(nbo)
    tkvar2.set(orders[current_order])

    popupMenu = tkinter.OptionMenu(mainframe, tkvar, *choices)
    tkinter.Label(mainframe, text="Choose a file").grid(row=1, column=1)
    popupMenu.grid(row=2, column=1, columnspan=4)

    orderMenu = tkinter.OptionMenu(mainframe, tkvar2, *orders)
    tkinter.Label(mainframe, text="Order:").grid(row=3, column=3)
    orderMenu.grid(row=3, column=4)

    f = Figure(figsize=(5, 5), dpi=100)
    a = f.add_subplot(111)
    a.plot(data[0])

    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH,
                                expand=True)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    # noinspection PyProtectedMember
    canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    # on change dropdown value
    # noinspection PyUnusedLocal
    def change_dropdown(*args):
        print(tkvar.get())
        filename1 = tkvar.get()
        plot_file(filename1, current_order)
        global current_file
        global current_int
        current_file = filename1
        current_int = choices.index(tkvar.get())


    # on change dropdown value
    # noinspection PyUnusedLocal
    def change_order(*args):
        order_num = tkvar2.get()
        filename1 = current_file
        plot_file(filename1, order_num)
        global current_order
        current_order = order_num


    # noinspection PyUnusedLocal
    def nextplot(*args):
        global current_int
        current_int += 1
        if current_int > len(choices) - 1:
            current_int = 0
        global current_file
        current_file = choices[current_int]
        plot_file(current_file, current_order)
        tkvar.set(current_file)


    # noinspection PyUnusedLocal
    def previousplot(*args):
        global current_int
        current_int -= 1
        if current_int < 0:
            current_int = len(choices) - 1
        global current_file
        current_file = choices[current_int]
        plot_file(current_file, current_order)
        tkvar.set(current_file)


    def plot_file(filename1, order_num):
        order_num = int(order_num)
        absfilename1 = os.path.join(PATH, filename1)
        try:
            data1 = fits.getdata(absfilename1)
            a.clear()
            a.plot(data1[order_num])
            title = '{0} Order={1}'.format(filename1, order_num)
            a.set_title(title)
            canvas.draw()
        except Exception as e:
            print('An error occured with file {0}'.format(filename1))
            print('Error was: {0}'.format(e))


    b1 = tkinter.Button(mainframe, text="Next", command=nextplot)
    b1.grid(row=3, column=2)

    b2 = tkinter.Button(mainframe, text="Previous", command=previousplot)
    b2.grid(row=3, column=1)

    # link function to change dropdown
    tkvar.trace('w', change_dropdown)
    tkvar2.trace('w', change_order)

    root.mainloop()

# =============================================================================
# End of code
# =============================================================================

# import matplotlib
#
# matplotlib.use("TkAgg")
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
#     NavigationToolbar2TkAgg
# from matplotlib.figure import Figure
#
# import tkinter as tk
# from tkinter import ttk
#
# LARGE_FONT = ("Verdana", 12)
#
#
# class SeaofBTCapp(tk.Tk):
#
#     def __init__(self, *args, **kwargs):
#         tk.Tk.__init__(self, *args, **kwargs)
#
#         #tk.Tk.iconbitmap(self, default="clienticon.ico")
#         tk.Tk.wm_title(self, "Sea of BTC client")
#
#         container = tk.Frame(self)
#         container.pack(side="top", fill="both", expand=True)
#         container.grid_rowconfigure(0, weight=1)
#         container.grid_columnconfigure(0, weight=1)
#
#         self.frames = {}
#
#         for F in (StartPage, PageOne, PageTwo, PageThree):
#             frame = F(container, self)
#
#             self.frames[F] = frame
#
#             frame.grid(row=0, column=0, sticky="nsew")
#
#         self.show_frame(StartPage)
#
#     def show_frame(self, cont):
#         frame = self.frames[cont]
#         frame.tkraise()
#
#
# class StartPage(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         label = tk.Label(self, text="Start Page", font=LARGE_FONT)
#         label.pack(pady=10, padx=10)
#
#         button = ttk.Button(self, text="Visit Page 1",
#                             command=lambda: controller.show_frame(PageOne))
#         button.pack()
#
#         button2 = ttk.Button(self, text="Visit Page 2",
#                              command=lambda: controller.show_frame(PageTwo))
#         button2.pack()
#
#         button3 = ttk.Button(self, text="Graph Page",
#                              command=lambda: controller.show_frame(PageThree))
#         button3.pack()
#
#
# class PageOne(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
#         label.pack(pady=10, padx=10)
#
#         button1 = ttk.Button(self, text="Back to Home",
#                              command=lambda: controller.show_frame(StartPage))
#         button1.pack()
#
#         button2 = ttk.Button(self, text="Page Two",
#                              command=lambda: controller.show_frame(PageTwo))
#         button2.pack()
#
#
# class PageTwo(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
#         label.pack(pady=10, padx=10)
#
#         button1 = ttk.Button(self, text="Back to Home",
#                              command=lambda: controller.show_frame(StartPage))
#         button1.pack()
#
#         button2 = ttk.Button(self, text="Page One",
#                              command=lambda: controller.show_frame(PageOne))
#         button2.pack()
#
#
# class PageThree(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
#         label.pack(pady=10, padx=10)
#
#         button1 = ttk.Button(self, text="Back to Home",
#                              command=lambda: controller.show_frame(StartPage))
#         button1.pack()
#
#         f = Figure(figsize=(5, 5), dpi=100)
#         a = f.add_subplot(111)
#         a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
#
#         canvas = FigureCanvasTkAgg(f, self)
#         canvas.show()
#         canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
#
#         toolbar = NavigationToolbar2TkAgg(canvas, self)
#         toolbar.update()
#         canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#
#
# app = SeaofBTCapp()
# app.mainloop()
