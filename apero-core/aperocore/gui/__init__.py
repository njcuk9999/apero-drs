#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aperocore.gui - generic browser gui framework

Reusable, application independent building blocks for small browser guis
served with the standard library http server:

    - webapp: GuiApp (routes, page, built-in api) and serve()
    - server: recovery supervisor (restart a hung worker)
    - procs: process registry (list / follow / stop gui processes)
    - jobs: background and interactive command jobs (local or Slurm)
    - slurm: batch templates and sbatch scripts
    - files: safe file access (allowed roots) and listings
    - diff: side by side diffs
    - fits_view: FITS headers, image previews and table rows
    - mpl_stream / mpl_view: stream figures, interactive figure views
    - yaml_outline: comment preserving yaml outlines / edits
    - static/: the shared css / js / html assets

Nothing in this package knows about any particular application.

Created on 2026-11-26

@author: cook
"""

# =============================================================================
# End of code
# =============================================================================
