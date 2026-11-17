#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free regression tests for object file-browser presets and UI."""

from pathlib import Path
import shutil
import subprocess

import pytest
from flask import Flask
from jinja2 import ChoiceLoader, DictLoader

from apero.dev import get_base_params
from apero_ri.application import data_portal_view_helpers as views
from apero_ri.core import basket_funcs as basket


_PARAMS = get_base_params('SPIROU')
_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('preset, outputs', [
    ('ext2d', ['DRS_POST_E']),
    ('tcorr2d', ['DRS_POST_T']),
    ('tcorr1d', ['DRS_POST_S']),
])
def test_spectrum_presets(preset: str, outputs: list[str]) -> None:
    """Select exact output types, retaining processed-block and QC limits.

    :param preset: File-browser preset identifier.
    :param outputs: Expected product output types.
    :return: None.
    """
    all_outputs = ['DRS_POST_E', 'DRS_POST_T', 'DRS_POST_S',
                   'TELLU_TEMP', 'TELLU_TEMP_S1DW', 'TELLU_TEMP_S1DV',
                   'TELLU_TEMP_OTHER']
    rows = [dict(KW_OUTPUT=output, BLOCK_KIND=block, PASSED_ALL_QC=qc)
            for block in ['out', 'tmp']
            for qc in [0, 1]
            for output in all_outputs]
    expected = [dict(KW_OUTPUT=output, BLOCK_KIND='out', PASSED_ALL_QC=1)
                for output in outputs]

    assert basket.apply_preset_filter(rows, preset) == expected


def test_template_preset() -> None:
    """Find only the three template types, independent of file block and QC.

    :return: None.
    """
    outputs = ['TELLU_TEMP', 'TELLU_TEMP_S1DW', 'TELLU_TEMP_S1DV']
    templates = [dict(KW_OUTPUT=output, BLOCK_KIND=block, PASSED_ALL_QC=qc)
                 for output in outputs
                 for block in ['red', 'tellu']
                 for qc in [0, 1]]
    rows = templates + [dict(KW_OUTPUT=output)
                        for output in ['TELLU_TEMP_OTHER', 'DRS_POST_S']]

    assert basket.apply_preset_filter(rows, 'template') == templates


@pytest.mark.parametrize('language, template_label', [
    ('en', 'Templates'),
    ('fr', 'Modèles'),
    ('es', 'Plantillas'),
])
def test_public_object_page_hides_refresh_status(
    language: str, template_label: str,
) -> None:
    """Never expose administrative refresh failures on the object page.

    :param language: Requested browser language.
    :param template_label: Localized template preset label.
    :return: None.
    """
    app = Flask(__name__, template_folder=str(_ROOT / 'apero_ri/templates'))
    app.jinja_env.filters['tl'] = str
    app.jinja_env.globals['url_for'] = lambda *args, **kwargs: '/test'
    shell = '{% block doc_content %}{% endblock %}'
    loader = app.jinja_loader
    assert loader is not None
    app.jinja_env.loader = ChoiceLoader([
        DictLoader({'general/sidebar_base.html': shell}), loader])
    profile = dict(profile_id='test', instrument='SPIROU',
                   data=dict(general=dict(has_polarimetry=False)))
    with app.test_request_context(headers={'Accept-Language': language}):
        html = app.jinja_env.get_template(
            'data_portal/object_page.html').render(
                profile=profile, objname='TEST', page_label='Object',
                api_url='/test', user_permissions=[],
                plot_yaxis_zoom=dict(), plotable_output_types=[],
                frame_output_prefixes=[],
                file_browser_labels=views._file_browser_labels(),
                object_query_status=dict(status='failed'))

    assert 'object-product refresh' not in html
    assert 'Product data shown here may be stale' not in html
    assert 'data-preset="template"' in html
    assert f'>{template_label}</button>' in html
    assert '[s.fits]' in html
    assert '[t.fits]' in html
    assert '[e.fits]' in html


def test_file_browser_filters() -> None:
    """Exercise case-insensitive filters and preserved input in JavaScript.

    :return: None.
    """
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node.js is required for file-browser UI tests')
    script = Path(__file__).with_suffix('.cjs')
    subprocess.run([node, str(script)], check=True)
