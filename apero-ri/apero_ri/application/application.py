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
import socket
import smtplib
import threading
import time
import traceback
import uuid
import yaml
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Optional, List

from flask import (Flask, render_template, redirect, url_for,
                   request, session, flash, jsonify,
                   send_from_directory, send_file)

from apero_ri.core.permissions import load_groups
from apero_ri.core.permissions import load_pages
from apero_ri.core.permissions import load_parameters
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core.permissions import get_inherited_groups
from apero_ri.core.permissions import get_children
from apero_ri.core.permissions import is_parent_page
from apero_ri.core.permissions import page_id_to_url
from apero_ri.core.permissions import page_id_to_template
from apero_ri.core.permissions import page_id_to_endpoint
from apero_ri.core.permissions import get_nav_pages
from apero_ri.core.permissions import get_visible_cards
from apero_ri.core.permissions import find_full_nav_root
from apero_ri.core.permissions import get_sidebar_tree
from apero_ri.core.permissions import get_pinned_sidebar_items
from apero_ri.core.auth import set_ari_dir as auth_set_ari_dir
from apero_ri.core.auth import ensure_default_user
from apero_ri.core.auth import authenticate
from apero_ri.core.auth import get_effective_user
from apero_ri.core.auth import get_public_permissions
from apero_ri.core.auth import get_user_info
from apero_ri.core.auth import hash_password
from apero_ri.core.auth import verify_password
from apero_ri.core.auth import search_users
from apero_ri.core.auth import list_all_users
from apero_ri.core.auth import update_user_groups
from apero_ri.core.auth import update_user_instruments
from apero_ri.core.auth import delete_user
from apero_ri.core.auth import load_users
from apero_ri.core.auth import save_users
from apero_ri.core.auth import user_has_admin_privileges
from apero_ri.core.auth import user_is_super_admin
from apero_ri.core.auth import load_science_groups
from apero_ri.core.auth import save_science_groups
from apero_ri.core.auth import get_users_for_instrument
from apero_ri.core.auth import load_apero_profiles
from apero_ri.core.auth import save_apero_profiles
from apero_ri.core.auth import load_db_access
from apero_ri.core.auth import save_db_access
from apero_ri.core.auth import load_db_tunnels
from apero_ri.core.auth import save_db_tunnels
from apero_ri.core.auth import load_admin_health_config
from apero_ri.core.auth import save_admin_health_config
from apero_ri.core.auth import validate_path_exists
from apero_ri.core.auth import validate_database_connection
from apero_ri.core.auth import get_accessible_profiles
from apero_ri.core.auth import load_async_tasks
from apero_ri.core.auth import save_async_tasks
from apero_ri.core import task_runner
from apero_ri.tasks import apero_async
from apero_ri.core import user_data as ud
from apero_ri.core import email_backend as eb
from apero_ri.core import backup_backend as bb
from apero_ri.core import sshfs_backend as sb
from apero_ri.core import secret_store as ss
from apero_ri.core.docs import get_versions
from apero_ri.core.docs import get_default_version
from apero_ri.core.docs import get_doc_content
from apero_ri.core.docs import save_doc_content
from apero_ri.core.docs import save_uploaded_image
from apero_ri.core.docs import DOC_IMAGES
from apero_ri.core.object_funcs import (build_object_page_stats,
                                         load_object_ftable_rows,
                                         load_object_htable_rows,
                                         load_object_preset,
                                         load_object_table_row)
from apero_ri.core import basket_funcs as bk
from apero_ri.core import download_tracker as dt
from apero_ri.core import api_tokens as at

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.application'
PACKAGE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = PACKAGE_DIR / 'templates'
STATIC_DIR = PACKAGE_DIR / 'static'


# =============================================================================
# Define classes
# =============================================================================
class ARIApp(Flask):
    """APERO Reduction Interface Flask application."""

    def __init__(self, **kwargs):
        super().__init__(
            __name__,
            template_folder=str(TEMPLATE_DIR),
            static_folder=str(STATIC_DIR),
            **kwargs,
        )
        # Parse command-line arguments
        self.args = self._get_arguments()
        os.environ['ARI_DIR'] = str(
            Path(self.args.data_dir).expanduser()
            if self.args.data_dir else (Path.home() / '.ari')
        )
        ud.set_ari_dir(self.args.data_dir or str(Path.home() / '.ari'))
        auth_set_ari_dir(self.args.data_dir or str(Path.home() / '.ari'))
        dt.set_ari_dir(Path(self.args.data_dir).expanduser()
                       if self.args.data_dir else Path.home() / '.ari')
        # Secret key for sessions
        self.secret_key = self._load_or_create_secret()
        # Load YAML definitions (read-only)
        self.ari_groups = load_groups()
        self.ari_pages = load_pages()
        # Remove template entries (with {placeholders}) — they are
        # expanded dynamically at request time from apero_profiles.yaml
        self._page_templates = {}
        for pid in list(self.ari_pages.keys()):
            if '{' in pid:
                self._page_templates[pid] = self.ari_pages.pop(pid)
        # Ensure default admin user exists
        ensure_default_user()
        # In-memory throttle state for forgot-password requests
        self._forgot_pw_rate_limit = {}
        self._forgot_pw_max_attempts = 3
        self._forgot_pw_base_wait = 30
        self._forgot_pw_max_wait = 600
        # Cached admin health checks (expensive DB/SMTP checks)
        self._admin_health_cache = {}
        self._admin_health_cache_ttl = timedelta(hours=1)
        self._admin_health_cache_lock = threading.Lock()
        ari_root = Path(self.args.data_dir or str(Path.home() / '.ari'))
        self._admin_health_cache_file = (
            ari_root / 'admin' / 'health' / 'health_cache.json'
        )
        self._admin_health_cache_legacy_file = (
            ari_root / 'admin' / 'health_cache.json'
        )
        self._load_health_cache_from_disk()
        self._shutdown_lock = threading.Lock()
        self._shutdown_started = False
        # Configure session lifetime for "remember me"
        self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        self.config['SESSION_COOKIE_NAME'] = 'apero_ri'
        self.config['SESSION_COOKIE_HTTPONLY'] = True
        self.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.config['SESSION_REFRESH_EACH_REQUEST'] = True
        # Register context processors and routes
        self._register_context_processors()
        self._register_routes()
        self._start_admin_health_refresher()
        task_runner.start_background_services(
            self.args.data_dir or str(Path.home() / '.ari')
        )
        atexit.register(self.shutdown)

    # -----------------------------------------------------------------
    # Argument parsing
    # -----------------------------------------------------------------
    @staticmethod
    def _get_arguments() -> argparse.Namespace:
        """Parse command-line arguments for the ARI server."""
        parser = argparse.ArgumentParser(
            description='APERO reduction interface'
        )
        parser.add_argument(
            '--data-dir', type=str,
            help='Override data directory (default: ~/.ari)',
        )
        parser.add_argument(
            '--port', type=int, default=6666,
            help='Port to run the server on (default: 6666)',
        )
        parser.add_argument(
            '--host', type=str, default='auto',
            help=('Host binding (default: auto; prefers :: for '
                  'localhost, falls back to 0.0.0.0)'),
        )
        return parser.parse_args()

    @staticmethod
    def _resolve_host(host: str) -> str:
        """Resolve 'auto' host to '::' (IPv6) or '0.0.0.0' (IPv4)."""
        if host != 'auto':
            return host
        # prefer IPv6 dual-stack if available
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.close()
            return '::'
        except OSError:
            return '0.0.0.0'

    # -----------------------------------------------------------------
    # Secret key management
    # -----------------------------------------------------------------
    @staticmethod
    def _load_or_create_secret() -> str:
        """Load or create a persistent secret key in ARI_DIR/secret."""
        ari_dir = ss.get_ari_dir()
        secret_file = ss.resolve_secret_file(
            'secret.key',
            legacy_paths=[ari_dir / 'secret.key',
                         Path.home() / '.ari' / 'secret.key'],
        )
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        if secret_file.exists():
            return secret_file.read_text().strip()
        key = secrets.token_hex(32)
        secret_file.write_text(key, encoding='utf-8')
        ss.protect_path(secret_file, 0o600)
        return key

    # -----------------------------------------------------------------
    # Context processors (available in every template)
    # -----------------------------------------------------------------
    def _register_context_processors(self):
        @self.context_processor
        def inject_globals():
            user_info = get_effective_user(session)
            if user_info:
                perms = resolve_user_permissions(
                    user_info['groups'], self.ari_groups
                )
                logged_in = True
                username = user_info['username']
                first_names = str(user_info.get('first_names', '')).strip()
                welcome_name = (first_names.split()[0]
                                if first_names else username)
                login_as = session.get('login_as')
            else:
                perms = get_public_permissions()
                logged_in = False
                username = None
                welcome_name = None
                login_as = None

            nav_pages = get_nav_pages(perms, self.ari_pages)
            logo_path = STATIC_DIR / 'images' / 'apero_logo.png'

            return {
                'logged_in': logged_in,
                'username': username,
                'welcome_name': welcome_name,
                'login_as_user': login_as,
                'last_login': session.get('last_login'),
                'user_permissions': perms,
                'nav_pages': nav_pages,
                'ari_pages': self.ari_pages,
                'logo_exists': logo_path.exists(),
            }

    # -----------------------------------------------------------------
    # Route registration
    # -----------------------------------------------------------------
    def _register_routes(self):
        """Register all routes from pages.yaml plus login/logout."""
        # Login route (special)
        self.add_url_rule('/login', 'login', self._login_view,
                          methods=['GET', 'POST'])
        self.add_url_rule('/forgot-password',
                  'forgot_password',
                  self._forgot_password_view,
                  methods=['GET', 'POST'])
        self.add_url_rule('/reset-password/<token>',
                  'reset_password',
                  self._reset_password_view,
                  methods=['GET', 'POST'])
        self.add_url_rule('/register', 'register', self._register_view,
                  methods=['GET'])
        # Logout route (special)
        self.add_url_rule('/logout', 'logout', self._logout_view)

        # Registration and account APIs
        self.add_url_rule('/api/auth/register/start',
                  'api_auth_register_start',
                  self._api_auth_register_start,
                  methods=['POST'])
        self.add_url_rule('/api/auth/register/verify',
                  'api_auth_register_verify',
                  self._api_auth_register_verify,
                  methods=['POST'])
        self.add_url_rule('/api/user/account/get',
                  'api_user_account_get',
                  self._api_user_account_get)
        self.add_url_rule('/api/user/account/update',
                  'api_user_account_update',
                  self._api_user_account_update,
                  methods=['POST'])
        self.add_url_rule('/api/user/account/request-primary-email',
                  'api_user_account_request_primary_email',
                  self._api_user_account_request_primary_email,
                  methods=['POST'])
        self.add_url_rule('/api/user/account/confirm-primary-email',
                  'api_user_account_confirm_primary_email',
                  self._api_user_account_confirm_primary_email,
                  methods=['POST'])
        self.add_url_rule('/api/user/pins/list',
              'api_user_pins_list',
              self._api_user_pins_list)
        self.add_url_rule('/api/user/pins/toggle',
              'api_user_pins_toggle',
              self._api_user_pins_toggle,
              methods=['POST'])
        self.add_url_rule('/api/user/pins/remove',
              'api_user_pins_remove',
              self._api_user_pins_remove,
              methods=['POST'])
        self.add_url_rule('/api/user/pins/reorder',
              'api_user_pins_reorder',
              self._api_user_pins_reorder,
              methods=['POST'])
        self.add_url_rule('/api/user/object-sections/get',
              'api_user_object_sections_get',
              self._api_user_object_sections_get)
        self.add_url_rule('/api/user/object-sections/toggle',
              'api_user_object_sections_toggle',
              self._api_user_object_sections_toggle,
              methods=['POST'])
        self.add_url_rule('/api/user/object-sections/reorder',
              'api_user_object_sections_reorder',
              self._api_user_object_sections_reorder,
              methods=['POST'])

        # User links API routes
        self.add_url_rule('/api/user/links/get', 'api_user_links_get',
                  self._api_user_links_get)
        self.add_url_rule('/api/user/links/add', 'api_user_links_add',
                  self._api_user_links_add, methods=['POST'])
        self.add_url_rule('/api/user/links/update', 'api_user_links_update',
                  self._api_user_links_update, methods=['POST'])
        self.add_url_rule('/api/user/links/remove', 'api_user_links_remove',
                  self._api_user_links_remove, methods=['POST'])
        self.add_url_rule('/api/user/links/add-section',
                  'api_user_links_add_section',
                  self._api_user_links_add_section, methods=['POST'])
        self.add_url_rule('/api/user/links/remove-section',
                  'api_user_links_remove_section',
                  self._api_user_links_remove_section, methods=['POST'])

        # User notes API routes
        self.add_url_rule('/api/user/notes/list', 'api_user_notes_list',
                  self._api_user_notes_list)
        self.add_url_rule('/api/user/notes/get', 'api_user_notes_get',
                  self._api_user_notes_get)
        self.add_url_rule('/api/user/notes/save', 'api_user_notes_save',
                  self._api_user_notes_save, methods=['POST'])
        self.add_url_rule('/api/user/notes/delete', 'api_user_notes_delete',
                  self._api_user_notes_delete, methods=['POST'])
        self.add_url_rule('/api/user/notes/render', 'api_user_notes_render',
                  self._api_user_notes_render, methods=['POST'])

        # User preferences API routes
        self.add_url_rule('/api/user/prefs/get', 'api_user_prefs_get',
                  self._api_user_prefs_get)
        self.add_url_rule('/api/user/prefs/save', 'api_user_prefs_save',
                  self._api_user_prefs_save, methods=['POST'])

        # User calendar API routes
        self.add_url_rule('/api/user/calendar/list', 'api_user_calendar_list',
                  self._api_user_calendar_list)
        self.add_url_rule('/api/user/calendar/save', 'api_user_calendar_save',
                  self._api_user_calendar_save, methods=['POST'])
        self.add_url_rule('/api/user/calendar/delete',
                  'api_user_calendar_delete',
                  self._api_user_calendar_delete, methods=['POST'])

        # User todo API routes
        self.add_url_rule('/api/user/todo/list', 'api_user_todo_list',
                  self._api_user_todo_list)
        self.add_url_rule('/api/user/todo/save', 'api_user_todo_save',
                  self._api_user_todo_save, methods=['POST'])
        self.add_url_rule('/api/user/todo/toggle', 'api_user_todo_toggle',
                  self._api_user_todo_toggle, methods=['POST'])
        self.add_url_rule('/api/user/todo/delete', 'api_user_todo_delete',
                  self._api_user_todo_delete, methods=['POST'])
        self.add_url_rule('/api/user/todo/reorder', 'api_user_todo_reorder',
                  self._api_user_todo_reorder, methods=['POST'])

        # Admin calendar API routes
        self.add_url_rule('/api/admin/calendar/list',
                  'api_admin_calendar_list',
                  self._api_admin_calendar_list)
        self.add_url_rule('/api/admin/calendar/save',
                  'api_admin_calendar_save',
                  self._api_admin_calendar_save, methods=['POST'])
        self.add_url_rule('/api/admin/calendar/delete',
                  'api_admin_calendar_delete',
                  self._api_admin_calendar_delete, methods=['POST'])

        # Admin links API routes
        self.add_url_rule('/api/admin/links/get', 'api_admin_links_get',
                  self._api_admin_links_get)
        self.add_url_rule('/api/admin/links/add', 'api_admin_links_add',
                  self._api_admin_links_add, methods=['POST'])
        self.add_url_rule('/api/admin/links/update', 'api_admin_links_update',
                  self._api_admin_links_update, methods=['POST'])
        self.add_url_rule('/api/admin/links/remove', 'api_admin_links_remove',
                  self._api_admin_links_remove, methods=['POST'])
        self.add_url_rule('/api/admin/links/add-section',
                  'api_admin_links_add_section',
                  self._api_admin_links_add_section, methods=['POST'])
        self.add_url_rule('/api/admin/links/remove-section',
                  'api_admin_links_remove_section',
                  self._api_admin_links_remove_section,
                  methods=['POST'])

        # Admin email API routes
        self.add_url_rule('/api/admin/email/test', 'api_admin_email_test',
                  self._api_admin_email_test)
        self.add_url_rule('/api/admin/email/save', 'api_admin_email_save',
                  self._api_admin_email_save, methods=['POST'])
        self.add_url_rule('/api/admin/email/send-test',
                  'api_admin_email_send_test',
                  self._api_admin_email_send_test, methods=['POST'])
        self.add_url_rule('/api/admin/backups/test',
                  'api_admin_backups_test',
                  self._api_admin_backups_test)
        self.add_url_rule('/api/admin/backups/oauth/start',
                  'api_admin_backups_oauth_start',
                  self._api_admin_backups_oauth_start)
        self.add_url_rule('/api/admin/backups/oauth/callback',
                  'api_admin_backups_oauth_callback',
                  self._api_admin_backups_oauth_callback)
        self.add_url_rule('/api/admin/backups/test-backup',
                  'api_admin_backups_test_backup',
                  self._api_admin_backups_test_backup, methods=['POST'])
        self.add_url_rule('/api/admin/backups/save',
                  'api_admin_backups_save',
                  self._api_admin_backups_save, methods=['POST'])
        self.add_url_rule('/api/admin/backups/upload-json',
              'api_admin_backups_upload_json',
              self._api_admin_backups_upload_json, methods=['POST'])
        self.add_url_rule('/api/admin/backups/list',
                  'api_admin_backups_list',
                  self._api_admin_backups_list)
        self.add_url_rule('/api/admin/backups/delete',
                  'api_admin_backups_delete',
                  self._api_admin_backups_delete, methods=['POST'])
        self.add_url_rule('/api/admin/backups/delete-all',
                  'api_admin_backups_delete_all',
                  self._api_admin_backups_delete_all, methods=['POST'])
        self.add_url_rule('/api/admin/backups/sync',
                  'api_admin_backups_sync',
                  self._api_admin_backups_sync, methods=['POST'])
        self.add_url_rule('/api/admin/backups/download',
                  'api_admin_backups_download',
                  self._api_admin_backups_download, methods=['POST'])
        self.add_url_rule('/api/admin/backups/sync-from-cloud',
                  'api_admin_backups_sync_from_cloud',
                  self._api_admin_backups_sync_from_cloud, methods=['POST'])
        self.add_url_rule('/api/admin/backups/browse',
              'api_admin_backups_browse',
              self._api_admin_backups_browse)
        self.add_url_rule('/api/admin/backups/validate-dir',
              'api_admin_backups_validate_dir',
              self._api_admin_backups_validate_dir)
        # SSHFS management routes
        self.add_url_rule('/api/admin/sshfs/keys/list',
                  'api_admin_sshfs_keys_list',
                  self._api_admin_sshfs_keys_list)
        self.add_url_rule('/api/admin/sshfs/keys/add',
                  'api_admin_sshfs_keys_add',
                  self._api_admin_sshfs_keys_add, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/keys/delete/<key_name>',
                  'api_admin_sshfs_keys_delete',
                  self._api_admin_sshfs_keys_delete, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/add',
                  'api_admin_sshfs_mounts_add',
                  self._api_admin_sshfs_mounts_add, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/update/<mount_name>',
              'api_admin_sshfs_mounts_update',
              self._api_admin_sshfs_mounts_update, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/test-connection',
              'api_admin_sshfs_mounts_test_connection',
              self._api_admin_sshfs_mounts_test_connection,
              methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/delete/<mount_name>',
                  'api_admin_sshfs_mounts_delete',
                  self._api_admin_sshfs_mounts_delete, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/mount/<mount_name>',
                  'api_admin_sshfs_mounts_mount',
                  self._api_admin_sshfs_mounts_mount, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/unmount/<mount_name>',
                  'api_admin_sshfs_mounts_unmount',
                  self._api_admin_sshfs_mounts_unmount, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/unmount-lazy/<mount_name>',
              'api_admin_sshfs_mounts_unmount_lazy',
              self._api_admin_sshfs_mounts_unmount_lazy, methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/mounts/status',
                  'api_admin_sshfs_mounts_status',
                  self._api_admin_sshfs_mounts_status)
        self.add_url_rule('/api/admin/sshfs/mounts/log/<mount_name>',
                  'api_admin_sshfs_mounts_log',
                  self._api_admin_sshfs_mounts_log)
        # Interactive SSH terminal routes
        self.add_url_rule('/api/admin/sshfs/interactive/start-test',
                  'api_admin_sshfs_interactive_start_test',
                  self._api_admin_sshfs_interactive_start_test,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/interactive/start-mount',
                  'api_admin_sshfs_interactive_start_mount',
                  self._api_admin_sshfs_interactive_start_mount,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/interactive/poll',
                  'api_admin_sshfs_interactive_poll',
                  self._api_admin_sshfs_interactive_poll,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/interactive/send',
                  'api_admin_sshfs_interactive_send',
                  self._api_admin_sshfs_interactive_send,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sshfs/interactive/close',
                  'api_admin_sshfs_interactive_close',
                  self._api_admin_sshfs_interactive_close,
                  methods=['POST'])
        self.add_url_rule('/api/admin/health/update',
              'api_admin_health_update',
              self._api_admin_health_update, methods=['POST'])
        self.add_url_rule('/api/admin/health/config',
            'api_admin_health_config_get',
            self._api_admin_health_config_get)
        self.add_url_rule('/api/admin/health/config',
            'api_admin_health_config_save',
            self._api_admin_health_config_save,
            methods=['POST'])

        # Plot cache admin routes
        self.add_url_rule('/api/admin/cache/save',
            'api_admin_cache_save',
            self._api_admin_cache_save, methods=['POST'])
        self.add_url_rule('/api/admin/cache/purge',
            'api_admin_cache_purge',
            self._api_admin_cache_purge, methods=['POST'])

        # Download management admin routes
        self.add_url_rule('/api/admin/dm/save-settings',
            'api_admin_dm_save_settings',
            self._api_admin_dm_save_settings, methods=['POST'])
        self.add_url_rule('/api/admin/dm/reset-user',
            'api_admin_dm_reset_user',
            self._api_admin_dm_reset_user, methods=['POST'])

        # User API token routes
        self.add_url_rule('/api/user/token/generate',
            'api_user_token_generate',
            self._api_user_token_generate, methods=['POST'])
        self.add_url_rule('/api/user/token/revoke',
            'api_user_token_revoke',
            self._api_user_token_revoke, methods=['POST'])

        # Documentation routes (edit, save, upload, images)
        self.add_url_rule('/docs/<page_ref>/edit', 'doc_edit',
                  self._doc_edit_view)
        self.add_url_rule('/docs/<page_ref>/save', 'doc_save',
                  self._doc_save_view, methods=['POST'])
        self.add_url_rule('/docs/upload-image', 'doc_upload_image',
                  self._doc_upload_image, methods=['POST'])
        self.add_url_rule('/doc-images/<filename>', 'doc_image',
                  self._doc_image_view)

        # Admin user management API routes
        self.add_url_rule('/api/admin/users/search', 'api_user_search',
                  self._api_user_search)
        self.add_url_rule('/api/admin/users/update-groups',
                  'api_user_update_groups',
                  self._api_user_update_groups,
                  methods=['POST'])
        self.add_url_rule('/api/admin/users/update-instruments',
                  'api_user_update_instruments',
                  self._api_user_update_instruments,
                  methods=['POST'])
        self.add_url_rule('/api/admin/users/delete',
                  'api_user_delete',
                  self._api_user_delete,
                  methods=['POST'])

        # Admin login-as API routes
        self.add_url_rule('/api/admin/login-as/search',
                  'api_login_as_search',
                  self._api_login_as_search)
        self.add_url_rule('/api/admin/login-as/set',
                  'api_login_as_set',
                  self._api_login_as_set,
                  methods=['POST'])
        self.add_url_rule('/api/admin/login-as/clear',
                  'api_login_as_clear',
                  self._api_login_as_clear,
                  methods=['POST'])

        # Admin science groups API routes
        self.add_url_rule('/api/admin/sci-groups/list',
                  'api_sci_groups_list',
                  self._api_sci_groups_list)
        self.add_url_rule('/api/admin/sci-groups/get',
                  'api_sci_groups_get',
                  self._api_sci_groups_get)
        self.add_url_rule('/api/admin/sci-groups/save',
                  'api_sci_groups_save',
                  self._api_sci_groups_save,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sci-groups/create',
                  'api_sci_groups_create',
                  self._api_sci_groups_create,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sci-groups/delete',
                  'api_sci_groups_delete',
                  self._api_sci_groups_delete,
                  methods=['POST'])
        self.add_url_rule('/api/admin/sci-groups/refresh-run-ids',
              'api_sci_groups_refresh_run_ids',
              self._api_sci_groups_refresh_run_ids,
              methods=['POST'])

        # Admin APERO profiles API routes
        self.add_url_rule('/api/admin/apero-profiles/list',
                  'api_apero_profiles_list',
                  self._api_apero_profiles_list)
        self.add_url_rule('/api/admin/apero-profiles/overview-status',
              'api_apero_profiles_overview',
              self._api_apero_profiles_overview)
        self.add_url_rule('/api/admin/apero-profiles/save',
                  'api_apero_profiles_save',
                  self._api_apero_profiles_save,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/delete',
                  'api_apero_profiles_delete',
                  self._api_apero_profiles_delete,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/reorder',
                  'api_apero_profiles_reorder',
                  self._api_apero_profiles_reorder,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/validate-path',
                  'api_apero_profiles_validate',
                  self._api_apero_profiles_validate)
        self.add_url_rule('/api/admin/apero-profiles/browse',
                  'api_apero_profiles_browse',
                  self._api_apero_profiles_browse)
        self.add_url_rule('/api/admin/apero-profiles/update-groups',
                  'api_apero_profiles_update_groups',
                  self._api_apero_profiles_update_groups,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/test-db',
                  'api_apero_profiles_test_db',
                  self._api_apero_profiles_test_db,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/list-tables',
              'api_apero_profiles_list_tables',
              self._api_apero_profiles_list_tables,
              methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/test-tables',
                  'api_apero_profiles_test_tables',
                  self._api_apero_profiles_test_tables,
                  methods=['POST'])

        # Interactive SSH tunnel for APERO profile DB connections
        self.add_url_rule('/api/admin/apero-profiles/ssh-tunnel/start',
                  'api_apero_profiles_ssh_tunnel_start',
                  self._api_apero_profiles_ssh_tunnel_start,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/ssh-tunnel/poll',
                  'api_apero_profiles_ssh_tunnel_poll',
                  self._api_apero_profiles_ssh_tunnel_poll,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/ssh-tunnel/send',
                  'api_apero_profiles_ssh_tunnel_send',
                  self._api_apero_profiles_ssh_tunnel_send,
                  methods=['POST'])
        self.add_url_rule('/api/admin/apero-profiles/ssh-tunnel/close',
                  'api_apero_profiles_ssh_tunnel_close',
                  self._api_apero_profiles_ssh_tunnel_close,
                  methods=['POST'])
        self.add_url_rule('/api/admin/db-ssh-tunnel/status',
              'api_db_ssh_tunnel_status',
              self._api_db_ssh_tunnel_status)
        self.add_url_rule('/api/admin/db-ssh-tunnel/list',
              'api_db_ssh_tunnel_list',
              self._api_db_ssh_tunnel_list)
        self.add_url_rule('/api/admin/db-ssh-tunnel/ssh-hosts',
              'api_db_ssh_tunnel_ssh_hosts',
              self._api_db_ssh_tunnel_ssh_hosts)
        self.add_url_rule('/api/admin/db-ssh-tunnel/save',
              'api_db_ssh_tunnel_save',
              self._api_db_ssh_tunnel_save,
              methods=['POST'])
        self.add_url_rule(
            '/api/admin/db-ssh-tunnel/delete',
            'api_db_ssh_tunnel_delete',
            self._api_db_ssh_tunnel_delete,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/db-ssh-tunnel/ensure',
            'api_db_ssh_tunnel_ensure',
            self._api_db_ssh_tunnel_ensure,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/db-ssh-tunnel/test',
            'api_db_ssh_tunnel_test',
            self._api_db_ssh_tunnel_test,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/db-ssh-tunnel/close',
            'api_db_ssh_tunnel_close',
            self._api_db_ssh_tunnel_close,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/database-setup/local-db/list',
            'api_database_setup_local_db_list',
            self._api_database_setup_local_db_list,
        )
        self.add_url_rule(
            '/api/admin/database-setup/local-db/save',
            'api_database_setup_local_db_save',
            self._api_database_setup_local_db_save,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/database-setup/local-db/delete',
            'api_database_setup_local_db_delete',
            self._api_database_setup_local_db_delete,
            methods=['POST'],
        )
        self.add_url_rule(
            '/api/admin/database-setup/local-db/test',
            'api_database_setup_local_db_test',
            self._api_database_setup_local_db_test,
            methods=['POST'],
        )

        # Admin user DB access API routes
        self.add_url_rule('/api/admin/user-db-access/profiles',
              'api_user_db_access_profiles',
              self._api_user_db_access_profiles)
        self.add_url_rule('/api/admin/user-db-access/details',
              'api_user_db_access_details',
              self._api_user_db_access_details)
        self.add_url_rule('/api/admin/user-db-access/health-check',
              'api_user_db_access_health_check',
              self._api_user_db_access_health_check)
        self.add_url_rule('/api/admin/user-db-access/save',
              'api_user_db_access_save',
              self._api_user_db_access_save,
              methods=['POST'])

        # Async tasks API routes
        self.add_url_rule('/api/admin/async-tasks/list',
                  'api_async_tasks_list',
                  self._api_async_tasks_list)
        self.add_url_rule('/api/admin/async-tasks/global-list',
                  'api_async_tasks_global_list',
                  self._api_async_tasks_global_list)
        self.add_url_rule('/api/admin/async-tasks/task-list',
                  'api_async_tasks_task_list',
                  self._api_async_tasks_task_list)
        self.add_url_rule('/api/admin/async-tasks/save',
                  'api_async_tasks_save',
                  self._api_async_tasks_save,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/delete',
                  'api_async_tasks_delete',
                  self._api_async_tasks_delete,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/reorder',
                  'api_async_tasks_reorder',
                  self._api_async_tasks_reorder,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/toggle',
                  'api_async_tasks_toggle',
                  self._api_async_tasks_toggle,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/run-now',
                  'api_async_tasks_run_now',
                  self._api_async_tasks_run_now,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/run-all',
                  'api_async_tasks_run_all',
                  self._api_async_tasks_run_all,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/stop',
                  'api_async_tasks_stop',
                  self._api_async_tasks_stop,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/clear-history',
              'api_async_tasks_clear_history',
              self._api_async_tasks_clear_history,
              methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/status',
                  'api_async_tasks_status',
                  self._api_async_tasks_status)
        self.add_url_rule('/api/admin/async-tasks/task-log',
                  'api_async_tasks_task_log',
                  self._api_async_tasks_task_log)
        self.add_url_rule('/api/admin/async-tasks/cancel-task',
                  'api_async_tasks_cancel_task',
                  self._api_async_tasks_cancel_task,
                  methods=['POST'])
        self.add_url_rule('/api/admin/async-tasks/read-file',
                  'api_async_tasks_read_file',
                  self._api_async_tasks_read_file)
        self.add_url_rule('/api/admin/async-tasks/download-file',
                  'api_async_tasks_download_file',
                  self._api_async_tasks_download_file)

        # Register every page from pages.yaml
        for page_id, page_def in self.ari_pages.items():
            # Skip login/logout - already registered
            if page_id in ('home.login', 'home.logout'):
                continue
            # External links are nav/cards only and do not map to Flask routes.
            if str(page_def.get('external-url', '') or '').strip():
                continue
            url = page_id_to_url(page_id)
            endpoint = page_id_to_endpoint(page_id)
            self.add_url_rule(
                url, endpoint,
                self._make_page_view(page_id),
            )

        # Dynamic data portal profile sub-pages
        self.add_url_rule('/data_portal/<profile_id>',
                          'ri_profile',
                          self._ri_profile_view)

        # Data portal profile health-check API
        self.add_url_rule('/api/ri/profile-health',
                          'api_ri_profile_health',
                          self._api_ri_profile_health,
                          methods=['POST'])

        # Object table sub-page + data API
        self.add_url_rule('/api/data-portal/profiles',
                          'api_profiles_list',
                          self._api_profiles_list)
        self.add_url_rule('/data_portal/<profile_id>/object-table',
                          'ri_object_table',
                          self._ri_object_table_view)
        self.add_url_rule('/data_portal/<profile_id>/find-object',
                  'ri_find_object',
                  self._ri_find_object_view)
        self.add_url_rule('/api/data-portal/object-table',
                          'api_object_table',
                          self._api_object_table)
        self.add_url_rule('/data_portal/<profile_id>/observation-table',
                  'ri_observation_table',
                  self._ri_obs_table_view)
        self.add_url_rule('/data_portal/<profile_id>/query-db',
                  'ri_query_db',
                  self._ri_query_db_view)
        self.add_url_rule('/data_portal/<profile_id>/qc-graphs',
              'ri_qc_graphs',
              self._ri_qc_graphs_view)
        self.add_url_rule(
            '/data_portal/<profile_id>/qc-graphs/max'
            '/<section>/<metric_key>/<view_key>',
              'ri_qc_graphs_max',
              self._ri_qc_graphs_max_view)
        self.add_url_rule('/api/data-portal/query-db/schema',
                  'api_query_db_schema',
                  self._api_query_db_schema)
        self.add_url_rule('/api/data-portal/query-db/run',
                  'api_query_db_run',
                  self._api_query_db_run,
                  methods=['POST'])
        # Download basket page + APIs (must be before /<path:objname> catch-all)
        self.add_url_rule('/data_portal/<profile_id>/basket',
                          'ri_basket',
                          self._ri_basket_view)
        self.add_url_rule('/api/data-portal/basket',
                          'api_basket_get',
                          self._api_basket_get)
        self.add_url_rule('/api/data-portal/basket/summary',
                          'api_basket_summary',
                          self._api_basket_summary)
        self.add_url_rule('/api/data-portal/basket/add',
                          'api_basket_add',
                          self._api_basket_add,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/remove',
                          'api_basket_remove',
                          self._api_basket_remove,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/clear',
                          'api_basket_clear',
                          self._api_basket_clear,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/compile',
                          'api_basket_compile',
                          self._api_basket_compile,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/compile-status/<job_id>',
                          'api_basket_compile_status',
                          self._api_basket_compile_status)
        self.add_url_rule(
            '/api/data-portal/basket/download/<job_id>/<int:chunk_idx>',
            'api_basket_download',
            self._api_basket_download)
        self.add_url_rule('/api/data-portal/basket/jobs',
                          'api_basket_jobs',
                          self._api_basket_jobs)
        self.add_url_rule('/api/data-portal/basket/jobs/remove',
                  'api_basket_jobs_remove',
                  self._api_basket_jobs_remove,
                  methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/jobs/clear',
                  'api_basket_jobs_clear',
                  self._api_basket_jobs_clear,
                  methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/add-from-ftable',
                          'api_basket_add_from_ftable',
                          self._api_basket_add_from_ftable,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/share-token',
                          'api_basket_share_token',
                          self._api_basket_share_token,
                          methods=['POST'])
        self.add_url_rule('/api/data-portal/basket/share-email',
                          'api_basket_share_email',
                          self._api_basket_share_email,
                          methods=['POST'])
        self.add_url_rule('/share/<token>',
                          'share_landing',
                          self._share_landing)
        self.add_url_rule('/share/<token>/file/<int:chunk_idx>',
                          'share_download',
                          self._share_download)
        self.add_url_rule('/api/data-portal/file-browser',
                          'api_file_browser',
                          self._api_file_browser)

        self.add_url_rule(
            '/data_portal/<profile_id>/object-plot-max/<objname>/<plot_key>',
                          'ri_object_plot_max',
                          self._ri_object_plot_max_view)
        self.add_url_rule('/data_portal/<profile_id>/<path:objname>',
              'ri_object_page',
              self._ri_object_page_view)
        self.add_url_rule('/api/data-portal/object-page',
                'api_object_page',
                self._api_object_page)
        self.add_url_rule('/api/data-portal/object-plots',
                          'api_object_plots',
                          self._api_object_plots)
        self.add_url_rule('/api/data-portal/object-lbl-plots',
                          'api_object_lbl_plots',
                          self._api_object_lbl_plots)
        self.add_url_rule('/api/data-portal/finder-chart',
                          'api_finder_chart',
                          self._api_finder_chart)
        self.add_url_rule('/api/data-portal/debug-plots',
                          'api_debug_plots',
                          self._api_debug_plots)
        self.add_url_rule('/api/data-portal/filename-plot',
                          'api_filename_plot',
                          self._api_filename_plot)
        self.add_url_rule('/api/data-portal/obs-table',
                  'api_obs_table',
                  self._api_obs_table)

    # -----------------------------------------------------------------
    # View factories
    # -----------------------------------------------------------------
    @staticmethod
    def _is_doc_leaf(page_id: str, pages: dict) -> bool:
        """Check if a page is a documentation leaf page."""
        parts = page_id.split('.')
        return (len(parts) >= 3
                and parts[0] == 'home' and parts[1] == 'docs'
                and not is_parent_page(page_id, pages))

    @staticmethod
    def _is_doc_page(page_id: str) -> bool:
        """Check if a page is under the docs section."""
        return page_id.startswith('home.docs')

    def _build_sidebar_context(self, page_id: str, perms, user_info=None):
        """Build sidebar context dict for pages with side-nav top-level."""
        nav_root = find_full_nav_root(page_id, self.ari_pages)
        if not nav_root:
            return {}
        root_def = self.ari_pages[nav_root]
        section_tree = get_sidebar_tree(
            nav_root, perms, self.ari_pages, page_id
        )
        pinned_tree = get_pinned_sidebar_items(
            perms,
            self.ari_pages,
            page_id,
            logged_in=(user_info is not None),
            username=(user_info or {}).get('username', ''),
        )
        seen = set()
        sidebar_tree = []
        for item in pinned_tree + section_tree:
            item_id = item.get('id', '')
            if item_id in seen:
                continue
            seen.add(item_id)
            sidebar_tree.append(item)
        return {
            'sidebar_root': nav_root,
            'sidebar_label': root_def.get('label', ''),
            'sidebar_icon': root_def.get('icon', ''),
            'sidebar_url': page_id_to_url(nav_root),
            'sidebar_tree': sidebar_tree,
        }

    def _build_home_sidebar_context(self, perms, user_info=None):
        """Build sidebar context for the home page using pinned entries."""
        sidebar_tree = get_pinned_sidebar_items(
            perms,
            self.ari_pages,
            'home',
            logged_in=(user_info is not None),
            username=(user_info or {}).get('username', ''),
        )
        if not sidebar_tree:
            return {}
        return {
            'sidebar_root': 'home',
            'sidebar_label': 'Home',
            'sidebar_icon': 'fa-solid fa-house',
            'sidebar_url': '/',
            'sidebar_tree': sidebar_tree,
        }

    def _build_home_page_context(self, user_info, perms) -> dict:
        """Build the full context payload used by the home page."""
        context = {
            'page_id': 'home',
            'page_label': 'Home',
            'page_icon': 'fa-solid fa-house',
            'is_parent': True,
        }
        context.update(self._build_home_sidebar_context(perms, user_info))

        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        instr_info = []
        for inst in all_instr:
            info = params.get(inst.lower(), {})
            instr_info.append({
                'name': inst,
                'homepage': info.get('homepage', ''),
            })
        context['instruments'] = instr_info

        pubs = params.get('publications', {})
        pub_list = []
        for _key, pub in pubs.items():
            pub_list.append({
                'title': pub.get('title', ''),
                'url': pub.get('paper-url', ''),
            })
        context['publications'] = pub_list
        context['cards'] = get_visible_cards(
            'home', perms, self.ari_pages,
            logged_in=(user_info is not None),
        )
        return context

    def _make_page_view(self, page_id: str):
        """Create a view function for a page defined in pages.yaml."""
        page_def = self.ari_pages[page_id]
        view_perm = page_def.get('view-permission', '')
        template = page_id_to_template(page_id, self.ari_pages)
        # A page acts as parent if it has children or uses a subdir template
        is_parent = (is_parent_page(page_id, self.ari_pages)
                     or template.endswith('/index.html'))
        # Check if this is a documentation leaf page
        is_doc = self._is_doc_leaf(page_id, self.ari_pages)

        def view_func():
            user_info = get_effective_user(session)
            if user_info:
                perms = resolve_user_permissions(
                    user_info['groups'], self.ari_groups
                )
            else:
                perms = get_public_permissions()

            if view_perm not in perms:
                flash('You do not have permission to view this page.',
                      'warning')
                return redirect(url_for('login'))

            if page_id.startswith('home.user_portal') and not user_info:
                flash('You must be logged in to access user portal pages.',
                      'warning')
                return redirect(url_for('login'))

            context = {
                'page_id': page_id,
                'page_label': page_def.get('label', ''),
                'page_icon': page_def.get('icon', ''),
                'is_parent': is_parent,
            }

            # Sidebar context for side-nav top-level sections
            nav_root = find_full_nav_root(page_id, self.ari_pages)
            if nav_root:
                context.update(self._build_sidebar_context(page_id, perms,
                                                          user_info))
                # Version info only for documentation pages
                if self._is_doc_page(page_id):
                    version = request.args.get('v')
                    context['doc_versions'] = get_versions()
                    context['current_version'] = (
                        version or get_default_version()
                    )

            if is_parent:
                context['cards'] = get_visible_cards(
                    page_id, perms, self.ari_pages,
                    logged_in=(user_info is not None),
                )

            # Documentation leaf pages: inject markdown content
            if is_doc:
                version = context.get('current_version')
                raw, html, current_ver = get_doc_content(
                    page_id, version
                )
                # Short ref for permissions and URL routes
                doc_short = page_id.split('.')[-1]
                context.update({
                    'doc_html': html,
                    'doc_raw': raw,
                    'current_version': current_ver,
                    'can_edit': f'edit.doc.{doc_short}' in perms,
                    'doc_ref': doc_short,
                })
                return render_template('docs/doc_page.html', **context)

            # Home page: inject instruments + publications
            if page_id == 'home':
                context.update(self._build_home_page_context(user_info, perms))

            # Science groups page: inject user's instruments
            if page_id == 'home.admin_portal.science_groups' and user_info:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                user_instr = user_info.get('instruments', [])
                # Filter to instruments the user has
                context['instruments'] = [
                    i for i in all_instr if i in user_instr
                ]

            # Async tasks page: inject instruments
            if page_id == 'home.admin_portal.async_tasks' and user_info:
                params = load_parameters()
                instruments_entry = params.get('instruments', {})
                if isinstance(instruments_entry, dict):
                    all_instr = instruments_entry.get('value', [])
                elif isinstance(instruments_entry, list):
                    all_instr = instruments_entry
                else:
                    all_instr = []
                context['instruments'] = (all_instr
                                           if isinstance(all_instr, list)
                                           else [])

            # APERO profiles page: inject instruments + groups meta
            if page_id == 'home.admin_portal.apero_profiles' and user_info:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                context['instruments'] = all_instr
                all_groups = list(self.ari_groups.keys())
                can_manage = sorted(
                    g for g in all_groups
                    if f'manage.group.{g}' in perms
                )
                inherited_map = {}
                for g in all_groups:
                    inherited_map[g] = sorted(
                        get_inherited_groups(g, self.ari_groups)
                    )
                context['all_groups'] = all_groups
                context['can_manage_groups'] = can_manage
                context['inherited_map'] = inherited_map
                # Load instrument profile presets from aprofile_instruments/
                _sci_profiles = {}
                _sci_dir = PACKAGE_DIR / 'resources' / 'aprofile_instruments'
                if _sci_dir.is_dir():
                    for _yf in sorted(_sci_dir.glob('*.yaml')):
                        try:
                            with open(_yf, encoding='utf-8') as _f:
                                _yd = yaml.safe_load(_f) or {}
                            _gen = _yd.get('general', {})
                            _sf = str(_gen.get('science_fiber', '')).strip()
                            _st = _gen.get('science_types', [])
                            if not isinstance(_st, list):
                                _st = [str(_st)] if _st else []
                            _sci_profiles[_yf.name] = {
                                'science_fiber': _sf,
                                'science_types': _st,
                                'params': _yd,
                            }
                        except Exception:
                            pass
                context['sci_profiles'] = _sci_profiles

            # User DB access page: inject current health summary
            if page_id == 'home.admin_portal.user_db_access' and user_info:
                health, _, _ = self._get_admin_health(
                    user_info=user_info,
                    perms=perms,
                    force=False,
                    allow_async_refresh=True,
                )
                context['user_db_access_health'] = health.get(
                    'home.admin_portal.user_db_access',
                    {
                        'status': 'info',
                        'message': ('Configure group and column access to '
                                    'APERO database tables by profile.'),
                    },
                )
                try:
                    context['user_db_access_health_report'] = (
                        self._build_user_db_access_health_report(user_info)
                    )
                except Exception:
                    context['user_db_access_health_report'] = {
                        'status': 'error',
                        'message': 'User DB access health check failed.',
                        'checked_profiles': 0,
                        'warning_profiles': 0,
                        'profiles': [],
                    }

            # Data portal: inject accessible profiles
            if page_id == 'home.data_portal':
                db_ctx = self._build_ri_context(user_info, perms)
                context.update(db_ctx)
                
            # User portal data access summary
            if page_id == 'home.user_portal.data_access' and user_info:
                context.update(self._build_user_data_access_context(user_info))

            # User portal support contacts
            if page_id == 'home.user_portal.support' and user_info:
                context.update(self._build_user_support_context(user_info))

            # User portal links
            if page_id == 'home.user_portal.links' and user_info:
                context.update(self._build_user_links_context(user_info))

            # User portal notes
            if page_id == 'home.user_portal.notes' and user_info:
                context['notes'] = ud.load_notes(user_info['username'])

            # User portal calendar
            if page_id == 'home.user_portal.calendar' and user_info:
                context.update(self._build_user_calendar_context(user_info))

            # User portal todo
            if page_id == 'home.user_portal.todo' and user_info:
                context['todo_items'] = ud.list_todo_items(
                    user_info['username'])

            # User portal API access
            if page_id == 'home.user_portal.api_access' and user_info:
                context.update(
                    self._build_user_api_access_context(user_info))

            # Admin calendar
            if page_id == 'home.admin_portal.calendar' and user_info:
                context.update(
                    self._build_admin_instrument_context(user_info, perms))

            # Admin links
            if page_id == 'home.admin_portal.links' and user_info:
                context.update(
                    self._build_admin_instrument_context(user_info, perms))

            # Admin email settings
            if page_id == 'home.admin_portal.email':
                context.update(self._build_admin_email_context(perms))

            # Admin cloud backup settings
            if page_id == 'home.admin_portal.backup_settings':
                context.update(self._build_admin_backup_context(perms))

            # Admin SSHFS management
            if page_id == 'home.admin_portal.sshfs_management':
                context.update(self._build_admin_sshfs_context(perms))

            # Admin DB SSH tunnel management
            if page_id == 'home.admin_portal.database_setup':
                context.update(
                    self._build_admin_db_tunnel_context(user_info, perms)
                )

            # Admin plot cache
            if page_id == 'home.admin_portal.cache_settings':
                context.update(self._build_admin_cache_context(perms))

            # Admin download management
            if page_id == 'home.admin_portal.download_management':
                context.update(
                    self._build_admin_download_mgmt_context(perms))

            # Admin index and health-status page: inject health context
            if page_id in {'home.admin_portal',
                          'home.admin_portal.health_status'}:
                health, updated_at, in_progress = self._get_admin_health(
                    user_info=user_info,
                    perms=perms,
                    force=False,
                    allow_async_refresh=True,
                )
                if page_id == 'home.admin_portal':
                    context['card_health'] = health
                context['admin_health_rows'] = self._build_admin_health_rows(
                    health
                )
                context['admin_health_meta'] = {
                    'updated_at': self._format_utc_datetime(updated_at),
                    'in_progress': in_progress,
                    'refresh_url': url_for('api_admin_health_update'),
                }
                context['admin_health_config'] = load_admin_health_config()
                context['admin_health_config_urls'] = {
                    'get': url_for('api_admin_health_config_get'),
                    'save': url_for('api_admin_health_config_save'),
                }

            return render_template(template, **context)

        # Give the function a unique name for Flask
        view_func.__name__ = page_id_to_endpoint(page_id)
        return view_func

    # -----------------------------------------------------------------
    # Data portal helpers
    # -----------------------------------------------------------------
    # Consistent colour palette for instrument identification
    _INSTRUMENT_PALETTE = [
        {'bg': '#e3f2fd', 'text': '#1565c0', 'border': '#90caf9'},
        {'bg': '#e8f5e9', 'text': '#2e7d32', 'border': '#a5d6a7'},
        {'bg': '#fff3e0', 'text': '#e65100', 'border': '#ffcc80'},
        {'bg': '#f3e5f5', 'text': '#6a1b9a', 'border': '#ce93d8'},
        {'bg': '#ffebee', 'text': '#c62828', 'border': '#ef9a9a'},
        {'bg': '#e0f2f1', 'text': '#00695c', 'border': '#80cbc4'},
        {'bg': '#fff8e1', 'text': '#f57f17', 'border': '#ffe082'},
        {'bg': '#e8eaf6', 'text': '#283593', 'border': '#9fa8da'},
    ]

    def _instrument_colors(self):
        """Map each instrument to a palette entry (stable ordering)."""
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        palette = self._INSTRUMENT_PALETTE
        return {inst: palette[i % len(palette)]
                for i, inst in enumerate(all_instr)}

    @staticmethod
    def _get_instrument_run_ids(instrument):
        """Return sorted list of all unique run_ids from object table JSONs.
        
        Only scans profiles that currently exist in apero_profiles to avoid
        picking up orphaned task files from deleted profiles.
        """
        import json as _json
        from apero_ri.core.auth import ARI_DIR, load_apero_profiles
        
        # Get current profiles; only scan their task files
        all_profiles = load_apero_profiles(hydrate=False)
        current_profile_names = set()
        if instrument in all_profiles:
            inst_profiles = all_profiles[instrument]
            if isinstance(inst_profiles, dict):
                current_profile_names = set(inst_profiles.keys())
        
        tasks_dir = ARI_DIR / 'tasks' / instrument
        run_ids = set()
        if tasks_dir.exists():
            # New layout: tasks/<instrument>/<apero_profile>/object_table.json
            # Only scan directories that correspond to current profiles
            for profile_dir in tasks_dir.iterdir():
                if not profile_dir.is_dir():
                    continue
                profile_name = profile_dir.name
                if profile_name not in current_profile_names:
                    continue  # Skip orphaned profile dirs
                jf = profile_dir / 'object_table.json'
                if jf.exists():
                    try:
                        with open(jf, encoding='utf-8') as f:
                            data = _json.load(f)
                        for row in data.get('rows', []):
                            raw = str(row.get('RUN_ID', '') or '')
                            for rid in raw.split(','):
                                rid = rid.strip()
                                if rid:
                                    run_ids.add(rid)
                    except Exception:
                        pass
            
            # Legacy layout: tasks/<instrument>/object_table_<profile>.json
            # Check these only if they correspond to current profiles
            for jf in tasks_dir.glob('object_table_*.json'):
                # Extract profile name from filename (object_table_<profile>.json)
                fname = jf.name
                if fname.startswith('object_table_') and fname.endswith('.json'):
                    profile_name = fname[len('object_table_'):-len('.json')]
                    if profile_name not in current_profile_names:
                        continue  # Skip orphaned legacy files
                    try:
                        with open(jf, encoding='utf-8') as f:
                            data = _json.load(f)
                        for row in data.get('rows', []):
                            raw = str(row.get('RUN_ID', '') or '')
                            for rid in raw.split(','):
                                rid = rid.strip()
                                if rid:
                                    run_ids.add(rid)
                    except Exception:
                        pass
        return sorted(run_ids)

    @staticmethod
    def _is_all_science_group(name: str) -> bool:
        """Return True when a science-group name refers to the reserved All group."""
        return str(name or '').strip().lower() == 'all'

    def _sync_all_science_group(self, instrument: str,
                                groups: Optional[dict] = None,
                                run_ids: Optional[list] = None,
                                persist: bool = True):
        """Ensure the reserved All science group exists and mirrors instrument run IDs."""
        if groups is None:
            groups = load_science_groups(instrument)
        if not isinstance(groups, dict):
            groups = {}

        if run_ids is None:
            run_ids = self._get_instrument_run_ids(instrument)
        normalized_run_ids = sorted({
            str(rid).strip() for rid in run_ids if str(rid).strip()
        })

        changed = False
        canonical_name = 'All'
        all_entry = groups.get(canonical_name)
        if not isinstance(all_entry, dict):
            all_entry = {}
            changed = True

        # Merge any legacy/case-variant "all" group names into canonical "All".
        for gname in list(groups.keys()):
            if gname == canonical_name:
                continue
            if self._is_all_science_group(gname):
                legacy_entry = groups.pop(gname)
                if isinstance(legacy_entry, dict):
                    legacy_users = legacy_entry.get('users', [])
                    if isinstance(legacy_users, list) and 'users' not in all_entry:
                        all_entry['users'] = legacy_users
                changed = True

        users = all_entry.get('users', [])
        if not isinstance(users, list):
            users = []
            changed = True

        desired_all = {
            'run_ids': normalized_run_ids,
            'users': users,
        }
        if groups.get(canonical_name) != desired_all:
            groups[canonical_name] = desired_all
            changed = True

        if changed and persist:
            save_science_groups(instrument, groups)

        return groups, normalized_run_ids

    def _get_user_accessible_run_ids(self, user_info, instrument):
        """Return set of run_ids the user may see for this instrument.

        Users only see run_ids from science groups where they are listed.
        An empty set means they should see no rows.
        """
        if user_info is None:
            return set()
        username = user_info.get('username', '')
        groups = load_science_groups(instrument)
        accessible = set()
        for group_data in groups.values():
            if username in group_data.get('users', []):
                for rid in group_data.get('run_ids', []):
                    if rid:
                        accessible.add(str(rid).strip())
        return accessible

    def _page_template_meta(self, template_id: str, **tokens) -> dict:
        """Resolve label/icon from a dynamic page template in pages.yaml."""
        template = self._page_templates.get(template_id, {})
        label = str(template.get('label', ''))
        for key, value in tokens.items():
            value_str = str(value)
            label = label.replace(f'{{{key}}}', value_str)
            label = label.replace(f'{{{key.replace("_", " ")}}}', value_str)
        return {
            'label': label,
            'icon': template.get('icon', ''),
        }

    def _build_data_portal_sidebar_tree(self,
                                        accessible_profiles: list,
                                        active_page_id: str,
                                        user_permissions,
                                        user_info=None,
                                        current_profile_id: Optional[str] = None,
                                        objname: Optional[str] = None,
                                        include_children: bool = True) -> list:
        """Build data portal sidebar tree from pages.yaml templates."""
        sidebar_tree = []
        pinned_tree = get_pinned_sidebar_items(
            user_permissions,
            self.ari_pages,
            active_page_id,
            logged_in=(user_info is not None),
            username=(user_info or {}).get('username', ''),
        )
        sidebar_tree.extend(pinned_tree)
        for prof in accessible_profiles:
            profile_id = prof['profile_id']
            page_id = f'home.data_portal.{profile_id}'
            profile_meta = self._page_template_meta(
                'home.data_portal.{apero_profile}',
                apero_profile=profile_id,
            )
            is_current = (profile_id == current_profile_id)
            sidebar_tree.append({
                'id': page_id,
                'label': profile_meta.get('label') or profile_id,
                'icon': profile_meta.get('icon') or 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{profile_id}',
                'depth': 0,
                'active': active_page_id == page_id,
                'expanded': is_current,
                'has_children': include_children,
            })

            if not include_children or not is_current:
                continue

            # Build child items in pages.yaml definition order so that
            # reordering pages.yaml automatically updates the sidebar.
            _child_url_map = {
                'object_table': (f'/data_portal/{profile_id}/object-table', False),
                'obs_table':    (f'/data_portal/{profile_id}/observation-table', False),
                'query_db':     (f'/data_portal/{profile_id}/query-db', False),
                'qc_graphs':    (f'/data_portal/{profile_id}/qc-graphs', False),
                'basket':       (f'/data_portal/{profile_id}/basket', False),
            }
            child_items = []
            for tpl_key, tpl_def in self._page_templates.items():
                if not isinstance(tpl_def, dict):
                    continue
                if tpl_def.get('parent') != 'home.data_portal.{apero_profile}':
                    continue
                suffix = tpl_key.split('.')[-1]
                if '{' in suffix:  # skip {objname} template entries
                    continue
                child_url, disabled = _child_url_map.get(suffix, ('', False))
                child_items.append((suffix, tpl_key, child_url, disabled))

            for suffix, tpl_id, child_url, disabled in child_items:
                child_id = f'{page_id}.{suffix}'
                child_meta = self._page_template_meta(
                    tpl_id,
                    apero_profile=profile_id,
                )
                sidebar_tree.append({
                    'id': child_id,
                    'label': child_meta.get('label') or suffix,
                    'icon': child_meta.get('icon', ''),
                    'url': child_url,
                    'depth': 1,
                    'active': active_page_id == child_id,
                    'disabled': disabled,
                })

            if objname:
                obj_id = f'{page_id}.{objname}'
                obj_meta = self._page_template_meta(
                    'home.data_portal.{apero_profile}.{objname}',
                    apero_profile=profile_id,
                    objname=objname,
                )
                sidebar_tree.append({
                    'id': obj_id,
                    'label': f'Object Page: {objname}',
                    'icon': obj_meta.get('icon') or 'fa-solid fa-star',
                    'url': f'/data_portal/{profile_id}/{objname}',
                    'depth': 1,
                    'active': active_page_id == obj_id,
                })

        seen = set()
        deduped_tree = []
        for item in sidebar_tree:
            item_id = item.get('id', '')
            if item_id in seen:
                continue
            seen.add(item_id)
            deduped_tree.append(item)
        return deduped_tree

    def _build_ri_context(self, user_info, user_permissions):
        """Build template context for the data portal page."""
        params = load_parameters()
        all_instruments = params.get('instruments', {}).get('value', [])
        colors = self._instrument_colors()
        accessible = get_accessible_profiles(user_info, self.ari_groups)

        # Determine which instruments to show based on user's list
        user_instruments = (
            user_info.get('instruments', []) if user_info else []
        )
        if user_instruments:
            shown = [i for i in all_instruments if i in user_instruments]
        else:
            shown = list(all_instruments)

        # Build profile cards
        profile_cards = []
        for prof in accessible:
            color = colors.get(prof['instrument'],
                               self._INSTRUMENT_PALETTE[0])
            profile_cards.append({
                'instrument': prof['instrument'],
                'profile_id': prof['profile_id'],
                'url': f'/data_portal/{prof["profile_id"]}',
                'color': color,
                'apero_version': prof['data'].get('apero_version', ''),
                'reduction_server': prof['data'].get(
                    'reduction_server', ''),
            })

        instruments_with = {p['instrument'] for p in accessible}
        no_profile = [i for i in shown if i not in instruments_with]

        # Sidebar listing all accessible APERO profiles from pages templates
        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id='home.data_portal',
            user_permissions=user_permissions,
            user_info=user_info,
            include_children=False,
        )

        return {
            'profile_cards': profile_cards,
            'shown_instruments': shown,
            'instrument_colors': colors,
            'no_profile_instruments': no_profile,
            'sidebar_tree': sidebar_tree,
        }

    def _build_user_data_access_context(self, user_info):
        """Build summary of user's data access by instrument."""
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = set(user_info.get('instruments', []))
        if user_instr:
            instruments = [i for i in all_instr if i in user_instr]
        else:
            instruments = list(all_instr)

        username = user_info.get('username', '')
        accessible_profiles = get_accessible_profiles(
            user_info,
            self.ari_groups)
        profiles_by_inst = {}
        for prof in accessible_profiles:
            profiles_by_inst.setdefault(prof['instrument'], []).append(
                prof['profile_id']
            )
        for inst in profiles_by_inst:
            profiles_by_inst[inst] = sorted(profiles_by_inst[inst])

        access_rows = []
        for inst in instruments:
            groups = load_science_groups(inst)
            member_groups = []
            run_ids = set()
            for gname, gdata in groups.items():
                if username in gdata.get('users', []):
                    member_groups.append(gname)
                    for rid in gdata.get('run_ids', []):
                        rid_s = str(rid).strip()
                        if rid_s:
                            run_ids.add(rid_s)

            access_rows.append({
                'instrument': inst,
                'profiles': profiles_by_inst.get(inst, []),
                'science_groups': sorted(member_groups),
                'run_ids': sorted(run_ids),
            })

        return {
            'data_access': access_rows,
        }

    def _build_user_support_context(self, user_info):
        """Build support contact lists grouped by instrument and role."""
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = set(user_info.get('instruments', []))
        if user_instr:
            instruments = [i for i in all_instr if i in user_instr]
        else:
            instruments = list(all_instr)

        users = load_users()
        role_order = ['admin', 'moderator', 'developer', 'monitor']
        role_to_key = {
            'admin': 'admins',
            'moderator': 'moderators',
            'developer': 'developers',
            'monitor': 'monitors',
        }

        support_rows = []
        for inst in instruments:
            grouped = {
                'admins': [],
                'moderators': [],
                'developers': [],
                'monitors': [],
            }

            for username, user_data in users.items():
                # Strict instrument scoping: only show support contacts
                # explicitly assigned to this instrument.
                u_instr = user_data.get('instruments', [])
                if isinstance(u_instr, str):
                    u_instr = [u_instr]
                u_instr = [str(val).strip()
                    for val in (u_instr or [])
                    if str(val).strip()]
                if inst not in u_instr:
                    continue

                direct_groups = set(user_data.get('groups', []))
                all_groups = set(direct_groups)
                for group_name in list(direct_groups):
                    all_groups |= get_inherited_groups(group_name,
                                                       self.ari_groups)

                role_name = None
                for candidate in role_order:
                    if candidate in all_groups:
                        role_name = candidate
                        break
                if role_name is None:
                    continue

                first_names = str(user_data.get('first_names', '')).strip()
                last_name = str(user_data.get('last_name', '')).strip()
                full_name = f'{first_names} {last_name}'.strip()
                if not full_name:
                    full_name = username

                grouped[role_to_key[role_name]].append({
                    'username': username,
                    'full_name': full_name,
                    'email': str(user_data.get('primary_email', '')).strip(),
                })

            for key in grouped:
                grouped[key].sort(key=lambda item: item['username'].lower())

            support_rows.append({
                'instrument': inst,
                **grouped,
            })

        return {
            'support_by_instrument': support_rows,
            'support_email': eb.get_support_email(),
        }

    def _build_user_links_context(self, user_info):
        """Build context for user links page."""
        username = user_info['username']
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = user_info.get('instruments', [])
        instruments = (
            [i for i in all_instr if i in user_instr]
            or list(all_instr))
        links_data = ud.load_links(username)
        instr_links = {
            i: ud.load_instrument_links(i) for i in instruments
        }
        return {
            'links_data': links_data,
            'instr_links': instr_links,
            'instruments': instruments,
        }

    def _build_user_api_access_context(self, user_info):
        """Build context for user API access page."""
        username = user_info['username']
        api_usage = dt.get_user_usage(username, 'api')
        basket_usage = dt.get_user_usage(username, 'basket')
        token_info = at.get_user_token_info(username)

        def _fmt_ts(raw):
            """Format an ISO timestamp to a compact, human-friendly form."""
            if not raw:
                return 'Never'
            try:
                from datetime import datetime as _dt, timezone as _tz
                ts = _dt.fromisoformat(raw)
                return ts.strftime('%d %b %Y, %H:%M UTC')
            except Exception:
                return str(raw)[:19]

        return {
            'token_info': token_info,
            'api_usage': {
                'total_bytes': api_usage.get('total_bytes', 0),
                'total_files': api_usage.get('total_files', 0),
                'total_size_fmt': dt.format_bytes(
                    api_usage.get('total_bytes', 0)),
                'last_download': _fmt_ts(
                    api_usage.get('last_download_at', '')),
            },
            'basket_usage': {
                'total_bytes': basket_usage.get('total_bytes', 0),
                'total_files': basket_usage.get('total_files', 0),
                'total_size_fmt': dt.format_bytes(
                    basket_usage.get('total_bytes', 0)),
                'last_download': _fmt_ts(
                    basket_usage.get('last_download_at', '')),
            },
        }

    def _build_user_calendar_context(self, user_info):
        """Build context for user calendar page."""
        username = user_info['username']
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = user_info.get('instruments', [])
        instruments = (
            [i for i in all_instr if i in user_instr]
            or list(all_instr))
        events = ud.list_events(username)
        instr_events = {}
        for i in instruments:
            instr_events[i] = ud.load_instrument_calendar(i).get('events', [])
        user_tz = ud.get_user_timezone(username)
        return {
            'events': events,
            'instr_events': instr_events,
            'instruments': instruments,
            'user_timezone': user_tz,
        }

    def _build_admin_instrument_context(self, user_info, perms):
        """Build instruments context for admin calendar/links pages."""
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = user_info.get('instruments', [])
        instruments = (
            [i for i in all_instr if i in user_instr]
            or list(all_instr))
        can_manage = ('manage.admin.calendar' in perms
                      or 'manage.admin.links' in perms)
        return {
            'instruments': instruments,
            'can_manage': can_manage,
        }

    def _build_admin_email_context(self, perms):
        """Build context for the admin email settings page."""
        import json as _json
        cfg = eb.load_email_config()
        providers = eb.PROVIDER_DEFAULTS
        current_provider = cfg.get('provider', 'log')
        # Ensure current is valid
        if current_provider not in providers:
            current_provider = 'log'
        return {
            'email_cfg': cfg,
            'providers': providers,
            'providers_json': _json.dumps(providers),
            'current_provider': current_provider,
            'can_manage': 'manage.admin.email' in perms,
        }

    @staticmethod
    def _resolve_local_data_dir() -> Path:
        """Resolve configured LOCAL_DATA_DIR, falling back to ARI_DIR."""
        params = load_parameters() or {}
        local_data = params.get('LOCAL_DATA_DIR', '')
        if isinstance(local_data, dict):
            local_data = local_data.get('value', '')
        local_data = str(local_data or '').strip()
        if local_data:
            return Path(local_data).expanduser().resolve()
        return Path(
            os.environ.get('ARI_DIR',
                         str(Path.home() / '.ari'))
        ).expanduser().resolve()

    def _build_admin_backup_context(self, perms):
        """Build context for admin backup settings page."""
        import json as _json
        cfg = bb.load_backup_config()
        providers = bb.PROVIDER_DEFAULTS
        current_provider = str(cfg.get('provider', 'local_only')).strip()
        if current_provider not in providers:
            current_provider = 'local_only'

        local_data_dir = self._resolve_local_data_dir()
        inventory = bb.backup_inventory(local_data_dir=local_data_dir,
                        cfg=cfg,
                        method_id=cfg.get('active_method_id'))

        return {
            'backup_cfg': cfg,
            'providers': providers,
            'providers_json': _json.dumps(providers),
            'current_provider': current_provider,
            'can_manage': 'manage.admin.backup' in perms,
            'backup_inventory': inventory,
        }

    def _build_admin_sshfs_context(self, perms):
        """Build context for admin SSHFS management page."""
        # Keep initial page render fast.  Live mount checks can be slow on
        # stale/broken SSHFS targets, so we only preload static config here
        # and let the page fetch live status asynchronously via API.
        try:
            cfg = sb.load_sshfs_config()
            mounts_data = cfg.get('mounts', []) if isinstance(cfg, dict) else []
            if not isinstance(mounts_data, list):
                mounts_data = []
        except Exception:
            mounts_data = []

        try:
            ssh_keys = sb.list_ssh_keys()
            ssh_keys_data = ssh_keys.get('keys', []) if isinstance(ssh_keys, dict) else []
            if not isinstance(ssh_keys_data, list):
                ssh_keys_data = []
        except Exception:
            ssh_keys_data = []

        return {
            'can_manage': 'manage.admin.sshfs' in perms or 'view.admin' in perms,
            'mounts_data': mounts_data,
            'ssh_keys_data': ssh_keys_data,
        }

    @staticmethod
    def _normalize_db_source(value: str) -> str:
        """Normalize database source mode for profile UI/runtime."""
        raw = str(value or '').strip().lower()
        return 'db_ssh_tunnel' if raw in {'db_ssh_tunnel', 'ssh', 'tunnel'} else 'local'

    def _load_db_tunnel_definitions(self) -> dict:
        """Load named DB SSH tunnel definitions."""
        data = load_db_tunnels()
        tunnels = data.get('tunnels', {}) if isinstance(data, dict) else {}
        return tunnels if isinstance(tunnels, dict) else {}

    def _save_db_tunnel_definitions(self, tunnels: dict) -> None:
        """Persist named DB SSH tunnel definitions."""
        existing = load_db_tunnels()
        payload = {
            'tunnels': tunnels if isinstance(tunnels, dict) else {},
            'local_databases': existing.get('local_databases', {})
            if isinstance(existing, dict) else {},
        }
        save_db_tunnels(payload)

    def _load_local_db_definitions(self) -> dict:
        """Load named local database definitions."""
        data = load_db_tunnels()
        local_db = data.get('local_databases', {}) if isinstance(data, dict) else {}
        return local_db if isinstance(local_db, dict) else {}

    def _save_local_db_definitions(self, local_databases: dict) -> None:
        """Persist named local database definitions."""
        existing = load_db_tunnels()
        payload = {
            'tunnels': existing.get('tunnels', {}) if isinstance(existing, dict) else {},
            'local_databases': local_databases if isinstance(local_databases, dict) else {},
        }
        save_db_tunnels(payload)

    def _build_db_tunnel_runtime_params(self, tunnel_name: str,
                                        tunnel_def: dict,
                                        mode: str = 'mysql+pymysql') -> dict:
        """Build apero_async-compatible params for one tunnel definition."""
        _ = tunnel_name
        tdef = tunnel_def if isinstance(tunnel_def, dict) else {}
        remote_host = str(tdef.get('remote_host', '') or '').strip()
        remote_port = str(tdef.get('remote_port', '') or '').strip() or '3306'
        local_port = str(tdef.get('local_port', '') or '').strip()
        ssh_host = str(tdef.get('ssh_config_host', '') or '').strip()
        return {
            'DATABASE_MODE': str(mode or 'mysql+pymysql').strip() or 'mysql+pymysql',
            'DATABASE_HOST': remote_host,
            'DATABASE_PORT': local_port,
            'DATABASE_USER': '',
            'DATABASE_USERNAME': '',
            'DATABASE_PASSWORD': '',
            'DATABASE_NAME': '',
            'DATABASE_USE_SSH_TUNNEL': True,
            'DATABASE_SSH_CONFIG_HOST': ssh_host,
            'DATABASE_SSH_LOCAL_PORT': local_port,
            'DATABASE_SSH_REMOTE_PORT': remote_port,
            # DB setup management supports multiple simultaneously active
            # tunnels; do not force-close other definitions for this path.
            'DATABASE_SSH_ALLOW_MULTIPLE': True,
            'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
        }

    @staticmethod
    def _list_ssh_config_hosts() -> List[str]:
        """Return host aliases from ~/.ssh/config (excluding wildcards)."""
        cfg_path = Path.home() / '.ssh' / 'config'
        if not cfg_path.exists() or not cfg_path.is_file():
            return []

        hosts: set = set()
        try:
            with open(cfg_path, 'r', encoding='utf-8', errors='replace') as fobj:
                for raw_line in fobj:
                    line = str(raw_line).strip()
                    if not line or line.startswith('#'):
                        continue
                    if not line.lower().startswith('host '):
                        continue
                    parts = line.split()[1:]
                    for token in parts:
                        tval = str(token or '').strip()
                        if not tval:
                            continue
                        if any(ch in tval for ch in ['*', '?', '!']):
                            continue
                        hosts.add(tval)
        except Exception:
            return []

        return sorted(hosts)

    def _list_db_tunnel_rows(self) -> List[dict]:
        """List DB tunnel definitions with live health details."""
        tunnels = self._load_db_tunnel_definitions()
        rows = []
        for name in sorted(tunnels.keys()):
            tunnel_def = tunnels.get(name, {})
            params = self._build_db_tunnel_runtime_params(name, tunnel_def)
            ssh_host = str(params.get('DATABASE_SSH_CONFIG_HOST', '') or '')
            remote_host = str(params.get('DATABASE_HOST', '') or '')
            local_port = str(params.get('DATABASE_SSH_LOCAL_PORT', '') or '')
            valid = bool(name and ssh_host and remote_host and local_port)

            status = {
                'active': False,
                'control_alive': False,
                'local_port_open': False,
                'local_host': '127.0.0.1',
                'local_port': local_port,
                'ssh_host': ssh_host,
                'remote_host': remote_host,
                'remote_port': str(params.get('DATABASE_SSH_REMOTE_PORT', '') or ''),
                'created_at': '',
            }
            err = ''
            if valid:
                try:
                    status = apero_async.get_db_tunnel_status(params)
                except Exception as exc:
                    err = str(exc)
            else:
                err = ('Tunnel definition is incomplete. '
                       'Require name, ssh_config_host, remote_host, local_port.')

            rows.append({
                'name': name,
                'definition': tunnel_def,
                'valid_config': valid,
                'config_error': err if not valid else '',
                'status': status,
                'error': err if valid else '',
            })

        return rows

    def _resolve_tunnel_name_from_profile_cfg(self, cfg: dict) -> str:
        """Resolve selected tunnel name from profile database settings."""
        return str(self._profile_get_db(cfg, 'DATABASE_TUNNEL_NAME', '') or '').strip()

    def _resolve_local_db_name_from_profile_cfg(self, cfg: dict) -> str:
        """Resolve selected local database definition name from profile settings."""
        return str(self._profile_get_db(cfg, 'DATABASE_LOCAL_NAME', '') or '').strip()

    def _build_admin_db_tunnel_context(self, user_info, perms):
        """Build context for DB setup page."""
        _ = user_info
        tunnel_rows = self._list_db_tunnel_rows()
        local_db = self._load_local_db_definitions()
        return {
            'can_manage_db_tunnel': 'manage.apero_profile' in (perms or set()),
            'db_tunnels': [row.get('name', '') for row in tunnel_rows],
            'db_local_databases': sorted(local_db.keys()),
        }

    def _build_admin_cache_context(self, perms):
        """Build context for admin plot-cache settings page."""
        from apero_ri.core.plot_cache import (
            load_cache_config, cache_inventory, CACHE_SECTIONS,
        )
        data_dir = self._resolve_local_data_dir()
        cfg = load_cache_config(data_dir)
        inv = cache_inventory(data_dir)

        # Aggregate per-plot timing stats from cached object_plots payloads.
        # Each cache file stores payload.server_timings_ms from API generation.
        cache_root = Path(inv.get('cache_dir', '') or '')
        for prof in inv.get('profiles', []):
            instrument = str(prof.get('instrument', '') or '').strip()
            profile_id = str(prof.get('profile_id', '') or '').strip()
            timing_rows = {}
            if instrument and profile_id and cache_root:
                section_dir = cache_root / instrument / profile_id / 'object_plots'
                if section_dir.exists():
                    for cfile in section_dir.glob('*.json'):
                        try:
                            with open(cfile, 'r', encoding='utf-8') as fh:
                                entry = json.load(fh)
                            payload = (entry or {}).get('payload', {})
                            timings = payload.get('server_timings_ms', {})
                            if not isinstance(timings, dict):
                                continue
                            for plot_name, value in timings.items():
                                try:
                                    ms = float(value)
                                except Exception:
                                    continue
                                timing_rows.setdefault(str(plot_name), []).append(ms)
                        except Exception:
                            continue

            prof['timing_stats'] = []
            for plot_name in sorted(timing_rows.keys()):
                values = timing_rows.get(plot_name, [])
                if not values:
                    continue
                count = len(values)
                vmin = min(values)
                vmax = max(values)
                vmean = sum(values) / count
                prof['timing_stats'].append({
                    'plot': plot_name,
                    'count': count,
                    'min_ms': round(vmin, 2),
                    'mean_ms': round(vmean, 2),
                    'max_ms': round(vmax, 2),
                })

        return {
            'can_manage': 'view.admin' in perms,
            'cache_cfg': cfg,
            'cache_inventory': inv,
            'cache_sections': CACHE_SECTIONS,
        }

    def _api_admin_cache_save(self):
        """Save cache settings (enable/disable, directory)."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups)
        else:
            perms = get_public_permissions()
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401
        from apero_ri.core.plot_cache import (
            load_cache_config, save_cache_config,
        )
        data_dir = self._resolve_local_data_dir()
        body = request.get_json(silent=True) or {}
        cfg = load_cache_config(data_dir)
        if 'enabled' in body:
            cfg['enabled'] = bool(body['enabled'])
        if 'cache_dir' in body:
            cfg['cache_dir'] = str(body['cache_dir']).strip()
        save_cache_config(cfg, data_dir)
        return jsonify(success=True)

    def _api_admin_cache_purge(self):
        """Purge cached data (all or per-profile)."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups)
        else:
            perms = get_public_permissions()
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401
        from apero_ri.core.plot_cache import (
            resolve_cache_root, invalidate_all, invalidate_profile,
            load_cache_config,
        )
        data_dir = self._resolve_local_data_dir()
        cfg = load_cache_config(data_dir)
        cache_root = resolve_cache_root(data_dir, cfg)
        body = request.get_json(silent=True) or {}
        scope = str(body.get('scope', 'all')).strip()
        if scope == 'section':
            instrument = str(body.get('instrument', '')).strip()
            profile_id = str(body.get('profile_id', '')).strip()
            section = str(body.get('section', '')).strip()
            if not instrument or not profile_id or not section:
                return jsonify(success=False,
                               error='Missing instrument, profile_id, or section'), 400
            removed = invalidate_profile(cache_root, instrument, profile_id,
                                         sections=[section])
        elif scope == 'profile':
            instrument = str(body.get('instrument', '')).strip()
            profile_id = str(body.get('profile_id', '')).strip()
            if not instrument or not profile_id:
                return jsonify(success=False,
                               error='Missing instrument or profile_id'), 400
            removed = invalidate_profile(cache_root, instrument, profile_id)
        else:
            removed = invalidate_all(cache_root)
        return jsonify(success=True, removed=removed)

    def _build_admin_download_mgmt_context(self, perms):
        """Build context for admin download-management page."""
        settings = dt.load_settings()
        api_usage = dt.list_all_usage('api')
        basket_usage = dt.list_all_usage('basket')
        for row in api_usage:
            row['total_size_fmt'] = dt.format_bytes(row['total_bytes'])
            row['last_download_fmt'] = (row['last_download_at'] or 'Never')
        for row in basket_usage:
            row['total_size_fmt'] = dt.format_bytes(row['total_bytes'])
            row['last_download_fmt'] = (row['last_download_at'] or 'Never')
        api_total_bytes = sum(r['total_bytes'] for r in api_usage)
        basket_total_bytes = sum(r['total_bytes'] for r in basket_usage)
        return {
            'can_manage': 'view.admin' in perms,
            'settings': settings,
            'api_usage': api_usage,
            'basket_usage': basket_usage,
            'api_total_size': dt.format_bytes(api_total_bytes),
            'api_total_files': sum(r['total_files'] for r in api_usage),
            'basket_total_size': dt.format_bytes(basket_total_bytes),
            'basket_total_files': sum(r['total_files'] for r in basket_usage),
        }

    def _api_admin_dm_save_settings(self):
        """Save download management settings."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups)
        else:
            perms = get_public_permissions()
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json(silent=True) or {}
        updates = {}
        for key in ('api_rate_limit_seconds',
                    'basket_rate_limit_seconds',
                    'basket_max_archive_gb'):
            if key in body:
                updates[key] = float(body[key])
        dt.save_settings(updates)
        return jsonify(success=True)

    def _api_admin_dm_reset_user(self):
        """Reset download counters for a user."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups)
        else:
            perms = get_public_permissions()
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json(silent=True) or {}
        username = str(body.get('username', '')).strip()
        category = str(body.get('category', '')).strip()
        if not username or category not in ('api', 'basket'):
            return jsonify(success=False, error='Invalid parameters'), 400
        dt.reset_user_usage(username, category)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Token-based API auth helper
    # -----------------------------------------------------------------
    @staticmethod
    def _get_api_user() -> Optional[dict]:
        """Return user info from Bearer token or session (in that order).

        Checks the ``Authorization: Bearer <token>`` header first.
        Falls back to the normal session-based ``get_effective_user``.
        """
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
            username = at.validate_token(token)
            if username:
                info = get_user_info(username)
                if info:
                    return info
            # Invalid token → do NOT fall back to session
            return None
        return get_effective_user(session)

    # -----------------------------------------------------------------
    # User API token endpoints
    # -----------------------------------------------------------------
    def _api_user_token_generate(self):
        """Generate a new API token for the logged-in user."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Not logged in'), 401
        body = request.get_json(silent=True) or {}
        label = str(body.get('label', '')).strip()[:100]
        token = at.generate_token(user_info['username'], label)
        return jsonify(success=True, token=token)

    def _api_user_token_revoke(self):
        """Revoke the API token for the logged-in user."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Not logged in'), 401
        removed = at.revoke_token(user_info['username'])
        return jsonify(success=True, removed=removed)

    @staticmethod
    def _format_utc_datetime(dt: Optional[datetime]) -> str:
        """Format UTC datetime for display."""
        if dt is None:
            return 'Never'
        return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _admin_health_cache_key(perms) -> str:
        """Stable key for admin-health cache entries."""
        return '|'.join(sorted(perms))

    def _load_health_cache_from_disk(self) -> None:
        """Populate in-memory admin health cache from the persisted disk file."""
        try:
            cache_file = self._admin_health_cache_file
            if (not cache_file.exists()
                    and self._admin_health_cache_legacy_file.exists()):
                cache_file = self._admin_health_cache_legacy_file
            if not cache_file.exists():
                return
            with open(cache_file, 'r',
                      encoding='utf-8') as fh:
                raw = json.load(fh)
            if not isinstance(raw, dict):
                return
            restored = {}
            for key, entry in raw.items():
                if not isinstance(entry, dict):
                    continue
                updated_at = None
                updated_at_str = entry.get('updated_at')
                if updated_at_str:
                    try:
                        updated_at = datetime.fromisoformat(updated_at_str)
                    except Exception:
                        pass
                restored[key] = {
                    'health': entry.get('health', {}),
                    'updated_at': updated_at,
                    'in_progress': False,
                    'perms': entry.get('perms', []),
                }
            with self._admin_health_cache_lock:
                self._admin_health_cache = restored
        except Exception:
            pass

    def _save_health_cache_to_disk(self) -> None:
        """Persist current in-memory admin health cache to disk."""
        try:
            with self._admin_health_cache_lock:
                snapshot = dict(self._admin_health_cache)
            serializable = {}
            for key, entry in snapshot.items():
                updated_at = entry.get('updated_at')
                serializable[key] = {
                    'health': entry.get('health', {}),
                    'updated_at': (
                        updated_at.isoformat() if updated_at else None
                    ),
                    'perms': entry.get('perms', []),
                }
            self._admin_health_cache_file.parent.mkdir(
                parents=True, exist_ok=True)
            tmp = self._admin_health_cache_file.with_suffix('.tmp')
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(serializable, fh)
            tmp.replace(self._admin_health_cache_file)
        except Exception:
            pass

    def _start_admin_health_refresher(self) -> None:
        """Start background hourly refresh; spawn async refresh of any
        entries loaded from the persisted disk cache at startup."""
        with self._admin_health_cache_lock:
            startup_items = [
                (key, set(entry.get('perms', [])))
                for key, entry in self._admin_health_cache.items()
            ]
        for key, perms in startup_items:
            self._spawn_admin_health_refresh(key, None, perms)
        thread = threading.Thread(
            target=self._admin_health_refresher_loop,
            daemon=True,
            name='admin-health-refresher',
        )
        thread.start()

    def _admin_health_refresher_loop(self) -> None:
        """Refresh all cached admin-health snapshots every hour."""
        while True:
            time.sleep(3600)
            with self._admin_health_cache_lock:
                work_items = [
                    (key, set(entry.get('perms', [])))
                    for key, entry in self._admin_health_cache.items()
                ]
            for key, perms in work_items:
                self._refresh_admin_health_entry(key, None, perms)

    def _refresh_admin_health_entry(self, cache_key: str,
                                    user_info,
                                    perms) -> None:
        """Refresh one admin-health cache entry synchronously."""
        health = self._build_admin_card_health_uncached(user_info, perms)
        with self._admin_health_cache_lock:
            self._admin_health_cache[cache_key] = {
                'health': health,
                'updated_at': datetime.now(timezone.utc),
                'in_progress': False,
                'perms': sorted(perms),
            }
        threading.Thread(
            target=self._save_health_cache_to_disk,
            daemon=True,
            name='admin-health-disk-save',
        ).start()

    def _spawn_admin_health_refresh(self, cache_key: str,
                                    user_info,
                                    perms) -> None:
        """Spawn async refresh if one is not already in progress."""
        with self._admin_health_cache_lock:
            entry = self._admin_health_cache.get(cache_key, {})
            if entry.get('in_progress', False):
                return
            self._admin_health_cache[cache_key] = {
                'health': entry.get('health', {}),
                'updated_at': entry.get('updated_at'),
                'in_progress': True,
                'perms': sorted(perms),
            }

        def _runner():
            try:
                self._refresh_admin_health_entry(cache_key, user_info, perms)
            except Exception:
                with self._admin_health_cache_lock:
                    existing = self._admin_health_cache.get(cache_key, {})
                    existing['in_progress'] = False
                    self._admin_health_cache[cache_key] = existing

        threading.Thread(
            target=_runner,
            daemon=True,
            name='admin-health-refresh-now',
        ).start()

    def shutdown(self) -> None:
        """Clean up background services and interactive child processes."""
        import sys as _sys
        with self._shutdown_lock:
            if self._shutdown_started:
                return
            self._shutdown_started = True

        _debug = self.debug

        if _debug:
            print('[apero_ri] Saving admin health cache...', file=_sys.stderr, flush=True)
        try:
            self._save_health_cache_to_disk()
            if _debug:
                print('[apero_ri]   health cache saved.', file=_sys.stderr, flush=True)
        except Exception as _exc:
            if _debug:
                print(f'[apero_ri]   health cache save failed: {_exc}', file=_sys.stderr, flush=True)

        if _debug:
            print('[apero_ri] Stopping background task worker/scheduler...', file=_sys.stderr, flush=True)
        try:
            task_runner.shutdown_background_services(debug=_debug)
            if _debug:
                print('[apero_ri]   background services stopped.', file=_sys.stderr, flush=True)
        except Exception as _exc:
            if _debug:
                print(f'[apero_ri]   background services stop failed: {_exc}', file=_sys.stderr, flush=True)

        if _debug:
            print('[apero_ri] Closing interactive SSHFS sessions...', file=_sys.stderr, flush=True)
        try:
            from apero_ri.core.sshfs_interactive import close_all_sessions
            result = close_all_sessions()
            if _debug:
                n = result.get('closed', 0)
                print(f'[apero_ri]   closed {n} interactive session(s).', file=_sys.stderr, flush=True)
        except Exception as _exc:
            if _debug:
                print(f'[apero_ri]   SSHFS session cleanup failed: {_exc}', file=_sys.stderr, flush=True)

        if _debug:
            print('[apero_ri] Shutdown complete.', file=_sys.stderr, flush=True)

    def _get_admin_health(self, user_info, perms,
                          force: bool = False,
                          allow_async_refresh: bool = True):
        """Return cached admin-health with optional async/sync refresh."""
        cache_key = self._admin_health_cache_key(perms)
        now = datetime.now(timezone.utc)

        with self._admin_health_cache_lock:
            entry = self._admin_health_cache.get(cache_key)

        if force:
            self._refresh_admin_health_entry(cache_key, user_info, perms)
            with self._admin_health_cache_lock:
                refreshed = self._admin_health_cache.get(cache_key, {})
            return (
                refreshed.get('health', {}),
                refreshed.get('updated_at'),
                refreshed.get('in_progress', False),
            )

        if entry:
            updated_at = entry.get('updated_at')
            fresh = (updated_at is not None
                     and (now - updated_at) <= self._admin_health_cache_ttl)
            if fresh:
                return (
                    entry.get('health', {}),
                    updated_at,
                    entry.get('in_progress', False),
                )

            # stale entry
            if allow_async_refresh:
                self._spawn_admin_health_refresh(cache_key, user_info, perms)
                with self._admin_health_cache_lock:
                    stale = self._admin_health_cache.get(cache_key, {})
                return (
                    stale.get('health', {}),
                    stale.get('updated_at'),
                    stale.get('in_progress', False),
                )

            self._refresh_admin_health_entry(cache_key, user_info, perms)
            with self._admin_health_cache_lock:
                refreshed = self._admin_health_cache.get(cache_key, {})
            return (
                refreshed.get('health', {}),
                refreshed.get('updated_at'),
                refreshed.get('in_progress', False),
            )

        # no cache entry yet
        if allow_async_refresh:
            with self._admin_health_cache_lock:
                self._admin_health_cache[cache_key] = {
                    'health': {},
                    'updated_at': None,
                    'in_progress': False,
                    'perms': sorted(perms),
                }
            self._spawn_admin_health_refresh(cache_key, user_info, perms)
            with self._admin_health_cache_lock:
                pending = self._admin_health_cache.get(cache_key, {})
            return (
                pending.get('health', {}),
                pending.get('updated_at'),
                pending.get('in_progress', False),
            )

        self._refresh_admin_health_entry(cache_key, user_info, perms)
        with self._admin_health_cache_lock:
            refreshed = self._admin_health_cache.get(cache_key, {})
        return (
            refreshed.get('health', {}),
            refreshed.get('updated_at'),
            refreshed.get('in_progress', False),
        )

    def _refresh_admin_health_after_change(self,
                                           user_info=None,
                                           perms=None) -> None:
        """Refresh admin-health cache after successful admin mutations.

        Best effort only: this must never break the primary API action.
        """
        try:
            if user_info is None:
                user_info = get_effective_user(session)
            if not user_info:
                return

            if perms is None:
                perms = resolve_user_permissions(
                    user_info.get('groups', []),
                    self.ari_groups,
                )
            perms = perms or set()
            if 'view.admin' not in perms:
                return

            self._get_admin_health(
                user_info=user_info,
                perms=perms,
                force=True,
                allow_async_refresh=False,
            )
        except Exception:
            return

    def _build_admin_card_health_uncached(self, user_info, perms) -> dict:
        """
        Return a dict keyed by admin card page_id with health dicts.
        Each health dict has: status ('ok'|'warning'|'error'), message.
        Only checks cards the user can see.
        """
        health = {}

        # ── User Management: warn if any user has only 'public' group  ───
        _t0 = time.monotonic()
        if 'view.admin' in perms:
            try:
                all_users = load_users()
                unreviewed = sum(
                    1 for _u, ud_data in all_users.items()
                    if set(ud_data.get('groups', [])) <= {'public'}
                )
                if unreviewed:
                    health['home.admin_portal.users'] = {
                        'status': 'warning',
                        'message': f'{unreviewed} user(s) with only "public" access – may need group assignment.',
                    }
                else:
                    health['home.admin_portal.users'] = {
                        'status': 'ok', 'message': ''}
            except Exception:
                pass
        if 'home.admin_portal.users' in health:
            health['home.admin_portal.users']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── Email: error if enabled but connection fails ──────────────────
        _t0 = time.monotonic()
        if 'view.admin' in perms:
            try:
                email_cfg = eb.load_email_config()
                if not email_cfg.get('enabled', False):
                    health['home.admin_portal.email'] = {
                        'status': 'warning',
                        'message': 'Email delivery is not enabled. Verification codes go to log file.',
                    }
                else:
                    test = eb.test_email_connection(email_cfg, quick_test=True)
                    if test['ok']:
                        health['home.admin_portal.email'] = {
                            'status': 'ok', 'message': ''}
                    else:
                        health['home.admin_portal.email'] = {
                            'status': 'error',
                            'message': f'SMTP connection failed: {test["error"]}',
                        }
            except Exception:
                pass
        if 'home.admin_portal.email' in health:
            health['home.admin_portal.email']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── Backup Settings: warn if cloud mirror disabled, error if broken ─
        _t0 = time.monotonic()
        if 'view.admin' in perms:
            try:
                backup_cfg = bb.load_backup_config()
                if (not backup_cfg.get('enabled', False)
                        or backup_cfg.get('provider', 'local_only')
                    == 'local_only'):
                    health['home.admin_portal.backup_settings'] = {
                        'status': 'warning',
                        'message': 'Cloud backup mirror is not enabled (local backups only).',
                    }
                else:
                    test = bb.test_backup_connection(backup_cfg)
                    if test.get('ok', False):
                        health['home.admin_portal.backup_settings'] = {
                            'status': 'ok', 'message': ''}
                    else:
                        health['home.admin_portal.backup_settings'] = {
                            'status': 'error',
                            'message': f'Cloud backup test failed: {test.get("error", "unknown error")}',
                        }
            except Exception:
                pass
        if 'home.admin_portal.backup_settings' in health:
            health['home.admin_portal.backup_settings']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── SSHFS Management: check mount status ───────────────────────
        _t0 = time.monotonic()
        if 'view.admin' in perms:
            try:
                health_check = sb.health_check()
                health['home.admin_portal.sshfs_management'] = health_check
            except Exception:
                pass
        if 'home.admin_portal.sshfs_management' in health:
            health['home.admin_portal.sshfs_management']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── APERO Profiles: error if any profile has DB/path failures ────
        _t0 = time.monotonic()
        if 'manage.apero_profile' in perms:
            try:
                overview = self._build_apero_profiles_overview_status()
                profile_errors = overview.get('issues', [])
                if profile_errors:
                    health['home.admin_portal.apero_profiles'] = {
                        'status': 'error',
                        'message': (
                            f'Some APERO profiles need attention. '
                            f'{"; ".join(profile_errors[:3])}'
                            f'{"; ..." if len(profile_errors) > 3 else ""}'
                        ),
                    }
                else:
                    health['home.admin_portal.apero_profiles'] = {
                        'status': 'ok', 'message': ''}
            except Exception:
                pass
        if 'home.admin_portal.apero_profiles' in health:
            health['home.admin_portal.apero_profiles']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── Async Tasks: error if any active task has failed/errors ─────
        _t0 = time.monotonic()
        if 'manage.apero_profile' in perms:
            try:
                all_tasks = load_async_tasks()
                failed_tasks = []

                for instrument, task_list in all_tasks.items():
                    if not isinstance(task_list, list):
                        continue
                    for task_cfg in task_list:
                        if not isinstance(task_cfg, dict):
                            continue
                        if task_cfg.get('active', True) is False:
                            continue

                        task_id = str(task_cfg.get('id', '') or '').strip()
                        runtime = (
                            task_runner.get_task_status(task_id)
                            if task_id else {'found': False}
                        )

                        if runtime.get('found'):
                            status = str(runtime.get('status', '') or '')
                            error = str(runtime.get('error', '') or '').strip()
                        else:
                            status = str(task_cfg.get('last_status', '') or '')
                            persisted = task_runner.get_persisted_task_info_error(task_id)
                            error = str(
                                persisted.get('error', '')
                                or task_cfg.get('error', '')
                                or ''
                            ).strip()

                        if status == 'failed' or error:
                            label = str(
                                task_cfg.get('task_key', task_id)
                                or task_id)
                            failed_tasks.append(f'{instrument}:{label}')

                if failed_tasks:
                    health['home.admin_portal.async_tasks'] = {
                        'status': 'error',
                        'message': (
                            f'{len(failed_tasks)} active task(s) in error: '
                            f'{", ".join(failed_tasks[:3])}'
                            f'{" ..." if len(failed_tasks) > 3 else ""}'
                        ),
                    }
                else:
                    health['home.admin_portal.async_tasks'] = {
                        'status': 'ok', 'message': ''}
            except Exception:
                pass
        if 'home.admin_portal.async_tasks' in health:
            health['home.admin_portal.async_tasks']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── Science Groups: warn on assignment/configuration gaps ───────
        _t0 = time.monotonic()
        if 'manage.sci_group' in perms:
            try:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                user_instr = set((user_info or {}).get('instruments', []))
                instruments = (
                    [i for i in all_instr if i in user_instr]
                    or list(all_instr))

                total_users = set()
                assigned_users = set()
                total_run_ids = set()
                assigned_run_ids = set()
                groups_without_users = []
                groups_without_run_ids = []
                for inst in instruments:
                    inst_users = set(get_users_for_instrument(inst))
                    total_users |= inst_users
                    inst_run_ids = {
                        str(rid).strip()
                        for rid in self._get_instrument_run_ids(inst)
                        if str(rid).strip()
                    }
                    total_run_ids |= inst_run_ids

                    groups = load_science_groups(inst)
                    groups, _ = self._sync_all_science_group(
                        inst,
                        groups=groups,
                        run_ids=sorted(inst_run_ids),
                        persist=True,
                    )

                    for gname, entry in groups.items():
                        if not isinstance(entry, dict):
                            continue
                        is_all_group = self._is_all_science_group(gname)

                        group_users = []
                        for username in entry.get('users', []):
                            uname = str(username).strip()
                            if uname:
                                group_users.append(uname)
                                assigned_users.add(uname)

                        group_run_ids = []
                        for run_id in entry.get('run_ids', []):
                            rid = str(run_id).strip()
                            if rid:
                                group_run_ids.append(rid)
                                if not is_all_group:
                                    assigned_run_ids.add(rid)

                        if not group_users and not is_all_group:
                            groups_without_users.append(f'{inst}:{gname}')
                        if not group_run_ids and not is_all_group:
                            groups_without_run_ids.append(f'{inst}:{gname}')

                unassigned_users = sorted(total_users - assigned_users)
                unassigned_run_ids = sorted(total_run_ids - assigned_run_ids)

                issue_parts = []
                details = []

                if unassigned_users:
                    issue_parts.append(
                        f'{len(unassigned_users)} user(s) not assigned to any science group'
                    )
                    details.extend([f'user: {u}' for u in unassigned_users])

                if groups_without_users:
                    issue_parts.append(
                        f'{len(groups_without_users)} science group(s) without users'
                    )
                    details.extend([
                        f'group-without-users: {name}' for name in groups_without_users
                    ])

                if groups_without_run_ids:
                    issue_parts.append(
                        f'{len(groups_without_run_ids)} science group(s) without run IDs'
                    )
                    details.extend([
                        f'group-without-run-ids: {name}'
                        for name in groups_without_run_ids
                    ])

                if unassigned_run_ids:
                    issue_parts.append(
                        f'{len(unassigned_run_ids)} run ID(s) not assigned to any science group'
                    )
                    details.extend(
                        [f'run_id: {rid}' for rid in unassigned_run_ids])

                if issue_parts:
                    health['home.admin_portal.science_groups'] = {
                        'status': 'warning',
                        'message': '; '.join(issue_parts) + '.',
                        'details': details,
                    }
                else:
                    if not total_users:
                        health['home.admin_portal.science_groups'] = {
                            'status': 'warning',
                            'message': 'No users are currently assigned to managed instruments.',
                        }
                    else:
                        health['home.admin_portal.science_groups'] = {
                            'status': 'ok',
                            'message': (
                                f'All {len(total_users)} users and '
                                f'{len(total_run_ids)} run ID(s) are assigned to at least one '
                                'science group, and all groups have users/run IDs.'
                            ),
                        }
            except Exception as exc:
                health['home.admin_portal.science_groups'] = {
                    'status': 'error',
                    'message': f'Science group health check failed: {exc}',
                }
        if 'home.admin_portal.science_groups' in health:
            health['home.admin_portal.science_groups']['duration_s'] = round(time.monotonic() - _t0, 2)

        # ── User DB Access: warn if profile table access is incomplete ──
        _t0 = time.monotonic()
        if 'manage.admin.user_db_access' in perms:
            try:
                report = self._build_user_db_access_health_report(user_info)
                health['home.admin_portal.user_db_access'] = {
                    'status': report.get('status', 'warning'),
                    'message': str(report.get('message', '')).strip(),
                }
            except Exception as exc:
                health['home.admin_portal.user_db_access'] = {
                    'status': 'error',
                    'message': f'User DB access health check failed: {exc}',
                }
        if 'home.admin_portal.user_db_access' in health:
            health['home.admin_portal.user_db_access']['duration_s'] = round(time.monotonic() - _t0, 2)

        return health

    def _build_admin_health_rows(self, health: dict) -> list:
        """Build ordered health rows for the Admin Portal health panel."""
        checks = {
            'home.admin_portal.users': {
                'ok': 'All users have at least one non-public group assignment.',
                'warning': 'Some users still only have public access and should be reviewed.',
                'error': 'User assignment checks failed.',
            },
            'home.admin_portal.science_groups': {
                'ok': 'All users are assigned to at least one science group.',
                'warning': 'At least one user is not assigned to any science group.',
                'error': 'Science-group assignment checks failed.',
            },
            'home.admin_portal.email': {
                'ok': 'Email delivery is enabled and SMTP connectivity check succeeds.',
                'warning': 'Email delivery is disabled or running in non-email mode.',
                'error': 'SMTP connectivity failed.',
            },
            'home.admin_portal.apero_profiles': {
                'ok': 'All APERO profiles pass database and path checks.',
                'warning': 'Some APERO profile checks need attention.',
                'error': 'One or more APERO profiles failed validation checks.',
            },
            'home.admin_portal.user_db_access': {
                'ok': 'All APERO profiles have complete DB table access rules.',
                'warning': 'At least one APERO profile has incomplete DB table access rules.',
                'error': 'DB-access health checks failed.',
            },
            'home.admin_portal.async_tasks': {
                'ok': 'No active async tasks are in failed/error state.',
                'warning': 'Some async task checks are inconclusive.',
                'error': 'One or more active async tasks are in failed/error state.',
            },
            'home.admin_portal.backup_settings': {
                'ok': 'Cloud backup is properly configured and connection check succeeds.',
                'warning': 'Cloud backup mirror is not enabled (local backups only).',
                'error': 'Cloud backup test failed.',
            },
            'home.admin_portal.sshfs_management': {
                'ok': 'All configured SSHFS mounts are mounted.',
                'warning': 'Some SSHFS mounts are not currently mounted, or no mounts are configured.',
                'error': 'One or more SSHFS mounts have connection issues.',
            },
        }

        rows = []
        for pid in get_children('home.admin_portal', self.ari_pages):
            status_data = health.get(pid)
            if not isinstance(status_data, dict):
                continue
            status = (str(status_data.get('status', 'warning')).strip()
                      or 'warning')
            if status not in {'ok', 'warning', 'error'}:
                status = 'warning'
            msg = str(status_data.get('message', '')).strip()
            details = status_data.get('details', [])
            if not isinstance(details, list):
                details = []
            details = [str(item).strip()
                for item in details
                if str(item).strip()]

            rules = checks.get(pid, {})
            rule_msg = str(rules.get(status, '')).strip()
            page_def = self.ari_pages.get(pid, {})
            page_label = str(page_def.get('label', pid)).strip()

            duration_s = status_data.get('duration_s')
            rows.append({
                'page_id': pid,
                'label': page_label,
                'url': page_id_to_url(pid),
                'status': status,
                'message': msg or rule_msg,
                'rule_message': rule_msg,
                'details': details,
                'duration_s': duration_s,
            })

        return rows

    def _api_admin_health_update(self):
        """Force-refresh cached admin health and return updated metadata."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Forbidden'), 403

        health, updated_at, _ = self._get_admin_health(
            user_info=user_info,
            perms=perms,
            force=True,
            allow_async_refresh=False,
        )
        return jsonify(
            success=True,
            updated_at=self._format_utc_datetime(updated_at),
            health=health,
        )

    def _api_admin_health_config_get(self):
        """Return persisted health-status UI config."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Forbidden'), 403

        cfg = load_admin_health_config()
        return jsonify(success=True, config=cfg)

    def _api_admin_health_config_save(self):
        """Persist health-status UI config."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(success=False, error='Forbidden'), 403

        data = request.get_json() or {}
        refresh_frequency = str(
            data.get('refresh_frequency', 'manual')
        ).strip().lower()
        if refresh_frequency not in {'manual', '5m', '15m', '1h'}:
            return jsonify(success=False, error='Invalid refresh_frequency'), 400

        save_admin_health_config({'refresh_frequency': refresh_frequency})
        return jsonify(
            success=True,
            config={'refresh_frequency': refresh_frequency},
        )

    def _build_apero_profiles_overview_status(self) -> dict:
        """Build all-instruments APERO profile readiness and issue details."""
        profiles_by_instrument = load_apero_profiles()
        path_keys = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_OUT', 'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]

        issues = []
        total_profiles = 0
        per_instrument = {}

        for instrument, inst_profiles in profiles_by_instrument.items():
            if not isinstance(inst_profiles, dict):
                continue

            inst_issues = []
            inst_total = 0
            for name, cfg in inst_profiles.items():
                if not isinstance(cfg, dict):
                    continue
                total_profiles += 1
                inst_total += 1

                reason_parts = []

                db = self._validate_profile_database(cfg)
                if not db.get('valid', False):
                    db_error = str(
                        db.get('error', '') or 'connection failed').strip()
                    reason_parts.append(f'Database error: {db_error}')

                invalid_paths = []
                for key in path_keys:
                    path_val = str(
                        self._profile_get_path(cfg, key, '')).strip()
                    if not path_val or not Path(path_val).is_dir():
                        invalid_paths.append(key)
                if invalid_paths:
                    reason_parts.append(
                        'Invalid paths: ' + ', '.join(invalid_paths)
                    )

                if not str(cfg.get('APERO_INSTRUMENT_PROFILE', '')).strip():
                    reason_parts.append('No instrument profile selected')

                if reason_parts:
                    line = (
                        f'Instrument {instrument} profile {name}: '
                        f'{" | ".join(reason_parts)}'
                    )
                    issues.append(line)
                    inst_issues.append(line)

            per_instrument[instrument] = {
                'total_profiles': inst_total,
                'issues': inst_issues,
            }

        if issues:
            status = {
                'level': 'error',
                'headline': 'Some APERO profiles need attention.',
                'details': issues,
            }
        else:
            status = {
                'level': 'ok',
                'headline': 'All profiles across instruments ready.',
                'details': [],
            }

        return {
            'status': status,
            'issues': issues,
            'total_profiles': total_profiles,
            'per_instrument': per_instrument,
        }

    def _ri_profile_view(self, profile_id):
        """View function for dynamic data portal profile sub-pages."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        # Build section cards in pages.yaml definition order so that
        # reordering pages.yaml automatically updates the profile page.
        _card_url_map = {
            'object_table': f'/data_portal/{profile_id}/object-table',
            'obs_table':    f'/data_portal/{profile_id}/observation-table',
            'query_db':     f'/data_portal/{profile_id}/query-db',
            'qc_graphs':    f'/data_portal/{profile_id}/qc-graphs',
            'basket':       f'/data_portal/{profile_id}/basket',
        }
        _card_desc_map = {
            'object_table':     'Browse and search astrophysical objects '
                                'in this reduction profile.',
            'obs_table':        'View night-by-night observations '
                                'and their reduction status.',
            'query_db':         'Run custom queries against the '
                                'reduction database tables.',
            'qc_graphs':        'Interactive plots of quality control '
                                'metrics over time.',
            'basket':           'Collect and download files from this '
                                'reduction profile.',
            'last_object_page': 'No object page opened yet for this profile.',
        }
        section_cards = []
        for tpl_key, tpl_def in self._page_templates.items():
            if not isinstance(tpl_def, dict):
                continue
            if tpl_def.get('parent') != 'home.data_portal.{apero_profile}':
                continue
            suffix = tpl_key.split('.')[-1]
            if '{' in suffix:  # skip {objname} template entries
                continue
            card = {
                'key':         suffix,
                'label':       tpl_def.get('label', suffix),
                'icon':        tpl_def.get('icon', ''),
                'url':         _card_url_map.get(suffix, ''),
                'description': _card_desc_map.get(suffix, ''),
            }
            section_cards.append(card)

        context = {
            'page_id': page_id,
            'page_label': profile_id,
            'page_icon': 'fa-solid fa-laptop-code',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'section_cards': section_cards,
            'health_url': '/api/ri/profile-health',
            # Sidebar
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
        }

        # Build sidebar tree with current page highlighted
        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )
        context['sidebar_tree'] = sidebar_tree

        return render_template('data_portal/profile.html',
                               **context)

    def _api_ri_profile_health(self):
        """Run database and path health checks for a profile."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        profile_id = data.get('profile_id', '').strip()
        if not profile_id:
            return jsonify(success=False, error='Missing profile_id'), 400

        # Verify user has access to this profile
        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Access denied'), 403

        cfg = profile['data']

        # -- Database check --
        db_result = self._validate_profile_database(cfg)

        # -- Path checks --
        path_keys = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_OUT', 'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]
        path_results = {}
        all_paths_ok = True
        for key in path_keys:
            val = self._profile_get_path(cfg, key, '')
            exists = bool(val) and Path(val).is_dir()
            path_results[key] = exists
            if not exists:
                all_paths_ok = False

        return jsonify(
            success=True,
            database={'ok': db_result['valid'],
                      'error': db_result.get('error', '')},
            paths={'ok': all_paths_ok, 'details': path_results},
        )

    # -----------------------------------------------------------------
    # Login / Logout views
    # -----------------------------------------------------------------
    def _login_view(self):
        """Handle login via a modal rendered on top of the home page."""
        username_value = str(session.get('last_username', '') or '')
        user_info = get_effective_user(session)
        if user_info:
            return redirect(url_for('home'))

        perms = get_public_permissions()
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            username_value = username
            session['last_username'] = username

            user = authenticate(username, password)
            if user:
                session['user'] = user['username']
                session['last_login'] = user.get('last_login')
                session.pop('login_as', None)
                session['last_username'] = user['username']
                # Default to persistent login unless user opts out.
                session.permanent = request.form.get('remember', '1') == '1'
                flash(f'Welcome, {user["username"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'danger')

        context = self._build_home_page_context(None, perms)
        context.update({
            'login_modal_open': True,
            'last_username': username_value,
        })
        return render_template('home/index.html', **context)

    def _logout_view(self):
        """Clear session and redirect to home."""
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @staticmethod
    def _get_primary_contact_email(user: dict) -> str:
        """Return best email address to use for account notifications."""
        primary = str(user.get('primary_email', '')).strip()
        if primary:
            return primary
        emails = user.get('emails', [])
        if isinstance(emails, list):
            for email in emails:
                val = str(email).strip()
                if val:
                    return val
        return ''

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
        """Remove expired password-reset tokens. Returns True if modified."""
        now = datetime.now(timezone.utc)
        changed = False
        for user in users.values():
            reset_data = user.get('password_reset')
            if not isinstance(reset_data, dict):
                continue
            exp = self._parse_iso_datetime(reset_data.get('expires_at', ''))
            if exp is None or now > exp:
                user.pop('password_reset', None)
                changed = True
        return changed

    def _find_reset_user(self, token: str, users: dict) -> Optional[str]:
        """Find username matching a valid reset token."""
        if not token:
            return None
        for username, user in users.items():
            reset_data = user.get('password_reset')
            if not isinstance(reset_data, dict):
                continue
            token_hash = str(reset_data.get('token_hash', '')).strip()
            if token_hash and verify_password(token, token_hash):
                return username
        return None

    @staticmethod
    def _get_request_ip() -> str:
        """Get client IP, preferring X-Forwarded-For when present."""
        xff = str(request.headers.get('X-Forwarded-For', '')).strip()
        if xff:
            return xff.split(',')[0].strip() or 'unknown'
        return str(request.remote_addr or 'unknown').strip() or 'unknown'

    def _prune_forgot_pw_rate_limit(self, now_ts: float) -> None:
        """Drop old throttle records to keep in-memory state small."""
        stale_after = 3600.0
        to_delete = []
        for ip, state in self._forgot_pw_rate_limit.items():
            last_seen = float(state.get('last_seen', 0.0) or 0.0)
            blocked_until = float(state.get('blocked_until', 0.0) or 0.0)
            if now_ts > blocked_until and (now_ts - last_seen) > stale_after:
                to_delete.append(ip)
        for ip in to_delete:
            self._forgot_pw_rate_limit.pop(ip, None)

    def _register_forgot_pw_attempt(self, ip: str) -> Optional[int]:
        """Record forgot-password attempt and return wait seconds if blocked."""
        now_ts = datetime.now(timezone.utc).timestamp()
        self._prune_forgot_pw_rate_limit(now_ts)

        state = self._forgot_pw_rate_limit.get(ip, {
            'attempts': 0,
            'penalty': 0,
            'blocked_until': 0.0,
            'last_seen': 0.0,
        })

        blocked_until = float(state.get('blocked_until', 0.0) or 0.0)
        if now_ts < blocked_until:
            remaining = int(blocked_until - now_ts + 0.999)
            state['last_seen'] = now_ts
            self._forgot_pw_rate_limit[ip] = state
            return max(1, remaining)

        # Decay penalties after idle time.
        last_seen = float(state.get('last_seen', 0.0) or 0.0)
        if last_seen and (now_ts - last_seen) > 600.0:
            state['attempts'] = 0
            state['penalty'] = 0

        state['attempts'] = int(state.get('attempts', 0) or 0) + 1
        state['last_seen'] = now_ts

        if state['attempts'] > self._forgot_pw_max_attempts:
            penalty = int(state.get('penalty', 0) or 0) + 1
            wait_seconds = min(
                self._forgot_pw_base_wait * (2 ** (penalty - 1)),
                self._forgot_pw_max_wait,
            )
            state['penalty'] = penalty
            state['attempts'] = 0
            state['blocked_until'] = now_ts + float(wait_seconds)
            self._forgot_pw_rate_limit[ip] = state
            return int(wait_seconds)

        state['blocked_until'] = 0.0
        self._forgot_pw_rate_limit[ip] = state
        return None

    def _forgot_password_view(self):
        """Request a password reset email without revealing account existence."""
        if request.method == 'POST':
            ip = self._get_request_ip()
            wait_seconds = self._register_forgot_pw_attempt(ip)
            if wait_seconds is not None:
                flash(
                    'Too many password reset attempts from this IP. '
                    f'Please wait {wait_seconds}s before trying again.',
                    'warning',
                )
                return redirect(url_for('forgot_password'))

            identifier = str(request.form.get('identifier', '')).strip()
            generic_msg = ('If an account matches that username/email, '
                           'a reset link has been sent.')

            users = load_users()
            changed = self._cleanup_expired_reset_tokens(users)
            identifier_l = identifier.lower()

            matched_username = None
            recipient_email = ''

            if identifier:
                for username, user in users.items():
                    if username.lower() == identifier_l:
                        matched_username = username
                        recipient_email = self._get_primary_contact_email(user)
                        break

                if matched_username is None:
                    for username, user in users.items():
                        emails = user.get('emails', [])
                        if not isinstance(emails, list):
                            emails = []
                        primary = str(user.get('primary_email', '')).strip()
                        candidates = [e for e in emails if str(e).strip()]
                        if primary:
                            candidates.append(primary)
                        if any(str(e).strip().lower() == identifier_l
                               for e in candidates):
                            matched_username = username
                            recipient_email = (primary
                                               or self._get_primary_contact_email(
                                                   user))
                            break

            if matched_username and recipient_email:
                token = secrets.token_urlsafe(32)
                expires_at = (
                    datetime.now(timezone.utc) + timedelta(minutes=30)
                ).isoformat()
                users[matched_username]['password_reset'] = {
                    'token_hash': hash_password(token),
                    'expires_at': expires_at,
                    'requested_at': datetime.now(timezone.utc).isoformat(),
                }
                changed = True

                reset_link = url_for('reset_password', token=token,
                                     _external=True)
                subject = 'APERO RI password reset request'
                body = (
                    'A request was received to reset your APERO RI password.\n\n'
                    f'Use this link to set a new password (valid for 30 minutes):\n{reset_link}\n\n'
                    'If you did not request this, you can ignore this email.'
                )
                err = eb.send_email(recipient_email, subject, body)
                if err:
                    # Do not reveal account status in UI; keep server-side
                    # trace.
                    print(f'Password reset email failed for {matched_username}: {err}')

            if changed:
                save_users(users)

            flash(generic_msg, 'info')
            return redirect(url_for('forgot_password'))

        return render_template('home/forgot_password.html',
                               page_label='Forgot Password',
                               page_icon='fa-solid fa-key')

    def _reset_password_view(self, token: str):
        """Validate token and allow user to set a new password."""
        users = load_users()
        changed = self._cleanup_expired_reset_tokens(users)
        username = self._find_reset_user(token, users)

        if request.method == 'POST':
            if not username:
                if changed:
                    save_users(users)
                flash('This reset link is invalid or has expired.', 'danger')
                return redirect(url_for('forgot_password'))

            new_password = str(request.form.get('new_password', ''))
            confirm_password = str(request.form.get('confirm_password', ''))

            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('home/reset_password.html',
                                       page_label='Reset Password',
                                       page_icon='fa-solid fa-lock',
                                       token_valid=True)
            if len(new_password) < 8:
                flash('Password must be at least 8 characters.', 'danger')
                return render_template('home/reset_password.html',
                                       page_label='Reset Password',
                                       page_icon='fa-solid fa-lock',
                                       token_valid=True)

            users[username]['password'] = hash_password(new_password)
            users[username].pop('password_reset', None)
            save_users(users)
            flash('Your password has been reset. You can now log in.', 'success')
            return redirect(url_for('login'))

        if changed:
            save_users(users)

        return render_template('home/reset_password.html',
                               page_label='Reset Password',
                               page_icon='fa-solid fa-lock',
                               token_valid=(username is not None))

    def _register_view(self):
        """Render self-registration page."""
        return render_template('home/register.html',
                               page_label='Register',
                               page_icon='fa-solid fa-user-plus')

    @staticmethod
    def _send_verification_email(recipient_email: str,
                                 code: str,
                                 purpose: str) -> Optional[str]:
        """Send verification code email via configured email backend.

        Returns None on success, error string on failure.
        Configuration is read from {ARI_DIR}/admin/email/email.yaml.
        Falls back to log mode (writes to admin/email/email_log.txt)
        when unconfigured.
        """
        return eb.send_verification_email(recipient_email, code, purpose)

    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Validate lowercase username format."""
        return bool(re.match(r'^[a-z][a-z0-9_]{2,63}$', username))

    # -----------------------------------------------------------------
    # Registration & account APIs
    # -----------------------------------------------------------------
    def _api_auth_register_start(self):
        """Start user registration by sending a 6-digit verification code."""
        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        username = str(data.get('username', '')).strip()
        first_names = str(data.get('first_names', '')).strip()
        last_name = str(data.get('last_name', '')).strip()
        password = str(data.get('password', ''))
        password_confirm = str(data.get('password_confirm', ''))

        emails_raw = data.get('emails', [])
        institutions_raw = data.get('institutions', [])
        if isinstance(emails_raw, str):
            emails_raw = [emails_raw]
        if isinstance(institutions_raw, str):
            institutions_raw = [institutions_raw]

        emails = [str(e).strip() for e in emails_raw if str(e).strip()]
        institutions = [str(i).strip()
            for i in institutions_raw
            if str(i).strip()]

        if not self._is_valid_username(username):
            return jsonify(success=False,
                           error=('Username must be 3+ chars, lowercase, and use '
                                  'only letters, numbers, or underscore (_).')), 400
        if not first_names or not last_name:
            return jsonify(success=False,
                           error='First name(s) and last name are required.'), 400
        if not emails:
            return jsonify(success=False,
                           error='At least one email is required.'), 400
        if not institutions:
            return jsonify(success=False,
                           error='At least one institution is required.'), 400
        if password != password_confirm:
            return jsonify(success=False,
                           error='Passwords do not match.'), 400
        if len(password) < 8:
            return jsonify(success=False,
                           error='Password must be at least 8 characters.'), 400

        users = load_users()
        if username in users:
            return jsonify(success=False,
                           error='Username already exists.'), 409

        code = f'{secrets.randbelow(1_000_000):06d}'
        expires_at = (
            (datetime.now(timezone.utc) + timedelta(minutes=15))
        ).isoformat()

        err = self._send_verification_email(emails[0], code, 'registration')
        if err:
            return jsonify(success=False,
                           error=f'Failed to send verification email: {err}'), 500

        session['pending_registration'] = {
            'username': username,
            'first_names': first_names,
            'last_name': last_name,
            'emails': emails,
            'primary_email': emails[0],
            'institutions': institutions,
            'primary_institution': institutions[0],
            'password_hash': hash_password(password),
            'code': code,
            'expires_at': expires_at,
        }
        return jsonify(success=True)

    def _api_auth_register_verify(self):
        """Verify registration code and create user account."""
        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        pending = session.get('pending_registration')
        if not pending:
            return jsonify(success=False,
                           error='No pending registration found.'), 400

        code = str(data.get('code', '')).strip()
        if code != str(pending.get('code', '')):
            return jsonify(success=False,
                           error='Invalid verification code.'), 400

        exp = pending.get('expires_at')
        if not exp or datetime.now(timezone.utc) > datetime.fromisoformat(exp):
            session.pop('pending_registration', None)
            return jsonify(success=False,
                           error='Verification code expired. Start again.'), 400

        username = pending['username']
        users = load_users()
        if username in users:
            session.pop('pending_registration', None)
            return jsonify(success=False,
                           error='Username already exists.'), 409

        users[username] = {
            'password': pending['password_hash'],
            'groups': ['public'],
            'instruments': [],
            'first_names': pending['first_names'],
            'last_name': pending['last_name'],
            'emails': pending['emails'],
            'primary_email': pending['primary_email'],
            'email_verified': True,
            'institutions': pending['institutions'],
            'primary_institution': pending['primary_institution'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_login': None,
        }
        save_users(users)

        session.pop('pending_registration', None)
        session['user'] = username
        session['last_login'] = None
        session.pop('login_as', None)
        return jsonify(success=True)

    def _require_user(self):
        """Require a logged in effective user."""
        user_info = get_effective_user(session)
        if not user_info:
            return None
        return user_info

    def _api_user_account_get(self):
        """Get current user's account profile."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        username = user_info['username']
        users = load_users()
        user = users.get(username, {})
        return jsonify(success=True,
                       account={
                           'username': username,
                           'first_names': user.get('first_names', ''),
                           'last_name': user.get('last_name', ''),
                           'emails': user.get('emails', []),
                           'primary_email': user.get('primary_email', ''),
                           'email_verified': bool(user.get('email_verified', False)),
                           'institutions': user.get('institutions', []),
                           'primary_institution': user.get('primary_institution', ''),
                       })

    def _api_user_account_update(self):
        """Update account fields except primary email change verification."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        username = user_info['username']
        users = load_users()
        if username not in users:
            return jsonify(success=False, error='User not found'), 404
        user = users[username]

        first_names = str(data.get('first_names', '')).strip()
        last_name = str(data.get('last_name', '')).strip()
        emails_raw = data.get('emails', [])
        institutions_raw = data.get('institutions', [])
        primary_institution = str(data.get('primary_institution', '')).strip()

        if isinstance(emails_raw, str):
            emails_raw = [emails_raw]
        if isinstance(institutions_raw, str):
            institutions_raw = [institutions_raw]

        emails = [str(e).strip() for e in emails_raw if str(e).strip()]
        institutions = [str(i).strip()
            for i in institutions_raw
            if str(i).strip()]

        if not first_names or not last_name:
            return jsonify(success=False,
                           error='First name(s) and last name are required.'), 400
        if not emails:
            return jsonify(success=False,
                           error='At least one email is required.'), 400
        if not institutions:
            return jsonify(success=False,
                           error='At least one institution is required.'), 400
        if not primary_institution:
            return jsonify(success=False,
                           error='Primary institution is required.'), 400
        if primary_institution not in institutions:
            return jsonify(success=False,
                           error='Primary institution must be in institutions list.'), 400

        # Keep existing primary email unless explicitly changed via verify flow
        primary_email = user.get('primary_email', emails[0])
        if primary_email not in emails:
            emails.insert(0, primary_email)

        user['first_names'] = first_names
        user['last_name'] = last_name
        user['emails'] = emails
        user['institutions'] = institutions
        user['primary_institution'] = primary_institution

        current_password = str(data.get('current_password', ''))
        new_password = str(data.get('new_password', ''))
        confirm_password = str(data.get('confirm_password', ''))
        if current_password or new_password or confirm_password:
            if not (current_password and new_password and confirm_password):
                return jsonify(success=False,
                               error='Fill all password fields to change password.'), 400
            if not verify_password(current_password, user.get('password', '')):
                return jsonify(success=False,
                               error='Current password is incorrect.'), 400
            if new_password != confirm_password:
                return jsonify(success=False,
                               error='New passwords do not match.'), 400
            if len(new_password) < 8:
                return jsonify(success=False,
                               error='New password must be at least 8 characters.'), 400
            user['password'] = hash_password(new_password)

        users[username] = user
        save_users(users)
        return jsonify(success=True)

    def _api_user_account_request_primary_email(self):
        """Request primary email change by sending verification code."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400
        new_email = str(data.get('new_primary_email', '')).strip()
        if not new_email:
            return jsonify(success=False,
                           error='New primary email is required.'), 400

        code = f'{secrets.randbelow(1_000_000):06d}'
        expires_at = (
            (datetime.now(timezone.utc) + timedelta(minutes=15))
        ).isoformat()
        err = self._send_verification_email(
            new_email, code, 'primary-email-change')
        if err:
            return jsonify(success=False,
                           error=f'Failed to send verification email: {err}'), 500

        session['pending_primary_email_change'] = {
            'username': user_info['username'],
            'new_primary_email': new_email,
            'code': code,
            'expires_at': expires_at,
        }
        return jsonify(success=True)

    def _api_user_account_confirm_primary_email(self):
        """Confirm primary email change with verification code."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        pending = session.get('pending_primary_email_change')
        if not pending or pending.get('username') != user_info['username']:
            return jsonify(success=False,
                           error='No pending primary email change.'), 400

        code = str(data.get('code', '')).strip()
        if code != str(pending.get('code', '')):
            return jsonify(success=False,
                           error='Invalid verification code.'), 400

        exp = pending.get('expires_at')
        if not exp or datetime.now(timezone.utc) > datetime.fromisoformat(exp):
            session.pop('pending_primary_email_change', None)
            return jsonify(success=False,
                           error='Verification code expired. Request a new one.'), 400

        username = user_info['username']
        users = load_users()
        user = users.get(username)
        if not user:
            session.pop('pending_primary_email_change', None)
            return jsonify(success=False, error='User not found'), 404

        new_email = pending['new_primary_email']
        emails = user.get('emails', []) or []
        if new_email not in emails:
            emails.insert(0, new_email)
        user['emails'] = emails
        user['primary_email'] = new_email
        user['email_verified'] = True
        users[username] = user
        save_users(users)

        session.pop('pending_primary_email_change', None)
        return jsonify(success=True)

    @staticmethod
    def _normalize_pinned_pages(value) -> List[dict]:
        """Normalize persisted pinned pages into a clean list of dicts."""
        if not isinstance(value, list):
            return []

        normalized = []
        seen_ids = set()
        for item in value:
            if not isinstance(item, dict):
                continue
            page_id = str(item.get('page_id', '')).strip()
            label = str(item.get('label', '')).strip()
            url = str(item.get('url', '')).strip()
            icon = str(item.get('icon', '')).strip()
            pinned_at = str(item.get('pinned_at', '')).strip()

            if not page_id or not label or not url or not url.startswith('/'):
                continue
            if page_id in seen_ids:
                continue

            seen_ids.add(page_id)
            normalized.append({
                'page_id': page_id,
                'label': label,
                'url': url,
                'icon': icon or 'fa-solid fa-thumbtack',
                'pinned_at': pinned_at,
            })

        return normalized

    @staticmethod
    def _normalize_object_section_pins(value) -> List[str]:
        """Normalize object section ids used for per-user pinned section order."""
        if not isinstance(value, list):
            return []
        normalized = []
        seen = set()
        for item in value:
            sid = str(item).strip()
            if not sid:
                continue
            if not re.match(r'^[a-zA-Z0-9_.\-]+$', sid):
                continue
            if sid in seen:
                continue
            seen.add(sid)
            normalized.append(sid)
        return normalized

    def _api_user_pins_list(self):
        """List pinned pages for the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        username = user_info['username']
        pins = self._load_user_pins(username)
        return jsonify(success=True, pins=pins)

    def _load_user_pins(self, username: str) -> List[dict]:
        """Load pins from per-user pins.yaml and migrate legacy users.yaml pins."""
        pins_data = ud.load_pins(username)
        file_pins = self._normalize_pinned_pages(pins_data.get('pins', []))

        users = load_users()
        user = users.get(username, {})
        legacy_pins = self._normalize_pinned_pages(
            user.get('pinned_pages', []))

        pins = file_pins or legacy_pins
        if pins != file_pins:
            ud.save_pins(username, {'pins': pins})

        # Keep legacy field synchronized for backward compatibility.
        if user and legacy_pins != pins:
            user['pinned_pages'] = pins
            users[username] = user
            save_users(users)

        return pins

    def _save_user_pins(self, username: str, pins: List[dict]) -> None:
        """Persist pins to per-user pins.yaml and mirror into legacy users.yaml."""
        pins = self._normalize_pinned_pages(pins)
        ud.save_pins(username, {'pins': pins})

        users = load_users()
        user = users.get(username)
        if user is not None:
            user['pinned_pages'] = pins
            users[username] = user
            save_users(users)

    def _load_user_object_section_pins(self, username: str) -> List[str]:
        """Load per-user object section pin order and migrate legacy users.yaml."""
        file_pins = self._normalize_object_section_pins(
            ud.list_object_section_pins(username)
        )

        users = load_users()
        user = users.get(username, {})
        legacy = (user.get('object_section', {})
                  if isinstance(user, dict)
                  else {})
        legacy_pins = self._normalize_object_section_pins(
            legacy.get('pinned', []) if isinstance(legacy, dict) else []
        )

        pins = file_pins or legacy_pins
        if pins != file_pins:
            ud.save_object_section(username, {'pinned': pins})

        if user and legacy_pins != pins:
            section_cfg = user.get('object_section', {})
            if not isinstance(section_cfg, dict):
                section_cfg = {}
            section_cfg['pinned'] = pins
            user['object_section'] = section_cfg
            users[username] = user
            save_users(users)

        return pins

    def _save_user_object_section_pins(self,
                                       username: str,
                                       pins: List[str]) -> None:
        """Persist object section pin order to file and legacy users.yaml field."""
        pins = self._normalize_object_section_pins(pins)
        ud.save_object_section(username, {'pinned': pins})

        users = load_users()
        user = users.get(username)
        if user is not None:
            section_cfg = user.get('object_section', {})
            if not isinstance(section_cfg, dict):
                section_cfg = {}
            section_cfg['pinned'] = pins
            user['object_section'] = section_cfg
            users[username] = user
            save_users(users)

    def _api_user_pins_toggle(self):
        """Toggle pin state for a page for the current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        page_id = str(data.get('page_id', '')).strip()
        label = str(data.get('label', '')).strip()
        url = str(data.get('url', '')).strip()
        icon = str(data.get('icon', '')).strip() or 'fa-solid fa-thumbtack'
        if not page_id or not label or not url or not url.startswith('/'):
            return jsonify(success=False,
                           error='page_id, label, and relative url are required.'), 400
        if page_id in ('home.login', 'home.logout'):
            return jsonify(success=False,
                           error='This page cannot be pinned.'), 400

        username = user_info['username']
        pins = self._load_user_pins(username)
        existing = {pin['page_id']: pin for pin in pins}
        now_iso = datetime.now(timezone.utc).isoformat()

        if page_id in existing:
            pins = [pin for pin in pins if pin['page_id'] != page_id]
            pinned = False
        else:
            pins.append({
                'page_id': page_id,
                'label': label,
                'url': url,
                'icon': icon,
                'pinned_at': now_iso,
            })
            pinned = True

        self._save_user_pins(username, pins)
        return jsonify(success=True, pinned=pinned, pins=pins)

    def _api_user_pins_remove(self):
        """Remove a pin from the current user's pinned pages list."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        page_id = str(data.get('page_id', '')).strip()
        if not page_id:
            return jsonify(success=False, error='page_id is required.'), 400

        username = user_info['username']
        pins = self._load_user_pins(username)
        pins = [pin for pin in pins if pin['page_id'] != page_id]

        self._save_user_pins(username, pins)
        return jsonify(success=True, pins=pins)

    def _api_user_pins_reorder(self):
        """Persist a user-specified order for pinned pages."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json() or {}
        ordered_ids = body.get('ids', [])
        if not isinstance(ordered_ids, list):
            return jsonify(success=False, error='ids must be a list'), 400
        ordered_ids = [str(i).strip() for i in ordered_ids if str(i).strip()]

        username = user_info['username']
        # Ensure pins.yaml exists and is migrated from any legacy field first.
        self._load_user_pins(username)
        pins = ud.reorder_pins(username, ordered_ids)
        pins = self._normalize_pinned_pages(pins)
        self._save_user_pins(username, pins)
        return jsonify(success=True, pins=pins)

    def _api_user_object_sections_get(self):
        """Get global object page section pin order for current user."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        username = user_info['username']
        pinned = self._load_user_object_section_pins(username)
        return jsonify(success=True, object_section={'pinned': pinned})

    def _api_user_object_sections_toggle(self):
        """Toggle a section id in the global object page pinned list."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json() or {}
        section_id = str(body.get('section_id', '')).strip()
        if not section_id:
            return jsonify(success=False, error='section_id is required'), 400
        section_id = self._normalize_object_section_pins([section_id])
        if not section_id:
            return jsonify(success=False, error='Invalid section_id'), 400
        section_id = section_id[0]

        username = user_info['username']
        pinned = self._load_user_object_section_pins(username)
        if section_id in pinned:
            pinned = [sid for sid in pinned if sid != section_id]
            is_pinned = False
        else:
            pinned.append(section_id)
            is_pinned = True
        self._save_user_object_section_pins(username, pinned)
        return jsonify(success=True,
                       pinned=is_pinned,
                       object_section={'pinned': pinned})

    def _api_user_object_sections_reorder(self):
        """Save explicit order for globally pinned object sections."""
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json() or {}
        ids = body.get('ids', [])
        if not isinstance(ids, list):
            return jsonify(success=False, error='ids must be a list'), 400
        ids = self._normalize_object_section_pins(ids)

        username = user_info['username']
        self._load_user_object_section_pins(username)
        pinned = ud.reorder_object_section_pins(username, ids)
        pinned = self._normalize_object_section_pins(pinned)
        self._save_user_object_section_pins(username, pinned)
        return jsonify(success=True, object_section={'pinned': pinned})

    # -----------------------------------------------------------------
    # Documentation views
    # -----------------------------------------------------------------
    def _doc_edit_view(self, page_ref: str):
        """Show the split-view markdown editor for a doc page."""
        user_info = get_effective_user(session)
        if not user_info:
            flash('You must be logged in to edit documentation.',
                  'warning')
            return redirect(url_for('login'))

        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        # page_ref is the short name (e.g. 'install')
        page_id = f'home.docs.{page_ref}'
        edit_perm = f'edit.doc.{page_ref}'
        if edit_perm not in perms:
            flash('You do not have permission to edit this page.',
                  'warning')
            return redirect(url_for(f'home_docs_{page_ref}'))

        page_def = self.ari_pages.get(page_id)
        if not page_def:
            flash('Page not found.', 'danger')
            return redirect(url_for('home_docs'))

        version = request.args.get('v') or get_default_version()
        raw, html, current_ver = get_doc_content(page_id, version)

        # Find version display name
        version_name = current_ver or 'New'
        for v in get_versions():
            if v['id'] == current_ver:
                version_name = v['name']
                break

        context = {
            'page_id': page_id,
            'page_label': page_def.get('label', ''),
            'page_icon': page_def.get('icon', ''),
            'page_endpoint': page_id_to_endpoint(page_id),
            'doc_ref': page_ref,
            'doc_raw': raw,
            'version_id': current_ver,
            'version_name': version_name,
        }
        # Sidebar for editor too
        context.update(self._build_sidebar_context(page_id, perms, user_info))
        context['doc_versions'] = get_versions()
        context['current_version'] = current_ver

        return render_template('docs/doc_editor.html', **context)

    def _doc_save_view(self, page_ref: str):
        """Save edited markdown content for a doc page."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Not logged in'), 401

        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if f'edit.doc.{page_ref}' not in perms:
            return jsonify(success=False, error='No permission'), 403

        data = request.get_json()
        if not data or 'content' not in data or 'version' not in data:
            return jsonify(success=False, error='Missing data'), 400

        page_id = f'home.docs.{page_ref}'
        save_doc_content(page_id, data['version'], data['content'])
        return jsonify(success=True)

    def _doc_upload_image(self):
        """Handle image upload for the doc editor."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Not logged in'), 401

        page_ref = request.form.get('page_ref', 'unknown')
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if f'edit.doc.{page_ref}' not in perms:
            return jsonify(success=False, error='No permission'), 403

        if 'image' not in request.files:
            return jsonify(success=False, error='No file'), 400

        img = request.files['image']
        if not img.filename:
            return jsonify(success=False, error='Empty filename'), 400

        filename = save_uploaded_image(
            page_ref, img.filename, img.read()
        )
        return jsonify(success=True, filename=filename)

    @staticmethod
    def _doc_image_view(filename: str):
        """Serve uploaded documentation images."""
        return send_from_directory(str(DOC_IMAGES), filename)

    # -----------------------------------------------------------------
    # Object table sub-page + API
    # -----------------------------------------------------------------
    def _ri_object_table_view(self, profile_id):
        """Serve the astrophysical object table page for a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}.object_table'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )

        context = {
            'page_id': page_id,
            'page_label': f'{profile_id}: Object Table',
            'page_icon': 'fa-solid fa-star',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'api_url': '/api/data-portal/object-table',
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/object_table.html', **context)

    def _ri_find_object_view(self, profile_id):
        """Legacy Find Object URL now redirects to object table."""
        return redirect(url_for('ri_object_table', profile_id=profile_id))

    def _api_profiles_list(self):
        """Return list of accessible profile IDs and basic metadata."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()
        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401
        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profiles = []
        for prof in accessible:
            profiles.append({
                'profile_id': prof['profile_id'],
                'instrument': prof.get('instrument', ''),
                'label': prof.get('label', prof['profile_id']),
            })
        return jsonify(success=True, profiles=profiles)

    def _api_object_table(self):
        """Return object table rows for a profile, filtered by science group."""
        import json as _json
        import re
        import math
        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))

        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        if not profile_id:
            return jsonify(success=False, error='Missing profile_id'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']

        # Determine which run_ids the user may see
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        # Locate the JSON file
        tasks_dir = base_dir / 'tasks' / instrument
        # New layout: tasks/<instrument>/<profile>/object_table.json
        json_path = tasks_dir / profile_id / 'object_table.json'

        # Legacy layout fallback: tasks/<instrument>/object_table_<profile>.json
        if not json_path.exists():
            legacy_path = tasks_dir / f'object_table_{profile_id}.json'
            if legacy_path.exists():
                json_path = legacy_path

        if not json_path.exists():
            return jsonify(
                success=True,
                rows=[],
                columns=[],
                generated_at=None,
                total_rows=0,
                message='No object table data found. '
                        'Run the object table task first.',
            )

        try:
            with open(json_path, encoding='utf-8') as f:
                data = _json.load(f)
        except Exception as exc:
            return jsonify(
                success=False, error=f'Failed to load data: {exc}'
            ), 500

        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}
        all_rows = data.get('rows', [])
        generated_at = (data.get('generated_at')
                        or metadata.get('GENERATED_AT'))
        raw_column_meta = metadata.get('COLUMN_META', {})
        if not isinstance(raw_column_meta, dict):
            raw_column_meta = {}

        hidden_by_meta = {
            col for col, meta in raw_column_meta.items()
            if isinstance(meta, dict) and bool(meta.get('hidden', False))
        }

        # Filter rows based on accessible run_ids
        filtered = []
        for row in all_rows:
            raw = str(row.get('RUN_ID', '') or '')
            row_rids = {r.strip() for r in raw.split(',') if r.strip()}
            if row_rids & accessible_run_ids:
                filtered.append(row)

        # Optional dynamic finder filters.
        find_only = str(request.args.get('find_only', '')).strip().lower() in {
            '1', 'true', 'yes', 'on'
        }
        name_query = str(request.args.get('name_query', '') or '').strip()

        ra_raw = str(request.args.get('ra', '') or '').strip()
        dec_raw = str(request.args.get('dec', '') or '').strip()
        sep_raw = str(request.args.get('separation', '') or '').strip()
        sep_unit = str(request.args.get('separation_unit', 'arcsec') or '').strip().lower()

        def _norm_variants(value: str):
            text = str(value or '').strip().lower()
            if not text:
                return set()
            variants = {
                re.sub(r'[^a-z0-9]+', '', text),
                re.sub(r'[^a-z0-9]+', '', text.replace('+', 'p').replace('-', 'm')),
            }
            return {v for v in variants if v}

        def _name_match_row(row, query):
            qvars = _norm_variants(query)
            if not qvars:
                return True
            names = [str(row.get('OBJNAME', '') or '')]
            aliases = str(row.get('ALIASES', '') or '')
            if aliases:
                names.extend(part.strip() for part in aliases.split('|') if part.strip())

            for name in names:
                nvars = _norm_variants(name)
                if any(qv in nv for qv in qvars for nv in nvars):
                    return True
            return False

        def _row_ra_dec_deg(row):
            ra_keys = ('RA [Deg]', 'RA', 'OBJRA', 'OBJ_RA')
            dec_keys = ('Dec [Deg]', 'DEC', 'Dec', 'OBJDEC', 'OBJ_DEC')
            ra_val = None
            dec_val = None
            for key in ra_keys:
                if key in row:
                    try:
                        ra_val = float(row.get(key))
                        break
                    except Exception:
                        continue
            for key in dec_keys:
                if key in row:
                    try:
                        dec_val = float(row.get(key))
                        break
                    except Exception:
                        continue
            if ra_val is None or dec_val is None:
                return None
            return ra_val, dec_val

        has_name_filter = len(name_query) >= 1
        has_coord_filter = bool(ra_raw and dec_raw and sep_raw)

        ra0 = dec0 = sep_deg = None
        if has_coord_filter:
            try:
                ra0 = float(ra_raw)
                dec0 = float(dec_raw)
                sep = float(sep_raw)
            except ValueError:
                return jsonify(success=False,
                               error='Invalid RA/Dec/separation values.'), 400

            if sep_unit == 'deg':
                sep_deg = sep
            elif sep_unit == 'arcmin':
                sep_deg = sep / 60.0
            else:
                sep_deg = sep / 3600.0

        if find_only and not has_name_filter and not has_coord_filter:
            return jsonify(
                success=True,
                rows=[],
                columns=[],
                column_meta={},
                generated_at=generated_at,
                total_rows=len(all_rows),
                message='Type at least 1 character for object search '
                        'or provide RA/Dec + separation.',
            )

        if has_name_filter:
            filtered = [row for row in filtered if _name_match_row(row, name_query)]

        if has_coord_filter and sep_deg is not None:
            ra0r = math.radians(ra0)
            dec0r = math.radians(dec0)
            cos_sep_max = math.cos(math.radians(max(sep_deg, 0.0)))

            coord_filtered = []
            for row in filtered:
                row_coords = _row_ra_dec_deg(row)
                if row_coords is None:
                    continue
                ra1, dec1 = row_coords
                ra1r = math.radians(ra1)
                dec1r = math.radians(dec1)
                cos_sep = (
                    math.sin(dec0r) * math.sin(dec1r)
                    + math.cos(dec0r) * math.cos(dec1r) * math.cos(ra0r - ra1r)
                )
                if cos_sep >= cos_sep_max:
                    coord_filtered.append(row)
            filtered = coord_filtered

        # Build column list (exclude RUN_ID)
        skip = {'RUN_ID', 'run_id', 'ALL_RUN_IDS', 'all_run_ids'}
        columns = [c for c in (all_rows[0].keys() if all_rows else [])
                   if c not in skip and c not in hidden_by_meta]

        column_meta = {
            col: dict(meta)
            for col, meta in raw_column_meta.items()
            if (col not in skip
                    and col not in hidden_by_meta
                    and isinstance(meta, dict))
        }
        if 'OBJNAME' in columns and 'OBJNAME' not in column_meta:
            column_meta['OBJNAME'] = {
                'sortable': True,
                'filterable': True,
                'removable': False,
                'default': True,
                'type': 'string',
            }

        # Strip skipped columns from each row
        clean_rows = [
            {k: v for k, v in row.items()
             if k not in skip and k not in hidden_by_meta}
            for row in filtered
        ]

        def _date_only(value):
            """Return date string in YYYY-MM-DD form when possible."""
            if value is None:
                return value
            text = str(value).strip()
            if not text:
                return value
            if 'T' in text:
                return text.split('T', 1)[0]
            if ' ' in text:
                return text.split(' ', 1)[0]
            return text

        # Keep object-table dates compact (no HH:MM:SS in table display).
        _date_cols = {'last obs', 'latest obs', 'last modified'}
        for row in clean_rows:
            for col in _date_cols:
                if col in row:
                    row[col] = _date_only(row.get(col))

        # ── File-count columns (parallel ftable reads) ────────────────────
        import concurrent.futures as _futures

        _FKIND_COLS = [
            ('raw',   'raw files'),
            ('pp',    'pp files'),
            ('ext',   'ext files'),
            ('tcorr', 'tcorr files'),
            ('ccf',   'ccf files'),
            ('efits', 'e.fits files'),
            ('tfits', 't.fits files'),
            ('lbl',   'lbl files'),
        ]

        _objects_dir = tasks_dir / profile_id / 'objects'

        def _read_ftable(objname, fkind):
            """Return (N, M): N = user-accessible rows, M = total rows."""
            _path = _objects_dir / f'ftable_{fkind}_{objname}.json'
            try:
                with open(_path, encoding='utf-8') as _fh:
                    _d = _json.load(_fh)
                _rows = _d.get('rows') or []
                _m = len(_rows)
                _n = sum(
                    1 for _r in _rows
                    if str(_r.get('KW_RUN_ID', '') or '') in accessible_run_ids
                )
                return _n, _m
            except FileNotFoundError:
                return None, None
            except Exception:
                return None, None

        # Build full task list: every (objname, fkind) pair
        _ftable_tasks = [
            (row.get('OBJNAME', ''), fkind)
            for row in clean_rows
            for fkind, _ in _FKIND_COLS
            if row.get('OBJNAME', '')
        ]

        # Read all files in parallel
        _ftable_results = {}  # (objname, fkind) -> (N, M)
        if _ftable_tasks:
            with _futures.ThreadPoolExecutor(
                max_workers=min(32, len(_ftable_tasks))
            ) as _pool:
                _fmap = {
                    _pool.submit(_read_ftable, _obj, _fki): (_obj, _fki)
                    for _obj, _fki in _ftable_tasks
                }
                for _fut in _futures.as_completed(_fmap):
                    _obj, _fki = _fmap[_fut]
                    try:
                        _n_res, _m_res = _fut.result()
                    except Exception:
                        _n_res, _m_res = None, None
                    _ftable_results[(_obj, _fki)] = (_n_res, _m_res)

        # Attach counts to rows
        for row in clean_rows:
            _objname = row.get('OBJNAME', '')
            for _fkind, _colname in _FKIND_COLS:
                _n_val, _m_val = _ftable_results.get(
                    (_objname, _fkind), (None, None)
                )
                row[_colname] = (
                    None if _n_val is None else f'{_n_val} ({_m_val})'
                )

        # Extend columns and column_meta with the new file-count columns
        _fcount_cols = [_colname for _, _colname in _FKIND_COLS]
        columns = list(columns) + _fcount_cols
        column_meta.update({
            _colname: {
                'sortable': True,
                'filterable': True,
                'removable': True,
                'default': True,
                'hidden': False,
                'type': 'count',
            }
            for _, _colname in _FKIND_COLS
        })
        # ── End file-count columns ────────────────────────────────────────

        payload = dict(
            success=True,
            rows=clean_rows,
            columns=columns,
            column_meta=column_meta,
            generated_at=generated_at,
            total_rows=len(all_rows),
        )
        if find_only and not clean_rows and (has_name_filter or has_coord_filter):
            payload['message'] = 'No objects matched the current search criteria.'

        return jsonify(**payload)

    def _ri_obs_table_view(self, profile_id):
        """Serve the observation table page for a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}.obs_table'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )

        context = {
            'page_id': page_id,
            'page_label': f'{profile_id}: Observation Table',
            'page_icon': 'fa-solid fa-binoculars',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'api_url': '/api/data-portal/obs-table',
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/obs_table.html', **context)

    def _ri_object_page_view(self, profile_id, objname):
        """Serve placeholder page for a specific object within a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_tpl_id = 'home.data_portal.{apero_profile}.{objname}'
        page_tpl = self._page_templates.get(page_tpl_id, {})
        label_tpl = str(page_tpl.get('label', '{apero profile}: {objname}'))
        page_label = (
            label_tpl
            .replace('{apero profile}', profile_id)
            .replace('{objname}', objname)
        )
        page_icon = page_tpl.get('icon', 'fa-solid fa-star')

        page_id = f'home.data_portal.{profile_id}.{objname}'

        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
            objname=objname,
        )

        # Check whether a finder chart is already cached
        finder_cached = False
        try:
            from apero_ri.core.plot_cache import (
                load_cache_config, resolve_cache_root, is_cache_enabled,
                get_finder_cached, _profile_dir, _load_meta,
                _db_fingerprint_matches,
            )
            base_dir = Path(self.args.data_dir
                            or str(Path.home() / '.ari'))
            cfg = load_cache_config(base_dir)
            if is_cache_enabled(cfg=cfg):
                cache_root = resolve_cache_root(base_dir, cfg)
                profile_data = profile.get('data') or {}
                pdir = _profile_dir(cache_root, profile['instrument'],
                                    profile_id)
                meta = _load_meta(pdir)
                db_upd = profile_data.get('database-update', {})
                if (isinstance(db_upd, dict) and db_upd
                        and _db_fingerprint_matches(meta, db_upd)):
                    fc_hit = get_finder_cached(
                        cache_root, profile['instrument'],
                        profile_id, objname)
                    finder_cached = fc_hit is not None
        except Exception:
            pass

        context = {
            'page_id': page_id,
            'page_label': page_label,
            'page_icon': page_icon,
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'objname': objname,
            'api_url': '/api/data-portal/object-page',
            'finder_chart_cached': finder_cached,
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/object_page.html', **context)

    def _api_object_page(self):
        """Return object-page data for a profile/object, filtered by science group."""
        import json as _json

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))

        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        if not profile_id or not objname:
            return jsonify(
                success=False,
                error='Missing profile_id or objname',
            ), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        tasks_dir = base_dir / 'tasks' / instrument
        profile_dir = tasks_dir / profile_id
        object_table_path = profile_dir / 'object_table.json'

        if not object_table_path.exists():
            legacy_path = tasks_dir / f'object_table_{profile_id}.json'
            if legacy_path.exists():
                object_table_path = legacy_path

        if not object_table_path.exists():
            return jsonify(
                success=False,
                error='No object table data found for this profile.',
            ), 404

        try:
            with open(object_table_path, encoding='utf-8') as _fh:
                object_table = _json.load(_fh)
        except Exception as exc:
            return jsonify(
                success=False,
                error=f'Failed to load object table: {exc}',
            ), 500

        all_rows = object_table.get('rows', [])

        def _row_accessible(row):
            raw = str(row.get('RUN_ID', '') or '')
            row_rids = {r.strip() for r in raw.split(',') if r.strip()}
            return bool(row_rids & accessible_run_ids)

        obj_row = None
        for row in all_rows:
            name = str(row.get('OBJNAME', '') or '')
            if name.lower() == objname.lower() and _row_accessible(row):
                obj_row = row
                break

        if obj_row is None:
            return jsonify(
                success=False,
                error='Object not found or not accessible for this user.',
            ), 404

        profile_data = profile.get('data') if isinstance(profile, dict) else {}
        if not isinstance(profile_data, dict):
            profile_data = {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        path_lbl = str(
            self._profile_get_path(profile_data, 'PATH_LBL', '') or ''
        ).strip()

        sections = build_object_page_stats(
            base_dir=base_dir,
            instrument=instrument,
            profile_id=profile_id,
            obj_row=obj_row,
            objname=objname,
            accessible_run_ids=accessible_run_ids,
            instrument_profile_file=instrument_profile_file,
            path_lbl=path_lbl,
        )
        labels = sections.pop('labels', {})

        return jsonify(
            success=True,
            object_name=obj_row.get('OBJNAME', objname),
            profile_id=profile_id,
            generated_at=object_table.get('generated_at'),
            sections=sections,
            labels=labels,
        )

    @staticmethod
    def _rid_cache_tag(accessible_run_ids):
        """Return a short hash of the accessible run_id set for cache keys."""
        import hashlib
        blob = '|'.join(sorted(accessible_run_ids)).encode()
        return hashlib.md5(blob).hexdigest()[:8]

    @staticmethod
    def _filter_plot_rows(htable_rows, ftable_dict, accessible_run_ids):
        """Filter htable and ftable rows by accessible run_ids.

        Parameters
        ----------
        htable_rows : list of dict
        ftable_dict : dict of {label: list of dict}
        accessible_run_ids : set of str

        Returns
        -------
        filtered_htable : list of dict
        filtered_ftables : dict of {label: list of dict}
        """
        from apero_ri.core.basket_funcs import filter_accessible_rows
        filtered_ftables = {}
        accessible_ids = set()
        for label, rows in ftable_dict.items():
            filt = filter_accessible_rows(rows, accessible_run_ids)
            filtered_ftables[label] = filt
            for r in filt:
                ident = str(r.get('IDENTIFIER', '') or '').strip()
                if ident:
                    accessible_ids.add(ident)
        if accessible_ids:
            filtered_htable = [
                r for r in htable_rows
                if str(r.get('IDENTIFIER', '') or '').strip()
                in accessible_ids
            ]
        else:
            filtered_htable = list(htable_rows)
        return filtered_htable, filtered_ftables

    def _api_object_plots(self):
        """Return Bokeh JSON plot payloads (SNR, BERV, spec, CCF) for the object page."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        plot_group = str(request.args.get('plot_group', 'all') or 'all').strip().lower()
        valid_groups = {'all', 'spectrum', 'ccf', 'ccf_rv', 'ccf_profile', 'time_series'}
        if plot_group not in valid_groups:
            return jsonify(success=False,
                           error=('Invalid plot_group. Use one of: '
                                  'all, spectrum, ccf, ccf_rv, ccf_profile, time_series')), 400
        if not profile_id or not objname:
            return jsonify(
                success=False,
                error='Missing profile_id or objname',
            ), 400

        vsys_ms = None
        vsys_ms_str = request.args.get('vsys_ms', '').strip()
        if vsys_ms_str:
            try:
                vsys_ms = float(vsys_ms_str)
            except ValueError:
                pass

        ccf_mjd_start = None
        ccf_mjd_start_str = request.args.get('ccf_mjd_start', '').strip()
        if ccf_mjd_start_str:
            try:
                ccf_mjd_start = float(ccf_mjd_start_str)
            except ValueError:
                pass

        ccf_mjd_end = None
        ccf_mjd_end_str = request.args.get('ccf_mjd_end', '').strip()
        if ccf_mjd_end_str:
            try:
                ccf_mjd_end = float(ccf_mjd_end_str)
            except ValueError:
                pass
        ccf_nobs = 100
        ccf_nobs_str = request.args.get('ccf_nobs', '').strip()
        if ccf_nobs_str:
            try:
                ccf_nobs = max(1, min(1000, int(float(ccf_nobs_str))))
            except ValueError:
                ccf_nobs = 100
        if (ccf_mjd_start is not None and ccf_mjd_end is not None
                and ccf_mjd_start > ccf_mjd_end):
            ccf_mjd_start, ccf_mjd_end = ccf_mjd_end, ccf_mjd_start
        force_regen = bool(str(request.args.get('_ts', '')).strip())

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        objects_dir = base_dir / 'tasks' / instrument / profile_id / 'objects'

        # --- Plot cache: try to serve from cache first ---
        from apero_ri.core.plot_cache import check_and_serve
        rid_tag = self._rid_cache_tag(accessible_run_ids)
        cache_key = (f'{plot_group}__{objname}__{rid_tag}' if vsys_ms is None
                     else f'{plot_group}__{objname}__vsys{vsys_ms}__{rid_tag}')
        if plot_group in {'all', 'ccf', 'ccf_profile'} and (
                ccf_mjd_start is not None or ccf_mjd_end is not None):
            cache_key += (
                f'__ccfmjd_{ccf_mjd_start if ccf_mjd_start is not None else ""}'
                f'_{ccf_mjd_end if ccf_mjd_end is not None else ""}'
            )
        if plot_group in {'all', 'ccf', 'ccf_profile'}:
            cache_key += f'__ccfnobs_{int(ccf_nobs)}'
        if plot_group in {'all', 'time_series'}:
            cache_key += '__tsaxis_v2'
        if not force_regen:
            cached = check_and_serve(
                base_dir, instrument, profile_id,
                'object_plots', cache_key, aparams=profile_data)
            if cached is not None:
                self.logger.info(
                    'OBJECT_PLOTS cache_hit profile=%s object=%s group=%s',
                    profile_id, objname, plot_group,
                )
                return jsonify(**cached)

        htable_rows = load_object_htable_rows(objects_dir, objname)
        preset = load_object_preset(instrument_profile_file)
        obj_props = load_object_table_row(objects_dir, objname)

        # Load only file tables needed for the requested plot group.
        need_ext = plot_group in {'all', 'spectrum', 'time_series'}
        need_tcorr = plot_group in {'all', 'spectrum'}
        need_ccf = plot_group in {'all', 'ccf', 'ccf_profile'}
        ftable_ext_rows = (load_object_ftable_rows(objects_dir, objname, 'ext')
                           if need_ext else [])
        ftable_tcorr_rows = (load_object_ftable_rows(objects_dir, objname, 'tcorr')
                             if need_tcorr else [])
        ftable_ccf_rows = (load_object_ftable_rows(objects_dir, objname, 'ccf')
                          if need_ccf else [])

        htable_rows, ftables = self._filter_plot_rows(
            htable_rows,
            {'ext': ftable_ext_rows, 'tcorr': ftable_tcorr_rows,
             'ccf': ftable_ccf_rows},
            accessible_run_ids,
        )
        ftable_ext_rows = ftables['ext']
        ftable_tcorr_rows = ftables['tcorr']
        ftable_ccf_rows = ftables['ccf']

        # Build path dict for file resolution
        path_red = str(
            self._profile_get_path(profile_data, 'PATH_RED', '') or '')
        path_lbl = str(
            self._profile_get_path(profile_data, 'PATH_LBL', '') or '')
        paths = {'PATH_RED': path_red, 'PATH_LBL': path_lbl}

        from apero_ri.plots.plot_objects import build_snr_plot_json
        from apero_ri.plots.plot_objects import build_berv_plot_json
        from apero_ri.plots.plot_objects import build_spec_plot_json
        from apero_ri.plots.plot_objects import build_ccf_rv_plot_json
        from apero_ri.plots.plot_objects import build_ccf_profile_plot_json
        from apero_ri.plots.plot_objects import build_ts_snr_plot_json
        from apero_ri.plots.plot_objects import build_ts_airmass_plot_json

        _no_plot = {'has_plot': False, 'message': 'Plot build failed'}
        timings_ms = {}

        def _timed_build(name, func):
            t0 = time.perf_counter()
            ok = True
            try:
                payload = func()
            except Exception:
                payload = dict(_no_plot)
                ok = False
            dt_ms = (time.perf_counter() - t0) * 1000.0
            timings_ms[name] = round(dt_ms, 2)
            self.logger.info(
                'OBJECT_PLOTS build profile=%s object=%s group=%s plot=%s ok=%s ms=%.2f',
                profile_id, objname, plot_group, name, ok, dt_ms,
            )
            return payload

        result = dict(success=True, plot_group=plot_group)

        if plot_group in {'all', 'spectrum'}:
            result['snr'] = _timed_build(
                'snr', lambda: build_snr_plot_json(htable_rows, preset))
            result['berv'] = _timed_build(
                'berv', lambda: build_berv_plot_json(
                    htable_rows, vsys_ms, preset, obj_props=obj_props))
            result['spec'] = _timed_build(
                'spec', lambda: build_spec_plot_json(
                    htable_rows, ftable_ext_rows, ftable_tcorr_rows,
                    paths, preset))

        if plot_group in {'all', 'ccf_rv'}:
            result['ccf_rv'] = _timed_build(
                'ccf_rv', lambda: build_ccf_rv_plot_json(
                    htable_rows,
                    preset,
                ))

        if plot_group in {'all', 'ccf', 'ccf_profile'}:
            ccf_profile_payload = _timed_build(
                'ccf_profile', lambda: build_ccf_profile_plot_json(
                    htable_rows,
                    ftable_ccf_rows,
                    paths,
                    preset,
                    ccf_mjd_start=ccf_mjd_start,
                    ccf_mjd_end=ccf_mjd_end,
                    ccf_nobs=ccf_nobs,
                ))
            result['ccf_profile'] = ccf_profile_payload
            if plot_group == 'ccf':
                # Backward compatibility for any client still expecting "ccf".
                result['ccf'] = ccf_profile_payload

        if plot_group in {'all', 'time_series'}:
            result['ts_snr'] = _timed_build(
                'ts_snr', lambda: build_ts_snr_plot_json(
                    htable_rows, ftable_ext_rows, preset))
            result['ts_airmass'] = _timed_build(
                'ts_airmass', lambda: build_ts_airmass_plot_json(
                    htable_rows, ftable_ext_rows, preset))
        result['updated_at'] = datetime.now(timezone.utc).isoformat()
        result['server_timings_ms'] = timings_ms

        # Store in cache (fire-and-forget; failures are non-fatal)
        try:
            from apero_ri.core.plot_cache import (
                is_cache_enabled, resolve_cache_root, put_cached,
                _profile_dir, _load_meta, _save_meta, load_cache_config,
            )
            cfg = load_cache_config(base_dir)
            if cfg.get('enabled'):
                cache_root = resolve_cache_root(base_dir, cfg)
                put_cached(cache_root, instrument, profile_id,
                           'object_plots', cache_key, result)
                pdir = _profile_dir(cache_root, instrument, profile_id)
                meta = _load_meta(pdir)
                db_upd = profile_data.get('database-update', {})
                if isinstance(db_upd, dict) and db_upd:
                    meta['db_updates'] = dict(db_upd)
                from datetime import datetime as _dt, timezone as _tz
                meta['last_cached'] = _dt.now(_tz.utc).isoformat()
                _save_meta(pdir, meta)
        except Exception:
            pass

        self.logger.info(
            'OBJECT_PLOTS done profile=%s object=%s group=%s total_ms=%.2f rows=%d',
            profile_id,
            objname,
            plot_group,
            sum(timings_ms.values()),
            len(htable_rows),
        )

        return jsonify(**result)

    def _api_object_lbl_plots(self):
        """Return Bokeh JSON plot payloads for all LBL flavors of an object."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        if not profile_id or not objname:
            return jsonify(
                success=False,
                error='Missing profile_id or objname',
            ), 400
        force_regen = bool(str(request.args.get('_ts', '')).strip())

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        objects_dir = base_dir / 'tasks' / instrument / profile_id / 'objects'

        # --- LBL cache (keyed by run_id access level) ---
        from apero_ri.core.plot_cache import check_and_serve
        rid_tag = self._rid_cache_tag(accessible_run_ids)
        cache_key = f'{objname}__{rid_tag}'
        if not force_regen:
            cached = check_and_serve(
                base_dir, instrument, profile_id,
                'lbl_plots', cache_key, aparams=profile_data)
            if cached is not None:
                return jsonify(**cached)

        preset = load_object_preset(instrument_profile_file)
        path_lbl = str(
            self._profile_get_path(profile_data, 'PATH_LBL', '') or '')

        ftable_lbl_rdb_rows = load_object_ftable_rows(
            objects_dir, objname, 'lbl_rdb'
        )
        # Filter by accessible run_ids
        from apero_ri.core.basket_funcs import filter_accessible_rows
        ftable_lbl_rdb_rows = filter_accessible_rows(
            ftable_lbl_rdb_rows, accessible_run_ids
        )

        from apero_ri.plots.plot_objects import build_lbl_plots_json
        try:
            plots = build_lbl_plots_json(ftable_lbl_rdb_rows, path_lbl, preset)
        except Exception:
            plots = {}

        result = dict(
            success=True,
            plots=plots,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            from apero_ri.core.plot_cache import (
                load_cache_config, resolve_cache_root, put_cached,
            )
            cfg = load_cache_config(base_dir)
            if cfg.get('enabled'):
                cache_root = resolve_cache_root(base_dir, cfg)
                put_cached(cache_root, instrument, profile_id,
                           'lbl_plots', cache_key, result)
        except Exception:
            pass

        return jsonify(**result)

    def _api_filename_plot(self):
        """Return a Bokeh JSON plot for a single file (filename-click feature)."""
        from apero_ri.base.base import BLOCK_KIND as _BLOCK_KIND_MAP
        from apero_ri.plots.plots_filename import build_filename_plot_json

        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        block_kind = request.args.get('block_kind', '').strip().lower()
        obs_dir = request.args.get('obs_dir', '').strip()
        filename = request.args.get('filename', '').strip()
        kw_output = request.args.get('kw_output', '').strip()
        kw_fiber = (request.args.get('kw_fiber', '').strip() or 'AB')
        kw_run_id = request.args.get('kw_run_id', '').strip()

        if not all([profile_id, block_kind, filename, kw_output]):
            return jsonify(success=False, error='Missing required params'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        # Validate run_id access
        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )
        if kw_run_id and kw_run_id not in accessible_run_ids:
            return jsonify(
                success=False,
                error='Access denied for this run_id',
            ), 403

        path_key = _BLOCK_KIND_MAP.get(block_kind)
        if not path_key:
            return jsonify(
                success=False,
                error=f'Unknown block_kind: {block_kind}',
            ), 400

        profile_data = profile.get('data') or {}
        base_path_str = str(
            self._profile_get_path(profile_data, path_key, '') or ''
        ).strip()
        if not base_path_str:
            return jsonify(
                success=False,
                error=f'No path configured for {path_key}',
            ), 400

        try:
            base_path = Path(base_path_str).resolve()
            obs_part = Path(obs_dir.strip('/')) if obs_dir else Path('')
            filepath = (base_path / obs_part / filename).resolve()
            # security: ensure we stay inside the declared base path
            filepath.relative_to(base_path)
        except (ValueError, OSError) as exc:
            return jsonify(success=False, error=f'Path error: {exc}'), 400

        if not filepath.is_file():
            return jsonify(
                success=False,
                has_plot=False,
                message=f'File not found: {filename}',
            ), 404

        try:
            result = build_filename_plot_json(filepath, kw_output, kw_fiber)
        except Exception:
            result = {'has_plot': False, 'message': 'Plot build failed'}
        return jsonify(success=True, **result)

    def _ri_object_plot_max_view(self, profile_id, objname, plot_key):
        """Serve a standalone maximized object plot page (SNR, BERV, spec, or CCF)."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.', 'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        vsys_ms = None
        vsys_ms_str = request.args.get('vsys_ms', '').strip()
        if vsys_ms_str:
            try:
                vsys_ms = float(vsys_ms_str)
            except ValueError:
                pass

        ccf_mjd_start = None
        ccf_mjd_start_str = request.args.get('ccf_mjd_start', '').strip()
        if ccf_mjd_start_str:
            try:
                ccf_mjd_start = float(ccf_mjd_start_str)
            except ValueError:
                pass

        ccf_mjd_end = None
        ccf_mjd_end_str = request.args.get('ccf_mjd_end', '').strip()
        if ccf_mjd_end_str:
            try:
                ccf_mjd_end = float(ccf_mjd_end_str)
            except ValueError:
                pass
        ccf_nobs = 100
        ccf_nobs_str = request.args.get('ccf_nobs', '').strip()
        if ccf_nobs_str:
            try:
                ccf_nobs = max(1, min(1000, int(float(ccf_nobs_str))))
            except ValueError:
                ccf_nobs = 100
        if (ccf_mjd_start is not None and ccf_mjd_end is not None
                and ccf_mjd_start > ccf_mjd_end):
            ccf_mjd_start, ccf_mjd_end = ccf_mjd_end, ccf_mjd_start

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        objects_dir = base_dir / 'tasks' / instrument / profile_id / 'objects'

        htable_rows = load_object_htable_rows(objects_dir, objname)
        preset = load_object_preset(instrument_profile_file)
        obj_props = load_object_table_row(objects_dir, objname)

        # Pre-load ftable rows that may be needed and filter by run_id
        _ftable_ext = load_object_ftable_rows(objects_dir, objname, 'ext')
        _ftable_tcorr = load_object_ftable_rows(objects_dir, objname, 'tcorr')
        _ftable_ccf = load_object_ftable_rows(objects_dir, objname, 'ccf')
        _ftable_lbl = load_object_ftable_rows(objects_dir, objname, 'lbl_rdb')

        htable_rows, ftables = self._filter_plot_rows(
            htable_rows,
            {'ext': _ftable_ext, 'tcorr': _ftable_tcorr,
             'ccf': _ftable_ccf, 'lbl_rdb': _ftable_lbl},
            accessible_run_ids,
        )
        _ftable_ext = ftables['ext']
        _ftable_tcorr = ftables['tcorr']
        _ftable_ccf = ftables['ccf']
        _ftable_lbl = ftables['lbl_rdb']

        from apero_ri.plots.plot_objects import build_snr_plot_components
        from apero_ri.plots.plot_objects import build_berv_plot_components
        from apero_ri.plots.plot_objects import build_spec_plot_components
        from apero_ri.plots.plot_objects import build_ccf_rv_plot_components
        from apero_ri.plots.plot_objects import build_ccf_profile_plot_components
        from apero_ri.plots.plot_objects import build_ts_snr_plot_components
        from apero_ri.plots.plot_objects import build_ts_airmass_plot_components

        safe_key = str(plot_key or '').strip().lower()
        if safe_key == 'snr':
            plot_payload = build_snr_plot_components(htable_rows, preset)
            display_name = 'SNR vs Time'
        elif safe_key == 'berv':
            plot_payload = build_berv_plot_components(
                htable_rows, vsys_ms, preset,
                                                      obj_props=obj_props)
            display_name = 'BERV Coverage'
        elif safe_key == 'spec':
            path_red = str(
            self._profile_get_path(profile_data, 'PATH_RED', '') or '')
            paths = {'PATH_RED': path_red}
            plot_payload = build_spec_plot_components(
                htable_rows, _ftable_ext, _ftable_tcorr, paths,
                preset, maximize=True)
            display_name = 'Median Spectrum'
        elif safe_key == 'ccf_rv':
            plot_payload = build_ccf_rv_plot_components(
                htable_rows,
                preset,
            )
            display_name = 'CCF RV vs Time'
        elif safe_key in {'ccf', 'ccf_profile'}:
            path_red = str(
            self._profile_get_path(profile_data, 'PATH_RED', '') or '')
            paths = {'PATH_RED': path_red}
            plot_payload = build_ccf_profile_plot_components(
                htable_rows,
                _ftable_ccf,
                paths,
                preset,
                ccf_mjd_start=ccf_mjd_start,
                ccf_mjd_end=ccf_mjd_end,
                ccf_nobs=ccf_nobs,
            )
            display_name = 'Median CCF Profile'
        elif safe_key == 'ts_snr':
            plot_payload = build_ts_snr_plot_components(
                htable_rows, _ftable_ext, preset)
            display_name = 'SNR per Night'
        elif safe_key == 'ts_airmass':
            plot_payload = build_ts_airmass_plot_components(
                htable_rows, _ftable_ext, preset)
            display_name = 'Airmass per Night'
        elif safe_key == 'lbl':
            from apero_ri.plots.plot_objects import build_lbl_plot_components
            lbl_file = str(request.args.get('lbl_file', '')).strip()
            path_lbl = str(
                self._profile_get_path(profile_data, 'PATH_LBL', '') or '')
            plot_payload = build_lbl_plot_components(
                _ftable_lbl, path_lbl, preset, lbl_file)
            display_name = f'LBL Velocity — {lbl_file}' if lbl_file else 'LBL Velocity'
        elif safe_key == 'finder':
            band_idx_str = str(request.args.get('band_idx', '0')).strip()
            try:
                band_idx = int(band_idx_str)
            except ValueError:
                band_idx = 0
            plot_payload = self._build_finder_max_payload(
                profile, objname, obj_props, preset, band_idx)
            display_name = 'Finder Chart'
        elif safe_key.startswith('debug_'):
            debug_plot_key = safe_key[6:]  # strip 'debug_' prefix
            from apero_ri.plots.plot_debug import generate_single_debug_plot
            from apero_ri.plots.plot_debug import DEBUG_PLOT_DEFS
            paths = None
            if debug_plot_key == 'tcorr_map':
                path_red = str(
                    self._profile_get_path(
                        profile_data, 'PATH_RED', '') or '')
                paths = {'PATH_RED': path_red}
            plot_payload = generate_single_debug_plot(
                debug_plot_key, htable_rows, objname, preset,
                _ftable_tcorr if debug_plot_key == 'tcorr_map' else None,
                paths)
            defn = DEBUG_PLOT_DEFS.get(debug_plot_key, {})
            display_name = defn.get('title', debug_plot_key)
        else:
            plot_payload = {'has_plot': False, 'script': '', 'div': '',
                            'message': f'Unknown plot key: {plot_key}'}
            display_name = str(plot_key)

        return_url = url_for(
            'ri_object_page',
            profile_id=profile_id,
            objname=objname,
        )
        context = {
            'profile': profile,
            'objname': objname,
            'plot_key': safe_key,
            'display_name': display_name,
            'plot_payload': plot_payload,
            'return_url': return_url,
        }
        return render_template('data_portal/object_plot_max.html', **context)

    # -----------------------------------------------------------------
    # Finder chart helpers
    # -----------------------------------------------------------------

    def _api_finder_chart(self):
        """Generate finder charts on demand (called via AJAX)."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()
        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        if not profile_id or not objname:
            return jsonify(success=False,
                           error='Missing profile_id or objname'), 400
        force_regen = bool(str(request.args.get('_ts', '')).strip())

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        objects_dir = (base_dir / 'tasks' / instrument
                       / profile_id / 'objects')

        obj_props = load_object_table_row(objects_dir, objname)
        preset = load_object_preset(instrument_profile_file)

        # --- Finder chart cache ---
        from apero_ri.core.plot_cache import (
            load_cache_config, resolve_cache_root, is_cache_enabled,
            get_finder_cached, put_finder_cached,
            _profile_dir, _load_meta, _save_meta,
            _db_fingerprint_matches,
        )
        cfg = load_cache_config(base_dir)
        if is_cache_enabled(cfg=cfg):
            cache_root = resolve_cache_root(base_dir, cfg)
            pdir = _profile_dir(cache_root, instrument, profile_id)
            meta = _load_meta(pdir)
            db_upd = profile_data.get('database-update', {})
            if isinstance(db_upd, dict) and db_upd and _db_fingerprint_matches(meta, db_upd):
                hit = get_finder_cached(cache_root, instrument, profile_id, objname)
                if hit is not None:
                    return jsonify(**hit)

        from apero_ri.plots.plot_find import generate_finder_charts
        result = generate_finder_charts(obj_props, preset)

        try:
            if is_cache_enabled(cfg=cfg):
                cache_root = resolve_cache_root(base_dir, cfg)
                put_finder_cached(cache_root, instrument, profile_id,
                                  objname, result)
                pdir = _profile_dir(cache_root, instrument, profile_id)
                meta = _load_meta(pdir)
                db_upd = profile_data.get('database-update', {})
                if isinstance(db_upd, dict) and db_upd:
                    meta['db_updates'] = dict(db_upd)
                from datetime import datetime as _dt, timezone as _tz
                meta['last_cached'] = _dt.now(_tz.utc).isoformat()
                _save_meta(pdir, meta)
        except Exception:
            pass

        return jsonify(**result)

    def _api_debug_plots(self):
        """Generate debug plots on demand (called via AJAX)."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()
        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        if not profile_id or not objname:
            return jsonify(success=False,
                           error='Missing profile_id or objname'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = next(
            (p for p in accessible if p['profile_id'] == profile_id), None
        )
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or ''
        ).strip()

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        objects_dir = (base_dir / 'tasks' / instrument
                       / profile_id / 'objects')

        # --- Debug plots cache (keyed by run_id access level) ---
        from apero_ri.core.plot_cache import check_and_serve
        rid_tag = self._rid_cache_tag(accessible_run_ids)
        cache_key = f'{objname}__{rid_tag}'
        if not force_regen:
            cached = check_and_serve(
                base_dir, instrument, profile_id,
                'debug_plots', cache_key, aparams=profile_data)
            if cached is not None:
                return jsonify(**cached)

        htable_rows = load_object_htable_rows(objects_dir, objname)
        preset = load_object_preset(instrument_profile_file)

        # Load tcorr data for the telluric map (optional)
        ftable_tcorr_rows = load_object_ftable_rows(
            objects_dir, objname, 'tcorr')

        # Filter by accessible run_ids
        htable_rows, ftables = self._filter_plot_rows(
            htable_rows,
            {'tcorr': ftable_tcorr_rows},
            accessible_run_ids,
        )
        ftable_tcorr_rows = ftables['tcorr']

        path_red = str(
            self._profile_get_path(profile_data, 'PATH_RED', '') or '')
        paths = {'PATH_RED': path_red} if path_red else None

        from apero_ri.plots.plot_debug import generate_debug_plots
        result = generate_debug_plots(
            htable_rows, objname, preset, ftable_tcorr_rows, paths)
        if isinstance(result, dict):
            result['updated_at'] = datetime.now(timezone.utc).isoformat()

        try:
            from apero_ri.core.plot_cache import (
                load_cache_config, resolve_cache_root, put_cached,
                _profile_dir, _load_meta, _save_meta,
            )
            cfg = load_cache_config(base_dir)
            if cfg.get('enabled'):
                cache_root = resolve_cache_root(base_dir, cfg)
                put_cached(cache_root, instrument, profile_id,
                           'debug_plots', cache_key, result)
                pdir = _profile_dir(cache_root, instrument, profile_id)
                meta = _load_meta(pdir)
                db_upd = profile_data.get('database-update', {})
                if isinstance(db_upd, dict) and db_upd:
                    meta['db_updates'] = dict(db_upd)
                from datetime import datetime as _dt, timezone as _tz
                meta['last_cached'] = _dt.now(_tz.utc).isoformat()
                _save_meta(pdir, meta)
        except Exception:
            pass

        return jsonify(**result)

    def _build_finder_max_payload(self, profile, objname, obj_props,
                                  preset, band_idx):
        """Build the plot_payload dict for a finder chart maximize page."""
        from apero_ri.plots.plot_find import generate_finder_charts
        result = generate_finder_charts(obj_props, preset)
        if not result.get('success') or not result.get('images'):
            return {'has_plot': False, 'script': '', 'div': '',
                    'message': result.get('error', 'Generation failed.')}
        idx = max(0, min(band_idx, len(result['images']) - 1))
        img_b64 = result['images'][idx]
        band_label = result.get('titles', result['bands'])[idx]
        div_html = (
            f'<div style="display:flex;align-items:center;'
            f'justify-content:center;width:100%;height:100%;">'
            f'<img src="data:image/png;base64,{img_b64}" '
            f'alt="Finder Chart – {band_label}" '
            f'style="max-width:100%;max-height:100%;object-fit:contain;">'
            f'</div>'
        )
        return {'has_plot': True, 'script': '', 'div': div_html,
                'message': ''}

    # -----------------------------------------------------------------
    # Download basket helpers
    # -----------------------------------------------------------------

    def _basket_access_check(self):
        """
        Shared access-check helper for all basket routes.
        Returns (user_info, None) on success, (None, error_response) on failure.
        """
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()
        if 'view.data_portal' not in perms:
            return None, (jsonify(success=False, error='Unauthorized'), 401)
        if not user_info:
            return None, (jsonify(success=False, error='Login required'), 401)
        return user_info, None

    def _build_profile_cfgs(self, user_info) -> dict:
        """
        Return {profile_id: profile_data} for all profiles accessible to the user.
        Used to resolve file paths during basket compilation.
        """
        accessible = get_accessible_profiles(user_info, self.ari_groups)
        return {p['profile_id']: p.get('data', {}) for p in accessible}

    def _all_accessible_run_ids(self, user_info) -> set:
        """Return the union of run_ids across all instruments the user can see."""
        accessible = get_accessible_profiles(user_info, self.ari_groups)
        all_run_ids: set = set()
        for prof in accessible:
            instrument = prof.get('instrument', '')
            if instrument:
                all_run_ids |= self._get_user_accessible_run_ids(
                    user_info, instrument
                )
        return all_run_ids

    # -----------------------------------------------------------------
    # Basket: page view
    # -----------------------------------------------------------------

    def _ri_basket_view(self, profile_id):
        """Serve the download basket page for a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.', 'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}.basket'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'], self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )

        context = {
            'page_id': page_id,
            'page_label': f'{profile_id}: Download Basket',
            'page_icon': 'fa-solid fa-basket-shopping',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/basket.html', **context)

    # -----------------------------------------------------------------
    # Basket: API – get basket contents
    # -----------------------------------------------------------------

    def _api_basket_get(self):
        """Return the user's basket entries (filtered to accessible run_ids)."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']
        profile_id = request.args.get('profile_id', '').strip()
        accessible_run_ids = self._all_accessible_run_ids(user_info)

        entries = bk.load_basket(username)
        # Security: only return entries the user still has access to
        entries = [
            e for e in entries
            if str(e.get('kw_run_id', '') or '').strip() in accessible_run_ids
        ]
        if profile_id:
            entries = [e for e in entries if e.get('profile_id') == profile_id]

        profile_cfgs = self._build_profile_cfgs(user_info)
        summary = bk.basket_summary(
            username,
            profile_cfgs,
            accessible_run_ids,
            profile_id=profile_id,
        )

        return jsonify(success=True, entries=entries, summary=summary,
                       total=len(entries))

    # -----------------------------------------------------------------
    # Basket: API – summary (file counts + sizes)
    # -----------------------------------------------------------------

    def _api_basket_summary(self):
        """Return basket summary: total files, size, missing files."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']
        profile_id = request.args.get('profile_id', '').strip() or None
        accessible_run_ids = self._all_accessible_run_ids(user_info)
        profile_cfgs = self._build_profile_cfgs(user_info)
        bk.cleanup_expired_downloads(username)
        summary = bk.basket_summary(
            username,
            profile_cfgs,
            accessible_run_ids,
            profile_id=profile_id,
        )
        return jsonify(success=True, **summary)

    # -----------------------------------------------------------------
    # Basket: API – add entries
    # -----------------------------------------------------------------

    def _api_basket_add(self):
        """Add file entries to the basket (POST JSON {entries: [...]})."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        new_entries = data.get('entries', [])
        if not isinstance(new_entries, list):
            return jsonify(success=False, error='entries must be a list'), 400

        username = user_info['username']
        accessible_run_ids = self._all_accessible_run_ids(user_info)
        added = bk.add_to_basket(username, new_entries, accessible_run_ids)
        basket = bk.load_basket(username)
        skipped = len(new_entries) - added
        return jsonify(success=True, added=added, skipped=skipped,
                       basket_count=len(basket))

    # -----------------------------------------------------------------
    # Basket: API – remove entries
    # -----------------------------------------------------------------

    def _api_basket_remove(self):
        """Remove entries from the basket (POST JSON {ids: [...]})."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        ids = data.get('ids', [])
        if not isinstance(ids, list):
            return jsonify(success=False, error='ids must be a list'), 400

        username = user_info['username']
        removed = bk.remove_from_basket(username, ids)
        return jsonify(success=True, removed=removed)

    # -----------------------------------------------------------------
    # Basket: API – clear
    # -----------------------------------------------------------------

    def _api_basket_clear(self):
        """Clear basket (POST JSON {profile_id?: ...})."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        profile_id = data.get('profile_id') or None
        username = user_info['username']
        removed = bk.clear_basket(username, profile_id)
        return jsonify(success=True, removed=removed)

    # -----------------------------------------------------------------
    # Basket: API – compile download
    # -----------------------------------------------------------------

    def _api_basket_compile(self):
        """
        Start background download compilation.
        POST JSON {fmt, chunk_size_gb, email_on_done, profile_id?}
        """
        user_info, err = self._basket_access_check()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        fmt = str(data.get('fmt', 'zip') or 'zip')
        chunk_size_gb = data.get('chunk_size_gb')
        if chunk_size_gb is not None:
            try:
                chunk_size_gb = float(chunk_size_gb)
            except (TypeError, ValueError):
                chunk_size_gb = None
        email_on_done = bool(data.get('email_on_done', False))
        profile_id = data.get('profile_id') or None

        username = user_info['username']
        accessible_run_ids = self._all_accessible_run_ids(user_info)
        profile_cfgs = self._build_profile_cfgs(user_info)

        # Hard limit: no new compilations once stored downloads exceed 5 GB.
        usage = bk.get_downloads_usage(username)
        quota_bytes = bk.get_downloads_storage_limit_bytes()
        if usage.get('total_bytes', 0) >= quota_bytes:
            return jsonify(
                success=False,
                error=('Download storage limit reached (5 GB). '
                       'Please remove old compilations in Recent compilations.'),
                quota_reached=True,
                download_usage=usage,
                download_limit_bytes=quota_bytes,
            ), 400

        entries = bk.load_basket(username)
        if profile_id:
            entries = [e for e in entries if e.get('profile_id') == profile_id]
        if not entries:
            return jsonify(success=False, error='Basket is empty'), 400

        # Resolve sender email for notification
        user_email = ''
        if email_on_done:
            user_email = self._get_primary_contact_email(user_info)

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
            profile_id=profile_id or '',
        )
        return jsonify(success=True, job_id=job_id)

    # -----------------------------------------------------------------
    # Basket: API – compilation status
    # -----------------------------------------------------------------

    def _api_basket_compile_status(self, job_id):
        """Get the status of a compilation job."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']
        meta = bk.get_job_status(username, job_id)
        if meta is None:
            return jsonify(success=False, error='Job not found'), 404
        # Strip internal file paths from response for security
        safe_meta = {k: v for k, v in meta.items() if k != 'chunks'}
        safe_chunks = []
        for chunk in meta.get('chunks', []):
            safe_chunks.append({
                'index': chunk.get('index'),
                'filename': chunk.get('filename'),
                'size_bytes': chunk.get('size_bytes'),
                'file_count': chunk.get('file_count'),
            })
        safe_meta['chunks'] = safe_chunks
        return jsonify(success=True, job=safe_meta)

    # -----------------------------------------------------------------
    # Basket: API – download compiled file
    # -----------------------------------------------------------------

    def _api_basket_download(self, job_id, chunk_idx):
        """Serve a compiled archive chunk for download."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']

        # Rate-limit check
        wait = dt.check_rate_limit(username, 'basket')
        if wait is not None:
            return jsonify(
                success=False,
                error=f'Rate limited – please wait {wait:.1f}s',
                retry_after=wait,
            ), 429

        path = bk.get_job_chunk_path(username, job_id, chunk_idx)
        if path is None:
            return jsonify(success=False, error='File not found or not ready'), 404

        # Track the download
        try:
            file_bytes = path.stat().st_size
        except OSError:
            file_bytes = 0
        dt.record_download(username, 'basket', file_bytes, 1)

        return send_file(
            str(path),
            as_attachment=True,
            download_name=path.name,
        )

    # -----------------------------------------------------------------
    # Basket: API – recent jobs
    # -----------------------------------------------------------------

    def _api_basket_jobs(self):
        """Return recent compilation jobs for the user."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']
        bk.cleanup_expired_downloads(username)
        jobs = bk.list_recent_jobs(username, limit=10)
        usage = bk.get_downloads_usage(username)
        limit_bytes = bk.get_downloads_storage_limit_bytes()

        # Strip internal paths from job metadata for security
        safe_jobs = []
        for job in jobs:
            sj = {k: v for k, v in job.items() if k != 'chunks'}
            safe_chunks = []
            for chunk in job.get('chunks', []):
                safe_chunks.append({
                    'index': chunk.get('index'),
                    'filename': chunk.get('filename'),
                    'size_bytes': chunk.get('size_bytes'),
                    'file_count': chunk.get('file_count'),
                })
            sj['chunks'] = safe_chunks
            safe_jobs.append(sj)

        return jsonify(success=True,
                       jobs=safe_jobs,
                       download_usage=usage,
                       download_limit_bytes=limit_bytes,
                       quota_reached=(
                           usage.get('total_bytes', 0) >= limit_bytes))

    def _api_basket_jobs_remove(self):
        """Remove one completed/failed compilation job for the user."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        job_id = str(data.get('job_id', '') or '').strip()
        if not job_id:
            return jsonify(success=False, error='job_id is required'), 400

        username = user_info['username']
        result = bk.remove_download_job(username, job_id)
        if not result.get('success'):
            return jsonify(success=False,
                           error=result.get(
                               'error', 'Could not remove job')), 400
        usage = bk.get_downloads_usage(username)
        limit_bytes = bk.get_downloads_storage_limit_bytes()
        return jsonify(success=True,
                       removed=result.get('removed', 0),
                       download_usage=usage,
                       download_limit_bytes=limit_bytes,
                       quota_reached=(
                           usage.get('total_bytes', 0) >= limit_bytes))

    def _api_basket_jobs_clear(self):
        """Remove all completed/failed compilation jobs for the user."""
        user_info, err = self._basket_access_check()
        if err:
            return err

        username = user_info['username']
        result = bk.clear_download_jobs(username)
        usage = bk.get_downloads_usage(username)
        limit_bytes = bk.get_downloads_storage_limit_bytes()
        return jsonify(success=True,
                       removed=result.get('removed', 0),
                       skipped=result.get('skipped', 0),
                       download_usage=usage,
                       download_limit_bytes=limit_bytes,
                       quota_reached=(
                           usage.get('total_bytes', 0) >= limit_bytes))

    # -----------------------------------------------------------------
    # Basket: API – create/retrieve share token for a completed job
    # -----------------------------------------------------------------

    def _api_basket_share_token(self):
        """Return (or create) a public share token for a completed job."""
        user_info, err = self._basket_access_check()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        job_id = str(data.get('job_id', '') or '').strip()
        if not job_id:
            return jsonify(success=False, error='job_id required'), 400
        username = user_info['username']
        try:
            token = bk.create_share_token(username, job_id)
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400
        share_url = (request.host_url.rstrip('/')
                     + url_for('share_landing', token=token))
        return jsonify(success=True, token=token, share_url=share_url)

    # -----------------------------------------------------------------
    # Basket: API – send share email
    # -----------------------------------------------------------------

    def _api_basket_share_email(self):
        """Email a share link for a completed job to a recipient."""
        user_info, err = self._basket_access_check()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        job_id = str(data.get('job_id', '') or '').strip()
        recipient = str(data.get('recipient_email', '') or '').strip()
        if not job_id or not recipient:
            return jsonify(
                success=False,
                error='job_id and recipient_email are required',
            ), 400
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', recipient):
            return jsonify(success=False, error='Invalid recipient email address'), 400

        username = user_info['username']
        # Load full user record to get last_name + email
        from apero_ri.core.auth import load_users as _load_users
        all_users = _load_users()
        ud = all_users.get(username, {})
        first_names = str(
            ud.get('first_names', '')
            or user_info.get('first_names', '') or '').strip()
        last_name = str(ud.get('last_name', '') or '').strip()
        sender_email = self._get_primary_contact_email({
            'primary_email': ud.get('primary_email', ''),
            'emails': ud.get('emails', []),
        })

        try:
            token = bk.create_share_token(username, job_id)
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400

        meta = bk.get_job_status(username, job_id)
        if not meta:
            return jsonify(success=False, error='Job not found'), 404

        created_str = meta.get('created_at', '')
        try:
            created_at = datetime.fromisoformat(str(created_str))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            expires_at = created_at + timedelta(hours=24)
            expires_str = expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        except Exception:
            expires_str = 'within 24 hours'

        share_url = (request.host_url.rstrip('/')
                     + url_for('share_landing', token=token))
        sender_full = f'{first_names} {last_name}'.strip() or username
        sender_display = (
            f'{sender_full} (email address: {sender_email})'
            if sender_email else sender_full
        )
        subject = 'APERO RI: Shared download link'
        body = (
            f'User {sender_display} has sent you a link to an APERO RI '
            f'download that will expire at {expires_str}.\n\n'
            f'Download link (no login required):\n{share_url}\n'
        )
        try:
            from apero_ri.core import email_backend as eb
            eb.send_email(recipient, subject, body)
            return jsonify(success=True)
        except Exception as exc:
            return jsonify(success=False, error=f'Failed to send email: {exc}'), 500

    # -----------------------------------------------------------------
    # Basket: Public share landing page (no login required)
    # -----------------------------------------------------------------

    def _share_landing(self, token):
        """Public page for a shared download – no authentication required."""
        share_info = bk.get_share_job(str(token or ''))
        if share_info is None:
            return render_template('data_portal/share_expired.html'), 404

        meta = share_info['meta']
        chunks = meta.get('chunks', [])
        safe_chunks = []
        for chunk in chunks:
            safe_chunks.append({
                'index': chunk.get('index', 0),
                'filename': chunk.get('filename', ''),
                'size_bytes': chunk.get('size_bytes', 0),
                'file_count': chunk.get('file_count', 0),
                'download_url': url_for('share_download', token=token,
                                        chunk_idx=chunk.get('index', 0)),
            })

        expires_str = None
        try:
            created_at = datetime.fromisoformat(
                str(meta.get('created_at', '')))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            expires_at = created_at + timedelta(hours=24)
            expires_str = expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        except Exception:
            pass

        return render_template(
            'data_portal/share_landing.html',
            chunks=safe_chunks,
            meta=meta,
            expires_at=expires_str,
            token=token,
        )

    # -----------------------------------------------------------------
    # Basket: Public share chunk download (no login required)
    # -----------------------------------------------------------------

    def _share_download(self, token, chunk_idx):
        """Direct file download for a shared job chunk – no auth required."""
        share_info = bk.get_share_job(str(token or ''))
        if share_info is None:
            return jsonify(success=False, error='Link expired or not found'), 404
        username = share_info['username']

        # Rate-limit check (uses basket category for share links)
        wait = dt.check_rate_limit(username, 'basket')
        if wait is not None:
            return jsonify(
                success=False,
                error=f'Rate limited – please wait {wait:.1f}s',
                retry_after=wait,
            ), 429

        path = bk.get_job_chunk_path(username,
                                     share_info['job_id'],
                                     chunk_idx)
        if path is None:
            return jsonify(success=False, error='File not found'), 404

        # Track the download
        try:
            file_bytes = path.stat().st_size
        except OSError:
            file_bytes = 0
        dt.record_download(username, 'basket', file_bytes, 1)

        return send_file(
            str(path), as_attachment=True, download_name=path.name)

    # -----------------------------------------------------------------
    # Basket: API – add from ftable by obs_dir + fkind
    # -----------------------------------------------------------------

    def _api_basket_add_from_ftable(self):
        """
        Add accessible files for a specific obs_dir + fkind to the basket.
        POST with query params: profile_id, objname, obs_dir, fkind
        """
        user_info, err = self._basket_access_check()
        if err:
            return err

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        obs_dir = request.args.get('obs_dir', '').strip()
        fkind = request.args.get('fkind', 'ext').strip()

        if not profile_id or not objname:
            return jsonify(success=False, error='Missing profile_id or objname'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        rows, _, _ = bk.load_ftable_rows(
            base_dir, instrument, profile_id, objname, fkind
        )
        # filter by access and by obs_dir
        rows = bk.filter_accessible_rows(rows, accessible_run_ids)
        if obs_dir:
            rows = [r
                for r in rows
                if str(r.get('OBS_DIR', '') or '') == obs_dir]

        entries = [
            {
                'profile_id': profile_id,
                'instrument': instrument,
                'objname': objname,
                'block_kind': r.get('BLOCK_KIND', ''),
                'obs_dir': r.get('OBS_DIR', ''),
                'filename': r.get('FILENAME', ''),
                'kw_output': r.get('KW_OUTPUT', ''),
                'kw_run_id': r.get('KW_RUN_ID', ''),
                'kw_dprtype': r.get('KW_DPRTYPE', ''),
                'kw_fiber': r.get('KW_FIBER', ''),
                'kw_pi_name': r.get('KW_PI_NAME', ''),
                'mid_obs_time': r.get('MID_OBS_TIME', ''),
                'passed_all_qc': r.get('PASSED_ALL_QC'),
                'identifier': r.get('IDENTIFIER', ''),
            }
            for r in rows
        ]

        username = user_info['username']
        added = bk.add_to_basket(username, entries, accessible_run_ids)
        basket = bk.load_basket(username)
        return jsonify(success=True, added=added, basket_count=len(basket))

    # -----------------------------------------------------------------
    # File browser API
    # -----------------------------------------------------------------

    def _api_file_browser(self):
        """
        Return ftable_all rows for an object, filtered to accessible run_ids
        and optionally by a preset.
        GET ?profile_id=&objname=&preset=default
        """
        import time as _time
        t_start = _time.time()

        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        objname = request.args.get('objname', '').strip()
        preset = request.args.get('preset', 'default').strip() or 'default'

        if not profile_id or not objname:
            return jsonify(success=False, error='Missing profile_id or objname'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        all_rows, _, generated_at = bk.load_ftable_rows(
            base_dir, instrument, profile_id, objname, 'all'
        )
        total_m = len(all_rows)

        # Access filter (security gate)
        accessible_rows = bk.filter_accessible_rows(
            all_rows,
            accessible_run_ids)

        # Preset filter
        filtered = bk.apply_preset_filter(accessible_rows, preset)

        query_time = _time.time() - t_start
        return jsonify(
            success=True,
            rows=filtered,
            total=total_m,
            accessible=len(accessible_rows),
            preset=preset,
            generated_at=generated_at,
            query_time=round(query_time, 3),
        )

    def _api_obs_table(self):
        """Return observation table rows for a profile, filtered by science group."""
        import json as _json
        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))

        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        if not profile_id:
            return jsonify(success=False, error='Missing profile_id'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        accessible_run_ids = self._get_user_accessible_run_ids(
            user_info, instrument
        )

        tasks_dir = base_dir / 'tasks' / instrument
        # New layout: tasks/<instrument>/<profile>/obs_table.json
        json_path = tasks_dir / profile_id / 'obs_table.json'

        # Backward compatibility for older task outputs.
        if not json_path.exists():
            legacy_path1 = tasks_dir / f'obs_table_{profile_id}.json'
            legacy_path2 = tasks_dir / f'observation_table_{profile_id}.json'
            if legacy_path1.exists():
                json_path = legacy_path1
            elif legacy_path2.exists():
                json_path = legacy_path2

        if not json_path.exists():
            return jsonify(
                success=True,
                rows=[],
                columns=[],
                generated_at=None,
                total_rows=0,
                message='No observation table data found. '
                        'Run the observation table task first.',
            )

        try:
            with open(json_path, encoding='utf-8') as f:
                data = _json.load(f)
        except Exception as exc:
            return jsonify(
                success=False, error=f'Failed to load data: {exc}'
            ), 500

        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}
        all_rows = data.get('rows', [])
        generated_at = (data.get('generated_at')
                        or metadata.get('GENERATED_AT'))
        raw_column_meta = metadata.get('COLUMN_META', {})
        if not isinstance(raw_column_meta, dict):
            raw_column_meta = {}

        filtered = []
        for row in all_rows:
            raw = str(
                row.get('RUN_ID', '')
                or row.get('run_id', '')
                or row.get('ALL_RUN_IDS', '')
                or row.get('all_run_ids', '')
                or ''
            )
            row_rids = {r.strip() for r in raw.split(',') if r.strip()}
            if row_rids & accessible_run_ids:
                filtered.append(row)

        skip = {'RUN_ID', 'run_id', 'ALL_RUN_IDS', 'all_run_ids'}
        columns = [c for c in (all_rows[0].keys() if all_rows else [])
                   if c not in skip]

        column_meta = {
            col: dict(meta)
            for col, meta in raw_column_meta.items()
            if col not in skip and isinstance(meta, dict)
        }
        if 'NIGHT' in columns and 'NIGHT' not in column_meta:
            column_meta['NIGHT'] = {
                'sortable': True,
                'filterable': True,
                'removable': False,
                'default': True,
                'type': 'night',
            }
        if 'OBJNAME' in columns and 'OBJNAME' not in column_meta:
            column_meta['OBJNAME'] = {
                'sortable': True,
                'filterable': True,
                'removable': False,
                'default': True,
                'type': 'string',
            }

        clean_rows = [
            {k: v for k, v in row.items() if k not in skip}
            for row in filtered
        ]

        return jsonify(
            success=True,
            rows=clean_rows,
            columns=columns,
            column_meta=column_meta,
            generated_at=generated_at,
            total_rows=len(all_rows),
        )

    # -----------------------------------------------------------------
    # Data portal — database query explorer
    # -----------------------------------------------------------------
    def _get_user_table_access(self, user_info, profile):
        """Return tables the user may query for this profile.

        Checks db_access.yaml groups vs user's groups.
        Returns dict: { 'FINDEX': {'table_name': '...', 'columns': [...]}, ... }
        Columns list is the intersection of db_access.yaml columns and actual
        table columns defined in the profile config.
        """
        if user_info is None:
            return {}

        instrument = str(profile.get('instrument', '')).strip()
        profile_id = str(profile.get('profile_id', '')).strip()
        cfg = (profile.get('data', {})
               if isinstance(profile.get('data'), dict)
               else {})
        user_groups = set(user_info.get('groups', []) or [])

        db_access = load_db_access()
        entry = (((db_access.get(instrument, {})
                   if isinstance(db_access.get(instrument, {}), dict)
                   else {}).get(profile_id, {}))
                 if instrument and profile_id else {})
        if not isinstance(entry, dict):
            entry = {}

        table_key_map = self._db_access_table_keys()
        result = {}

        for label, key in table_key_map.items():
            table_name = str(self._profile_get_db(cfg, key, '')).strip()
            if not table_name:
                continue

            # Check user group access for this table label
            allowed_groups = entry.get('groups', {}).get(label, [])
            if not isinstance(allowed_groups, list):
                allowed_groups = []
            if not user_groups & set(allowed_groups):
                continue  # user not in any allowed group for this table

            # Columns from db_access config
            allowed_cols = entry.get('columns', {}).get(label, [])
            if not isinstance(allowed_cols, list):
                allowed_cols = []
            allowed_cols = [str(c).strip()
                for c in allowed_cols
                if str(c).strip()]

            if not allowed_cols:
                continue  # no columns configured

            result[label] = {
                'table_name': table_name,
                'columns': allowed_cols,
            }

        return result

    def _execute_db_query(self, profile_cfg, query, query_params=None):
        """Execute a parameterized SELECT query against the profile's database.

        Uses SQLAlchemy's expanding bindparams for IN-clause list values.
        Only SELECT statements are accepted (validated by caller).
        """
        from urllib.parse import quote_plus
        from sqlalchemy import create_engine, text, bindparam

        db_params = self._profile_db_params(profile_cfg)
        mode = str(db_params.get('DATABASE_MODE', '')).strip()
        username = str(db_params.get('DATABASE_USERNAME', '')).strip()
        password = str(db_params.get('DATABASE_PASSWORD', '') or '')
        db_name = str(db_params.get('DATABASE_NAME', '')).strip()

        if not all([mode, username, db_name]):
            raise ValueError('Missing database connection configuration.')

        host, port = apero_async._resolve_database_endpoint(db_params)

        db_url = (
            f'{mode}://{quote_plus(username)}:{quote_plus(password)}'
            f'@{host}:{port}/{db_name}'
        )
        engine = create_engine(db_url, future=True)

        try:
            params = dict(query_params or {})
            stmt = text(query)
            # Apply expanding bindparams for list values (IN clauses)
            for key, val in params.items():
                if isinstance(val, (list, tuple)):
                    stmt = stmt.bindparams(bindparam(key, expanding=True))
            with engine.begin() as conn:
                result = conn.execute(stmt, params)
                if result.returns_rows:
                    return [dict(row) for row in result.mappings().all()]
                return []
        finally:
            engine.dispose()

    @staticmethod
    def _build_safe_select_query(table_access, query_spec, run_ids):
        """Build a safe parameterized SELECT from a structured query spec.

        All table/column identifiers are validated against the whitelist in
        table_access.  Only the operators in ALLOWED_OPS are accepted for
        filters.  WHERE values are always passed as bound parameters.

        :param table_access: dict from _get_user_table_access()
        :param query_spec: structured dict (see _api_query_db_run for schema)
        :param run_ids: set of str run-ids the user may see
        :returns: (sql_str, params_dict)
        :raises ValueError: on any invalid / disallowed input
        """
        ALLOWED_OPS = frozenset({'=', '!=', '<', '>', '<=', '>=',
                                  'LIKE', 'NOT LIKE'})
        ALLOWED_NULL_OPS = frozenset({'IS NULL', 'IS NOT NULL'})
        ALLOWED_JOIN_TYPES = frozenset({'INNER', 'LEFT', 'RIGHT'})
        ALLOWED_SORT_DIRS = frozenset({'ASC', 'DESC'})

        def q_id(name):
            """Backtick-quote a single identifier (no dots allowed)."""
            if not re.match(r'^[A-Za-z0-9_]+$', name):
                raise ValueError(f'Invalid identifier: {name!r}')
            return f'`{name}`'

        tables_spec = query_spec.get('tables', [])
        joins_spec = query_spec.get('joins', [])
        filters_spec = query_spec.get('filters', [])
        order_by_spec = query_spec.get('order_by')
        limit = int(query_spec.get('limit', 500))
        limit = min(max(1, limit), 2000)

        if not tables_spec:
            raise ValueError('No tables specified.')

        # Gather validated table info
        table_names = {}   # label -> actual_table_name
        table_cols = {}    # label -> set of allowed columns
        select_parts = []
        col_labels = []    # returned to caller for result header

        for tspec in tables_spec:
            label = str(tspec.get('label', '')).strip().upper()
            if label not in table_access:
                raise ValueError(f'Table {label!r} is not accessible.')
            allowed = table_access[label]['columns']
            tname = table_access[label]['table_name']
            if not re.match(r'^[A-Za-z0-9_.]+$', tname):
                raise ValueError(f'Invalid table name: {tname!r}')
            table_names[label] = tname
            table_cols[label] = set(allowed)

            cols = tspec.get('columns') or list(allowed)
            for col in cols:
                col = str(col).strip()
                if col not in table_cols[label]:
                    raise ValueError(
                        f'Column {col!r} is not accessible for {label}.')
                alias = f'{label}__{col}'
                select_parts.append(
                    f'`_t_{label}`.{q_id(col)} AS {q_id(alias)}'
                )
                col_labels.append(alias)

        # Basket integration: whenever FINDEX is in the query, always
        # inject the four basket-key columns as hidden extras (not in
        # col_labels so they are absent from the display table, but
        # present in every result row so the JS can enable checkboxes).
        _BASKET_KEY_COLS = ['KW_RUN_ID', 'BLOCK_KIND', 'OBS_DIR', 'FILENAME']
        if 'FINDEX' in table_cols:
            for _bk_col in _BASKET_KEY_COLS:
                _bk_alias = f'FINDEX__{_bk_col}'
                if (_bk_alias not in col_labels
                        and _bk_col in table_cols['FINDEX']):
                    select_parts.append(
                        f'`_t_FINDEX`.{q_id(_bk_col)} AS {q_id(_bk_alias)}'
                    )
                    # Intentionally NOT added to col_labels

        if not select_parts:
            raise ValueError('No columns selected.')

        # FROM clause: first table
        first_label = str(tables_spec[0].get('label', '')).strip().upper()
        first_tname = table_names[first_label]
        from_clause = f'`{first_tname}` AS `_t_{first_label}`'

        # JOIN clauses
        join_clauses = []
        for jspec in joins_spec:
            left = str(jspec.get('left_label', '')).strip().upper()
            right = str(jspec.get('right_label', '')).strip().upper()
            left_col = str(jspec.get('left_col', '')).strip()
            right_col = str(jspec.get('right_col', '')).strip()
            jtype = str(jspec.get('type', 'LEFT')).strip().upper()

            if left not in table_names or right not in table_names:
                raise ValueError('Join references an inaccessible table.')
            if jtype not in ALLOWED_JOIN_TYPES:
                raise ValueError(f'Invalid join type: {jtype!r}')
            if left_col not in table_cols[left]:
                raise ValueError(
                    f'Join column {left_col!r} not accessible for {left}.')
            if right_col not in table_cols[right]:
                raise ValueError(
                    f'Join column {right_col!r} not accessible for {right}.')

            right_tname = table_names[right]
            join_clauses.append(
                f'{jtype} JOIN `{right_tname}` AS `_t_{right}` '
                f'ON `_t_{left}`.{q_id(left_col)} = `_t_{right}`.{q_id(right_col)}'
            )

        # WHERE clause
        where_parts = []
        params = {}
        param_idx = 0

        # Always filter FINDEX by user's accessible run_ids
        if 'FINDEX' in table_names:
            if not run_ids:
                return 'SELECT 1 WHERE 1=0', {}, []
            params['_run_ids'] = sorted(run_ids)
            where_parts.append(
                f'`_t_FINDEX`.`KW_RUN_ID` IN :_run_ids'
            )

        # User-supplied filters
        for fspec in filters_spec:
            tlabel = str(fspec.get('table_label', '')).strip().upper()
            col = str(fspec.get('column', '')).strip()
            op_raw = str(fspec.get('op', '')).strip().upper()

            if tlabel not in table_names:
                raise ValueError(
                    f'Filter references an inaccessible table: {tlabel!r}')
            if col not in table_cols[tlabel]:
                raise ValueError(
                    f'Filter column {col!r} not accessible for {tlabel}.')

            col_ref = f'`_t_{tlabel}`.{q_id(col)}'

            if op_raw in ALLOWED_NULL_OPS:
                where_parts.append(f'{col_ref} {op_raw}')
            elif op_raw in ALLOWED_OPS:
                pname = f'p{param_idx}'
                param_idx += 1
                where_parts.append(f'{col_ref} {op_raw} :{pname}')
                params[pname] = fspec.get('value', '')
            else:
                raise ValueError(f'Invalid filter operator: {op_raw!r}')

        # ORDER BY
        order_clause = ''
        if order_by_spec and isinstance(order_by_spec, dict):
            ob_label = str(
                order_by_spec.get('table_label', '')).strip().upper()
            ob_col = str(order_by_spec.get('column', '')).strip()
            ob_dir = str(order_by_spec.get('direction', 'ASC')).strip().upper()
            if ob_label in table_names and ob_col:
                if ob_col not in table_cols[ob_label]:
                    raise ValueError(
                        f'Order column {ob_col!r} not accessible for {ob_label}.')
                if ob_dir not in ALLOWED_SORT_DIRS:
                    ob_dir = 'ASC'
                order_clause = (
                    f'ORDER BY `_t_{ob_label}`.{q_id(ob_col)} {ob_dir}'
                )

        # Build final SQL
        sql = f'SELECT {", ".join(select_parts)}\nFROM {from_clause}'
        for jc in join_clauses:
            sql += f'\n{jc}'
        if where_parts:
            sql += f'\nWHERE {" AND ".join(where_parts)}'
        if order_clause:
            sql += f'\n{order_clause}'
        sql += f'\nLIMIT {limit}'

        return sql, params, col_labels

    def _ri_query_db_view(self, profile_id):
        """Serve the database query explorer page for a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}.query_db'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )

        query_presets = self._load_query_db_presets(profile)

        context = {
            'page_id': page_id,
            'page_label': f'{profile_id}: Database Query',
            'page_icon': 'fa-solid fa-terminal',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'schema_api_url': '/api/data-portal/query-db/schema',
            'run_api_url': '/api/data-portal/query-db/run',
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
            'query_presets': query_presets,
        }
        return render_template('data_portal/query_db.html', **context)

    def _ri_qc_graphs_view(self, profile_id):
        """Serve interactive quality-control graphs for a profile."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        page_id = f'home.data_portal.{profile_id}.qc_graphs'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        sidebar_tree = self._build_data_portal_sidebar_tree(
            accessible_profiles=accessible,
            active_page_id=page_id,
            user_permissions=perms,
            user_info=user_info,
            current_profile_id=profile_id,
        )

        from apero_ri.plots.plots_qc import build_qc_plot_payload

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))

        # --- QC cache ---
        from apero_ri.core.plot_cache import check_and_serve, is_cache_enabled
        profile_data = profile.get('data') or {}
        cached_qc = check_and_serve(
            base_dir, profile['instrument'], profile_id,
            'qc_graphs', 'payload', aparams=profile_data)
        if cached_qc is not None:
            qc_payload = cached_qc
        else:
            qc_payload = build_qc_plot_payload(base_dir=base_dir,
                                               profile=profile)
            # Store in cache
            try:
                from apero_ri.core.plot_cache import (
                    load_cache_config, resolve_cache_root, put_cached,
                    _profile_dir, _load_meta, _save_meta,
                )
                cfg = load_cache_config(base_dir)
                if cfg.get('enabled'):
                    cache_root = resolve_cache_root(base_dir, cfg)
                    import time as _time
                    put_cached(cache_root, profile['instrument'], profile_id,
                               'qc_graphs', 'payload', qc_payload)
                    pdir = _profile_dir(cache_root, profile['instrument'],
                                        profile_id)
                    meta = _load_meta(pdir)
                    db_upd = profile_data.get('database-update', {})
                    if isinstance(db_upd, dict) and db_upd:
                        meta['db_updates'] = dict(db_upd)
                    from datetime import datetime as _dt, timezone as _tz
                    meta['last_cached'] = _dt.now(_tz.utc).isoformat()
                    _save_meta(pdir, meta)
            except Exception:
                pass

        context = {
            'page_id': page_id,
            'page_label': f'{profile_id}: Quality Control Graphs',
            'page_icon': 'fa-solid fa-chart-line',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'qc_payload': qc_payload,
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/qc_graphs.html', **context)

    def _ri_qc_graphs_max_view(self,
                               profile_id,
                               section,
                               metric_key,
                               view_key):
        """Serve a standalone maximized QC plot page."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            flash('You do not have permission to view this page.',
                  'warning')
            return redirect(url_for('login'))

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break

        if not profile:
            flash('Profile not found or access denied.', 'warning')
            return redirect(url_for('home_data_portal'))

        from apero_ri.plots.plots_qc import build_qc_single_plot_payload

        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))
        plot_payload = build_qc_single_plot_payload(
            base_dir=base_dir,
            profile=profile,
            section=section,
            metric_key=metric_key,
            view_key=view_key,
        )

        context = {
            'profile': profile,
            'plot_payload': plot_payload,
            'return_url': url_for('ri_qc_graphs', profile_id=profile_id),
        }
        return render_template('data_portal/qc_graphs_max.html', **context)

    def _load_query_db_presets(self, profile):
        """Load query-db presets and replace table placeholders.

        Presets are loaded from a per-instrument text file referenced by
        ``general.db-query-preset-file`` in the instrument profile YAML.
        The text file lives under ``resources/aprofile_qdb_presets/``.
        If that key is absent or the file is missing, fall back to the
        global ``resources/db_presets.yaml``.

        Text file format::

            ================
            Preset name here
            ================
            SELECT ...
            FROM {FINDEX_TABLENAME}
            WHERE ...

        Supported placeholders include both {LABEL} and
        {LABEL_TABLENAME}, where LABEL is one of the db-access table labels
        (e.g. FINDEX, ASTROM, CALIB).
        """
        cfg = (profile.get('data', {})
               if isinstance(profile.get('data'), dict)
               else {})
        table_names = {}
        for label, key in self._db_access_table_keys().items():
            tname = str(self._profile_get_db(cfg, key, '')).strip()
            if tname:
                table_names[label] = tname

        constants = {}
        for key, value in cfg.items():
            skey = str(key).strip()
            if not skey:
                continue
            if value is None:
                constants[skey] = ''
            else:
                constants[skey] = str(value)
        for section_name in ('database', 'paths', 'general'):
            section = cfg.get(section_name, {})
            if not isinstance(section, dict):
                continue
            for key, value in section.items():
                skey = str(key).strip()
                if not skey or skey in constants:
                    continue
                if value is None:
                    constants[skey] = ''
                elif isinstance(value, list):
                    constants[skey] = ','.join(str(v) for v in value)
                else:
                    constants[skey] = str(value)

        def _replace_placeholders(sql):
            if not isinstance(sql, str):
                return ''
            out = sql
            for key, value in constants.items():
                out = out.replace(f'{{{key}}}', value)
            for label, tname in table_names.items():
                out = out.replace(f'{{{label}}}', tname)
                out = out.replace(f'{{{label}_TABLENAME}}', tname)
            return out.strip()

        # ── Try per-instrument text preset file ──────────────────────────
        general_cfg = cfg.get('general', {})
        preset_filename = ''
        if isinstance(general_cfg, dict):
            # Accept both separator styles for backward compatibility.
            preset_filename = str(
                general_cfg.get('db-query-preset-file')
                or general_cfg.get('db-query-preset_file')
                or general_cfg.get('db_query_preset_file')
                or ''
            ).strip()

        # Existing saved profiles may not yet include the new key in their
        # embedded data; in that case derive the filename from profile_id.
        if not preset_filename:
            guessed = str(profile.get('profile_id', '')).strip()
            if guessed:
                preset_filename = f'{guessed}.txt'

        if preset_filename:
            text_path = (PACKAGE_DIR / 'resources'
                         / 'aprofile_qdb_presets' / preset_filename)
            if text_path.exists():
                return self._parse_text_presets(
                    text_path.read_text(encoding='utf-8'),
                    _replace_placeholders,
                )

        # ── Fall back to global YAML preset file ─────────────────────────
        preset_path = PACKAGE_DIR / 'resources' / 'db_presets.yaml'
        if not preset_path.exists():
            return []

        try:
            with preset_path.open('r', encoding='utf-8') as f:
                raw = yaml.safe_load(f) or {}
        except Exception:
            return []

        presets = []

        if isinstance(raw, dict):
            iterator = raw.items()
        elif isinstance(raw, list):
            iterator = []
            for idx, entry in enumerate(raw):
                if isinstance(entry, dict):
                    name = (entry.get('name') or entry.get('label')
                            or entry.get('title') or f'Preset {idx + 1}')
                    iterator.append((name, entry))
        else:
            iterator = []

        for name, entry in iterator:
            query = ''
            if isinstance(entry, str):
                query = entry
            elif isinstance(entry, dict):
                query = entry.get('query') or entry.get('sql') or ''

            query = _replace_placeholders(query)
            if not query:
                continue

            presets.append({
                'name': str(name),
                'query': query,
            })

        return presets

    @staticmethod
    def _parse_text_presets(text, replace_fn):
        """Parse a ``================`` -delimited preset text file.

        Each preset block has the form::

            ================
            Preset name
            ================
            SELECT ...

        Returns a list of ``{'name': str, 'query': str}`` dicts.
        """
        _DELIM = re.compile(r'^={4,}\s*$')
        presets = []
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            # Seek the first delimiter line
            if not _DELIM.match(lines[i]):
                i += 1
                continue
            i += 1  # skip first delimiter
            # Collect name lines until next delimiter
            name_lines = []
            while i < len(lines) and not _DELIM.match(lines[i]):
                name_lines.append(lines[i])
                i += 1
            name = ' '.join(ln.strip() for ln in name_lines if ln.strip())
            if not name or i >= len(lines):
                continue
            i += 1  # skip second delimiter
            # Collect SQL lines until next delimiter or EOF
            sql_lines = []
            while i < len(lines) and not _DELIM.match(lines[i]):
                sql_lines.append(lines[i])
                i += 1
            # Preserve multi-line SQL; strip each line but keep structure
            sql = '\n'.join(ln.rstrip() for ln in sql_lines).strip()
            sql = replace_fn(sql)
            if name and sql:
                presets.append({'name': name, 'query': sql})
        return presets

    def _api_query_db_schema(self):
        """Return allowed tables and columns for a profile+user combination."""
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        if not profile_id:
            return jsonify(success=False, error='Missing profile_id'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        table_access = self._get_user_table_access(user_info, profile)

        tables_out = []
        for label, info in table_access.items():
            tables_out.append({
                'label': label,
                'table_name': info['table_name'],
                'columns': info['columns'],
                'has_run_id_filter': label == 'FINDEX',
            })
        # Stable order
        tables_out.sort(key=lambda t: t['label'])

        return jsonify(success=True, tables=tables_out)

    def _api_query_db_run(self):
        """Execute a structured, user-driven SELECT query safely.

        Expected JSON body::
            {
                "profile_id": "spirou_xxs_08_cook_home",
                "tables": [
                    {"label": "FINDEX", "columns": ["OBS_DIR", "KW_OBJNAME"]}
                ],
                "joins": [
                    {
                        "left_label": "FINDEX", "left_col": "KW_OBJNAME",
                        "right_label": "ASTROM", "right_col": "OBJNAME",
                        "type": "LEFT"
                    }
                ],
                "filters": [
                    {"table_label": "FINDEX", "column": "KW_DPRTYPE",
                     "op": "=", "value": "OBJ_DARK"}
                ],
                "order_by": {"table_label": "FINDEX", "column": "KW_DATE_OBS",
                             "direction": "DESC"},
                "limit": 500
            }

        All identifiers are validated against the user's access whitelist.
        Run-ID filtering is automatically applied to the FINDEX table.
        Only SELECT behaviour is possible through this API by design.
        """
        user_info = self._get_api_user()
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.data_portal' not in perms:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        profile_id = str(body.get('profile_id', '')).strip()
        if not profile_id:
            return jsonify(success=False, error='Missing profile_id'), 400

        accessible = get_accessible_profiles(user_info, self.ari_groups)
        profile = None
        for prof in accessible:
            if prof['profile_id'] == profile_id:
                profile = prof
                break
        if not profile:
            return jsonify(success=False, error='Profile not found'), 404

        instrument = profile['instrument']
        cfg = (profile.get('data', {})
               if isinstance(profile.get('data'), dict)
               else {})

        # Determine which run_ids the user may see
        run_ids = self._get_user_accessible_run_ids(user_info, instrument)

        # Determine which tables/columns the user may access
        table_access = self._get_user_table_access(user_info, profile)
        if not table_access:
            return jsonify(
                success=False,
                error='No database tables are accessible with your current '
                      'permissions for this profile.',
            ), 403

        try:
            sql, params, col_labels = self._build_safe_select_query(
                table_access=table_access,
                query_spec=body,
                run_ids=run_ids,
            )
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400

        # Produce a redacted SQL preview (replace run_ids list with count)
        nrids = len(run_ids)
        sql_preview = sql.replace(
            ':_run_ids',
            f'(/* {nrids} run ID{"s" if nrids != 1 else ""} */)',
        )
        # Replace filter param placeholders with the actual values
        params_preview = {k: v for k, v in params.items()
                          if k != '_run_ids'}
        for key, val in params_preview.items():
            sql_preview = sql_preview.replace(f':{key}', repr(str(val)))

        try:
            rows = self._execute_db_query(cfg, sql, params)
        except Exception as exc:
            return jsonify(
                success=False,
                error=f'Query failed: {exc}',
                sql_preview=sql_preview,
            ), 500

        # Strip the internal alias prefix from column names for display
        clean_rows = []
        for row in rows:
            clean_rows.append({
                k.split('__', 1)[-1]: v for k, v in row.items()
            })

        # Return both original (label__col) keys and stripped keys
        display_columns = [c.split('__', 1)[-1] for c in col_labels]
        table_for_col = {
            c.split('__', 1)[-1]: c.split('__', 1)[0]
            for c in col_labels
        }

        return jsonify(
            success=True,
            rows=clean_rows,
            columns=display_columns,
            table_for_col=table_for_col,
            total_rows=len(rows),
            sql_preview=sql_preview,
        )

    # -----------------------------------------------------------------
    # Admin user management API
    # -----------------------------------------------------------------
    def _require_admin_user(self):
        """Check that current user has view.admin permission.

        Returns (user_info, perms) or raises a JSON error response.
        """
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return None, None
        return user_info, perms

    def _api_user_search(self):
        """Search users by username substring."""
        user_info, perms = self._require_admin_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        perms = perms or set()

        query = request.args.get('q', '').strip()
        if query:
            results = search_users(query)
        else:
            results = list_all_users()

        # Build group metadata for the editing user
        all_groups = list(self.ari_groups.keys())
        editor_is_admin = user_has_admin_privileges(
            user_info.get('groups', [])
        )
        editor_is_super_admin = user_is_super_admin(
            user_info.get('groups', [])
        )
        # Which groups can the editor manage?
        can_add = {g for g in all_groups if f'manage.group.{g}' in perms}
        # Admin users can manage all non-admin groups from this UI.
        if editor_is_super_admin:
            can_add |= set(all_groups)
        elif editor_is_admin:
            can_add |= {g for g in all_groups if g not in ('admin', 'super_admin')}
        # For each group, what groups does it encompass?
        inherited_map = {}
        for g in all_groups:
            inherited_map[g] = sorted(
                get_inherited_groups(g, self.ari_groups)
            )

        # Instruments available
        params = load_parameters()
        all_instruments = params.get('instruments', {}).get('value', [])
        # Editor's own instruments
        editor_full = get_user_info(user_info['username'])
        editor_instruments = (editor_full.get('instruments', [])
                              if editor_full else [])
        can_manage_instrument_groups = {
            g for g in all_groups if f'manage.instrument.{g}' in perms
        }
        can_add_instrument = (
            ('add.instrument' in perms)
            or bool(can_manage_instrument_groups)
            or editor_is_admin
        )

        return jsonify(
            success=True,
            users=results,
            all_groups=all_groups,
            can_add_groups=sorted(can_add),
            inherited_map=inherited_map,
            all_instruments=all_instruments,
            editor_instruments=editor_instruments,
            can_add_instrument=can_add_instrument,
            can_add_instrument_groups=sorted(can_manage_instrument_groups),
            editor_username=user_info['username'],
            editor_is_admin=editor_is_admin,
            editor_is_super_admin=editor_is_super_admin,
        )

    def _api_user_update_groups(self):
        """Update a target user's groups."""
        user_info, perms = self._require_admin_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        perms = perms or set()

        data = request.get_json()
        if not data or 'username' not in data or 'groups' not in data:
            return jsonify(success=False, error='Missing data'), 400

        target = data['username']
        new_groups = data['groups']

        # Validate: editor must have manage.group.{group} for every group
        # being assigned or removed
        target_info = get_user_info(target)
        if not target_info:
            return jsonify(success=False, error='User not found'), 404

        editor_is_admin = user_has_admin_privileges(
            user_info.get('groups', [])
        )
        editor_is_super_admin = user_is_super_admin(
            user_info.get('groups', [])
        )
        target_groups = set(target_info.get('groups', []))

        # Only super-admin may edit admin/super-admin accounts.
        if ('super_admin' in target_groups) and not editor_is_super_admin:
            return jsonify(
                success=False,
                error='Only super-admin can modify super-admin accounts'
            ), 403
        if ('admin' in target_groups) and not editor_is_super_admin:
            return jsonify(
                success=False,
                error='Only super-admin can modify admin accounts'
            ), 403

        # Only super-admin may assign admin/super-admin from this UI.
        if (('admin' in set(new_groups)) or ('super_admin' in set(new_groups))) and not editor_is_super_admin:
            return jsonify(
                success=False,
                error='Only super-admin can assign admin-level groups'
            ), 403

        old_groups = target_groups
        changed = ((set(new_groups) - old_groups)
                   | (old_groups - set(new_groups)))
        for g in changed:
            if f'manage.group.{g}' not in perms and not editor_is_admin:
                return jsonify(
                    success=False,
                    error=f'No permission to manage group: {g}'
                ), 403

        if not update_user_groups(target, new_groups):
            return jsonify(success=False, error='Update failed'), 500
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_user_update_instruments(self):
        """Update a target user's instruments."""
        user_info, perms = self._require_admin_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        perms = perms or set()

        data = request.get_json()
        if not data or 'username' not in data or 'instruments' not in data:
            return jsonify(success=False, error='Missing data'), 400

        target = data['username']
        new_instruments = data['instruments']

        target_info = get_user_info(target)
        if not target_info:
            return jsonify(success=False, error='User not found'), 404

        editor_is_admin = user_has_admin_privileges(
            user_info.get('groups', [])
        )
        editor_is_super_admin = user_is_super_admin(
            user_info.get('groups', [])
        )
        target_groups = set(target_info.get('groups', []))

        # Only super-admin may edit admin/super-admin account instruments.
        if ('super_admin' in target_groups) and not editor_is_super_admin:
            return jsonify(
                success=False,
                error='Only super-admin can modify super-admin accounts'
            ), 403
        if ('admin' in target_groups) and not editor_is_super_admin:
            return jsonify(
                success=False,
                error='Only super-admin can modify admin accounts'
            ), 403

        # Non-admin editors may always edit their own instruments.
        if target != user_info['username'] and not editor_is_admin:
            can_manage_any = 'add.instrument' in perms
            missing = [
                g for g in target_groups
                if f'manage.instrument.{g}' not in perms
            ]
            if not can_manage_any and missing:
                return jsonify(
                    success=False,
                    error=(
                        'No permission to manage instruments for user groups: '
                        + ', '.join(sorted(missing))
                    )
                ), 403

        if not isinstance(new_instruments, list):
            return jsonify(success=False, error='instruments must be a list'), 400

        # Validate instruments against the allowed list
        params = load_parameters()
        valid = set(params.get('instruments', {}).get('value', []))
        for inst in new_instruments:
            if inst not in valid:
                return jsonify(
                    success=False,
                    error=f'Invalid instrument: {inst}'
                ), 400

        if not update_user_instruments(target, new_instruments):
            return jsonify(success=False, error='Update failed'), 500
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_user_delete(self):
        """Delete a user account."""
        user_info, perms = self._require_admin_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        perms = perms or set()

        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify(success=False, error='Missing data'), 400

        target = data['username']
        target_info = get_user_info(target)
        if not target_info:
            return jsonify(success=False, error='User not found'), 404

        # Cannot delete yourself
        if target == user_info['username']:
            return jsonify(
                success=False, error='Cannot delete your own account'
            ), 403

        # Must have manage.group.{group} for ALL of the target's groups
        for g in target_info.get('groups', []):
            if f'manage.group.{g}' not in perms:
                return jsonify(
                    success=False,
                    error=f'No permission to manage users in group: {g}'
                ), 403

        if not delete_user(target):
            return jsonify(success=False, error='Delete failed'), 500
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Admin login-as API
    # -----------------------------------------------------------------
    def _api_login_as_search(self):
        """Search users that the editor can impersonate."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        # Use the REAL user (not impersonated) for permission checks
        real_user = session.get('user')
        real_info = get_user_info(real_user)
        if not real_info:
            return jsonify(success=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(
            real_info['groups'], self.ari_groups
        )

        query = request.args.get('q', '').strip()
        if query:
            results = search_users(query)
        else:
            results = list_all_users()

        # Filter to only users the editor can login_as
        # Editor must have login_as.{group} for at least one of the
        # target's groups, and target must NOT be the editor themselves,
        # and target must be at a LOWER level (editor must not be able
        # to login_as users at the same or higher level)
        filtered = []
        for u in results:
            if u['username'] == real_user:
                continue
            # Check if editor can login_as any of target's groups
            can_impersonate = any(
                f'login_as.{g}' in perms for g in u['groups']
            )
            if can_impersonate:
                filtered.append(u)

        return jsonify(
            success=True,
            users=filtered,
            current_login_as=session.get('login_as'),
            real_user=real_user,
        )

    def _api_login_as_set(self):
        """Set the login-as user in the session."""
        real_user = session.get('user')
        if not real_user:
            return jsonify(success=False, error='Not logged in'), 401

        real_info = get_user_info(real_user)
        if not real_info:
            return jsonify(success=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(
            real_info['groups'], self.ari_groups
        )

        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify(success=False, error='Missing data'), 400

        target = data['username']
        if target == real_user:
            return jsonify(
                success=False, error='Cannot login as yourself'
            ), 400

        target_info = get_user_info(target)
        if not target_info:
            return jsonify(success=False, error='User not found'), 404

        # Must have login_as.{group} for at least one of target's groups
        can_do = any(
            f'login_as.{g}' in perms for g in target_info['groups']
        )
        if not can_do:
            return jsonify(
                success=False, error='No permission to login as this user'
            ), 403

        session['login_as'] = target
        return jsonify(success=True, username=target)

    @staticmethod
    def _api_login_as_clear():
        """Clear the login-as session."""
        if 'user' not in session:
            return jsonify(success=False, error='Not logged in'), 401
        session.pop('login_as', None)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Admin science groups API
    # -----------------------------------------------------------------
    def _require_sci_group_perm(self):
        """Check for manage.sci_group permission."""
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'manage.sci_group' not in perms:
            return None, None
        return user_info, perms

    def _api_sci_groups_list(self):
        """List science group names for an instrument."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='No instrument'), 400

        # Validate instrument
        params = load_parameters()
        valid = params.get('instruments', {}).get('value', [])
        if instrument not in valid:
            return jsonify(success=False, error='Invalid instrument'), 400

        # Derive available run_ids from all object table JSONs for instrument
        run_ids = self._get_instrument_run_ids(instrument)
        groups = load_science_groups(instrument)
        groups, run_ids = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=run_ids,
            persist=True,
        )
        group_names = sorted(
            groups.keys(),
            key=lambda n: (0 if self._is_all_science_group(n) else 1,
                           str(n).lower())
        )
        available_users = get_users_for_instrument(instrument)

        assigned_users = set()
        assigned_run_ids = set()
        groups_without_users = []
        groups_without_run_ids = []
        for gname, group_entry in groups.items():
            if not isinstance(group_entry, dict):
                continue
            is_all_group = self._is_all_science_group(gname)

            group_users = []
            for username in group_entry.get('users', []):
                uname = str(username).strip()
                if uname:
                    group_users.append(uname)
                    assigned_users.add(uname)

            group_run_ids = []
            for run_id in group_entry.get('run_ids', []):
                rid = str(run_id).strip()
                if rid:
                    group_run_ids.append(rid)
                    if not is_all_group:
                        assigned_run_ids.add(rid)

            if not group_users and not is_all_group:
                groups_without_users.append(str(gname))
            if not group_run_ids and not is_all_group:
                groups_without_run_ids.append(str(gname))

        available_set = {str(u).strip()
                        for u in available_users
                        if str(u).strip()}
        available_run_id_set = {str(rid).strip()
                             for rid in run_ids
                             if str(rid).strip()}
        missing_users = sorted(available_set - assigned_users)
        missing_run_ids = sorted(available_run_id_set - assigned_run_ids)

        health_issues = []
        health_details = []
        if missing_users:
            health_issues.append(
                f'{len(missing_users)} user(s) not assigned to any science group'
            )
            health_details.extend([f'user: {u}' for u in missing_users])

        if groups_without_users:
            health_issues.append(
                f'{len(groups_without_users)} science group(s) without users'
            )
            health_details.extend([
                f'group-without-users: {name}' for name in sorted(groups_without_users)
            ])

        if groups_without_run_ids:
            health_issues.append(
                f'{len(groups_without_run_ids)} science group(s) without run IDs'
            )
            health_details.extend([
                f'group-without-run-ids: {name}'
                for name in sorted(groups_without_run_ids)
            ])

        if missing_run_ids:
            health_issues.append(
                f'{len(missing_run_ids)} run ID(s) not assigned to any science group'
            )
            health_details.extend(
                [f'run_id: {rid}' for rid in missing_run_ids])

        if health_issues:
            health_status = 'warning'
            health_message = '; '.join(health_issues) + '.'
        else:
            health_status = 'ok'
            health_message = (
                f'All {len(available_users)} users and {len(run_ids)} run ID(s) '
                f'are assigned to at least one science group.'
            )

        return jsonify(
            success=True,
            groups=group_names,
            run_ids=run_ids,
            available_users=available_users,
            health_status=health_status,
            health_message=health_message,
            total_users=len(available_users),
            missing_users=len(missing_users),
            missing_user_list=missing_users,
            missing_run_ids=len(missing_run_ids),
            missing_run_id_list=missing_run_ids,
            groups_without_users=sorted(groups_without_users),
            groups_without_run_ids=sorted(groups_without_run_ids),
            health_details=health_details,
        )

    def _api_sci_groups_get(self):
        """Get details of a specific science group."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        instrument = request.args.get('instrument', '').strip()
        name = request.args.get('name', '').strip()
        if not instrument or not name:
            return jsonify(success=False, error='Missing params'), 400

        groups = load_science_groups(instrument)
        groups, run_ids = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=self._get_instrument_run_ids(instrument),
            persist=True,
        )
        canonical_name = 'All' if self._is_all_science_group(name) else name
        if canonical_name not in groups:
            return jsonify(
                success=True,
                group={'run_ids': [], 'users': []}
            )

        entry = groups[canonical_name]
        return jsonify(
            success=True,
            group={
                'run_ids': entry.get('run_ids', []),
                'users': entry.get('users', []),
            }
        )

    def _api_sci_groups_refresh_run_ids(self):
        """Re-scan instrument run IDs and sync the reserved All group only."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json(silent=True) or {}
        instrument = str(data.get('instrument', '') or '').strip()
        if not instrument:
            return jsonify(success=False, error='Missing instrument'), 400

        params = load_parameters()
        valid = params.get('instruments', {}).get('value', [])
        if instrument not in valid:
            return jsonify(success=False, error='Invalid instrument'), 400

        groups = load_science_groups(instrument)
        run_ids = self._get_instrument_run_ids(instrument)
        _, run_ids = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=run_ids,
            persist=True,
        )
        self._refresh_admin_health_after_change(user_info, perms)

        return jsonify(
            success=True,
            run_ids=run_ids,
            removed_run_ids=0,
            message=('Run ID list refreshed. User-defined group run IDs were left unchanged; '
                     'the All group was synchronized automatically.'),
        )

    def _api_sci_groups_save(self):
        """Save run_ids and users for a science group."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()
        run_ids = data.get('run_ids', [])
        users = data.get('users', [])

        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        groups = load_science_groups(instrument)
        groups, all_run_ids = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=self._get_instrument_run_ids(instrument),
            persist=True,
        )
        canonical_name = 'All' if self._is_all_science_group(name) else name

        run_ids_clean = sorted({
            str(rid).strip() for rid in (run_ids or []) if str(rid).strip()
        })
        users_clean = sorted({
            str(user).strip() for user in (users or []) if str(user).strip()
        })
        if self._is_all_science_group(canonical_name):
            run_ids_clean = all_run_ids

        groups[canonical_name] = {
            'run_ids': run_ids_clean,
            'users': users_clean,
        }
        groups, _ = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=all_run_ids,
            persist=True,
        )
        # Persist explicitly: _sync_all_science_group only saves when the
        # reserved All entry itself changes, but this endpoint also edits
        # arbitrary groups (users/run_ids) that must always be written.
        save_science_groups(instrument, groups)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, group=groups.get(canonical_name, {}))

    def _api_sci_groups_create(self):
        """Create a new science group."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()

        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        # Validate name (alphanumeric, underscores, hyphens)
        if not re.match(r'^[\w\-]+$', name):
            return jsonify(
                success=False,
                error='Name must be alphanumeric (with _ or -)'
            ), 400

        groups = load_science_groups(instrument)
        groups, _ = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=self._get_instrument_run_ids(instrument),
            persist=True,
        )
        canonical_name = 'All' if self._is_all_science_group(name) else name
        if canonical_name in groups:
            return jsonify(
                success=False, error='Group already exists'
            ), 409

        groups[canonical_name] = {'run_ids': [], 'users': []}
        save_science_groups(instrument, groups)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_sci_groups_delete(self):
        """Delete a science group."""
        user_info, perms = self._require_sci_group_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()

        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        groups = load_science_groups(instrument)
        groups, _ = self._sync_all_science_group(
            instrument,
            groups=groups,
            run_ids=self._get_instrument_run_ids(instrument),
            persist=True,
        )
        canonical_name = 'All' if self._is_all_science_group(name) else name
        if self._is_all_science_group(canonical_name):
            return jsonify(
                success=False, error='The All group cannot be deleted'
            ), 400
        if canonical_name not in groups:
            return jsonify(
                success=False, error='Group not found'
            ), 404

        del groups[canonical_name]
        save_science_groups(instrument, groups)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # APERO profiles API
    # -----------------------------------------------------------------
    def _require_apero_profile_perm(self):
        """Check for manage.apero_profile permission."""
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'manage.apero_profile' not in perms:
            return None, None
        return user_info, perms

    def _require_user_db_access_perm(self):
        """Check for manage.admin.user_db_access permission."""
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'manage.admin.user_db_access' not in perms:
            return None, None
        return user_info, perms

    @staticmethod
    def _db_access_table_keys() -> dict:
        """Map UI table labels to APERO profile table-name keys."""
        return {
            'ASTROM': 'ASTROM_TABLENAME',
            'CALIB': 'CALIB_TABLENAME',
            'FINDEX': 'FINDEX_TABLENAME',
            'LOG': 'LOG_TABLENAME',
            'TELLU': 'TELLU_TABLENAME',
            'REJECT': 'REJECT_TABLENAME',
        }

    def _editable_groups_for_editor(self, user_info, perms):
        """Return groups this editor may grant DB table access to."""
        all_groups = list(self.ari_groups.keys())
        editor_groups = set(user_info.get('groups', []))
        editor_is_admin = user_has_admin_privileges(list(editor_groups))
        editor_is_super_admin = user_is_super_admin(list(editor_groups))
        if editor_is_super_admin:
            return sorted(all_groups)
        if editor_is_admin:
            return sorted([g for g in all_groups if g != 'super_admin'])

        allowed = {g for g in all_groups if f'manage.group.{g}' in perms}
        expanded = set(allowed)
        for g in list(allowed):
            expanded |= set(get_inherited_groups(g, self.ari_groups))
        return sorted(expanded)

    def _find_accessible_profile(self, user_info, profile_id: str,
                                 instrument: str = ''):
        """Find one profile in the editor's accessible profile set."""
        for profile in get_accessible_profiles(user_info, self.ari_groups):
            if profile.get('profile_id') != profile_id:
                continue
            if instrument and profile.get('instrument') != instrument:
                continue
            return profile
        return None

    @staticmethod
    def _q_ident(name: str) -> str:
        """Quote SQL identifier path safely (schema/table)."""
        return '.'.join(f'`{part}`' for part in name.split('.'))

    @staticmethod
    def _profile_get_db(cfg: dict, key: str, default: Any = '') -> Any:
        """Get a DB key from nested ``database`` with flat fallback."""
        db_cfg = cfg.get('database', {}) if isinstance(cfg, dict) else {}
        if not isinstance(db_cfg, dict):
            db_cfg = {}
        if key in db_cfg:
            value = db_cfg.get(key)
            return default if value is None else value
        if isinstance(cfg, dict):
            value = cfg.get(key, default)
            return default if value is None else value
        return default

    @staticmethod
    def _profile_get_path(cfg: dict, key: str, default: Any = '') -> Any:
        """Get a path key from nested ``paths`` with flat fallback."""
        paths_cfg = cfg.get('paths', {}) if isinstance(cfg, dict) else {}
        if not isinstance(paths_cfg, dict):
            paths_cfg = {}
        if key in paths_cfg:
            value = paths_cfg.get(key)
            return default if value is None else value
        if isinstance(cfg, dict):
            value = cfg.get(key, default)
            return default if value is None else value
        return default

    @staticmethod
    def _profile_get_general(cfg: dict, key: str, default: Any = '') -> Any:
        """Get a general key from nested ``general`` with flat fallback."""
        general_cfg = cfg.get('general', {}) if isinstance(cfg, dict) else {}
        if not isinstance(general_cfg, dict):
            general_cfg = {}
        if key in general_cfg:
            value = general_cfg.get(key)
            return default if value is None else value
        if isinstance(cfg, dict):
            value = cfg.get(key, default)
            return default if value is None else value
        return default

    def _profile_db_params(self, profile_cfg: dict) -> dict:
        """Build runtime DB params for one APERO profile."""
        username = str(self._profile_get_db(profile_cfg, 'DATABASE_USERNAME', '')).strip()
        source = self._normalize_db_source(
            self._profile_get_db(profile_cfg, 'DATABASE_SOURCE', '')
        )
        local_name = self._resolve_local_db_name_from_profile_cfg(profile_cfg)
        tunnel_name = self._resolve_tunnel_name_from_profile_cfg(profile_cfg)

        if source == 'local' and local_name:
            local_defs = self._load_local_db_definitions()
            local_def = local_defs.get(local_name, {})
            if isinstance(local_def, dict) and local_def:
                return {
                    'DATABASE_MODE': str(local_def.get('DATABASE_MODE', '') or 'mysql+pymysql').strip(),
                    'DATABASE_SOURCE': source,
                    'DATABASE_LOCAL_NAME': local_name,
                    'DATABASE_TUNNEL_NAME': '',
                    'DATABASE_HOST': str(local_def.get('DATABASE_HOST', '') or '').strip(),
                    'DATABASE_PORT': str(local_def.get('DATABASE_PORT', '') or '3306').strip(),
                    'DATABASE_USERNAME': username,
                    'DATABASE_PASSWORD': str(self._profile_get_db(profile_cfg, 'DATABASE_PASSWORD', '') or ''),
                    'DATABASE_NAME': str(self._profile_get_db(profile_cfg, 'DATABASE_NAME', '')).strip(),
                    'DATABASE_USE_SSH_TUNNEL': False,
                    'DATABASE_SSH_CONFIG_HOST': '',
                    'DATABASE_SSH_LOCAL_PORT': '',
                    'DATABASE_SSH_REMOTE_PORT': '',
                    'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
                }

        if source == 'db_ssh_tunnel' and tunnel_name:
            tunnels = self._load_db_tunnel_definitions()
            tunnel_def = tunnels.get(tunnel_name, {})
            if isinstance(tunnel_def, dict) and tunnel_def:
                tparams = self._build_db_tunnel_runtime_params(
                    tunnel_name, tunnel_def, mode='mysql+pymysql')
                host = str(tparams.get('DATABASE_HOST', '') or '').strip()
                port = str(tparams.get('DATABASE_PORT', '') or '').strip()
                return {
                    'DATABASE_MODE': str(tparams.get('DATABASE_MODE', 'mysql+pymysql')).strip(),
                    'DATABASE_SOURCE': source,
                    'DATABASE_LOCAL_NAME': '',
                    'DATABASE_TUNNEL_NAME': tunnel_name,
                    'DATABASE_HOST': host,
                    'DATABASE_PORT': port,
                    'DATABASE_USERNAME': username,
                    'DATABASE_PASSWORD': str(self._profile_get_db(profile_cfg, 'DATABASE_PASSWORD', '') or ''),
                    'DATABASE_NAME': str(self._profile_get_db(profile_cfg, 'DATABASE_NAME', '')).strip(),
                    'DATABASE_USE_SSH_TUNNEL': True,
                    'DATABASE_SSH_CONFIG_HOST': str(tparams.get('DATABASE_SSH_CONFIG_HOST', '') or '').strip(),
                    'DATABASE_SSH_LOCAL_PORT': str(tparams.get('DATABASE_SSH_LOCAL_PORT', '') or '').strip(),
                    'DATABASE_SSH_REMOTE_PORT': str(tparams.get('DATABASE_SSH_REMOTE_PORT', '') or '').strip(),
                    'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
                }

        return {
            'DATABASE_MODE': '',
            'DATABASE_SOURCE': source,
            'DATABASE_LOCAL_NAME': local_name,
            'DATABASE_TUNNEL_NAME': tunnel_name,
            'DATABASE_HOST': '',
            'DATABASE_PORT': '',
            'DATABASE_USERNAME': username,
            'DATABASE_PASSWORD': str(self._profile_get_db(profile_cfg, 'DATABASE_PASSWORD', '') or ''),
            'DATABASE_NAME': str(self._profile_get_db(profile_cfg, 'DATABASE_NAME', '')).strip(),
            'DATABASE_USE_SSH_TUNNEL': False,
            'DATABASE_SSH_CONFIG_HOST': '',
            'DATABASE_SSH_LOCAL_PORT': '',
            'DATABASE_SSH_REMOTE_PORT': '',
            'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
        }

    def _resolve_db_payload_for_test(self, data: dict) -> dict:
        """Resolve request DB payload into concrete test connection params."""
        mode = str(data.get('DATABASE_MODE', '') or '').strip()
        source = self._normalize_db_source(data.get('DATABASE_SOURCE', ''))
        local_name = str(data.get('DATABASE_LOCAL_NAME', '') or '').strip()
        username = str(data.get('DATABASE_USERNAME', '') or '').strip()
        password = data.get('DATABASE_PASSWORD', '')
        db_name = str(data.get('DATABASE_NAME', '') or '').strip()
        tunnel_name = str(data.get('DATABASE_TUNNEL_NAME', '') or '').strip()

        if not all([username, db_name]):
            return {
                'ok': False,
                'error': 'DATABASE_USERNAME and DATABASE_NAME are required.',
            }

        if source == 'local':
            if not local_name:
                return {'ok': False, 'error': 'DATABASE_LOCAL_NAME is required for local source.'}
            local_defs = self._load_local_db_definitions()
            local_def = local_defs.get(local_name, {})
            if not isinstance(local_def, dict) or not local_def:
                return {'ok': False, 'error': f'Unknown local database definition: {local_name}'}
            mode = str(local_def.get('DATABASE_MODE', '') or 'mysql+pymysql').strip()
            host = str(local_def.get('DATABASE_HOST', '') or '').strip()
            port = str(local_def.get('DATABASE_PORT', '') or '3306').strip()
            if not host:
                return {'ok': False, 'error': 'Selected local database definition has no DATABASE_HOST.'}
            return {
                'ok': True,
                'mode': mode,
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'db_name': db_name,
                'use_ssh_tunnel': False,
                'ssh_config_host': '',
                'ssh_local_port': '',
                'ssh_remote_port': '',
                'database_source': 'local',
                'database_local_name': local_name,
                'database_tunnel_name': '',
            }

        if not tunnel_name:
            return {
                'ok': False,
                'error': 'DATABASE_TUNNEL_NAME is required when source is DB SSH tunnel.',
            }

        tunnels = self._load_db_tunnel_definitions()
        tunnel_def = tunnels.get(tunnel_name, {})
        if not isinstance(tunnel_def, dict) or not tunnel_def:
            return {
                'ok': False,
                'error': f'Unknown DB tunnel definition: {tunnel_name}',
            }

        runtime = self._build_db_tunnel_runtime_params(tunnel_name, tunnel_def, mode='mysql+pymysql')
        try:
            status = apero_async.get_db_tunnel_status(runtime)
        except Exception as exc:
            return {
                'ok': False,
                'error': str(exc),
                'requires_tunnel_admin': True,
                'tunnel_admin_url': url_for('home_admin_portal_database_setup'),
            }

        if not status.get('active'):
            return {
                'ok': False,
                'error': (
                    f'No active DB SSH tunnel for "{tunnel_name}". '
                    'Open Database Setup and start/authenticate it first.'
                ),
                'requires_tunnel_admin': True,
                'tunnel_admin_url': url_for('home_admin_portal_database_setup'),
            }

        return {
            'ok': True,
            'mode': 'mysql+pymysql',
            'host': '127.0.0.1',
            'port': str(status.get('local_port', '') or ''),
            'username': username,
            'password': password,
            'db_name': db_name,
            'use_ssh_tunnel': False,
            'ssh_config_host': '',
            'ssh_local_port': '',
            'ssh_remote_port': '',
            'database_source': 'db_ssh_tunnel',
            'database_local_name': '',
            'database_tunnel_name': tunnel_name,
        }

    def _resolve_profile_db_test_target(self, mode: str, host: str,
                                        port: str, username: str,
                                        password: str, db_name: str,
                                        use_ssh_tunnel: bool,
                                        ssh_config_host: str,
                                        ssh_local_port: str,
                                        ssh_remote_port: str):
        """Resolve DB test target while keeping tunnel setup on admin page."""
        if not use_ssh_tunnel:
            return {
                'mode': mode,
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'db_name': db_name,
                'use_ssh_tunnel': False,
                'ssh_config_host': '',
                'ssh_local_port': '',
                'ssh_remote_port': '',
                'tunnel_required': False,
            }

        db_params = {
            'DATABASE_MODE': mode,
            'DATABASE_HOST': host,
            'DATABASE_PORT': port,
            'DATABASE_USERNAME': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
            'DATABASE_USE_SSH_TUNNEL': True,
            'DATABASE_SSH_CONFIG_HOST': ssh_config_host,
            'DATABASE_SSH_LOCAL_PORT': ssh_local_port,
            'DATABASE_SSH_REMOTE_PORT': ssh_remote_port,
            'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
        }
        status = apero_async.get_db_tunnel_status(db_params)
        if not status.get('active'):
            return {
                'tunnel_required': True,
                'error': (
                    'No active DB SSH tunnel for this profile. '
                    'Open Database Setup and start/authenticate tunnel first.'
                ),
                'tunnel_admin_url': url_for('home_admin_portal_database_setup'),
            }

        return {
            'mode': mode,
            'host': '127.0.0.1',
            'port': str(status.get('local_port', '') or ''),
            'username': username,
            'password': password,
            'db_name': db_name,
            'use_ssh_tunnel': False,
            'ssh_config_host': '',
            'ssh_local_port': '',
            'ssh_remote_port': '',
            'tunnel_required': False,
        }

    def _validate_profile_database(self, profile_cfg: dict) -> dict:
        """Validate one profile DB config using the shared runtime path."""
        db_params = self._profile_db_params(profile_cfg)
        return validate_database_connection(
            db_params.get('DATABASE_MODE', ''),
            db_params.get('DATABASE_HOST', ''),
            db_params.get('DATABASE_USERNAME', ''),
            db_params.get('DATABASE_PASSWORD', ''),
            db_params.get('DATABASE_NAME', ''),
            port=db_params.get('DATABASE_PORT', ''),
            use_ssh_tunnel=db_params.get('DATABASE_USE_SSH_TUNNEL', False),
            ssh_config_host=db_params.get('DATABASE_SSH_CONFIG_HOST', ''),
            ssh_local_port=db_params.get('DATABASE_SSH_LOCAL_PORT', ''),
            ssh_remote_port=db_params.get('DATABASE_SSH_REMOTE_PORT', ''),
            local_data_dir=str(self._resolve_local_data_dir()),
        )

    def _fetch_table_columns(self, profile_cfg: dict, table_name: str):
        """Fetch ordered column names from a profile DB/table."""
        db_params = self._profile_db_params(profile_cfg)
        if ('DATABASE_USER' not in db_params
                and str(db_params.get('DATABASE_USERNAME', '')).strip()):
            db_params['DATABASE_USER'] = str(
                db_params.get('DATABASE_USERNAME', '')).strip()
        mode = str(db_params.get('DATABASE_MODE', '')).strip()
        host = str(db_params.get('DATABASE_HOST', '')).strip()
        username = str(db_params.get('DATABASE_USERNAME', '')).strip()
        db_name = str(db_params.get('DATABASE_NAME', '')).strip()

        if not all([mode, host, username, db_name, table_name]):
            raise ValueError('Missing DB connection or table configuration.')

        if '.' in table_name:
            schema_name, table_only = table_name.split('.', 1)
        else:
            schema_name, table_only = db_name, table_name

        if not re.match(r'^[A-Za-z0-9_]+$', schema_name):
            raise ValueError(f'Invalid schema name: {schema_name}')
        if not re.match(r'^[A-Za-z0-9_]+$', table_only):
            raise ValueError(f'Invalid table name: {table_only}')

        # Probe table existence/read access.
        apero_async.database_query(
            db_params,
            f'SELECT 1 AS ok FROM {self._q_ident(table_name)} LIMIT 1'
        )

        rows = apero_async.database_query(
            db_params,
            (
                'SELECT COLUMN_NAME AS col '
                'FROM information_schema.COLUMNS '
                f"WHERE TABLE_SCHEMA = '{schema_name}' "
                f"AND TABLE_NAME = '{table_only}' "
                'ORDER BY ORDINAL_POSITION'
            ),
        )
        out = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            col = str(row.get('col', '')).strip()
            if col:
                out.append(col)
        return out

    def _profile_db_access_health(self, entry: dict, table_names: list) -> str:
        """Return health status for one profile DB-access config."""
        groups_map = entry.get('groups', {}) if isinstance(entry, dict) else {}
        columns_map = (entry.get('columns', {})
                      if isinstance(entry, dict)
                      else {})
        if not table_names:
            return 'warning'
        for table in table_names:
            glist = groups_map.get(table, [])
            if not isinstance(glist, list) or not glist:
                return 'warning'
            clist = columns_map.get(table, [])
            if not isinstance(clist, list) or not clist:
                return 'warning'
        return 'ok'

    def _build_user_db_access_health_report(self, user_info: dict) -> dict:
        """Build detailed health report for User DB Access rules."""
        if user_info is None:
            # Background / startup refresh has no user context.  Load all
            # profiles directly so the health check isn't limited to the
            # public-only set (which usually finds zero configured tables
            # and emits a spurious warning).
            from apero_ri.core.auth import load_apero_profiles, _hydrate_profile_data
            all_profiles_data = load_apero_profiles(hydrate=False)
            profiles = []
            for instrument, instr_profiles in (all_profiles_data or {}).items():
                if not isinstance(instr_profiles, dict):
                    continue
                for profile_id, profile_data in instr_profiles.items():
                    if not isinstance(profile_data, dict):
                        continue
                    hydrated = _hydrate_profile_data(profile_data, instrument)
                    profiles.append({
                        'instrument': instrument,
                        'profile_id': profile_id,
                        'data': hydrated,
                    })
        else:
            profiles = get_accessible_profiles(user_info, self.ari_groups)
        db_access = load_db_access()
        table_key_map = self._db_access_table_keys()

        checked = 0
        warnings = 0
        profile_rows = []

        for prof in profiles:
            instrument = str(prof.get('instrument', '')).strip()
            profile_id = str(prof.get('profile_id', '')).strip()
            cfg = (prof.get('data', {})
                   if isinstance(prof.get('data'), dict)
                   else {})

            if not instrument or not profile_id:
                continue

            table_names = [
                label for label, key in table_key_map.items()
                if str(self._profile_get_db(cfg, key, '')).strip()
            ]
            if not table_names:
                profile_rows.append({
                    'instrument': instrument,
                    'profile_id': profile_id,
                    'has_tables': False,
                    'status': 'info',
                    'message': 'No configured APERO DB table names for this profile.',
                    'missing_groups': [],
                    'missing_columns': [],
                })
                continue

            checked += 1
            prof_entry = (((db_access.get(instrument, {})
                           if isinstance(db_access.get(instrument, {}), dict)
                           else {}).get(profile_id, {}))
                          if instrument and profile_id else {})
            groups_map = (prof_entry.get('groups', {})
                          if isinstance(prof_entry, dict)
                          else {})
            columns_map = (prof_entry.get('columns', {})
                           if isinstance(prof_entry, dict)
                           else {})

            missing_groups = []
            missing_columns = []
            for table in table_names:
                glist = groups_map.get(table, [])
                if not isinstance(glist, list) or not glist:
                    missing_groups.append(table)
                clist = columns_map.get(table, [])
                if not isinstance(clist, list) or not clist:
                    missing_columns.append(table)

            is_warning = bool(missing_groups or missing_columns)
            if is_warning:
                warnings += 1
                parts = []
                if missing_groups:
                    parts.append(f'missing groups: {", ".join(missing_groups)}')
                if missing_columns:
                    parts.append(f'missing columns: {", ".join(missing_columns)}')
                message = '; '.join(parts)
                status = 'warning'
            else:
                status = 'ok'
                message = f'All {len(table_names)} table rule(s) are configured.'

            profile_rows.append({
                'instrument': instrument,
                'profile_id': profile_id,
                'has_tables': True,
                'status': status,
                'message': message,
                'missing_groups': missing_groups,
                'missing_columns': missing_columns,
            })

        if checked == 0:
            status = 'warning'
            message = ('No APERO profiles with configured table names '
                       'were found for DB-access checks.')
        elif warnings:
            status = 'warning'
            message = f'{warnings} of {checked} profile(s) have incomplete DB table access rules.'
        else:
            status = 'ok'
            message = f'All {checked} profile(s) have complete DB table access rules.'

        profile_rows.sort(
            key=lambda row: (row.get('instrument', ''),
                             row.get('profile_id', '')))
        return {
            'status': status,
            'message': message,
            'checked_profiles': checked,
            'warning_profiles': warnings,
            'profiles': profile_rows,
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }

    def _api_user_db_access_profiles(self):
        """List editor-accessible APERO profiles for DB access management."""
        user_info, perms = self._require_user_db_access_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        profiles = get_accessible_profiles(user_info, self.ari_groups)
        db_access = load_db_access()
        table_key_map = self._db_access_table_keys()

        out = []
        for prof in profiles:
            instrument = str(prof.get('instrument', '')).strip()
            profile_id = str(prof.get('profile_id', '')).strip()
            cfg = (prof.get('data', {})
                   if isinstance(prof.get('data'), dict)
                   else {})

            table_names = []
            for label, key in table_key_map.items():
                if str(self._profile_get_db(cfg, key, '')).strip():
                    table_names.append(label)

            prof_entry = (((db_access.get(instrument, {})
                           if isinstance(db_access.get(instrument, {}), dict)
                           else {}).get(profile_id, {}))
                          if instrument and profile_id else {})

            out.append({
                'instrument': instrument,
                'profile_id': profile_id,
                'has_tables': bool(table_names),
                'health': self._profile_db_access_health(prof_entry, table_names),
            })

        out.sort(key=lambda r: (r['instrument'], r['profile_id']))
        return jsonify(success=True, profiles=out)

    def _api_user_db_access_details(self):
        """Get group toggles and DB columns for one selected profile."""
        user_info, perms = self._require_user_db_access_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        profile_id = request.args.get('profile_id', '').strip()
        instrument = request.args.get('instrument', '').strip()
        if not profile_id or not instrument:
            return jsonify(success=False, error='Missing profile selection'), 400

        profile = self._find_accessible_profile(
            user_info,
            profile_id,
            instrument)
        if not profile:
            return jsonify(success=False, error='Profile not found or access denied'), 404

        editable_groups = self._editable_groups_for_editor(user_info, perms)
        all_groups = list(self.ari_groups.keys())
        cfg = (profile.get('data', {})
               if isinstance(profile.get('data'), dict)
               else {})

        db_access = load_db_access()
        saved_entry = (((db_access.get(instrument, {})
                        if isinstance(db_access.get(instrument, {}), dict)
                        else {}).get(profile_id, {}))
                       if instrument and profile_id else {})
        saved_groups = (saved_entry.get('groups', {})
                       if isinstance(saved_entry, dict)
                       else {})
        saved_columns = (saved_entry.get('columns', {})
                        if isinstance(saved_entry, dict)
                        else {})

        sections = []
        for label, key in self._db_access_table_keys().items():
            table_name = str(self._profile_get_db(cfg, key, '')).strip()
            if not table_name:
                continue

            selected_groups = saved_groups.get(label, [])
            if not isinstance(selected_groups, list):
                selected_groups = []
            selected_groups = [str(g).strip()
                for g in selected_groups
                if str(g).strip()]

            groups_ui = []
            for group_name in all_groups:
                groups_ui.append({
                    'name': group_name,
                    'selected': group_name in selected_groups,
                    'editable': group_name in editable_groups,
                })

            columns_error = ''
            columns_all = []
            try:
                columns_all = self._fetch_table_columns(cfg, table_name)
            except Exception as exc:
                columns_error = str(exc)

            selected_cols = saved_columns.get(label, [])
            if not isinstance(selected_cols, list):
                selected_cols = []
            selected_cols = [str(c).strip()
                for c in selected_cols
                if str(c).strip()]

            if not selected_cols and columns_all:
                selected_cols = list(columns_all)

            columns_ui = []
            selected_set = set(selected_cols)
            for col in columns_all:
                columns_ui.append({
                    'name': col,
                    'selected': col in selected_set,
                })

            sections.append({
                'table': label,
                'table_name': table_name,
                'groups': groups_ui,
                'columns': columns_ui,
                'columns_error': columns_error,
            })

        return jsonify(
            success=True,
            instrument=instrument,
            profile_id=profile_id,
            sections=sections,
            editable_groups=editable_groups,
        )

    def _api_user_db_access_health_check(self):
        """Run User DB Access health check and return detailed diagnostics."""
        user_info, perms = self._require_user_db_access_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        try:
            report = self._build_user_db_access_health_report(user_info)
            instrument = request.args.get('instrument', '').strip()
            profile_id = request.args.get('profile_id', '').strip()
            selected = None
            if instrument and profile_id:
                for row in report.get('profiles', []):
                    if (str(row.get('instrument', '')).strip() == instrument
                            and (str(row.get('profile_id', '')).strip()
                                 == profile_id)):
                        selected = row
                        break

            return jsonify(success=True, report=report, selected=selected)
        except Exception as exc:
            return jsonify(success=False,
                           error=f'User DB access health check failed: {exc}'), 500

    def _api_user_db_access_save(self):
        """Persist group/column access for one profile into db_access.yaml."""
        user_info, perms = self._require_user_db_access_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = str(data.get('instrument', '')).strip()
        profile_id = str(data.get('profile_id', '')).strip()
        groups_map = data.get('groups', {})
        columns_map = data.get('columns', {})

        if not instrument or not profile_id:
            return jsonify(success=False, error='Missing profile selection'), 400
        if (not isinstance(groups_map, dict)
                or not isinstance(columns_map, dict)):
            return jsonify(success=False, error='Invalid groups/columns payload'), 400

        profile = self._find_accessible_profile(
            user_info,
            profile_id,
            instrument)
        if not profile:
            return jsonify(success=False, error='Profile not found or access denied'), 404

        editable_groups = set(
            self._editable_groups_for_editor(user_info,
            perms))

        cfg = (profile.get('data', {})
               if isinstance(profile.get('data'), dict)
               else {})
        valid_tables = {
            label for label, key in self._db_access_table_keys().items()
            if str(self._profile_get_db(cfg, key, '')).strip()
        }

        db_access = load_db_access()
        existing_entry = (((db_access.get(instrument, {})
                           if isinstance(db_access.get(instrument, {}), dict)
                           else {}).get(profile_id, {}))
                          if instrument and profile_id else {})
        existing_groups_map = (existing_entry.get('groups', {})
                               if isinstance(existing_entry, dict) else {})

        cleaned_groups = {}
        for table, raw_groups in groups_map.items():
            if table not in valid_tables:
                continue
            if not isinstance(raw_groups, list):
                return jsonify(success=False,
                               error=f'groups[{table}] must be a list'), 400

            existing_for_table = existing_groups_map.get(table, [])
            if not isinstance(existing_for_table, list):
                existing_for_table = []
            existing_for_table = [str(g).strip() for g in existing_for_table
                                  if str(g).strip()]

            preserved_noneditable = [
                g for g in existing_for_table if g not in editable_groups
            ]
            vals = list(preserved_noneditable)
            for g in raw_groups:
                gname = str(g).strip()
                if not gname:
                    continue
                if gname not in self.ari_groups:
                    continue
                if (gname not in editable_groups
                        and gname not in existing_for_table):
                    return jsonify(success=False,
                                   error=f'No permission to assign group: {gname}'), 403
                if gname not in vals:
                    vals.append(gname)
            cleaned_groups[table] = vals

        cleaned_cols = {}
        table_columns = {}
        for label, key in self._db_access_table_keys().items():
            if label not in valid_tables:
                continue
            table_name = str(self._profile_get_db(cfg, key, '')).strip()
            try:
                table_columns[label] = self._fetch_table_columns(
                    cfg, table_name)
            except Exception as exc:
                return jsonify(
                    success=False,
                    error=f'Unable to validate columns for {label}: {exc}',
                ), 400

        for table, raw_cols in columns_map.items():
            if table not in valid_tables:
                continue
            if not isinstance(raw_cols, list):
                return jsonify(success=False,
                               error=f'columns[{table}] must be a list'), 400
            allowed_cols = set(table_columns.get(table, []))
            cols = []
            for col in raw_cols:
                cname = str(col).strip()
                if cname and cname not in allowed_cols:
                    return jsonify(success=False,
                                   error=f'Invalid column for {table}: {cname}'), 400
                if cname and cname not in cols:
                    cols.append(cname)
            cleaned_cols[table] = cols

        # Ensure all valid tables exist in saved structure.
        for table in valid_tables:
            cleaned_groups.setdefault(table, [])
            cleaned_cols.setdefault(table, [])

        inst_access = db_access.get(instrument)
        if instrument not in db_access or not isinstance(inst_access, dict):
            db_access[instrument] = {}
        db_access[instrument][profile_id] = {
            'groups': cleaned_groups,
            'columns': cleaned_cols,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        save_db_access(db_access)

        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_apero_profiles_list(self):
        """List APERO profiles for an instrument."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='No instrument'), 400

        params = load_parameters()
        valid = params.get('instruments', {}).get('value', [])
        if instrument not in valid:
            return jsonify(success=False, error='Invalid instrument'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        inst_profiles = all_profiles.get(instrument, {})

        # Keys stored per profile (served flat to UI for compatibility)
        _DB_KEYS = [
            'DATABASE_USERNAME', 'DATABASE_PASSWORD', 'DATABASE_NAME',
            'DATABASE_SOURCE', 'DATABASE_LOCAL_NAME', 'DATABASE_TUNNEL_NAME',
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
        ]
        _PATH_KEYS = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_OUT', 'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]

        # Build list with validation status, sorted by DISPLAY_ORDER
        profiles = []
        profile_errors = []
        for name, cfg in inst_profiles.items():
            entry = {
                'name': name,
                'DISPLAY_ORDER': cfg.get('DISPLAY_ORDER', 999),
                'groups': cfg.get('groups', []),
                'apero_version': cfg.get('apero_version', ''),
                'reduction_server': cfg.get('reduction_server', ''),
            }
            # Copy DB fields
            for k in _DB_KEYS:
                entry[k] = self._profile_get_db(cfg, k, '')
            entry['DATABASE_SOURCE'] = self._normalize_db_source(
                entry.get('DATABASE_SOURCE', '')
            )
            entry['SCIENCE_FIBER'] = self._profile_get_general(
                cfg, 'SCIENCE_FIBER', '')
            # SCIENCE_TYPES is a list
            entry['SCIENCE_TYPES'] = self._profile_get_general(
                cfg, 'SCIENCE_TYPES', [])
            entry['APERO_INSTRUMENT_PROFILE'] = cfg.get(
                'APERO_INSTRUMENT_PROFILE', '')
            # Copy path fields with exists check
            all_paths_ok = True
            for k in _PATH_KEYS:
                val = self._profile_get_path(cfg, k, '')
                entry[k] = val
                if val:
                    entry[k + '_exists'] = Path(val).is_dir()
                    if not entry[k + '_exists']:
                        all_paths_ok = False
                else:
                    entry[k + '_exists'] = False
                    all_paths_ok = False
            entry['all_paths_ok'] = all_paths_ok

            # DB check used by admin home red-cross logic (db/path only)
            db_check = self._validate_profile_database(cfg)
            db_ok = bool(db_check.get('valid', False))
            db_error = str(db_check.get('error', '')).strip()
            entry['db_ok'] = db_ok
            entry['db_error'] = db_error

            reasons = []
            if not db_ok:
                reasons.append(f'db: {db_error or "connection failed"}')
            if not all_paths_ok:
                reasons.append('paths: missing or invalid directory')
            entry['status_reasons'] = reasons
            if reasons:
                profile_errors.append(
                    f"Instrument {instrument} profile {name}: {'; '.join(reasons)}"
                )

            profiles.append(entry)

        profiles.sort(key=lambda p: p['DISPLAY_ORDER'])

        if not profiles:
            status = {
                'level': 'warning',
                'headline': 'No APERO profiles configured for this instrument.',
                'details': [],
            }
        elif profile_errors:
            status = {
                'level': 'error',
                'headline': f'{len(profile_errors)} profile(s) need attention.',
                'details': profile_errors,
            }
        else:
            status = {
                'level': 'ok',
                'headline': 'Everything ready for this instrument.',
                'details': [],
            }

        return jsonify(success=True, profiles=profiles, status=status)

    def _api_apero_profiles_overview(self):
        """Return all-instruments APERO profile readiness summary."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        overview = self._build_apero_profiles_overview_status()
        return jsonify(
            success=True,
            status=overview.get('status', {}),
            total_profiles=overview.get('total_profiles', 0),
        )

    def _api_apero_profiles_save(self):
        """Create or update an APERO profile."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()

        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        if not re.match(r'^[\w\-]+$', name):
            return jsonify(
                success=False,
                error='Name must be alphanumeric (with _ or -)'
            ), 400

        # Collect all required fields
        _META_KEYS = ['apero_version', 'reduction_server']
        _DB_REQUIRED_KEYS = [
            'DATABASE_USERNAME',
            'DATABASE_NAME', 'ASTROM_TABLENAME', 'CALIB_TABLENAME',
            'FINDEX_TABLENAME', 'LOG_TABLENAME', 'TELLU_TABLENAME',
            'REJECT_TABLENAME',
        ]
        _DB_OPTIONAL_KEYS = [
            'DATABASE_PASSWORD', 'DATABASE_SOURCE',
            'DATABASE_LOCAL_NAME', 'DATABASE_TUNNEL_NAME',
        ]
        # Store instrument profile file reference (optional, no validation)
        _apero_instrument_profile = str(
            data.get('APERO_INSTRUMENT_PROFILE', '') or ''
        ).strip()
        _PATH_KEYS = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_OUT', 'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]

        values = {}
        for k in _META_KEYS:
            val = data.get(k, '').strip()
            if not val:
                return jsonify(
                    success=False,
                    error=f'{k} is required'
                ), 400
            values[k] = val

        db_values = {}
        for k in _DB_REQUIRED_KEYS:
            val = data.get(k, '').strip()
            if not val:
                return jsonify(
                    success=False,
                    error=f'{k} is required'
                ), 400
            db_values[k] = val
        db_values['DATABASE_PASSWORD'] = data.get('DATABASE_PASSWORD', '')
        for k in _DB_OPTIONAL_KEYS:
            if k == 'DATABASE_PASSWORD':
                continue
            db_values[k] = str(data.get(k, '') or '').strip()

        database_source = self._normalize_db_source(data.get('DATABASE_SOURCE', ''))
        local_name = str(data.get('DATABASE_LOCAL_NAME', '') or '').strip()
        tunnel_name = str(data.get('DATABASE_TUNNEL_NAME', '') or '').strip()

        db_values['DATABASE_SOURCE'] = database_source
        db_values['DATABASE_LOCAL_NAME'] = local_name
        db_values['DATABASE_TUNNEL_NAME'] = tunnel_name

        if database_source == 'local':
            if not local_name:
                return jsonify(
                    success=False,
                    error='DATABASE_LOCAL_NAME is required when DATABASE_SOURCE is local'
                ), 400
            local_defs = self._load_local_db_definitions()
            local_def = local_defs.get(local_name, {})
            if not isinstance(local_def, dict) or not local_def:
                return jsonify(
                    success=False,
                    error=f'Unknown local database definition: {local_name}'
                ), 400
            db_values.pop('DATABASE_MODE', None)
            db_values.pop('DATABASE_HOST', None)
            db_values.pop('DATABASE_PORT', None)
            db_values['DATABASE_TUNNEL_NAME'] = ''
        else:
            if not tunnel_name:
                return jsonify(
                    success=False,
                    error='DATABASE_TUNNEL_NAME is required when DATABASE_SOURCE is db_ssh_tunnel'
                ), 400
            tunnels = self._load_db_tunnel_definitions()
            tunnel_def = tunnels.get(tunnel_name, {})
            if not isinstance(tunnel_def, dict) or not tunnel_def:
                return jsonify(
                    success=False,
                    error=f'Unknown DB tunnel definition: {tunnel_name}'
                ), 400
            # Keep local DB host/port fields empty in tunnel mode; runtime resolves
            # from selected tunnel definition.
            db_values.pop('DATABASE_MODE', None)
            db_values.pop('DATABASE_HOST', None)
            db_values.pop('DATABASE_PORT', None)
            db_values['DATABASE_LOCAL_NAME'] = ''

        science_fiber = str(data.get('SCIENCE_FIBER', '')).strip()
        if not science_fiber:
            return jsonify(success=False, error='SCIENCE_FIBER is required'), 400

        path_values = {}
        for k in _PATH_KEYS:
            val = data.get(k, '').strip()
            if not val:
                return jsonify(
                    success=False,
                    error=f'{k} is required'
                ), 400
            if not os.path.isabs(val):
                return jsonify(
                    success=False,
                    error=f'{k} must be an absolute path'
                ), 400
            path_values[k] = val

        # SCIENCE_TYPES: accepted as a list or comma-separated string
        science_types_raw = data.get('SCIENCE_TYPES', [])
        if isinstance(science_types_raw, str):
            science_types = [t.strip()
                for t in science_types_raw.split(',')
                if t.strip()]
        else:
            science_types = [str(t).strip()
                for t in science_types_raw
                if str(t).strip()]
        if not science_types:
            return jsonify(success=False, error='SCIENCE_TYPES is required'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        inst_profiles = all_profiles.setdefault(instrument, {})

        # Preserve display_order if editing, else assign next
        if name in inst_profiles:
            order = inst_profiles[name].get('DISPLAY_ORDER', 999)
        else:
            max_order = max(
                (p.get('DISPLAY_ORDER', 0) for p in inst_profiles.values()),
                default=0
            )
            order = max_order + 1

        # Groups are required and can be provided on save.
        if name in inst_profiles:
            existing_groups = inst_profiles[name].get('groups', [])
        else:
            existing_groups = []
        new_groups = data.get('groups', existing_groups)
        if not isinstance(new_groups, list):
            return jsonify(success=False,
                           error='groups must be a list'), 400
        new_groups = [str(g).strip() for g in new_groups if str(g).strip()]
        if not new_groups:
            return jsonify(success=False,
                           error='At least one group is required'), 400

        profile_data = {'DISPLAY_ORDER': order, 'groups': new_groups}
        profile_data.update(values)
        profile_data['database'] = dict(db_values)
        profile_data['paths'] = dict(path_values)
        profile_data['general'] = {
            'INSTRUMENT': instrument,
            'SCIENCE_FIBER': science_fiber,
            'SCIENCE_TYPES': science_types,
        }
        if _apero_instrument_profile:
            profile_data['APERO_INSTRUMENT_PROFILE'] = (
                _apero_instrument_profile)
            # Validate selected APERO instrument profile exists.
            preset_path = (PACKAGE_DIR / 'resources' / 'aprofile_instruments'
                           / _apero_instrument_profile)
            if not preset_path.is_file():
                return jsonify(success=False,
                               error=f'Instrument profile file not found: {_apero_instrument_profile}'), 400
        inst_profiles[name] = profile_data
        save_apero_profiles(all_profiles)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_apero_profiles_delete(self):
        """Delete an APERO profile and remove all matching profile directories."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()
        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        inst_profiles = all_profiles.get(instrument, {})
        if name not in inst_profiles:
            return jsonify(
                success=False, error='Profile not found'
            ), 404

        del inst_profiles[name]
        all_profiles[instrument] = inst_profiles
        save_apero_profiles(all_profiles)
        
        # Clean up all directories named after this profile from local data directory
        import shutil
        local_data_dir = self._resolve_local_data_dir()
        if local_data_dir and os.path.isdir(local_data_dir):
            for item in Path(local_data_dir).rglob(name):
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                    except Exception:
                        pass  # Log silently; don't block profile deletion on cleanup errors
        
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_apero_profiles_reorder(self):
        """Update the DISPLAY_ORDER of profiles after drag reorder."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        order_list = data.get('order', [])
        if not instrument or not order_list:
            return jsonify(success=False, error='Missing fields'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        inst_profiles = all_profiles.get(instrument, {})

        for idx, name in enumerate(order_list, start=1):
            if name in inst_profiles:
                inst_profiles[name]['DISPLAY_ORDER'] = idx

        all_profiles[instrument] = inst_profiles
        save_apero_profiles(all_profiles)
        return jsonify(success=True)

    def _api_apero_profiles_validate(self):
        """Validate a path exists as a directory."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        path = request.args.get('path', '').strip()
        if not path:
            return jsonify(success=False, error='No path'), 400
        if not os.path.isabs(path):
            return jsonify(success=False, error='Must be absolute'), 400

        result = validate_path_exists(path)
        return jsonify(success=True, **result)

    def _api_apero_profiles_browse(self):
        """Browse server directories for the file browser."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        path = request.args.get('path', '/').strip()
        if not os.path.isabs(path):
            return jsonify(success=False, error='Must be absolute'), 400

        target = Path(path)
        if not target.is_dir():
            return jsonify(success=False, error='Not a directory'), 400

        dirs = []
        try:
            for entry in sorted(target.iterdir()):
                try:
                    is_dir = entry.is_dir()
                except PermissionError:
                    continue
                if is_dir and not entry.name.startswith('.'):
                    dirs.append(entry.name)
        except PermissionError:
            return jsonify(success=False,
                           error='Permission denied'), 403

        # Check if this directory exists
        validation = validate_path_exists(str(target))
        return jsonify(
            success=True,
            path=str(target),
            dirs=dirs,
            validation=validation,
        )

    def _api_apero_profiles_update_groups(self):
        """Update the groups assigned to an APERO profile."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        perms = perms or set()

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        name = data.get('name', '').strip()
        new_groups = data.get('groups', [])
        if not instrument or not name:
            return jsonify(success=False, error='Missing fields'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        inst_profiles = all_profiles.get(instrument, {})
        if name not in inst_profiles:
            return jsonify(success=False, error='Profile not found'), 404

        old_groups = set(inst_profiles[name].get('groups', []))
        changed = ((set(new_groups) - old_groups)
                   | (old_groups - set(new_groups)))
        for g in changed:
            if f'manage.group.{g}' not in perms:
                return jsonify(
                    success=False,
                    error=f'No permission to manage group: {g}'
                ), 403

        inst_profiles[name]['groups'] = new_groups
        save_apero_profiles(all_profiles)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_apero_profiles_test_db(self):
        """Test a database connection with the given credentials."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        resolved = self._resolve_db_payload_for_test(data)
        if not resolved.get('ok') and resolved.get('requires_tunnel_admin'):
            return jsonify(
                success=True,
                valid=False,
                requires_tunnel_admin=True,
                error=resolved.get('error', 'DB tunnel required.'),
                tunnel_admin_url=resolved.get('tunnel_admin_url', ''),
            )
        if not resolved.get('ok'):
            return jsonify(success=False, error=resolved.get('error', 'Invalid database payload')), 400

        result = validate_database_connection(
            resolved['mode'], resolved['host'], resolved['username'],
            resolved['password'], resolved['db_name'],
            port=resolved['port'],
            use_ssh_tunnel=resolved['use_ssh_tunnel'],
            ssh_config_host=resolved['ssh_config_host'],
            ssh_local_port=resolved['ssh_local_port'],
            ssh_remote_port=resolved['ssh_remote_port'],
            local_data_dir=str(self._resolve_local_data_dir()),
        )
        return jsonify(success=True, **result)

    def _api_apero_profiles_list_tables(self):
        """List available tables in the selected APERO profile database."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        resolved = self._resolve_db_payload_for_test(data)
        if not resolved.get('ok') and resolved.get('requires_tunnel_admin'):
            return jsonify(
                success=True,
                valid=False,
                tables=[],
                requires_tunnel_admin=True,
                error=resolved.get('error', 'DB tunnel required.'),
                tunnel_admin_url=resolved.get('tunnel_admin_url', ''),
            )
        if not resolved.get('ok'):
            return jsonify(success=False, error=resolved.get('error', 'Invalid database payload')), 400

        db_params = {
            'DATABASE_MODE': resolved['mode'],
            'DATABASE_HOST': resolved['host'],
            'DATABASE_PORT': resolved['port'],
            'DATABASE_USER': resolved['username'],
            'DATABASE_PASSWORD': resolved['password'],
            'DATABASE_NAME': resolved['db_name'],
            'DATABASE_USE_SSH_TUNNEL': resolved['use_ssh_tunnel'],
            'DATABASE_SSH_CONFIG_HOST': resolved['ssh_config_host'],
            'DATABASE_SSH_LOCAL_PORT': resolved['ssh_local_port'],
            'DATABASE_SSH_REMOTE_PORT': resolved['ssh_remote_port'],
            'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
        }

        sql_db_name = str(resolved['db_name']).replace("'", "''")
        query = (
            'SELECT table_name '
            'FROM information_schema.tables '
            f"WHERE table_schema = '{sql_db_name}' "
            'ORDER BY table_name'
        )

        try:
            rows = apero_async.database_query(db_params, query)
            tables = sorted({
                str(row.get('table_name')).strip()
                for row in (rows or [])
                if isinstance(row, dict)
                and str(row.get('table_name') or '').strip()
            })
            return jsonify(success=True, valid=True, tables=tables)
        except Exception as exc:
            return jsonify(success=True, valid=False,
                           error=str(exc), tables=[])

    # -----------------------------------------------------------------
    # Interactive SSH tunnel for APERO profile DB connections
    # -----------------------------------------------------------------
    def _api_apero_profiles_ssh_tunnel_start(self):
        """Start an interactive SSH tunnel session for DB access."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        from apero_ri.core.sshfs_interactive import start_interactive_ssh_tunnel

        body = request.get_json(silent=True) or {}
        ssh_config_host = str(body.get('ssh_config_host', '')).strip()
        local_port = body.get('local_port', 0)
        remote_host = str(body.get('remote_host', '')).strip()
        remote_port = body.get('remote_port', 3306)
        allow_multiple = bool(body.get('allow_multiple', False))

        try:
            local_port = int(local_port)
            remote_port = int(remote_port)
        except (ValueError, TypeError):
            return jsonify(ok=False, error='Invalid port number'), 400

        if not allow_multiple:
            singleton = apero_async.ensure_single_db_tunnel_slot({
                'DATABASE_SSH_CONFIG_HOST': ssh_config_host,
                'DATABASE_HOST': remote_host,
                'DATABASE_SSH_LOCAL_PORT': local_port,
                'DATABASE_SSH_REMOTE_PORT': remote_port,
                'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
            })
            if not singleton.get('ok'):
                return jsonify(ok=False, error=singleton.get('error', 'Failed to enforce single active DB SSH tunnel policy.')), 400

        result = start_interactive_ssh_tunnel(
            ssh_config_host=ssh_config_host,
            local_port=local_port,
            remote_host=remote_host,
            remote_port=remote_port,
            local_data_dir=str(self._resolve_local_data_dir()),
        )
        return jsonify(**result)

    def _api_apero_profiles_ssh_tunnel_poll(self):
        """Poll output from an interactive SSH tunnel session."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        from apero_ri.core.sshfs_interactive import poll_session

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        if not token:
            return jsonify(ok=False, error='token required'), 400
        return jsonify(**poll_session(token))

    def _api_apero_profiles_ssh_tunnel_send(self):
        """Send input to an interactive SSH tunnel session."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        from apero_ri.core.sshfs_interactive import send_input

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        data = str(body.get('data', ''))
        if not token:
            return jsonify(ok=False, error='token required'), 400
        return jsonify(**send_input(token, data))

    def _api_apero_profiles_ssh_tunnel_close(self):
        """Close and clean up an interactive SSH tunnel session."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        from apero_ri.core.sshfs_interactive import close_session

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        if not token:
            return jsonify(ok=False, error='token required'), 400
        return jsonify(**close_session(token))

    def _api_db_ssh_tunnel_status(self):
        """List tunnel status for all saved DB tunnel definitions."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        rows = self._list_db_tunnel_rows()
        active_count = sum(1 for row in rows if bool((row.get('status') or {}).get('active')))

        return jsonify(
            success=True,
            tunnels=rows,
            active_count=active_count,
            multi_active_supported=True,
        )

    def _api_db_ssh_tunnel_ssh_hosts(self):
        """List SSH config host aliases from ~/.ssh/config for dropdowns."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        return jsonify(success=True, hosts=self._list_ssh_config_hosts())

    def _api_db_ssh_tunnel_list(self):
        """List DB tunnel definitions for setup UI and profile dropdowns."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        tunnels = self._load_db_tunnel_definitions()
        rows = []
        for name in sorted(tunnels.keys()):
            tdef = tunnels.get(name, {})
            if not isinstance(tdef, dict):
                continue
            rows.append({
                'name': name,
                'ssh_config_host': str(tdef.get('ssh_config_host', '') or '').strip(),
                'remote_host': str(tdef.get('remote_host', '') or '').strip(),
                'remote_port': str(tdef.get('remote_port', '') or '').strip() or '3306',
                'local_port': str(tdef.get('local_port', '') or '').strip(),
                'DATABASE_USERNAME': str(tdef.get('DATABASE_USERNAME', '') or '').strip(),
                'DATABASE_PASSWORD': str(tdef.get('DATABASE_PASSWORD', '') or ''),
                'DATABASE_NAME': str(tdef.get('DATABASE_NAME', '') or '').strip(),
                'notes': str(tdef.get('notes', '') or '').strip(),
            })
        return jsonify(success=True, tunnels=rows)

    def _api_db_ssh_tunnel_save(self):
        """Create or update one DB tunnel definition."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        name = str(body.get('name', '') or '').strip()
        ssh_config_host = str(body.get('ssh_config_host', '') or '').strip()
        remote_host = str(body.get('remote_host', '') or '').strip()
        remote_port = str(body.get('remote_port', '') or '').strip()
        local_port = str(body.get('local_port', '') or '').strip()
        username = str(body.get('DATABASE_USERNAME', '') or '').strip()
        password = str(body.get('DATABASE_PASSWORD', '') or '')
        db_name = str(body.get('DATABASE_NAME', '') or '').strip()
        notes = str(body.get('notes', '') or '').strip()

        if not name:
            return jsonify(success=False, error='name is required'), 400
        if not re.match(r'^[A-Za-z0-9_\-]+$', name):
            return jsonify(success=False,
                           error='name must be alphanumeric, dash, or underscore'), 400
        if not ssh_config_host:
            return jsonify(success=False, error='ssh_config_host is required'), 400
        if not remote_host:
            return jsonify(success=False, error='remote_host is required'), 400
        if not local_port:
            return jsonify(success=False, error='local_port is required'), 400
        if not str(remote_port).isdigit() or not str(local_port).isdigit():
            return jsonify(success=False, error='local_port and remote_port must be numeric'), 400

        tunnels = self._load_db_tunnel_definitions()
        tunnels[name] = {
            'ssh_config_host': ssh_config_host,
            'remote_host': remote_host,
            'remote_port': remote_port,
            'local_port': local_port,
            'DATABASE_USERNAME': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
            'notes': notes,
        }
        self._save_db_tunnel_definitions(tunnels)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_db_ssh_tunnel_delete(self):
        """Delete one DB tunnel definition."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        name = str(body.get('name', '') or '').strip()
        if not name:
            return jsonify(success=False, error='name is required'), 400

        all_profiles = load_apero_profiles(hydrate=False)
        in_use = []
        for instrument, inst_profiles in (all_profiles or {}).items():
            if not isinstance(inst_profiles, dict):
                continue
            for profile_name, profile_cfg in inst_profiles.items():
                cfg = profile_cfg if isinstance(profile_cfg, dict) else {}
                source = self._normalize_db_source(
                    self._profile_get_db(cfg, 'DATABASE_SOURCE', ''))
                tname = self._resolve_tunnel_name_from_profile_cfg(cfg)
                if source == 'db_ssh_tunnel' and tname == name:
                    in_use.append(f'{instrument}/{profile_name}')

        if in_use:
            return jsonify(success=False,
                           error=('Tunnel is used by profile(s): '
                                  + ', '.join(in_use))), 400

        tunnels = self._load_db_tunnel_definitions()
        if name not in tunnels:
            return jsonify(success=False, error='Tunnel not found'), 404

        del tunnels[name]
        self._save_db_tunnel_definitions(tunnels)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_db_ssh_tunnel_ensure(self):
        """Ensure selected named tunnel is active."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        tunnel_name = str(body.get('tunnel_name', '') or '').strip()
        if not tunnel_name:
            return jsonify(success=False,
                           error='tunnel_name is required'), 400

        tunnels = self._load_db_tunnel_definitions()
        tunnel_def = tunnels.get(tunnel_name, {})
        if not isinstance(tunnel_def, dict) or not tunnel_def:
            return jsonify(success=False, error='Tunnel not found'), 404

        db_params = self._build_db_tunnel_runtime_params(tunnel_name, tunnel_def)

        try:
            host, port = apero_async._ensure_ssh_tunnel(db_params)
            status = apero_async.get_db_tunnel_status(db_params)
            return jsonify(success=True,
                           message='DB SSH tunnel is active (or started).',
                           tunnel_name=tunnel_name,
                           local_host=host,
                           local_port=port,
                           status=status)
        except Exception as exc:
            return jsonify(success=False,
                           error=f'Failed to ensure DB tunnel: {exc}'), 500

    def _api_db_ssh_tunnel_close(self):
        """Close one selected named DB tunnel or all saved DB tunnels."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        close_all = bool(body.get('close_all', False))
        rows = self._list_db_tunnel_rows()

        if close_all:
            seen_controls = set()
            closed = 0
            failed = []
            for row in rows:
                if not row.get('valid_config'):
                    continue
                try:
                    status = row.get('status', {}) if isinstance(row.get('status'), dict) else {}
                    control_path = str(status.get('control_path', '') or '')
                    if not control_path or control_path in seen_controls:
                        continue
                    seen_controls.add(control_path)
                    tdef = row.get('definition', {}) if isinstance(row.get('definition'), dict) else {}
                    db_params = self._build_db_tunnel_runtime_params(
                        str(row.get('name', '') or ''), tdef)
                    result = apero_async.close_db_tunnel(db_params)
                    if result.get('ok'):
                        closed += 1
                    else:
                        failed.append(result.get('error', 'Unknown close error'))
                except Exception as exc:
                    failed.append(str(exc))

            if failed:
                return jsonify(success=False,
                               error='; '.join(failed),
                               closed=closed)
            return jsonify(success=True,
                           message='Closed all DB SSH tunnels.',
                           closed=closed)

        tunnel_name = str(body.get('tunnel_name', '') or '').strip()
        if not tunnel_name:
            return jsonify(success=False,
                           error='tunnel_name is required'), 400

        tunnels = self._load_db_tunnel_definitions()
        tunnel_def = tunnels.get(tunnel_name, {})
        if not isinstance(tunnel_def, dict) or not tunnel_def:
            return jsonify(success=False, error='Tunnel not found'), 404

        db_params = self._build_db_tunnel_runtime_params(tunnel_name, tunnel_def)
        result = apero_async.close_db_tunnel(db_params)
        status_code = 200 if result.get('ok') else 500
        return jsonify(success=bool(result.get('ok')),
                       **result), status_code

    def _api_db_ssh_tunnel_test(self):
        """Test one DB SSH tunnel definition using stored or supplied test credentials."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        name = str(body.get('name', '') or '').strip()
        ssh_config_host = str(body.get('ssh_config_host', '') or '').strip()
        remote_host = str(body.get('remote_host', '') or '').strip()
        remote_port = str(body.get('remote_port', '') or '').strip() or '3306'
        local_port = str(body.get('local_port', '') or '').strip()
        username = str(body.get('DATABASE_USERNAME', '') or '').strip()
        password = str(body.get('DATABASE_PASSWORD', '') or '')
        db_name = str(body.get('DATABASE_NAME', '') or '').strip()

        has_direct_tunnel_fields = bool(
            ssh_config_host or remote_host or local_port
        )

        if name and not has_direct_tunnel_fields:
            tunnels = self._load_db_tunnel_definitions()
            tdef = tunnels.get(name, {})
            if not isinstance(tdef, dict) or not tdef:
                return jsonify(success=False, error='Tunnel not found'), 404
            ssh_config_host = ssh_config_host or str(tdef.get('ssh_config_host', '') or '').strip()
            remote_host = remote_host or str(tdef.get('remote_host', '') or '').strip()
            remote_port = remote_port or str(tdef.get('remote_port', '') or '').strip()
            local_port = local_port or str(tdef.get('local_port', '') or '').strip()
            username = username or str(tdef.get('DATABASE_USERNAME', '') or '').strip()
            password = password or str(tdef.get('DATABASE_PASSWORD', '') or '')
            db_name = db_name or str(tdef.get('DATABASE_NAME', '') or '').strip()

        remote_port = remote_port or '3306'

        if not ssh_config_host:
            return jsonify(success=False, error='DATABASE_SSH_CONFIG_HOST is required'), 400
        if not remote_host:
            return jsonify(success=False, error='DATABASE_HOST is required'), 400
        if not local_port:
            return jsonify(success=False, error='DATABASE_SSH_LOCAL_PORT is required'), 400
        if not str(remote_port).isdigit() or not str(local_port).isdigit():
            return jsonify(success=False, error='DATABASE_SSH_LOCAL_PORT and DATABASE_SSH_REMOTE_PORT must be numeric'), 400
        if not username or not db_name:
            return jsonify(success=False, error='DATABASE_USERNAME and DATABASE_NAME are required'), 400

        runtime = self._build_db_tunnel_runtime_params(
            name or '__adhoc__',
            {
                'ssh_config_host': ssh_config_host,
                'remote_host': remote_host,
                'remote_port': remote_port,
                'local_port': local_port,
            },
            mode='mysql+pymysql',
        )
        # Test Connection should be self-contained: attempt tunnel bring-up
        # from the provided definition and then run SELECT 1.
        result = validate_database_connection(
            'mysql+pymysql',
            remote_host,
            username,
            password,
            db_name,
            port=str(local_port),
            use_ssh_tunnel=True,
            ssh_config_host=ssh_config_host,
            ssh_local_port=str(local_port),
            ssh_remote_port=str(remote_port),
            local_data_dir=str(self._resolve_local_data_dir()),
        )

        if not result.get('valid'):
            err = str(result.get('error', '') or '')
            if ('batchmode' in err.lower() or 'permission denied' in err.lower()
                    or 'passphrase' in err.lower()):
                err = (
                    f'{err} Interactive Auth may be required for this SSH host.'
                ).strip()
                result['error'] = err

        return jsonify(success=True, **result)

    def _api_database_setup_local_db_list(self):
        """List reusable local database definitions."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        defs = self._load_local_db_definitions()
        rows = []
        for name in sorted(defs.keys()):
            item = defs.get(name, {})
            if not isinstance(item, dict):
                continue
            rows.append({
                'name': name,
                'DATABASE_MODE': str(item.get('DATABASE_MODE', '') or '').strip() or 'mysql+pymysql',
                'DATABASE_HOST': str(item.get('DATABASE_HOST', '') or '').strip(),
                'DATABASE_PORT': str(item.get('DATABASE_PORT', '') or '').strip() or '3306',
                'DATABASE_USERNAME': str(item.get('DATABASE_USERNAME', '') or '').strip(),
                'DATABASE_PASSWORD': str(item.get('DATABASE_PASSWORD', '') or ''),
                'DATABASE_NAME': str(item.get('DATABASE_NAME', '') or '').strip(),
                'notes': str(item.get('notes', '') or '').strip(),
            })
        return jsonify(success=True, local_databases=rows)

    def _api_database_setup_local_db_save(self):
        """Create/update one reusable local database definition."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        name = str(body.get('name', '') or '').strip()
        mode = str(body.get('DATABASE_MODE', '') or '').strip() or 'mysql+pymysql'
        host = str(body.get('DATABASE_HOST', '') or '').strip()
        port = str(body.get('DATABASE_PORT', '') or '').strip() or '3306'
        username = str(body.get('DATABASE_USERNAME', '') or '').strip()
        password = str(body.get('DATABASE_PASSWORD', '') or '')
        db_name = str(body.get('DATABASE_NAME', '') or '').strip()
        notes = str(body.get('notes', '') or '').strip()

        if not name:
            return jsonify(success=False, error='name is required'), 400
        if not re.match(r'^[A-Za-z0-9_\-]+$', name):
            return jsonify(success=False,
                           error='name must be alphanumeric, dash, or underscore'), 400
        if mode not in ('mysql+pymysql',):
            return jsonify(success=False, error='Unsupported DATABASE_MODE'), 400
        if not host:
            return jsonify(success=False, error='DATABASE_HOST is required'), 400
        if not port.isdigit():
            return jsonify(success=False, error='DATABASE_PORT must be numeric'), 400

        defs = self._load_local_db_definitions()
        defs[name] = {
            'DATABASE_MODE': mode,
            'DATABASE_HOST': host,
            'DATABASE_PORT': port,
            'DATABASE_USERNAME': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
            'notes': notes,
        }
        self._save_local_db_definitions(defs)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_database_setup_local_db_delete(self):
        """Delete one reusable local database definition."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        name = str(body.get('name', '') or '').strip()
        if not name:
            return jsonify(success=False, error='name is required'), 400

        defs = self._load_local_db_definitions()
        if name not in defs:
            return jsonify(success=False, error='Local database definition not found'), 404

        del defs[name]
        self._save_local_db_definitions(defs)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_database_setup_local_db_test(self):
        """Test one local database definition with supplied credentials."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        body = request.get_json(silent=True) or {}
        mode = str(body.get('DATABASE_MODE', '') or '').strip() or 'mysql+pymysql'
        host = str(body.get('DATABASE_HOST', '') or '').strip()
        port = str(body.get('DATABASE_PORT', '') or '').strip() or '3306'
        username = str(body.get('DATABASE_USERNAME', '') or '').strip()
        password = str(body.get('DATABASE_PASSWORD', '') or '')
        db_name = str(body.get('DATABASE_NAME', '') or '').strip()

        if mode not in ('mysql+pymysql',):
            return jsonify(success=False, error='Unsupported DATABASE_MODE'), 400
        if not host:
            return jsonify(success=False, error='DATABASE_HOST is required'), 400
        if not port.isdigit():
            return jsonify(success=False, error='DATABASE_PORT must be numeric'), 400
        if not username or not db_name:
            return jsonify(success=False, error='DATABASE_USERNAME and DATABASE_NAME are required'), 400

        result = validate_database_connection(
            mode,
            host,
            username,
            password,
            db_name,
            port=port,
            use_ssh_tunnel=False,
            ssh_config_host='',
            ssh_local_port='',
            ssh_remote_port='',
            local_data_dir=str(self._resolve_local_data_dir()),
        )
        return jsonify(success=True, **result)

    def _api_apero_profiles_test_tables(self):
        """Test table names and fetch available fibers / DPRTYPE options."""
        user_info, perms = self._require_apero_profile_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        table_keys = [
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
        ]

        resolved = self._resolve_db_payload_for_test(data)
        if not resolved.get('ok') and resolved.get('requires_tunnel_admin'):
            return jsonify(
                success=True,
                valid=False,
                requires_tunnel_admin=True,
                error=resolved.get('error', 'DB tunnel required.'),
                tunnel_admin_url=resolved.get('tunnel_admin_url', ''),
            )
        if not resolved.get('ok'):
            return jsonify(success=False, error=resolved.get('error', 'Invalid database payload')), 400

        tables = {}
        for key in table_keys:
            val = str(data.get(key, '')).strip()
            if not val:
                return jsonify(success=False,
                               error=f'{key} is required'), 400
            if not re.match(r'^[A-Za-z0-9_\.]+$', val):
                return jsonify(success=False,
                               error=f'Invalid table name: {key}'), 400
            tables[key] = val

        def qtable(name):
            # Quote db/table identifiers defensively while preserving schema.table
            return '.'.join(f'`{part}`' for part in name.split('.'))

        db_params = {
            'DATABASE_MODE': resolved['mode'],
            'DATABASE_HOST': resolved['host'],
            'DATABASE_PORT': resolved['port'],
            'DATABASE_USER': resolved['username'],
            'DATABASE_PASSWORD': resolved['password'],
            'DATABASE_NAME': resolved['db_name'],
            'DATABASE_USE_SSH_TUNNEL': resolved['use_ssh_tunnel'],
            'DATABASE_SSH_CONFIG_HOST': resolved['ssh_config_host'],
            'DATABASE_SSH_LOCAL_PORT': resolved['ssh_local_port'],
            'DATABASE_SSH_REMOTE_PORT': resolved['ssh_remote_port'],
            'LOCAL_DATA_DIR': str(self._resolve_local_data_dir()),
        }

        try:
            # Check each required table is queryable
            for key in table_keys:
                query = f'SELECT 1 AS ok FROM {qtable(tables[key])} LIMIT 1'
                apero_async.database_query(db_params, query)

            # Populate science options from FINDEX
            findex = qtable(tables['FINDEX_TABLENAME'])
            # Fetch unique science options only; avoid ORDER BY and TRIM in SQL
            # to keep this lightweight on large FINDEX tables.
            fiber_rows = apero_async.database_query(
                db_params,
                f"""
                SELECT KW_FIBER AS value
                FROM {findex}
                WHERE KW_FIBER IS NOT NULL
                    AND KW_FIBER <> ''
                GROUP BY KW_FIBER
                """,
            )
            dpr_rows = apero_async.database_query(
                db_params,
                f"""
                SELECT KW_DPRTYPE AS value
                FROM {findex}
                WHERE KW_DPRTYPE IS NOT NULL
                    AND KW_DPRTYPE <> ''
                GROUP BY KW_DPRTYPE
                """,
            )

            fibers = sorted({
                str(r.get('value')).strip() for r in fiber_rows
                if str(r.get('value', '')).strip()
            })
            dprtypes = sorted({
                str(r.get('value')).strip() for r in dpr_rows
                if str(r.get('value', '')).strip()
            })

            return jsonify(success=True,
                           valid=True,
                           fibers=fibers,
                           dprtypes=dprtypes)
        except Exception as exc:
            return jsonify(success=True,
                           valid=False,
                           error=str(exc),
                           fibers=[],
                           dprtypes=[])

    # -----------------------------------------------------------------
    # Async tasks API
    # -----------------------------------------------------------------
    def _require_async_tasks_perm(self):
        """Check manage.apero_profile permission for async task management."""
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'manage.apero_profile' not in perms:
            return None, None
        return user_info, perms

    @staticmethod
    def _coerce_task_frequency(value, default: float = 24.0) -> float:
        """Normalize a task frequency value in hours."""
        try:
            freq = float(value)
            if freq > 0:
                return freq
        except (TypeError, ValueError):
            pass
        return float(default)

    @staticmethod
    def _coerce_task_enabled(value, default: bool = False) -> bool:
        """Normalize a task enabled flag."""
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        if isinstance(value, str):
            sval = value.strip().lower()
            if sval in ['true', '1', 'yes', 'on']:
                return True
            if sval in ['false', '0', 'no', 'off', '']:
                return False
        return bool(value)

    @staticmethod
    def _is_global_scope(instrument: str) -> bool:
        """Return True if this task scope is the shared global scope."""
        return str(instrument).strip() == '__GLOBAL__'

    def _task_keys_for_scope(self, instrument: str) -> list:
        """Return task keys allowed in a given scope from tasks.TYPE."""
        from apero_ri import tasks as task_module

        want_type = ('GLOBAL'
                    if self._is_global_scope(instrument)
                    else 'INSTRUMENT')
        keys = []
        for task_key in task_module.TASK_LIST.keys():
            ttype = str(
                task_module.TYPE.get(task_key, 'INSTRUMENT')).strip().upper()
            if ttype == want_type:
                keys.append(task_key)
        return keys

    def _merge_async_task_catalog(self, instrument: str, all_tasks: dict):
        """Merge persisted task overrides with the task catalog defaults."""
        from apero_ri import tasks as task_module
        import_errors = getattr(task_module, 'IMPORT_ERRORS', {}) or {}

        stored_tasks = all_tasks.get(instrument, [])
        if not isinstance(stored_tasks, list):
            stored_tasks = []

        by_key = {}
        for task_cfg in stored_tasks:
            if not isinstance(task_cfg, dict):
                continue
            key = str(task_cfg.get('task_key', '')).strip()
            if key and key not in by_key:
                by_key[key] = task_cfg

        merged = []
        task_keys = self._task_keys_for_scope(instrument)
        for idx, task_key in enumerate(task_keys, start=1):
            task_cfg = dict(by_key.get(task_key, {}))
            task_id = str(task_cfg.get('id', '')).strip()
            if not task_id:
                task_id = str(uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f'ari-async-task:{instrument}:{task_key}'
                ))

            default_freq = self._coerce_task_frequency(
                task_module.FREQ.get(task_key, 24.0), 24.0
            )
            default_enabled = self._coerce_task_enabled(
                task_module.ENABLED.get(task_key, False), False
            )

            merged_cfg = {
                'id': task_id,
                'task_key': task_key,
                'frequency': self._coerce_task_frequency(
                    task_cfg.get('frequency', default_freq), default_freq
                ),
                'active': self._coerce_task_enabled(
                    task_cfg.get('active', default_enabled), default_enabled
                ),
                'order': idx,
            }

            if task_key == 'ARI_LOCAL_DATA_BACKUP':
                try:
                    daily_copies = int(task_cfg.get('daily_copies', 7) or 0)
                except (TypeError, ValueError):
                    daily_copies = 7
                try:
                    weekly_copies = int(task_cfg.get('weekly_copies', 4) or 0)
                except (TypeError, ValueError):
                    weekly_copies = 4
                merged_cfg['daily_copies'] = max(0, daily_copies)
                merged_cfg['weekly_copies'] = max(0, weekly_copies)

            if bool(task_module.MULTI_PROCESS.get(task_key, False)):
                try:
                    ncores = int(task_cfg.get('ncores', 1) or 1)
                except (TypeError, ValueError):
                    ncores = 1
                merged_cfg['ncores'] = max(1, ncores)
                backend = str(task_cfg.get('mp_backend', 'threads')
                              or 'threads').strip().lower()
                start_method = str(task_cfg.get('mp_start_method', 'default')
                                   or 'default').strip().lower()
                merged_cfg['mp_backend'] = (
                    backend if backend in ['threads', 'processes']
                    else 'threads'
                )
                merged_cfg['mp_start_method'] = (
                    start_method if start_method in
                    ['default', 'spawn', 'fork', 'forkserver']
                    else 'default'
                )
            else:
                # Preserve previously saved multiprocessing fields even when
                # task metadata is temporarily unavailable (e.g. import error).
                if any(k in task_cfg for k in
                       ['ncores', 'mp_backend', 'mp_start_method']):
                    try:
                        ncores = int(task_cfg.get('ncores', 1) or 1)
                    except (TypeError, ValueError):
                        ncores = 1
                    merged_cfg['ncores'] = max(1, ncores)
                    backend = str(task_cfg.get('mp_backend', 'threads')
                                  or 'threads').strip().lower()
                    start_method = str(
                        task_cfg.get('mp_start_method', 'default')
                        or 'default'
                    ).strip().lower()
                    merged_cfg['mp_backend'] = (
                        backend if backend in ['threads', 'processes']
                        else 'threads'
                    )
                    merged_cfg['mp_start_method'] = (
                        start_method if start_method in
                        ['default', 'spawn', 'fork', 'forkserver']
                        else 'default'
                    )

            if bool(task_module.LOCAL_TASK.get(task_key, False)):
                merged_cfg['sync_source'] = str(
                    task_cfg.get('sync_source', '') or ''
                ).strip()
            else:
                merged_cfg.pop('sync_source', None)

            for field in ['last_run', 'run_count', 'output_files',
                          'last_status', 'cooldown_until']:
                if field in task_cfg:
                    merged_cfg[field] = task_cfg.get(field)

            import_error = str(import_errors.get(task_key, '')).strip()
            if import_error:
                merged_cfg['last_status'] = 'failed'

            merged.append(merged_cfg)

        original = all_tasks.get(instrument, [])
        changed = original != merged
        all_tasks[instrument] = merged
        return merged, changed

    def _api_async_tasks_list(self):
        """List async task configs for an instrument, merged with runtime state."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='No instrument'), 400

        from apero_ri import tasks as task_module
        all_tasks = load_async_tasks()
        inst_tasks, changed = self._merge_async_task_catalog(
            instrument, all_tasks)
        if changed:
            save_async_tasks(all_tasks)

        result = []
        import_errors = getattr(task_module, 'IMPORT_ERRORS', {}) or {}
        for tc in inst_tasks:
            entry = dict(tc)
            tid = tc.get('id', '')
            rt = task_runner.get_task_status(tid) if tid else {'found': False}
            if not rt.get('found'):
                persisted = task_runner.get_persisted_task_info_error(tid)
                import_error = str(import_errors.get(tc.get('task_key', ''), '')).strip()
                info_text = persisted.get('info', '') or str(tc.get('info', '') or '')
                err_text = persisted.get('error', '') or str(tc.get('error', '') or '')
                if import_error:
                    err_text = import_error
                    if not info_text:
                        info_text = (
                            '## Task Import Error\n\n'
                            f'**Task key**: `{tc.get("task_key", "")}`\n\n'
                            f'```\n{import_error}\n```\n'
                        )
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'subprogress': 0,
                    'use_subprocess': bool(task_module.USE_SUBPROCESS.get(
                        tc.get('task_key', ''), False)),
                    'info': info_text,
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': err_text,
                    'run_count': tc.get('run_count', 0),
                }
            entry['runtime'] = rt
            task_key = entry.get('task_key', '')
            entry['task_type'] = task_module.TYPE.get(task_key, 'INSTRUMENT')
            entry['local_task'] = bool(task_module.LOCAL_TASK.get(task_key, False))
            result.append(entry)

        queue_status = task_runner.get_status()
        return jsonify(success=True, tasks=result, queue=queue_status)

    def _api_async_tasks_global_list(self):
        """Load global tasks from the task registry defaults and overrides."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        from apero_ri import tasks as task_module
        import_errors = getattr(task_module, 'IMPORT_ERRORS', {}) or {}
        all_tasks = load_async_tasks()
        global_scope = '__GLOBAL__'
        global_tasks, changed = self._merge_async_task_catalog(
            global_scope, all_tasks)
        if changed:
            save_async_tasks(all_tasks)

        result = []
        for tc in global_tasks:
            entry = dict(tc)
            tid = tc.get('id', '')
            rt = task_runner.get_task_status(tid) if tid else {'found': False}
            if not rt.get('found'):
                persisted = task_runner.get_persisted_task_info_error(tid)
                import_error = str(import_errors.get(tc.get('task_key', ''), '')).strip()
                info_text = persisted.get('info', '') or str(tc.get('info', '') or '')
                err_text = persisted.get('error', '') or str(tc.get('error', '') or '')
                if import_error:
                    err_text = import_error
                    if not info_text:
                        info_text = (
                            '## Task Import Error\n\n'
                            f'**Task key**: `{tc.get("task_key", "")}`\n\n'
                            f'```\n{import_error}\n```\n'
                        )
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'subprogress': 0,
                    'use_subprocess': bool(task_module.USE_SUBPROCESS.get(
                        tc.get('task_key', ''), False)),
                    'info': info_text,
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': err_text,
                    'run_count': tc.get('run_count', 0),
                }
            entry['runtime'] = rt
            entry['task_type'] = 'GLOBAL'
            entry['instrument'] = global_scope
            task_key = entry.get('task_key', '')
            entry['local_task'] = bool(task_module.LOCAL_TASK.get(task_key, False))
            result.append(entry)

        queue_status = task_runner.get_status()
        return jsonify(success=True, tasks=result, queue=queue_status)

    def _api_async_tasks_task_list(self):
        """Return available task classes from apero_ri.tasks.TASK_LIST."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        try:
            from apero_ri import tasks as task_module
        except Exception:
            return jsonify(success=False,
                           error=f'Failed to import task catalog:\n{traceback.format_exc()}'), 200
        opts = []
        max_cores = max(int(os.cpu_count() or 1), 1)
        for key, cls in task_module.TASK_LIST.items():
            try:
                inst = cls()
                task_type = task_module.TYPE.get(key, 'INSTRUMENT')
                name = inst.name
                description = inst.description
            except Exception:
                task_type = task_module.TYPE.get(key, 'INSTRUMENT')
                name = f'{key} (Init Error)'
                description = traceback.format_exc()
            opts.append({
                'key': key,
                'name': name,
                'description': description,
                'type': task_type,
                'local_task': bool(task_module.LOCAL_TASK.get(key, False)),
                'multi_process': bool(
                    task_module.MULTI_PROCESS.get(key, False)
                ),
            })
        return jsonify(
            success=True,
            tasks=opts,
            multiprocessing={
                'max_cores': max_cores,
                'recommended_max_cores': max(max_cores - 1, 1),
                'backends': ['threads', 'processes'],
                'start_methods': ['default', 'spawn', 'fork', 'forkserver'],
            },
        )

    def _api_async_tasks_save(self):
        """Update an async task configuration from the fixed task catalog."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        task_key = data.get('task_key', '').strip()
        frequency = float(data.get('frequency', 24))
        task_id = str(data.get('id', '')).strip()
        active = bool(data.get('active', True))
        daily_copies = int(data.get('daily_copies', 0) or 0)
        weekly_copies = int(data.get('weekly_copies', 0) or 0)
        has_ncores = 'ncores' in data
        has_mp_backend = 'mp_backend' in data
        has_mp_start_method = (
            'mp_start_method' in data or 'mp_start_methd' in data
        )
        has_sync_source = 'sync_source' in data

        ncores = None
        mp_backend = None
        mp_start_method = None
        sync_source = None

        if not instrument or not task_id:
            return jsonify(success=False, error='Missing fields'), 400
        if frequency <= 0:
            return jsonify(success=False, error='Frequency must be > 0'), 400
        if daily_copies < 0 or weekly_copies < 0:
            return jsonify(success=False,
                           error='Backup copy counts must be non-negative'), 400
        if has_ncores:
            try:
                ncores = int(data.get('ncores'))
            except (TypeError, ValueError):
                return jsonify(success=False,
                               error='NCORES must be an integer'), 400
            if ncores <= 0:
                return jsonify(success=False, error='NCORES must be >= 1'), 400

        if has_mp_backend:
            mp_backend = str(data.get('mp_backend', '') or '').strip().lower()
            if mp_backend not in ['threads', 'processes']:
                return jsonify(success=False,
                               error='mp_backend must be threads or processes'), 400

        if has_mp_start_method:
            mp_start_method_raw = data.get(
                'mp_start_method', data.get('mp_start_methd', '')
            )
            mp_start_method = str(
                mp_start_method_raw or ''
            ).strip().lower()
            if mp_start_method not in ['default', 'spawn', 'fork', 'forkserver']:
                return jsonify(success=False,
                               error='Invalid mp_start_method'), 400

        if has_sync_source:
            sync_source = str(data.get('sync_source', '') or '').strip()

        all_tasks = load_async_tasks()
        inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)
        from apero_ri import tasks as task_module
        max_cores = max(int(os.cpu_count() or 1), 1)
        recommended_max_cores = max(max_cores - 1, 1)
        warnings = []

        found = False
        for t in inst_tasks:
            if t.get('id') != task_id:
                continue

            task_key = t.get('task_key', '')
            if (task_key == 'ARI_LOCAL_DATA_BACKUP'
                    and daily_copies + weekly_copies <= 0):
                return jsonify(success=False,
                               error='Backup task needs at least one retained daily or weekly copy'), 400

            t['frequency'] = frequency
            t['active'] = active
            if task_key == 'ARI_LOCAL_DATA_BACKUP':
                t['daily_copies'] = daily_copies
                t['weekly_copies'] = weekly_copies

            supports_mp = bool(task_module.MULTI_PROCESS.get(task_key, False))
            supports_local_task = bool(task_module.LOCAL_TASK.get(task_key, False))
            if (sync_source is not None and sync_source
                    and not supports_local_task):
                return jsonify(
                    success=False,
                    error='sync_source is only supported for LOCAL_TASK tasks'
                ), 400
            preserve_mp = (
                supports_mp
                or any(k in data for k in
                       ['ncores', 'mp_backend', 'mp_start_method',
                        'mp_start_methd'])
                or any(k in t for k in
                       ['ncores', 'mp_backend', 'mp_start_method'])
            )
            if preserve_mp:
                existing_ncores = t.get('ncores', 1)
                existing_backend = t.get('mp_backend', 'threads')
                existing_start_method = t.get('mp_start_method', 'default')

                try:
                    resolved_ncores = int(
                        ncores if ncores is not None else existing_ncores
                    )
                except (TypeError, ValueError):
                    resolved_ncores = 1
                resolved_ncores = max(1, resolved_ncores)

                resolved_backend = str(
                    mp_backend if mp_backend is not None else existing_backend
                ).strip().lower()
                if resolved_backend not in ['threads', 'processes']:
                    resolved_backend = 'threads'

                resolved_start_method = str(
                    mp_start_method
                    if mp_start_method is not None
                    else existing_start_method
                ).strip().lower()
                if resolved_start_method not in [
                    'default', 'spawn', 'fork', 'forkserver'
                ]:
                    resolved_start_method = 'default'

                t['ncores'] = resolved_ncores
                t['mp_backend'] = resolved_backend
                t['mp_start_method'] = resolved_start_method
                if resolved_ncores > recommended_max_cores:
                    warnings.append(
                        f'NCORES={resolved_ncores} is above recommended max '
                        f'({recommended_max_cores}) for this server.'
                    )
            else:
                t.pop('ncores', None)
                t.pop('mp_backend', None)
                t.pop('mp_start_method', None)

            if supports_local_task:
                if sync_source is not None:
                    t['sync_source'] = sync_source
                else:
                    t.setdefault('sync_source', str(t.get('sync_source', '') or ''))
            else:
                t.pop('sync_source', None)
            found = True
            break

        if not found:
            return jsonify(success=False, error='Task not found'), 404

        all_tasks[instrument] = inst_tasks
        save_async_tasks(all_tasks)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, id=task_id, warnings=warnings)

    def _api_async_tasks_delete(self):
        """Delete an async task configuration."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        task_id = data.get('id', '').strip()
        if not instrument or not task_id:
            return jsonify(success=False, error='Missing fields'), 400

        all_tasks = load_async_tasks()
        inst_tasks = all_tasks.get(instrument, [])
        new_tasks = [t for t in inst_tasks if t.get('id') != task_id]
        if len(new_tasks) == len(inst_tasks):
            return jsonify(success=False, error='Task not found'), 404

        all_tasks[instrument] = new_tasks
        save_async_tasks(all_tasks)
        task_runner.clear_instance(task_id)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_async_tasks_reorder(self):
        """Update task order after a drag-reorder."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        order_list = data.get('order', [])
        if not instrument:
            return jsonify(success=False, error='Missing instrument'), 400

        all_tasks = load_async_tasks()
        inst_tasks = all_tasks.get(instrument, [])
        task_map = {t.get('id'): t for t in inst_tasks}
        ordered_ids = set(order_list)

        reordered = []
        for idx, tid in enumerate(order_list, start=1):
            if tid in task_map:
                task_map[tid]['order'] = idx
                reordered.append(task_map[tid])
        # Append tasks not mentioned in order_list
        for t in inst_tasks:
            if t.get('id') not in ordered_ids:
                reordered.append(t)

        all_tasks[instrument] = reordered
        save_async_tasks(all_tasks)
        return jsonify(success=True)

    def _api_async_tasks_toggle(self):
        """Toggle a task's active/inactive state."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        task_id = data.get('id', '').strip()
        if not instrument or not task_id:
            return jsonify(success=False, error='Missing fields'), 400

        all_tasks = load_async_tasks()
        inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)
        for t in inst_tasks:
            if t.get('id') == task_id:
                t['active'] = not t.get('active', True)
                all_tasks[instrument] = inst_tasks
                save_async_tasks(all_tasks)
                self._refresh_admin_health_after_change(user_info, perms)
                return jsonify(success=True, active=t['active'])

        return jsonify(success=False, error='Task not found'), 404

    def _api_async_tasks_run_now(self):
        """Enqueue a single task to run immediately (prepend to queue)."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        task_id = data.get('id', '').strip()
        force_run = bool(data.get('force_run', False))
        local_data_dir = (data.get('local_data_dir', '') or
                          str(Path.home() / '.ari'))
        if not instrument or not task_id:
            return jsonify(success=False, error='Missing fields'), 400

        all_tasks = load_async_tasks()
        inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)
        task_cfg = next(
            (t for t in inst_tasks
             if t.get('id') == task_id),
            None
        )
        if not task_cfg:
            return jsonify(success=False, error='Task not found'), 404

        allowed, reason = task_runner.can_enqueue_now(task_cfg)
        if not allowed:
            return jsonify(success=False, error=reason), 409

        from apero_ri import tasks as task_module
        task_key = task_cfg.get('task_key', '')
        task_cls = task_module.TASK_LIST.get(task_key)
        if not task_cls:
            return jsonify(success=False, error='Unknown task class'), 400

        all_profiles = load_apero_profiles()
        run_task_cfg = dict(task_cfg)
        if force_run:
            run_task_cfg['force_run'] = True
        run_params = task_runner.build_run_params(
            instrument, local_data_dir, all_profiles, run_task_cfg
        )
        try:
            instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
            instance.USE_SUBPROCESS = bool(
                task_module.USE_SUBPROCESS.get(task_key, False)
            )
            instance._task_key = task_key
        except Exception:
            task_cfg['last_status'] = 'failed'
            task_cfg['error'] = traceback.format_exc()
            all_tasks[instrument] = inst_tasks
            save_async_tasks(all_tasks)
            return jsonify(success=False, error='Task initialization failed; see task error panel.'), 500
        task_runner.enqueue(
            instrument, task_id, instance, run_params, prepend=True
        )
        return jsonify(success=True)

    def _api_async_tasks_run_all(self):
        """Enqueue all active tasks for an instrument.

        ``action`` may be ``'add'`` (append to existing queue) or
        ``'replace'`` (clear queue first).
        """
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        data = request.get_json()
        if not data:
            return jsonify(success=False, error='Missing data'), 400

        instrument = data.get('instrument', '').strip()
        action = data.get('action', 'add')  # 'add' | 'replace'
        force_run = bool(data.get('force_run', False))
        local_data_dir = (data.get('local_data_dir', '') or
                          str(Path.home() / '.ari'))
        if not instrument:
            return jsonify(success=False, error='Missing instrument'), 400

        if action == 'replace':
            task_runner.stop_and_clear()

        all_tasks = load_async_tasks()
        inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)
        inst_tasks = sorted(
            inst_tasks,
            key=lambda t: t.get('order', 999)
        )

        from apero_ri import tasks as task_module
        all_profiles = load_apero_profiles()

        added = []
        blocked = []
        for task_cfg in inst_tasks:
            if not task_cfg.get('active', True):
                continue
            allowed, reason = task_runner.can_enqueue_now(task_cfg)
            if not allowed:
                blocked.append({'id': task_cfg.get('id', ''),
                               'reason': reason})
                continue
            task_key = task_cfg.get('task_key', '')
            task_cls = task_module.TASK_LIST.get(task_key)
            if not task_cls:
                continue
            tid = task_cfg.get('id', '')
            if not tid:
                continue
            run_task_cfg = dict(task_cfg)
            if force_run:
                run_task_cfg['force_run'] = True

            run_params = task_runner.build_run_params(
                instrument, local_data_dir, all_profiles, run_task_cfg
            )
            try:
                instance = task_runner.hydrate_runtime_state(
                    task_cls(),
                    task_cfg)
                instance.USE_SUBPROCESS = bool(
                    task_module.USE_SUBPROCESS.get(task_key, False)
                )
                instance._task_key = task_key
            except Exception:
                task_cfg['last_status'] = 'failed'
                task_cfg['error'] = traceback.format_exc()
                blocked.append({
                    'id': task_cfg.get('id', ''),
                    'reason': 'Task initialization failed; see task error panel.',
                })
                continue
            task_runner.enqueue(instrument, tid, instance, run_params)
            added.append(tid)

        all_tasks[instrument] = inst_tasks
        save_async_tasks(all_tasks)

        return jsonify(success=True, added=added, blocked=blocked)

    def _api_async_tasks_stop(self):
        """Stop queued tasks and apply cooldown before any next attempt."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        data = request.get_json(silent=True) or {}
        instrument = str(data.get('instrument', '') or '').strip() or None
        result = task_runner.stop_all_with_cooldown(instrument=instrument)
        return jsonify(success=True, **result)

    def _api_async_tasks_cancel_task(self):
        """Cancel a single queued or running task by task_id."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        data = request.get_json(silent=True) or {}
        task_id = str(data.get('task_id', '') or '').strip()
        if not task_id:
            return jsonify(success=False, error='task_id is required'), 400
        result = task_runner.cancel_task(task_id)
        if not result.get('success'):
            return jsonify(**result), 404
        return jsonify(**result)

    def _api_async_tasks_clear_history(self):
        """Clear recent async task history entries."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        result = task_runner.clear_recent_history()
        if result.get('success'):
            return jsonify(
                success=True,
                removed=int(result.get('removed', 0) or 0))
        return jsonify(
            success=False,
            error=result.get('error', 'Failed to clear history')), 500

    def _api_async_tasks_status(self):
        """Poll runtime status for a set of task ids and the full queue."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        ids_param = request.args.get('ids', '').strip()
        task_ids = [i for i in ids_param.split(',') if i.strip()]
        if not task_ids:
            queue_status = task_runner.get_status()
            current_info = queue_status.get('current_info') or {}
            current_id = str(current_info.get('task_id', '')).strip()
            queue_ids = [
                str(item.get('task_id', '')).strip()
                for item in (queue_status.get('queue_info') or [])
                if isinstance(item, dict)
            ]
            task_ids = [tid for tid in [current_id] + queue_ids if tid]

        # Build a map from task_id -> yaml config for fallback after restart
        all_tasks = load_async_tasks()
        task_cfg_map: dict = {}
        for _inst, tc_list in all_tasks.items():
            for tc in tc_list:
                _tid = tc.get('id', '')
                if _tid:
                    task_cfg_map[_tid] = tc

        statuses: dict = {}
        from apero_ri import tasks as task_module
        for tid in task_ids:
            rt = task_runner.get_task_status(tid)
            if not rt.get('found'):
                tc = task_cfg_map.get(tid, {})
                task_key = str(tc.get('task_key', '') or '')
                persisted = task_runner.get_persisted_task_info_error(tid)
                import_error = str(task_module.IMPORT_ERRORS.get(task_key, '') or '').strip()
                info_text = persisted.get('info', '') or str(tc.get('info', '') or '')
                err_text = persisted.get('error', '') or str(tc.get('error', '') or '')
                if import_error:
                    err_text = import_error
                    if not info_text:
                        info_text = (
                            '## Task Import Error\n\n'
                            f'**Task key**: `{task_key}`\n\n'
                            f'```\n{import_error}\n```\n'
                        )
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'subprogress': 0,
                    'use_subprocess': bool(
                        task_module.USE_SUBPROCESS.get(task_key, False)
                    ),
                    'info': info_text,
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': err_text,
                    'run_count': tc.get('run_count', 0),
                    'log_path': '',
                }
            statuses[tid] = rt
        queue_status = task_runner.get_status()
        return jsonify(success=True, statuses=statuses, queue=queue_status)

    def _api_async_tasks_task_log(self):
        """Return current per-task async log content."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        task_id = str(request.args.get('task_id', '') or '').strip()
        if not task_id:
            return jsonify(success=False, error='Missing task_id'), 400

        try:
            lines = int(request.args.get('lines', 400) or 400)
        except (TypeError, ValueError):
            lines = 400
        lines = max(1, min(lines, 2000))

        payload = task_runner.get_task_log(task_id, lines=lines)
        return jsonify(success=True, **payload)

    def _validate_async_task_file_path(self, path: str):
        """Validate and resolve an async task output file path."""
        if not path:
            return None, (jsonify(success=False, error='No path'), 400)
        if not os.path.isabs(path):
            return None, (jsonify(
                success=False, error='Must be an absolute path'), 400)

        resolved = Path(path).resolve()
        try:
            resolved.relative_to(Path.home().resolve())
        except ValueError:
            return None, (jsonify(success=False,
                                  error='Path outside allowed directory'), 403)

        if not resolved.is_file():
            return None, (jsonify(success=False, error='File not found'), 404)
        return resolved, None

    def _api_async_tasks_read_file(self):
        """Return a preview of the first lines of an async task output file."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        path = request.args.get('path', '').strip()
        preview_lines = max(int(request.args.get('lines', 50) or 50), 1)
        resolved, error_response = self._validate_async_task_file_path(path)
        if error_response is not None:
            return error_response
        if resolved is None:
            return jsonify(success=False, error='Invalid path'), 400
        try:
            raw = resolved.read_bytes()
            suffixes = {suffix.lower() for suffix in resolved.suffixes}
            if (suffixes.intersection({'.gz', '.zip', '.fits', '.tar'})
                    or b'\x00' in raw[:4096]):
                return jsonify(success=True,
                               preview='Binary file preview is not available. Use Download instead.',
                               truncated=False,
                               line_count=0,
                               preview_lines=preview_lines,
                               is_binary=True,
                               is_json=False,
                               json_table=None,
                               path=str(resolved))

            text = raw.decode('utf-8', errors='replace')
            all_lines = text.splitlines()
            preview = '\n'.join(all_lines[:preview_lines])

            json_table = None
            if resolved.suffix.lower() == '.json':
                try:
                    parsed = json.loads(text)
                    json_table = self._build_json_preview_table(parsed)
                except Exception:
                    json_table = None

            return jsonify(success=True,
                           preview=preview,
                           truncated=len(all_lines) > preview_lines,
                           line_count=len(all_lines),
                           preview_lines=preview_lines,
                           is_binary=False,
                           is_json=json_table is not None,
                           json_table=json_table,
                           path=str(resolved))
        except Exception as exc:
            return jsonify(success=False, error=str(exc)), 500

    @staticmethod
    def _build_json_preview_table(data, max_rows: int = 200) -> dict:
        """Convert JSON data into a compact table payload for UI rendering."""

        def _cell(value) -> str:
            if value is None:
                return ''
            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False)
            return str(value)

        def _rows_to_table(rows_data: list,
                           columns_hint=None,
                           row_count_hint=None) -> dict:
            columns = []
            seen = set()
            if isinstance(columns_hint, list):
                for col in columns_hint:
                    scol = str(col)
                    if scol not in seen:
                        seen.add(scol)
                        columns.append(scol)
            for item in rows_data:
                if isinstance(item, dict):
                    for key in item.keys():
                        skey = str(key)
                        if skey not in seen:
                            seen.add(skey)
                            columns.append(skey)

            rows = []
            for item in rows_data[:max_rows]:
                if isinstance(item, dict):
                    row = {col: _cell(item.get(col, '')) for col in columns}
                else:
                    row = {'value': _cell(item)}
                rows.append(row)

            row_count = (row_count_hint
                          if isinstance(row_count_hint, int)
                          else len(rows_data))
            if row_count < len(rows_data):
                row_count = len(rows_data)
            return {
                'columns': columns if columns else ['value'],
                'rows': rows,
                'row_count': row_count,
                'truncated': len(rows_data) > max_rows,
            }

        if isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return _rows_to_table(data)

            rows = []
            for index, value in enumerate(data[:max_rows], start=1):
                rows.append({'index': str(index), 'value': _cell(value)})
            return {
                'columns': ['index', 'value'],
                'rows': rows,
                'row_count': len(data),
                'truncated': len(data) > max_rows,
            }

        if isinstance(data, dict):
            rows_payload = data.get('rows')
            if isinstance(rows_payload, list):
                return _rows_to_table(rows_payload,
                                      columns_hint=data.get('columns'),
                                      row_count_hint=data.get('row_count'))

            items = list(data.items())
            rows = []
            for key, value in items[:max_rows]:
                rows.append({'key': str(key), 'value': _cell(value)})
            return {
                'columns': ['key', 'value'],
                'rows': rows,
                'row_count': len(items),
                'truncated': len(items) > max_rows,
            }

        return {
            'columns': ['value'],
            'rows': [{'value': _cell(data)}],
            'row_count': 1,
            'truncated': False,
        }

    def _api_async_tasks_download_file(self):
        """Download an async task output file."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        path = request.args.get('path', '').strip()
        resolved, error_response = self._validate_async_task_file_path(path)
        if error_response is not None:
            return error_response
        if resolved is None:
            return jsonify(success=False, error='Invalid path'), 400

        return send_from_directory(str(resolved.parent),
                                   resolved.name,
                                   as_attachment=True)

    # -----------------------------------------------------------------
    # User links API
    # -----------------------------------------------------------------
    def _api_user_links_get(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        username = user_info['username']
        instrument = request.args.get('instrument', '').strip()
        if instrument == '__all__':
            params = load_parameters()
            all_instr = params.get('instruments', {}).get('value', [])
            user_instr = user_info.get('instruments', [])
            instruments = (
                [i for i in all_instr if i in user_instr]
                or list(all_instr))

            data = ud.load_links(username)
            merged = {
                'sections': list(data.get('sections', [])),
                'types': dict(data.get('types', {})),
                'links': {s: dict(v) for s, v in data.get('links', {}).items()},
                'instrument_sections': [],
            }
            for inst in instruments:
                inst_data = ud.load_instrument_links(inst)
                for section in inst_data.get('sections', []):
                    tag = f'[{inst}] {section}'
                    merged['instrument_sections'].append(tag)
                    merged['links'][tag] = dict(
                        inst_data.get('links', {}).get(section, {}))
            data = merged
        elif instrument:
            data = ud.get_merged_links(username, instrument)
        else:
            data = ud.load_links(username)
        return jsonify(success=True, data=data)

    def _api_user_links_add(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        url = str(body.get('url', '')).strip()
        if not section or not name or not url:
            return jsonify(success=False, error='section, name and url required'), 400
        data = ud.add_link(user_info['username'], section, name, url,
                           str(body.get('type', '')),
                           str(body.get('description', '')))
        return jsonify(success=True, data=data)

    def _api_user_links_update(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        new_name = str(body.get('new_name', name)).strip()
        url = str(body.get('url', '')).strip()
        if not section or not name or not url:
            return jsonify(success=False, error='section, name and url required'), 400
        data = ud.update_link(user_info['username'], section, name, new_name,
                              url, str(body.get('type', '')),
                              str(body.get('description', '')))
        return jsonify(success=True, data=data)

    def _api_user_links_remove(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        if not section or not name:
            return jsonify(success=False, error='section and name required'), 400
        data = ud.remove_link(user_info['username'], section, name)
        return jsonify(success=True, data=data)

    def _api_user_links_add_section(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        section = str(body.get('section', '')).strip()
        if not section:
            return jsonify(success=False, error='section required'), 400
        data = ud.add_link_section(user_info['username'], section)
        return jsonify(success=True, data=data)

    def _api_user_links_remove_section(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        section = str(body.get('section', '')).strip()
        if not section:
            return jsonify(success=False, error='section required'), 400
        data = ud.remove_link_section(user_info['username'], section)
        return jsonify(success=True, data=data)

    # -----------------------------------------------------------------
    # User notes API
    # -----------------------------------------------------------------
    def _api_user_notes_list(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        notes = ud.load_notes(user_info['username'])
        slim = []
        for note in notes:
            entry = {k: v for k, v in note.items() if k != 'content'}
            content = str(note.get('content', ''))
            preview = ' '.join(content.split())[:180]
            entry['content_preview'] = preview
            slim.append(entry)
        return jsonify(success=True, notes=slim)

    def _api_user_notes_get(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        note_id = request.args.get('id', '').strip()
        if not note_id:
            return jsonify(success=False, error='id required'), 400
        note = ud.get_note(user_info['username'], note_id)
        if note is None:
            return jsonify(success=False, error='Not found'), 404
        return jsonify(success=True, note=note)

    def _api_user_notes_save(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        note = {
            'id': str(body.get('id', '')).strip(),
            'title': str(body.get('title', 'Untitled')).strip(),
            'color': str(body.get('color', '#ffd966')).strip(),
            'section': str(body.get('section', '')).strip(),
            'created': str(body.get('created', '')).strip(),
            'content': str(body.get('content', '')),
        }
        saved = ud.save_note(user_info['username'], note)
        return jsonify(success=True, note=saved)

    def _api_user_notes_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        note_id = str(body.get('id', '')).strip()
        if not note_id:
            return jsonify(success=False, error='id required'), 400
        ok = ud.delete_note(user_info['username'], note_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_notes_render(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        content = str(body.get('content', ''))
        html = ud.render_note_html(content)
        return jsonify(success=True, html=html)

    # -----------------------------------------------------------------
    # User preferences API
    # -----------------------------------------------------------------
    def _api_user_prefs_get(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        prefs = ud.load_user_prefs(user_info['username'])
        return jsonify(success=True, prefs=prefs)

    def _api_user_prefs_save(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        updates = {}
        if 'timezone' in body:
            updates['timezone'] = str(body['timezone']).strip() or 'UTC'
        if updates:
            ud.save_user_prefs(user_info['username'], updates)
        prefs = ud.load_user_prefs(user_info['username'])
        return jsonify(success=True, prefs=prefs)

    # -----------------------------------------------------------------
    # User calendar API
    # -----------------------------------------------------------------
    def _api_user_calendar_list(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        instrument = request.args.get('instrument', '').strip()
        if instrument == '__all__':
            params = load_parameters()
            all_instr = params.get('instruments', {}).get('value', [])
            user_instr = user_info.get('instruments', [])
            instruments = (
                [i for i in all_instr if i in user_instr]
                or list(all_instr))

            events = list(ud.list_events(user_info['username']))
            for inst in instruments:
                inst_events = ud.load_instrument_calendar(inst).get(
                    'events', [])
                for ev in inst_events:
                    tagged = dict(ev)
                    tagged['_source'] = inst
                    tagged['category'] = 'instrument'
                    events.append(tagged)
        elif instrument:
            events = ud.get_merged_calendar(user_info['username'], instrument)
        else:
            events = ud.list_events(user_info['username'])
        return jsonify(success=True, events=events)

    def _api_user_calendar_save(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        event = {
            'id': str(body.get('id', '')).strip(),
            'title': str(body.get('title', '')).strip(),
            'date': str(body.get('date', '')).strip(),
            'time': str(body.get('time', '')).strip(),
            'color': str(body.get('color', '#4a90d9')).strip(),
            'category': str(body.get('category', 'personal')).strip(),
            'recurrence': str(body.get('recurrence', 'none')).strip(),
            'status': str(body.get('status', 'confirmed')).strip(),
            'timezone': str(body.get('timezone', 'UTC')).strip(),
        }
        if not event['title'] or not event['date']:
            return jsonify(success=False, error='title and date required'), 400
        saved = ud.save_event(user_info['username'], event)
        return jsonify(success=True, event=saved)

    def _api_user_calendar_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        event_id = str(body.get('id', '')).strip()
        if not event_id:
            return jsonify(success=False, error='id required'), 400
        ok = ud.delete_event(user_info['username'], event_id)
        return jsonify(success=True, deleted=ok)

    # -----------------------------------------------------------------
    # User todo API
    # -----------------------------------------------------------------
    def _api_user_todo_list(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        items = ud.list_todo_items(user_info['username'])
        metadata = ud.get_todo_metadata(user_info['username'])
        return jsonify(success=True, items=items, metadata=metadata)

    def _api_user_todo_save(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        item = {
            'id': str(body.get('id', '')).strip(),
            'title': str(body.get('title', '')).strip(),
            'status': str(body.get('status', '')).strip(),
            'size': str(body.get('size', 'md')).strip(),
            'priority': body.get('priority', 0),
            'date_added': str(body.get('date_added', '')).strip(),
            'created': str(body.get('created', '')).strip(),
            'projects': body.get('projects', []),
            'tags': body.get('tags', []),
            'comments': str(body.get('comments', '') or ''),
            'link_url': str(body.get('link_url', '') or '').strip(),
            'done': bool(body.get('done', False)),
        }
        if not item['title']:
            return jsonify(success=False, error='title required'), 400
        saved = ud.save_todo_item(user_info['username'], item)
        return jsonify(success=True, item=saved)

    def _api_user_todo_toggle(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        item_id = str(body.get('id', '')).strip()
        if not item_id:
            return jsonify(success=False, error='id required'), 400
        item = ud.toggle_todo(user_info['username'], item_id)
        if item is None:
            return jsonify(success=False, error='Not found'), 404
        return jsonify(success=True, item=item)

    def _api_user_todo_delete(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}
        item_id = str(body.get('id', '')).strip()
        if not item_id:
            return jsonify(success=False, error='id required'), 400
        ok = ud.delete_todo_item(user_info['username'], item_id)
        return jsonify(success=True, deleted=ok)

    def _api_user_todo_reorder(self):
        user_info = self._require_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        body = request.get_json() or {}

        if str(body.get('action', '')).strip() == 'metadata':
            kind = str(body.get('kind', '')).strip()
            op = str(body.get('op', '')).strip()
            value = str(body.get('value', '')).strip()
            if kind not in {'projects', 'tags'}:
                return jsonify(success=False, error='kind must be projects or tags'), 400
            if op not in {'add', 'remove'}:
                return jsonify(success=False, error='op must be add or remove'), 400
            metadata = ud.manage_todo_metadata(
                user_info['username'], kind, op, value)
            return jsonify(success=True, metadata=metadata)

        ordered_ids = body.get('ids', [])
        if not isinstance(ordered_ids, list):
            return jsonify(success=False, error='ids must be a list'), 400
        ordered_ids = [str(i) for i in ordered_ids]
        items = ud.reorder_todo_items(user_info['username'], ordered_ids)
        return jsonify(success=True, items=items)

    # -----------------------------------------------------------------
    # Admin calendar API
    # -----------------------------------------------------------------
    def _require_admin_calendar_perm(self):
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin.calendar' not in perms:
            return None, None
        return user_info, perms

    def _api_admin_calendar_list(self):
        user_info, perms = self._require_admin_calendar_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='instrument required'), 400
        events = ud.load_instrument_calendar(instrument).get('events', [])
        return jsonify(success=True, events=events)

    def _api_admin_calendar_save(self):
        user_info, perms = self._require_admin_calendar_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.calendar' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        if not instrument:
            return jsonify(success=False, error='instrument required'), 400
        event = {
            'id': str(body.get('id', '')).strip(),
            'title': str(body.get('title', '')).strip(),
            'date': str(body.get('date', '')).strip(),
            'time': str(body.get('time', '')).strip(),
            'color': str(body.get('color', '#7b5ea7')).strip(),
            'category': 'instrument',
            'recurrence': str(body.get('recurrence', 'none')).strip(),
            'status': str(body.get('status', 'confirmed')).strip(),
            'timezone': str(body.get('timezone', 'UTC')).strip(),
        }
        if not event['title'] or not event['date']:
            return jsonify(success=False, error='title and date required'), 400
        saved = ud.save_instrument_event(instrument, event)
        return jsonify(success=True, event=saved)

    def _api_admin_calendar_delete(self):
        user_info, perms = self._require_admin_calendar_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.calendar' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        event_id = str(body.get('id', '')).strip()
        if not instrument or not event_id:
            return jsonify(success=False, error='instrument and id required'), 400
        ok = ud.delete_instrument_event(instrument, event_id)
        return jsonify(success=True, deleted=ok)

    # -----------------------------------------------------------------
    # Admin links API
    # -----------------------------------------------------------------
    def _require_admin_links_perm(self):
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin.links' not in perms:
            return None, None
        return user_info, perms

    def _api_admin_links_get(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='instrument required'), 400
        data = ud.load_instrument_links(instrument)
        return jsonify(success=True, data=data)

    def _api_admin_links_add(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.links' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        url = str(body.get('url', '')).strip()
        if not instrument or not section or not name or not url:
            return jsonify(success=False,
                           error='instrument, section, name and url required'), 400
        data = ud.add_instrument_link(instrument, section, name, url,
                                      str(body.get('type', '')),
                                      str(body.get('description', '')))
        return jsonify(success=True, data=data)

    def _api_admin_links_update(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.links' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        new_name = str(body.get('new_name', name)).strip()
        url = str(body.get('url', '')).strip()
        if not instrument or not section or not name or not url:
            return jsonify(success=False,
                           error='instrument, section, name and url required'), 400
        data = ud.update_instrument_link(instrument, section, name, new_name,
                                         url, str(body.get('type', '')),
                                         str(body.get('description', '')))
        return jsonify(success=True, data=data)

    def _api_admin_links_remove(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.links' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        section = str(body.get('section', '')).strip()
        name = str(body.get('name', '')).strip()
        if not instrument or not section or not name:
            return jsonify(success=False,
                           error='instrument, section and name required'), 400
        data = ud.remove_instrument_link(instrument, section, name)
        return jsonify(success=True, data=data)

    def _api_admin_links_add_section(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.links' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        section = str(body.get('section', '')).strip()
        if not instrument or not section:
            return jsonify(success=False,
                           error='instrument and section required'), 400
        data = ud.add_instrument_link_section(instrument, section)
        return jsonify(success=True, data=data)

    def _api_admin_links_remove_section(self):
        user_info, perms = self._require_admin_links_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.links' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        instrument = str(body.get('instrument', '')).strip()
        section = str(body.get('section', '')).strip()
        if not instrument or not section:
            return jsonify(success=False,
                           error='instrument and section required'), 400
        data = ud.remove_instrument_link_section(instrument, section)
        return jsonify(success=True, data=data)

    # -----------------------------------------------------------------
    # Admin email API
    # -----------------------------------------------------------------
    def _require_admin_email_perm(self):
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        return user_info, perms

    def _api_admin_email_test(self):
        user_info, perms = self._require_admin_email_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        if 'view.admin' not in (perms or set()):
            return jsonify(ok=False, error='Insufficient permissions'), 403
        cfg = eb.load_email_config()
        provider = cfg.get('provider', 'log')
        if provider == 'log' or not cfg.get('enabled', False):
            return jsonify(ok=True, detail='Log mode — no SMTP connection needed.')
        result = eb.test_email_connection(cfg)
        return jsonify(ok=result['ok'],
                       error=result.get('error', ''), detail='')

    def _api_admin_email_save(self):
        user_info, perms = self._require_admin_email_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.email' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        allowed = {'provider', 'enabled', 'from_address', 'smtp_host',
                   'smtp_port', 'smtp_ssl', 'smtp_tls', 'smtp_user', 'smtp_password'}
        cfg = {k: v for k, v in body.items() if k in allowed}
        if 'smtp_password' not in cfg:
            existing = eb.load_email_config()
            if existing.get('smtp_password_enc'):
                cfg['smtp_password_enc'] = existing['smtp_password_enc']
        eb.save_email_config(cfg)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_admin_email_send_test(self):
        user_info, perms = self._require_admin_email_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.email' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403
        body = request.get_json() or {}
        to = str(body.get('to', '')).strip()
        if not to:
            return jsonify(success=False, error='Recipient address required.'), 400
        err = eb.send_email(
            to,
            'APERO RI — test email',
            'This is a test email from APERO RI.\n\nIf you received this, email delivery is working correctly.'
        )
        if err:
            return jsonify(success=False, error=err)
        return jsonify(success=True)

    # -----------------------------------------------------------------
    # Admin backup API
    # -----------------------------------------------------------------
    def _require_admin_backup_perm(self):
        user_info = get_effective_user(session)
        if not user_info:
            return None, None
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        return user_info, perms

    def _api_admin_backups_test(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        if 'view.admin' not in (perms or set()):
            return jsonify(ok=False, error='Insufficient permissions'), 403

        method_id = str(request.args.get('method_id', '') or '').strip() or None
        result = bb.test_backup_connection(bb.load_backup_config(),
                           method_id=method_id)
        return jsonify(result)

    def _api_admin_backups_oauth_start(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(ok=False, error='Insufficient permissions'), 403

        cfg = bb.load_backup_config()
        client_secret_path = Path(
            str(cfg.get('gdrive_oauth_client_secret_file', '')).strip()
        ).expanduser()
        if not client_secret_path.exists():
            return jsonify(ok=False, error='Google OAuth client secret file is missing. Upload and save it first.'), 400

        try:
            from google_auth_oauthlib.flow import Flow
        except Exception:
            return jsonify(ok=False,
                           error=('Google OAuth dependency missing. '
                                  'Install google-auth-oauthlib.')), 500

        redirect_uri = url_for(
            'api_admin_backups_oauth_callback', _external=True)
        flow = Flow.from_client_secrets_file(
            str(client_secret_path),
            scopes=bb.GDRIVE_OAUTH_SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
        )
        session['ab_google_oauth_state'] = state
        session['ab_google_oauth_code_verifier'] = str(
            flow.code_verifier or '')
        return redirect(auth_url)

    def _api_admin_backups_oauth_callback(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return 'Unauthorized', 401
        if 'manage.admin.backup' not in (perms or set()):
            return 'Insufficient permissions', 403

        cfg = bb.load_backup_config()
        client_secret_path = Path(
            str(cfg.get('gdrive_oauth_client_secret_file', '')).strip()
        ).expanduser()
        if not client_secret_path.exists():
            return 'Google OAuth client secret file not found.', 400

        if request.args.get('error'):
            err = str(request.args.get('error', '')).strip()
            return (
                '<html><body><h3>Google OAuth failed</h3>'
                f'<p>{err}</p><script>setTimeout(function(){{window.close();}}, 1500);</script>'
                '</body></html>'
            )

        expected_state = str(
            session.get('ab_google_oauth_state', '') or '').strip()
        expected_code_verifier = str(
            session.get('ab_google_oauth_code_verifier', '')
            or '').strip()
        got_state = str(request.args.get('state', '') or '').strip()
        if not expected_state or expected_state != got_state:
            return 'Google OAuth state mismatch. Please retry connect.', 400
        if not expected_code_verifier:
            return 'Google OAuth verifier missing in session. Please retry connect.', 400

        try:
            from google_auth_oauthlib.flow import Flow
        except Exception:
            return 'google-auth-oauthlib is not installed.', 500

        redirect_uri = url_for(
            'api_admin_backups_oauth_callback', _external=True)
        flow = Flow.from_client_secrets_file(
            str(client_secret_path),
            scopes=bb.GDRIVE_OAUTH_SCOPES,
            state=expected_state,
            redirect_uri=redirect_uri,
            code_verifier=expected_code_verifier,
        )

        # OAuthlib requires HTTPS unless localhost or explicit insecure
        # override is enabled.
        host_name = (str(request.host or '')
                     .split(':', 1)[0].strip().lower())
        is_local_host = host_name in {'localhost', '127.0.0.1',
                               '::1'}
        allow_insecure = str(
            os.environ.get(
                'ARI_ALLOW_INSECURE_OAUTH', '')
        ).strip().lower() in {'1', 'true', 'yes', 'on'}
        using_https = bool(request.is_secure)

        if (not using_https) and (not is_local_host) and (not allow_insecure):
            return (
                '<html><body><h3>Google OAuth requires HTTPS</h3>'
                '<p>This callback was reached over HTTP. Use an HTTPS URL for APERO RI, '
                'or (for trusted private testing only) set ARI_ALLOW_INSECURE_OAUTH=1 '
                'before starting the server.</p>'
                '<script>setTimeout(function(){window.close();}, 3000);</script>'
                '</body></html>'
            ), 400

        old_insecure = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
        try:
            if (not using_https) and (is_local_host or allow_insecure):
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            flow.fetch_token(authorization_response=request.url)
        except Exception as exc:
            msg = str(exc) or 'OAuth token exchange failed.'
            return (
                '<html><body><h3>Google OAuth failed</h3>'
                f'<p>{msg}</p><script>setTimeout(function(){{window.close();}}, 2500);</script>'
                '</body></html>'
            ), 400
        finally:
            if old_insecure is None:
                os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT', None)
            else:
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = old_insecure

        token_path = bb.save_gdrive_oauth_token(
            cfg,
            json.loads(flow.credentials.to_json()))
        cfg['gdrive_oauth_token_file'] = str(token_path)
        bb.save_backup_config(cfg)
        self._refresh_admin_health_after_change(user_info, perms)
        session.pop('ab_google_oauth_state', None)
        session.pop('ab_google_oauth_code_verifier', None)

        return (
            '<html><body><h3>Google account connected</h3>'
            '<p>You can close this window.</p>'
            '<script>setTimeout(function(){window.close();}, 1200);</script>'
            '</body></html>'
        )

    def _api_admin_backups_test_backup(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(ok=False, error='Insufficient permissions'), 403

        body = request.get_json(silent=True) or {}
        method_id = str(body.get('method_id', '') or '').strip() or None
        result = bb.test_backup_roundtrip(bb.load_backup_config(),
                          method_id=method_id)
        return jsonify(result)

    def _api_admin_backups_save(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        body = request.get_json() or {}
        allowed = {
            'enabled', 'provider',
            'gdrive_oauth_client_secret_file', 'gdrive_oauth_token_file',
            'gdrive_folder_id',
            's3_bucket', 's3_prefix', 's3_region', 's3_endpoint_url',
            's3_access_key_id', 's3_secret_access_key',
            's3_credentials_file',
            'rsync_ssh_target', 'rsync_remote_dir', 'rsync_ssh_key',
            'rsync_port', 'rsync_extra_opts',
            'local_mirror_dir',
            'backup_methods', 'active_method_id',
        }

        existing = bb.load_backup_config()
        cfg = dict(existing)
        for key in allowed:
            if key in body:
                cfg[key] = body.get(key)

        if 'enabled' in body:
            enabled_val = body.get('enabled')
            if isinstance(enabled_val, bool):
                cfg['enabled'] = enabled_val
            else:
                cfg['enabled'] = str(enabled_val).strip().lower() in {
                    '1', 'true', 'yes', 'on'
                }

        if ('s3_secret_access_key' not in body
                and existing.get('s3_secret_access_key_enc')):
            cfg['s3_secret_access_key_enc'] = existing.get(
                's3_secret_access_key_enc', '')

        bb.save_backup_config(cfg)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_admin_backups_upload_json(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        target_field = str(request.form.get('target_field', '')).strip()
        allowed_targets = {'gdrive_oauth_client_secret_file',
                          's3_credentials_file'}
        if target_field not in allowed_targets:
            return jsonify(success=False, error='Invalid target field.'), 400

        if 'file' not in request.files:
            return jsonify(success=False, error='No file provided.'), 400

        uploaded = request.files['file']
        if not uploaded or not uploaded.filename:
            return jsonify(success=False, error='Empty filename.'), 400

        filename = secure_filename(uploaded.filename)
        if not filename.lower().endswith('.json'):
            return jsonify(success=False, error='Only .json files are accepted.'), 400

        payload = uploaded.read()
        if not payload:
            return jsonify(success=False, error='Uploaded file is empty.'), 400
        if len(payload) > 5 * 1024 * 1024:
            return jsonify(success=False, error='JSON file is too large (max 5 MB).'), 400

        try:
            # Ensure uploaded content is valid JSON before storing it.
            json.loads(payload.decode('utf-8'))
        except Exception:
            return jsonify(success=False, error='Uploaded file is not valid UTF-8 JSON.'), 400

        upload_targets = {
            'gdrive_oauth_client_secret_file': 'gdrive_oauth_client_secret.json',
            's3_credentials_file': 's3_credentials.json',
        }
        final_path = ss.get_secret_path(upload_targets[target_field])

        with open(final_path, 'wb') as handle:
            handle.write(payload)

        ss.protect_path(final_path, 0o600)

        return jsonify(success=True,
                       stored_file=final_path.name,
                       stored_path=str(final_path))

    def _api_admin_backups_list(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'view.admin' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        method_id = str(request.args.get('method_id', '') or '').strip() or None
        inventory = bb.backup_inventory(local_data_dir=local_data_dir,
                        cfg=cfg,
                        method_id=method_id)
        return jsonify(success=True, data=inventory)

    def _api_admin_backups_delete(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        body = request.get_json() or {}
        rel = str(body.get('relative_path', '')).strip()
        target = str(body.get('target', 'both')).strip().lower()
        method_id = str(body.get('method_id', '') or '').strip() or None
        if target not in {'local', 'cloud', 'both'}:
            return jsonify(success=False, error='Invalid target'), 400
        if not rel:
            return jsonify(success=False, error='relative_path is required'), 400

        try:
            cfg = bb.load_backup_config()
            local_data_dir = self._resolve_local_data_dir()
            result = bb.delete_backup(rel, target=target,
                                      local_data_dir=local_data_dir,
                                      cfg=cfg,
                                      method_id=method_id)
            self._refresh_admin_health_after_change(user_info, perms)
            return jsonify(success=True, data=result)
        except Exception as exc:
            return jsonify(success=False, error=str(exc)), 400

    def _api_admin_backups_delete_all(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        body = request.get_json() or {}
        period = str(body.get('period', 'all')).strip().lower()
        target = str(body.get('target', 'both')).strip().lower()
        method_id = str(body.get('method_id', '') or '').strip() or None
        if period not in {'daily', 'weekly', 'all'}:
            return jsonify(success=False, error='Invalid period'), 400
        if target not in {'local', 'cloud', 'both'}:
            return jsonify(success=False, error='Invalid target'), 400

        try:
            cfg = bb.load_backup_config()
            local_data_dir = self._resolve_local_data_dir()
            result = bb.delete_all_backups(period=period,
                                           target=target,
                                           local_data_dir=local_data_dir,
                                           cfg=cfg,
                                           method_id=method_id)
            self._refresh_admin_health_after_change(user_info, perms)
            return jsonify(success=True, data=result)
        except Exception as exc:
            return jsonify(success=False, error=str(exc)), 400

    def _api_admin_backups_sync(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        body = request.get_json(silent=True) or {}
        method_id = str(body.get('method_id', '') or '').strip() or None
        result = bb.sync_local_backups_to_cloud(local_data_dir=local_data_dir,
                            cfg=cfg,
                            method_id=method_id)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, data=result)

    def _api_admin_backups_download(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        body = request.get_json() or {}
        relative_path = str(body.get('relative_path', '')).strip()
        method_id = str(body.get('method_id', '') or '').strip() or None
        if not relative_path:
            return jsonify(success=False, error='relative_path is required.'), 400

        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        result = bb.download_cloud_backup(
            relative_path,
            local_data_dir=local_data_dir,
            cfg=cfg,
            method_id=method_id)
        
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=result.get('ok', False), 
                      path=result.get('path'),
                      error=result.get('error'))

    def _api_admin_backups_sync_from_cloud(self):
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        if 'manage.admin.backup' not in (perms or set()):
            return jsonify(success=False, error='Insufficient permissions'), 403

        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        body = request.get_json(silent=True) or {}
        method_id = str(body.get('method_id', '') or '').strip() or None
        result = bb.sync_cloud_backups_to_local(
            local_data_dir=local_data_dir,
            cfg=cfg,
            method_id=method_id)
        
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=result.get('ok', False),
                      downloaded=result.get('downloaded', 0),
                      error=result.get('error'))

    def _api_admin_backups_validate_dir(self):
        try:
            user_info, perms = self._require_admin_backup_perm()
            if not user_info:
                return jsonify(success=False, error='Unauthorized'), 401
            if 'view.admin' not in (perms or set()):
                return jsonify(success=False, error='Insufficient permissions'), 403

            path = str(request.args.get('path', '') or '').strip()
            if not path:
                return jsonify(success=False, error='No path provided'), 400
            if not os.path.isabs(path):
                return jsonify(success=False, error='Path must be absolute'), 400

            target = Path(path).expanduser()
            if not target.exists():
                return jsonify(success=True, ok=False,
                               path=str(target),
                               message='Directory does not exist')
            if not target.is_dir():
                return jsonify(success=True, ok=False,
                               path=str(target),
                               message='Path is not a directory')
            try:
                _ = any(target.iterdir())
            except PermissionError:
                return jsonify(success=True, ok=False,
                               path=str(target),
                               message='Permission denied for this directory')
            return jsonify(success=True, ok=True,
                           path=str(target), message='Directory is valid')
        except Exception as exc:
            return jsonify(success=False,
                           error=f'Validate directory failed: {exc}'), 500

    def _api_admin_backups_browse(self):
        try:
            user_info, perms = self._require_admin_backup_perm()
            if not user_info:
                return jsonify(success=False, error='Unauthorized'), 401
            if 'view.admin' not in (perms or set()):
                return jsonify(success=False, error='Insufficient permissions'), 403

            path = str(request.args.get('path', '/') or '/').strip()
            if not os.path.isabs(path):
                return jsonify(success=False, error='Path must be absolute'), 400

            target = Path(path).expanduser()
            if not target.is_dir():
                return jsonify(success=False, error='Not a directory'), 400

            dirs = []
            try:
                for entry in sorted(target.iterdir()):
                    try:
                        is_dir = entry.is_dir()
                    except PermissionError:
                        continue
                    if is_dir and not entry.name.startswith('.'):
                        dirs.append(entry.name)
            except PermissionError:
                return jsonify(success=False, error='Permission denied'), 403

            parent = str(target.parent) if str(target) != '/' else '/'
            return jsonify(success=True,
                           path=str(target),
                           parent=parent,
                           dirs=dirs)
        except Exception as exc:
            return jsonify(success=False,
                           error=f'Browse failed: {exc}'), 500

    # -----------------------------------------------------------------
    # SSHFS Management API handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_keys_list(self):
        """List available SSH keys."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.list_ssh_keys()
        return jsonify(**result)

    def _api_admin_sshfs_keys_add(self):
        """Add a new SSH key."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        data = request.get_json() or {}
        key_name = data.get('key_name', '').strip()
        key_content = data.get('key_content', '').strip()
        
        result = sb.add_ssh_key(key_name, key_content)
        return jsonify(**result)

    def _api_admin_sshfs_keys_delete(self, key_name):
        """Delete an SSH key."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.delete_ssh_key(key_name)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_add(self):
        """Add a new SSHFS mount."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        data = request.get_json() or {}
        mount_config = {
            'connection_mode': data.get('connection_mode', 'direct').strip(),
            'ssh_config_host': data.get('ssh_config_host', '').strip(),
            'name': data.get('name', '').strip(),
            'remote_host': data.get('remote_host', '').strip(),
            'remote_path': data.get('remote_path', '').strip(),
            'local_mount': data.get('local_mount', '').strip(),
            'ssh_key': data.get('ssh_key', '').strip(),
            'remote_user': data.get('remote_user', '').strip() or 'root',
            'manual_mode': data.get('manual_mode', False),
        }
        
        result = sb.add_mount(mount_config)
        if result['ok']:
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_test_connection(self):
        """Test SSH authentication/path before saving a mount."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        data = request.get_json() or {}
        result = sb.test_ssh_connection(
            connection_mode=data.get('connection_mode', 'direct'),
            remote_host=data.get('remote_host', ''),
            remote_user=data.get('remote_user', ''),
            ssh_config_host=data.get('ssh_config_host', ''),
            remote_path=data.get('remote_path', ''),
            ssh_key_name=data.get('ssh_key', ''),
        )
        return jsonify(**result)

    def _api_admin_sshfs_mounts_update(self, mount_name):
        """Update an existing SSHFS mount."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        data = request.get_json() or {}
        mount_config = {
            'connection_mode': data.get('connection_mode', 'direct').strip(),
            'ssh_config_host': data.get('ssh_config_host', '').strip(),
            'name': data.get('name', '').strip(),
            'remote_host': data.get('remote_host', '').strip(),
            'remote_path': data.get('remote_path', '').strip(),
            'local_mount': data.get('local_mount', '').strip(),
            'ssh_key': data.get('ssh_key', '').strip(),
            'remote_user': data.get('remote_user', '').strip() or 'root',
            'manual_mode': data.get('manual_mode', False),
        }

        result = sb.update_mount(mount_name, mount_config)
        if result.get('ok'):
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_delete(self, mount_name):
        """Delete an SSHFS mount."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.delete_mount(mount_name)
        if result['ok']:
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_mount(self, mount_name):
        """Mount an SSHFS volume."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.mount_sshfs(mount_name)
        if result['ok']:
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_unmount(self, mount_name):
        """Unmount an SSHFS volume."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.unmount_sshfs(mount_name)
        if result['ok']:
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_unmount_lazy(self, mount_name):
        """Lazy-unmount an SSHFS volume."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        result = sb.lazy_unmount_sshfs(mount_name)
        if result['ok']:
            self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(**result)

    def _api_admin_sshfs_mounts_status(self):
        """Get status of all SSHFS mounts."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        
        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403
        
        result = sb.get_mounts_status()
        return jsonify(**result)

    def _api_admin_sshfs_mounts_log(self, mount_name):
        """Get the last saved log for a mount."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401

        perms = resolve_user_permissions(user_info['groups'], self.ari_groups)
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        result = sb.get_mount_log(mount_name)
        return jsonify(**result)

    # -----------------------------------------------------------------
    # Interactive SSH terminal handlers
    # -----------------------------------------------------------------
    def _api_admin_sshfs_interactive_start_test(self):
        """Start an interactive SSH test session with PTY."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        from apero_ri.core.sshfs_interactive import start_interactive_test

        body = request.get_json(silent=True) or {}
        result = start_interactive_test(
            connection_mode=body.get('connection_mode', 'direct'),
            remote_host=body.get('remote_host', ''),
            remote_user=body.get('remote_user', ''),
            ssh_config_host=body.get('ssh_config_host', ''),
            remote_path=body.get('remote_path', ''),
            ssh_key_name=body.get('ssh_key', ''),
        )
        return jsonify(**result)

    def _api_admin_sshfs_interactive_start_mount(self):
        """Start an interactive SSHFS mount session with PTY."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        from apero_ri.core.sshfs_interactive import start_interactive_mount

        body = request.get_json(silent=True) or {}
        mount_name = str(body.get('mount_name', '')).strip()
        if not mount_name:
            return jsonify(ok=False, error='mount_name required'), 400
        result = start_interactive_mount(mount_name)
        return jsonify(**result)

    def _api_admin_sshfs_interactive_poll(self):
        """Poll output from an interactive SSH/SSHFS session."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        from apero_ri.core.sshfs_interactive import poll_session

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        if not token:
            return jsonify(ok=False, error='token required'), 400
        result = poll_session(token)
        return jsonify(**result)

    def _api_admin_sshfs_interactive_send(self):
        """Send input to an interactive SSH/SSHFS session."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        from apero_ri.core.sshfs_interactive import send_input

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        data = str(body.get('data', ''))
        if not token:
            return jsonify(ok=False, error='token required'), 400
        result = send_input(token, data)
        return jsonify(**result)

    def _api_admin_sshfs_interactive_close(self):
        """Close and clean up an interactive SSH/SSHFS session."""
        user_info = get_effective_user(session)
        if not user_info:
            return jsonify(ok=False, error='Unauthorized'), 401
        perms = resolve_user_permissions(
            user_info['groups'], self.ari_groups
        )
        if 'view.admin' not in perms:
            return jsonify(ok=False, error='Forbidden'), 403

        from apero_ri.core.sshfs_interactive import close_session

        body = request.get_json(silent=True) or {}
        token = str(body.get('token', '')).strip()
        if not token:
            return jsonify(ok=False, error='token required'), 400

        result = close_session(token)

        # If this was a mount session, check if the mount actually
        # succeeded and update the config accordingly.
        mount_name = str(body.get('mount_name', '')).strip()
        if mount_name:
            from apero_ri.core.sshfs_interactive import (
                finalise_interactive_mount,
            )
            # Save the terminal output as the mount log
            terminal_log = str(body.get('terminal_log', '')).strip()
            if terminal_log:
                sb.save_mount_log(
                    mount_name,
                    terminal_log.splitlines(),
                    source='interactive',
                )
            mount_status = sb.check_mount_status(mount_name)
            if mount_status.get('mounted'):
                finalise_interactive_mount(mount_name)
                self._refresh_admin_health_after_change(
                    user_info, perms,
                )
                result['mount_ok'] = True
            else:
                result['mount_ok'] = False

        return jsonify(**result)

    # -----------------------------------------------------------------
    # Run override
    # -----------------------------------------------------------------
    def run(self, host=None, port=None, debug=True, **kwargs):
        """Run the ARI Flask application.

        Uses values from command-line args unless explicitly overridden.
        """
        """Run the ARI Flask application.

        Uses values from command-line args unless explicitly overridden.

        Werkzeug's ``ThreadingMixIn`` uses ``block_on_close=True``, which
        means ``server_close()`` joins every active request-handler thread
        before returning.  If any handler is long-running (SSE poll, slow
        DB/SSHFS call) this blocks indefinitely on Ctrl+C.

        A SIGINT handler is installed that:
        1. Starts a 5-second watchdog daemon thread.
        2. Re-raises ``KeyboardInterrupt`` to unblock ``serve_forever()``.
        3. Watchdog calls ``os._exit(130)`` if the server has not returned
           within 5 seconds, guaranteeing the port is always released.
        """
        import signal
        import sys as _sys

        if host is None:
            host = self._resolve_host(self.args.host)
        if port is None:
            port = self.args.port
        kwargs.setdefault('use_reloader', False)

        if debug:
            print(
                f'[apero_ri] Starting server on {host}:{port}'
                f' (debug={debug}, reloader=off)',
                file=_sys.stderr, flush=True,
            )

        _cleanup_done = threading.Event()

        def _watchdog(timeout_s: float) -> None:
            """Force-exit if clean shutdown takes longer than *timeout_s* s.

            Werkzeug's ThreadingMixIn block_on_close=True can hang
            server_close() waiting for long-running request threads
            (e.g. SSE, slow SSHFS/DB calls).  After the timeout we call
            os._exit() which bypasses atexit but releases the port
            immediately.  Daemon threads (task worker, scheduler) are
            killed by the OS on process exit.
            """
            if not _cleanup_done.wait(timeout_s):
                if debug:
                    print(
                        f'\n[apero_ri] Shutdown watchdog fired after '
                        f'{timeout_s}s — a request-handler thread did not '
                        f'finish in time.  Forcing exit. '
                        f'(Port will be released.)',
                        file=_sys.stderr, flush=True,
                    )
                os._exit(130)

        _watchdog_thread = None
        _original_sigint = signal.getsignal(signal.SIGINT)

        def _sigint_handler(signum, frame):
            nonlocal _watchdog_thread
            # Restore the previous handler so a *second* Ctrl+C forces
            # the original behaviour (usually raising KeyboardInterrupt
            # directly, which unblocks if still stuck).
            signal.signal(signal.SIGINT, _original_sigint)
            if debug:
                print(
                    '\n[apero_ri] Ctrl+C received — shutting down...',
                    file=_sys.stderr, flush=True,
                )
            # Arm watchdog before re-raising so Werkzeug block_on_close
            # cannot hang us beyond the timeout.
            if _watchdog_thread is None:
                _watchdog_thread = threading.Thread(
                    target=_watchdog,
                    args=(5.0,),
                    daemon=True,
                    name='ari-shutdown-watchdog',
                )
                _watchdog_thread.start()
                if debug:
                    print(
                        '[apero_ri] Shutdown watchdog armed (5s timeout).',
                        file=_sys.stderr, flush=True,
                    )
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, _sigint_handler)
        try:
            super().run(host=host, port=port, debug=debug, **kwargs)
        except KeyboardInterrupt:
            pass
        finally:
            signal.signal(signal.SIGINT, _original_sigint)
            if debug:
                print(
                    '[apero_ri] Server stopped — running shutdown hook...',
                    file=_sys.stderr, flush=True,
                )
            self.shutdown()
            # Signal the watchdog that cleanup finished; it will not fire.
            _cleanup_done.set()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
