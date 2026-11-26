#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prebuilt documentation snapshot and first-view object cache tests."""

from pathlib import Path

import pytest
from apero import dev

from apero_ri.core import docs, plot_cache
from apero_ri.plots import plot_obj_targetinfo


@pytest.fixture
def doc_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point docs at an isolated tree with clean module caches."""
    assert dev is not None
    root = tmp_path / 'ari'
    pages = root / '1.0' / 'home' / 'docs'
    (pages / 'guide').mkdir(parents=True)
    (pages / 'index.md').write_text('# Home\n', encoding='utf-8')
    (pages / 'guide' / 'index.md').write_text(
        '---\ncard_label: Guide\n---\n# Guide\n', encoding='utf-8')
    (pages / 'guide' / 'start.md').write_text('# Start\n\nHello\n',
                                               encoding='utf-8')
    (root / 'versions.yaml').write_text(
        'versions:\n  - id: "1.0"\n    name: One\n', encoding='utf-8')
    monkeypatch.setattr(docs, 'DOC_ROOT', root)
    monkeypatch.setattr(docs, 'VERSIONS_FILE', root / 'versions.yaml')
    monkeypatch.setitem(docs._SNAPSHOT_STATE, 'dir', None)
    for cache in (docs._DOC_VERSIONS_CACHE, docs._DOC_CHILDREN_CACHE,
                  docs._DOC_CHILDREN_GENERATION, docs._DOC_SIDEBAR_CACHE,
                  docs._DOC_SEARCH_CACHE, docs._DOC_RENDER_CACHE,
                  docs._SNAPSHOTS, docs._SNAPSHOT_CHECKED,
                  docs._SNAPSHOT_FILE_MTIME):
        cache.clear()
    docs.set_snapshot_dir(tmp_path / 'data')
    return pages


def test_snapshot_serves_without_rendering(
        doc_tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A built snapshot persists and serves pages, cards and search."""
    status = docs.refresh_snapshots()
    assert status['1.0'].startswith('rebuilt')
    assert docs.refresh_snapshots() == {'1.0': 'up to date'}
    snap_file = doc_tree.parents[3] / 'data' / 'docs_cache' / '1.0.json'
    assert snap_file.is_file()

    def fail_render(text: str) -> str:
        """Reject a live markdown render."""
        pytest.fail('Snapshot page was re-rendered')

    monkeypatch.setattr(docs, 'render_markdown', fail_render)
    # A fresh process only has the file on disk.
    docs._SNAPSHOTS.clear()
    docs._SNAPSHOT_CHECKED.clear()
    docs._SNAPSHOT_FILE_MTIME.clear()
    raw, html, version, _meta = docs.get_doc_content('guide/start', '1.0')
    assert version == '1.0'
    assert 'Hello' in raw and '<h1' in html
    cards, _, _ = docs.get_doc_cards('guide', '1.0')
    assert [card['label'] for card in cards] == ['Start']
    labels = [item['label'] for item in docs.get_search_index('1.0')]
    assert 'Start' in labels
    text, etag = docs.get_search_index_json('1.0')
    assert '"items"' in text and etag


def test_edited_page_bypasses_stale_snapshot(doc_tree: Path) -> None:
    """Editing a source page is visible at once and triggers a rebuild."""
    docs.refresh_snapshots()
    page = doc_tree / 'guide' / 'start.md'
    page.write_text('# Start\n\nChanged\n', encoding='utf-8')
    raw, _html, _version, _meta = docs.get_doc_content('guide/start', '1.0')
    assert 'Changed' in raw
    assert docs.refresh_snapshots()['1.0'].startswith('rebuilt')


def test_docs_snapshot_task(doc_tree: Path, tmp_path: Path) -> None:
    """The GLOBAL task is enabled by default and writes the snapshot."""
    from apero_ri import tasks

    assert tasks.TYPE['DOCS_SNAPSHOT'] == 'GLOBAL'
    assert tasks.ENABLED['DOCS_SNAPSHOT']
    assert 'DOCS_SNAPSHOT' not in tasks.IMPORT_ERRORS
    messages = []
    params = dict(LOCAL_DATA_DIR=str(tmp_path / 'task'),
                  TASK_LOGGER=messages.append)
    task = tasks.TASK_LIST['DOCS_SNAPSHOT']()
    task.run_job(params)
    assert (tmp_path / 'task' / 'docs_cache' / '1.0.json').is_file()
    assert messages and '1.0' in messages[0]


def test_object_warm_markers(tmp_path: Path) -> None:
    """An object is warm only once every first-view group is cached."""
    assert dev is not None
    aparams = {'database-update': dict(LOG_TABLENAME='t1')}
    root = plot_cache.resolve_cache_root(tmp_path)
    pdir = plot_cache._profile_dir(root, 'SPIROU', 'prof')
    plot_cache._save_meta(pdir, dict(db_updates=dict(LOG_TABLENAME='t1')))
    warm_args = [tmp_path, 'SPIROU', 'prof', 'Star', aparams]
    assert not plot_cache.is_object_warm(*warm_args)
    for group in plot_cache.OBJECT_WARM_GROUPS:
        plot_cache.mark_object_group_warm(root, 'SPIROU', 'prof', 'STAR',
                                          group)
    assert plot_cache.is_object_warm(*warm_args)
    aparams['database-update'] = dict(LOG_TABLENAME='t2')
    assert not plot_cache.is_object_warm(*warm_args)


def test_neighborhood_never_blocks_request(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A cache miss starts a background fetch instead of querying."""
    assert dev is not None
    started = []
    monkeypatch.setattr(plot_obj_targetinfo, 'prefetch_20pc_neighborhood',
                        started.append)
    cache_path = plot_obj_targetinfo.neighborhood_cache_path(tmp_path)
    items = plot_obj_targetinfo.load_or_query_20pc_neighborhood(
        cache_path=cache_path, allow_query=False)
    assert items == []
    assert started == [cache_path]
