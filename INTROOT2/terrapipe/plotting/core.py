#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 13:45

@author: cook
"""
from __future__ import division
import numpy as np
from astropy.table import Table
import sys
import os
import glob
import matplotlib
import shutil
from collections import OrderedDict

from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import drs_log
from terrapipe.core import math as mp
from terrapipe.io import drs_path

from terrapipe.plotting import plot_functions
from terrapipe.plotting import latex
from terrapipe.plotting import html

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
WLOG = drs_log.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = drs_log.find_param
# get plotting definitions
definitions = plot_functions.definitions
# get Graph function
Graph = plot_functions.Graph
# -----------------------------------------------------------------------------
# storage of modules (so we only load them once)
PLT_MOD = None
MPL_MOD = None
# -----------------------------------------------------------------------------
# get latex string cleaning function
clean = latex.clean


# =============================================================================
# Define plotting class
# =============================================================================
class Plotter:
    def __init__(self, params, recipe=None):
        self.params = params
        self.recipe = recipe
        self.recipename = '{0} ({1})'.format(recipe.name, recipe.shortname)
        self.plotoption = params['DRS_PLOT']
        self.names = dict()
        self.plot_switches = dict()
        self.has_debugs = False
        self.stat_dict = OrderedDict()
        self.stats = None
        self.qc_params = OrderedDict()
        # get the text dictionary
        self.textdict = TextDict(self.params['INSTRUMENT'],
                                 self.params['LANGUAGE'])
        # ------------------------------------------------------------------
        # storage of debug plots
        self.debug_graphs = dict()
        # ------------------------------------------------------------------
        # summary file location
        self.summary_location = None
        self.summary_filename = None
        # storage of summary plots
        self.summary_graphs = dict()
        # ------------------------------------------------------------------
        # matplotlib modules
        self.backend = None
        self.plt = None
        self.matplotlib = None
        self.axes_grid1 = None
        # ------------------------------------------------------------------
        # set self.names via _get_plot_names()
        self._get_plot_names()
        # set self.plot_switches via _get_plot_switches()
        self._get_plot_switches()
        # set summary location
        self._set_location()
        # set matplotlib via _get_matplotlib()
        self._get_matplotlib()

    def __call__(self, name, func=None, fiber=None, **kwargs):
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
        if self.plotoption == -1:
            WLOG(self.params, 'debug', TextEntry('09-100-00002'))
            return 0
        # ------------------------------------------------------------------
        # deal with no plot needed
        if (self.plotoption == 0) and (name in self.debug_graphs):
            WLOG(self.params, 'debug', TextEntry('09-100-00002'))
            return 0
        # ------------------------------------------------------------------
        # add fiber to keyword arguments
        kwargs['fiber'] = fiber
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
            # do not need to turn off/on summary plots
            if plot_obj.kind == 'summary':
                pass
            # if it is check whether it is set to False
            elif not self.plot_switches[name]:
                dmsg = TextEntry('09-100-00003', args=[name.upper()])
                WLOG(self.params, 'debug', dmsg)
                # if it is check whether it is set to False
                return 0
        # do not plot if we are in debug mode and plot == 0
        if plot_obj.kind == 'debug':
            if self.plotoption == 0:
                return 0
        # ------------------------------------------------------------------
        # must be in plot lists
        if name in self.recipe.debug_plots:
            # log: plotting debug plot
            WLOG(self.params, '', TextEntry('40-100-00002', args=[name]))
        elif name in self.recipe.summary_plots:
            # log: plotting summary plot
            WLOG(self.params, '', TextEntry('40-100-00003', args=[name]))
        else:
            # else log an error
            eargs = [name, self.recipe.name]
            WLOG(self.params, 'error', TextEntry('00-100-00002', args=eargs))
        # ------------------------------------------------------------------
        # new instance of the plot object
        plot_inst = plot_obj.copy()
        # set output file name
        plot_inst.set_filename(self.params, self.summary_location, fiber)
        # execute the plotting function
        plot_inst.func(self, plot_inst, kwargs)
        # ------------------------------------------------------------------
        # if successful return 1
        return 1

    def plotstart(self, graph):
        if graph.kind == 'debug':
            if self.plotoption == 1:
                self.interactive(True)
            if self.plotoption > 0:
                return True
            else:
                return False
        elif graph.kind == 'summary':
            return True
        else:
            return False

    def plotend(self, graph):
        # deal with debug plots
        if graph.kind == 'debug':
            # we shouldn't have got here but if plot=0 do not plot
            if self.plotoption == 0:
                pass
            # if plot = 1 we are in interactive mode
            elif self.plotoption == 1:
                self.interactive(False)
                # add debug plots
                self.debug_graphs[graph.name] = graph.copy()
            # if plot = 2 we need to show the plot
            elif self.plotoption == 2:
                self.plt.show()
                self.plt.close()
        # deal with summary plots
        elif graph.kind == 'summary':
            # TODO: Add summary options
            # 1. save to file
            self.interactive(False)
            self.plt.savefig(graph.filename + '.png', dpi=graph.dpi)
            self.plt.savefig(graph.filename + '.pdf', dpi=graph.dpi)
            self.plt.close()
            # 2. add graph to summary plots
            self.summary_graphs[graph.filename] = graph.copy()
        else:
            pass

    def plotloop(self, looplist):
        # must run in plot mode 2

        if self.plotoption == 1:
            current_mode = 1
            self.plotoption = 2
            self.plt.ioff()
        else:
            current_mode = None
        # check that looplist is a valid list
        if not isinstance(looplist, list):
            # noinspection PyBroadException
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
                # must set the mode back to original (if changed)
                if current_mode is not None:
                    self.plotoption = current_mode
                    self.plt.ion()
                # break out of while
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
                # noinspection PyBroadException
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
                    # must set the mode back to original (if changed)
                    if current_mode is not None:
                        self.plotoption = current_mode
                        self.plt.ion()
                    # break out of while
                    break

    def closeall(self):
        """
        Close all matplotlib plots currently open

        :return None:
        """
        self.plt.close('all')

    def close_plots(self, loop=False):
        # deal with closing loop plots
        if loop:
            WLOG(self.params, 'info', TextEntry('40-100-00006'), printonly=True)
        # log message asking to close plots
        WLOG(self.params, 'info', TextEntry('40-003-00003'), printonly=True)
        # deal with python 2 / python 3 input method
        if sys.version_info.major < 3:
            # note python 3 wont find this!
            # noinspection PyUnresolvedReferences
            uinput = raw_input('[Y]es or [N]o:\t')
        else:
            uinput = input('[Y]es or [N]o:\t')
        # if yes close all plots
        if 'Y' in uinput.upper():
            # close any open plots properly
            self.closeall()

    def interactive(self, switch=False):
        """
        plt.ion()/plt.ioff() sometimes does not work in debug mode
        therefore we must catch it.

        :param switch: bool, if True turn on interactive mode else turn it off
        :type switch: bool

        :return: None
        """
        # if switch is True turn on interactive mode
        if switch:
            try:
                self.plt.ion()
            except:
                pass
        # else we assume switch is False and turn off interactive mode
        #    note here we show and close plots in case anything was opened
        #    in interactive mode and is now stuck open
        else:
            try:
                self.plt.ioff()
            except:
                self.plt.show()
                self.plt.close()

    # ------------------------------------------------------------------
    # summary methods
    # ------------------------------------------------------------------
    def summary_document(self, iteration, qc_params=None, stats=None):
        func_name = display_func(self.params, 'summary_document', __NAME__,
                                 'Plotter')
        # get recipe short name
        name = self.recipe.name
        pid = self.params['PID'].lower()
        pid_dir = '{0}_{1}_{2}'.format(pid, name, iteration + 1)
        # deal with no stats
        if stats is None:
            # process stats
            self.summary_stats()
            # set stats to internal stats
            stats = self.stats
        # ------------------------------------------------------------------
        # summary plot in latex
        try:
            # log progress
            WLOG(self.params, 'info', TextEntry('40-100-00004'))
            # latex document
            latexdoc = self.summary_latex(qc_params, stats)
        except Exception as e:
            # log error as warning
            wargs = [type(e), e, func_name]
            WLOG(self.params, 'warning', TextEntry('10-100-01001', args=wargs))
            # set latex doc to None
            latexdoc = None
        # ------------------------------------------------------------------
        # summary html
        try:
            # log progress
            WLOG(self.params, 'info', TextEntry('40-100-00005'))
            # latex document
            htmldoc = self.summary_html(qc_params, stats)
        except Exception as e:
            # log error as warning
            wargs = [type(e), e, func_name]
            WLOG(self.params, 'warning', TextEntry('10-100-01002', args=wargs))
            # set latex doc to None
            htmldoc = None
        # ------------------------------------------------------------------
        # clean up
        if latexdoc is not None:
            latexdoc.cleanup()
        if htmldoc is not None:
            htmldoc.cleanup()
        # move all pid to a folder
        files = glob.glob(self.summary_location + os.sep + '*')
        # ------------------------------------------------------------------
        # make pid directory
        fullpath = os.path.join(self.summary_location, pid_dir)
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)
        # loop around files and move to pid directory
        for filename in files:
            # skip directories
            if os.path.isdir(filename):
                continue
            # only look for files with pid in the name
            if pid in filename:
                # get new path
                basename = os.path.basename(filename)
                newfilename = os.path.join(fullpath, basename)
                # move files
                shutil.move(filename, newfilename)

    def summary_latex(self, qc_params, stats):
        # set up the latex document
        doc = latex.LatexDocument(self.summary_filename)
        # get recipe short name
        shortname = clean(self.recipename)
        pid = self.params['PID'].lower()
        # summary info
        sargs = [shortname, pid]
        summary_title = self.textdict['40-100-01006'].format(*sargs)
        summary_authors = ' '.join(__author__)
        # add start
        doc.preamble()
        doc.begin()
        # add title
        doc.add_title(summary_title, summary_authors)
        # display the arguments used
        doc.newline()
        argv = ' '.join(clean(self.recipe.used_command))
        doc.add_text(self.textdict['40-100-01002'].format(argv))
        doc.newline()
        # add graph section
        doc.section(self.textdict['40-100-01000'])
        # add graph section text
        doc.add_text(self.textdict['40-100-01001'].format(shortname))
        doc.newline()
        # display all graphs
        for g_it, key in enumerate(self.summary_graphs):
            # get graph instance for gname
            sgraph = self.summary_graphs[key]
            # get cleaned name
            cgname = clean(sgraph.name)
            # reference graph
            doc.add_text(self.textdict['40-100-01007'].format(g_it + 1, cgname))
            doc.newline()
        # display all graphs
        for key in self.summary_graphs:
            # get graph instance for gname
            sgraph = self.summary_graphs[key]
            # get graph basename with correct file extension
            sbasename = os.path.basename(sgraph.filename) + '.pdf'
            # add graph
            doc.figure(filename=sbasename, caption=clean(sgraph.description),
                       width=16)
        # add qc params section
        self.summary_latex_qc_params(doc, qc_params)
        # add stats section
        self.summary_latex_stats(doc, stats)
        # end the document properly
        doc.end()
        # write and compile latex file
        doc.write_latex()
        # get log file
        logfile = drs_log.get_logfilepath(WLOG, self.params)
        doc.compile(logfile + '.latex')
        # return the doc
        return doc

    def summary_latex_qc_params(self, doc, qc_params):
        if qc_params is None and self.qc_params is None:
            return
        # get recipe short name
        shortname = clean(self.recipename)
        # add qc_param section
        doc.section(self.textdict['40-100-01003'])
        # add qc_param text
        doc.add_text(self.textdict['40-100-01004'].format(shortname))
        # add qc_param table
        qc_table, qc_mask = qc_param_table(qc_params, self.qc_params)
        # get qc_caption
        qc_caption = self.textdict['40-100-01005'].format(shortname)
        # insert table
        doc.insert_table(qc_table, caption=qc_caption, colormask=qc_mask)

    def summary_latex_stats(self, doc, stats):
        if stats is None:
            return
        # get recipe short name
        shortname = clean(self.recipename)
        # add qc_param section
        doc.section(self.textdict['40-100-01008'])
        # add qc_param text
        doc.add_text(self.textdict['40-100-01009'].format(shortname))
        # get qc_caption
        caption = self.textdict['40-100-01010'].format(shortname)
        # copy table
        stats_latex = Table(stats)
        # insert table
        doc.insert_table(stats_latex, caption=caption)

    def summary_html(self, qc_params, stats):
        summary_filename = self.summary_filename
        # set up the latex document
        doc = html.HtmlDocument(summary_filename)
        # get recipe short name
        shortname = self.recipename
        pid = self.params['PID'].lower()
        name = self.recipe.name
        # summary info
        sargs = [shortname, pid]
        summary_title = self.textdict['40-100-01006'].format(*sargs)
        summary_authors = ' '.join(__author__)
        # add start
        doc.preamble()
        # add title
        doc.add_title(summary_title, summary_authors)
        # display the arguments used
        doc.newline()
        argv = ' '.join(self.recipe.used_command)
        doc.add_text(self.textdict['40-100-01002'].format(argv))
        doc.newline()
        # add graph section
        doc.section(self.textdict['40-100-01000'])
        # add graph section text
        doc.add_text(self.textdict['40-100-01001'].format(shortname))
        doc.newline()
        # display all graphs
        for g_it, key in enumerate(self.summary_graphs):
            # get graph instance for gname
            sgraph = self.summary_graphs[key]
            # reference graph
            targs = [g_it + 1, sgraph.description]
            doc.add_text(self.textdict['40-100-01007'].format(*targs))
            doc.newline()
            # add graph with correct extension
            sbasename = os.path.basename(sgraph.filename) + '.png'
            doc.figure(filename=sbasename, width=1024)
        # add qc params section
        self.summary_html_qc_params(doc, qc_params)
        # add stats section
        self.summary_html_stats(doc, stats)
        # end the document properly
        doc.end()
        # write and compile latex file
        doc.write_html()
        # return doc
        return doc

    def summary_html_qc_params(self, doc, qc_params):
        if qc_params is None and self.qc_params is None:
            return
        # get recipe short name
        shortname = self.recipename
        # add qc_param section
        doc.section(self.textdict['40-100-01003'])
        # add qc_param text
        doc.add_text(self.textdict['40-100-01004'].format(shortname))
        # add qc_param table
        qc_table, qc_mask = qc_param_table(qc_params, self.qc_params)
        # get qc_caption
        qc_caption = self.textdict['40-100-01005'].format(shortname)
        # insert table
        doc.insert_table(qc_table, caption=qc_caption, colormask=qc_mask)

    def summary_html_stats(self, doc, stats):
        if stats is None:
            return
        if stats is None:
            return
        # get recipe short name
        shortname = self.recipename
        # add qc_param section
        doc.section(self.textdict['40-100-01008'])
        # add qc_param text
        doc.add_text(self.textdict['40-100-01009'].format(shortname))
        # get qc_caption
        caption = self.textdict['40-100-01010'].format(shortname)
        # copy table
        stats_html = Table(stats)
        # insert table
        doc.insert_table(stats_html, caption=caption)

    def summary_stats(self):
        # storage of table columns
        names, values, comments, fibers = [], [], [], []
        # switch for knowing whether we have found comments
        has_comments = False
        has_fibers = False
        # loop around statistics dictionary
        for kwarg in self.stat_dict:
            # append to lists
            names.append(kwarg)
            # get value and comment
            value, comment, fiber = self.stat_dict[kwarg]
            # append to lists
            values.append(str(value))
            if comment is not None:
                comments.append(comment)
                has_comments = True
            else:
                comments.append('')
            if fiber is not None:
                fibers.append(fiber)
                has_fibers = True
            else:
                fibers.append('')
        # push into table
        self.stats = Table()
        self.stats['NAMES'] = names
        self.stats['VALUES'] = values
        if has_comments:
            self.stats['COMMENTS'] = comments
        if has_fibers:
            self.stats['FIBER'] = fibers

    def add_stat(self, key, value, comment=None, fiber=None):

        # if key is in parameter dictionary then assume we have a
        #    drs key word store ([key, value, comment])
        if key in self.params:
            # get key
            dkey = self.params[key][0]
            # get comment
            dcomment = self.params[key][2]
            # check if value is float and round if needed
            value = _sigfig(value, digits=5)
            # add to stat dictionary
            self.stat_dict[dkey] = [str(value), str(dcomment), fiber]

        else:
            # check if value is float and round if needed
            value = _sigfig(value, digits=5)
            # get key in capitals
            dkey = str(key).upper()
            # add to stat dictionary
            self.stat_dict[dkey] = [str(value), comment, fiber]

    def add_qc_params(self, qc_params, fiber):
        # add qc_params for this fiber
        self.qc_params[fiber] = qc_params

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
            return self.names[name].copy()
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
        debug_plots = self.recipe.debug_plots
        # loop around keys in parameter dictionary
        for name in self.names:
            # get kind
            kind = self.names[name].kind
            # only deal with keys that start with 'PLOT_'
            key = 'PLOT_{0}'.format(name.upper())
            # check if in params
            if key in self.params:
                # load into switch dictionary
                self.plot_switches[name] = self.params[key]
            else:
                self.plot_switches[name] = False
            # if recipe is allowed to use plot (in recipe.set_plots)
            if name in debug_plots and kind == 'debug':
                self.has_debugs = True

    def _get_matplotlib(self):
        """
        Deal with the difference plotting modes and get the correct backend
        This sets self.plt, self.matplotlib and self.mpl_toolkits

        :return:
        """
        global PLT_MOD
        global MPL_MOD
        # ------------------------------------------------------------------
        # if matplotlib modules set then just use these
        if PLT_MOD is not None:
            self.plt = PLT_MOD
            self.axes_grid1 = MPL_MOD
        # ------------------------------------------------------------------
        # if we do not have debug plots then we do not need any fancy backend
        # and can just use Agg
        if not self.has_debugs:
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from  mpl_toolkits import axes_grid1
            self.plt = plt
            self.matplotlib = matplotlib
            self.axes_grid1 = axes_grid1
            PLT_MOD = plt
            MPL_MOD = axes_grid1
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
                    from mpl_toolkits import axes_grid1
                    self.plt = plt
                    self.matplotlib = matplotlib
                    self.axes_grid1 = axes_grid1
                    PLT_MOD = plt
                    MPL_MOD = axes_grid1
                    break
                except Exception as _:
                    continue
        # ------------------------------------------------------------------
        # get backend
        self.backend = matplotlib.get_backend()
        # debug log which backend used
        dargs = [self.backend]
        WLOG(self.params, 'debug', TextEntry('09-100-00001', args=dargs))
        # ------------------------------------------------------------------
        # deal with still having MacOSX backend
        if self.backend == 'MacOSX':
            WLOG(self.params, 'error', TextEntry('09-100-00001'))

    def _set_location(self):
        # get pid
        pid = self.params['PID']
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
        filename = 'summary_{0}_{1}'.format(pid, rname)
        # make filename all lower case
        filename = filename.lower()
        # update these values
        self.summary_location = path
        self.summary_filename = os.path.join(path, filename)


# =============================================================================
# Define  functions
# =============================================================================
def qc_param_table(qc_params, qc_param_dict):
    # deal with no qc_params
    if qc_params is None:
        # flag that we do have fibers
        has_fiber = True
    else:
        # set up a one key dictionary
        qc_param_dict = OrderedDict(none=qc_params)
        # flag that we do not have fibers
        has_fiber = False
    # define storage to pipe into table
    conditions = []
    values = []
    passed = []
    fibers = []
    # loop around keys in dicitonary of quality control params
    for key in qc_param_dict:
        # get qc_params for this key
        qc_params = qc_param_dict[key]
        # get qc_param vectors
        qc_names, qc_values, qc_logic, qc_pass = qc_params
        # loop around length of vectors and extract values
        for it in range(len(qc_names)):
            # if value is None then ignore this row
            if qc_names[it] == 'None':
                continue
            # else extract conditions values and passed criteria
            else:
                conditions.append(qc_logic[it])
                # get value
                value = qc_values[it]
                # deal with no value
                if value == 'None':
                    values.append(qc_names[it])
                    continue
                # check if value is float and round if needed
                value = _sigfig(value, digits=5)
                vargs = [qc_names[it], value]
                # append to list
                values.append('{0} = {1}'.format(*vargs))
                passed.append(qc_pass[it] == 1)
                fibers.append(key)
        # deal with no qc defined
        if len(conditions) == 0:
            return None, None
        else:
            qc_table = Table()
            qc_table['Condition'] = conditions
            qc_table['Value'] = values
            if has_fiber:
                qc_table['Fiber'] = fibers
            return qc_table, np.array(passed)


def _sigfig(value, digits=5):
    # deal with float values
    try:
        if '.' in str(value):
            value = np.round(float(value), digits)
            return mp.sigfig(value, digits)
    except ValueError:
        pass
    return value


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
    _recipe, _params = cal_dark_spirou.main(DEBUG0000=True)

    _recipe.debug_plots.append('TEST1')
    _recipe.debug_plots.append('TEST2')
    _recipe.summary_plots.append('TEST3')

    _params.set('DRS_DEBUG', value=1)
    _params.set('DRS_PLOT', value=2)
    _params.set('DRS_PLOT_EXT', 'pdf')
    _params.set('DRS_SUMMARY_EXT', 'pdf')
    _params.set('PLOT_TEST1', value=True)
    _params.set('PLOT_TEST2', value=True)
    _params.set('PLOT_TEST3', value=True)
    plotter = Plotter(_params, _recipe)
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

    _qc_params = [['DARKAMP', 'LIGHTAMP'], [4, 10],
                  ['DARKAMP < 5', 'LIGHTAMP < 5'], [1, 0]]

    _stats = Table()
    _stats['Name'] = ['TEST_VALUE_1', 'V2', 'VALUE3', 'TEST4']
    _stats['Value'] = [1, 0.1, 0.2, 100]

    plotter.summary_document(_qc_params, _stats)


# =============================================================================
# End of code
# =============================================================================
