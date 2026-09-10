#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared pytest setup for apero-drs tests."""

import pytest

from apero.dev import get_base_params

# Configure DRS_UCONFIG before pytest imports APERO modules from test files.
_SPIROU_PARAMS = get_base_params('SPIROU')


@pytest.fixture(scope='session')
def spirou_params():
	"""Return profile-free default SPIROU parameters for unit tests."""
	return _SPIROU_PARAMS

