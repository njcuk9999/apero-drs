#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 13:45

@author: cook
"""
from __future__ import division
import os
import matplotlib

from terrapipe.plotting import plot_functions
from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import drs_log
from terrapipe.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_reprocess.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = core.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# get plotting definitions
definitions = plot_functions.definitions
# get Graph function
Graph = plot_functions.Graph
# -----------------------------------------------------------------------------
# storage of modules (so we only load them once)
PLT_MOD = None
MPL_MOD = None


# =============================================================================
# Define plotting class
# =============================================================================
class Plotter:
    def __init__(self, params, recipe=None):
        self.params = params
        self.recipe = recipe
        self.plot = params['DRS_PLOT']
        self.names = dict()
        self.plot_switches = dict()
        self.has_debugs = False
        # summary file location
        self.summary_location = None
        self.summary_filename = None
        # storage of summary plots
        self.summary_graphs = dict()
        # get the text dictionary
        self.textdict = TextDict(self.params['INSTRUMENT'],
                                 self.params['LANGUAGE'])
        # ------------------------------------------------------------------
        # matplotlib modules
        self.plt = None
        self.matplotlib = None
        self.mpl_toolkits = None
        # ------------------------------------------------------------------
        # set self.names via _get_plot_names()
        self._get_plot_names()
        # set self.plot_switches via _get_plot_switches()
        self._get_plot_switches()
        # set summary location
        self._set_location()
        # set matplotlib via _get_matplotlib()
        self._get_matplotlib()

    def graph(self, name, func=None, **kwargs):
        """
        Function used to plot a specific graph (name needs to be defined in
        plot functions), keyword arguments are passed to plotting function

        :param name: string, the name of the graph to plot
        :param func: if defined this is the function kwargs are passed to
        :param kwargs: keyword arguments passed to graph function

        :type name: str
        :type func: function

        :return: Returns 1 if plot or 0 elsewise
        :rtype: int
        """
        # ------------------------------------------------------------------
        # deal with no plot needed
        if self.plot == 0:
            WLOG(self.params, 'debug', TextEntry('09-100-00002'))
            return 0
        # ------------------------------------------------------------------
        # deal with func being set
        if func is not None:
            func(self, None, kwargs)
        # ------------------------------------------------------------------
        # get the function to pass
        plot_obj = self._get_func(name)
        # ------------------------------------------------------------------
        # deal with debug plots (that should be skipped if PLOT_{NAME} is False)
        if name in self.plot_switches:
            # if it is check whether it is set to False
            if not self.plot_switches[name]:
                dmsg = TextEntry('09-100-00003', args=[name.upper()])
                WLOG(self.params, 'debug', dmsg)
                # if it is check whether it is set to False
                return 0
        # ------------------------------------------------------------------
        # new instance of the plot object
        plot_inst = plot_obj.copy()
        # set output file name
        plot_inst.set_filename(self.params, self.summary_location)
        # execute the plotting function
        plot_inst.func(self, plot_inst, kwargs)
        # ------------------------------------------------------------------
        # if successful return 1
        return 1

    def start(self, graph):
        if graph.kind == 'debug':
            if self.plot == 1:
                self.plt.ion()

    def end(self, graph):
        # deal with debug plots
        if graph.kind == 'debug':
            # we shouldn't have got here but if plot=0 do not plot
            if self.plot == 0:
                pass
            # if plot = 1 we are in iteractive mode
            elif self.plot == 1:
                self.plt.ioff()
            # if plot = 2 we need to show the plot
            elif self.plot == 2:
                self.plt.show()
                self.plt.close()
        # deal with summary plots
        elif graph.kind == 'summary':
            # TODO: Add summary options
            # 1. save to file
            self.plt.ioff()
            self.plt.savefig(graph.filename)
            self.plt.close()
            # 2. add graph to summary plots
            self.summary_graphs[graph.name] = graph.copy()
        else:
            pass

    def plotloop(self, looplist):
        # check that looplist is a valid list
        if not isinstance(looplist, list):
            try:
                looplist = list(looplist)
            except Exception as _:
                WLOG(self.params, 'error', 'Must be a list')
        # define message to give to user
        message = self.textdict['40-100-00001'].format(len(looplist) - 1)
        # start the iterator at zero
        it = 0
        first = True
        # loop around until we hit the length of the loop list
        while it < len(looplist):
            # deal with end of looplist
            if it == len(looplist):
                break
            # if this is the first iteration do not print message
            if first:
                # yield the first iteration value
                yield looplist[it]
                # increase the iterator value
                it += 1
                first = False
            # else we need to ask to go to previous, next or end
            else:
                # get user input
                userinput = input(message)
                # try to cast into a integer
                try:
                    userinput = int(userinput)
                except Exception as _:
                    userinput = str(userinput)
                # if 'p' in user input we assume they want to go to previous
                if 'P' in str(userinput).upper():
                    yield looplist[it - 1]
                    it -= 1
                # if 'n' in user input we assume they want to go to next
                elif 'N' in str(userinput).upper():
                    yield looplist[it + 1]
                    it += 1
                elif isinstance(userinput, int):
                    it = userinput
                    # deal with it too low
                    if it < 0:
                        it = 0
                    # deal with it too large
                    elif it >= len(looplist):
                        it = len(looplist) - 1
                    # yield the value of it
                    yield looplist[it]
                # else we assume the loop is over and we want to exit
                else:
                    break

    def closeall(self):
        """
        Close all matplotlib plots currently open

        :return None:
        """
        self.plt.close('all')

    # ------------------------------------------------------------------
    # internal methods
    # ------------------------------------------------------------------
    def _get_func(self, name):
        """
        Internal function to return the plot object defined by "name"
        :param name: string, the name of the graph to plot
        :type name: str

        :return: Graph object for the "name" or raises error
        :rtype: Graph
        """
        # set function name
        func_name = display_func(self.params, '_get_func', __NAME__, 'Plotter')
        # check if name is in plot names
        if name.upper() in self.names:
            return self.names[name]
        # else return an error
        else:
            # log error: Plotter error: graph name was not found in plotting
            #            definitions
            eargs = [name, func_name]
            WLOG(self.params, 'error', TextEntry('00-100-00001', args=eargs))

    def _get_plot_names(self):
        """
        Get the plot names (stored in self.names)
        :return: None
        """
        self.names = dict()
        # loop around plot objects
        for plot_obj in definitions:
            # get the plot object name
            name = plot_obj.name.upper()
            # store in names dictionary
            self.names[name] = plot_obj

    def _get_plot_switches(self):
        """
        Find all currently defined plot switches in params and checks
        to see if we have any debug plots
        :return:
        """
        # loop around keys in parameter dictionary
        for name in self.names:
            # only deal with keys that start with 'PLOT_'
            key = 'PLOT_{0}'.format(name.upper())
            # check if in params
            if key in params:
                # load into switch dictionary
                self.plot_switches[name] = params[key]
                # for debug plots check whether switch is True
                if (self.names[name].kind == 'debug') and params[key]:
                    self.has_debugs = True

    def _get_matplotlib(self):
        """
        Deal with the difference plotting modes and get the correct backend
        This sets self.plt, self.matplotlib and self.mpl_toolkits

        :return:
        """
        global PLT_MOD
        global MPL_MOD

        # if matplotlib modules set then just use these
        if PLT_MOD is not None:
            self.plt = PLT_MOD
            self.mpl_toolkits = MPL_MOD
        # ------------------------------------------------------------------
        # if we do not have debug plots then we do not need any fancy backend
        # and can just use Agg
        if not self.has_debugs:
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import mpl_toolkits
            self.plt = plt
            self.matplotlib = matplotlib
            self.mpl_toolkits = mpl_toolkits
            PLT_MOD = plt
            MPL_MOD = mpl_toolkits
        # else we may have to plot graphs to the screen so we need to use
        #    a more fancy backend (but not MacOSX)
        else:
            # fix for MacOSX plots freezing
            gui_env = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'TKAgg', 'WXAgg', 'Agg']
            for gui in gui_env:
                # noinspection PyBroadException
                try:
                    matplotlib.use(gui, warn=False, force=True)
                    import matplotlib.pyplot as plt
                    import mpl_toolkits
                    self.plt = plt
                    self.matplotlib = matplotlib
                    self.mpl_toolkits = mpl_toolkits
                    PLT_MOD = plt
                    MPL_MOD = mpl_toolkits
                    break
                except:
                    continue
        # ------------------------------------------------------------------
        # get backend
        backend = matplotlib.get_backend()
        # debug log which backend used
        dargs = [backend]
        WLOG(self.params, 'debug', TextEntry('09-100-00001', args=dargs))
        # ------------------------------------------------------------------
        # deal with still having MacOSX backend
        if backend == 'MacOSX':
            WLOG(self.params, 'error', TextEntry('09-100-00001'))

    def _set_location(self):
        # get pid
        pid = self.params['PID']
        ext = self.params['DRS_SUMMARY_EXT']
        if self.recipe is None:
            rname = 'None'
        else:
            rname = self.recipe.name
        # get root plot path
        plot_path = self.params['DRS_DATA_PLOT']
        # get night name (and deal with unset/other)
        nightname = self.params['NIGHTNAME']
        if nightname is None or nightname == '':
            nightname = 'other'
        # construct summary pdf
        path = os.path.join(plot_path, nightname)
        # create folder it if doesn't exist
        drs_path.makedirs(self.params, path)
        # create the summary plot name
        filename = 'summary_{0}_{1}.{2}'.format(pid, rname, ext)
        # make filename all lower case
        filename = filename.lower()
        # update these values
        self.summary_location = path
        self.summary_filename = os.path.join(path, filename)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    __NAME__ = 'cal_dark_spirou.py'
    import sys
    sys.argv = 'cal_dark_spirou.py 2018-09-24 2305769d_pp.fits'.split()
    from terrapipe.recipes.spirou import cal_dark_spirou
    recipe, params = cal_dark_spirou.main(DEBUG0000=True)

    params.set('DRS_DEBUG', value=1)
    params.set('DRS_PLOT', value=2)
    params.set('DRS_PLOT_EXT', 'pdf')
    params.set('DRS_SUMMARY_EXT', 'pdf')
    params.set('PLOT_TEST1', value=True)
    params.set('PLOT_TEST2', value=True)
    params.set('PLOT_TEST3', value=True)
    plotter = Plotter(params, recipe)
    import numpy as np
    x = np.arange(-10, 10)
    y = x ** 2
    plotter.graph('TEST1', x=x, y=y, colour='red')
    plotter.graph('TEST2', x=x, y=y, colour='blue')

    orders = np.arange(10)
    xarr, yarr = [], []
    for order_num in range(len(orders)):
        yarr.append(x ** order_num)
        xarr.append(x + 10**order_num)
    plotter.graph('TEST3', ord=orders, x=xarr, y=yarr)

# =============================================================================
# End of code
# =============================================================================
