#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for reusable collection display preferences."""

from pathlib import Path
import shutil
import subprocess

from flask import Flask
import pytest
import yaml

from apero_ri.application import ariapp_impls
from apero_ri.application import monitor_view_helpers
from apero_ri.application import page_view_helpers
from apero_ri.core import user_data as ud


def test_user_page_view_preferences_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Persist one page without discarding another page or core settings."""
    path = tmp_path / "prefs.yaml"
    monkeypatch.setattr(ud, "_prefs_path", lambda username: path)
    ud.save_user_prefs(
        "alice",
        {
            "timezone": "Europe/Paris",
            "page_views": {
                "home.admin_portal": {"view": "list", "sort": "desc"}
            },
        },
    )

    prefs = ud.load_user_prefs("alice")

    assert prefs["timezone"] == "Europe/Paris"
    assert prefs["page_views"]["home.admin_portal"] == {
        "view": "list", "sort": "desc"}
    assert yaml.safe_load(path.read_text(encoding="utf-8")) == prefs


def test_page_view_settings_validate_saved_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use valid saved choices and ignore corrupt preference values."""
    monkeypatch.setattr(
        page_view_helpers.ud,
        "load_user_prefs",
        lambda username: {
            "page_views": {
                "home.admin_portal": {"view": "list", "sort": "desc"},
                "home.data_portal": {"view": "unknown", "sort": "sideways"},
            }
        },
    )

    assert page_view_helpers._page_view_settings(
        {"username": "alice"}, "home.admin_portal", "cards"
    ) == {"view": "list", "sort": "desc"}
    assert page_view_helpers._page_view_settings(
        {"username": "alice"}, "home.data_portal", "list"
    ) == {"view": "list", "sort": "asc"}


def test_preferences_api_saves_page_view(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validate page view updates through the existing preferences API."""
    app = Flask(__name__)
    owner = type("Owner", (), {})()
    owner._require_user = lambda: {"username": "alice"}
    saved = {}
    monkeypatch.setattr(
        ariapp_impls.ud,
        "load_user_prefs",
        lambda username: {"page_views": {}},
    )
    monkeypatch.setattr(
        ariapp_impls.ud,
        "save_user_prefs",
        lambda username, updates: saved.update(updates),
    )

    with app.test_request_context(
        json={
            "page_view": {
                "page_id": "home.monitor_portal.apero_queue",
                "view": "cards",
                "sort": "desc",
            }
        }
    ):
        response = ariapp_impls.ariapp_api_user_prefs_save(owner)

    assert response.get_json()["success"] is True
    assert saved["page_views"]["home.monitor_portal.apero_queue"] == {
        "view": "cards", "sort": "desc"}


def test_page_view_javascript() -> None:
    """Exercise client-side switching, sorting, and persistence."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the collection view test")
    script = Path(__file__).with_suffix(".cjs")
    subprocess.run([node, str(script)], check=True)


@pytest.mark.parametrize("template", [
    "monitor_portal/apero_checks.html",
    "monitor_portal/processing_logs.html",
    "monitor_portal/apero_queue.html",
])
def test_monitor_collections_wrap_one_section(template: str) -> None:
    """Keep every monitor collection inside one balanced section wrapper.

    :param template: Monitor template using the shared view controls.
    :return: None.
    """
    path = Path(__file__).resolve().parents[1] / "apero_ri/templates" / template
    source = path.read_text(encoding="utf-8")

    assert source.count("<section data-ari-view-section>") == 1
    assert source.count("</section>") == 1


def test_monitor_portal_supplies_view_preferences(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Add controls and sorting to the custom-rendered monitor index.

    :param monkeypatch: Fixture replacing request and application services.
    :return: None.
    """
    captured = {}
    app = type("App", (), {
        "ari_groups": {},
        "_build_sidebar_context": lambda self, *args: {},
    })()
    monkeypatch.setattr(
        monitor_view_helpers, "get_effective_user",
        lambda session: {"username": "alice", "groups": ["monitor"]},
    )
    monkeypatch.setattr(
        monitor_view_helpers, "resolve_user_permissions",
        lambda groups, config: {"view.monitor_portal"},
    )
    monkeypatch.setattr(
        monitor_view_helpers.perms_mod, "load_pages", lambda: {}
    )
    monkeypatch.setattr(
        monitor_view_helpers.perms_mod, "get_visible_cards",
        lambda *args, **kwargs: [
            {"id": "z", "label": "Zulu", "icon": "", "url": "/z"},
            {"id": "a", "label": "alpha", "icon": "", "url": "/a"},
        ],
    )
    monkeypatch.setattr(
        monitor_view_helpers.ud, "get_page_view_prefs",
        lambda username, page_id: {"view": "list", "sort": "desc"},
    )
    monkeypatch.setattr(
        monitor_view_helpers, "render_template",
        lambda template, **context: captured.update(context) or "rendered",
    )

    assert monitor_view_helpers.monitor_portal_index_view(app) == "rendered"
    assert captured["page_view"] == {"view": "list", "sort": "desc"}
    assert [card["label"] for card in captured["cards"]] == [
        "Zulu", "Become a Monitor", "alpha"]
