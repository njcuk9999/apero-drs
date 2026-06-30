"""Basket API helper functions for ARIApp."""

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apero_ri.core import basket_funcs as bk
from apero_ri.core.auth import get_accessible_profiles
from flask import jsonify, request, url_for


def api_basket_share_email(app):
    """Email a share link for a completed job to a recipient."""
    user_info, err = app._basket_access_check()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id", "") or "").strip()
    recipient = str(data.get("recipient_email", "") or "").strip()
    if not job_id or not recipient:
        return (
            jsonify(
                success=False,
                error="job_id and recipient_email are required",
            ),
            400,
        )
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
        return (
            jsonify(success=False, error="Invalid recipient email address"),
            400,
        )

    username = user_info["username"]
    from apero_ri.core.auth import load_users as _load_users

    all_users = _load_users()
    user_data = all_users.get(username, {})
    first_names = str(
        user_data.get("first_names", "")
        or user_info.get("first_names", "")
        or ""
    ).strip()
    last_name = str(user_data.get("last_name", "") or "").strip()
    sender_email = app._get_primary_contact_email(
        {
            "primary_email": user_data.get("primary_email", ""),
            "emails": user_data.get("emails", []),
        }
    )

    try:
        token = bk.create_share_token(username, job_id)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400

    meta = bk.get_job_status(username, job_id)
    if not meta:
        return jsonify(success=False, error="Job not found"), 404

    created_str = meta.get("created_at", "")
    try:
        created_at = datetime.fromisoformat(str(created_str))
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        expires_at = created_at + timedelta(hours=24)
        expires_str = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        expires_str = "within 24 hours"

    share_url = request.host_url.rstrip("/") + url_for(
        "share_landing", token=token
    )
    sender_full = f"{first_names} {last_name}".strip() or username
    sender_display = (
        f"{sender_full} (email address: {sender_email})"
        if sender_email
        else sender_full
    )
    subject = "APERO RI: Shared download link"
    body = (
        f"User {sender_display} has sent you a link to an APERO RI "
        f"download that will expire at {expires_str}.\n\n"
        f"Download link (no login required):\n{share_url}\n"
    )
    try:
        from apero_ri.core import email_backend as eb

        eb.send_email(recipient, subject, body)
        return jsonify(success=True)
    except Exception as exc:
        return jsonify(success=False, error=f"Failed to send email: {exc}"), 500


def api_basket_compile(app):
    """Start background download compilation."""
    user_info, err = app._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    fmt = str(data.get("fmt", "zip") or "zip")
    chunk_size_gb = data.get("chunk_size_gb")
    if chunk_size_gb is not None:
        try:
            chunk_size_gb = float(chunk_size_gb)
        except (TypeError, ValueError):
            chunk_size_gb = None
    email_on_done = bool(data.get("email_on_done", False))
    profile_id = data.get("profile_id") or None

    username = user_info["username"]
    accessible_run_ids = app._all_accessible_run_ids(user_info)
    profile_cfgs = app._build_profile_cfgs(user_info)

    usage = bk.get_downloads_usage(username)
    quota_bytes = bk.get_downloads_storage_limit_bytes()
    if usage.get("total_bytes", 0) >= quota_bytes:
        return (
            jsonify(
                success=False,
                error=(
                    "Download storage limit reached (5 GB). "
                    "Please remove old compilations in Recent compilations."
                ),
                quota_reached=True,
                download_usage=usage,
                download_limit_bytes=quota_bytes,
            ),
            400,
        )

    entries = bk.load_basket(username)
    if profile_id:
        entries = [e for e in entries if e.get("profile_id") == profile_id]
    if not entries:
        return jsonify(success=False, error="Basket is empty"), 400

    user_email = ""
    if email_on_done:
        user_email = app._get_primary_contact_email(user_info)

    bk.cleanup_expired_downloads(username)
    job_id = bk.create_download_job(
        username=username,
        entries=entries,
        profile_cfgs=profile_cfgs,
        accessible_run_ids=accessible_run_ids,
        fmt=fmt,
        chunk_size_gb=chunk_size_gb,
        email_on_done=email_on_done,
        user_email=user_email,
        profile_id=profile_id or "",
    )
    return jsonify(success=True, job_id=job_id)


def api_basket_add_from_ftable(app):
    """Add accessible files for one obs_dir + fkind to the basket."""
    user_info, err = app._basket_access_check()
    if err:
        return err

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    obs_dir = request.args.get("obs_dir", "").strip()
    fkind = request.args.get("fkind", "ext").strip()

    if not profile_id or not objname:
        return (
            jsonify(success=False, error="Missing profile_id or objname"),
            400,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    rows, _, _ = bk.load_ftable_rows(
        base_dir, instrument, profile_id, objname, fkind
    )
    rows = bk.filter_accessible_rows(rows, accessible_run_ids)
    if obs_dir:
        rows = [r for r in rows if str(r.get("OBS_DIR", "") or "") == obs_dir]

    entries = [
        {
            "profile_id": profile_id,
            "instrument": instrument,
            "objname": objname,
            "block_kind": r.get("BLOCK_KIND", ""),
            "obs_dir": r.get("OBS_DIR", ""),
            "filename": r.get("FILENAME", ""),
            "kw_output": r.get("KW_OUTPUT", ""),
            "kw_run_id": r.get("KW_RUN_ID", ""),
            "kw_dprtype": r.get("KW_DPRTYPE", ""),
            "kw_fiber": r.get("KW_FIBER", ""),
            "kw_pi_name": r.get("KW_PI_NAME", ""),
            "mid_obs_time": r.get("MID_OBS_TIME", ""),
            "passed_all_qc": r.get("PASSED_ALL_QC"),
            "identifier": r.get("IDENTIFIER", ""),
        }
        for r in rows
    ]

    username = user_info["username"]
    added = bk.add_to_basket(username, entries, accessible_run_ids)
    basket = bk.load_basket(username)
    return jsonify(success=True, added=added, basket_count=len(basket))
