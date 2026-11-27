#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keep queue dashboard recovery independent of its worker process.

The supervisor (public port, worker restart, recovery page) is the generic
gui supervisor shared with other guis (aperocore.gui.server); this module
adds the APERO queue worker variable and the recovery page texts from the
language database.
"""
from typing import List, Tuple

from aperocore.base import base
from aperocore import drs_lang
from aperocore.gui import server as gui_server

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.processing.drs_queue_server'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
# environment variable telling the dashboard worker its private port
WORKER_PORT_ENV = 'APERO_QUEUE_GUI_WORKER_PORT'
# the shared supervisor settings (see aperocore.gui.server)
REQUEST_TIMEOUT = gui_server.REQUEST_TIMEOUT
WORKER_STOP_TIMEOUT = gui_server.WORKER_STOP_TIMEOUT
# the recovery request handler (see aperocore.gui.server)
RecoveryHandler = gui_server.RecoveryHandler
textentry = drs_lang.textentry


# =============================================================================
# Define classes
# =============================================================================
class QueueServer(gui_server.SupervisorServer):
    """Supervise a disposable dashboard behind a stable public HTTP port."""

    def __init__(self, address: Tuple[str, int], command: List[str]) -> None:
        """Bind the public listener without starting the worker.

        :param address: Public bind host and port.
        :param command: Original queue command, including its interpreter.
        :return: None.
        """
        # recovery page texts come from the language database
        skwargs = dict(worker_env=WORKER_PORT_ENV, title='APERO Queue',
                       down_message=textentry('40-513-00044'),
                       restart_label=textentry('40-513-00045'),
                       restart_prompt=textentry('40-513-00046'))
        super().__init__(address, command, **skwargs)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
