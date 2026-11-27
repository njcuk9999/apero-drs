#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A matplotlib backend that streams figures to a browser gui

Use it for programs started from a gui instead of opening plot windows:

    MPLBACKEND=module://aperocore.gui.mpl_stream
    APEROCORE_PLOT_STREAM_DIR=/path/to/stream/folder

Every plt.show() (or fig.show()) saves each open figure as a png in the
stream folder, appends one json line describing it to index.jsonl and
closes the figure - nothing ever blocks or pops up. A program can describe
a figure for the gui by setting a dict on it before showing it:

    figure.gui_info = dict(title='...', description='...', name='...',
                           func='...')

(title replaces the automatic title; every key is optional). Without a stream
folder figures are simply closed (like a non interactive backend). The
gui reads index.jsonl to show the figures while the program runs.

Interactive figures: next to the png the figure itself is pickled
({name}.mplfig) so the gui can redraw it with other axis limits (zoom /
pan, see aperocore.gui.mpl_view) - also after the program ended. Figures
that cannot be pickled, or whose pickle is bigger than
APEROCORE_PLOT_STREAM_MAX_MB (default 50, 0 = never pickle), are png only.

Every entry records where the program was when the figure was shown
(step = aperocore.progress.context(): its tags and the step path) so a
gui can show the figures of one step.

Drawing is done by the Agg backend.

Created on 2026-11-26

@author: cook
"""
import json
import os
import re
import threading
import time
from typing import Any, Dict, Optional

import pickle

from matplotlib import _pylab_helpers
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.backends.backend_agg import FigureCanvasAgg

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.mpl_stream.py'
# environment variable naming the stream folder
STREAM_ENV = 'APEROCORE_PLOT_STREAM_DIR'
# the index of streamed figures (one json object per line)
INDEX_NAME = 'index.jsonl'
# environment variable: the largest figure pickle kept (MB, 0 = none)
MAX_MB_ENV = 'APEROCORE_PLOT_STREAM_MAX_MB'
DEFAULT_MAX_MB = 50.0
# the extension of pickled (interactive) figures
FIGURE_EXT = '.mplfig'
# resolution of the streamed pngs
STREAM_DPI = 100
# characters allowed in figure file names
SAFE_RE = re.compile(r'[^A-Za-z0-9_.+-]+')
# counter of streamed figures (file name prefix) and its lock
_COUNT = dict(n=0)
_LOCK = threading.Lock()


# =============================================================================
# Define functions
# =============================================================================
def stream_dir() -> Optional[str]:
    """
    Get (and create) the stream folder

    :return: str or None, the folder (None = streaming is off)
    """
    path = os.environ.get(STREAM_ENV)
    if not path:
        return None
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        return None
    return path


def figure_title(figure: Any) -> str:
    """
    Get a readable title of a figure (suptitle, window label or the title
    of its first titled axes)

    :param figure: matplotlib Figure, the figure

    :return: str, the title ('' if none)
    """
    suptitle = getattr(figure, '_suptitle', None)
    if suptitle is not None and suptitle.get_text():
        return suptitle.get_text()
    if figure.get_label():
        return figure.get_label()
    for axis in figure.get_axes():
        if axis.get_title():
            return axis.get_title()
    return ''


def max_pickle_bytes() -> int:
    """
    Get the largest figure pickle kept (APEROCORE_PLOT_STREAM_MAX_MB)

    :return: int, the size in bytes (0 = never pickle)
    """
    try:
        value = float(os.environ.get(MAX_MB_ENV, DEFAULT_MAX_MB))
    except ValueError:
        value = DEFAULT_MAX_MB
    return max(0, int(value * 1024 * 1024))


def pickle_figure(figure: Any, path: str) -> Optional[str]:
    """
    Pickle a figure (detached from pyplot so loading it never creates a
    plot window) if it is not too big

    :param figure: matplotlib Figure, the figure
    :param path: str, the pickle file

    :return: str or None, the reason it was not pickled (None = saved)
    """
    limit = max_pickle_bytes()
    if limit == 0:
        return 'interactive figures are off'
    canvas = figure.canvas
    manager = getattr(canvas, 'manager', None)
    try:
        # without its manager the figure does not restore itself to pyplot
        canvas.manager = None
        data = pickle.dumps(figure, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as error:
        return 'cannot pickle the figure ({0})'.format(
            type(error).__name__)
    finally:
        canvas.manager = manager
    if len(data) > limit:
        return 'figure too large to keep interactive ({0:.0f} MB)'.format(
            len(data) / 1024 / 1024)
    try:
        with open(path, 'wb') as pfile:
            pfile.write(data)
    except OSError as error:
        return str(error)
    return None


def step_context() -> Dict[str, Any]:
    """
    Get where the program is now (aperocore.progress tags and step path)

    :return: dict, the context ({} if unknown)
    """
    try:
        from aperocore import progress
        return progress.context()
    except Exception:
        return dict()


def stream_figure(figure: Any) -> Optional[Dict[str, Any]]:
    """
    Save one figure into the stream folder and record it in the index

    :param figure: matplotlib Figure, the figure

    :return: dict or None, the index entry (None if streaming is off or
             saving failed)
    """
    directory = stream_dir()
    if directory is None:
        return None
    # optional description set by the program (figure.gui_info)
    info = getattr(figure, 'gui_info', None)
    info = info if isinstance(info, dict) else dict()
    title = str(info.get('title') or '') or figure_title(figure)
    extra = {key: str(info[key]) for key in ['description', 'name', 'func']
             if info.get(key)}
    with _LOCK:
        _COUNT['n'] += 1
        number = _COUNT['n']
    stem = SAFE_RE.sub('_', title.strip())[:60].strip('_') or 'figure'
    name = '{0:04d}-{1}-{2}.png'.format(number, os.getpid(), stem)
    path = os.path.join(directory, name)
    try:
        figure.savefig(path, dpi=STREAM_DPI)
    except Exception as error:
        entry = dict(file=None, title=title, time=time.time(),
                     error=str(error), pid=os.getpid())
    else:
        entry = dict(file=name, title=title, time=time.time(),
                     pid=os.getpid(), number=number)
        # the figure itself (interactive zoom / pan in the gui)
        fig_name = name[:-len('.png')] + FIGURE_EXT
        reason = pickle_figure(figure, os.path.join(directory, fig_name))
        if reason is None:
            entry['figure'] = fig_name
        else:
            entry['static_reason'] = reason
    entry.update(extra)
    # where the program was (e.g. the pogos stage and step)
    context = step_context()
    if context:
        entry['step'] = context
    try:
        with _LOCK:
            with open(os.path.join(directory, INDEX_NAME), 'a') as ifile:
                ifile.write(json.dumps(entry, default=str) + '\n')
    except OSError:
        return None
    return entry


def _stream_and_close(manager: Any) -> None:
    """
    Stream the figure of a figure manager and close it

    :param manager: FigureManagerBase, the manager

    :return: None
    """
    stream_figure(manager.canvas.figure)
    _pylab_helpers.Gcf.destroy(manager)


# =============================================================================
# Define classes
# =============================================================================
class FigureManagerStream(FigureManagerBase):
    """Figure manager whose show() streams the figure to the gui"""

    def show(self) -> None:
        """
        Stream this figure (fig.show())

        :return: None
        """
        stream_figure(self.canvas.figure)

    @classmethod
    def pyplot_show(cls, *, block: Optional[bool] = None) -> None:
        """
        Stream (and close) every open figure (plt.show()) - never blocks

        :param block: ignored (nothing is ever shown on screen)

        :return: None
        """
        _ = block
        for manager in list(_pylab_helpers.Gcf.get_all_fig_managers()):
            _stream_and_close(manager)


class FigureCanvasStream(FigureCanvasAgg):
    """Agg canvas using the streaming figure manager"""
    manager_class = FigureManagerStream


# the names matplotlib looks for in a backend module
FigureCanvas = FigureCanvasStream
FigureManager = FigureManagerStream


# =============================================================================
# End of code
# =============================================================================
