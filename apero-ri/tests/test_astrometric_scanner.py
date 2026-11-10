#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for the startup astrometric issue scan."""

from apero_ri.core import astrometric_scanner as scanner
from apero_ri.core import issues


def test_pending_scan_loads_issue_store_once(tmp_path, monkeypatch):
    """Existing open issues are skipped without re-reading the store."""
    pending = tmp_path / 'astrometrics' / 'pending'
    pending.mkdir(parents=True)
    for name in ('OLD', 'NEW1', 'NEW2'):
        (pending / f'{name}.yaml').write_text(
            f'APERO_NAME: {name}\n', encoding='utf-8'
        )
    issues.create_issue(
        tmp_path, kind='astrometric', reason='pending',
        apero_name='OLD', label=scanner.LABEL_VERIFY,
        dedupe_key='verify:OLD', visibility='monitor',
    )
    original_load = issues._load
    calls = []

    def counting_load(data_dir):
        calls.append(data_dir)
        return original_load(data_dir)

    monkeypatch.setattr(issues, '_load', counting_load)
    count = scanner.scan_pending_verification(
        tmp_path, tmp_path / 'astrometrics'
    )

    assert count == 3
    assert len(calls) == 3
    names = sorted(it['apero_name'] for it in original_load(tmp_path))
    assert names == ['NEW1', 'NEW2', 'OLD']

    calls.clear()
    assert scanner.scan_pending_verification(
        tmp_path, tmp_path / 'astrometrics'
    ) == 3
    assert len(calls) == 1
    assert len(original_load(tmp_path)) == 3
