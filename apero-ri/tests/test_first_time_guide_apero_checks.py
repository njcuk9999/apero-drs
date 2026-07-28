import json

from apero_ri.application import page_view_helpers


def test_apero_checks_setup_status_marks_complete_when_ready(tmp_path):
    local_data_dir = tmp_path / "ari"
    astrom_dir = local_data_dir / "apero-assets" / "astrometrics"
    astrom_dir.mkdir(parents=True)
    (astrom_dir / "example.yaml").write_text(
        "APERO_NAME: demo\n",
        encoding="utf-8",
    )
    (local_data_dir / "api_config.json").write_text(
        json.dumps({"server": "https://example.test", "token": "abc"}),
        encoding="utf-8",
    )

    status = page_view_helpers._build_apero_checks_setup_status(
        data_dir=str(local_data_dir)
    )

    assert status["complete"] is True
    assert status["status"] == "ok"


def test_apero_checks_setup_status_requires_config_and_astrom_dir(tmp_path):
    local_data_dir = tmp_path / "ari"
    astrom_dir = local_data_dir / "apero-assets" / "astrometrics"
    astrom_dir.mkdir(parents=True)

    status = page_view_helpers._build_apero_checks_setup_status(
        data_dir=str(local_data_dir)
    )

    assert status["complete"] is False
    assert status["status"] == "pending"
    assert "api_config.json" in status["message"]


def test_apero_checks_guide_step_uses_resolved_data_dir_and_api_access_link():
    class DummyApp:
        def _get_admin_health(self, **kwargs):
            return {}, None, None

        def _build_admin_db_tunnel_context(self, *args, **kwargs):
            return {"db_tunnels": [], "db_local_databases": []}

        def _resolve_local_data_dir(self):
            return "/tmp/ari-test"

    steps = page_view_helpers._build_first_time_guide_steps(
        DummyApp(), None, []
    )
    step = next(
        item for item in steps
        if item["page_id"] == "home.admin_portal.apero_checks_policy"
    )

    assert "/tmp/ari-test/apero-assets/astrometrics" in step["sub_steps"][1]["text"]
    assert "/tmp/ari-test/api_config.json" in step["sub_steps"][2]["text"]
    assert step["sub_steps"][2]["link"]["endpoint"] == "home_admin_portal_api_config"
