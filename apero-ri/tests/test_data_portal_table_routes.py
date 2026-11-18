#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for data portal table route dispatch."""

from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from apero_ri.application import data_portal_view_helpers


# =============================================================================
# Define functions
# =============================================================================
@pytest.mark.parametrize('table_path, expected', [
    ('object-table', 'objects'),
    ('observation-table', 'observations'),
])
def test_table_routes_dispatch_independently(
    app: Flask,
    client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
    table_path: str,
    expected: str,
) -> None:
    """Check that each table URL invokes its corresponding view helper.

    :param app: Isolated ARI application fixture.
    :param client: Flask client for the isolated application.
    :param monkeypatch: Fixture for replacing the data-dependent helpers.
    :param table_path: Table URL suffix to request.
    :param expected: Response identifying the expected view helper.
    :return: None.
    """
    object_view = Mock(return_value='objects')
    obs_view = Mock(return_value='observations')
    monkeypatch.setattr(data_portal_view_helpers, 'ri_object_table_view',
                        object_view)
    monkeypatch.setattr(data_portal_view_helpers, 'ri_obs_table_view',
                        obs_view)

    response = client.get(f'/data_portal/test_profile/{table_path}')

    assert response.status_code == 200
    assert response.get_data(as_text=True) == expected
    selected = object_view if expected == 'objects' else obs_view
    other = obs_view if expected == 'objects' else object_view
    selected.assert_called_once_with(app, profile_id='test_profile')
    other.assert_not_called()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================