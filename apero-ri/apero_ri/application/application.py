#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Flask application class.

ARIApp inherits from Flask and wires up all routes, authentication,
and permission handling from groups.yaml / pages.yaml.
"""
import argparse
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
from datetime import timedelta, datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Optional, List

from flask import (Flask, render_template, redirect, url_for,
                   request, session, flash, jsonify,
                   send_from_directory, send_file)

from apero_ri.core.permissions import (
    load_groups, load_pages, load_parameters,
    resolve_user_permissions, get_inherited_groups,
    get_children, is_parent_page, page_id_to_url,
    page_id_to_template, page_id_to_endpoint,
    get_nav_pages, get_visible_cards,
    find_full_nav_root, get_sidebar_tree, get_pinned_sidebar_items,
)
from apero_ri.core.auth import (
    set_ari_dir as auth_set_ari_dir,
    ensure_default_user, authenticate, get_effective_user,
    get_public_permissions, get_user_info,
    hash_password, verify_password,
    search_users, list_all_users, update_user_groups,
    update_user_instruments,
    delete_user, load_users, save_users,
    load_science_groups, save_science_groups, get_users_for_instrument,
    load_apero_profiles, save_apero_profiles,
    load_db_access, save_db_access,
    load_admin_health_config, save_admin_health_config,
    validate_path_exists, validate_database_connection,
    get_accessible_profiles,
    load_async_tasks, save_async_tasks,
)
from apero_ri.core import task_runner
from apero_ri.tasks import apero_async
from apero_ri.core import user_data as ud
from apero_ri.core import email_backend as eb
from apero_ri.core.docs import (
    get_versions, get_default_version, get_doc_content,
    save_doc_content, save_uploaded_image, DOC_IMAGES,
)
from apero_ri.core.object_funcs import build_object_page_stats
from apero_ri.core import basket_funcs as bk

# =============================================================================
# Define variables
# =============================================================================
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
        """Load or create a persistent secret key in ~/.ari."""
        secret_file = Path.home() / '.ari' / 'secret.key'
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        if secret_file.exists():
            return secret_file.read_text().strip()
        key = secrets.token_hex(32)
        secret_file.write_text(key)
        # restrict permissions to owner only
        os.chmod(secret_file, 0o600)
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
        self.add_url_rule('/api/admin/apero-profiles/test-tables',
                  'api_apero_profiles_test_tables',
                  self._api_apero_profiles_test_tables,
                  methods=['POST'])

        # Admin user DB access API routes
        self.add_url_rule('/api/admin/user-db-access/profiles',
              'api_user_db_access_profiles',
              self._api_user_db_access_profiles)
        self.add_url_rule('/api/admin/user-db-access/details',
              'api_user_db_access_details',
              self._api_user_db_access_details)
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
        self.add_url_rule('/data_portal/<profile_id>/object-table',
                          'ri_object_table',
                          self._ri_object_table_view)
        self.add_url_rule('/api/data-portal/object-table',
                          'api_object_table',
                          self._api_object_table)
        self.add_url_rule('/data_portal/<profile_id>/observation-table',
                  'ri_observation_table',
                  self._ri_obs_table_view)
        self.add_url_rule('/data_portal/<profile_id>/query-db',
                  'ri_query_db',
                  self._ri_query_db_view)
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
        self.add_url_rule('/api/data-portal/file-browser',
                          'api_file_browser',
                          self._api_file_browser)

        self.add_url_rule('/data_portal/<profile_id>/<path:objname>',
              'ri_object_page',
              self._ri_object_page_view)
        self.add_url_rule('/api/data-portal/object-page',
                'api_object_page',
                self._api_object_page)
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
                context['instruments'] = all_instr if isinstance(all_instr, list) else []

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

            # Admin index and health-status page: inject health context
            if page_id in {'home.admin_portal', 'home.admin_portal.health_status'}:
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
        """Return sorted list of all unique run_ids from object table JSONs."""
        import json as _json
        from apero_ri.core.auth import ARI_DIR
        tasks_dir = ARI_DIR / 'tasks' / instrument
        run_ids = set()
        if tasks_dir.exists():
            # New layout: tasks/<instrument>/<apero_profile>/object_table.json
            for jf in tasks_dir.glob('*/object_table.json'):
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
            for jf in tasks_dir.glob('object_table_*.json'):
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
                'qc_graphs':    ('', True),
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
                    'label': objname,
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
        accessible_profiles = get_accessible_profiles(user_info, self.ari_groups)
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
                u_instr = [str(val).strip() for val in (u_instr or []) if str(val).strip()]
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
        instruments = [i for i in all_instr if i in user_instr] or list(all_instr)
        links_data = ud.load_links(username)
        instr_links = {
            i: ud.load_instrument_links(i) for i in instruments
        }
        return {
            'links_data': links_data,
            'instr_links': instr_links,
            'instruments': instruments,
        }

    def _build_user_calendar_context(self, user_info):
        """Build context for user calendar page."""
        username = user_info['username']
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = user_info.get('instruments', [])
        instruments = [i for i in all_instr if i in user_instr] or list(all_instr)
        events = ud.list_events(username)
        instr_events = {}
        for i in instruments:
            instr_events[i] = ud.load_instrument_calendar(i).get('events', [])
        return {
            'events': events,
            'instr_events': instr_events,
            'instruments': instruments,
        }

    def _build_admin_instrument_context(self, user_info, perms):
        """Build instruments context for admin calendar/links pages."""
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        user_instr = user_info.get('instruments', [])
        instruments = [i for i in all_instr if i in user_instr] or list(all_instr)
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
    def _format_utc_datetime(dt: Optional[datetime]) -> str:
        """Format UTC datetime for display."""
        if dt is None:
            return 'Never'
        return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _admin_health_cache_key(perms) -> str:
        """Stable key for admin-health cache entries."""
        return '|'.join(sorted(perms))

    def _start_admin_health_refresher(self) -> None:
        """Start background hourly refresh for existing admin-health cache."""
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

    def _refresh_admin_health_after_change(self, user_info=None, perms=None) -> None:
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
                    health['home.admin_portal.users'] = {'status': 'ok', 'message': ''}
            except Exception:
                pass

        # ── Email: error if enabled but connection fails ──────────────────
        if 'view.admin' in perms:
            try:
                email_cfg = eb.load_email_config()
                if not email_cfg.get('enabled', False):
                    health['home.admin_portal.email'] = {
                        'status': 'warning',
                        'message': 'Email delivery is not enabled. Verification codes go to log file.',
                    }
                else:
                    test = eb.test_email_connection(email_cfg)
                    if test['ok']:
                        health['home.admin_portal.email'] = {'status': 'ok', 'message': ''}
                    else:
                        health['home.admin_portal.email'] = {
                            'status': 'error',
                            'message': f'SMTP connection failed: {test["error"]}',
                        }
            except Exception:
                pass

        # ── APERO Profiles: error if any profile has DB/path failures ────
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
                    health['home.admin_portal.apero_profiles'] = {'status': 'ok', 'message': ''}
            except Exception:
                pass

        # ── Async Tasks: error if any active task has failed/errors ─────
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
                            error = str(task_cfg.get('error', '') or '').strip()

                        if status == 'failed' or error:
                            label = str(task_cfg.get('task_key', task_id) or task_id)
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
                    health['home.admin_portal.async_tasks'] = {'status': 'ok', 'message': ''}
            except Exception:
                pass

        # ── Science Groups: warn on assignment/configuration gaps ───────
        if 'manage.sci_group' in perms:
            try:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                user_instr = set((user_info or {}).get('instruments', []))
                instruments = [i for i in all_instr if i in user_instr] or list(all_instr)

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
                        str(rid).strip() for rid in self._get_instrument_run_ids(inst)
                        if str(rid).strip()
                    }
                    total_run_ids |= inst_run_ids

                    groups = load_science_groups(inst)
                    if not isinstance(groups, dict):
                        continue

                    for gname, entry in groups.items():
                        if not isinstance(entry, dict):
                            continue

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
                                assigned_run_ids.add(rid)

                        if not group_users:
                            groups_without_users.append(f'{inst}:{gname}')
                        if not group_run_ids:
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
                    details.extend([f'run_id: {rid}' for rid in unassigned_run_ids])

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

        # ── User DB Access: warn if profile table access is incomplete ──
        if 'manage.admin.user_db_access' in perms:
            try:
                profiles = get_accessible_profiles(user_info, self.ari_groups)
                db_access = load_db_access()
                table_key_map = self._db_access_table_keys()

                checked = 0
                warnings = 0
                for prof in profiles:
                    instrument = str(prof.get('instrument', '')).strip()
                    profile_id = str(prof.get('profile_id', '')).strip()
                    cfg = prof.get('data', {}) if isinstance(prof.get('data'), dict) else {}
                    if not instrument or not profile_id:
                        continue

                    table_names = [
                        label for label, key in table_key_map.items()
                        if str(self._profile_get_db(cfg, key, '')).strip()
                    ]
                    if not table_names:
                        continue

                    checked += 1
                    prof_entry = (((db_access.get(instrument, {})
                                   if isinstance(db_access.get(instrument, {}), dict)
                                   else {}).get(profile_id, {}))
                                  if instrument and profile_id else {})

                    if self._profile_db_access_health(prof_entry, table_names) != 'ok':
                        warnings += 1

                if checked == 0:
                    health['home.admin_portal.user_db_access'] = {
                        'status': 'warning',
                        'message': ('No APERO profiles with configured table names '
                                    'were found for DB-access checks.'),
                    }
                elif warnings:
                    health['home.admin_portal.user_db_access'] = {
                        'status': 'warning',
                        'message': (
                            f'{warnings} of {checked} profile(s) have incomplete '
                            'DB table access rules.'
                        ),
                    }
                else:
                    health['home.admin_portal.user_db_access'] = {
                        'status': 'ok',
                        'message': f'All {checked} profile(s) have complete DB table access rules.',
                    }
            except Exception as exc:
                health['home.admin_portal.user_db_access'] = {
                    'status': 'error',
                    'message': f'User DB access health check failed: {exc}',
                }

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
        }

        rows = []
        for pid in get_children('home.admin_portal', self.ari_pages):
            status_data = health.get(pid)
            if not isinstance(status_data, dict):
                continue
            status = str(status_data.get('status', 'warning')).strip() or 'warning'
            if status not in {'ok', 'warning', 'error'}:
                status = 'warning'
            msg = str(status_data.get('message', '')).strip()
            details = status_data.get('details', [])
            if not isinstance(details, list):
                details = []
            details = [str(item).strip() for item in details if str(item).strip()]

            rules = checks.get(pid, {})
            rule_msg = str(rules.get(status, '')).strip()
            page_def = self.ari_pages.get(pid, {})
            page_label = str(page_def.get('label', pid)).strip()

            rows.append({
                'page_id': pid,
                'label': page_label,
                'url': page_id_to_url(pid),
                'status': status,
                'message': msg or rule_msg,
                'rule_message': rule_msg,
                'details': details,
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

                db = validate_database_connection(
                    self._profile_get_db(cfg, 'DATABASE_MODE', ''),
                    self._profile_get_db(cfg, 'DATABASE_HOST', ''),
                    self._profile_get_db(cfg, 'DATABASE_USERNAME', ''),
                    self._profile_get_db(cfg, 'DATABASE_PASSWORD', ''),
                    self._profile_get_db(cfg, 'DATABASE_NAME', ''),
                )
                if not db.get('valid', False):
                    db_error = str(db.get('error', '') or 'connection failed').strip()
                    reason_parts.append(f'Database error: {db_error}')

                invalid_paths = []
                for key in path_keys:
                    path_val = str(self._profile_get_path(cfg, key, '')).strip()
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
            'qc_graphs':    '',
            'basket':       f'/data_portal/{profile_id}/basket',
        }
        _card_desc_map = {
            'object_table': 'Browse and search astrophysical objects '
                            'in this reduction profile.',
            'obs_table':    'View night-by-night observations '
                            'and their reduction status.',
            'query_db':     'Run custom queries against the '
                            'reduction database tables.',
            'qc_graphs':    'Interactive plots of quality control '
                            'metrics over time.',
            'basket':       'Collect and download files from this '
                            'reduction profile.',
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
        db_result = validate_database_connection(
            self._profile_get_db(cfg, 'DATABASE_MODE', ''),
            self._profile_get_db(cfg, 'DATABASE_HOST', ''),
            self._profile_get_db(cfg, 'DATABASE_USERNAME', ''),
            self._profile_get_db(cfg, 'DATABASE_PASSWORD', ''),
            self._profile_get_db(cfg, 'DATABASE_NAME', ''),
        )

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
                                               or self._get_primary_contact_email(user))
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
                    # Do not reveal account status in UI; keep server-side trace.
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
        Configuration is read from {ARI_DIR}/admin/email.yaml.
        Falls back to log mode (writes to email_log.txt) when unconfigured.
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
        institutions = [str(i).strip() for i in institutions_raw if str(i).strip()]

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
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()

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
        institutions = [str(i).strip() for i in institutions_raw if str(i).strip()]

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
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        err = self._send_verification_email(new_email, code, 'primary-email-change')
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
        legacy_pins = self._normalize_pinned_pages(user.get('pinned_pages', []))

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
        legacy = user.get('object_section', {}) if isinstance(user, dict) else {}
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

    def _save_user_object_section_pins(self, username: str, pins: List[str]) -> None:
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

    def _api_object_table(self):
        """Return object table rows for a profile, filtered by science group."""
        import json as _json
        base_dir = Path(self.args.data_dir or str(Path.home() / '.ari'))

        user_info = get_effective_user(session)
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

        # Build column list (exclude RUN_ID)
        skip = {'RUN_ID', 'run_id', 'ALL_RUN_IDS', 'all_run_ids'}
        columns = [c for c in (all_rows[0].keys() if all_rows else [])
                   if c not in skip and c not in hidden_by_meta]

        column_meta = {
            col: dict(meta)
            for col, meta in raw_column_meta.items()
            if col not in skip and col not in hidden_by_meta and isinstance(meta, dict)
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

        return jsonify(
            success=True,
            rows=clean_rows,
            columns=columns,
            column_meta=column_meta,
            generated_at=generated_at,
            total_rows=len(all_rows),
        )

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

        context = {
            'page_id': page_id,
            'page_label': page_label,
            'page_icon': page_icon,
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'objname': objname,
            'api_url': '/api/data-portal/object-page',
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

        user_info = get_effective_user(session)
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

    # -----------------------------------------------------------------
    # Download basket helpers
    # -----------------------------------------------------------------

    def _basket_access_check(self):
        """
        Shared access-check helper for all basket routes.
        Returns (user_info, None) on success, (None, error_response) on failure.
        """
        user_info = get_effective_user(session)
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
        summary = bk.basket_summary(username, profile_cfgs, accessible_run_ids)

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
        accessible_run_ids = self._all_accessible_run_ids(user_info)
        profile_cfgs = self._build_profile_cfgs(user_info)
        bk.cleanup_expired_downloads(username)
        summary = bk.basket_summary(username, profile_cfgs, accessible_run_ids)
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
        path = bk.get_job_chunk_path(username, job_id, chunk_idx)
        if path is None:
            return jsonify(success=False, error='File not found or not ready'), 404

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
                       quota_reached=(usage.get('total_bytes', 0) >= limit_bytes))

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
                           error=result.get('error', 'Could not remove job')), 400
        usage = bk.get_downloads_usage(username)
        limit_bytes = bk.get_downloads_storage_limit_bytes()
        return jsonify(success=True,
                       removed=result.get('removed', 0),
                       download_usage=usage,
                       download_limit_bytes=limit_bytes,
                       quota_reached=(usage.get('total_bytes', 0) >= limit_bytes))

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
                       quota_reached=(usage.get('total_bytes', 0) >= limit_bytes))

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
            rows = [r for r in rows if str(r.get('OBS_DIR', '') or '') == obs_dir]

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

        user_info = get_effective_user(session)
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
        accessible_rows = bk.filter_accessible_rows(all_rows, accessible_run_ids)

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

        user_info = get_effective_user(session)
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
        cfg = profile.get('data', {}) if isinstance(profile.get('data'), dict) else {}
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
            allowed_cols = [str(c).strip() for c in allowed_cols if str(c).strip()]

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

        db_cfg = profile_cfg.get('database', {}) if isinstance(profile_cfg, dict) else {}
        if not isinstance(db_cfg, dict):
            db_cfg = {}
        mode = str(db_cfg.get('DATABASE_MODE', profile_cfg.get('DATABASE_MODE', ''))).strip()
        host = str(db_cfg.get('DATABASE_HOST', profile_cfg.get('DATABASE_HOST', ''))).strip()
        username = str(db_cfg.get('DATABASE_USERNAME', profile_cfg.get('DATABASE_USERNAME', ''))).strip()
        password = str(db_cfg.get('DATABASE_PASSWORD', profile_cfg.get('DATABASE_PASSWORD', '')) or '')
        db_name = str(db_cfg.get('DATABASE_NAME', profile_cfg.get('DATABASE_NAME', ''))).strip()

        if not all([mode, host, username, db_name]):
            raise ValueError('Missing database connection configuration.')

        db_url = (
            f'{mode}://{quote_plus(username)}:{quote_plus(password)}'
            f'@{host}/{db_name}'
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
            ob_label = str(order_by_spec.get('table_label', '')).strip().upper()
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
        cfg = profile.get('data', {}) if isinstance(profile.get('data'), dict) else {}
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
        preset_filename = (
            general_cfg.get('db-query-preset-file', '').strip()
            if isinstance(general_cfg, dict) else ''
        )
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
        user_info = get_effective_user(session)
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
        user_info = get_effective_user(session)
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
        cfg = profile.get('data', {}) if isinstance(profile.get('data'), dict) else {}

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
        editor_is_admin = 'admin' in (user_info.get('groups', []) or [])
        # Which groups can the editor manage?
        can_add = {g for g in all_groups if f'manage.group.{g}' in perms}
        # Admin users can manage all non-admin groups from this UI.
        if editor_is_admin:
            can_add |= {g for g in all_groups if g != 'admin'}
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

        editor_is_admin = 'admin' in (user_info.get('groups', []) or [])
        target_groups = set(target_info.get('groups', []))

        # Never allow edits to admin accounts from this endpoint.
        if 'admin' in target_groups:
            return jsonify(
                success=False,
                error='Cannot modify admin accounts'
            ), 403

        # Never allow assigning admin via the users UI.
        if 'admin' in set(new_groups):
            return jsonify(
                success=False,
                error='Cannot assign admin group from this page'
            ), 403

        old_groups = target_groups
        changed = (set(new_groups) - old_groups) | (old_groups - set(new_groups))
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

        editor_is_admin = 'admin' in (user_info.get('groups', []) or [])
        target_groups = set(target_info.get('groups', []))

        # Never allow edits to admin accounts from this endpoint.
        if 'admin' in target_groups:
            return jsonify(
                success=False,
                error='Cannot modify admin accounts'
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

        groups = load_science_groups(instrument)
        group_names = sorted(groups.keys())

        # Derive available run_ids from all object table JSONs for instrument
        run_ids = self._get_instrument_run_ids(instrument)
        available_users = get_users_for_instrument(instrument)

        assigned_users = set()
        assigned_run_ids = set()
        groups_without_users = []
        groups_without_run_ids = []
        for gname, group_entry in groups.items():
            if not isinstance(group_entry, dict):
                continue

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
                    assigned_run_ids.add(rid)

            if not group_users:
                groups_without_users.append(str(gname))
            if not group_run_ids:
                groups_without_run_ids.append(str(gname))

        available_set = {str(u).strip() for u in available_users if str(u).strip()}
        available_run_id_set = {str(rid).strip() for rid in run_ids if str(rid).strip()}
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
            health_details.extend([f'run_id: {rid}' for rid in missing_run_ids])

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
        if name not in groups:
            return jsonify(
                success=True,
                group={'run_ids': [], 'users': []}
            )

        entry = groups[name]
        return jsonify(
            success=True,
            group={
                'run_ids': entry.get('run_ids', []),
                'users': entry.get('users', []),
            }
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
        groups[name] = {
            'run_ids': run_ids,
            'users': users,
        }
        save_science_groups(instrument, groups)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

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
        if name in groups:
            return jsonify(
                success=False, error='Group already exists'
            ), 409

        groups[name] = {'run_ids': [], 'users': []}
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
        if name not in groups:
            return jsonify(
                success=False, error='Group not found'
            ), 404

        del groups[name]
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
        editor_is_admin = 'admin' in editor_groups
        if editor_is_admin:
            return sorted(all_groups)

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

    def _fetch_table_columns(self, profile_cfg: dict, table_name: str):
        """Fetch ordered column names from a profile DB/table."""
        mode = str(self._profile_get_db(profile_cfg, 'DATABASE_MODE', '')).strip()
        host = str(self._profile_get_db(profile_cfg, 'DATABASE_HOST', '')).strip()
        username = str(self._profile_get_db(profile_cfg, 'DATABASE_USERNAME', '')).strip()
        password = str(self._profile_get_db(profile_cfg, 'DATABASE_PASSWORD', '') or '')
        db_name = str(self._profile_get_db(profile_cfg, 'DATABASE_NAME', '')).strip()

        if not all([mode, host, username, db_name, table_name]):
            raise ValueError('Missing DB connection or table configuration.')

        db_params = {
            'DATABASE_MODE': mode,
            'DATABASE_HOST': host,
            'DATABASE_USER': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
        }

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
        columns_map = entry.get('columns', {}) if isinstance(entry, dict) else {}
        if not table_names:
            return 'warning'
        for table in table_names:
            if not isinstance(groups_map.get(table, []), list) or not groups_map.get(table, []):
                return 'warning'
            if not isinstance(columns_map.get(table, []), list) or not columns_map.get(table, []):
                return 'warning'
        return 'ok'

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
            cfg = prof.get('data', {}) if isinstance(prof.get('data'), dict) else {}

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

        profile = self._find_accessible_profile(user_info, profile_id, instrument)
        if not profile:
            return jsonify(success=False, error='Profile not found or access denied'), 404

        editable_groups = self._editable_groups_for_editor(user_info, perms)
        all_groups = list(self.ari_groups.keys())
        cfg = profile.get('data', {}) if isinstance(profile.get('data'), dict) else {}

        db_access = load_db_access()
        saved_entry = (((db_access.get(instrument, {})
                        if isinstance(db_access.get(instrument, {}), dict)
                        else {}).get(profile_id, {}))
                       if instrument and profile_id else {})
        saved_groups = saved_entry.get('groups', {}) if isinstance(saved_entry, dict) else {}
        saved_columns = saved_entry.get('columns', {}) if isinstance(saved_entry, dict) else {}

        sections = []
        for label, key in self._db_access_table_keys().items():
            table_name = str(self._profile_get_db(cfg, key, '')).strip()
            if not table_name:
                continue

            selected_groups = saved_groups.get(label, [])
            if not isinstance(selected_groups, list):
                selected_groups = []
            selected_groups = [str(g).strip() for g in selected_groups if str(g).strip()]

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
            selected_cols = [str(c).strip() for c in selected_cols if str(c).strip()]

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
        if not isinstance(groups_map, dict) or not isinstance(columns_map, dict):
            return jsonify(success=False, error='Invalid groups/columns payload'), 400

        profile = self._find_accessible_profile(user_info, profile_id, instrument)
        if not profile:
            return jsonify(success=False, error='Profile not found or access denied'), 404

        editable_groups = set(self._editable_groups_for_editor(user_info, perms))

        cfg = profile.get('data', {}) if isinstance(profile.get('data'), dict) else {}
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
                if gname not in editable_groups and gname not in existing_for_table:
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
                table_columns[label] = self._fetch_table_columns(cfg, table_name)
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

        if instrument not in db_access or not isinstance(db_access.get(instrument), dict):
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

        all_profiles = load_apero_profiles()
        inst_profiles = all_profiles.get(instrument, {})

        # Keys stored per profile (served flat to UI for compatibility)
        _DB_KEYS = [
            'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_USERNAME',
            'DATABASE_PASSWORD', 'DATABASE_NAME',
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
            entry['SCIENCE_FIBER'] = self._profile_get_general(cfg, 'SCIENCE_FIBER', '')
            # SCIENCE_TYPES is a list
            entry['SCIENCE_TYPES'] = self._profile_get_general(cfg, 'SCIENCE_TYPES', [])
            entry['APERO_INSTRUMENT_PROFILE'] = cfg.get('APERO_INSTRUMENT_PROFILE', '')
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
            db_check = validate_database_connection(
                self._profile_get_db(cfg, 'DATABASE_MODE', ''),
                self._profile_get_db(cfg, 'DATABASE_HOST', ''),
                self._profile_get_db(cfg, 'DATABASE_USERNAME', ''),
                self._profile_get_db(cfg, 'DATABASE_PASSWORD', ''),
                self._profile_get_db(cfg, 'DATABASE_NAME', ''),
            )
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
        _DB_KEYS = [
            'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_USERNAME',
            'DATABASE_PASSWORD', 'DATABASE_NAME',
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
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
        for k in _DB_KEYS:
            val = data.get(k, '').strip()
            if not val:
                return jsonify(
                    success=False,
                    error=f'{k} is required'
                ), 400
            db_values[k] = val

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
            science_types = [t.strip() for t in science_types_raw.split(',') if t.strip()]
        else:
            science_types = [str(t).strip() for t in science_types_raw if str(t).strip()]
        if not science_types:
            return jsonify(success=False, error='SCIENCE_TYPES is required'), 400

        # Validate DATABASE_MODE
        if db_values['DATABASE_MODE'] not in ('mysql+pymysql',):
            return jsonify(
                success=False,
                error='Unsupported DATABASE_MODE'
            ), 400

        all_profiles = load_apero_profiles()
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
            profile_data['APERO_INSTRUMENT_PROFILE'] = _apero_instrument_profile
            # Materialize selected APERO instrument profile content so it is
            # persisted directly in apero_profiles.yaml.
            preset_path = (PACKAGE_DIR / 'resources' / 'aprofile_instruments'
                           / _apero_instrument_profile)
            if preset_path.is_file():
                try:
                    with preset_path.open('r', encoding='utf-8') as f:
                        preset_data = yaml.safe_load(f) or {}
                except Exception as _err:
                    return jsonify(success=False,
                                   error=f'Failed to load instrument profile: {_err}'), 400
                if isinstance(preset_data, dict):
                    if isinstance(preset_data.get('headers'), dict):
                        profile_data['headers'] = dict(preset_data.get('headers', {}))
                    # Presets can use either "plot" or "plots".
                    if isinstance(preset_data.get('plots'), dict):
                        profile_data['plots'] = dict(preset_data.get('plots', {}))
                    elif isinstance(preset_data.get('plot'), dict):
                        profile_data['plots'] = dict(preset_data.get('plot', {}))

                    preset_general = preset_data.get('general', {})
                    if isinstance(preset_general, dict):
                        merged_general = {}
                        # Keep non-science fields from preset general (e.g. bands),
                        # but normalize science keys to canonical uppercase form only.
                        for gkey, gval in preset_general.items():
                            if gkey in ('instrument', 'science_fiber', 'science_types'):
                                continue
                            merged_general[gkey] = gval
                        if 'SCIENCE_FIBER' in preset_general:
                            merged_general['SCIENCE_FIBER'] = preset_general.get('SCIENCE_FIBER')
                        elif 'science_fiber' in preset_general:
                            merged_general['SCIENCE_FIBER'] = preset_general.get('science_fiber')
                        if 'SCIENCE_TYPES' in preset_general:
                            merged_general['SCIENCE_TYPES'] = preset_general.get('SCIENCE_TYPES')
                        elif 'science_types' in preset_general:
                            merged_general['SCIENCE_TYPES'] = preset_general.get('science_types')
                        if 'INSTRUMENT' in preset_general:
                            merged_general['INSTRUMENT'] = preset_general.get('INSTRUMENT')
                        elif 'instrument' in preset_general:
                            merged_general['INSTRUMENT'] = preset_general.get('instrument')
                        # Preserve user-selected science values as source of truth.
                        merged_general['INSTRUMENT'] = instrument
                        merged_general['SCIENCE_FIBER'] = science_fiber
                        merged_general['SCIENCE_TYPES'] = science_types
                        profile_data['general'] = merged_general
            else:
                return jsonify(success=False,
                               error=f'Instrument profile file not found: {_apero_instrument_profile}'), 400
        inst_profiles[name] = profile_data
        save_apero_profiles(all_profiles)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True)

    def _api_apero_profiles_delete(self):
        """Delete an APERO profile."""
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

        all_profiles = load_apero_profiles()
        inst_profiles = all_profiles.get(instrument, {})
        if name not in inst_profiles:
            return jsonify(
                success=False, error='Profile not found'
            ), 404

        del inst_profiles[name]
        all_profiles[instrument] = inst_profiles
        save_apero_profiles(all_profiles)
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

        all_profiles = load_apero_profiles()
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

        all_profiles = load_apero_profiles()
        inst_profiles = all_profiles.get(instrument, {})
        if name not in inst_profiles:
            return jsonify(success=False, error='Profile not found'), 404

        old_groups = set(inst_profiles[name].get('groups', []))
        changed = (set(new_groups) - old_groups) | (old_groups - set(new_groups))
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

        mode = data.get('DATABASE_MODE', '').strip()
        host = data.get('DATABASE_HOST', '').strip()
        username = data.get('DATABASE_USERNAME', '').strip()
        password = data.get('DATABASE_PASSWORD', '')
        db_name = data.get('DATABASE_NAME', '').strip()

        if not all([mode, host, username, db_name]):
            return jsonify(success=False,
                           error='All database fields are required'), 400

        result = validate_database_connection(
            mode, host, username, password, db_name
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

        mode = data.get('DATABASE_MODE', '').strip()
        host = data.get('DATABASE_HOST', '').strip()
        username = data.get('DATABASE_USERNAME', '').strip()
        password = data.get('DATABASE_PASSWORD', '')
        db_name = data.get('DATABASE_NAME', '').strip()

        table_keys = [
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
        ]

        if not all([mode, host, username, db_name]):
            return jsonify(success=False,
                           error='All database fields are required'), 400

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
            'DATABASE_MODE': mode,
            'DATABASE_HOST': host,
            'DATABASE_USER': username,
            'DATABASE_PASSWORD': password,
            'DATABASE_NAME': db_name,
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

        want_type = 'GLOBAL' if self._is_global_scope(instrument) else 'INSTRUMENT'
        keys = []
        for task_key in task_module.TASK_LIST.keys():
            ttype = str(task_module.TYPE.get(task_key, 'INSTRUMENT')).strip().upper()
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

            for field in ['last_run', 'run_count', 'info', 'output_files',
                          'error', 'last_status', 'cooldown_until']:
                if field in task_cfg:
                    merged_cfg[field] = task_cfg.get(field)

            import_error = str(import_errors.get(task_key, '')).strip()
            if import_error:
                merged_cfg['last_status'] = 'failed'
                merged_cfg['error'] = import_error
                merged_cfg['info'] = (
                    '## Task Import Error\n\n'
                    f'**Task key**: `{task_key}`\n\n'
                    f'```\n{import_error}\n```\n'
                )

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
        inst_tasks, changed = self._merge_async_task_catalog(instrument, all_tasks)
        if changed:
            save_async_tasks(all_tasks)

        result = []
        for tc in inst_tasks:
            entry = dict(tc)
            tid = tc.get('id', '')
            rt = task_runner.get_task_status(tid) if tid else {'found': False}
            if not rt.get('found'):
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'info': tc.get('info', ''),
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': tc.get('error', ''),
                    'run_count': tc.get('run_count', 0),
                }
            entry['runtime'] = rt
            task_key = entry.get('task_key', '')
            entry['task_type'] = task_module.TYPE.get(task_key, 'INSTRUMENT')
            result.append(entry)

        queue_status = task_runner.get_status()
        return jsonify(success=True, tasks=result, queue=queue_status)

    def _api_async_tasks_global_list(self):
        """Load global tasks from the task registry defaults and overrides."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        all_tasks = load_async_tasks()
        global_scope = '__GLOBAL__'
        global_tasks, changed = self._merge_async_task_catalog(global_scope, all_tasks)
        if changed:
            save_async_tasks(all_tasks)

        result = []
        for tc in global_tasks:
            entry = dict(tc)
            tid = tc.get('id', '')
            rt = task_runner.get_task_status(tid) if tid else {'found': False}
            if not rt.get('found'):
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'info': tc.get('info', ''),
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': tc.get('error', ''),
                    'run_count': tc.get('run_count', 0),
                }
            entry['runtime'] = rt
            entry['task_type'] = 'GLOBAL'
            entry['instrument'] = global_scope
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
            })
        return jsonify(success=True, tasks=opts)

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

        if not instrument or not task_id:
            return jsonify(success=False, error='Missing fields'), 400
        if frequency <= 0:
            return jsonify(success=False, error='Frequency must be > 0'), 400
        if daily_copies < 0 or weekly_copies < 0:
            return jsonify(success=False,
                           error='Backup copy counts must be non-negative'), 400

        all_tasks = load_async_tasks()
        inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)

        found = False
        for t in inst_tasks:
            if t.get('id') != task_id:
                continue

            task_key = t.get('task_key', '')
            if task_key == 'ARI_LOCAL_DATA_BACKUP' and daily_copies + weekly_copies <= 0:
                return jsonify(success=False,
                               error='Backup task needs at least one retained daily or weekly copy'), 400

            t['frequency'] = frequency
            t['active'] = active
            if task_key == 'ARI_LOCAL_DATA_BACKUP':
                t['daily_copies'] = daily_copies
                t['weekly_copies'] = weekly_copies
            found = True
            break

        if not found:
            return jsonify(success=False, error='Task not found'), 404

        all_tasks[instrument] = inst_tasks
        save_async_tasks(all_tasks)
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, id=task_id)

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
        run_params = task_runner.build_run_params(
            instrument, local_data_dir, all_profiles, task_cfg
        )
        try:
            instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
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
                blocked.append({'id': task_cfg.get('id', ''), 'reason': reason})
                continue
            task_key = task_cfg.get('task_key', '')
            task_cls = task_module.TASK_LIST.get(task_key)
            if not task_cls:
                continue
            tid = task_cfg.get('id', '')
            if not tid:
                continue
            run_params = task_runner.build_run_params(
                instrument, local_data_dir, all_profiles, task_cfg
            )
            try:
                instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
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

    def _api_async_tasks_clear_history(self):
        """Clear recent async task history entries."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        result = task_runner.clear_recent_history()
        if result.get('success'):
            return jsonify(success=True, removed=int(result.get('removed', 0) or 0))
        return jsonify(success=False, error=result.get('error', 'Failed to clear history')), 500

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
        for tid in task_ids:
            rt = task_runner.get_task_status(tid)
            if not rt.get('found'):
                tc = task_cfg_map.get(tid, {})
                rt = {
                    'found': False,
                    'status': tc.get('last_status', 'not_started'),
                    'progress': 0,
                    'info': tc.get('info', ''),
                    'last_run': tc.get('last_run', 'Never'),
                    'output_files': tc.get('output_files', []),
                    'run_params': tc.get('last_run_params', {}),
                    'is_current': False,
                    'is_queued': False,
                    'error': tc.get('error', ''),
                    'run_count': tc.get('run_count', 0),
                }
            statuses[tid] = rt
        queue_status = task_runner.get_status()
        return jsonify(success=True, statuses=statuses, queue=queue_status)

    def _validate_async_task_file_path(self, path: str):
        """Validate and resolve an async task output file path."""
        if not path:
            return None, (jsonify(success=False, error='No path'), 400)
        if not os.path.isabs(path):
            return None, (jsonify(success=False, error='Must be an absolute path'), 400)

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
            if suffixes.intersection({'.gz', '.zip', '.fits', '.tar'}) or b'\x00' in raw[:4096]:
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

        def _rows_to_table(rows_data: list, columns_hint=None, row_count_hint=None) -> dict:
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

            row_count = row_count_hint if isinstance(row_count_hint, int) else len(rows_data)
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
            instruments = [i for i in all_instr if i in user_instr] or list(all_instr)

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
                    merged['links'][tag] = dict(inst_data.get('links', {}).get(section, {}))
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
            instruments = [i for i in all_instr if i in user_instr] or list(all_instr)

            events = list(ud.list_events(user_info['username']))
            for inst in instruments:
                inst_events = ud.load_instrument_calendar(inst).get('events', [])
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
            metadata = ud.manage_todo_metadata(user_info['username'], kind, op, value)
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
        return jsonify(ok=result['ok'], error=result.get('error', ''), detail='')

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
    # Run override
    # -----------------------------------------------------------------
    def run(self, host=None, port=None, debug=True, **kwargs):
        """Run the ARI Flask application.

        Uses values from command-line args unless explicitly overridden.
        """
        if host is None:
            host = self._resolve_host(self.args.host)
        if port is None:
            port = self.args.port
        super().run(host=host, port=port, debug=debug, **kwargs)
