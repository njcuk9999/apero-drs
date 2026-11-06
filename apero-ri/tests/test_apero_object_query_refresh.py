#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for safe, incremental APERO object refreshes."""

import json
from pathlib import Path

import pytest

from apero_ri.core import auth
from apero_ri.application import data_portal_view_helpers
from apero_ri.tasks import apero_async
from apero_ri.tasks import apero_object_query


def test_product_fingerprint_covers_non_raw_products(monkeypatch) -> None:
    """Adding a reduced product changes the object's fingerprint."""
    rows = [
        {
            "BLOCK_KIND": "raw",
            "KW_OUTPUT": "RAW_OBJ_SKY",
            "FILENAME": "raw.fits",
        }
    ]
    monkeypatch.setattr(
        apero_object_query, "_check_required", lambda params: {
            "FINDEX_TABLENAME": "findex",
        }
    )
    monkeypatch.setattr(
        apero_async, "get_db_params", lambda params: {}
    )
    monkeypatch.setattr(
        apero_async,
        "database_query",
        lambda params, query: list(rows),
    )

    raw_fingerprint = apero_object_query._product_change_fingerprint(
        {}, "TOI249"
    )
    rows.append(
        {
            "BLOCK_KIND": "red",
            "KW_OUTPUT": "EXT_E2DS_FF",
            "FILENAME": "extracted.fits",
        }
    )
    product_fingerprint = apero_object_query._product_change_fingerprint(
        {}, "TOI249"
    )

    assert raw_fingerprint != product_fingerprint
    query = apero_object_query._product_change_query(
        {"FINDEX_TABLENAME": "findex"}, "TOI249"
    )
    assert "fdb.KW_OUTPUT AS KW_OUTPUT" in query
    assert "fdb.BLOCK_KIND = 'raw'" not in query


def test_refresh_checkpoints_are_independent(monkeypatch) -> None:
    """A different task's DB marker cannot suppress this task's refresh."""
    monkeypatch.setattr(
        apero_async,
        "get_profile_db_table_updates",
        lambda params, keys: {"FINDEX_TABLENAME": "current"},
    )
    params = {
        "database-update-object-table": {
            "FINDEX_TABLENAME": "old",
        },
        "database-update-observation-table": {
            "FINDEX_TABLENAME": "current",
        },
    }

    object_skip = apero_async.should_skip_profile_query(
        params,
        table_keys=["FINDEX_TABLENAME"],
        update_key="database-update-object-table",
    )[0]
    observation_skip = apero_async.should_skip_profile_query(
        params,
        table_keys=["FINDEX_TABLENAME"],
        update_key="database-update-observation-table",
    )[0]

    assert not object_skip
    assert observation_skip


def test_save_refresh_checkpoint_uses_task_key(monkeypatch) -> None:
    """Saving a task marker preserves other task markers."""
    profiles = {
        "NIRPS": {
            "nirps_he_rali": {
                "database-update-object-table": {"old": "value"},
            },
        },
    }
    saved = {}
    monkeypatch.setattr(auth, "load_apero_profiles", lambda: profiles)
    monkeypatch.setattr(
        auth, "save_apero_profiles", lambda value: saved.update(value)
    )

    apero_async.save_profile_db_table_updates(
        "NIRPS",
        "nirps_he_rali",
        {"FINDEX_TABLENAME": "new"},
        update_key="database-update-observation-table",
    )

    profile = saved["NIRPS"]["nirps_he_rali"]
    assert profile["database-update-object-table"] == {"old": "value"}
    assert profile["database-update-observation-table"] == {
        "FINDEX_TABLENAME": "new",
    }
    assert profile["database-update"] == {
        "FINDEX_TABLENAME": "new",
    }


def test_profile_refresh_status_keeps_last_success_on_failure(
    tmp_path: Path,
) -> None:
    """Failed attempts remain visible without losing the last good refresh."""
    params = {
        "INSTRUMENT": "NIRPS",
        "LOCAL_DATA_DIR": str(tmp_path),
        "general": {"INSTRUMENT": "NIRPS"},
    }

    apero_object_query._save_profile_query_state(
        params, "nirps_he_rali", status="success"
    )
    apero_object_query._save_profile_query_state(
        params,
        "nirps_he_rali",
        status="failed",
        error="simulated mount failure",
    )

    state_path = apero_object_query._profile_query_state_path(
        params, "nirps_he_rali"
    )
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "failed"
    assert state["error"] == "simulated mount failure"
    assert state["last_success_at"]


def test_broken_mount_path_is_reported_instead_of_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Filesystem errors are treated as inaccessible configured paths."""
    def broken_is_dir(path: Path) -> bool:
        raise OSError("simulated disconnected mount")

    monkeypatch.setattr(Path, "is_dir", broken_is_dir)

    missing = apero_async.check_profile_paths_accessible(
        {"paths": {"PATH_RED": "/mnt/nirps/red"}}
    )

    assert missing == [("PATH_RED", "/mnt/nirps/red")]


def test_object_page_warns_when_refresh_failed(
    app, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The portal warns users when it is serving potentially stale tables."""
    data_dir = Path(app.args.data_dir)
    profile_dir = data_dir / "tasks" / "NIRPS" / "test_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / ".object_query_state.json").write_text(
        json.dumps(
            {
                "status": "failed",
                "last_success_at": "2026-11-05T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        data_portal_view_helpers,
        "get_effective_user",
        lambda current_session: {"groups": ["super_admin"]},
    )
    monkeypatch.setattr(
        data_portal_view_helpers,
        "resolve_user_permissions",
        lambda groups, ari_groups: {"view.data_portal"},
    )
    monkeypatch.setattr(
        data_portal_view_helpers,
        "get_accessible_profiles",
        lambda user, groups: [
            {
                "profile_id": "test_profile",
                "instrument": "NIRPS",
                "data": {"general": {"has_polarimetry": True}},
            },
        ],
    )
    monkeypatch.setattr(
        app,
        "_build_data_portal_sidebar_tree",
        lambda **kwargs: [],
    )

    with app.test_request_context("/data_portal/test_profile/TOI249"):
        response = data_portal_view_helpers.ri_object_page_view(
            app, "test_profile", "TOI249"
        )

    assert "Product data shown here may be stale." in response
    assert "2026-11-05T12:00:00+00:00" in response

    (profile_dir / ".object_query_state.json").unlink()
    objects_dir = profile_dir / "objects"
    objects_dir.mkdir(exist_ok=True)
    (objects_dir / ".state_TOI249.json").write_text(
        json.dumps({"raw_last_modified_fingerprint": "legacy"}),
        encoding="utf-8",
    )
    with app.test_request_context("/data_portal/test_profile/TOI249"):
        response = data_portal_view_helpers.ri_object_page_view(
            app, "test_profile", "TOI249"
        )

    assert "old product cache that cannot be verified" in response


def test_failed_refresh_preserves_published_tables_and_fingerprint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A header read failure keeps old output and leaves the cache stale."""
    params = {
        "INSTRUMENT": "NIRPS",
        "LOCAL_DATA_DIR": str(tmp_path),
        "general": {"INSTRUMENT": "NIRPS"},
    }
    objects_dir = apero_object_query._resolve_objects_dir(
        params, "nirps_he_rali"
    )
    objects_dir.mkdir(parents=True)
    old_tables = {
        "ftable_raw_TOI249.json": [{"FILENAME": "old-raw.fits"}],
        "ftable_ext_TOI249.json": [{"FILENAME": "old-ext.fits"}],
        "htable_TOI249.json": [{"IDENTIFIER": "old"}],
    }
    for name, rows in old_tables.items():
        (objects_dir / name).write_text(json.dumps({"rows": rows}))
    apero_object_query._save_object_product_fingerprint(
        objects_dir, "TOI249", "old-fingerprint"
    )

    fingerprints = iter(["new-fingerprint", "new-fingerprint"])
    monkeypatch.setattr(
        apero_object_query,
        "_product_change_fingerprint",
        lambda params, objname: next(fingerprints),
    )

    def write_staged_tables(params, objname, profile_name):
        stage_dir = apero_object_query._resolve_objects_dir(
            params, profile_name
        )
        stage_dir.mkdir(parents=True)
        (stage_dir / "ftable_raw_TOI249.json").write_text(
            json.dumps({"rows": [{"FILENAME": "new-raw.fits"}]})
        )
        return {"results": {"raw": [{"FILENAME": "new-raw.fits"}]}}

    monkeypatch.setattr(
        apero_object_query, "object_query_db", write_staged_tables
    )
    def fail_header_read(*args):
        raise OSError("simulated mounted-file read failure")

    monkeypatch.setattr(
        apero_object_query, "object_query_headers", fail_header_read
    )

    with pytest.raises(OSError, match="mounted-file read failure"):
        apero_object_query._run_single_object_job(
            params, "TOI249", "nirps_he_rali"
        )

    for name, rows in old_tables.items():
        assert json.loads((objects_dir / name).read_text())["rows"] == rows
    assert (
        apero_object_query._load_object_product_fingerprint(
            objects_dir, "TOI249"
        )
        == "old-fingerprint"
    )


def test_complete_refresh_replaces_tables_and_removes_stale_products(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A complete refresh atomically replaces tables and cache state."""
    params = {
        "INSTRUMENT": "NIRPS",
        "LOCAL_DATA_DIR": str(tmp_path),
        "general": {"INSTRUMENT": "NIRPS"},
    }
    objects_dir = apero_object_query._resolve_objects_dir(
        params, "nirps_he_rali"
    )
    objects_dir.mkdir(parents=True)
    (objects_dir / "ftable_ccf_TOI249.json").write_text(
        json.dumps({"rows": [{"FILENAME": "stale-ccf.fits"}]})
    )
    fingerprints = iter(["new-fingerprint", "new-fingerprint"])
    monkeypatch.setattr(
        apero_object_query,
        "_product_change_fingerprint",
        lambda params, objname: next(fingerprints),
    )

    def write_staged_tables(params, objname, profile_name):
        stage_dir = apero_object_query._resolve_objects_dir(
            params, profile_name
        )
        stage_dir.mkdir(parents=True)
        (stage_dir / "ftable_raw_TOI249.json").write_text(
            json.dumps({"rows": [{"FILENAME": "new-raw.fits"}]})
        )
        return {
            "results": {
                "raw": [{"FILENAME": "new-raw.fits"}],
                "ccf": [],
            },
        }

    def write_staged_headers(params, objname, profile_name, outputs):
        stage_dir = apero_object_query._resolve_objects_dir(
            params, profile_name
        )
        (stage_dir / "htable_TOI249.json").write_text(
            json.dumps({"rows": [{"IDENTIFIER": "new"}]})
        )
        return 0.1

    monkeypatch.setattr(
        apero_object_query, "object_query_db", write_staged_tables
    )
    monkeypatch.setattr(
        apero_object_query, "object_query_headers", write_staged_headers
    )

    result = apero_object_query._run_single_object_job(
        params, "TOI249", "nirps_he_rali"
    )

    assert not result["skipped"]
    assert json.loads(
        (objects_dir / "ftable_raw_TOI249.json").read_text()
    )["rows"][0]["FILENAME"] == "new-raw.fits"
    assert json.loads(
        (objects_dir / "htable_TOI249.json").read_text()
    )["rows"][0]["IDENTIFIER"] == "new"
    assert not (objects_dir / "ftable_ccf_TOI249.json").exists()
    assert apero_object_query._load_object_product_fingerprint(
        objects_dir, "TOI249"
    ) == "new-fingerprint"


def test_publish_failure_rolls_back_previous_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A filesystem error during publication restores all prior tables."""
    stage_dir = tmp_path / "stage"
    local_dir = tmp_path / "objects"
    stage_dir.mkdir()
    local_dir.mkdir()
    old_contents = {
        "ftable_raw_TOI249.json": "old raw",
        "htable_TOI249.json": "old headers",
    }
    new_contents = {
        "ftable_raw_TOI249.json": "new raw",
        "htable_TOI249.json": "new headers",
    }
    for name, content in old_contents.items():
        (local_dir / name).write_text(content, encoding="utf-8")
    for name, content in new_contents.items():
        (stage_dir / name).write_text(content, encoding="utf-8")

    real_replace = apero_object_query.os.replace
    stage_replacements = 0

    def fail_second_stage_replace(source, target):
        nonlocal stage_replacements
        if Path(source).parent == stage_dir:
            stage_replacements += 1
            if stage_replacements == 2:
                raise OSError("simulated publish failure")
        return real_replace(source, target)

    monkeypatch.setattr(
        apero_object_query.os, "replace", fail_second_stage_replace
    )

    with pytest.raises(OSError, match="simulated publish failure"):
        apero_object_query._publish_object_outputs(
            stage_dir, local_dir, "TOI249"
        )

    for name, content in old_contents.items():
        assert (local_dir / name).read_text(encoding="utf-8") == content
