#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-22

@author: cook
"""
import numpy as np
import warnings

import bokeh
from bokeh.themes import built_in_themes
from bokeh.io import curdoc, show, output_file
from bokeh.plotting import figure
from bokeh.layouts import grid, row, column
from bokeh.models import HoverTool, CheckboxButtonGroup
from bokeh.models import ColumnDataSource, Slider, TextInput, Button
from bokeh.models import Range1d, Dropdown

from apero.core import constants
from apero.core import math as mp
from apero.tools.module.visulisation import visu_core


# =============================================================================
# Define variables
# =============================================================================
DEBUG = True
# get params
PARAMS = constants.load()
# get pseudo constants
PCONST = constants.pload()
# get fibers
scifibers, reffibers = PCONST.FIBER_KINDS()


# =============================================================================
# Define test functions
# =============================================================================
def test_plot(**kwargs) -> bokeh.models.Model:
    plot1 = figure(height=400, width=800,
                   tools="crosshair,pan,reset,save,wheel_zoom",
                   x_range=[0, 4 * np.pi], y_range=[-2.5, 2.5])

    x = np.arange(-10, 10, 0.1)
    plot1.circle(x=x, y=x**kwargs['power'])
    plot1.xaxis.axis_label = kwargs['xlabel']
    plot1.yaxis.axis_label = kwargs['ylabel']

    return grid([plot1])


# =============================================================================
# Define e2ds plotter
# =============================================================================
class SpectrumPlot:
    def __init__(self, figure):
        # figure this is part of
        self.figure = figure
        # values to change by the user
        self.obs_dir = '2020-08-31'
        self.identifier = '2510303o'
        self.order_num = 0
        self.fiber = scifibers[0]
        # line variables
        self.line_bkind = ['red', 'red', 'red', 'red']
        self.line_labels = ['e2ds', 'tcorr', 'recon', 'skymodel']
        self.line_otypes = ['EXT_E2DS_FF', 'TELLU_OBJ', 'TELLU_RECON',
                            'TELLU_PCLEAN']
        self.line_norm = ['med', 'med', None, 'max']
        self.line_blaze_cor = [True, True, False, False]
        self.line_oext = [1, 1, 1, 4]
        self.line_active = [1, 0, 0, 0]
        self.line_colors = ['black', 'red', 'blue', 'orange']
        self.line_alphas = [0.5, 0.5, 0.5, 0.5]
        self.line_dc = [0, 0, 0, 1]
        self.lines = [None, None, None, None]
        self.source = ColumnDataSource()

        # widgets
        self.obs_dir_widget = None
        self.identifier_widget = None
        self.lines_widget = None
        self.order_num_widget = None
        self.widgets = []
        # other variables
        self.fibers = scifibers + [reffibers]
        self.order_max = PARAMS['FIBER_MAX_NUM_ORDERS_A']
        self.xmin = 0
        self.xmax = 1
        self.ymin = 0
        self.ymax = 1
        # whether we currently have identifier loaded
        self.loaded = ''

        self.valid = False
        # create the graph
        self.create()

    def create(self):
        # ---------------------------------------------------------------------
        # create obs dir text widget
        self.obs_dir_widget = TextInput(title='OBS_DIR', value=self.obs_dir)
        #self.obs_dir_widget.on_change('value', self.update_graph)
        # ---------------------------------------------------------------------
        # create identifier text widget
        self.identifier_widget = TextInput(title='ID', value=self.identifier)
        #self.identifier_widget.on_change('value', self.update_graph)
        # ---------------------------------------------------------------------
        # create widget for order number
        self.order_num_widget = Slider(title='Order No.', value=self.order_num,
                                       start=0, end=self.order_max, step=1)
        # self.order_num_widget.on_change('value', self.update_graph)
        # ---------------------------------------------------------------------
        fiber_menu = []
        for fiber in self.fibers:
            fiber_menu.append((fiber, fiber))
        self.dropdown_widget = Dropdown(label='Fiber', button_type='primary',
                                        menu=fiber_menu)
        self.dropdown_widget.on_click(self.update_fiber)
        # ---------------------------------------------------------------------
        # create a button to update graph
        self.button = Button(label='Update', button_type='success')
        self.button.on_click(self.update_graph_on_click)
        # ---------------------------------------------------------------------
        # create lines checkbox group widget
        self.lines_widget = CheckboxButtonGroup(labels=self.line_labels,
                                                active=self.line_active)
        self.lines_widget.on_change('active', self.update_active)
        # ---------------------------------------------------------------------
        self.widgets = [self.obs_dir_widget, self.identifier_widget,
                        self.order_num_widget, self.dropdown_widget,
                        self.button,  self.lines_widget]
        # update graph now
        self.update_graph()

    def update_fiber(self, event):
        self.fiber = event.item

    def update_active(self, attrname, old, new):
        _ = attrname, old, new
        self.update_line_visibility()

    def update_graph_on_click(self):
        self.update_graph()

    def update_graph(self):
        # _ = attrname, old, new

        # update values from widgets
        self.identifier = str(self.identifier_widget.value)
        self.obs_dir = str(self.obs_dir_widget.value)
        self.order_num = int(self.order_num_widget.value)

        if DEBUG:
            out = dict(idenfier=self.identifier, obs_dir=self.obs_dir,
                       order_num=self.order_num, fiber=self.fiber)
            print('Update')
            print(out)

        # if identifier is the same as loaded we just check line visibility
        if self.identifier != self.loaded or not self.valid:
            self.update_files()
        # update line visibility
        if self.valid:
            # replot
            self.plot()
            # update line visibility
            self.update_line_visibility()

    def update_line_visibility(self):
        """
        Update the line visibility (turn them on or off)
        :return:
        """
        # get which checkboxs are active
        switch = self.lines_widget.active
        # loop around lines and change visibility
        for it in range(0, len(self.lines)):
            if it in switch:
                self.lines[it].visible = True
            else:
                self.lines[it].visible = False

    def error(self):
        pass

    def update_files(self):
        """
        Find files and update graph if possible
        :return:
        """
        # ---------------------------------------------------------------------
        # get blaze
        blaze = None
        if np.sum(self.line_blaze_cor) > 0:
            pos = np.where(self.line_blaze_cor)[0][0]
            # get file dict
            file_dict = dict(block_kind=self.line_bkind[pos],
                             obs_dir=self.obs_dir, identifier=self.identifier,
                             output=self.line_otypes[pos],
                             hdu=self.line_oext[pos], fiber=self.fiber)
            # find data and load
            _, filename = visu_core.get_file(get_data=False, **file_dict)
            if filename is not None:
                blaze, blazefile = visu_core.get_calib(filename, 'BLAZE')
            else:
                if DEBUG:
                    print('Cannot find data')
                    print(file_dict)
                return
        # ----------------------------------------------------------------------
        # get the wave solution

        # -----------------------------------------------------------------
        # copy source dict
        sdict = dict(self.source.data)
        # ---------------------------------------------------------------------
        # get files from index database
        for it in range(len(self.line_labels)):
            # get name
            name = self.line_labels[it]
            # get file dict
            file_dict = dict(block_kind=self.line_bkind[it],
                             obs_dir=self.obs_dir, identifier=self.identifier,
                             output=self.line_otypes[it],
                             hdu=self.line_oext[it], fiber=self.fiber)
            # -----------------------------------------------------------------
            # find data and load
            data, filename = visu_core.get_file(**file_dict)
            # deal with no valid data
            if data is None:
                if DEBUG:
                    print('Cannot find data')
                    print(file_dict)

                self.valid = False
                return
            else:
                self.valid = True
                self.loaded = self.identifier
                if DEBUG:
                    print('Found file {0}'.format(filename))
            # -----------------------------------------------------------------
            # update max order
            self.order_max = data.shape[0]
            self.order_num_widget.end = self.order_max
            self.xmin = 0
            self.xmax = data.shape[1]
            # -----------------------------------------------------------------
            # correct for blaze
            if self.line_blaze_cor[it] and blaze is not None:
                data = data / blaze

            # get dc level
            dclevel = self.line_dc[it]
            # push into storage
            for order_num in range(data.shape[0]):
                # add x values
                sxname = 'x_{0}[{1}]'.format(name, order_num)
                sdict[sxname] = np.arange(data.shape[1])
                # add y values
                syname = 'flux_{0}[{1}]'.format(name, order_num)
                with warnings.catch_warnings(record=True) as _:
                    if self.line_norm[it] == 'med':
                        norm = mp.nanmedian(data[order_num])
                    elif self.line_norm[it] == 'max':
                        norm = np.nanmax(data[order_num])
                    else:
                        norm = np.ones_like(data[order_num])
                    sdict[syname] = (data[order_num] / norm) + dclevel
            # update current
            sdict['current_{0}_x'] = 'x_{0}[{1}]'.format(name, 0)
            sdict['current_{0}_y'] = 'flux_{0}[{1}]'.format(name, 0)
        # update source
        self.source.data = sdict


    def plot(self):
        # get order number
        order_num = self.order_num
        # loop around lines
        for it in range(len(self.line_labels)):
            # get name
            name = self.line_labels[it]
            color = self.line_colors[it]
            alpha = self.line_alphas[it]

            # get x and y values
            sxname = 'x_{0}[{1}]'.format(name, order_num)
            syname = 'flux_{0}[{1}]'.format(name, order_num)

            cxname = 'current_{0}_x'.format(name)
            cyname = 'current_{0}_y'.format(name)
            # update current
            self.source.data[cxname] = self.source.data[sxname]
            self.source.data[cyname] = self.source.data[syname]
            # adjust ymin and ymax
            y = self.source[syname]
            self.ymin = np.min([self.ymin, np.nanmin(y)])
            self.ymax = np.max([self.ymax, np.nanmax(y)])
            # deal with debugging
            if DEBUG:
                dargs = [name, order_num]
                print('Plotting {0} [Order={1}]'.format(*dargs))

            if self.lines[it] is None:
                # plot line
                line = self.figure.line(cxname, cyname, source=self.source,
                                        color=color, alpha=alpha,
                                        legend_label=name)
                # keep lines
                self.lines[it] = line
        # set x and y range
        self.figure.y_range = Range1d(self.ymin, self.ymax)
        self.figure.x_range = Range1d(self.xmin, self.xmax)


def e2ds_plot(**kwargs) -> bokeh.models.Model:
    # -------------------------------------------------------------------------
    plotwindow = figure()
    plotwindow.sizing_mode = 'scale_width'
    # -------------------------------------------------------------------------
    e2dsplotapp = SpectrumPlot(plotwindow)
    # -------------------------------------------------------------------------
    # get widgets
    inputs = column(*e2dsplotapp.widgets)
    # return the grid
    page = row(inputs, plotwindow, width=1200)
    page.sizing_mode = 'scale_width'
    # return full page
    return page


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
