#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive matplotlib figures in a browser gui (the real matplotlib
toolbar: zoom / pan / home / back / forward, shared axes, coordinates)

aperocore.gui.mpl_stream pickles every streamed figure ({name}.mplfig).
Opening one in the gui unpickles a private copy into matplotlib's own
browser backend (backend_webagg_core - the one behind WebAgg and the
notebook backend) and drives it from matplotlib's mpl.js. matplotlib
normally talks to mpl.js over a websocket; the gui http server has none,
so the browser posts its events (send) and long-polls for matplotlib's
messages and images (poll) - see GUI.mpl in gui_files.js.

Loading a pickle runs code: only figures inside the roots a gui allows
(its own stream folder) with the .mplfig extension are ever loaded.

pyplot is never used (the gui server must not open plot windows); figures
are drawn with Agg. Sessions not polled for SESSION_IDLE seconds are
closed, and at most MAX_SESSIONS are open at once.

Created on 2026-11-27

@author: cook
"""
import base64
import json
import os
import pickle
import threading
import time
import uuid
import warnings
from typing import Any, Dict, List, Optional

from aperocore.gui import files as gui_files

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.mpl_view.py'
# the extension of pickled figures (see mpl_stream.FIGURE_EXT)
FIGURE_EXT = '.mplfig'
# the most figures open at once (the oldest is closed first)
MAX_SESSIONS = 6
# seconds without a poll before a figure is closed
SESSION_IDLE = 120.0
# the longest a poll waits for messages (below the supervisor's request
#   timeout)
MAX_WAIT = 15.0
# messages handled here rather than by matplotlib (websocket details)
SOCKET_MESSAGES = ['supports_binary']
# the matplotlib web assets (mpl.js / css / toolbar icons) once read
_ASSETS: Dict[str, Any] = dict()
# the open figures: session id -> FigureSession
_SESSIONS: Dict[str, 'FigureSession'] = dict()
# guards the session table
_LOCK = threading.Lock()


# =============================================================================
# Define classes
# =============================================================================
class FigureViewError(Exception):
    """A figure that cannot be loaded or a session that does not exist"""


class FigureSession:
    """
    One open figure: a private copy of the pickled figure driven by
    matplotlib's browser backend, with a message queue standing in for
    the websocket to mpl.js
    """

    def __init__(self, real: str) -> None:
        """
        Load the figure into matplotlib's browser backend

        :param real: str, the checked figure path

        :raises FigureViewError: if the figure cannot be loaded

        :return: None
        """
        self.id = uuid.uuid4().hex
        self.path = real
        self.last = time.time()
        self.closed = False
        # messages for the browser (json strings / png data uris)
        self.queue: List[str] = []
        self.cond = threading.Condition()
        # matplotlib figures are not thread safe: one event at a time
        self.lock = threading.RLock()
        figure, self.warning = _load_figure(real)
        manager_class = _manager_class()
        from matplotlib.backends import backend_webagg_core as wcore
        canvas = wcore.FigureCanvasWebAggCore(figure)
        self.manager = manager_class(canvas, 1)
        self.title = _figure_title(figure)
        # registers this session as the figure's "websocket" (matplotlib
        #   sends the figure size and asks for a refresh)
        with self.lock:
            self.manager.add_web_socket(self)

    # the websocket interface matplotlib sends through
    def send_json(self, content: Dict[str, Any]) -> None:
        """
        Queue a json message for the browser (called by matplotlib)

        :param content: dict, the message

        :return: None
        """
        self._put(json.dumps(content, default=str))

    def send_binary(self, blob: bytes) -> None:
        """
        Queue an image for the browser (called by matplotlib)

        :param blob: bytes, the png (full or diff image)

        :return: None
        """
        self._put('data:image/png;base64,'
                  + base64.b64encode(blob).decode('ascii'))

    def _put(self, message: str) -> None:
        """
        Add a message to the queue and wake the waiting poll

        :param message: str, the message

        :return: None
        """
        with self.cond:
            self.queue.append(message)
            self.cond.notify_all()

    def handle(self, messages: List[Any]) -> None:
        """
        Pass browser events (mouse, keys, toolbar, draw requests) to
        matplotlib in order

        :param messages: list of str / dict, the mpl.js messages

        :return: None
        """
        self.last = time.time()
        with self.lock:
            for message in messages:
                try:
                    content = (json.loads(message)
                               if isinstance(message, str) else message)
                except ValueError:
                    continue
                if not isinstance(content, dict):
                    continue
                if content.get('type') in SOCKET_MESSAGES:
                    continue
                try:
                    self.manager.handle_json(content)
                except Exception as error:
                    # one bad event must not end the session
                    self.send_json(dict(type='message', message='error: '
                                        '{0}'.format(error)))

    def poll(self, wait: float) -> List[str]:
        """
        Get the queued messages (waiting up to wait seconds for one)

        :param wait: float, the longest wait in seconds

        :return: list of str, the messages in order ([] after the wait)
        """
        self.last = time.time()
        with self.cond:
            if not self.queue and not self.closed:
                self.cond.wait(max(0.0, min(wait, MAX_WAIT)))
            messages, self.queue = self.queue, []
        self.last = time.time()
        return messages

    def close(self) -> None:
        """
        Close the session (wakes a waiting poll)

        :return: None
        """
        with self.cond:
            self.closed = True
            self.cond.notify_all()


# =============================================================================
# Define functions
# =============================================================================
def _manager_class() -> Any:
    """
    Get matplotlib's browser figure manager with its navigation toolbar
    (FigureManagerWebAgg only gets a toolbar from its subclasses, as in
    the notebook backend)

    :return: class, the figure manager class
    """
    if 'manager' not in _ASSETS:
        from matplotlib.backends import backend_webagg_core as wcore

        class _Manager(wcore.FigureManagerWebAgg):
            """FigureManagerWebAgg with the standard toolbar"""
            _toolbar2_class = wcore.NavigationToolbar2WebAgg
            ToolbarCls = wcore.NavigationToolbar2WebAgg

        _ASSETS['manager'] = _Manager
    return _ASSETS['manager']


def _load_figure(real: str) -> Any:
    """
    Unpickle a figure (a fresh copy for every session)

    :param real: str, the checked figure path

    :raises FigureViewError: if it cannot be unpickled

    :return: tuple(Figure, str or None = warnings while loading)
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            with open(real, 'rb') as pfile:
                figure = pickle.load(pfile)
        except Exception as error:
            raise FigureViewError('cannot load the figure ({0}: {1})'
                                  .format(type(error).__name__, error))
    if not hasattr(figure, 'get_axes'):
        raise FigureViewError('not a matplotlib figure')
    warning = '; '.join(str(item.message) for item in caught) or None
    return figure, warning


def _figure_title(figure: Any) -> str:
    """
    Get a readable title of a figure (suptitle, label, first axes title)

    :param figure: matplotlib Figure

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


def check_figure(path: str, roots: List[str]) -> str:
    """
    Check a figure path is a pickled figure inside the allowed roots

    :param path: str, the requested path
    :param roots: list of str, the allowed roots (empty = none allowed)

    :raises FigureViewError: if the figure may not be loaded

    :return: str, the resolved path
    """
    if not roots:
        raise FigureViewError('interactive figures are not enabled')
    try:
        real = gui_files.check_path(path, roots)
    except gui_files.FileAccessError as error:
        raise FigureViewError(str(error))
    if not real.endswith(FIGURE_EXT) or not os.path.isfile(real):
        raise FigureViewError('not an interactive figure: {0}'.format(path))
    return real


def _expire() -> None:
    """
    Close idle sessions and the oldest ones above MAX_SESSIONS - call
    with _LOCK held

    :return: None
    """
    now = time.time()
    for sid in [sid for sid, session in _SESSIONS.items()
                if now - session.last > SESSION_IDLE]:
        _SESSIONS.pop(sid).close()
    while len(_SESSIONS) >= MAX_SESSIONS:
        oldest = min(_SESSIONS, key=lambda key: _SESSIONS[key].last)
        _SESSIONS.pop(oldest).close()


def open_figure(path: str, roots: List[str]) -> Dict[str, Any]:
    """
    Open a pickled figure for interactive viewing

    :param path: str, the figure (.mplfig)
    :param roots: list of str, the roots figures may be loaded from

    :raises FigureViewError: if the figure cannot be loaded

    :return: dict(id = the session id, title, warning)
    """
    real = check_figure(path, roots)
    with _LOCK:
        _expire()
    session = FigureSession(real)
    with _LOCK:
        _SESSIONS[session.id] = session
    return dict(id=session.id, title=session.title,
                warning=session.warning)


def get_session(sid: str) -> FigureSession:
    """
    Get an open session

    :param sid: str, the session id

    :raises FigureViewError: if it is not open (closed or expired)

    :return: FigureSession, the session
    """
    with _LOCK:
        session = _SESSIONS.get(str(sid))
    if session is None:
        raise FigureViewError('figure closed (open it again)')
    return session


def close_figure(sid: str) -> None:
    """
    Close a session (nothing happens if it is not open)

    :param sid: str, the session id

    :return: None
    """
    with _LOCK:
        session = _SESSIONS.pop(str(sid), None)
    if session is not None:
        session.close()


def javascript() -> str:
    """
    Get matplotlib's mpl.js with its toolbar items and save formats

    :return: str, the javascript
    """
    if 'js' not in _ASSETS:
        _ASSETS['js'] = _manager_class().get_javascript()
    return _ASSETS['js']


def stylesheet() -> str:
    """
    Get matplotlib's figure / toolbar css (only class scoped rules: the
    page level css of matplotlib's own pages is left out)

    :return: str, the css
    """
    if 'css' not in _ASSETS:
        folder = os.path.join(_manager_class().get_static_file_path(),
                              'css')
        parts = []
        for name in ['fbm.css', 'mpl.css']:
            with open(os.path.join(folder, name), 'r') as cfile:
                parts.append(cfile.read())
        _ASSETS['css'] = '\n'.join(parts)
    return _ASSETS['css']


def toolbar_image(name: str) -> Optional[bytes]:
    """
    Get a toolbar icon of matplotlib (mpl.js loads _images/{name})

    :param name: str, the file name (e.g. home.png)

    :return: bytes or None (unknown icon)
    """
    import matplotlib
    if (not name or '/' in name or '\\' in name or name.startswith('.')
            or not name.endswith('.png')):
        return None
    path = os.path.join(matplotlib.get_data_path(), 'images', name)
    if not os.path.isfile(path):
        return None
    with open(path, 'rb') as ifile:
        return ifile.read()


# =============================================================================
# End of code
# =============================================================================
