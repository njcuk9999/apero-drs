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

func = getattr(visu_plots, 'test_plot')

kwargs = dict(power=3, xlabel="x", ylabel="x^3")

root = func(**kwargs)

curdoc().add_root(root)
curdoc().title = 'My test plot'

