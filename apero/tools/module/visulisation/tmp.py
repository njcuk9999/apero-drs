#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-22

@author: cook
"""

from bokeh.io import curdoc
from apero.tools.module.visulisation import visu_plots

from bokeh.io import curdoc
from apero.tools.module.visulisation import visu_plots

func = getattr(visu_plots, 'e2ds_plot')

kwargs = dict()

root = func(**kwargs)

curdoc().add_root(root)
curdoc().title = 'E2DS plot'
