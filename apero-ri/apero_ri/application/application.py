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
    admin_assets_api_helpers,
    admin_backup_api_helpers,
    admin_cache_helpers,
    admin_health_helpers,
    admin_sshfs_api_helpers,
    admin_user_api_helpers,
    apero_profiles_api_helpers,
)
from apero_ri.application import ariapp_impls as _impls
from apero_ri.application import apero_queue_api_helpers
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
from apero_ri.application import run_ids_api_helpers
from apero_ri.application import search_helpers
from apero_ri.application import server_sync_api_helpers
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

    def __init__(self, **kwargs: Any) -> None:
        """Initialize ARI services, routes, and shared Flask settings."""
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
    def ari_groups(self) -> Any:
        """Return the cached group definitions, refreshing expired data."""
        now = time.monotonic()
        with ARIApp._groups_lock:
            cached = ARIApp._groups_cache
            if cached and cached.get("expires", 0) > now:
                return cached["data"]
            data = perms.load_groups()
            ARIApp._groups_cache = {
                "data": data,
                "expires": now + ARIApp._GROUPS_TTL,
            }
            return data

    @ari_groups.setter
    def ari_groups(self, _value: Any) -> None:
        """Invalidate cached group definitions after a configuration change."""
        # Invalidate the cache so the next read fetches fresh data.
        with ARIApp._groups_lock:
            ARIApp._groups_cache = {}

    # -----------------------------------------------------------------
    # Argument parsing
    # -----------------------------------------------------------------
    @staticmethod
    def _get_arguments() -> argparse.Namespace:
        """Parse command-line options for the ARI server."""
        return _impls.ariapp_get_arguments()

    @staticmethod
    def _resolve_host(host: str) -> str:
        """Resolve the configured host into a bindable address."""
        return _impls.ariapp_resolve_host(host)

    # -----------------------------------------------------------------
    # Secret key management
    # -----------------------------------------------------------------
    @staticmethod
    def _load_or_create_secret() -> str:
        """Load the session secret or create one for this installation."""
        return _impls.ariapp_load_or_create_secret()

    # -----------------------------------------------------------------
    # Production hardening (security headers, proxy support, limits)
    # -----------------------------------------------------------------
    def _configure_production_hardening(self) -> None:
        """Apply security headers, proxy handling, and request limits."""
        return _impls.ariapp_configure_production_hardening(self)

    # -----------------------------------------------------------------
    # Context processors (available in every template)
    # -----------------------------------------------------------------
    def _register_context_processors(self) -> None:
        """Register template context values shared across ARI pages."""
        return _impls.ariapp_register_context_processors(self)

    # -----------------------------------------------------------------
    # Route registration
    # -----------------------------------------------------------------
    def _register_routes(self) -> None:
        """Register page and API endpoints on this Flask application."""
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

    def _build_sidebar_context(
        self, page_id: str, perms: Any, user_info: Any = None
    ) -> Any:
        """Build the permission-aware sidebar context for a page."""
        args = (page_id, perms, user_info)
        return _impls.ariapp_build_sidebar_context(self, *args)

    def _build_home_sidebar_context(
        self, perms: Any, user_info: Any = None
    ) -> Any:
        """Build the sidebar context used by home pages."""
        return _impls.ariapp_build_home_sidebar_context(self, perms, user_info)

    def _build_home_page_context(
        self, user_info: Any, perms: Any
    ) -> dict:
        """Assemble user-specific values for the home page."""
        return _impls.ariapp_build_home_page_context(self, user_info, perms)

    def _make_page_view(self, page_id: str) -> Any:
        """Create a Flask view function for a registered page."""
        return page_view_helpers.make_page_view(
            self, page_id=page_id, package_dir=PACKAGE_DIR
        )

    # -----------------------------------------------------------------
    # Data portal helpers
    # -----------------------------------------------------------------
    def _instrument_colors(self) -> Any:
        """Map each instrument to a palette entry (stable ordering)."""
        return (
            data_portal_view_helpers.instrument_color_helpers
            .instrument_colors()
        )

    @staticmethod
    def _get_instrument_run_ids(instrument: str) -> list:
        """Return catalogued run IDs available for an instrument."""
        return _impls.ariapp_get_instrument_run_ids(instrument)

    @staticmethod
    def _get_instrument_run_id_pi_names(instrument: str) -> dict:
        """Return the PI-name lookup for an instrument's run IDs."""
        return _impls.ariapp_get_instrument_run_id_pi_names(instrument)

    @staticmethod
    def _is_all_science_group(name: str) -> bool:
        """Return True when a science-group name is the reserved All group."""
        return str(name or "").strip().lower() == "all"

    def _sync_all_science_group(self, instrument: str, 
                                groups: Optional[dict] = None,
                                run_ids: Optional[list] = None,
                                persist: bool = True) -> Any:
        """Keep the reserved All science group aligned with run IDs."""
        args = (instrument, groups, run_ids, persist)
        return _impls.ariapp_sync_all_science_group(self, *args)

    def _get_user_accessible_run_ids(
        self, user_info: Any, instrument: str
    ) -> Any:
        """Return run IDs visible to a user for one instrument."""
        args = (user_info, instrument)
        return _impls.ariapp_get_user_accessible_run_ids(self, *args)

    def _page_template_meta(
        self, template_id: str, **tokens: Any
    ) -> dict:
        """Build display metadata for a documentation template."""
        return _impls.ariapp_page_template_meta(self, template_id, **tokens)

    def _build_data_portal_sidebar_tree(
        self,
        accessible_profiles: list,
        active_page_id: str,
        user_permissions: Any,
        user_info: Any = None,
        current_profile_id: Optional[str] = None,
        objname: Optional[str] = None,
        include_children: bool = True,
    ) -> list:
        """Build the data-portal sidebar tree for accessible profiles."""
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

    def _build_ri_context(
        self, user_info: Any, user_permissions: Any
    ) -> Any:
        """Assemble shared RI template context for the current user."""
        kwargs = dict(user_info=user_info, user_permissions=user_permissions)
        return user_context_helpers.build_ri_context(self, **kwargs)

    def _build_user_data_access_context(self, user_info: Any) -> Any:
        """Build the user's data-access settings page context."""
        args = (user_info,)
        return user_context_helpers.build_user_data_access_context(self, *args)

    def _build_user_support_context(self, user_info: Any) -> Any:
        """Build support-page context for the current user."""
        return user_context_helpers.build_user_support_context(self, user_info)

    def _build_user_links_context(self, user_info: Any) -> Any:
        """Build context for the user's saved links page."""
        return user_context_helpers.build_user_links_context(
            self, user_info
        )

    def _build_user_api_access_context(self, user_info: Any) -> Any:
        """Build context for the user's API access page."""
        return user_context_helpers.build_user_api_access_context(user_info)

    def _build_user_calendar_context(self, user_info: Any) -> Any:
        """Build the user's calendar page context."""
        return user_context_helpers.build_user_calendar_context(
            self, user_info
        )

    def _build_admin_instrument_context(
        self, user_info: Any, perms: Any, manage_prefix: str
    ) -> Any:
        """Build instrument-management context filtered by permissions."""
        return user_context_helpers.build_admin_instrument_context(
            user_info, perms, manage_prefix
        )

    def _build_admin_email_context(self, perms: Any) -> Any:
        """Build the administrator email-settings page context."""
        return _impls.ariapp_build_admin_email_context(self, perms)

    @staticmethod
    def _resolve_local_data_dir() -> Path:
        """Resolve the local data directory used by the RI application."""
        return _impls.ariapp_resolve_local_data_dir()

    def _build_admin_backup_context(self, perms: Any) -> Any:
        """Build context for backup configuration and status."""
        return _impls.ariapp_build_admin_backup_context(self, perms)

    def _build_admin_sshfs_context(self, perms: Any) -> Any:
        """Build context for configured SSHFS mounts."""
        return _impls.ariapp_build_admin_sshfs_context(self, perms)

    def _build_admin_manage_instruments_context(
        self, perms: Any
    ) -> Any:
        """Build context for instrument and science-group administration."""
        return _impls.ariapp_build_admin_manage_instruments_context(
            self, perms
        )

    def _api_manage_instruments_groups_create(self) -> Any:
        """Create a science group through the instrument admin API."""
        return _impls.ariapp_api_manage_instruments_groups_create(self)

    def _api_manage_instruments_groups_delete(self) -> Any:
        """Delete a science group through the instrument admin API."""
        return _impls.ariapp_api_manage_instruments_groups_delete(self)

    def _api_manage_instruments_add(self) -> Any:
        """Add an instrument to the managed instrument list."""
        return _impls.ariapp_api_manage_instruments_add(self)

    def _api_manage_instruments_remove(self) -> Any:
        """Remove an instrument from the managed instrument list."""
        return _impls.ariapp_api_manage_instruments_remove(self)

    def _api_manage_instruments_rename(self) -> Any:
        """Rename an instrument in the managed instrument list."""
        return _impls.ariapp_api_manage_instruments_rename(self)

    def _api_manage_instruments_yaml_get(self) -> Any:
        """Return the instrument-management YAML configuration."""
        return _impls.ariapp_api_manage_instruments_yaml_get(self)

    def _api_manage_instruments_yaml_save(self) -> Any:
        """Validate and save instrument-management YAML configuration."""
        return _impls.ariapp_api_manage_instruments_yaml_save(self)

    # -----------------------------------------------------------------
    # Vault API
    # -----------------------------------------------------------------
    def _require_vault_perm(self) -> Any:
        """Return user and permissions when vault access is allowed."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        resolved = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
        if "manage.admin.vault" not in resolved:
            return None, None
        return user_info, resolved

    def _build_admin_vault_context(self, perms: Any) -> Any:
        """Build context for the administrator credential vault."""
        return _impls.ariapp_build_admin_vault_context(
            self, perms
        )

    def _build_admin_server_information_context(self, perms: Any) -> Any:
        """Build context for the server-information page."""
        return _impls.ariapp_build_admin_server_information_context(
            self, perms
        )

    def _api_clocks_get(self) -> Any:
        """Return configured clocks for navigation and user pages.

        :return: JSON response containing the configured clock rows.
        """
        return _impls.ariapp_api_clocks_get(self)

    def _api_admin_clocks(self) -> Any:
        """Read or update administrator-managed clocks.

        :return: JSON response from the permission-checked clock API.
        """
        return _impls.ariapp_api_admin_clocks(self)

    def _api_admin_vault_list(self) -> Any:
        """List entries in the administrator credential vault."""
        return _impls.ariapp_api_vault_list(self)

    def _api_admin_vault_get(self) -> Any:
        """Retrieve one administrator vault entry."""
        return _impls.ariapp_api_vault_get(self)

    def _api_admin_vault_add(self) -> Any:
        """Add an entry to the administrator credential vault."""
        return _impls.ariapp_api_vault_add(self)

    def _api_admin_vault_update(self) -> Any:
        """Update an administrator credential vault entry."""
        return _impls.ariapp_api_vault_update(self)

    def _api_admin_vault_delete(self) -> Any:
        """Delete an administrator credential vault entry."""
        return _impls.ariapp_api_vault_delete(self)

    def _api_admin_vault_export(self) -> Any:
        """Export entries from the administrator credential vault."""
        return _impls.ariapp_api_vault_export(self)

    def _api_admin_vault_import(self) -> Any:
        """Import entries into the administrator credential vault."""
        return _impls.ariapp_api_vault_import(self)

    # -----------------------------------------------------------------
    # Server sync API (admin page + peer protocol)
    # -----------------------------------------------------------------
    def _api_server_sync_admin(self, action: str) -> Any:
        """Handle an administrator request to synchronize servers."""
        return server_sync_api_helpers.admin_api(self, action)

    def _api_server_sync_peer(self, action: str) -> Any:
        """Handle a peer-to-peer server synchronization request."""
        return server_sync_api_helpers.peer_api_view(self, action)

    # -----------------------------------------------------------------
    # APERO queue setup API (admin) and dashboard proxy (monitor)
    # -----------------------------------------------------------------
    def _api_apero_queue_admin(self, action: str) -> Any:
        """Handle an administrator action on the APERO job queue."""
        return apero_queue_api_helpers.admin_api(self, action)

    def _monitor_apero_queue_proxy(
        self, name: str, subpath: str = ''
    ) -> Any:
        """Proxy a monitor request to an APERO queue service endpoint."""
        return apero_queue_api_helpers.proxy_view(self, name, subpath)

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
        """Build database connection settings for a named SSH tunnel."""
        args = (tunnel_name, tunnel_def, mode)
        return _impls.ariapp_build_db_tunnel_runtime_params(self, *args)

    @staticmethod
    def _list_ssh_config_hosts() -> List[str]:
        """List host aliases defined in the user's SSH configuration."""
        return _impls.ariapp_list_ssh_config_hosts()

    def _list_db_tunnel_rows(self) -> List[dict]:
        """Return normalized rows for configured database connections."""
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

    def _build_admin_db_tunnel_context(
        self, user_info: Any, perms: Any
    ) -> dict:
        """Build database-tunnel settings for the administrator page."""
        _ = user_info
        tunnel_rows = self._list_db_tunnel_rows()
        local_db = self._load_local_db_definitions()
        
        cond = "manage.apero_profile" in (perms or set())
        
        tcontext = dict()
        tcontext['can_manage_db_tunnel'] = cond
        tcontext['db_tunnels'] = [row.get("name", "") for row in tunnel_rows]
        tcontext['db_local_databases'] = sorted(local_db.keys())

        return tcontext

    def _build_admin_cache_context(self, perms: Any) -> Any:
        """Build context for administrator cache controls."""
        return admin_cache_helpers.build_admin_cache_context(self, perms)

    def _api_admin_cache_reset_timings(self) -> Any:
        """Reset cache timing statistics through the admin API."""
        return _impls.ariapp_api_admin_cache_reset_timings(self)

    def _api_admin_cache_save(self) -> Any:
        """Persist administrator cache settings."""
        return _impls.ariapp_api_admin_cache_save(self)

    def _api_admin_cache_purge(self) -> Any:
        """Purge cached plot data through the admin API."""
        return _impls.ariapp_api_admin_cache_purge(self)

    def _build_admin_download_mgmt_context(self, perms: Any) -> Any:
        """Build context for download-management settings."""
        return _impls.ariapp_build_admin_download_mgmt_context(self, perms)

    def _api_admin_dm_save_settings(self) -> Any:
        """Save administrator download-management settings."""
        return _impls.ariapp_api_admin_dm_save_settings(self)

    def _api_admin_dm_reset_user(self) -> Any:
        """Reset download-management state for a selected user."""
        return _impls.ariapp_api_admin_dm_reset_user(self)

    # -----------------------------------------------------------------
    # Token-based API auth helper
    # -----------------------------------------------------------------
    @staticmethod
    def _get_api_user() -> Optional[dict]:
        """Resolve the user authenticated by an API token, if present."""
        return _impls.ariapp_get_api_user()

    # -----------------------------------------------------------------
    # User API token endpoints
    # -----------------------------------------------------------------
    def _api_user_token_generate(self) -> Any:
        """Generate a new API token for the logged-in user."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error="Not logged in"), 401
        body = request.get_json(silent=True) or {}
        label = str(body.get("label", "")).strip()[:100]
        token = at.generate_token(user_info["username"], label)
        return jsonify(success=True, token=token)

    def _api_user_token_revoke(self) -> Any:
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
    def _admin_health_cache_key(perms: Any) -> str:
        """Stable key for admin-health cache entries."""
        return "|".join(sorted(perms))

    def _load_health_cache_from_disk(self) -> None:
        """Restore cached admin-health data from its on-disk store."""
        return _impls.ariapp_load_health_cache_from_disk(self)

    def _save_health_cache_to_disk(self) -> None:
        """Persist the current admin-health cache to disk."""
        return _impls.ariapp_save_health_cache_to_disk(self)

    def _start_admin_health_refresher(self) -> None:
        """Start the background worker that refreshes admin-health data."""
        return _impls.ariapp_start_admin_health_refresher(self)

    def _admin_health_refresher_loop(self) -> None:
        """Run the recurring admin-health refresh worker."""
        return _impls.ariapp_admin_health_refresher_loop(self)

    def _admin_health_digest_loop(self) -> None:
        """Run the recurring admin-health digest worker."""
        return _impls.ariapp_admin_health_digest_loop(self)

    def _refresh_admin_health_entry(
        self, cache_key: str, user_info: Any, perms: Any
    ) -> None:
        """Refresh one cached health entry for a user and permission set."""
        args = (cache_key, user_info, perms)
        return _impls.ariapp_refresh_admin_health_entry(self, *args)

    def _spawn_admin_health_refresh(
        self, cache_key: str, user_info: Any, perms: Any
    ) -> None:
        """Schedule an asynchronous refresh for one admin-health entry."""
        args = (cache_key, user_info, perms)
        return _impls.ariapp_spawn_admin_health_refresh(self, *args)

    def shutdown(self) -> None:
        """Stop background workers and release application resources."""
        return _impls.ariapp_shutdown(self)

    def _get_admin_health(
        self,
        user_info: Any,
        perms: Any,
        force: bool = False,
        allow_async_refresh: bool = True,
    ) -> Any:
        """Return cached or refreshed health data for the current admin."""
        kwargs = dict(user_info=user_info,
                      perms=perms, force=force,
                      allow_async_refresh=allow_async_refresh)
        return admin_health_helpers.get_admin_health(self, **kwargs)

    def _refresh_admin_health_after_change(
        self, user_info: Any = None, perms: Any = None
    ) -> None:
        """Refresh health entries affected by an administrative change."""
        args = (user_info, perms)
        return _impls.ariapp_refresh_admin_health_after_change(self, *args)

    def _build_admin_card_health_uncached(
        self, user_info: Any, perms: Any
    ) -> dict:
        """Build admin-card health details without consulting the cache."""
        kwargs = dict(user_info=user_info, perms=perms)
        return admin_health_helpers.build_admin_card_health_uncached(
            self, **kwargs
        )

    def _build_admin_health_rows(self, health: dict) -> list:
        """Convert admin-health details into rows for the interface."""
        return admin_health_helpers.build_admin_health_rows(self, health)

    def _api_admin_health_update(self) -> Any:
        """Handle a request to refresh administrative health data."""
        return _impls.ariapp_api_admin_health_update(self)

    def _api_admin_audit_log(self) -> Any:
        """Return the administrative audit log response."""
        return _impls.ariapp_api_admin_audit_log(self)

    def _api_admin_health_history(self) -> Any:
        """Return historical administrative health records."""
        return _impls.ariapp_api_admin_health_history(self)

    def _api_admin_health_patch(self) -> Any:
        """Apply an administrative health configuration patch."""
        return _impls.ariapp_api_admin_health_patch(self)

    def _api_admin_health_config_get(self) -> Any:
        """Return the current administrative health configuration."""
        return _impls.ariapp_api_admin_health_config_get(self)

    def _api_admin_health_config_save(self) -> Any:
        """Save administrative health configuration from the request."""
        return _impls.ariapp_api_admin_health_config_save(self)

    def _build_apero_profiles_overview_status(self) -> dict:
        """Build status data for the APERO profiles overview."""
        return apero_profiles_api_helpers.build_apero_profiles_overview_status(
            self
        )

    def _ri_profile_view(self, profile_id: str) -> Any:
        """Render the data portal page for one APERO profile."""
        return data_portal_view_helpers.ri_profile_view(self, profile_id)

    def _ri_favourites_objects_view(self, profile_id: str) -> Any:
        """Render the saved favourite objects for one profile."""
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_favourites_objects_view(
            self, **kwargs
        )

    def _ri_object_groups_view(self, profile_id: str) -> Any:
        """Render the object-group page for one profile."""
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_object_groups_view(
            self, **kwargs
        )

    def _ri_object_group_summary_view(
        self,
        profile_id: str,
        group_name: str,
    ) -> Any:
        """Render the summary table for one object group."""
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
        profile_id: str,
        section_name: str,
    ) -> Any:
        """Render a summary of one favourite-object section."""
        kwargs = dict(
            profile_id=profile_id,
            section_name=section_name,
        )
        return data_portal_view_helpers.ri_favourites_summary_view(
            self,
            **kwargs,
        )

    def _api_object_comments_list(self) -> Any:
        """List comments attached to an object."""
        return object_comments_api_helpers.api_object_comments_list(self)

    def _api_object_comments_add(self) -> Any:
        """Add a comment to an object."""
        return object_comments_api_helpers.api_object_comments_add(self)

    def _api_object_comments_edit(self) -> Any:
        """Edit an existing object comment."""
        return object_comments_api_helpers.api_object_comments_edit(self)

    def _api_object_comments_delete(self) -> Any:
        """Delete an object comment."""
        return object_comments_api_helpers.api_object_comments_delete(self)

    def _api_object_groups_list(self) -> Any:
        """List object groups available to the current user."""
        return object_groups_api_helpers.api_object_groups_list(self)

    def _api_object_groups_for_object(self) -> Any:
        """List groups containing the requested object."""
        return object_groups_api_helpers.api_object_groups_for_object(self)

    def _api_object_groups_objects(self) -> Any:
        """List objects assigned to a selected group."""
        return object_groups_api_helpers.api_object_groups_objects(self)

    def _api_object_groups_create(self) -> Any:
        """Create an object group."""
        return object_groups_api_helpers.api_object_groups_create(self)

    def _api_object_groups_delete(self) -> Any:
        """Delete an object group."""
        return object_groups_api_helpers.api_object_groups_delete(self)

    def _api_object_groups_rename(self) -> Any:
        """Rename an object group."""
        return object_groups_api_helpers.api_object_groups_rename(self)

    def _api_object_groups_add_object(self) -> Any:
        """Add one object to a group."""
        return object_groups_api_helpers.api_object_groups_add_object(self)

    def _api_object_groups_add_objects_bulk(self) -> Any:
        """Add multiple objects to a group in one request."""
        return object_groups_api_helpers.api_object_groups_add_objects_bulk(
            self
        )

    def _api_object_groups_add_objects_json(self) -> Any:
        """Add objects from a JSON upload to a group."""
        return (
            object_groups_api_helpers
            .api_object_groups_add_objects_json(self)
        )

    def _api_object_groups_remove_object(self) -> Any:
        """Remove an object from a group."""
        return (
            object_groups_api_helpers
            .api_object_groups_remove_object(self)
        )

    def _api_object_groups_summary_config(self) -> Any:
        """Get the saved summary configuration for an object group."""
        return (
            object_groups_api_helpers
            .api_object_groups_summary_config(self)
        )

    def _api_object_groups_summary_table(self) -> Any:
        """Build the summary table for an object group."""
        return (
            object_groups_api_helpers
            .api_object_groups_summary_table(self)
        )

    def _api_object_groups_summary_export(self) -> Any:
        """Export an object-group summary table."""
        return (
            object_groups_api_helpers
            .api_object_groups_summary_export(self)
        )

    def _api_object_groups_summary_custom_test(self) -> Any:
        """Validate a custom object-group summary expression."""
        return (
            object_groups_api_helpers
            .api_object_groups_summary_custom_test(self)
        )

    def _api_object_groups_allowed_expressions(self) -> Any:
        """List expressions allowed in custom group summaries."""
        return (
            object_groups_api_helpers
            .api_object_groups_allowed_expressions(self)
        )

    def _api_object_groups_admin_custom_columns(self) -> Any:
        """List administrator-defined custom summary columns."""
        return (
            object_groups_api_helpers
            .api_object_groups_admin_custom_columns(self)
        )

    def _api_object_groups_admin_custom_test(self) -> Any:
        """Test a custom summary column before saving it."""
        return (
            object_groups_api_helpers
            .api_object_groups_admin_custom_test(self)
        )

    def _api_admin_clocks(self) -> Any:
        """Return the administrative clock-status response."""
        return _impls.ariapp_api_admin_clocks(self)

    def _api_ri_profile_health(self) -> Any:
        """Return health information for the selected RI profile."""
        return data_portal_api_helpers.api_ri_profile_health(self)

    # -----------------------------------------------------------------
    # Login / Logout views
    # -----------------------------------------------------------------
    def _login_view(self) -> Any:
        """Render or process the login page."""
        return _impls.ariapp_login_view(self)

    def _logout_view(self) -> Any:
        """Clear session and redirect to home."""
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    @staticmethod
    def _get_primary_contact_email(user: dict) -> str:
        """Select the user's primary contact email address."""
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
        """Remove expired password-reset tokens from the user mapping."""
        return _impls.ariapp_cleanup_expired_reset_tokens(self, users)

    def _find_reset_user(self, token: str, users: dict) -> Optional[str]:
        """Find the username associated with an active reset token."""
        return _impls.ariapp_find_reset_user(self, token, users)

    @staticmethod
    def _get_request_ip() -> str:
        """Get client IP, preferring X-Forwarded-For when present."""
        xff = str(request.headers.get("X-Forwarded-For", "")).strip()
        if xff:
            return xff.split(",")[0].strip() or "unknown"
        return str(request.remote_addr or "unknown").strip() or "unknown"

    def _prune_forgot_pw_rate_limit(self, now_ts: float) -> None:
        """Discard expired entries from the password-reset throttle."""
        return _impls.ariapp_prune_forgot_pw_rate_limit(self, now_ts)

    def _register_forgot_pw_attempt(self, ip: str) -> Optional[int]:
        """Record a password-reset attempt and return its retry delay."""
        return user_account_api_helpers.register_forgot_pw_attempt(self, ip)

    def _forgot_password_view(self) -> Any:
        """Render or process the password-reset request page."""
        return user_account_api_helpers.forgot_password_view(self)

    def _reset_password_view(self, token: str) -> Any:
        """Render or process a password reset for the supplied token."""
        return _impls.ariapp_reset_password_view(self, token)

    def _register_view(self) -> Any:
        """Render self-registration page."""
        return render_template("home/register.html",
                               page_label="Register",
                               page_icon="fa-solid fa-user-plus")

    @staticmethod
    def _send_verification_email(recipient_email: str, code: str, 
                                 purpose: str) -> Optional[str]:
        """Send a verification code and return any delivery error."""
        return _impls.ariapp_send_verification_email(recipient_email,
                                                     code, purpose)

    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Validate lowercase username format."""
        return bool(re.match(r"^[a-z][a-z0-9_]{2,63}$", username))

    # -----------------------------------------------------------------
    # Registration & account APIs
    # -----------------------------------------------------------------
    def _api_auth_register_start(self) -> Any:
        """Begin account registration and send its verification code."""
        return user_account_api_helpers.api_auth_register_start(self)

    def _api_auth_register_verify(self) -> Any:
        """Verify a registration code and complete account creation."""
        return user_account_api_helpers.api_auth_register_verify(self)

    def _require_user(self) -> Any:
        """Require a logged in effective user."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None
        return user_info

    def _api_user_account_get(self) -> Any:
        """Return account details for the current user."""
        return _impls.ariapp_api_user_account_get(self)

    def _api_user_account_update(self) -> Any:
        """Update editable account details for the current user."""
        return user_account_api_helpers.api_user_account_update(self)

    def _api_user_account_request_primary_email(self) -> Any:
        """Request verification to change the primary email address."""
        return user_account_api_helpers.api_user_account_request_primary_email(
            self
        )

    def _api_user_account_confirm_primary_email(self) -> Any:
        """Confirm a pending primary-email change with its code."""
        return user_account_api_helpers.api_user_account_confirm_primary_email(
            self
        )

    def _api_user_data_access_request(self) -> Any:
        """Submit a request for access to user data."""
        return user_context_helpers.api_user_data_access_request(self)

    @staticmethod
    def _normalize_pinned_pages(value: Any) -> List[dict]:
        """Normalize persisted page pins into the supported record format."""
        return _impls.ariapp_normalize_pinned_pages(value)

    @staticmethod
    def _normalize_object_section_pins(value: Any) -> List[str]:
        """Normalize the user's saved object-page section order."""
        return _impls.ariapp_normalize_object_section_pins(value)

    def _api_user_pins_list(self) -> Any:
        """List pinned pages for the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401

        username = user_info["username"]
        pins = self._load_user_pins(username)
        return jsonify(success=True, pins=pins)

    def _load_user_pins(self, username: str) -> List[dict]:
        """Load a user's pinned pages."""
        return _impls.ariapp_load_user_pins(self, username)

    def _save_user_pins(self, username: str, pins: List[dict]) -> None:
        """Persist a user's pinned pages."""
        return _impls.ariapp_save_user_pins(self, username, pins)

    def _load_user_object_section_pins(self, username: str) -> List[str]:
        """Load the user's preferred order of object-page sections."""
        return _impls.ariapp_load_user_object_section_pins(self, username)

    def _save_user_object_section_pins(
        self, username: str, pins: List[str]
    ) -> None:
        """Persist the user's preferred object-page section order."""
        return _impls.ariapp_save_user_object_section_pins(self, username, pins)

    def _api_user_pins_toggle(self) -> Any:
        """Toggle a page in the current user's pinned-page list."""
        return user_pins_api_helpers.api_user_pins_toggle(self)

    def _api_user_pins_remove(self) -> Any:
        """Remove a page from the current user's pinned-page list."""
        return user_pins_api_helpers.api_user_pins_remove(self)

    def _api_user_pins_reorder(self) -> Any:
        """Save the current user's pinned-page order."""
        return user_pins_api_helpers.api_user_pins_reorder(self)

    def _api_user_object_sections_get(self) -> Any:
        """Get global object page section pin order for current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        username = user_info["username"]
        pinned = self._load_user_object_section_pins(username)
        return jsonify(success=True, object_section={"pinned": pinned})

    def _api_user_object_sections_toggle(self) -> Any:
        """Toggle a section in the user's object-page section order."""
        return _impls.ariapp_api_user_object_sections_toggle(self)

    def _api_user_object_sections_reorder(self) -> Any:
        """Save the user's object-page section order."""
        return _impls.ariapp_api_user_object_sections_reorder(self)

    def _api_user_favourite_objects_get(self) -> Any:
        """List the current user's favourite objects."""
        return _impls.ariapp_api_user_favourite_objects_get(self)

    def _api_user_favourite_objects_toggle(self) -> Any:
        """Toggle an object's favourite status for the current user."""
        return _impls.ariapp_api_user_favourite_objects_toggle(self)

    def _api_user_favourite_objects_remove(self) -> Any:
        """Remove an object from the current user's favourites."""
        return _impls.ariapp_api_user_favourite_objects_remove(self)

    def _api_user_favourite_objects_reorder(self) -> Any:
        """Save the order of the current user's favourite objects."""
        return user_favourites_api_helpers.api_user_favourite_objects_reorder(
            self
        )

    def _api_user_favourite_objects_last_opened(self) -> Any:
        """Return recently opened favourite objects for the current user."""
        return _impls.ariapp_api_user_favourite_objects_last_opened(self)

    def _api_user_favourite_objects_sections_save(self) -> Any:
        """Save named sections for the user's favourite objects."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_save(self)
        )

    def _api_user_favourite_objects_sections_rename(self) -> Any:
        """Rename a section in the user's favourite-object list."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_rename(self)
        )

    def _api_user_favourite_objects_sections_delete(self) -> Any:
        """Delete a section from the user's favourite-object list."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_sections_delete(self)
        )

    def _api_user_favourite_objects_meta_save(self) -> Any:
        """Save display metadata for the user's favourite objects."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_meta_save(self)
        )

    def _api_user_favourite_objects_add(self) -> Any:
        """Add an object to the user's favourite-object list."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_add(self)
        )

    def _api_user_favourite_objects_add_bulk(self) -> Any:
        """Add multiple objects to the user's favourite-object list."""
        return (
            user_favourites_api_helpers
            .api_user_favourite_objects_add_bulk(self)
        )

    # -----------------------------------------------------------------
    # Documentation views
    # -----------------------------------------------------------------
    def _doc_edit_view(self, page_ref: str) -> Any:
        """Render the editor for a documentation page."""
        return doc_views_helpers.doc_edit_view(self, page_ref)

    def _doc_dynamic_view(self, page_ref: str) -> Any:
        """Render a documentation page assembled from dynamic content."""
        return doc_views_helpers.doc_dynamic_view(self, page_ref)

    def _doc_save_view(self, page_ref: str) -> Any:
        """Save edits submitted for a documentation page."""
        return _impls.ariapp_doc_save_view(self, page_ref)

    def _doc_upload_image(self) -> Any:
        """Handle an uploaded image for the documentation editor."""
        return _impls.ariapp_doc_upload_image(self)

    def _doc_search_index(self) -> Any:
        """Return the documentation search index response."""
        return doc_views_helpers.doc_search_index_view(self)

    @staticmethod
    def _doc_image_view(filename: str) -> Any:
        """Serve documentation images from the static docs image directory."""
        safe_name = Path(filename).name
        if not safe_name or safe_name != filename:
            return ("Invalid image path", 400)
        image_path = docs.DOC_IMAGES / safe_name
        if not image_path.exists() or not image_path.is_file():
            return ("Image not found", 404)
        return send_from_directory(str(docs.DOC_IMAGES), safe_name)

    # -----------------------------------------------------------------
    # Object table sub-page + API
    # -----------------------------------------------------------------
    def _ri_object_table_view(self, profile_id: str) -> Any:
        """Render the observation table page for one profile."""
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_obs_table_view(self, **kwargs)

    def _ri_find_object_view(self, profile_id: str) -> Any:
        """Legacy Find Object URL now redirects to object table."""
        return redirect(url_for("ri_object_table", profile_id=profile_id))

    def _api_profiles_list(self) -> Any:
        """List profiles visible to the current user."""
        return _impls.ariapp_api_profiles_list(self)

    def _api_object_table(self) -> Any:
        """Return object-table rows for the selected profile."""
        return data_portal_api_helpers.api_object_table(self)

    def _api_astrometrics_find_object(self) -> Any:
        """Find an object in the astrometrics catalogue."""
        return astrometrics_api_helpers.api_astrometrics_find_object(self)

    def _api_astrometrics_resolve_by_name(self) -> Any:
        """Resolve an object name against the local astrometrics catalogue."""
        return astrometrics_api_helpers.api_astrometrics_resolve_by_name(
            self
        )

    def _api_astrometrics_resolve_by_coords(self) -> Any:
        """Resolve catalogue entries near supplied coordinates."""
        return astrometrics_api_helpers.api_astrometrics_resolve_by_coords(
            self
        )

    def _api_astrometrics_resolve_by_filter(self) -> Any:
        """Resolve catalogue entries using the submitted filter."""
        return astrometrics_api_helpers.api_astrometrics_resolve_by_filter(
            self
        )

    def _api_astrometrics_columns(self) -> Any:
        """List columns available in the astrometrics catalogue."""
        return astrometrics_api_helpers.api_astrometrics_columns(self)

    def _api_astrometrics_list_all(self) -> Any:
        """List astrometrics catalogue entries."""
        return astrometrics_api_helpers.api_astrometrics_list_all(self)

    def _api_astrometrics_list_rejected(self) -> Any:
        """List entries currently rejected from astrometrics."""
        return (astrometrics_api_helpers
                .api_astrometrics_list_rejected(self))

    def _api_astrometrics_add_rejected(self) -> Any:
        """Add an entry to the astrometrics rejection list."""
        return (astrometrics_api_helpers
                .api_astrometrics_add_rejected(self))

    def _api_astrometrics_update_rejected(self) -> Any:
        """Update a rejected astrometrics entry."""
        return (astrometrics_api_helpers
                .api_astrometrics_update_rejected(self))

    def _api_astrometrics_delete_rejected(self) -> Any:
        """Remove an entry from the astrometrics rejection list."""
        return (astrometrics_api_helpers
                .api_astrometrics_delete_rejected(self))

    def _api_astrometrics_add_manual(self) -> Any:
        """Add a manually supplied entry to astrometrics."""
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

    def _api_astrometrics_recompute_manual(self) -> Any:
        """Recompute derived data for manually maintained entries."""
        return (astrometrics_api_helpers
                .api_astrometrics_recompute_manual(self))

    def _api_astrometrics_lock_acquire(self) -> Any:
        """Acquire the astrometrics editing lock."""
        return (astrometrics_api_helpers
                .api_astrometrics_lock_acquire(self))

    def _api_astrometrics_lock_heartbeat(self) -> Any:
        """Refresh the current astrometrics editing lock."""
        return (astrometrics_api_helpers
                .api_astrometrics_lock_heartbeat(self))

    def _api_astrometrics_lock_release(self) -> Any:
        """Release the current astrometrics editing lock."""
        return (astrometrics_api_helpers
                .api_astrometrics_lock_release(self))

    def _api_astrometrics_update_field(self) -> Any:
        """Update a field on an astrometrics entry."""
        return astrometrics_api_helpers.api_astrometrics_update_field(
            self
        )

    def _api_astrometrics_upload_yaml(self) -> Any:
        """Upload astrometrics entries from a YAML document."""
        return astrometrics_api_helpers.api_astrometrics_upload_yaml(
            self
        )

    def _api_astrometrics_status(self) -> Any:
        """Return astrometrics catalogue status information."""
        return astrometrics_api_helpers.api_astrometrics_status(self)

    def _api_astrometrics_verify(self) -> Any:
        """Run verification checks on astrometrics data."""
        return astrometrics_api_helpers.api_astrometrics_verify(self)

    def _api_astrometrics_sed(self) -> Any:
        """Return spectral-energy-distribution data for an object."""
        return astrometrics_api_helpers.api_astrometrics_sed(self)

    def _api_astrometrics_hr(self) -> Any:
        """Return Hertzsprung-Russell diagram data for an object."""
        return astrometrics_api_helpers.api_astrometrics_hr(self)

    def _api_astrometrics_resolve_online_by_name(self) -> Any:
        """Resolve an object name using the configured online service."""
        return (
            astrometrics_api_helpers
            .api_astrometrics_resolve_online_by_name(self))

    def _api_astrometrics_resolve_online_by_coords(self) -> Any:
        """Resolve coordinates using the configured online service."""
        return (
            astrometrics_api_helpers
            .api_astrometrics_resolve_online_by_coords(self))

    # ----- astrometrics edit history -----
    def _api_astrometrics_history_list(self) -> Any:
        """List saved astrometrics edit-history entries."""
        return astrometrics_history.api_astrometrics_history_list(
            self)

    def _api_astrometrics_history_get(self) -> Any:
        """Retrieve one astrometrics edit-history entry."""
        return astrometrics_history.api_astrometrics_history_get(
            self)

    def _api_astrometrics_history_delete(self) -> Any:
        """Delete one astrometrics edit-history entry."""
        return astrometrics_history.api_astrometrics_history_delete(
            self)

    def _api_astrometrics_history_clear(self) -> Any:
        """Clear astrometrics edit history."""
        return astrometrics_history.api_astrometrics_history_clear(
            self)

    def _api_rejection_list_list(self) -> Any:
        """List entries in the rejection list."""
        return rejection_list_api_helpers.api_rejection_list_list(
            self
        )

    def _api_rejection_list_add(self) -> Any:
        """Add an entry to the rejection list."""
        return rejection_list_api_helpers.api_rejection_list_add(
            self
        )

    def _api_rejection_list_update(self) -> Any:
        """Update an entry in the rejection list."""
        return rejection_list_api_helpers.api_rejection_list_update(
            self
        )

    def _api_rejection_list_delete(self) -> Any:
        """Delete an entry from the rejection list."""
        return rejection_list_api_helpers.api_rejection_list_delete(
            self
        )

    def _api_rejection_list_upload(self) -> Any:
        """Upload entries to the rejection list."""
        return rejection_list_api_helpers.api_rejection_list_upload(
            self
        )

    def _api_rejection_history_list(self) -> Any:
        """List rejection-list history entries."""
        return rejection_list_api_helpers.api_rejection_history_list(
            self
        )

    def _api_rejection_history_get(self) -> Any:
        """Retrieve a rejection-list history entry."""
        return rejection_list_api_helpers.api_rejection_history_get(
            self
        )

    def _api_rejection_history_restore(self) -> Any:
        """Restore a rejection-list state from history."""
        return rejection_list_api_helpers.api_rejection_history_restore(
            self
        )

    def _api_rejection_history_resolve(self) -> Any:
        """Resolve a pending rejection-list history change."""
        return rejection_list_api_helpers.api_rejection_history_resolve(
            self
        )

    def _api_rejection_history_delete(self) -> Any:
        """Delete a rejection-list history entry."""
        return rejection_list_api_helpers.api_rejection_history_delete(
            self
        )

    def _api_rejection_history_clear(self) -> Any:
        """Clear rejection-list history."""
        return rejection_list_api_helpers.api_rejection_history_clear(
            self
        )

    # -----------------------------------------------------------------
    # Issues subsystem
    # -----------------------------------------------------------------

    def _api_issues_list(self) -> Any:
        """List issues visible to the current user."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_list(self)

    def _api_issues_create(self) -> Any:
        """Create an issue from the current request."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_create(self)

    def _api_issues_update(self) -> Any:
        """Update an existing issue from the current request."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_update(self)

    def _api_issues_users(self) -> Any:
        """List users available for issue assignment."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_users(self)

    def _api_issues_delete(self) -> Any:
        """Delete an issue selected by the request."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_delete(self)

    def _api_issues_edit(self) -> Any:
        """Render or process the issue-editing response."""
        from apero_ri.application import issues_api_helpers as ih
        return ih.api_issues_edit(self)

    def _api_known_errors_list(self) -> Any:
        """List known errors available to the current user."""
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_list(self)

    def _api_known_errors_create(self) -> Any:
        """Create a known-error entry from the current request."""
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_create(self)

    def _api_known_errors_update(self) -> Any:
        """Update a known-error entry from the current request."""
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_update(self)

    def _api_known_errors_delete(self) -> Any:
        """Delete a known-error entry selected by the request."""
        from apero_ri.application import known_errors_api_helpers as keh
        return keh.api_known_errors_delete(self)

    # -----------------------------------------------------------------
    # Monitor schedule subsystem
    # -----------------------------------------------------------------

    def _api_schedule_meta(self) -> Any:
        """Return metadata used by the monitor schedule interface."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_meta(self)

    def _api_schedule_entries_list(self) -> Any:
        """List schedule entries selected by the request filters."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_list(self)

    def _api_schedule_entries_add(self) -> Any:
        """Add a schedule entry from the current request."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_add(self)

    def _api_schedule_entries_edit(self) -> Any:
        """Edit a schedule entry from the current request."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_edit(self)

    def _api_schedule_entries_delete(self) -> Any:
        """Delete a schedule entry selected by the request."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_delete(self)

    def _api_schedule_link_user_calendar(self) -> Any:
        """Link the current user's calendar to the monitor schedule."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_link_user_calendar(self)

    def _api_schedule_tasks_upsert(self) -> Any:
        """Create or update a task in the monitor schedule."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_upsert(self)

    def _api_schedule_tasks_rename(self) -> Any:
        """Rename a monitor schedule task."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_rename(self)

    def _api_schedule_tasks_set_active(self) -> Any:
        """Set whether a monitor schedule task is active."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_tasks_set_active(self)

    def _api_schedule_calendar_week(self) -> Any:
        """Return schedule calendar data for one week."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_week(self)

    def _api_schedule_calendar_month(self) -> Any:
        """Return schedule calendar data for one month."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_month(self)

    def _api_schedule_calendar_weeks(self) -> Any:
        """Return schedule calendar data grouped by week."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_calendar_weeks(self)

    def _api_schedule_stats(self) -> Any:
        """Return monitor schedule statistics."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_stats(self)

    def _api_schedule_stats_visibility_set(self) -> Any:
        """Update visibility settings for schedule statistics."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_stats_visibility_set(self)

    def _api_schedule_instrument_setting_set(self) -> Any:
        """Update an instrument-specific schedule setting."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_instrument_setting_set(self)

    def _api_schedule_entries_bulk_add(self) -> Any:
        """Add multiple schedule entries from one request."""
        from apero_ri.application import schedule_api_helpers as sh
        return sh.api_schedule_entries_bulk_add(self)

    # -----------------------------------------------------------------
    # Notifications + messaging subsystem
    # -----------------------------------------------------------------
    def _api_notifications_list(self) -> Any:
        """List notifications for the current user."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_list(self)

    def _api_notifications_unread_count(self) -> Any:
        """Return the current user's unread notification count."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_unread_count(self)

    def _api_notifications_mark_read(self) -> Any:
        """Mark selected notifications as read."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_mark_read(self)

    def _api_notifications_dismiss(self) -> Any:
        """Dismiss selected notifications for the current user."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notifications_dismiss(self)

    def _api_notification_prefs_get(self) -> Any:
        """Return notification preferences for the current user."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notification_prefs_get(self)

    def _api_notification_prefs_save(self) -> Any:
        """Save notification preferences from the current request."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_notification_prefs_save(self)

    def _api_messages_list(self) -> Any:
        """List messages available to the current user."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_list(self)

    def _api_messages_send(self) -> Any:
        """Send a message using the current request data."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_send(self)

    def _api_messages_get(self, mid: Any) -> Any:
        """Return a message selected by its route identifier."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_get(self, mid)

    def _api_messages_delete(self, mid: Any) -> Any:
        """Delete a message selected by its route identifier."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_delete(self, mid)

    def _api_messages_mark_unread(self, mid: Any) -> Any:
        """Mark a message unread by its route identifier."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_mark_unread(self, mid)

    def _api_messages_mark_all_read(self) -> Any:
        """Mark all messages for the current user as read."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_mark_all_read(self)

    def _api_messages_delete_all(self) -> Any:
        """Delete all messages for the current user."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_delete_all(self)

    def _api_messages_flag_as_issue(self, mid: Any) -> Any:
        """Flag a message as an issue using its route identifier."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_messages_flag_as_issue(self, mid)

    def _api_users_directory(self) -> Any:
        """List users available in the user directory."""
        from apero_ri.application import notifications_api_helpers as nh
        return nh.api_users_directory(self)

    def _user_portal_users_view(self) -> Any:
        """Render the user portal's user directory."""
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_users_view(self)

    def _user_portal_user_card_view(self, username: str) -> Any:
        """Render a user card selected by username."""
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_user_card_view(self, username)

    def _user_portal_messages_view(self) -> Any:
        """Render the current user's message page."""
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_messages_view(self)

    def _user_portal_notifications_view(self) -> Any:
        """Render the current user's notification page."""
        from apero_ri.application import user_portal_view_helpers as uvh
        return uvh.user_portal_notifications_view(self)

    def _become_monitor_view(self) -> Any:
        """Switch the current session to its monitor view."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.become_monitor_view(self)

    def _monitor_portal_index_view(self) -> Any:
        """Render the monitor portal index."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_portal_index_view(self)

    def _monitor_issues_view(self) -> Any:
        """Render the monitor issues page."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_issues_view(self)

    def _monitor_known_errors_view(self) -> Any:
        """Render the monitor known-errors page."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_known_errors_view(self)

    def _monitor_status_view(self) -> Any:
        """Render the monitor service-status page."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_view(self)

    def _monitor_status_alliance_view(self) -> Any:
        """Render service status for the Alliance environment."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_alliance_view(self)

    def _monitor_status_canfar_view(self) -> Any:
        """Render service status for the CANFAR environment."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_status_canfar_view(self)

    def _monitor_schedule_view(self) -> Any:
        """Render the monitor schedule page."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_schedule_view(self)

    def _monitor_awards_view(self) -> Any:
        """Render the monitor awards page."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_awards_view(self)

    def _monitor_processing_logs_view(self) -> Any:
        """Render the processing-log browser."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_view(self)

    def _monitor_processing_logs_profile_view(
        self, profile_id: str
    ) -> Any:
        """Render processing logs filtered to one profile."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_profile_view(
            self, profile_id
        )

    def _monitor_processing_logs_pid_view(
        self, profile_id: str, pid: Any
    ) -> Any:
        """Render processing logs for one process in a profile."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_processing_logs_pid_view(
            self, profile_id, pid
        )

    def _monitor_apero_checks_view(self) -> Any:
        """Render the APERO checks dashboard."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_view(self)

    def _monitor_apero_checks_profile_view(
        self, profile_id: str
    ) -> Any:
        """Render APERO checks for one profile."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_profile_view(self, profile_id)

    def _monitor_apero_checks_obsdir_view(
        self, profile_id: str, obsdir: str
    ) -> Any:
        """Render APERO checks for one observation directory."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_obsdir_view(
            self, profile_id, obsdir
        )

    def _monitor_apero_checks_check_view(
        self,
        profile_id: str,
        obsdir: str,
        check_key: str,
    ) -> Any:
        """Render the selected check result for an observation directory."""
        from apero_ri.application import monitor_view_helpers as mvh
        args = [self, profile_id, obsdir, check_key]
        return mvh.monitor_apero_checks_check_view(*args)

    def _monitor_apero_checks_queue_view(
        self, profile_id: str
    ) -> Any:
        """Render the APERO checks queue for one profile."""
        from apero_ri.application import monitor_view_helpers as mvh
        return mvh.monitor_apero_checks_queue_view(self, profile_id)

    def _monitor_apero_checks_stats_view(
        self, profile_id: str
    ) -> Any:
        """Render APERO checks statistics for one profile."""
        from apero_ri.application import (
            apero_checks_stats_helpers as acsh,
        )
        return acsh.monitor_apero_checks_stats_view(
            self, profile_id
        )

    def _api_apero_checks_stats(self, profile_id: str) -> Any:
        """Return APERO checks statistics for one profile."""
        from apero_ri.application import (
            apero_checks_stats_helpers as acsh,
        )
        return acsh.api_apero_checks_stats(self, profile_id)

    def _api_processing_logs(self) -> Any:
        """Return processing-log entries selected by the request."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs(self)

    def _api_processing_logs_pid(self) -> Any:
        """Return processing-log entries filtered by process ID."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_pid(self)

    def _api_processing_log_file(self) -> Any:
        """Return the requested processing-log file response."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_log_file(self)

    def _api_processing_logs_fail_report(self) -> Any:
        """Return a processing-log failure report."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_fail_report(self)

    def _api_processing_logs_fail_report_info(self) -> Any:
        """Return metadata for a processing-log failure report."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_fail_report_info(self)

    def _api_processing_logs_report_download(self, token: str) -> Any:
        """Download a generated failure report using its token."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_report_download(self, token)

    def _api_processing_logs_filters_list(self) -> Any:
        """List saved processing-log filters."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_list(self)

    def _api_processing_logs_filters_save(self) -> Any:
        """Save processing-log filters from the current request."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_save(self)

    def _api_processing_logs_filters_delete(self) -> Any:
        """Delete a saved processing-log filter."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_filters_delete(self)

    def _api_processing_logs_pid_export(self) -> Any:
        """Export processing logs selected by process ID."""
        from apero_ri.application import (
            processing_logs_api_helpers as plh,
        )
        return plh.api_processing_logs_pid_export(self)

    def _api_apero_checks_update_failure(self) -> Any:
        """Update a recorded APERO check failure."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_update_failure(self)

    def _api_apero_checks_create_issue(self) -> Any:
        """Create an issue from an APERO check result."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_create_issue(self)

    def _api_apero_checks_config_save(self) -> Any:
        """Save APERO checks configuration from the request."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_config_save(self)

    def _api_apero_checks_browse_dirs(self) -> Any:
        """Browse directories available to APERO checks."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_browse_dirs(self)

    def _api_apero_checks_profile_page(self, profile_id: str) -> Any:
        """Return APERO checks page data for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_profile_page(self, profile_id)

    def _api_apero_checks_list_obsdirs(self, profile_id: str) -> Any:
        """List observation directories checked for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_list_obsdirs(self, profile_id)

    def _api_apero_checks_policy_sections(self) -> Any:
        """List sections in the APERO checks policy."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_policy_sections(self)

    def _api_apero_checks_view_yaml(self) -> Any:
        """Return the requested APERO checks YAML content."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_view_yaml(self)

    def _api_apero_checks_validate_obsdir(self) -> Any:
        """Validate an observation directory for APERO checks."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_validate_obsdir(self)

    def _api_apero_checks_rerun_night(self) -> Any:
        """Queue APERO checks to rerun for a night."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_rerun_night(self)

    def _api_apero_checks_rerun_single_check(self) -> Any:
        """Queue a single APERO check to rerun."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_rerun_single_check(self)

    def _api_apero_checks_advanced_run(self) -> Any:
        """Queue an advanced APERO checks run."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_advanced_run(self)

    def _api_apero_checks_clean_reset_profile(self) -> Any:
        """Clean and reset APERO checks data for a profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_clean_reset_profile(self)

    def _api_apero_checks_delete_obsdir(self) -> Any:
        """Delete stored APERO checks data for an observation directory."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_delete_obsdir(self)

    def _api_apero_checks_exclude_obsdir(self) -> Any:
        """Exclude an observation directory from APERO checks."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_exclude_obsdir(self)

    def _api_apero_checks_list_excluded_obsdirs(self) -> Any:
        """List observation directories excluded from APERO checks."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_list_excluded_obsdirs(self)

    def _api_apero_checks_remove_excluded_obsdir(self) -> Any:
        """Remove an observation-directory exclusion."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_remove_excluded_obsdir(self)

    def _api_apero_checks_delete_test_from_yamls(self) -> Any:
        """Remove a test definition from APERO checks YAML files."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_delete_test_from_yamls(self)

    def _api_apero_checks_queue_status(self, profile_id: str) -> Any:
        """Return queued APERO checks tasks for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_status(self, profile_id)

    def _api_apero_checks_queue_cancel_task(
        self, profile_id: str
    ) -> Any:
        """Cancel a queued APERO checks task for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_cancel_task(self, profile_id)

    def _api_apero_checks_queue_kill_profile(
        self, profile_id: str
    ) -> Any:
        """Stop APERO checks tasks running for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_kill_profile(self, profile_id)

    def _api_apero_checks_queue_clear_history(
        self, profile_id: str
    ) -> Any:
        """Clear APERO checks queue history for one profile."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_queue_clear_history(self, profile_id)

    def _api_apero_checks_check_results(self) -> Any:
        """Return results for the selected APERO check."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_check_results(self)

    def _api_apero_checks_check_info_async(self) -> Any:
        """Return asynchronously collected information for a check."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_check_info_async(self)

    def _api_apero_checks_policy_build_status(self) -> Any:
        """Return the status of an APERO checks policy build."""
        from apero_ri.application import (
            apero_checks_api_helpers as ach,
        )
        return ach.api_apero_checks_policy_build_status(self)


        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_obs_table_view(self, **kwargs)

    def _ri_object_page_view(
        self, profile_id: str, objname: str
    ) -> Any:
        """Render an object's page within a selected profile."""
        kwargs = dict(profile_id=profile_id, objname=objname)
        return data_portal_view_helpers.ri_object_page_view(self, **kwargs)

    def _api_object_page(self) -> Any:
        """Return object-page data selected by the current request."""
        return data_portal_api_helpers.api_object_page(self)

    def _api_object_rejection_issue(self) -> Any:
        """Create or update an issue for an object rejection."""
        return data_portal_api_helpers.api_object_rejection_issue(self)

    @staticmethod
    def _rid_cache_tag(accessible_run_ids: Any) -> str:
        """Return a short hash of the accessible run_id set for cache keys."""
        import hashlib

        blob = "|".join(sorted(accessible_run_ids)).encode()
        return hashlib.md5(blob).hexdigest()[:8]

    @staticmethod
    def _filter_plot_rows(
        htable_rows: Any,
        ftable_dict: Any,
        accessible_run_ids: Any,
    ) -> Any:
        """Filter plot rows to the run IDs visible to the current user."""
        args = [htable_rows, ftable_dict, accessible_run_ids]
        return _impls.ariapp_filter_plot_rows(*args)

    def _api_object_plots(self) -> Any:
        """Return plots available for the selected object."""
        return data_portal_api_helpers.api_object_plots(self)

    def _api_object_download(self) -> Any:
        """Return the requested object download response."""
        return object_download_helpers.api_object_download(self)

    def _api_object_lbl_plots(self) -> Any:
        """Return line-by-line plots for the selected object."""
        return data_portal_api_helpers.api_object_lbl_plots(self)

    def _api_filename_plot(self) -> Any:
        """Return a plot associated with a requested filename."""
        return data_portal_api_helpers.api_filename_plot(self)

    def _ri_object_plot_max_view(
        self, profile_id: str, objname: str, plot_key: str
    ) -> Any:
        """Render one object plot at its expanded display size."""
        kwargs = dict(profile_id=profile_id, objname=objname,
                      plot_key=plot_key)
        return data_portal_view_helpers.ri_object_plot_max_view(self, **kwargs)

    # -----------------------------------------------------------------
    # Finder chart helpers
    # -----------------------------------------------------------------

    def _api_finder_chart(self) -> Any:
        """Return a finder chart for the requested object."""
        return data_portal_api_helpers.api_finder_chart(self)

    def _api_finder_chart_stream(self) -> Any:
        """Stream a generated finder chart response."""
        return (
            data_portal_api_helpers
            .api_finder_chart_stream(self)
        )

    def _api_tess_rotation(self) -> Any:
        """Return TESS rotation information for the requested object."""
        return data_portal_api_helpers.api_tess_rotation(
            self
        )

    def _api_tess_rotation_lc(self) -> Any:
        """Return TESS light-curve data for rotation analysis."""
        return data_portal_api_helpers.api_tess_rotation_lc(
            self
        )

    def _api_tess_rotation_stream(self) -> Any:
        """Stream TESS rotation-analysis data."""
        return (
            data_portal_api_helpers
            .api_tess_rotation_stream(self)
        )

    def _api_tess_rotation_data(self) -> Any:
        """Return the available TESS rotation-analysis data."""
        return (
            data_portal_api_helpers
            .api_tess_rotation_data(self)
        )

    def _api_debug_plots(self) -> Any:
        """Return debug plots for the selected object or exposure."""
        return data_portal_api_helpers.api_debug_plots(self)

    def _api_tcorr_map_generate(self) -> Any:
        """Generate and return a telluric-correction map."""
        return data_portal_api_helpers.api_tcorr_map_generate(self)

    def _build_finder_max_payload(
        self,
        profile: Any,
        objname: str,
        obj_props: Any,
        preset: Any,
        band_idx: Any,
    ) -> Any:
        """Build the expanded finder-chart payload for a selected band."""
        args = [profile, objname, obj_props, preset, band_idx]
        return _impls.ariapp_build_finder_max_payload(self, *args)

    # -----------------------------------------------------------------
    # Download basket helpers
    # -----------------------------------------------------------------

    def _basket_access_check(self) -> Any:
        """Check whether the current request can access the download basket."""
        return _impls.ariapp_basket_access_check(self)

    def _build_profile_cfgs(self, user_info: Any) -> dict:
        """
        Return {profile_id: profile_data} for all user-accessible profiles.
        Used to resolve file paths during basket compilation.
        """
        accessible = auth.get_accessible_profiles(user_info, self.ari_groups)
        return {p["profile_id"]: p.get("data", {}) for p in accessible}

    def _all_accessible_run_ids(self, user_info: Any) -> set:
        """Collect run IDs accessible through the user's profiles."""
        return _impls.ariapp_all_accessible_run_ids(self, user_info)

    # -----------------------------------------------------------------
    # Basket: page view
    # -----------------------------------------------------------------

    def _ri_basket_view(self, profile_id: str) -> Any:
        """Render the download basket for one profile."""
        return data_portal_view_helpers.ri_basket_view(self, profile_id)

    # -----------------------------------------------------------------
    # Basket: API – get basket contents
    # -----------------------------------------------------------------

    def _api_basket_get(self) -> Any:
        """Return the current user's download basket."""
        return _impls.ariapp_api_basket_get(self)

    # -----------------------------------------------------------------
    # Basket: API – summary (file counts + sizes)
    # -----------------------------------------------------------------

    def _api_basket_summary(self) -> Any:
        """Return counts and sizes for the current download basket."""
        return _impls.ariapp_api_basket_summary(self)

    # -----------------------------------------------------------------
    # Basket: API – add entries
    # -----------------------------------------------------------------

    def _api_basket_add(self) -> Any:
        """Add requested files to the download basket."""
        return _impls.ariapp_api_basket_add(self)

    # -----------------------------------------------------------------
    # Basket: API – remove entries
    # -----------------------------------------------------------------

    def _api_basket_remove(self) -> Any:
        """Remove requested files from the download basket."""
        return _impls.ariapp_api_basket_remove(self)

    # -----------------------------------------------------------------
    # Basket: API – clear
    # -----------------------------------------------------------------

    def _api_basket_clear(self) -> Any:
        """Remove all entries from the download basket."""
        return _impls.ariapp_api_basket_clear(self)

    # -----------------------------------------------------------------
    # Basket: API – compile download
    # -----------------------------------------------------------------

    def _api_basket_compile(self) -> Any:
        """Start compiling the current basket into a download."""
        return basket_api_helpers.api_basket_compile(self)

    # -----------------------------------------------------------------
    # Basket: API – compilation status
    # -----------------------------------------------------------------

    def _api_basket_compile_status(self, job_id: str) -> Any:
        """Return the status of a basket-compilation job."""
        return _impls.ariapp_api_basket_compile_status(self, job_id)

    # -----------------------------------------------------------------
    # Basket: API – download compiled file
    # -----------------------------------------------------------------

    def _api_basket_download(
        self, job_id: str, chunk_idx: Any
    ) -> Any:
        """Download one chunk from a compiled basket job."""
        return _impls.ariapp_api_basket_download(self, job_id, chunk_idx)

    # -----------------------------------------------------------------
    # Basket: API – recent jobs
    # -----------------------------------------------------------------

    def _api_basket_jobs(self) -> Any:
        """List recent basket-compilation jobs for the current user."""
        return _impls.ariapp_api_basket_jobs(self)

    def _api_basket_jobs_extend(self) -> Any:
        """Extend the expiry of a basket-compilation job."""
        return _impls.ariapp_api_basket_jobs_extend(self)

    def _api_basket_jobs_expiry(self) -> Any:
        """Return expiry information for basket-compilation jobs."""
        return _impls.ariapp_api_basket_jobs_expiry(self)

    def _api_basket_jobs_remove(self) -> Any:
        """Remove a basket-compilation job from the user's job list."""
        return _impls.ariapp_api_basket_jobs_remove(self)

    def _api_basket_jobs_clear(self) -> Any:
        """Clear the current user's basket-compilation job list."""
        return _impls.ariapp_api_basket_jobs_clear(self)

    # -----------------------------------------------------------------
    # Basket: API – create/retrieve share token for a completed job
    # -----------------------------------------------------------------

    def _api_basket_share_token(self) -> Any:
        """Create or retrieve a token for sharing a completed basket job."""
        return _impls.ariapp_api_basket_share_token(self)

    # -----------------------------------------------------------------
    # Basket: API – send share email
    # -----------------------------------------------------------------

    def _api_basket_share_email(self) -> Any:
        """Email a link to a shared basket download."""
        return basket_api_helpers.api_basket_share_email(self)

    # -----------------------------------------------------------------
    # Basket: Public share landing page (no login required)
    # -----------------------------------------------------------------

    def _share_landing(self, token: str) -> Any:
        """Render the public landing page for a shared basket download."""
        return _impls.ariapp_share_landing(self, token)

    # -----------------------------------------------------------------
    # Basket: Public share chunk download (no login required)
    # -----------------------------------------------------------------

    def _share_download(self, token: str, chunk_idx: Any) -> Any:
        """Download a chunk through a public basket share token."""
        return _impls.ariapp_share_download(self, token, chunk_idx)

    # -----------------------------------------------------------------
    # Basket: API – add from ftable by obs_dir + fkind
    # -----------------------------------------------------------------

    def _api_basket_add_from_ftable(self) -> Any:
        """Add files selected from an observation table to the basket."""
        return basket_api_helpers.api_basket_add_from_ftable(self)

    # -----------------------------------------------------------------
    # File browser API
    # -----------------------------------------------------------------

    def _api_file_browser(self) -> Any:
        """Browse files available through the selected profile."""
        return query_db_api_helpers.api_file_browser(self)

    def _api_file_header(self) -> Any:
        """Return the header of a selected file."""
        return query_db_api_helpers.api_file_header(self)

    def _api_file_header_download(self) -> Any:
        """Download the header of a selected file."""
        return query_db_api_helpers.api_file_header_download(self)

    def _api_obs_table(self) -> Any:
        """Return observation-table data selected by the request."""
        return data_portal_api_helpers.api_obs_table(self)

    # -----------------------------------------------------------------
    # Data portal — database query explorer
    # -----------------------------------------------------------------
    def _get_user_table_access(
        self, user_info: Any, profile: Any
    ) -> Any:
        """Resolve database tables available to a user for a profile."""
        args = (user_info, profile)
        return query_db_api_helpers.get_user_table_access(self, *args)

    def _execute_db_query(
        self, profile_cfg: Any, query: str, query_params: Any = None
    ) -> Any:
        """Execute a database query using profile connection settings."""
        args = (profile_cfg, query, query_params)
        return _impls.ariapp_execute_db_query(self, *args)

    @staticmethod
    def _build_safe_select_query(
        table_access: Any, query_spec: Any, run_ids: Any
    ) -> Any:
        """Build a guarded SELECT query for accessible run IDs."""
        args = [table_access, query_spec, run_ids]
        return _impls.ariapp_build_safe_select_query(*args)

    @staticmethod
    def _build_safe_count_query(
        table_access: Any, query_spec: Any, run_ids: Any
    ) -> Any:
        """Build a guarded row-count query for accessible run IDs."""
        args = [table_access, query_spec, run_ids]
        return _impls.ariapp_build_safe_count_query(*args)

    def _api_query_db_count(self) -> Any:
        """Return a count for the selected database query."""
        return query_db_api_helpers.api_query_db_count(self)

    def _ri_query_db_view(self, profile_id: str) -> Any:
        """Render the database query explorer for one profile."""
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_query_db_view(self, **kwargs)

    def _ri_qc_graphs_view(self, profile_id: str) -> Any:
        """Render QC graphs for one profile."""
        kwargs = dict(profile_id=profile_id)
        return data_portal_view_helpers.ri_qc_graphs_view(self, **kwargs)

    def _ri_qc_graphs_max_view(
        self,
        profile_id: str,
        section: str,
        metric_key: str,
        view_key: str,
    ) -> Any:
        """Render one QC graph at its expanded display size."""
        args = (profile_id, section, metric_key, view_key)
        return _impls.ariapp_ri_qc_graphs_max_view(self, *args)

    def _load_query_db_presets(self, profile: Any) -> Any:
        """Load saved query presets for a profile."""
        args = [profile,  PACKAGE_DIR, self._db_access_table_keys(),
                self._profile_get_db]
        return query_helpers.load_query_db_presets(*args)

    @staticmethod
    def _parse_text_presets(text: str, replace_fn: Any) -> Any:
        """Parse text-form query presets with a token replacement helper."""
        return _impls.ariapp_parse_text_presets(text, replace_fn)

    def _api_query_db_schema(self) -> Any:
        """Return the queryable database schema for the selected profile."""
        return query_db_api_helpers.api_query_db_schema(self)

    def _api_query_db_run(self) -> Any:
        """Run the database query submitted in the current request."""
        return query_db_api_helpers.api_query_db_run(self)

    # -----------------------------------------------------------------
    # Admin user management API
    # -----------------------------------------------------------------
    def _require_admin_user(self) -> Any:
        """Check whether the current user can access user administration."""
        return _impls.ariapp_require_admin_user(self)

    def _api_user_search(self) -> Any:
        """Search users using the current request filters."""
        return admin_user_api_helpers.api_user_search(self)

    def _api_user_update_groups(self) -> Any:
        """Update group membership for the selected user."""
        return admin_user_api_helpers.api_user_update_groups(self)

    def _api_user_update_instruments(self) -> Any:
        """Update instrument access for the selected user."""
        return admin_user_api_helpers.api_user_update_instruments(self)

    def _api_user_delete(self) -> Any:
        """Delete the user selected by the current request."""
        return _impls.ariapp_api_user_delete(self)

    # -----------------------------------------------------------------
    # Admin login-as API
    # -----------------------------------------------------------------
    def _api_login_as_search(self) -> Any:
        """Search for a user to open through login-as."""
        return admin_user_api_helpers.api_login_as_search(self)

    def _api_login_as_set(self) -> Any:
        """Set the current session to act as a selected user."""
        return admin_user_api_helpers.api_login_as_set(self)

    @staticmethod
    def _api_login_as_clear() -> Any:
        """Clear the login-as session."""
        if "user" not in session:
            return jsonify(success=False, error="Not logged in"), 401
        session.pop("login_as", None)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Admin science groups API
    # -----------------------------------------------------------------
    def _require_sci_group_perm(self) -> Any:
        """Check whether the current user can manage science groups."""
        return _impls.ariapp_require_sci_group_perm(self)

    def _api_sci_groups_list(self) -> Any:
        """List science groups available to the current user."""
        return sci_groups_api_helpers.api_sci_groups_list(self)

    def _api_run_ids_list(self) -> Any:
        """List catalogued run IDs."""
        return run_ids_api_helpers.catalog_api(self)

    def _api_search_index(self) -> Any:
        """Search the configured object index."""
        return search_helpers.search_index(self)

    def _api_run_ids_save(self) -> Any:
        """Save run-ID catalog changes from the current request."""
        return run_ids_api_helpers.catalog_api(self, save=True)

    def _api_run_ids_import(self) -> Any:
        """Import run IDs into the catalog."""
        return run_ids_api_helpers.import_api(self)

    def _api_run_ids_export(self) -> Any:
        """Export the run-ID catalog."""
        return run_ids_api_helpers.export_api(self)

    def _api_sci_groups_get(self) -> Any:
        """Return science-group data selected by the current request."""
        return _impls.ariapp_api_sci_groups_get(self)

    def _api_sci_groups_refresh_run_ids(self) -> Any:
        """Refresh run-ID membership in science groups."""
        return _impls.ariapp_api_sci_groups_refresh_run_ids(self)

    def _api_sci_groups_save(self) -> Any:
        """Save changes to one science group."""
        return sci_groups_api_helpers.api_sci_groups_save(self)

    def _api_sci_groups_save_all(self) -> Any:
        """Save changes to all science groups."""
        return sci_groups_api_helpers.api_sci_groups_save_all(self)

    def _api_sci_groups_create(self) -> Any:
        """Create a science group from the current request."""
        return sci_groups_api_helpers.api_sci_groups_create(self)

    def _api_sci_groups_delete(self) -> Any:
        """Delete a science group selected by the current request."""
        return sci_groups_api_helpers.api_sci_groups_delete(self)

    def _api_sci_groups_export(self) -> Any:
        """Export science-group definitions."""
        return sci_groups_api_helpers.api_sci_groups_export(self)

    def _api_sci_groups_import(self) -> Any:
        """Import science-group definitions."""
        return sci_groups_api_helpers.api_sci_groups_import(self)

    def _api_sci_groups_io_export(self) -> Any:
        """Export science groups in the I/O interchange format."""
        return sci_groups_api_helpers.api_sci_groups_io_export(self)

    def _api_sci_groups_io_import(self) -> Any:
        """Import science groups from the I/O interchange format."""
        return sci_groups_api_helpers.api_sci_groups_io_import(self)

    # -----------------------------------------------------------------
    # APERO profiles API
    # -----------------------------------------------------------------
    def _require_apero_profile_perm(self) -> Any:
        """Check whether the current user can manage APERO profiles."""
        return _impls.ariapp_require_apero_profile_perm(self)

    def _require_user_db_access_perm(self) -> Any:
        """Check whether the current user can manage database access."""
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

    def _editable_groups_for_editor(
        self, user_info: Any, perms: Any
    ) -> Any:
        """Return groups the current editor is allowed to modify."""
        return _impls.ariapp_editable_groups_for_editor(self, user_info, perms)

    def _find_accessible_profile(
        self,
        user_info: Any,
        profile_id: str,
        instrument: str = '',
    ) -> Optional[dict]:
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
        """Build database connection parameters from a profile config."""
        return apero_profiles_api_helpers.profile_db_params(self, profile_cfg)

    def _resolve_db_payload_for_test(self, data: dict) -> dict:
        """Resolve submitted database fields for a connection test."""
        return (
            apero_profiles_api_helpers.resolve_db_payload_for_test(
                self, data
            )
        )

    def _resolve_profile_db_test_target(
        self,
        mode: str,
        host: str,
        port: str,
        username: str,
        password: str,
        db_name: str,
        use_ssh_tunnel: bool,
        ssh_config_host: str,
        ssh_local_port: str,
        ssh_remote_port: str,
    ) -> Any:
        """Resolve a submitted profile DB test target and tunnel settings."""
        args = (mode, host, port, username, password, db_name,
                use_ssh_tunnel, ssh_config_host, ssh_local_port,
                ssh_remote_port)
        return _impls.ariapp_resolve_profile_db_test_target(self, *args)

    def _validate_profile_database(self, profile_cfg: dict) -> dict:
        """Validate database settings in an APERO profile configuration."""
        return _impls.ariapp_validate_profile_database(self, profile_cfg)

    def _fetch_table_columns(
        self, profile_cfg: dict, table_name: str
    ) -> Any:
        """Fetch column metadata for a table in a profile database."""
        args = (profile_cfg, table_name)
        return apero_profiles_api_helpers.fetch_table_columns(self, *args)

    def _profile_db_access_health(self, entry: dict, table_names: list) -> str:
        """Summarize database access health for one profile entry."""
        return _impls.ariapp_profile_db_access_health(self, entry, table_names)

    def _build_user_db_access_health_report(self, user_info: dict) -> dict:
        """Build the database-access health report for a user."""
        return user_db_access_api_helpers.build_user_db_access_health_report(
            app=self,
            user_info=user_info,
        )

    def _api_user_db_access_profiles(self) -> Any:
        """List profiles for which the current user can request DB access."""
        return _impls.ariapp_api_user_db_access_profiles(self)

    def _api_user_db_access_details(self) -> Any:
        """Return database-access details for the current user."""
        return user_db_access_api_helpers.api_user_db_access_details(self)

    def _api_user_db_access_health_check(self) -> Any:
        """Check database access health for the current user."""
        return _impls.ariapp_api_user_db_access_health_check(self)

    def _api_user_db_access_save(self) -> Any:
        """Save database-access settings submitted by the current user."""
        return user_db_access_api_helpers.api_user_db_access_save(self)

    def _api_apero_profiles_list(self) -> Any:
        """List APERO profiles visible to the current user."""
        return apero_profiles_api_helpers.api_apero_profiles_list(self)

    def _api_apero_profiles_overview(self) -> Any:
        """Return status details for the APERO profiles overview."""
        return _impls.ariapp_api_apero_profiles_overview(self)

    def _api_apero_profiles_save(self) -> Any:
        """Save an APERO profile submitted by an administrator."""
        return apero_profiles_api_helpers.api_apero_profiles_save(
            self,
            package_dir=PACKAGE_DIR,
        )

    def _api_apero_profiles_save_temporary(self) -> Any:
        """Save a temporary APERO profile for testing."""
        return apero_profiles_api_helpers.api_apero_profiles_save_temporary(
            self,
            package_dir=PACKAGE_DIR,
        )

    def _api_apero_profiles_delete(self) -> Any:
        """Delete the APERO profile selected by the request."""
        return _impls.ariapp_api_apero_profiles_delete(self)

    def _api_apero_profiles_reorder(self) -> Any:
        """Reorder configured APERO profiles."""
        return _impls.ariapp_api_apero_profiles_reorder(self)

    def _api_apero_profiles_validate(self) -> Any:
        """Validate an APERO profile submitted by the request."""
        return _impls.ariapp_api_apero_profiles_validate(self)

    def _api_apero_profiles_browse(self) -> Any:
        """Browse paths while configuring an APERO profile."""
        return _impls.ariapp_api_apero_profiles_browse(self)

    def _api_apero_profiles_update_groups(self) -> Any:
        """Update groups associated with APERO profiles."""
        return _impls.ariapp_api_apero_profiles_update_groups(self)

    def _api_apero_profiles_toggle_disabled(self) -> Any:
        """Toggle whether an APERO profile is disabled."""
        return apero_profiles_api_helpers.api_apero_profiles_toggle_disabled(
            self
        )

    def _api_apero_profiles_test_db(self) -> Any:
        """Test a database connection configured for an APERO profile."""
        return _impls.ariapp_api_apero_profiles_test_db(self)

    def _api_apero_profiles_list_tables(self) -> Any:
        """List tables available through a configured APERO profile."""
        return apero_profiles_api_helpers.api_apero_profiles_list_tables(self)

    # -----------------------------------------------------------------
    # Interactive SSH tunnel for APERO profile DB connections
    # -----------------------------------------------------------------
    def _api_apero_profiles_ssh_tunnel_start(self) -> Any:
        """Start an interactive SSH tunnel for a profile database."""
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_start(self)

    def _api_apero_profiles_ssh_tunnel_poll(self) -> Any:
        """Poll an interactive profile SSH-tunnel session."""
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_poll(self)

    def _api_apero_profiles_ssh_tunnel_send(self) -> Any:
        """Send input to an interactive profile SSH-tunnel session."""
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_send(self)

    def _api_apero_profiles_ssh_tunnel_close(self) -> Any:
        """Close an interactive profile SSH-tunnel session."""
        return _impls.ariapp_api_apero_profiles_ssh_tunnel_close(self)

    def _api_db_ssh_tunnel_status(self) -> Any:
        """Return the status of configured database SSH tunnels."""
        return _impls.ariapp_api_db_ssh_tunnel_status(self)

    def _api_db_ssh_tunnel_ssh_hosts(self) -> Any:
        """List SSH config host aliases from ~/.ssh/config for dropdowns."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401

        return jsonify(success=True, hosts=self._list_ssh_config_hosts())

    def _api_db_ssh_tunnel_list(self) -> Any:
        """List saved database SSH-tunnel definitions."""
        return _impls.ariapp_api_db_ssh_tunnel_list(self)

    def _api_db_ssh_tunnel_save(self) -> Any:
        """Save a database SSH-tunnel definition."""
        return _impls.ariapp_api_db_ssh_tunnel_save(self)

    def _api_db_ssh_tunnel_delete(self) -> Any:
        """Delete a saved database SSH-tunnel definition."""
        return _impls.ariapp_api_db_ssh_tunnel_delete(self)

    def _api_db_ssh_tunnel_ensure(self) -> Any:
        """Ensure a database SSH tunnel is available."""
        return _impls.ariapp_api_db_ssh_tunnel_ensure(self)

    def _api_db_ssh_tunnel_close(self) -> Any:
        """Close a database SSH tunnel."""
        return db_tunnel_api_helpers.api_db_ssh_tunnel_close(self)

    def _api_db_ssh_tunnel_test(self) -> Any:
        """Test a database connection through its SSH tunnel."""
        return db_tunnel_api_helpers.api_db_ssh_tunnel_test(self)

    def _api_database_setup_local_db_list(self) -> Any:
        """List locally configured database connections."""
        return _impls.ariapp_api_database_setup_local_db_list(self)

    def _api_database_setup_local_db_save(self) -> Any:
        """Save local database connection settings."""
        return db_tunnel_api_helpers.api_database_setup_local_db_save(self)

    def _api_database_setup_local_db_delete(self) -> Any:
        """Delete a locally configured database connection."""
        return _impls.ariapp_api_database_setup_local_db_delete(self)

    def _api_database_setup_local_db_test(self) -> Any:
        """Test a locally configured database connection."""
        return _impls.ariapp_api_database_setup_local_db_test(self)

    def _api_apero_profiles_test_tables(self) -> Any:
        """Test profile database access to its configured tables."""
        return apero_profiles_api_helpers.api_apero_profiles_test_tables(self)

    # -----------------------------------------------------------------
    # Async tasks API
    # -----------------------------------------------------------------
    def _require_async_tasks_perm(self) -> Any:
        """Check whether the current user can manage async tasks."""
        return _impls.ariapp_require_async_tasks_perm(self)

    @staticmethod
    def _coerce_task_frequency(
        value: Any, default: float = 24.0
    ) -> float:
        """Normalize a task frequency value in hours."""
        return async_task_helpers.coerce_task_frequency(value, default)

    @staticmethod
    def _coerce_task_enabled(
        value: Any, default: bool = False
    ) -> bool:
        """Normalize a task enabled flag."""
        return async_task_helpers.coerce_task_enabled(value, default)

    @staticmethod
    def _is_global_scope(instrument: str) -> bool:
        """Return True if this task scope is the shared global scope."""
        return async_task_helpers.is_global_scope(instrument)

    def _task_keys_for_scope(self, instrument: str) -> list:
        """Return task keys allowed in a given scope from tasks.TYPE."""
        return async_task_helpers.task_keys_for_scope(instrument)

    def _merge_async_task_catalog(
        self, instrument: str, all_tasks: dict
    ) -> Any:
        """Merge persisted task overrides with the task catalog defaults."""
        
        kwargs = dict(instrument=instrument, all_tasks=all_tasks)
        merged, changed = async_task_helpers.merge_async_task_catalog(**kwargs)
        return merged, changed

    def _api_async_tasks_list(self) -> Any:
        """List async tasks visible in the current scope."""
        return async_tasks_api_helpers.api_async_tasks_list(self)

    def _api_async_tasks_global_list(self) -> Any:
        """List async tasks configured for the global scope."""
        return async_tasks_api_helpers.api_async_tasks_global_list(self)

    def _api_async_tasks_task_list(self) -> Any:
        """List tasks available in the selected instrument scope."""
        return async_tasks_api_helpers.api_async_tasks_task_list(self)

    def _api_async_tasks_save(self) -> Any:
        """Save async task settings from the current request."""
        return async_tasks_api_helpers.api_async_tasks_save(self)

    def _api_async_tasks_delete(self) -> Any:
        """Delete an async task selected by the request."""
        return _impls.ariapp_api_async_tasks_delete(self)

    def _api_async_tasks_reorder(self) -> Any:
        """Reorder async tasks in the selected scope."""
        return _impls.ariapp_api_async_tasks_reorder(self)

    def _api_async_tasks_toggle(self) -> Any:
        """Toggle an async task's enabled state."""
        return _impls.ariapp_api_async_tasks_toggle(self)

    def _api_async_tasks_run_now(self) -> Any:
        """Run the selected async task immediately."""
        return async_tasks_api_helpers.api_async_tasks_run_now(self)

    def _api_async_tasks_run_all(self) -> Any:
        """Run all enabled async tasks in the selected scope."""
        return async_tasks_api_helpers.api_async_tasks_run_all(self)

    def _api_async_tasks_stop(self) -> Any:
        """Stop queued tasks and apply cooldown before any next attempt."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        data = request.get_json(silent=True) or {}
        instrument = str(data.get("instrument", "") or "").strip() or None
        result = task_runner.stop_all_with_cooldown(instrument=instrument)
        return jsonify(success=True, **result)

    def _api_async_tasks_kill_all(self) -> Any:
        """Immediately interrupt running task and clear queue."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(
                success=False, error='Unauthorized'
            ), 401
        result = task_runner.kill_all()
        return jsonify(success=True, **result)

    def _api_async_tasks_cancel_task(self) -> Any:
        """Cancel the selected queued async task."""
        return _impls.ariapp_api_async_tasks_cancel_task(self)

    def _api_async_tasks_clear_history(self) -> Any:
        """Clear async-task execution history."""
        return _impls.ariapp_api_async_tasks_clear_history(self)

    def _api_async_tasks_status(self) -> Any:
        """Return async-task status for the current scope."""
        return async_tasks_api_helpers.api_async_tasks_status(self)

    def _api_async_tasks_task_log(self) -> Any:
        """Return log output for the selected async task."""
        return _impls.ariapp_api_async_tasks_task_log(self)

    def _validate_async_task_file_path(self, path: str) -> Any:
        """Validate a file path requested by an async task operation."""
        return _impls.ariapp_validate_async_task_file_path(self, path)

    def _api_async_tasks_read_file(self) -> Any:
        """Read a file produced by an async task."""
        return async_tasks_api_helpers.api_async_tasks_read_file(self)

    @staticmethod
    def _build_json_preview_table(
        data: Any, max_rows: int = 200
    ) -> dict:
        """Build a tabular preview from JSON-compatible data."""
        kwargs = dict(data=data, max_rows=max_rows)
        return async_tasks_api_helpers.build_json_preview_table(**kwargs)

    def _api_async_tasks_download_file(self) -> Any:
        """Download a file produced by an async task."""
        return _impls.ariapp_api_async_tasks_download_file(self)

    def _api_async_tasks_gsheet_oauth_start(self) -> Any:
        """Start Google Sheets OAuth for async-task integration."""
        from apero_ri.application import async_tasks_api_helpers as _ath
        return _ath.api_async_tasks_gsheet_oauth_start(self)

    def _api_async_tasks_gsheet_oauth_callback(self) -> Any:
        """Complete Google Sheets OAuth for async-task integration."""
        from apero_ri.application import async_tasks_api_helpers as _ath
        return _ath.api_async_tasks_gsheet_oauth_callback(self)

    # -----------------------------------------------------------------
    # User links API
    # -----------------------------------------------------------------
    def _api_user_links_get(self) -> Any:
        """Return saved links for the current user."""
        return _impls.ariapp_api_user_links_get(self)

    def _api_user_links_add(self) -> Any:
        """Add a saved link for the current user."""
        return _impls.ariapp_api_user_links_add(self)

    def _api_user_links_update(self) -> Any:
        """Update a saved link for the current user."""
        return _impls.ariapp_api_user_links_update(self)

    def _api_user_links_remove(self) -> Any:
        """Remove a saved link for the current user."""
        return _impls.ariapp_api_user_links_remove(self)

    def _api_user_links_add_section(self) -> Any:
        """Add a section to the current user's saved links."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        section = str(body.get("section", "")).strip()
        if not section:
            return jsonify(success=False, error="section required"), 400
        data = ud.add_link_section(user_info["username"], section)
        return jsonify(success=True, data=data)

    def _api_user_links_remove_section(self) -> Any:
        """Remove a section from the current user's saved links."""
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
    def _api_user_notes_list(self) -> Any:
        """List notes saved by the current user."""
        return _impls.ariapp_api_user_notes_list(self)

    def _api_user_notes_get(self) -> Any:
        """Return a note selected by the current request."""
        return _impls.ariapp_api_user_notes_get(self)

    def _api_user_notes_save(self) -> Any:
        """Save a note submitted by the current user."""
        return _impls.ariapp_api_user_notes_save(self)

    def _api_user_notes_delete(self) -> Any:
        """Delete a note selected by the current request."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        note_id = str(body.get("id", "")).strip()
        if not note_id:
            return jsonify(success=False, error="id required"), 400
        ok = ud.delete_note(user_info["username"], note_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_notes_render(self) -> Any:
        """Render submitted note text as HTML."""
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
    def _api_user_prefs_get(self) -> Any:
        """Return preferences saved by the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        prefs = ud.load_user_prefs(user_info["username"])
        return jsonify(success=True, prefs=prefs)

    def _api_user_prefs_save(self) -> Any:
        """Save user preferences from the current request."""
        return _impls.ariapp_api_user_prefs_save(self)

    # -----------------------------------------------------------------
    # User calendar API
    # -----------------------------------------------------------------
    def _api_user_calendar_list(self) -> Any:
        """List calendar events for the current user."""
        return _impls.ariapp_api_user_calendar_list(self)

    def _api_user_calendar_save(self) -> Any:
        """Save a calendar event submitted by the current user."""
        return _impls.ariapp_api_user_calendar_save(self)

    def _api_user_calendar_delete(self) -> Any:
        """Delete a calendar event selected by the current request."""
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
    def _api_user_todo_list(self) -> Any:
        """List todo items saved by the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        items = ud.list_todo_items(user_info["username"])
        metadata = ud.get_todo_metadata(user_info["username"])
        return jsonify(success=True, items=items, metadata=metadata)

    def _api_user_todo_save(self) -> Any:
        """Save a todo item submitted by the current user."""
        return _impls.ariapp_api_user_todo_save(self)

    def _api_user_todo_toggle(self) -> Any:
        """Toggle completion for a selected todo item."""
        return _impls.ariapp_api_user_todo_toggle(self)

    def _api_user_todo_delete(self) -> Any:
        """Delete a todo item selected by the current request."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        body = request.get_json() or {}
        item_id = str(body.get("id", "")).strip()
        if not item_id:
            return jsonify(success=False, error="id required"), 400
        ok = ud.delete_todo_item(user_info["username"], item_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_todo_reorder(self) -> Any:
        """Reorder todo items for the current user."""
        return _impls.ariapp_api_user_todo_reorder(self)

    # -----------------------------------------------------------------
    # Admin calendar API
    # -----------------------------------------------------------------
    def _require_admin_calendar_perm(self) -> Any:
        """Resolve the current user's admin-calendar permission."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        
        args = (user_info["groups"], self.ari_groups)
        perms = permissions_mod.resolve_user_permissions(*args)
        
        if "view.admin.calendar" not in perms:
            return None, None
        return user_info, perms

    def _api_admin_calendar_list(self) -> Any:
        """List calendar events for the requested instrument."""
        user_info, perms = self._require_admin_calendar_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        instrument = request.args.get("instrument", "").strip()
        if not instrument:
            return jsonify(success=False, error="instrument required"), 400
        events = ud.load_instrument_calendar(instrument).get("events", [])
        return jsonify(success=True, events=events)

    def _api_admin_calendar_save(self) -> Any:
        """Save an instrument calendar event from the current request."""
        return _impls.ariapp_api_admin_calendar_save(self)

    def _api_admin_calendar_delete(self) -> Any:
        """Delete an instrument calendar event."""
        return _impls.ariapp_api_admin_calendar_delete(self)

    # -----------------------------------------------------------------
    # ICS feed API — user calendar
    # -----------------------------------------------------------------
    def _api_user_ics_list(self) -> Any:
        """List ICS feeds configured for the current user's calendar."""
        return _impls.ariapp_api_user_ics_list(self)

    def _api_user_ics_add(self) -> Any:
        """Add an ICS feed to the current user's calendar."""
        return _impls.ariapp_api_user_ics_add(self)

    def _api_user_ics_delete(self) -> Any:
        """Delete an ICS feed from the current user's calendar."""
        return _impls.ariapp_api_user_ics_delete(self)

    def _api_user_ics_refresh(self) -> Any:
        """Refresh an ICS feed in the current user's calendar."""
        return _impls.ariapp_api_user_ics_refresh(self)

    def _api_user_ics_edit(self) -> Any:
        """Edit an ICS feed in the current user's calendar."""
        return _impls.ariapp_api_user_ics_edit(self)

    # -----------------------------------------------------------------
    # ICS feed API — instrument / admin calendar
    # -----------------------------------------------------------------
    def _api_admin_ics_list(self) -> Any:
        """List ICS feeds for the instrument calendar."""
        return _impls.ariapp_api_admin_ics_list(self)

    def _api_admin_ics_add(self) -> Any:
        """Add an ICS feed to the instrument calendar."""
        return _impls.ariapp_api_admin_ics_add(self)

    def _api_admin_ics_delete(self) -> Any:
        """Delete an ICS feed from the instrument calendar."""
        return _impls.ariapp_api_admin_ics_delete(self)

    def _api_admin_ics_refresh(self) -> Any:
        """Refresh an ICS feed in the instrument calendar."""
        return _impls.ariapp_api_admin_ics_refresh(self)

    def _api_admin_ics_edit(self) -> Any:
        """Edit an ICS feed in the instrument calendar."""
        return _impls.ariapp_api_admin_ics_edit(self)

    # -----------------------------------------------------------------
    # Admin links API
    # -----------------------------------------------------------------
    def _require_admin_links_perm(self) -> Any:
        """Resolve the current user's admin-links permission."""
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

    def _api_admin_links_get(self) -> Any:
        """Return configured links for the requested instrument."""
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        instrument = request.args.get("instrument", "").strip()
        if not instrument:
            return jsonify(success=False, error="instrument required"), 400
        data = ud.load_instrument_links(instrument)
        return jsonify(success=True, data=data)

    def _api_admin_links_add(self) -> Any:
        """Add an instrument link from the current request."""
        return _impls.ariapp_api_admin_links_add(self)

    def _api_admin_links_update(self) -> Any:
        """Update an instrument link from the current request."""
        return _impls.ariapp_api_admin_links_update(self)

    def _api_admin_links_remove(self) -> Any:
        """Remove an instrument link selected by the request."""
        return _impls.ariapp_api_admin_links_remove(self)

    def _api_admin_links_add_section(self) -> Any:
        """Add a section to the instrument link list."""
        return _impls.ariapp_api_admin_links_add_section(self)

    def _api_admin_links_remove_section(self) -> Any:
        """Remove a section from the instrument link list."""
        return _impls.ariapp_api_admin_links_remove_section(self)

    # -----------------------------------------------------------------
    # Admin email API
    # -----------------------------------------------------------------
    def _require_admin_email_perm(self) -> Any:
        """Resolve the current user's administrative email permissions."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"],
            self.ari_groups,
        )
        return user_info, perms

    def _api_admin_email_test(self) -> Any:
        """Check whether administrative email settings are valid."""
        return _impls.ariapp_api_admin_email_test(self)

    def _api_admin_email_save(self) -> Any:
        """Save administrative email settings."""
        return _impls.ariapp_api_admin_email_save(self)

    def _api_admin_email_send_test(self) -> Any:
        """Send a test email using administrative mail settings."""
        return _impls.ariapp_api_admin_email_send_test(self)

    # -----------------------------------------------------------------
    # Admin backup API
    # -----------------------------------------------------------------
    def _require_admin_backup_perm(self) -> Any:
        """Resolve the current user's administrative backup permissions."""
        user_info = auth.get_effective_user(session)
        if not user_info:
            return None, None
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"],
            self.ari_groups,
        )
        return user_info, perms

    def _api_admin_backups_test(self) -> Any:
        """Check the configured backup service connection."""
        return _impls.ariapp_api_admin_backups_test(self)

    def _api_admin_backups_oauth_start(self) -> Any:
        """Start OAuth authorization for the backup service."""
        return _impls.ariapp_api_admin_backups_oauth_start(self)

    def _api_admin_backups_oauth_callback(self) -> Any:
        """Complete OAuth authorization for the backup service."""
        return admin_backup_api_helpers.api_admin_backups_oauth_callback(self)

    def _api_admin_backups_test_backup(self) -> Any:
        """Test a backup using the configured backup destination."""
        return _impls.ariapp_api_admin_backups_test_backup(self)

    def _api_admin_backups_save(self) -> Any:
        """Save administrative backup settings."""
        return admin_backup_api_helpers.api_admin_backups_save(self)

    def _api_admin_backups_upload_json(self) -> Any:
        """Upload backup configuration in JSON form."""
        return admin_backup_api_helpers.api_admin_backups_upload_json(self)

    def _api_admin_backups_list(self) -> Any:
        """List available administrative backups."""
        return _impls.ariapp_api_admin_backups_list(self)

    def _api_admin_backups_delete(self) -> Any:
        """Delete a selected administrative backup."""
        return _impls.ariapp_api_admin_backups_delete(self)

    def _api_admin_backups_delete_all(self) -> Any:
        """Delete all administrative backups."""
        return _impls.ariapp_api_admin_backups_delete_all(self)

    def _api_admin_backups_sync(self) -> Any:
        """Synchronize configured backups with their destination."""
        return _impls.ariapp_api_admin_backups_sync(self)

    def _api_admin_backups_download(self) -> Any:
        """Download a selected administrative backup."""
        return _impls.ariapp_api_admin_backups_download(self)

    def _api_admin_backups_sync_from_cloud(self) -> Any:
        """Synchronize backups from the configured cloud destination."""
        return _impls.ariapp_api_admin_backups_sync_from_cloud(self)

    def _api_admin_backups_validate_dir(self) -> Any:
        """Validate a directory selected as a backup destination."""
        return _impls.ariapp_api_admin_backups_validate_dir(self)

    def _api_admin_backups_browse(self) -> Any:
        """Browse directories available for backup configuration."""
        return _impls.ariapp_api_admin_backups_browse(self)

    # -----------------------------------------------------------------
    # SSHFS Management API handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_keys_list(self) -> Any:
        """List SSHFS keys configured for administrative mounts."""
        return _impls.ariapp_api_admin_sshfs_keys_list(self)

    def _api_admin_sshfs_keys_add(self) -> Any:
        """Add an SSH key for administrative SSHFS mounts."""
        return _impls.ariapp_api_admin_sshfs_keys_add(self)

    def _api_admin_sshfs_keys_delete(self, key_name: str) -> Any:
        """Delete an SSHFS key selected by its name."""
        return _impls.ariapp_api_admin_sshfs_keys_delete(self, key_name)

    def _api_admin_sshfs_mounts_add(self) -> Any:
        """Add an administrative SSHFS mount definition."""
        return _impls.ariapp_api_admin_sshfs_mounts_add(self)

    def _api_admin_sshfs_mounts_test_connection(self) -> Any:
        """Test a connection for an administrative SSHFS mount."""
        return _impls.ariapp_api_admin_sshfs_mounts_test_connection(self)

    def _api_admin_sshfs_mounts_update(self, mount_name: str) -> Any:
        """Update an SSHFS mount selected by its name."""
        return _impls.ariapp_api_admin_sshfs_mounts_update(self, mount_name)

    def _api_admin_sshfs_mounts_delete(self, mount_name: str) -> Any:
        """Delete an SSHFS mount selected by its name."""
        return _impls.ariapp_api_admin_sshfs_mounts_delete(self, mount_name)

    def _api_admin_sshfs_mounts_mount(self, mount_name: str) -> Any:
        """Mount an SSHFS target selected by its name."""
        return _impls.ariapp_api_admin_sshfs_mounts_mount(self, mount_name)

    def _api_admin_sshfs_mounts_unmount(self, mount_name: str) -> Any:
        """Unmount an SSHFS target selected by its name."""
        return _impls.ariapp_api_admin_sshfs_mounts_unmount(self, mount_name)

    def _api_admin_sshfs_mounts_unmount_lazy(
        self, mount_name: str
    ) -> Any:
        """Lazily unmount an SSHFS target selected by its name."""
        args = (mount_name,)
        return _impls.ariapp_api_admin_sshfs_mounts_unmount_lazy(self, *args)

    def _api_admin_sshfs_mounts_status(self) -> Any:
        """Return status for configured SSHFS mounts."""
        return _impls.ariapp_api_admin_sshfs_mounts_status(self)

    def _api_admin_sshfs_mounts_log(self, mount_name: str) -> Any:
        """Return log output for an SSHFS mount selected by name."""
        return _impls.ariapp_api_admin_sshfs_mounts_log(self, mount_name)

    # -----------------------------------------------------------------
    # Interactive SSH terminal handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_interactive_start_test(self) -> Any:
        """Start an interactive test SSHFS session."""
        return _impls.ariapp_api_admin_sshfs_interactive_start_test(self)

    def _api_admin_sshfs_interactive_start_mount(self) -> Any:
        """Start an interactive SSHFS mount session."""
        return _impls.ariapp_api_admin_sshfs_interactive_start_mount(self)

    def _api_admin_sshfs_interactive_poll(self) -> Any:
        """Poll an interactive SSHFS session for output."""
        return _impls.ariapp_api_admin_sshfs_interactive_poll(self)

    def _api_admin_sshfs_interactive_send(self) -> Any:
        """Send input to an interactive SSHFS session."""
        return _impls.ariapp_api_admin_sshfs_interactive_send(self)

    def _api_admin_sshfs_interactive_close(self) -> Any:
        """Close an interactive SSHFS session."""
        return admin_sshfs_api_helpers.api_admin_sshfs_interactive_close(self)

    # -----------------------------------------------------------------
    # Upload management — Admin API
    # -----------------------------------------------------------------
    def _api_admin_uploads_config_get(self) -> Any:
        """Return administrative upload configuration."""
        return _impls.ariapp_api_admin_uploads_config_get(self)

    def _api_admin_uploads_dir_add(self) -> Any:
        """Add a directory to administrative upload settings."""
        return _impls.ariapp_api_admin_uploads_dir_add(self)

    def _api_admin_uploads_dir_edit(self) -> Any:
        """Edit an administrative upload directory definition."""
        return _impls.ariapp_api_admin_uploads_dir_edit(self)

    def _api_admin_uploads_dir_delete(self) -> Any:
        """Delete an administrative upload directory definition."""
        return _impls.ariapp_api_admin_uploads_dir_delete(self)

    def _api_admin_uploads_quota_get(self) -> Any:
        """Return quota information for administrative uploads."""
        return _impls.ariapp_api_admin_uploads_quota_get(self)

    # -----------------------------------------------------------------
    # Asset management — Admin API (also used by apero_assets.py)
    # -----------------------------------------------------------------
    def _api_admin_assets_status(self) -> Any:
        """Return status for managed static assets."""
        return admin_assets_api_helpers.api_admin_assets_status(self)

    def _api_admin_assets_config(self) -> Any:
        """Return configuration for managed static assets."""
        return admin_assets_api_helpers.api_admin_assets_config(self)

    def _api_admin_assets_delete(self) -> Any:
        """Delete a managed static asset selected by the request."""
        return admin_assets_api_helpers.api_admin_assets_delete(self)

    def _api_admin_assets_upload(self) -> Any:
        """Upload a managed static asset."""
        return admin_assets_api_helpers.api_admin_assets_upload(self)

    def _public_assets_download(self, filename: str) -> Any:
        """Download an asset available through the public asset route."""
        return admin_assets_api_helpers.public_assets_download(
            self, filename)

    def _api_assets_download(self, filename: str) -> Any:
        """Download a managed asset through the authenticated API."""
        return admin_assets_api_helpers.api_assets_download(self, filename)

    # -----------------------------------------------------------------
    # Upload management — User API
    # -----------------------------------------------------------------
    def _api_user_uploads_list(self) -> Any:
        """List uploads belonging to the current user."""
        return _impls.ariapp_api_user_uploads_list(self)

    def _api_user_uploads_upload(self) -> Any:
        """Upload a file for the current user."""
        return _impls.ariapp_api_user_uploads_upload(self)

    def _api_user_uploads_delete(self) -> Any:
        """Delete an upload selected by the current request."""
        return _impls.ariapp_api_user_uploads_delete(self)

    def _api_user_uploads_share(self) -> Any:
        """Create or update a share link for a user upload."""
        return _impls.ariapp_api_user_uploads_share(self)

    def _uploads_share_download(self, token: str) -> Any:
        """Download a user upload through its public share token."""
        return _impls.ariapp_uploads_share_download(self, token)

    # -----------------------------------------------------------------
    # Run override
    # -----------------------------------------------------------------
    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Start the Flask development or production server."""
        return _impls.ariapp_run(self, host, port, debug, **kwargs)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
