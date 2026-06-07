#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Flask application class.

ARIApp inherits from Flask and wires up all routes, authentication,
and permission handling from groups.yaml / pages.yaml.
"""

import argparse
import atexit
import json
import os
import re
import secrets
import smtplib
import socket
import threading
import time
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, List, Optional

import yaml
from apero_ri.application import (
    admin_backup_api_helpers,
    admin_cache_helpers,
    admin_health_helpers,
    admin_sshfs_api_helpers,
    admin_user_api_helpers,
    apero_profiles_api_helpers,
)
from apero_ri.application import ariapp_impls as _impls
from apero_ri.application import astrometrics_api_helpers
from apero_ri.application import astrometrics_history
from apero_ri.application import rejection_list_api_helpers
from apero_ri.application import (
    async_task_helpers,
    async_tasks_api_helpers,
    basket_api_helpers,
    data_portal_api_helpers,
    data_portal_view_helpers,
    db_tunnel_api_helpers,
    doc_views_helpers,
    page_view_helpers,
    profile_utils,
    query_db_api_helpers,
    query_helpers,
)
from apero_ri.application import routes as app_routes
from apero_ri.application import sci_groups_api_helpers
from apero_ri.application import (
    object_comments_api_helpers,
    object_download_helpers,
    object_groups_api_helpers,
)
from apero_ri.application import sidebar as app_sidebar
from apero_ri.application import (
    user_account_api_helpers,
    user_context_helpers,
    user_db_access_api_helpers,
    user_favourites_api_helpers,
    user_pins_api_helpers,
)
from apero_ri.core import api_tokens as at
from apero_ri.core import auth
from apero_ri.core import backup_backend as bb
from apero_ri.core import basket_funcs as bk
from apero_ri.core import docs
from apero_ri.core import download_tracker as dt
from apero_ri.core import email_backend as eb
from apero_ri.core import object_funcs
from apero_ri.core import permissions as perms
from apero_ri.core import secret_store as ss
from apero_ri.core import sshfs_backend as sb
from apero_ri.core import task_runner
from apero_ri.core import user_data as ud
from apero_ri.tasks import apero_async
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

permissions_mod = perms

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.application.application"
PACKAGE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"


# =============================================================================
# Define classes
# =============================================================================


class ARIApp(Flask):
    """APERO Reduction Interface Flask application."""

    def __init__(self, **kwargs):
        _impls.ariapp_init(self, **kwargs)

    # -----------------------------------------------------------------
    # Group definitions with TTL cache
    # Groups are re-read from disk at most every _GROUPS_TTL seconds so
    # permission changes propagate quickly without a per-request disk read.
    # -----------------------------------------------------------------
    _groups_cache: dict = {}    # {'data': ..., 'expires': float}
    _groups_lock: threading.Lock = threading.Lock()
    _GROUPS_TTL: float = 30.0   # seconds

    @property
    def ari_groups(self):
        now = time.monotonic()
        with ARIApp._groups_lock:
            cached = ARIApp._groups_cache
            if cached and cached.get("expires", 0) > now:
                return cached["data"]
            data = perms.load_groups()
            ARIApp._groups_cache = {"data": data, "expires": now + ARIApp._GROUPS_TTL}
            return data

    @ari_groups.setter
    def ari_groups(self, _value):
        # Invalidate the cache so the next read fetches fresh data.
        with ARIApp._groups_lock:
            ARIApp._groups_cache = {}

    # -----------------------------------------------------------------
    # Argument parsing
    # -----------------------------------------------------------------
    @staticmethod
    def _get_arguments() -> argparse.Namespace:
        return _impls.ariapp_get_arguments()

    @staticmethod
    def _resolve_host(host: str) -> str:
        return _impls.ariapp_resolve_host(host)

    # -----------------------------------------------------------------
    # Secret key management
    # -----------------------------------------------------------------
    @staticmethod
    def _load_or_create_secret() -> str:
        return _impls.ariapp_load_or_create_secret()

    # -----------------------------------------------------------------
    # Context processors (available in every template)
    # -----------------------------------------------------------------
    def _register_context_processors(self):
        return _impls.ariapp_register_context_processors(self)

    # -----------------------------------------------------------------
    # Route registration
    # -----------------------------------------------------------------
    def _register_routes(self):
        return _impls.ariapp_register_routes(self)

    # -----------------------------------------------------------------
    # View factories
    # -----------------------------------------------------------------
    @staticmethod
    def _is_doc_leaf(page_id: str, pages: dict) -> bool:
        """Check if a page is a documentation leaf page."""
        parts = page_id.split(".")
        
        cond = len(parts) >= 3
        
        if not cond:
            return False
        
        cond &= parts[0] == "home"
        cond &= parts[1] == "docs"
        cond &= not perms.is_parent_page(page_id, pages)
        
        return cond

    @staticmethod
    def _is_doc_page(page_id: str) -> bool:
        """Check if a page is under the docs section."""
        return page_id.startswith("home.docs")

    def _build_sidebar_context(self, page_id: str, perms, user_info=None):
        args = (page_id, perms, user_info)
        return _impls.ariapp_build_sidebar_context(self, *args)

    def _build_home_sidebar_context(self, perms, user_info=None):
        return _impls.ariapp_build_home_sidebar_context(self, perms, user_info)

    def _build_home_page_context(self, user_info, perms) -> dict:
        return _impls.ariapp_build_home_page_context(self, user_info, perms)

    def _make_page_view(self, page_id: str):
        return page_view_helpers.make_page_view(
            self, page_id=page_id, package_dir=PACKAGE_DIR
        )

    # -----------------------------------------------------------------
    # Data portal helpers
    # -----------------------------------------------------------------
    def _instrument_colors(self):
        """Map each instrument to a palette entry (stable ordering)."""
        return (
            data_portal_view_helpers.instrument_color_helpers
            .instrument_colors()
        )

    @staticmethod
    def _get_instrument_run_ids(instrument):
        return _impls.ariapp_get_instrument_run_ids(instrument)

    @staticmethod
    def _get_instrument_run_id_pi_names(instrument):
        return _impls.ariapp_get_instrument_run_id_pi_names(instrument)

    @staticmethod
    def _is_all_science_group(name: str) -> bool:
        """Return True when a science-group name is the reserved All group."""
        return str(name or "").strip().lower() == "all"

    def _sync_all_science_group(self, instrument: str, 
                                groups: Optional[dict] = None,
                                run_ids: Optional[list] = None,
                                persist: bool = True):
        args = (instrument, groups, run_ids, persist)
        return _impls.ariapp_sync_all_science_group(self, *args)

    def _get_user_accessible_run_ids(self, user_info, instrument):
        args = (user_info, instrument)
        return _impls.ariapp_get_user_accessible_run_ids(self, *args)

    def _page_template_meta(self, template_id: str, **tokens) -> dict:
        return _impls.ariapp_page_template_meta(self, template_id, **tokens)

    def _build_data_portal_sidebar_tree(
        self,
        accessible_profiles: list,
        active_page_id: str,
        user_permissions,
        user_info=None,
        current_profile_id: Optional[str] = None,
        objname: Optional[str] = None,
        include_children: bool = True,
    ) -> list:
        args = (
            accessible_profiles,
            active_page_id,
            user_permissions,
            user_info,
            current_profile_id,
            objname,
            include_children,
        )
        return _impls.ariapp_build_data_portal_sidebar_tree(self, *args)

    def _build_ri_context(self, user_info, user_permissions):
        kwargs = dict(user_info=user_info, user_permissions=user_permissions)
        return user_context_helpers.build_ri_context(self, **kwargs)

    def _build_user_data_access_context(self, user_info):
        args = (user_info,)
        return user_context_helpers.build_user_data_access_context(self, *args)

    def _build_user_support_context(self, user_info):
        return user_context_helpers.build_user_support_context(self, user_info)

    def _build_user_links_context(self, user_info):
        return user_context_helpers.build_user_links_context(
            self, user_info
        )

    def _build_user_api_access_context(self, user_info):
        return user_context_helpers.build_user_api_access_context(user_info)

    def _build_user_calendar_context(self, user_info):
        return user_context_helpers.build_user_calendar_context(
            self, user_info
        )

    def _build_admin_instrument_context(
        self, user_info, perms, manage_prefix
    ):
        return user_context_helpers.build_admin_instrument_context(
            user_info, perms, manage_prefix
        )

    def _build_admin_email_context(self, perms):
        return _impls.ariapp_build_admin_email_context(self, perms)

    @staticmethod
    def _resolve_local_data_dir() -> Path:
        return _impls.ariapp_resolve_local_data_dir()

    def _build_admin_backup_context(self, perms):
        return _impls.ariapp_build_admin_backup_context(self, perms)

    def _build_admin_sshfs_context(self, perms):
        return _impls.ariapp_build_admin_sshfs_context(self, perms)

    def _build_admin_manage_instruments_context(self, perms):
        return _impls.ariapp_build_admin_manage_instruments_context(
            self, perms
        )

    def _api_manage_instruments_groups_create(self):
        return _impls.ariapp_api_manage_instruments_groups_create(self)

    def _api_manage_instruments_groups_delete(self):
        return _impls.ariapp_api_manage_instruments_groups_delete(self)

    def _api_manage_instruments_add(self):
        return _impls.ariapp_api_manage_instruments_add(self)

    def _api_manage_instruments_remove(self):
        return _impls.ariapp_api_manage_instruments_remove(self)

    def _api_manage_instruments_rename(self):
        return _impls.ariapp_api_manage_instruments_rename(self)

    def _api_manage_instruments_yaml_get(self):
        return _impls.ariapp_api_manage_instruments_yaml_get(self)

    def _api_manage_instruments_yaml_save(self):
        return _impls.ariapp_api_manage_instruments_yaml_save(self)

    # -----------------------------------------------------------------
    # Vault API
    # -----------------------------------------------------------------
    def _require_vault_perm(self):
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        resolved = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
        if "manage.admin.vault" not in resolved:
            return None, None
        return user_info, resolved

    def _build_admin_vault_context(self, perms):
        return _impls.ariapp_build_admin_vault_context(
            self, perms
        )

    def _api_admin_vault_list(self):
        return _impls.ariapp_api_vault_list(self)

    def _api_admin_vault_get(self):
        return _impls.ariapp_api_vault_get(self)

    def _api_admin_vault_add(self):
        return _impls.ariapp_api_vault_add(self)

    def _api_admin_vault_update(self):
        return _impls.ariapp_api_vault_update(self)

    def _api_admin_vault_delete(self):
        return _impls.ariapp_api_vault_delete(self)

    def _api_admin_vault_export(self):
        return _impls.ariapp_api_vault_export(self)

    def _api_admin_vault_import(self):
        return _impls.ariapp_api_vault_import(self)

    @staticmethod
    def _normalize_db_source(value: str) -> str:
        """Normalize database source mode for profile UI/runtime."""
        raw = str(value or "").strip().lower()
        return (
            "db_ssh_tunnel"
            if raw in {"db_ssh_tunnel", "ssh", "tunnel"}
            else "local"
        )

    def _load_db_tunnel_definitions(self) -> dict:
        """Load named DB SSH tunnel definitions."""
        data = auth.load_db_tunnels()
        tunnels = data.get("tunnels", {}) if isinstance(data, dict) else {}
        return tunnels if isinstance(tunnels, dict) else {}

    def _save_db_tunnel_definitions(self, tunnels: dict) -> None:
        """Persist named DB SSH tunnel definitions."""
        existing = auth.load_db_tunnels()
        payload = {
            "tunnels": tunnels if isinstance(tunnels, dict) else {},
            "local_databases": (
                existing.get("local_databases", {})
                if isinstance(existing, dict)
                else {}
            ),
        }
        auth.save_db_tunnels(payload)

    def _load_local_db_definitions(self) -> dict:
        """Load named local database definitions."""
        data = auth.load_db_tunnels()
        local_db = (
            data.get("local_databases", {}) if isinstance(data, dict) else {}
        )
        return local_db if isinstance(local_db, dict) else {}

    def _save_local_db_definitions(self, local_databases: dict) -> None:
        """Persist named local database definitions."""
        existing = auth.load_db_tunnels()
        
        if isinstance(existing, dict):
            tunnels = existing.get("tunnels", {})
        else:
            tunnels = dict()
        
        if isinstance(local_databases, dict):
            local_db = local_databases
        else:
            local_db = dict()
        
        payload = dict()
        payload['tunnels'] = tunnels
        payload['local_databases'] = local_db

        auth.save_db_tunnels(payload)

    def _build_db_tunnel_runtime_params(self, tunnel_name: str, 
                                        tunnel_def: dict, 
                                        mode: str = "mysql+pymysql") -> dict:
        args = (tunnel_name, tunnel_def, mode)
        return _impls.ariapp_build_db_tunnel_runtime_params(self, *args)

    @staticmethod
    def _list_ssh_config_hosts() -> List[str]:
        return _impls.ariapp_list_ssh_config_hosts()

    def _list_db_tunnel_rows(self) -> List[dict]:
        return _impls.ariapp_list_db_tunnel_rows(self)

    def _resolve_tunnel_name_from_profile_cfg(self, cfg: dict) -> str:
        """Resolve selected tunnel name from profile database settings."""
        return str(
            self._profile_get_db(cfg, "DATABASE_TUNNEL_NAME", "") or ""
        ).strip()

    def _resolve_local_db_name_from_profile_cfg(self, cfg: dict) -> str:
        """Resolve selected local DB definition name from profile settings."""
        return str(
            self._profile_get_db(cfg, "DATABASE_LOCAL_NAME", "") or ""
        ).strip()

    def _build_admin_db_tunnel_context(self, user_info, perms):
        """Build context for DB setup page."""
        _ = user_info
        tunnel_rows = self._list_db_tunnel_rows()
        local_db = self._load_local_db_definitions()
        
        cond = "manage.apero_profile" in (perms or set())
        
        tcontext = dict()
        tcontext['can_manage_db_tunnel'] = cond
        tcontext['db_tunnels'] = [row.get("name", "") for row in tunnel_rows]
        tcontext['db_local_databases'] = sorted(local_db.keys())

        return tcontext

    def _build_admin_cache_context(self, perms):
        return admin_cache_helpers.build_admin_cache_context(self, perms)

    def _api_admin_cache_reset_timings(self):
        return _impls.ariapp_api_admin_cache_reset_timings(self)

    def _api_admin_cache_save(self):
        return _impls.ariapp_api_admin_cache_save(self)

    def _api_admin_cache_purge(self):
        return _impls.ariapp_api_admin_cache_purge(self)

    def _build_admin_download_mgmt_context(self, perms):
        return _impls.ariapp_build_admin_download_mgmt_context(self, perms)

    def _api_admin_dm_save_settings(self):
        return _impls.ariapp_api_admin_dm_save_settings(self)

    def _api_admin_dm_reset_user(self):
        return _impls.ariapp_api_admin_dm_reset_user(self)

    # -----------------------------------------------------------------
    # Token-based API auth helper
    # -----------------------------------------------------------------
    @staticmethod
    def _get_api_user() -> Optional[dict]:
        return _impls.ariapp_get_api_user()

    # -----------------------------------------------------------------
    # User API token endpoints
    # -----------------------------------------------------------------
    def _api_user_token_generate(self):
        """Generate a new API token for the logged-in user."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error="Not logged in"), 401
        body = request.get_json(silent=True) or {}
        label = str(body.get("label", "")).strip()[:100]
        token = at.generate_token(user_info["username"], label)
        return jsonify(success=True, token=token)

    def _api_user_token_revoke(self):
        """Revoke the API token for the logged-in user."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error="Not logged in"), 401
        removed = at.revoke_token(user_info["username"])
        return jsonify(success=True, removed=removed)

    @staticmethod
    def _format_utc_datetime(dt: Optional[datetime]) -> str:
        """Format UTC datetime for display."""
        if dt is None:
            return "Never"
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _admin_health_cache_key(perms) -> str:
        """Stable key for admin-health cache entries."""
        return "|".join(sorted(perms))

    def _load_health_cache_from_disk(self) -> None:
        return _impls.ariapp_load_health_cache_from_disk(self)

    def _save_health_cache_to_disk(self) -> None:
        return _impls.ariapp_save_health_cache_to_disk(self)

    def _start_admin_health_refresher(self) -> None:
        return _impls.ariapp_start_admin_health_refresher(self)

    def _admin_health_refresher_loop(self) -> None:
        return _impls.ariapp_admin_health_refresher_loop(self)

    def _admin_health_digest_loop(self) -> None:
        return _impls.ariapp_admin_health_digest_loop(self)

    def _refresh_admin_health_entry(
        self, cache_key: str, user_info, perms
    ) -> None:
        args = (cache_key, user_info, perms)
        return _impls.ariapp_refresh_admin_health_entry(self, *args)

    def _spawn_admin_health_refresh(
        self, cache_key: str, user_info, perms
    ) -> None:
        args = (cache_key, user_info, perms)
        return _impls.ariapp_spawn_admin_health_refresh(self, *args)

    def shutdown(self) -> None:
        return _impls.ariapp_shutdown(self)

    def _get_admin_health(self, user_info,  perms,
                          force: bool = False,
                          allow_async_refresh: bool = True):
        kwargs = dict(user_info=user_info,
                      perms=perms, force=force,
                      allow_async_refresh=allow_async_refresh)
        return admin_health_helpers.get_admin_health(self, **kwargs)

    def _refresh_admin_health_after_change(self, user_info=None, 
                                           perms=None) -> None:
        args = (user_info, perms)
        return _impls.ariapp_refresh_admin_health_after_change(self, *args)

    def _build_admin_card_health_uncached(self, user_info, perms) -> dict:
        kwargs = dict(user_info=user_info, perms=perms)
        return admin_health_helpers.build_admin_card_health_uncached(
            self, **kwargs
        )

    def _build_admin_health_rows(self, health: dict) -> list:
        return admin_health_helpers.build_admin_health_rows(self, health)

    def _api_admin_health_update(self):
        return _impls.ariapp_api_admin_health_update(self)

    def _api_admin_audit_log(self):
        return _impls.ariapp_api_admin_audit_log(self)

    def _api_admin_health_history(self):
        return _impls.ariapp_api_admin_health_history(self)

    def _api_admin_health_patch(self):
        return _impls.ariapp_api_admin_health_patch(self)

    def _api_admin_health_config_get(self):
        return _impls.ariapp_api_admin_health_config_get(self)

    def _api_admin_health_config_save(self):
        return _impls.ariapp_api_admin_health_config_save(self)

    def _build_apero_profiles_overview_status(self) -> dict:
        return apero_profiles_api_helpers.build_apero_profiles_overview_status(
            self
        )

    def _ri_profile_view(self, profile_id):
        return data_portal_view_helpers.ri_profile_view(self, profile_id)

    def _ri_favourites_objects_view(self, profile_id):
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_favourites_objects_view(
            self, **kwargs
        )

    def _ri_object_groups_view(self, profile_id):
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_object_groups_view(
            self, **kwargs
        )

    def _ri_object_group_summary_view(
        self,
        profile_id,
        group_name,
    ):
        kwargs = dict(
            profile_id=profile_id,
            group_name=group_name,
        )
        return data_portal_view_helpers.ri_object_group_summary_view(
            self,
            **kwargs,
        )

    def _ri_favourites_summary_view(
        self,
        profile_id,
        section_name,
    ):
        kwargs = dict(
            profile_id=profile_id,
            section_name=section_name,
        )
        return data_portal_view_helpers.ri_favourites_summary_view(
            self,
            **kwargs,
        )

    def _api_object_comments_list(self):
        return object_comments_api_helpers.api_object_comments_list(
            self
        )

    def _api_object_comments_add(self):
        return object_comments_api_helpers.api_object_comments_add(
            self
        )

    def _api_object_comments_edit(self):
        return object_comments_api_helpers.api_object_comments_edit(
            self
        )

    def _api_object_comments_delete(self):
        return object_comments_api_helpers.api_object_comments_delete(
            self
        )

    def _api_object_groups_list(self):
        return object_groups_api_helpers.api_object_groups_list(
            self
        )

    def _api_object_groups_for_object(self):
        return object_groups_api_helpers.api_object_groups_for_object(
            self
        )

    def _api_object_groups_objects(self):
        return object_groups_api_helpers.api_object_groups_objects(
            self
        )

    def _api_object_groups_create(self):
        return object_groups_api_helpers.api_object_groups_create(
            self
        )

    def _api_object_groups_delete(self):
        return object_groups_api_helpers.api_object_groups_delete(
            self
        )

    def _api_object_groups_rename(self):
        return object_groups_api_helpers.api_object_groups_rename(
            self
        )

    def _api_object_groups_add_object(self):
        return object_groups_api_helpers.api_object_groups_add_object(
            self
        )

    def _api_object_groups_add_objects_bulk(self):
        return (
            object_groups_api_helpers
            .api_object_groups_add_objects_bulk(self)
        )

    def _api_object_groups_add_objects_json(self):
        return (
            object_groups_api_helpers
            .api_object_groups_add_objects_json(self)
        )

    def _api_object_groups_remove_object(self):
        return (
            object_groups_api_helpers
            .api_object_groups_remove_object(self)
        )

    def _api_object_groups_summary_config(self):
        return (
            object_groups_api_helpers
            .api_object_groups_summary_config(self)
        )

    def _api_object_groups_summary_table(self):
        return (
            object_groups_api_helpers
            .api_object_groups_summary_table(self)
        )

    def _api_object_groups_summary_export(self):
        return (
            object_groups_api_helpers
            .api_object_groups_summary_export(self)
        )

    def _api_object_groups_summary_custom_test(self):
        return (
            object_groups_api_helpers
            .api_object_groups_summary_custom_test(self)
        )

    def _api_object_groups_allowed_expressions(self):
        return (
            object_groups_api_helpers
            .api_object_groups_allowed_expressions(self)
        )

    def _api_object_groups_admin_custom_columns(self):
        return (
            object_groups_api_helpers
            .api_object_groups_admin_custom_columns(self)
        )

    def _api_object_groups_admin_custom_test(self):
        return (
            object_groups_api_helpers
            .api_object_groups_admin_custom_test(self)
        )

    def _api_clocks_get(self):
        return _impls.ariapp_api_clocks_get(self)

    def _api_admin_clocks(self):
        return _impls.ariapp_api_admin_clocks(self)

    def _api_ri_profile_health(self):
        return data_portal_api_helpers.api_ri_profile_health(self)

    # -----------------------------------------------------------------
    # Login / Logout views
    # -----------------------------------------------------------------
    def _login_view(self):
        return _impls.ariapp_login_view(self)

    def _logout_view(self):
        """Clear session and redirect to home."""
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    @staticmethod
    def _get_primary_contact_email(user: dict) -> str:
        return _impls.ariapp_get_primary_contact_email(user)

    @staticmethod
    def _parse_iso_datetime(value: str) -> Optional[datetime]:
        """Parse an ISO datetime string safely."""
        try:
            dt = datetime.fromisoformat(str(value))
        except Exception:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _cleanup_expired_reset_tokens(self, users: dict) -> bool:
        return _impls.ariapp_cleanup_expired_reset_tokens(self, users)

    def _find_reset_user(self, token: str, users: dict) -> Optional[str]:
        return _impls.ariapp_find_reset_user(self, token, users)

    @staticmethod
    def _get_request_ip() -> str:
        """Get client IP, preferring X-Forwarded-For when present."""
        xff = str(request.headers.get("X-Forwarded-For", "")).strip()
        if xff:
            return xff.split(",")[0].strip() or "unknown"
        return str(request.remote_addr or "unknown").strip() or "unknown"

    def _prune_forgot_pw_rate_limit(self, now_ts: float) -> None:
        return _impls.ariapp_prune_forgot_pw_rate_limit(self, now_ts)

    def _register_forgot_pw_attempt(self, ip: str) -> Optional[int]:
        return user_account_api_helpers.register_forgot_pw_attempt(self, ip)

    def _forgot_password_view(self):
        return user_account_api_helpers.forgot_password_view(self)

    def _reset_password_view(self, token: str):
        return _impls.ariapp_reset_password_view(self, token)

    def _register_view(self):
        """Render self-registration page."""
        return render_template("home/register.html",
                               page_label="Register",
                               page_icon="fa-solid fa-user-plus")

    @staticmethod
    def _send_verification_email(recipient_email: str, code: str, 
                                 purpose: str) -> Optional[str]:
        return _impls.ariapp_send_verification_email(recipient_email,
                                                     code, purpose)

    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Validate lowercase username format."""
        return bool(re.match(r"^[a-z][a-z0-9_]{2,63}$", username))

    # -----------------------------------------------------------------
    # Registration & account APIs
    # -----------------------------------------------------------------
    def _api_auth_register_start(self):
        return user_account_api_helpers.api_auth_register_start(self)

    def _api_auth_register_verify(self):
        return user_account_api_helpers.api_auth_register_verify(self)

    def _require_user(self):
        """Require a logged in effective user."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None
        return user_info

    def _api_user_account_get(self):
        return _impls.ariapp_api_user_account_get(self)

    def _api_user_account_update(self):
        return user_account_api_helpers.api_user_account_update(self)

    def _api_user_account_request_primary_email(self):
        return user_account_api_helpers.api_user_account_request_primary_email(
            self
        )

    def _api_user_account_confirm_primary_email(self):
        return user_account_api_helpers.api_user_account_confirm_primary_email(
            self
        )

    def _api_user_data_access_request(self):
        return user_context_helpers.api_user_data_access_request(self)

    @staticmethod
    def _normalize_pinned_pages(value) -> List[dict]:
        return _impls.ariapp_normalize_pinned_pages(value)

    @staticmethod
    def _normalize_object_section_pins(value) -> List[str]:
        return _impls.ariapp_normalize_object_section_pins(value)

    def _api_user_pins_list(self):
        """List pinned pages for the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401

        username = user_info["username"]
        pins = self._load_user_pins(username)
        return jsonify(success=True, pins=pins)

    def _load_user_pins(self, username: str) -> List[dict]:
        return _impls.ariapp_load_user_pins(self, username)

    def _save_user_pins(self, username: str, pins: List[dict]) -> None:
        return _impls.ariapp_save_user_pins(self, username, pins)

    def _load_user_object_section_pins(self, username: str) -> List[str]:
        return _impls.ariapp_load_user_object_section_pins(self, username)

    def _save_user_object_section_pins(
        self, username: str, pins: List[str]
    ) -> None:
        return _impls.ariapp_save_user_object_section_pins(self, username, pins)

    def _api_user_pins_toggle(self):
        return user_pins_api_helpers.api_user_pins_toggle(self)

    def _api_user_pins_remove(self):
        return user_pins_api_helpers.api_user_pins_remove(self)

    def _api_user_pins_reorder(self):
        return user_pins_api_helpers.api_user_pins_reorder(self)

    def _api_user_object_sections_get(self):
        """Get global object page section pin order for current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        username = user_info["username"]
        pinned = self._load_user_object_section_pins(username)
        return jsonify(success=True, object_section={"pinned": pinned})

    def _api_user_object_sections_toggle(self):
        return _impls.ariapp_api_user_object_sections_toggle(self)

    def _api_user_object_sections_reorder(self):
        return _impls.ariapp_api_user_object_sections_reorder(self)

    def _api_user_favourite_objects_get(self):
        return _impls.ariapp_api_user_favourite_objects_get(self)

    def _api_user_favourite_objects_toggle(self):
        return _impls.ariapp_api_user_favourite_objects_toggle(self)

    def _api_user_favourite_objects_remove(self):
        return _impls.ariapp_api_user_favourite_objects_remove(self)

    def _api_user_favourite_objects_reorder(self):
        return user_favourites_api_helpers.api_user_favourite_objects_reorder(
            self
        )

    def _api_user_favourite_objects_last_opened(self):
        return _impls.ariapp_api_user_favourite_objects_last_opened(self)

    def _api_user_favourite_objects_sections_save(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_save(self)
        )

    def _api_user_favourite_objects_sections_rename(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_rename(self)
        )

    def _api_user_favourite_objects_sections_delete(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_delete(self)
        )

    def _api_user_favourite_objects_meta_save(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_meta_save(self)
        )

    def _api_user_favourite_objects_add(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_add(self)
        )

    def _api_user_favourite_objects_add_bulk(self):
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_add_bulk(self)
        )

    # -----------------------------------------------------------------
    # Documentation views
    # -----------------------------------------------------------------
    def _doc_edit_view(self, page_ref: str):
        return doc_views_helpers.doc_edit_view(self, page_ref)

    def _doc_dynamic_view(self, page_ref: str):
        return doc_views_helpers.doc_dynamic_view(self, page_ref)

    def _doc_save_view(self, page_ref: str):
        return _impls.ariapp_doc_save_view(self, page_ref)

    def _doc_upload_image(self):
        return _impls.ariapp_doc_upload_image(self)

    @staticmethod
    def _doc_image_view(filename: str):
        """Serve uploaded documentation images."""
        return send_from_directory(str(DOC_IMAGES), filename)

    # -----------------------------------------------------------------
    # Object table sub-page + API
    # -----------------------------------------------------------------
    def _ri_object_table_view(self, profile_id):
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_object_table_view(self, **kwargs)

    def _ri_find_object_view(self, profile_id):
        """Legacy Find Object URL now redirects to object table."""
        return redirect(url_for("ri_object_table", profile_id=profile_id))

    def _api_profiles_list(self):
        return _impls.ariapp_api_profiles_list(self)

    def _api_object_table(self):
        return data_portal_api_helpers.api_object_table(self)

    def _api_astrometrics_find_object(self):
        return astrometrics_api_helpers.api_astrometrics_find_object(self)

    def _api_astrometrics_resolve_by_name(self):
        return astrometrics_api_helpers.api_astrometrics_resolve_by_name(
            self
        )

    def _api_astrometrics_resolve_by_coords(self):
        return astrometrics_api_helpers.api_astrometrics_resolve_by_coords(
            self
        )

    def _api_astrometrics_resolve_by_filter(self):
        return astrometrics_api_helpers.api_astrometrics_resolve_by_filter(
            self
        )

    def _api_astrometrics_columns(self):
        return astrometrics_api_helpers.api_astrometrics_columns(self)

    def _api_astrometrics_list_all(self):
        return astrometrics_api_helpers.api_astrometrics_list_all(self)

    def _api_astrometrics_list_rejected(self):
        return (astrometrics_api_helpers
                .api_astrometrics_list_rejected(self))

    def _api_astrometrics_add_rejected(self):
        return (astrometrics_api_helpers
                .api_astrometrics_add_rejected(self))

    def _api_astrometrics_update_rejected(self):
        return (astrometrics_api_helpers
                .api_astrometrics_update_rejected(self))

    def _api_astrometrics_delete_rejected(self):
        return (astrometrics_api_helpers
                .api_astrometrics_delete_rejected(self))

    def _api_astrometrics_add_manual(self):
        try:
            return (astrometrics_api_helpers
                    .api_astrometrics_add_manual(self))
        except Exception as exc:  # noqa: BLE001
            import traceback as _tb
            from flask import jsonify as _jsonify
            tb = _tb.format_exc()
            try:
                from pathlib import Path as _P
                base = _P(self.args.data_dir
                          or str(_P.home() / ".ari"))
                logf = base / "apero_ri_errors.log"
                with logf.open("a", encoding="utf-8") as fp:
                    fp.write("\n=== add-manual error ===\n")
                    fp.write(tb)
            except Exception:  # noqa: BLE001
                pass
            try:
                self.log.error(
                    "add-manual unhandled: %s\n%s", exc, tb)
            except Exception:  # noqa: BLE001
                pass
            return _jsonify(
                success=False,
                error="Server exception: {0}: {1}".format(
                    type(exc).__name__, exc),
            ), 500

    def _api_astrometrics_recompute_manual(self):
        return (astrometrics_api_helpers
                .api_astrometrics_recompute_manual(self))

    def _api_astrometrics_lock_acquire(self):
        return (astrometrics_api_helpers
                .api_astrometrics_lock_acquire(self))

    def _api_astrometrics_lock_heartbeat(self):
        return (astrometrics_api_helpers
                .api_astrometrics_lock_heartbeat(self))

    def _api_astrometrics_lock_release(self):
        return (astrometrics_api_helpers
                .api_astrometrics_lock_release(self))

    def _api_astrometrics_update_field(self):
        return astrometrics_api_helpers.api_astrometrics_update_field(
            self
        )

    def _api_astrometrics_upload_yaml(self):
        return astrometrics_api_helpers.api_astrometrics_upload_yaml(
            self
        )

    def _api_astrometrics_status(self):
        return astrometrics_api_helpers.api_astrometrics_status(self)

    def _api_astrometrics_verify(self):
        return astrometrics_api_helpers.api_astrometrics_verify(self)

    def _api_astrometrics_sed(self):
        return astrometrics_api_helpers.api_astrometrics_sed(self)

    def _api_astrometrics_hr(self):
        return astrometrics_api_helpers.api_astrometrics_hr(self)

    def _api_astrometrics_resolve_online_by_name(self):
        return (
            astrometrics_api_helpers
            .api_astrometrics_resolve_online_by_name(self))

    def _api_astrometrics_resolve_online_by_coords(self):
        return (
            astrometrics_api_helpers
            .api_astrometrics_resolve_online_by_coords(self))

    # ----- astrometrics edit history -----
    def _api_astrometrics_history_list(self):
        return astrometrics_history.api_astrometrics_history_list(
            self)

    def _api_astrometrics_history_get(self):
        return astrometrics_history.api_astrometrics_history_get(
            self)

    def _api_astrometrics_history_delete(self):
        return astrometrics_history.api_astrometrics_history_delete(
            self)

    def _api_astrometrics_history_clear(self):
        return astrometrics_history.api_astrometrics_history_clear(
            self)

    def _api_rejection_list_list(self):
        return rejection_list_api_helpers.api_rejection_list_list(
            self
        )

    def _api_rejection_list_add(self):
        return rejection_list_api_helpers.api_rejection_list_add(
            self
        )

    def _api_rejection_list_update(self):
        return rejection_list_api_helpers.api_rejection_list_update(
            self
        )

    def _api_rejection_list_delete(self):
        return rejection_list_api_helpers.api_rejection_list_delete(
            self
        )

    def _api_rejection_list_upload(self):
        return rejection_list_api_helpers.api_rejection_list_upload(
            self
        )

    def _api_rejection_history_list(self):
        return rejection_list_api_helpers.api_rejection_history_list(
            self
        )

    def _api_rejection_history_get(self):
        return rejection_list_api_helpers.api_rejection_history_get(
            self
        )

    def _api_rejection_history_restore(self):
        return rejection_list_api_helpers.api_rejection_history_restore(
            self
        )

    def _api_rejection_history_resolve(self):
        return rejection_list_api_helpers.api_rejection_history_resolve(
            self
        )

    def _api_rejection_history_delete(self):
        return rejection_list_api_helpers.api_rejection_history_delete(
            self
        )

    def _api_rejection_history_clear(self):
        return rejection_list_api_helpers.api_rejection_history_clear(
            self
        )

    # -----------------------------------------------------------------
    # Issues subsystem
    # -----------------------------------------------------------------

    def _api_issues_list(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_list(self)

    def _api_issues_create(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_create(self)

    def _api_issues_update(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_update(self)

    def _api_issues_users(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_users(self)

    def _api_issues_delete(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_delete(self)

    def _api_issues_edit(self):
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_edit(self)

    def _api_known_errors_list(self):
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_list(self)

    def _api_known_errors_create(self):
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_create(self)

    def _api_known_errors_update(self):
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_update(self)

    def _api_known_errors_delete(self):
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_delete(self)

    # -----------------------------------------------------------------
    # Monitor schedule subsystem
    # -----------------------------------------------------------------

    def _api_schedule_meta(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_meta(self)

    def _api_schedule_entries_list(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_list(self)

    def _api_schedule_entries_add(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_add(self)

    def _api_schedule_entries_edit(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_edit(self)

    def _api_schedule_entries_delete(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_delete(self)

    def _api_schedule_link_user_calendar(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_link_user_calendar(self)

    def _api_schedule_tasks_upsert(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_upsert(self)

    def _api_schedule_tasks_rename(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_rename(self)

    def _api_schedule_tasks_set_active(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_set_active(self)

    def _api_schedule_calendar_week(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_week(self)

    def _api_schedule_calendar_month(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_month(self)

    def _api_schedule_calendar_weeks(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_weeks(self)

    def _api_schedule_stats(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_stats(self)

    def _api_schedule_stats_visibility_set(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_stats_visibility_set(self)

    def _api_schedule_instrument_setting_set(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_instrument_setting_set(self)

    def _api_schedule_entries_bulk_add(self):
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_bulk_add(self)

    # -----------------------------------------------------------------
    # Notifications + messaging subsystem
    # -----------------------------------------------------------------
    def _api_notifications_list(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_list(self)

    def _api_notifications_unread_count(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_unread_count(self)

    def _api_notifications_mark_read(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_mark_read(self)

    def _api_notifications_dismiss(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_dismiss(self)

    def _api_notification_prefs_get(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notification_prefs_get(self)

    def _api_notification_prefs_save(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notification_prefs_save(self)

    def _api_messages_list(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_list(self)

    def _api_messages_send(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_send(self)

    def _api_messages_get(self, mid):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_get(self, mid)

    def _api_messages_delete(self, mid):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_delete(self, mid)

    def _api_messages_mark_unread(self, mid):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_mark_unread(self, mid)

    def _api_messages_mark_all_read(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_mark_all_read(self)

    def _api_messages_delete_all(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_delete_all(self)

    def _api_messages_flag_as_issue(self, mid):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_flag_as_issue(self, mid)

    def _api_users_directory(self):
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_users_directory(self)

    def _user_portal_users_view(self):
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_users_view(self)

    def _user_portal_user_card_view(self, username):
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_user_card_view(self, username)

    def _user_portal_messages_view(self):
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_messages_view(self)

    def _user_portal_notifications_view(self):
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_notifications_view(self)

    def _monitor_portal_index_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_portal_index_view(self)

    def _monitor_issues_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_issues_view(self)

    def _monitor_known_errors_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_known_errors_view(self)

    def _monitor_status_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_view(self)

    def _monitor_status_alliance_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_alliance_view(self)

    def _monitor_status_canfar_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_canfar_view(self)

    def _monitor_schedule_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_schedule_view(self)

    def _monitor_processing_logs_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_view(self)

    def _monitor_processing_logs_profile_view(
        self, profile_id
    ):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_profile_view(
            self, profile_id
        )

    def _monitor_processing_logs_pid_view(
        self, profile_id, pid
    ):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_pid_view(
            self, profile_id, pid
        )

    def _monitor_apero_checks_view(self):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_view(self)

    def _monitor_apero_checks_profile_view(self, profile_id):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_profile_view(self, profile_id)

    def _monitor_apero_checks_obsdir_view(self, profile_id, obsdir):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_obsdir_view(
            self, profile_id, obsdir
        )

    def _monitor_apero_checks_check_view(
        self,
        profile_id,
        obsdir,
        check_key,
    ):
        from apero_ri.application import monitor_view_helpers as mvh
        args = [self, profile_id, obsdir, check_key]
        return mvh.monitor_apero_checks_check_view(*args)

    def _monitor_apero_checks_queue_view(self, profile_id):
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_queue_view(self, profile_id)

    def _monitor_apero_checks_stats_view(self, profile_id):
        from apero_ri.application import (
            apero_checks_stats_helpers as acsh,
        )
        return acsh.monitor_apero_checks_stats_view(
            self, profile_id
        )

    def _api_apero_checks_stats(self, profile_id):
        from apero_ri.application import (
            apero_checks_stats_helpers as acsh,
        )
        return acsh.api_apero_checks_stats(self, profile_id)

    def _api_processing_logs(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs(self)

    def _api_processing_logs_pid(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_pid(self)

    def _api_processing_log_file(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_log_file(self)

    def _api_processing_logs_fail_report(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_fail_report(self)

    def _api_processing_logs_fail_report_info(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_fail_report_info(self)

    def _api_processing_logs_report_download(self, token):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_report_download(self, token)

    def _api_processing_logs_filters_list(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_list(self)

    def _api_processing_logs_filters_save(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_save(self)

    def _api_processing_logs_filters_delete(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_delete(self)

    def _api_processing_logs_pid_export(self):
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_pid_export(self)

    def _api_apero_checks_update_failure(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_update_failure(self)

    def _api_apero_checks_create_issue(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_create_issue(self)

    def _api_apero_checks_config_save(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_config_save(self)

    def _api_apero_checks_browse_dirs(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_browse_dirs(self)

    def _api_apero_checks_profile_page(self, profile_id):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_profile_page(self, profile_id)

    def _api_apero_checks_policy_sections(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_policy_sections(self)

    def _api_apero_checks_view_yaml(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_view_yaml(self)

    def _api_apero_checks_rerun_night(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_rerun_night(self)

    def _api_apero_checks_rerun_single_check(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_rerun_single_check(self)

    def _api_apero_checks_clean_reset_profile(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_clean_reset_profile(self)

    def _api_apero_checks_delete_obsdir(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_delete_obsdir(self)

    def _api_apero_checks_delete_test_from_yamls(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_delete_test_from_yamls(self)

    def _api_apero_checks_queue_status(self, profile_id):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_status(self, profile_id)

    def _api_apero_checks_queue_cancel_task(self, profile_id):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_cancel_task(self, profile_id)

    def _api_apero_checks_queue_kill_profile(self, profile_id):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_kill_profile(self, profile_id)

    def _api_apero_checks_queue_clear_history(self, profile_id):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_clear_history(self, profile_id)

    def _api_apero_checks_check_results(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_check_results(self)

    def _api_apero_checks_check_info_async(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_check_info_async(self)

    def _api_apero_checks_policy_build_status(self):
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_policy_build_status(self)


        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_obs_table_view(self, **kwargs)

    def _ri_object_page_view(self, profile_id, objname):
        kwargs = dict(profile_id=profile_id, objname=objname)
        return data_portal_view_helpers.ri_object_page_view(self, **kwargs)

    def _api_object_page(self):
        return data_portal_api_helpers.api_object_page(self)

    def _api_object_rejection_issue(self):
        return data_portal_api_helpers.api_object_rejection_issue(self)

    @staticmethod
    def _rid_cache_tag(accessible_run_ids):
        """Return a short hash of the accessible run_id set for cache keys."""
        import hashlib

        blob = "|".join(sorted(accessible_run_ids)).encode()
        return hashlib.md5(blob).hexdigest()[:8]

    @staticmethod
    def _filter_plot_rows(htable_rows, ftable_dict, accessible_run_ids):
        
        args = [htable_rows, ftable_dict, accessible_run_ids]
        return _impls.ariapp_filter_plot_rows(*args)

    def _api_object_plots(self):
        return data_portal_api_helpers.api_object_plots(self)

    def _api_object_download(self):
        return object_download_helpers.api_object_download(self)

    def _api_object_lbl_plots(self):
        return data_portal_api_helpers.api_object_lbl_plots(self)

    def _api_filename_plot(self):
        return data_portal_api_helpers.api_filename_plot(self)

    def _ri_object_plot_max_view(self, profile_id, objname, plot_key):
        kwargs = dict(profile_id=profile_id, objname=objname,
                      plot_key=plot_key)
        return data_portal_view_helpers.ri_object_plot_max_view(self, **kwargs)

    # -----------------------------------------------------------------
    # Finder chart helpers
    # -----------------------------------------------------------------

    def _api_finder_chart(self):
        return data_portal_api_helpers.api_finder_chart(self)

    def _api_finder_chart_stream(self):
        return (
            data_portal_api_helpers
            .api_finder_chart_stream(self)
        )

    def _api_tess_rotation(self):
        return data_portal_api_helpers.api_tess_rotation(
            self
        )

    def _api_tess_rotation_lc(self):
        return data_portal_api_helpers.api_tess_rotation_lc(
            self
        )

    def _api_tess_rotation_stream(self):
        return (
            data_portal_api_helpers
            .api_tess_rotation_stream(self)
        )

    def _api_tess_rotation_data(self):
        return (
            data_portal_api_helpers
            .api_tess_rotation_data(self)
        )

    def _api_debug_plots(self):
        return data_portal_api_helpers.api_debug_plots(self)

    def _api_tcorr_map_generate(self):
        return data_portal_api_helpers.api_tcorr_map_generate(self)

    def _build_finder_max_payload(self, profile, objname, obj_props, 
                                  preset, band_idx):
        
        args = [profile, objname, obj_props, preset, band_idx]
        return _impls.ariapp_build_finder_max_payload(self, *args)

    # -----------------------------------------------------------------
    # Download basket helpers
    # -----------------------------------------------------------------

    def _basket_access_check(self):
        return _impls.ariapp_basket_access_check(self)

    def _build_profile_cfgs(self, user_info) -> dict:
        """
        Return {profile_id: profile_data} for all user-accessible profiles.
        Used to resolve file paths during basket compilation.
        """
        accessible = auth.get_accessible_profiles(user_info, self.ari_groups)
        return {p["profile_id"]: p.get("data", {}) for p in accessible}

    def _all_accessible_run_ids(self, user_info) -> set:
        return _impls.ariapp_all_accessible_run_ids(self, user_info)

    # -----------------------------------------------------------------
    # Basket: page view
    # -----------------------------------------------------------------

    def _ri_basket_view(self, profile_id):
        return data_portal_view_helpers.ri_basket_view(self, profile_id)

    # -----------------------------------------------------------------
    # Basket: API – get basket contents
    # -----------------------------------------------------------------

    def _api_basket_get(self):
        return _impls.ariapp_api_basket_get(self)

    # -----------------------------------------------------------------
    # Basket: API – summary (file counts + sizes)
    # -----------------------------------------------------------------

    def _api_basket_summary(self):
        return _impls.ariapp_api_basket_summary(self)

    # -----------------------------------------------------------------
    # Basket: API – add entries
    # -----------------------------------------------------------------

    def _api_basket_add(self):
        return _impls.ariapp_api_basket_add(self)

    # -----------------------------------------------------------------
    # Basket: API – remove entries
    # -----------------------------------------------------------------

    def _api_basket_remove(self):
        return _impls.ariapp_api_basket_remove(self)

    # -----------------------------------------------------------------
    # Basket: API – clear
    # -----------------------------------------------------------------

    def _api_basket_clear(self):
        return _impls.ariapp_api_basket_clear(self)

    # -----------------------------------------------------------------
    # Basket: API – compile download
    # -----------------------------------------------------------------

    def _api_basket_compile(self):
        return basket_api_helpers.api_basket_compile(self)

    # -----------------------------------------------------------------
    # Basket: API – compilation status
    # -----------------------------------------------------------------

    def _api_basket_compile_status(self, job_id):
        return _impls.ariapp_api_basket_compile_status(self, job_id)

    # -----------------------------------------------------------------
    # Basket: API – download compiled file
    # -----------------------------------------------------------------

    def _api_basket_download(self, job_id, chunk_idx):
        return _impls.ariapp_api_basket_download(self, job_id, chunk_idx)

    # -----------------------------------------------------------------
    # Basket: API – recent jobs
    # -----------------------------------------------------------------

    def _api_basket_jobs(self):
        return _impls.ariapp_api_basket_jobs(self)

    def _api_basket_jobs_remove(self):
        return _impls.ariapp_api_basket_jobs_remove(self)

    def _api_basket_jobs_clear(self):
        return _impls.ariapp_api_basket_jobs_clear(self)

    # -----------------------------------------------------------------
    # Basket: API – create/retrieve share token for a completed job
    # -----------------------------------------------------------------

    def _api_basket_share_token(self):
        return _impls.ariapp_api_basket_share_token(self)

    # -----------------------------------------------------------------
    # Basket: API – send share email
    # -----------------------------------------------------------------

    def _api_basket_share_email(self):
        return basket_api_helpers.api_basket_share_email(self)

    # -----------------------------------------------------------------
    # Basket: Public share landing page (no login required)
    # -----------------------------------------------------------------

    def _share_landing(self, token):
        return _impls.ariapp_share_landing(self, token)

    # -----------------------------------------------------------------
    # Basket: Public share chunk download (no login required)
    # -----------------------------------------------------------------

    def _share_download(self, token, chunk_idx):
        return _impls.ariapp_share_download(self, token, chunk_idx)

    # -----------------------------------------------------------------
    # Basket: API – add from ftable by obs_dir + fkind
    # -----------------------------------------------------------------

    def _api_basket_add_from_ftable(self):
        return basket_api_helpers.api_basket_add_from_ftable(self)

    # -----------------------------------------------------------------
    # File browser API
    # -----------------------------------------------------------------

    def _api_file_browser(self):
        return query_db_api_helpers.api_file_browser(self)

    def _api_file_header(self):
        return query_db_api_helpers.api_file_header(self)

    def _api_file_header_download(self):
        return query_db_api_helpers.api_file_header_download(self)

    def _api_obs_table(self):
        return data_portal_api_helpers.api_obs_table(self)

    # -----------------------------------------------------------------
    # Data portal — database query explorer
    # -----------------------------------------------------------------
    def _get_user_table_access(self, user_info, profile):
        args = (user_info, profile)
        return query_db_api_helpers.get_user_table_access(self, *args)

    def _execute_db_query(self, profile_cfg, query, query_params=None):
        args = (profile_cfg, query, query_params)
        return _impls.ariapp_execute_db_query(self, *args)

    @staticmethod
    def _build_safe_select_query(table_access, query_spec, run_ids):
        args = [table_access, query_spec, run_ids]
        return _impls.ariapp_build_safe_select_query(*args)

    def _ri_query_db_view(self, profile_id):
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_query_db_view(self, **kwargs)

    def _ri_qc_graphs_view(self, profile_id):
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_qc_graphs_view(self, **kwargs)

    def _ri_qc_graphs_max_view(self, profile_id, section, metric_key, view_key):
        args = (profile_id, section, metric_key, view_key)
        return _impls.ariapp_ri_qc_graphs_max_view(self, *args)

    def _load_query_db_presets(self, profile):
        args = [profile,  PACKAGE_DIR, self._db_access_table_keys(),
                self._profile_get_db]
        return query_helpers.load_query_db_presets(*args)

    @staticmethod
    def _parse_text_presets(text, replace_fn):
        return _impls.ariapp_parse_text_presets(text, replace_fn)

    def _api_query_db_schema(self):
        return query_db_api_helpers.api_query_db_schema(self)

    def _api_query_db_run(self):
        return query_db_api_helpers.api_query_db_run(self)

    # -----------------------------------------------------------------
    # Admin user management API
    # -----------------------------------------------------------------
    def _require_admin_user(self):
        return _impls.ariapp_require_admin_user(self)

    def _api_user_search(self):
        return admin_user_api_helpers.api_user_search(self)

    def _api_user_update_groups(self):
        return admin_user_api_helpers.api_user_update_groups(self)

    def _api_user_update_instruments(self):
        return admin_user_api_helpers.api_user_update_instruments(self)

    def _api_user_delete(self):
        return _impls.ariapp_api_user_delete(self)

    # -----------------------------------------------------------------
    # Admin login-as API
    # -----------------------------------------------------------------
    def _api_login_as_search(self):
        return admin_user_api_helpers.api_login_as_search(self)

    def _api_login_as_set(self):
        return admin_user_api_helpers.api_login_as_set(self)

    @staticmethod
    def _api_login_as_clear():
        """Clear the login-as session."""
        if "user" not in session:
            return jsonify(success=False, error="Not logged in"), 401
        session.pop("login_as", None)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Admin science groups API
    # -----------------------------------------------------------------
    def _require_sci_group_perm(self):
        return _impls.ariapp_require_sci_group_perm(self)

    def _api_sci_groups_list(self):
        return sci_groups_api_helpers.api_sci_groups_list(self)

    def _api_sci_groups_get(self):
        return _impls.ariapp_api_sci_groups_get(self)

    def _api_sci_groups_refresh_run_ids(self):
        return _impls.ariapp_api_sci_groups_refresh_run_ids(self)

    def _api_sci_groups_save(self):
        return sci_groups_api_helpers.api_sci_groups_save(self)

    def _api_sci_groups_save_all(self):
        return sci_groups_api_helpers.api_sci_groups_save_all(self)

    def _api_sci_groups_create(self):
        return sci_groups_api_helpers.api_sci_groups_create(self)

    def _api_sci_groups_delete(self):
        return sci_groups_api_helpers.api_sci_groups_delete(self)

    def _api_sci_groups_export(self):
        return sci_groups_api_helpers.api_sci_groups_export(self)

    def _api_sci_groups_import(self):
        return sci_groups_api_helpers.api_sci_groups_import(self)

    def _api_sci_groups_io_export(self):
        return sci_groups_api_helpers.api_sci_groups_io_export(self)

    def _api_sci_groups_io_import(self):
        return sci_groups_api_helpers.api_sci_groups_io_import(self)

    # -----------------------------------------------------------------
    # APERO profiles API
    # -----------------------------------------------------------------
    def _require_apero_profile_perm(self):
        return _impls.ariapp_require_apero_profile_perm(self)

    def _require_user_db_access_perm(self):
        return _impls.ariapp_require_user_db_access_perm(self)

    @staticmethod
    def _db_access_table_keys() -> dict:
        """Map UI table labels to APERO profile table-name keys."""
        
        dbaccess = dict()
        dbaccess['ASTROM'] = "ASTROM_TABLENAME"
        dbaccess['CALIB'] = "CALIB_TABLENAME"
        dbaccess['FINDEX'] = "FINDEX_TABLENAME"
        dbaccess['LOG'] = "LOG_TABLENAME"
        dbaccess['TELLU'] = "TELLU_TABLENAME"
        dbaccess['REJECT'] = "REJECT_TABLENAME"
        
        return dbaccess

    def _editable_groups_for_editor(self, user_info, perms):
        return _impls.ariapp_editable_groups_for_editor(self, user_info, perms)

    def _find_accessible_profile(self, user_info, profile_id: str, 
                                 instrument: str = ""):
        """Find one profile in the editor's accessible profile set."""
        for profile in auth.get_accessible_profiles(user_info, self.ari_groups):
            if profile.get("profile_id") != profile_id:
                continue
            if instrument and profile.get("instrument") != instrument:
                continue
            return profile
        return None

    @staticmethod
    def _q_ident(name: str) -> str:
        """Quote SQL identifier path safely (schema/table)."""
        return profile_utils.q_ident(name)

    @staticmethod
    def _profile_get_db(cfg: dict, key: str, default: Any = "") -> Any:
        """Get a DB key from nested ``database`` with flat fallback."""
        return profile_utils.profile_get_db(cfg, key, default)

    @staticmethod
    def _profile_get_path(cfg: dict, key: str, default: Any = "") -> Any:
        """Get a path key from nested ``paths`` with flat fallback."""
        return profile_utils.profile_get_path(cfg, key, default)

    @staticmethod
    def _profile_get_general(cfg: dict, key: str, default: Any = "") -> Any:
        """Get a general key from nested ``general`` with flat fallback."""
        return profile_utils.profile_get_general(cfg, key, default)

    def _profile_db_params(self, profile_cfg: dict) -> dict:
        return apero_profiles_api_helpers.profile_db_params(self, profile_cfg)

    def _resolve_db_payload_for_test(self, data: dict) -> dict:
        return (
            apero_profiles_api_helpers.resolve_db_payload_for_test(
                self, data
            )
        )

    def _resolve_profile_db_test_target(self, mode: str, host: str,  port: str,
                                        username: str, password: str, 
                                        db_name: str, use_ssh_tunnel: bool,
                                        ssh_config_host: str,
                                        ssh_local_port: str,
                                        ssh_remote_port: str):
        args = (mode, host, port, username, password, db_name,
                use_ssh_tunnel, ssh_config_host, ssh_local_port,
                ssh_remote_port)
        return _impls.ariapp_resolve_profile_db_test_target(self, *args)

    def _validate_profile_database(self, profile_cfg: dict) -> dict:
        return _impls.ariapp_validate_profile_database(self, profile_cfg)

    def _fetch_table_columns(self, profile_cfg: dict, table_name: str):
        args = (profile_cfg, table_name)
        return apero_profiles_api_helpers.fetch_table_columns(self, *args)

    def _profile_db_access_health(self, entry: dict, table_names: list) -> str:
        return _impls.ariapp_profile_db_access_health(self, entry, table_names)

    def _build_user_db_access_health_report(self, user_info: dict) -> dict:
        return user_db_access_api_helpers.build_user_db_access_health_report(
            app=self,
            user_info=user_info,
        )

    def _api_user_db_access_profiles(self):
        return _impls.ariapp_api_user_db_access_profiles(self)

    def _api_user_db_access_details(self):
        return user_db_access_api_helpers.api_user_db_access_details(self)

    def _api_user_db_access_health_check(self):
        return _impls.ariapp_api_user_db_access_health_check(self)

    def _api_user_db_access_save(self):
        return user_db_access_api_helpers.api_user_db_access_save(self)

    def _api_apero_profiles_list(self):
        return apero_profiles_api_helpers.api_apero_profiles_list(self)

    def _api_apero_profiles_overview(self):
        return _impls.ariapp_api_apero_profiles_overview(self)

    def _api_apero_profiles_save(self):
        return apero_profiles_api_helpers.api_apero_profiles_save(
            self,
            package_dir=PACKAGE_DIR,
        )

    def _api_apero_profiles_delete(self):
        return _impls.ariapp_api_apero_profiles_delete(self)

    def _api_apero_profiles_reorder(self):
        return _impls.ariapp_api_apero_profiles_reorder(self)

    def _api_apero_profiles_validate(self):
        return _impls.ariapp_api_apero_profiles_validate(self)

    def _api_apero_profiles_browse(self):
        return _impls.ariapp_api_apero_profiles_browse(self)

    def _api_apero_profiles_update_groups(self):
        return _impls.ariapp_api_apero_profiles_update_groups(self)

    def _api_apero_profiles_toggle_disabled(self):
        return apero_profiles_api_helpers.api_apero_profiles_toggle_disabled(
            self
        )

    def _api_apero_profiles_test_db(self):
        return _impls.ariapp_api_apero_profiles_test_db(self)

    def _api_apero_profiles_list_tables(self):
        return apero_profiles_api_helpers.api_apero_profiles_list_tables(self)

    # -----------------------------------------------------------------
    # Interactive SSH tunnel for APERO profile DB connections
    # -----------------------------------------------------------------
    def _api_apero_profiles_ssh_tunnel_start(self):
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_start(self)

    def _api_apero_profiles_ssh_tunnel_poll(self):
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_poll(self)

    def _api_apero_profiles_ssh_tunnel_send(self):
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_send(self)

    def _api_apero_profiles_ssh_tunnel_close(self):
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_close(self)

    def _api_db_ssh_tunnel_status(self):
        return _impls.ariapp_api_db_ssh_tunnel_status(self)

    def _api_db_ssh_tunnel_ssh_hosts(self):
        """List SSH config host aliases from ~/.ssh/config for dropdowns."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401

        return jsonify(success=True, hosts=self._list_ssh_config_hosts())

    def _api_db_ssh_tunnel_list(self):
        return _impls.ariapp_api_db_ssh_tunnel_list(self)

    def _api_db_ssh_tunnel_save(self):
        return _impls.ariapp_api_db_ssh_tunnel_save(self)

    def _api_db_ssh_tunnel_delete(self):
        return _impls.ariapp_api_db_ssh_tunnel_delete(self)

    def _api_db_ssh_tunnel_ensure(self):
        return _impls.ariapp_api_db_ssh_tunnel_ensure(self)

    def _api_db_ssh_tunnel_close(self):
        return db_tunnel_api_helpers.api_db_ssh_tunnel_close(self)

    def _api_db_ssh_tunnel_test(self):
        return db_tunnel_api_helpers.api_db_ssh_tunnel_test(self)

    def _api_database_setup_local_db_list(self):
        return _impls.ariapp_api_database_setup_local_db_list(self)

    def _api_database_setup_local_db_save(self):
        return db_tunnel_api_helpers.api_database_setup_local_db_save(self)

    def _api_database_setup_local_db_delete(self):
        return _impls.ariapp_api_database_setup_local_db_delete(self)

    def _api_database_setup_local_db_test(self):
        return _impls.ariapp_api_database_setup_local_db_test(self)

    def _api_apero_profiles_test_tables(self):
        return apero_profiles_api_helpers.api_apero_profiles_test_tables(self)

    # -----------------------------------------------------------------
    # Async tasks API
    # -----------------------------------------------------------------
    def _require_async_tasks_perm(self):
        return _impls.ariapp_require_async_tasks_perm(self)

    @staticmethod
    def _coerce_task_frequency(value, default: float = 24.0) -> float:
        """Normalize a task frequency value in hours."""
        return async_task_helpers.coerce_task_frequency(value, default)

    @staticmethod
    def _coerce_task_enabled(value, default: bool = False) -> bool:
        """Normalize a task enabled flag."""
        return async_task_helpers.coerce_task_enabled(value, default)

    @staticmethod
    def _is_global_scope(instrument: str) -> bool:
        """Return True if this task scope is the shared global scope."""
        return async_task_helpers.is_global_scope(instrument)

    def _task_keys_for_scope(self, instrument: str) -> list:
        """Return task keys allowed in a given scope from tasks.TYPE."""
        return async_task_helpers.task_keys_for_scope(instrument)

    def _merge_async_task_catalog(self, instrument: str, all_tasks: dict):
        """Merge persisted task overrides with the task catalog defaults."""
        
        kwargs = dict(instrument=instrument, all_tasks=all_tasks)
        merged, changed = async_task_helpers.merge_async_task_catalog(**kwargs)
        return merged, changed

    def _api_async_tasks_list(self):
        return async_tasks_api_helpers.api_async_tasks_list(self)

    def _api_async_tasks_global_list(self):
        return async_tasks_api_helpers.api_async_tasks_global_list(self)

    def _api_async_tasks_task_list(self):
        return async_tasks_api_helpers.api_async_tasks_task_list(self)

    def _api_async_tasks_save(self):
        return async_tasks_api_helpers.api_async_tasks_save(self)

    def _api_async_tasks_delete(self):
        return _impls.ariapp_api_async_tasks_delete(self)

    def _api_async_tasks_reorder(self):
        return _impls.ariapp_api_async_tasks_reorder(self)

    def _api_async_tasks_toggle(self):
        return _impls.ariapp_api_async_tasks_toggle(self)

    def _api_async_tasks_run_now(self):
        return async_tasks_api_helpers.api_async_tasks_run_now(self)

    def _api_async_tasks_run_all(self):
        return async_tasks_api_helpers.api_async_tasks_run_all(self)

    def _api_async_tasks_stop(self):
        """Stop queued tasks and apply cooldown before any next attempt."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        data = request.get_json(silent=True) or {}
        instrument = str(data.get("instrument", "") or "").strip() or None
        result = task_runner.stop_all_with_cooldown(instrument=instrument)
        return jsonify(success=True, **result)

    def _api_async_tasks_kill_all(self):
        """Immediately interrupt running task and clear queue."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(
                success=False, error='Unauthorized'
            ), 401
        result = task_runner.kill_all()
        return jsonify(success=True, **result)

    def _api_async_tasks_cancel_task(self):
        return _impls.ariapp_api_async_tasks_cancel_task(self)

    def _api_async_tasks_clear_history(self):
        return _impls.ariapp_api_async_tasks_clear_history(self)

    def _api_async_tasks_status(self):
        return async_tasks_api_helpers.api_async_tasks_status(self)

    def _api_async_tasks_task_log(self):
        return _impls.ariapp_api_async_tasks_task_log(self)

    def _validate_async_task_file_path(self, path: str):
        return _impls.ariapp_validate_async_task_file_path(self, path)

    def _api_async_tasks_read_file(self):
        return async_tasks_api_helpers.api_async_tasks_read_file(self)

    @staticmethod
    def _build_json_preview_table(data, max_rows: int = 200) -> dict:
        kwargs = dict(data=data, max_rows=max_rows)
        return async_tasks_api_helpers.build_json_preview_table(**kwargs)

    def _api_async_tasks_download_file(self):
        return _impls.ariapp_api_async_tasks_download_file(self)

    # -----------------------------------------------------------------
    # User links API
    # -----------------------------------------------------------------
    def _api_user_links_get(self):
        return _impls.ariapp_api_user_links_get(self)

    def _api_user_links_add(self):
        return _impls.ariapp_api_user_links_add(self)

    def _api_user_links_update(self):
        return _impls.ariapp_api_user_links_update(self)

    def _api_user_links_remove(self):
        return _impls.ariapp_api_user_links_remove(self)

    def _api_user_links_add_section(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        section = str(body.get("section", "")).strip()
        if not section:
            return jsonify(success=False, error="section required"), 400
        data = ud.add_link_section(user_info["username"], section)
        return jsonify(success=True, data=data)

    def _api_user_links_remove_section(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        section = str(body.get("section", "")).strip()
        if not section:
            return jsonify(success=False, error="section required"), 400
        data = ud.remove_link_section(user_info["username"], section)
        return jsonify(success=True, data=data)

    # -----------------------------------------------------------------
    # User notes API
    # -----------------------------------------------------------------
    def _api_user_notes_list(self):
        return _impls.ariapp_api_user_notes_list(self)

    def _api_user_notes_get(self):
        return _impls.ariapp_api_user_notes_get(self)

    def _api_user_notes_save(self):
        return _impls.ariapp_api_user_notes_save(self)

    def _api_user_notes_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        note_id = str(body.get("id", "")).strip()
        if not note_id:
            return jsonify(success=False, error="id required"), 400
        ok = ud.delete_note(user_info["username"], note_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_notes_render(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        content = str(body.get("content", ""))
        html = ud.render_note_html(content)
        return jsonify(success=True, html=html)

    # -----------------------------------------------------------------
    # User preferences API
    # -----------------------------------------------------------------
    def _api_user_prefs_get(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        prefs = ud.load_user_prefs(user_info["username"])
        return jsonify(success=True, prefs=prefs)

    def _api_user_prefs_save(self):
        return _impls.ariapp_api_user_prefs_save(self)

    # -----------------------------------------------------------------
    # User calendar API
    # -----------------------------------------------------------------
    def _api_user_calendar_list(self):
        return _impls.ariapp_api_user_calendar_list(self)

    def _api_user_calendar_save(self):
        return _impls.ariapp_api_user_calendar_save(self)

    def _api_user_calendar_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        event_id = str(body.get("id", "")).strip()
        if not event_id:
            return jsonify(success=False, error="id required"), 400
        ok = ud.delete_event(user_info["username"], event_id)
        return jsonify(success=True, deleted=ok)

    # -----------------------------------------------------------------
    # User todo API
    # -----------------------------------------------------------------
    def _api_user_todo_list(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        items = ud.list_todo_items(user_info["username"])
        metadata = ud.get_todo_metadata(user_info["username"])
        return jsonify(success=True, items=items, metadata=metadata)

    def _api_user_todo_save(self):
        return _impls.ariapp_api_user_todo_save(self)

    def _api_user_todo_toggle(self):
        return _impls.ariapp_api_user_todo_toggle(self)

    def _api_user_todo_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        item_id = str(body.get("id", "")).strip()
        if not item_id:
            return jsonify(success=False, error="id required"), 400
        ok = ud.delete_todo_item(user_info["username"], item_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_todo_reorder(self):
        return _impls.ariapp_api_user_todo_reorder(self)

    # -----------------------------------------------------------------
    # Admin calendar API
    # -----------------------------------------------------------------
    def _require_admin_calendar_perm(self):
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        
        args = (user_info["groups"], self.ari_groups)
        perms = permissions_mod.resolve_user_permissions(*args)
        
        if "view.admin.calendar" not in perms:
            return None, None
        return user_info, perms

    def _api_admin_calendar_list(self):
        user_info, perms = self._require_admin_calendar_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        instrument = request.args.get("instrument", "").strip()
        if not instrument:
            return jsonify(success=False, error="instrument required"), 400
        events = ud.load_instrument_calendar(instrument).get("events", [])
        return jsonify(success=True, events=events)

    def _api_admin_calendar_save(self):
        return _impls.ariapp_api_admin_calendar_save(self)

    def _api_admin_calendar_delete(self):
        return _impls.ariapp_api_admin_calendar_delete(self)

    # -----------------------------------------------------------------
    # ICS feed API — user calendar
    # -----------------------------------------------------------------
    def _api_user_ics_list(self):
        return _impls.ariapp_api_user_ics_list(self)

    def _api_user_ics_add(self):
        return _impls.ariapp_api_user_ics_add(self)

    def _api_user_ics_delete(self):
        return _impls.ariapp_api_user_ics_delete(self)

    def _api_user_ics_refresh(self):
        return _impls.ariapp_api_user_ics_refresh(self)

    def _api_user_ics_edit(self):
        return _impls.ariapp_api_user_ics_edit(self)

    # -----------------------------------------------------------------
    # ICS feed API — instrument / admin calendar
    # -----------------------------------------------------------------
    def _api_admin_ics_list(self):
        return _impls.ariapp_api_admin_ics_list(self)

    def _api_admin_ics_add(self):
        return _impls.ariapp_api_admin_ics_add(self)

    def _api_admin_ics_delete(self):
        return _impls.ariapp_api_admin_ics_delete(self)

    def _api_admin_ics_refresh(self):
        return _impls.ariapp_api_admin_ics_refresh(self)

    def _api_admin_ics_edit(self):
        return _impls.ariapp_api_admin_ics_edit(self)

    # -----------------------------------------------------------------
    # Admin links API
    # -----------------------------------------------------------------
    def _require_admin_links_perm(self):
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"],
            self.ari_groups,
        )
        if "view.admin.links" not in perms:
            return None, None
        return user_info, perms

    def _api_admin_links_get(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        instrument = request.args.get("instrument", "").strip()
        if not instrument:
            return jsonify(success=False, error="instrument required"), 400
        data = ud.load_instrument_links(instrument)
        return jsonify(success=True, data=data)

    def _api_admin_links_add(self):
        return _impls.ariapp_api_admin_links_add(self)

    def _api_admin_links_update(self):
        return _impls.ariapp_api_admin_links_update(self)

    def _api_admin_links_remove(self):
        return _impls.ariapp_api_admin_links_remove(self)

    def _api_admin_links_add_section(self):
        return _impls.ariapp_api_admin_links_add_section(self)

    def _api_admin_links_remove_section(self):
        return _impls.ariapp_api_admin_links_remove_section(self)

    # -----------------------------------------------------------------
    # Admin email API
    # -----------------------------------------------------------------
    def _require_admin_email_perm(self):
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"],
            self.ari_groups,
        )
        return user_info, perms

    def _api_admin_email_test(self):
        return _impls.ariapp_api_admin_email_test(self)

    def _api_admin_email_save(self):
        return _impls.ariapp_api_admin_email_save(self)

    def _api_admin_email_send_test(self):
        return _impls.ariapp_api_admin_email_send_test(self)

    # -----------------------------------------------------------------
    # Admin backup API
    # -----------------------------------------------------------------
    def _require_admin_backup_perm(self):
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"],
            self.ari_groups,
        )
        return user_info, perms

    def _api_admin_backups_test(self):
        return _impls.ariapp_api_admin_backups_test(self)

    def _api_admin_backups_oauth_start(self):
        return _impls.ariapp_api_admin_backups_oauth_start(self)

    def _api_admin_backups_oauth_callback(self):
        return admin_backup_api_helpers.api_admin_backups_oauth_callback(self)

    def _api_admin_backups_test_backup(self):
        return _impls.ariapp_api_admin_backups_test_backup(self)

    def _api_admin_backups_save(self):
        return admin_backup_api_helpers.api_admin_backups_save(self)

    def _api_admin_backups_upload_json(self):
        return admin_backup_api_helpers.api_admin_backups_upload_json(self)

    def _api_admin_backups_list(self):
        return _impls.ariapp_api_admin_backups_list(self)

    def _api_admin_backups_delete(self):
        return _impls.ariapp_api_admin_backups_delete(self)

    def _api_admin_backups_delete_all(self):
        return _impls.ariapp_api_admin_backups_delete_all(self)

    def _api_admin_backups_sync(self):
        return _impls.ariapp_api_admin_backups_sync(self)

    def _api_admin_backups_download(self):
        return _impls.ariapp_api_admin_backups_download(self)

    def _api_admin_backups_sync_from_cloud(self):
        return _impls.ariapp_api_admin_backups_sync_from_cloud(self)

    def _api_admin_backups_validate_dir(self):
        return _impls.ariapp_api_admin_backups_validate_dir(self)

    def _api_admin_backups_browse(self):
        return _impls.ariapp_api_admin_backups_browse(self)

    # -----------------------------------------------------------------
    # SSHFS Management API handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_keys_list(self):
        return _impls.ariapp_api_admin_sshfs_keys_list(self)

    def _api_admin_sshfs_keys_add(self):
        return _impls.ariapp_api_admin_sshfs_keys_add(self)

    def _api_admin_sshfs_keys_delete(self, key_name):
        return _impls.ariapp_api_admin_sshfs_keys_delete(self, key_name)

    def _api_admin_sshfs_mounts_add(self):
        return _impls.ariapp_api_admin_sshfs_mounts_add(self)

    def _api_admin_sshfs_mounts_test_connection(self):
        return _impls.ariapp_api_admin_sshfs_mounts_test_connection(self)

    def _api_admin_sshfs_mounts_update(self, mount_name):
        return _impls.ariapp_api_admin_sshfs_mounts_update(self, mount_name)

    def _api_admin_sshfs_mounts_delete(self, mount_name):
        return _impls.ariapp_api_admin_sshfs_mounts_delete(self, mount_name)

    def _api_admin_sshfs_mounts_mount(self, mount_name):
        return _impls.ariapp_api_admin_sshfs_mounts_mount(self, mount_name)

    def _api_admin_sshfs_mounts_unmount(self, mount_name):
        return _impls.ariapp_api_admin_sshfs_mounts_unmount(self, mount_name)

    def _api_admin_sshfs_mounts_unmount_lazy(self, mount_name):
        args = (mount_name,)
        return _impls.ariapp_api_admin_sshfs_mounts_unmount_lazy(self, *args)

    def _api_admin_sshfs_mounts_status(self):
        return _impls.ariapp_api_admin_sshfs_mounts_status(self)

    def _api_admin_sshfs_mounts_log(self, mount_name):
        return _impls.ariapp_api_admin_sshfs_mounts_log(self, mount_name)

    # -----------------------------------------------------------------
    # Interactive SSH terminal handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_interactive_start_test(self):
        return _impls.ariapp_api_admin_sshfs_interactive_start_test(self)

    def _api_admin_sshfs_interactive_start_mount(self):
        return _impls.ariapp_api_admin_sshfs_interactive_start_mount(self)

    def _api_admin_sshfs_interactive_poll(self):
        return _impls.ariapp_api_admin_sshfs_interactive_poll(self)

    def _api_admin_sshfs_interactive_send(self):
        return _impls.ariapp_api_admin_sshfs_interactive_send(self)

    def _api_admin_sshfs_interactive_close(self):
        return admin_sshfs_api_helpers.api_admin_sshfs_interactive_close(self)

    # -----------------------------------------------------------------
    # Upload management — Admin API
    # -----------------------------------------------------------------
    def _api_admin_uploads_config_get(self):
        return _impls.ariapp_api_admin_uploads_config_get(self)

    def _api_admin_uploads_dir_add(self):
        return _impls.ariapp_api_admin_uploads_dir_add(self)

    def _api_admin_uploads_dir_edit(self):
        return _impls.ariapp_api_admin_uploads_dir_edit(self)

    def _api_admin_uploads_dir_delete(self):
        return _impls.ariapp_api_admin_uploads_dir_delete(self)

    def _api_admin_uploads_quota_get(self):
        return _impls.ariapp_api_admin_uploads_quota_get(self)

    # -----------------------------------------------------------------
    # Upload management — User API
    # -----------------------------------------------------------------
    def _api_user_uploads_list(self):
        return _impls.ariapp_api_user_uploads_list(self)

    def _api_user_uploads_upload(self):
        return _impls.ariapp_api_user_uploads_upload(self)

    def _api_user_uploads_delete(self):
        return _impls.ariapp_api_user_uploads_delete(self)

    def _api_user_uploads_share(self):
        return _impls.ariapp_api_user_uploads_share(self)

    def _uploads_share_download(self, token):
        return _impls.ariapp_uploads_share_download(self, token)

    # -----------------------------------------------------------------
    # Run override
    # -----------------------------------------------------------------
    def run(self, host=None, port=None, debug=True, **kwargs):
        return _impls.ariapp_run(self, host, port, debug, **kwargs)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
