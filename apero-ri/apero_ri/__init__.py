#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Force non-interactive backend before any other import
# can pull in matplotlib.pyplot with TkAgg (crashes Flask)
import matplotlib
matplotlib.use('Agg')
