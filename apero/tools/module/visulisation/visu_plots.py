#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-22

@author: cook
"""
import warnings

import bokeh
import numpy as np
from bokeh.layouts import grid, row, column, Spacer
from bokeh.models import ColumnDataSource, Slider, Button
from bokeh.models import HoverTool, CheckboxButtonGroup
from bokeh.models import Range1d, Dropdown, RangeSlider
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models.widgets import Div
from bokeh.plotting import figure

from apero.core import constants
from apero.core import math as mp
from apero.tools.module.visulisation import visu_core

# =============================================================================
# Define variables
# =============================================================================
DEBUG = True
# get params
PARAMS = constants.load()
# define log text
LOG_HTML = '<strong>Log:</strong><br><br>'
# tool tip
e2ds_span = """
<div>
<span style="font-size: 12px; color: {color};">{name}: (x=@{x}, y=@{y})</span>
</div>
"""


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
        self.obs_dir = ''
        self.identifier = ''
        self.order_num = 0
        self.fibers = PARAMS.listp('TELLURIC_FIBER_TYPE', dtype=str)
        self.order_max = PARAMS['FIBER_MAX_NUM_ORDERS_A'] - 1
        self.fiber = str(self.fibers[0])
        self.obs_dirs = visu_core.get_obs_dirs()
        self.identifiers = []
        # line variables
        self.line_bkind = ['red', 'red', 'red', 'red', 'red']
        self.line_labels = ['e2dsff', 'e2ds', 'tcorr', 'recon', 'skymodel']
        self.line_otypes = ['EXT_E2DS_FF', 'EXT_E2DS', 'TELLU_OBJ',
                            'TELLU_RECON', 'TELLU_PCLEAN']
        self.line_norm = ['med', 'med', 'med', None, 'max']
        self.line_blaze_cor = [True, True, True, False, False]
        self.line_oext = [1, 1, 1, 1, 4]
        self.line_active = [0, 2, 3, 4]
        self.line_colors = ['black', 'purple', 'red', 'blue', 'orange']
        self.line_hexcolors = ['#212f3d ', '#9b59b6', ' #e74c3c', ' #3498db',
                               '#e67e22']
        self.line_alphas = [0.75, 0.75, 0.75, 0.75, 0.75]
        self.line_widths = [1.25, 1.25, 1.25, 1, 1]
        self.line_dc = [0, 0, 0, 0, 1]
        self.lines = [None, None, None, None, None]
        # data source
        self.source = ColumnDataSource()
        # object table
        self.obj_hkeys = ['KW_OBJNAME', 'KW_DPRTYPE', 'KW_DATE_OBS',
                          'KW_UTC_OBS', 'KW_EXPTIME', 'KW_EXT_SNR']
        self.obj_keys = ['OBJECT', 'DPRTYPE', 'DATE', 'START TIME', 'EXPTIME',
                         'SNR[{0}]']
        self.obj_values = ['None', 'None', 'None', 'None', 'None', 'None']
        self.object_source = ColumnDataSource()
        self.object_header = None
        self.object_cols = [TableColumn(field='keys', title=''),
                            TableColumn(field='values', title='')]
        self.current_filename = 'None'
        # create div spinner
        self.div_spinner = Div(text="",width=120,height=120)
        # widgets
        self.obs_dir_widget = None
        self.identifier_widget = None
        self.order_num_widget = None
        self.dropdown_widget = None
        self.button = None
        self.lines_widget = None
        self.object_table = None
        self.widgets = []
        # other variables
        self.xmin = 0
        self.xmax = 1
        self.xstep = 0.1
        self.ymin = 0
        self.ymax = 1
        self.yrange = Range1d(self.ymin, self.ymax)
        self.xrange = Range1d(self.xmin, self.xmax)
        # whether we currently have identifier loaded
        self.loaded_params = dict(identifier=self.identifier,
                                  obs_dir=self.obs_dir,
                                  order_num=self.order_num,
                                  fiber=self.fiber)

        self.valid = False
        # create the graph
        self.create()

    def create(self):
        # add hover tool
        self.hover = HoverTool(tooltips=self.tooltip())

        # add widgets
        self.widgets = []
        # ---------------------------------------------------------------------
        # create obs dir text widget
        menu = [(key, key) for key in self.obs_dirs]
        self.obs_dir_widget = Dropdown(label='OBS_DIR',
                                       button_type='primary',
                                       menu=menu)
        self.obs_dir_widget.on_click(self.update_obs_dir)
        self.widgets.append(self.obs_dir_widget)
        # ---------------------------------------------------------------------
        # create identifier text widget
        menu = [(key, key) for key in self.identifiers]
        self.identifier_widget = Dropdown(label='ID',
                                          button_type='primary',
                                          menu=menu)
        self.identifier_widget.on_click(self.update_identifier)
        self.widgets.append(self.identifier_widget)
        # ---------------------------------------------------------------------
        # create widget for order number
        self.order_num_widget = Slider(title='Order No.', value=self.order_num,
                                       start=0, end=self.order_max, step=1)
        self.order_num_widget.on_change('value', self.update_order_num)
        self.widgets.append(self.order_num_widget)
        # ---------------------------------------------------------------------
        if len(self.fibers) > 1:
            fiber_menu = [(fiber, fiber) for fiber in self.fibers]
            self.dropdown_widget = Dropdown(label='Fiber',
                                            button_type='primary',
                                            menu=fiber_menu)
            self.dropdown_widget.on_click(self.update_fiber)
            self.widgets.append(self.dropdown_widget)
        # ---------------------------------------------------------------------
        # create a button to update graph
        self.button = Button(label='Update', button_type='success')
        self.button.on_click(self.update_graph_on_click)
        self.widgets.append(self.button)
        # ---------------------------------------------------------------------
        # create lines checkbox group widget
        self.lines_widget = CheckboxButtonGroup(labels=self.line_labels,
                                                active=self.line_active)
        self.lines_widget.on_change('active', self.update_lines)
        self.lines_widget.disabled = True
        self.widgets.append(self.lines_widget)
        # ---------------------------------------------------------------------
        self.wave_widget = RangeSlider(title='Adjust wavelength range',
                                       start=self.xmin,
                                       end=self.xmax,
                                       value=(self.xmin, self.xmax),
                                       step=self.xstep)
        # wave_widgetcallback = CustomJS(args=dict(p=self.figure),
        #                                code="""
        #                                     var a = cb_obj.value;
        #                                     p.x_range.start = a[0];
        #                                     p.x_range.end = a[1];
        #                                     """)
        self.wave_widget.on_change('value', self.update_wave_axis)
        self.wave_widget.disabled = True
        self.widgets.append(self.wave_widget)
        # ---------------------------------------------------------------------
        # Add object box
        self.object_table = DataTable(source=self.object_source,
                                      columns=self.object_cols)
        self.update_hkeys()
        self.object_table.disabled = True
        self.widgets.append(self.object_table)
        # ---------------------------------------------------------------------
        # add spacer
        self.widget_spacer = Spacer(width=640, height=200)
        self.widgets.append(self.widget_spacer)
        # ---------------------------------------------------------------------
        # logger
        self.log_widget = Div(text=LOG_HTML, background='aliceblue',
                              width=640, height=128, align='end')
        self.widgets.append(self.log_widget)

    # =========================================================================
    # Update functions
    # =========================================================================
    def update_obs_dir(self, event):
        self.obs_dir = str(event.item)
        # update
        if self.obs_dir not in [None, 'None', '', 'Null']:
            new_identifiers = visu_core.get_identifers(obs_dir=self.obs_dir)
            menu = [(key, key) for key in new_identifiers]
            self.identifier_widget.menu = menu

    def update_identifier(self, event):
        self.identifier = str(event.item)

    def update_order_num(self, attrname, old, new):
        _ = attrname, old, new
        self.order_num = int(self.order_num_widget.value)
        self.update_hkeys()

    def update_waveord_limits(self):
        # get wavemap for current order
        key = 'wavemap[{0}]'.format(self.order_num)
        if key not in self.source.data:
            return
        waveord = self.source.data[key]
        # update limtes
        self.xmin = np.min(waveord)
        self.xmax = np.max(waveord)
        self.xstep = np.mean(np.diff(waveord))
        # update widget
        self.wave_widget.start = self.xmin
        self.wave_widget.end = self.xmax
        self.wave_widget.step = self.xstep
        self.wave_widget.value = (self.xmin, self.xmax)

    def update_wave_axis(self, attrname, old, new):
        _ = attrname, old, new
        low, high = self.wave_widget.value
        # self.figure.x_range.bounds = (low, high)
        self.figure.x_range.start = low
        self.figure.x_range.end = high
        # self.yrange.start = self.ymin
        # self.yrange.end = self.ymax
        # self.xrange.start = low
        # self.xrange.end = high
        # self.figure.y_range = self.yrange
        # self.figure.x_range = self.xrange

    def update_fiber(self, event):
        self.fiber = event.item

    def update_lines(self, attrname, old, new):
        _ = attrname, old, new
        self.update_line_visibility()

    def update_graph_on_click(self):
        self.update_graph()
        self.update_waveord_limits()

    def update_graph(self):
        self.update_hkeys()
        # get loaded params
        lparams = dict(identifier=self.identifier, obs_dir=self.obs_dir,
                       order_num=self.order_num, fiber=self.fiber)

        if DEBUG:
            print('Update')
            print(lparams)
        # check condition to update file
        cond_update = False
        for key in self.loaded_params:
            if lparams[key] != self.loaded_params[key]:
                cond_update = True

        # if identifier is the same as loaded we just check line visibility
        if cond_update or not self.valid:
            # update files
            self.logger('Loading data...')
            self.update_files()
            self.reset_logger()
        # update line visibility
        if self.valid:
            # replot
            self.logger('Plotting data...')
            self.plot()
            self.reset_logger()
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
                if self.lines[it] is None:
                    self.plot_line(it)
                else:
                    self.lines[it].visible = True
            elif self.lines[it] is not None:
                self.lines[it].visible = False
        # update tool tip
        self.hover.tooltips = self.tooltip()

    def update_hkeys(self, header=None):
        # deal with not having header
        if header is None:
            header = self.object_header
        # storage for new values
        new_values = []
        new_keys = []

        # if header is still None do nothing
        if header is None:
            # loop round and update
            for it in range(len(self.obj_keys)):
                # get object data key
                key = self.obj_keys[it]
                # get header key
                if key.startswith('SNR'):
                    key = key.format(self.order_num)
                # append reset values
                new_keys.append(key)
                new_values.append(self.obj_values[it])
        else:
            # get the list of hkeys
            hkeys = self.obj_hkeys
            # loop round and update
            for it in range(len(hkeys)):
                # get object data key
                key = self.obj_keys[it]
                # get header key
                if key.startswith('SNR'):
                    key = key.format(self.order_num)
                    hkey = PARAMS[hkeys[it]][0].format(self.order_num)
                    value = header[hkey]
                    value = '{0:.3f}'.format(value)
                else:
                    hkey = PARAMS[hkeys[it]][0]
                    value = header[hkey]
                # add to new values
                new_keys.append(key)
                new_values.append(value)
        # add filename
        new_keys += ['PATH', 'OBS_DIR', 'ID']
        new_values += [PARAMS['DRS_DATA_REDUC'], self.obs_dir,
                       self.identifier]
        # update object source
        sdict = dict(keys=new_keys, values=new_values)
        self.object_source.data = sdict

    def update_files(self):
        """
        Find files and update graph if possible
        :return:
        """
        # ---------------------------------------------------------------------
        # get header of first file
        # get file dict
        file_dict = dict(block_kind=self.line_bkind[0],
                         obs_dir=self.obs_dir, identifier=self.identifier,
                         output=self.line_otypes[0],
                         hdu=self.line_oext[0], fiber=self.fiber)
        # find data and load
        _, filename = visu_core.get_file(get_data=False, **file_dict)

        # get header
        if filename is not None:
            header = visu_core.get_header(filename)
            self.object_header = header
            # set current filename
            self.current_filename = filename
        else:
            header = None
            self.object_header = None
            # set current filename
            self.current_filename = 'None'
        # ---------------------------------------------------------------------
        # populate object table
        self.update_hkeys(header)
        # ---------------------------------------------------------------------
        # get blaze
        blaze = None
        if np.sum(self.line_blaze_cor) > 0:
            if filename is not None:
                blaze, blazefile = visu_core.get_calib(header, 'BLAZE')
                # push into source
                for order_num in range(self.order_max):
                    key = 'blaze[{0}]'.format(order_num)
                    self.source.data[key] = blaze[order_num]
            else:
                if DEBUG:
                    print('Cannot find data')
                    print(file_dict)
                return
        # ----------------------------------------------------------------------
        # get the wave solution
        wavemap, wavefile = visu_core.get_calib(header, 'WAVE')
        # push into source
        for order_num in range(self.order_max):
            key = 'wavemap[{0}]'.format(order_num)
            self.source.data[key] = wavemap[order_num]
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

                # enable some widgets and set valid
                self.wave_widget.disabled = False
                self.lines_widget.disabled = False
                self.object_table = False
                self.valid = True
                # set loaded params
                self.loaded_params = dict(identifier=self.identifier,
                                          fiber=self.fiber)
                if DEBUG:
                    print('Found file {0}'.format(filename))
            # -----------------------------------------------------------------
            # update max order
            self.order_max = data.shape[0]
            self.order_num_widget.end = self.order_max
            self.update_waveord_limits()
            # -----------------------------------------------------------------
            # correct for blaze
            if self.line_blaze_cor[it] and blaze is not None:
                data = data / blaze
            # -----------------------------------------------------------------
            # get dc level
            dclevel = self.line_dc[it]
            # -----------------------------------------------------------------
            # push into storage
            for order_num in range(data.shape[0]):
                # add x values
                sxname = 'x_{0}[{1}]'.format(name, order_num)
                sdict[sxname] = wavemap[order_num]
                # add y values
                syname = 'flux_{0}[{1}]'.format(name, order_num)
                with warnings.catch_warnings(record=True) as _:
                    if self.line_norm[it] == 'med':
                        norm = mp.nanmedian(data[order_num])
                    elif self.line_norm[it] == 'max':
                        norm = mp.nanmax(data[order_num])
                    else:
                        norm = np.ones_like(data[order_num])
                    # norm and add dc level
                    newdata = (data[order_num] / norm)
                # -------------------------------------------------------------
                # finally add the new data to sdict
                #    (with a dc level if required)
                sdict[syname] = newdata + dclevel
            # -----------------------------------------------------------------
            # get x and y values for start position
            sxname0 = 'x_{0}[{1}]'.format(name, self.order_num)
            syname0 = 'flux_{0}[{1}]'.format(name, self.order_num)
            cxname = 'current_{0}_x'.format(name)
            cyname = 'current_{0}_y'.format(name)
            # update current
            sdict[cxname] = sdict[sxname0]
            sdict[cyname] = sdict[syname0]
        # update source
        self.source.data = sdict

    # =========================================================================
    # Features
    # =========================================================================
    def plot(self):

        # reset ymin and ymax
        self.ymin, self.ymax = 0, 1
        # set axis labels
        self.figure.xaxis.axis_label = 'Wavelength [nm]'
        self.figure.yaxis.axis_label = 'Normalized Flux'
        # add hover
        self.figure.add_tools(self.hover)
        # loop around lines
        for it in range(len(self.line_labels)):
            self.plot_line(it)

    def plot_line(self, it):
        # get which checkboxs are active
        switch = self.lines_widget.active
        # get order number
        order_num = self.order_num
        # get name
        name = self.line_labels[it]
        color = self.line_colors[it]
        alpha = self.line_alphas[it]
        lwidth = self.line_widths[it]
        # get x and y values
        sxname = 'x_{0}[{1}]'.format(name, order_num)
        syname = 'flux_{0}[{1}]'.format(name, order_num)
        # assign current values
        cxname = 'current_{0}_x'.format(name)
        cyname = 'current_{0}_y'.format(name)
        # update current
        self.source.data[cxname] = self.source.data[sxname]
        self.source.data[cyname] = self.source.data[syname]
        # adjust ymin and ymax
        y = self.source.data[syname]
        self.ymin = np.min([self.ymin, mp.nanmin(y)])
        self.ymax = np.max([self.ymax, mp.nanmax(y)])
        # only plot if active
        if self.lines[it] is None and it in switch:
            # deal with debugging
            if DEBUG:
                dargs = [name, order_num]
                print('Plotting {0} [Order={1}]'.format(*dargs))
            # plot line
            line = self.figure.line(cxname, cyname, source=self.source,
                                    color=color, alpha=alpha,
                                    legend_label=name, line_width=lwidth)
            # keep lines
            self.lines[it] = line

    def logger(self, text):
        print(text)
        self.log_widget.text = str(LOG_HTML) + text

    def reset_logger(self):
        self.log_widget.text = str(LOG_HTML)

    def tooltip(self) -> str:
        # deal with no line widget yet
        if self.lines_widget is None:
            return ''
        # add start of the box
        tooltipstr = '<div>'
        # get which checkboxs are active
        switch = self.lines_widget.active
        # loop around line labels (has to be all of them)
        for it in range(len(self.line_labels)):
            if it in switch:
                name = self.line_labels[it]
                cxname = 'current_{0}_x'.format(name)
                cyname = 'current_{0}_y'.format(name)
                color = self.line_hexcolors[it]
                tooltipstr += e2ds_span.format(x=cxname, y=cyname, name=name,
                                               color=color)
        # add the end of the box
        tooltipstr += '</div>'
        # return the tool tip string
        return tooltipstr


def e2ds_plot(**kwargs) -> bokeh.models.Model:
    # -------------------------------------------------------------------------
    plotwindow = figure(height=512, width=768)
    plotwindow.sizing_mode = 'stretch_both'
    # -------------------------------------------------------------------------
    e2dsplotapp = SpectrumPlot(plotwindow)
    # -------------------------------------------------------------------------
    # get widgets
    inputs = column(*e2dsplotapp.widgets)
    # return the grid
    page = row(inputs, plotwindow, width=1024)
    page.sizing_mode = 'stretch_both'
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
