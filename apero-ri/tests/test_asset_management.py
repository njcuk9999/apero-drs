"""Tests for the Asset Management admin page backend and upload API."""

import hashlib
import io

import pytest

from apero_ri.core import api_tokens as at
from apero_ri.core import asset_management as am
from apero_ri.core import user_data as ud


@pytest.fixture()
def ari_dir(tmp_path, monkeypatch):
    """Isolate the asset config and API token files in a temp dir."""
    monkeypatch.setattr(ud, "ARI_DIR", tmp_path)
    token_file = tmp_path / "secret" / "api_tokens.json"
    monkeypatch.setattr(at, "_tokens_path", lambda: token_file)
    return tmp_path


def test_validate_filename_rejects_unsafe_names():
    assert am.validate_filename("123_assets.tar.gz") == "123_assets.tar.gz"
    for bad in ("../x.tar.gz", "a/b.tar.gz", "x.py", ""):
        with pytest.raises(ValueError):
            am.validate_filename(bad)


def test_save_list_delete_roundtrip(tmp_path):
    payload = b"tar-bytes"
    md5 = hashlib.md5(payload).hexdigest()
    stored = am.save_stream(tmp_path, "1_assets.tar.gz",
                            io.BytesIO(payload), expected_md5=md5)
    assert stored["size_bytes"] == len(payload)
    with pytest.raises(ValueError):
        am.save_stream(tmp_path, "1_assets.tar.gz", io.BytesIO(payload))
    with pytest.raises(ValueError):
        am.save_stream(tmp_path, "2_assets.tar.gz", io.BytesIO(payload),
                       expected_md5="0" * 32)
    names = [row["name"] for row in am.list_files(tmp_path)]
    assert names == ["1_assets.tar.gz"]
    assert am.delete_file(tmp_path, "1_assets.tar.gz")
    assert am.list_files(tmp_path) == []


def test_upload_api_requires_setup_then_accepts(client, admin_user,
                                                ari_dir):
    token = at.generate_token(admin_user[0])
    headers = {"Authorization": f"Bearer {token}"}
    url = "/api/admin/assets/upload?filename=1_assets.tar.gz"
    # not configured -> setup signal pointing at the admin page
    resp = client.post(url, data=b"abc", headers=headers)
    assert resp.status_code == 409
    body = resp.get_json()
    assert body["setup_required"] is True
    assert body["setup_url"].endswith("/admin_portal/asset_management")
    # admin sets the hosting path
    resp = client.post("/api/admin/assets/config", headers=headers,
                       json={"assets_path": str(ari_dir / "hosted")})
    assert resp.get_json()["success"] is True
    # upload succeeds and is listed
    resp = client.post(url, data=b"abc", headers=headers)
    assert resp.get_json()["success"] is True
    status = client.get("/api/admin/assets/status", headers=headers)
    files = status.get_json()["files"]
    assert [row["name"] for row in files] == ["1_assets.tar.gz"]
    # delete removes it from disk
    resp = client.post("/api/admin/assets/delete", headers=headers,
                       json={"filename": "1_assets.tar.gz"})
    assert resp.get_json()["success"] is True
    assert not (ari_dir / "hosted" / "1_assets.tar.gz").exists()


def test_upload_api_rejects_bad_token(client, ari_dir):
    resp = client.post("/api/admin/assets/upload?filename=1_assets.tar.gz",
                       data=b"abc",
                       headers={"Authorization": "Bearer nope"})
    assert resp.status_code == 401


def test_public_and_api_download(client, admin_user, ari_dir):
    hosted = ari_dir / "hosted"
    am.set_assets_path(str(hosted))
    (hosted / "1_assets.tar.gz").write_bytes(b"abc")
    # public download needs no login
    resp = client.get("/apero-assets/1_assets.tar.gz")
    assert resp.status_code == 200 and resp.data == b"abc"
    # api download needs a token
    url = "/api/assets/download/1_assets.tar.gz"
    assert client.get(url).status_code == 401
    token = at.generate_token(admin_user[0])
    resp = client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200 and resp.data == b"abc"
    # admin can turn the public route off
    am.set_assets_path(str(hosted), public_download=False)
    assert client.get("/apero-assets/1_assets.tar.gz").status_code == 404
