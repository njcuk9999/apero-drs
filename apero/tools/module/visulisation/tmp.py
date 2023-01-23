#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is just a test code for the tmp py file written by apero_visu and
visu_core do not use

Created on 2022-02-22

@author: cook
"""
from bokeh.io import curdoc

from apero.tools.module.visulisation import visu_plots

func = getattr(visu_plots, 'e2ds_plot')

kwargs = dict()

root = func(**kwargs)

curdoc().add_root(root)
curdoc().title = 'E2DS plot'
