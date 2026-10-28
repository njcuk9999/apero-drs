#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free regressions for Markdown description lookup and retirement."""

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from astropy.table import Table

from apero.tools.module.documentation import ari_docs
from apero.tools.module.documentation import drs_documentation
from apero.utils import drs_recipe


@pytest.mark.parametrize('kind', ari_docs.DESC_KINDS)
def test_description_path_uses_instrument_kind_and_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str,
) -> None:
    """Use a temporary root and each kind to verify the source path."""
    monkeypatch.setattr(ari_docs, 'DESC_ROOT', tmp_path)

    result = ari_docs.description_path('NIRPS_HA', kind, 'apero_extract')

    assert result == tmp_path / 'nirps_ha' / kind / 'apero_extract.md'


def test_read_description_prefers_instrument_then_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify instrument preference, default fallback, and missing content."""
    monkeypatch.setattr(ari_docs, 'DESC_ROOT', tmp_path)
    shared = tmp_path / 'default' / 'recipes' / 'apero_extract.md'
    shared.parent.mkdir(parents=True)
    shared.write_text('---\nalgorithms: [extraction]\n---\nShared prose.\n')

    meta, body = ari_docs.read_description('SPIROU', 'recipes', 'apero_extract')
    assert meta == dict(algorithms=['extraction'])
    assert body == 'Shared prose.\n'

    local = tmp_path / 'spirou' / 'recipes' / 'apero_extract.md'
    local.parent.mkdir(parents=True)
    local.write_text('---\nreferences: [Local paper]\n---\nLocal prose.\n')

    meta, body = ari_docs.read_description('SPIROU', 'recipes', 'apero_extract')
    assert meta == dict(references=['Local paper'])
    assert body == 'Local prose.\n'
    shared_result = ari_docs.read_description('NIRPS_HE', 'recipes',
                                              'apero_extract')
    assert shared_result == (dict(algorithms=['extraction']), 'Shared prose.\n')
    other_kind = ari_docs.read_description('SPIROU', 'dev_tools',
                                           'apero_extract')
    assert other_kind == (dict(), '')
    assert ari_docs.read_description('default', 'recipes', 'missing') == (
        dict(), '')


@pytest.mark.parametrize('kind', ['recipes', 'user_tools', 'dev_tools'])
def test_build_recipe_page_needs_no_description_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    spirou_params: Any, kind: str,
) -> None:
    """Build from a fake summary and dev params without legacy metadata."""
    monkeypatch.setattr(ari_docs, 'DESC_ROOT', tmp_path / 'descriptions')
    source = tmp_path / 'descriptions' / 'spirou' / kind / 'apero_example.md'
    source.parent.mkdir(parents=True)
    prose = ('---\nalgorithms: [extraction]\nreferences: [Example paper]\n'
             '---\nAuthored **Markdown**.\n\n```mermaid\n'
             'flowchart TD\n    Input --> Output\n```\n')
    source.write_text(prose, encoding='utf-8')
    decoy = source.with_name('short.md')
    decoy.write_text('Wrong short-name lookup.\n', encoding='utf-8')
    summary = dict(NAME='apero_example.py', SHORTNAME='SHORT',
                   RECIPE_TYPE='recipe', RECIPE_KIND='science',
                   USAGE='apero_example.py INPUT', LPOS=['INPUT // Input file'],
                   LOPT=['--test // Test mode'], LSOPT=[], OUTDIR='reduced',
                   OUTPUTS=[], DEBUG_PLOTS=[], SUMMARY_PLOTS=[])
    recipe = SimpleNamespace(description='Definition fallback')
    recipe.summary = lambda params: summary
    assert not hasattr(recipe, 'description_file')
    assert 'DESCRIPTION_FILE' not in summary
    outdir = tmp_path / 'generated'

    page_args = [spirou_params, None, recipe, 'SPIROU', kind, outdir]
    ari_docs.build_recipe_page(*page_args)

    page = (outdir / 'short.md').read_text(encoding='utf-8')
    assert '# apero_example' in page
    assert 'Authored **Markdown**.' in page
    assert 'flowchart TD\n    Input --> Output\n```' in page
    assert 'Wrong short-name lookup.' not in page
    assert 'Definition fallback' not in page
    assert 'apero_example.py INPUT' in page
    assert '| `INPUT` | Input file |' in page
    assert '| `--test` | Test mode |' in page
    assert '/docs/algorithms/extraction' in page
    assert '- Example paper' in page
    assert source.read_text(encoding='utf-8') == prose


@pytest.mark.parametrize('instrument', ['default', 'spirou',
                                        'nirps_ha', 'nirps_he'])
def test_recipe_definitions_do_not_use_rst_metadata(instrument: str) -> None:
    """Parse each definition module without importing instrument profiles."""
    instruments = Path(__file__).resolve().parents[1] / 'apero' / 'instruments'
    source = instruments / instrument / 'recipe_definitions.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr != 'description_file', source
        if isinstance(node, ast.keyword):
            assert node.arg != 'description_file', source
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr != 'default_rfile', source
            elif isinstance(node.func, ast.Name):
                assert node.func.id != 'default_rfile', source


def test_legacy_sequence_summary_needs_no_rst_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    spirou_params: Any,
) -> None:
    """Compile a sequence table without a description-file attribute."""
    sequence = drs_recipe.DrsRunSequence('example', 'SPIROU')
    assert not hasattr(sequence, 'description_file')
    monkeypatch.setattr(sequence, 'summary_table',
                        lambda: Table(dict(recipe=['apero_example.py'])))
    monkeypatch.setattr(drs_documentation, 'WLOG', lambda *args, **kwargs: None)

    summary = drs_documentation._compile_sequence(
        spirou_params, sequence, str(tmp_path))

    assert summary['NAME'] == 'example'
    assert 'DESCRIPTION_FILE' not in summary
    assert (tmp_path / 'rout_example.csv').exists()


def test_legacy_rst_description_sources_are_retired() -> None:
    """Prevent legacy narrative fragments from being reintroduced."""
    resources = ari_docs.REPO_ROOT / 'documentation' / 'working' / 'resources'

    assert not list(resources.glob('*/descriptions/*.rst'))