#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free regression tests for object file-browser presets and UI."""

from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess

import pytest
from flask import Flask
from jinja2 import ChoiceLoader, DictLoader

from apero.dev import get_base_params
from apero_ri.application import data_portal_view_helpers as views
from apero_ri.application import query_db_api_helpers as query_api
from apero_ri.core import auth
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


@pytest.mark.parametrize('preset, output', [
    ('default', 'DRS_POST_T'),
    ('ext2d', 'DRS_POST_E'),
    ('tcorr2d', 'DRS_POST_T'),
    ('tcorr1d', 'DRS_POST_S'),
    ('polar', 'DRS_POST_P'),
    ('ccfrv', 'DRS_POST_V'),
])
def test_processed_presets_accept_missing_qc(preset: str, output: str) -> None:
    """Include unknown QC but exclude failures and non-output blocks.

    :param preset: File-browser preset identifier.
    :param output: Output type selected by the preset.
    :return: None.
    """
    rows = [dict(KW_OUTPUT=output, BLOCK_KIND=block, PASSED_ALL_QC=qc)
            for block in ['out', 'red']
            for qc in [None, 0, 1]]
    expected = [rows[0], rows[2]]

    assert basket.apply_preset_filter(rows, preset) == expected


@pytest.mark.parametrize('preset, suffix', [
    ('ext2d', 'e.fits'),
    ('tcorr2d', 't.fits'),
    ('tcorr1d', 's.fits'),
    ('polar', 'p.fits'),
    ('ccfrv', 'v.fits'),
])
@pytest.mark.parametrize('version, expected', [('v7', 1), ('v8', 0)])
def test_file_browser_legacy_pp_by_profile_version(
    monkeypatch: pytest.MonkeyPatch, preset: str, suffix: str,
    version: str, expected: int,
) -> None:
    """Only v7 profiles match out-block DRS_PP using the product suffix.

    :param monkeypatch: Pytest fixture replacing external dependencies.
    :param preset: Preset selected in the request.
    :param suffix: Expected filename suffix.
    :param version: Instrument settings version.
    :param expected: Number of expected matching files.
    :return: None.
    """
    profile_data = dict(APERO_INSTRUMENT_PROFILE=f'nirps_ha_{version}.yaml')
    profile_data = auth._hydrate_profile_data(profile_data, 'NIRPS_HA')
    profile = dict(profile_id='test', instrument='NIRPS_HA', data=profile_data)
    rows = [
        dict(FILENAME='file' + suffix, BLOCK_KIND='out', KW_OUTPUT='DRS_PP',
             KW_RUN_ID='R1', PASSED_ALL_QC=None),
        dict(FILENAME='file' + suffix, BLOCK_KIND='red', KW_OUTPUT='DRS_PP',
             KW_RUN_ID='R1', PASSED_ALL_QC=1),
        dict(FILENAME='file' + suffix + '.bak', BLOCK_KIND='out',
             KW_OUTPUT='DRS_PP', KW_RUN_ID='R1', PASSED_ALL_QC=1),
        dict(FILENAME='file' + suffix, BLOCK_KIND='out', KW_OUTPUT='DRS_PP',
             KW_RUN_ID='R1', PASSED_ALL_QC=0),
        dict(FILENAME='file' + suffix, BLOCK_KIND='out', KW_OUTPUT='OTHER',
             KW_RUN_ID='R1', PASSED_ALL_QC=1),
        dict(FILENAME='file' + suffix, BLOCK_KIND='out', KW_OUTPUT='DRS_PP',
             KW_RUN_ID='R2', PASSED_ALL_QC=1),
    ]
    monkeypatch.setattr(query_api, 'get_accessible_profiles',
                        lambda *args: [profile])
    monkeypatch.setattr(query_api, 'get_public_permissions',
                        lambda: {'view.data_portal'})
    monkeypatch.setattr(
        basket, 'load_ftable_rows',
        lambda base, instr, pid, obj, kind:
            (rows if kind == 'all' else [], None, None))
    ari = SimpleNamespace(
        args=SimpleNamespace(data_dir=None), ari_groups={},
        _get_api_user=lambda: None,
        _get_user_accessible_run_ids=lambda user, instr: {'R1'})
    app = Flask(__name__)
    url = f'/?profile_id=test&objname=Proxima&preset={preset}'
    with app.test_request_context(url):
        response = query_api.api_file_browser(ari)

    assert response.get_json()['rows'] == [
        dict(rows[0], ACCESS_RUN_ID='R1')
    ][:expected]


def test_v07_telluric_preset_includes_both_indexed_output_types() -> None:
    """Include all 148 t.fits products in the reported Proxima case.

    :return: None.
    """
    rows = [dict(FILENAME=f'file{index}t.fits', BLOCK_KIND='out',
                 KW_OUTPUT='DRS_POST_T', PASSED_ALL_QC=None)
            for index in range(6)]
    rows += [dict(FILENAME=f'legacy{index}t.fits', BLOCK_KIND='out',
                  KW_OUTPUT='DRS_PP', PASSED_ALL_QC=None)
             for index in range(142)]

    assert len(basket.apply_preset_filter(rows, 'tcorr2d', True)) == 148
    assert len(basket.apply_preset_filter(rows, 'tcorr2d', False)) == 6


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
