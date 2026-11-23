#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Centralised logging configuration.

Import ``get_logger`` in any module and use it instead of bare print() or
swallowed exceptions:

    from apero_ri.core.log import get_logger
    log = get_logger(__name__)
    log.warning("Something went wrong: %s", exc)

Calling ``configure_logging()`` once at app startup sets the format and level
for the whole ``apero_ri`` namespace.  If it is never called the stdlib
defaults apply, which is still functional.
"""

import logging
import sys
from typing import Optional

_ROOT_LOGGER = "apero_ri"


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the apero_ri namespace."""
    if not name.startswith(_ROOT_LOGGER):
        name = f"{_ROOT_LOGGER}.{name}"
    return logging.getLogger(name)


def configure_logging(
    level: int = logging.INFO,
    fmt: Optional[str] = None,
    datefmt: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """Configure the apero_ri root logger.

    Safe to call multiple times; subsequent calls are no-ops once handlers
    have been attached.
    """
    logger = logging.getLogger(_ROOT_LOGGER)
    if logger.handlers:
        return  # already configured
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt or "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt=datefmt,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
