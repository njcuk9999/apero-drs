#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared pytest setup for apero-drs tests."""

import os
import tempfile
from pathlib import Path

# Many apero modules require DRS_UCONFIG at import time.
_DRS_CFG = Path(tempfile.mkdtemp(prefix='apero_drs_test_cfg_'))
(_DRS_CFG / 'database.yaml').write_text('{}', encoding='utf-8')
(_DRS_CFG / 'install.yaml').write_text('{}', encoding='utf-8')
os.environ.setdefault('DRS_UCONFIG', str(_DRS_CFG))

