#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import json


def test_uses_ari_dir_config_when_present(monkeypatch, tmp_path) -> None:
    """The client should read api_config.json from ARI_DIR when set."""
    monkeypatch.setenv("ARI_DIR", str(tmp_path))
    monkeypatch.delenv("ARI_API_SERVER", raising=False)
    monkeypatch.delenv("ARI_API_TOKEN", raising=False)

    config_path = tmp_path / "api_config.json"
    config_path.write_text(
        json.dumps({"server": "https://ari.example.test", "token": "abc123"}),
        encoding="utf-8",
    )

    import apero_ri.ari_api.client as client

    client = importlib.reload(client)

    assert client._get_server() == "https://ari.example.test"
    assert client._get_token() == "abc123"


def test_uses_local_data_dir_config_when_ari_dir_missing(
    monkeypatch, tmp_path
) -> None:
    """The client should also honour LOCAL_DATA_DIR for task runs."""
    monkeypatch.delenv("ARI_DIR", raising=False)
    monkeypatch.setenv("LOCAL_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("ARI_API_SERVER", raising=False)
    monkeypatch.delenv("ARI_API_TOKEN", raising=False)

    config_path = tmp_path / "api_config.json"
    config_path.write_text(
        json.dumps({"server": "https://task.example.test", "token": "xyz789"}),
        encoding="utf-8",
    )

    import apero_ri.ari_api.client as client

    client = importlib.reload(client)

    assert client._get_server() == "https://task.example.test"
    assert client._get_token() == "xyz789"
