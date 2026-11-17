#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for dependency reporting during recipe startup."""

from importlib import metadata
from pathlib import Path

import pytest

from apero.dev import get_base_params
from apero.utils import drs_startup


def test_dependency_report_uses_installed_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Report applicable dependencies and missing distributions accurately."""
    get_base_params('SPIROU')
    requirements = [
        'sample-package>=1,<3',
        'missing-package==2',
        'direct-package @ https://example.invalid/package.zip',
        'future-package; python_version < "2"',
        'optional-package; extra == "dev"',
    ]

    def requires(name: str) -> list[str]:
        """Return synthetic installed APERO requirement metadata."""
        assert name == 'apero'
        return requirements

    def version(name: str) -> str:
        """Return distribution versions without importing the packages."""
        if name == 'missing-package':
            raise metadata.PackageNotFoundError(name)
        assert name in ('sample-package', 'direct-package')
        return '1.5'

    monkeypatch.setattr(metadata, 'requires', requires)
    monkeypatch.setattr(metadata, 'version', version)
    result = drs_startup._display_python_modules()
    assert 'sample-package: 1.5' in result
    assert '<3,>=1' in result
    assert 'missing-package: not installed' in result
    assert 'direct-package: 1.5' in result
    assert 'https://example.invalid/package.zip' in result
    assert 'future-package' not in result
    assert 'optional-package' not in result


def test_system_information_does_not_read_requirements_file(
    spirou_params, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the recipe startup logging path with installed metadata."""
    monkeypatch.setattr(drs_startup.apero_base, 'REQUIREMENTS',
                        tmp_path / 'requirements.txt', raising=False)
    monkeypatch.setattr(metadata, 'requires', lambda name: ['numpy>=1'])
    result = drs_startup._display_system_info(
        spirou_params, return_message=True
    )
    assert 'numpy:' in result
    assert 'req>=1' in result


def test_system_information_uses_real_distribution_metadata(
    spirou_params,
) -> None:
    """Verify installed APERO metadata reaches the startup log."""
    result = drs_startup._display_system_info(
        spirou_params, return_message=True
    )
    assert f"numpy: {metadata.version('numpy')}" in result
