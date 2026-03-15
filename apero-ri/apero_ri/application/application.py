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
from datetime import timedelta, datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, List

from flask import (Flask, render_template, redirect, url_for,
                   request, session, flash, jsonify,
                   send_from_directory)

from apero_ri.core.permissions import (
    load_groups, load_pages, load_parameters,
    resolve_user_permissions, get_inherited_groups,
    get_children, is_parent_page, page_id_to_url,
    page_id_to_template, page_id_to_endpoint,
    get_nav_pages, get_visible_cards,
    find_full_nav_root, get_sidebar_tree,
)
from apero_ri.core.auth import (
    ensure_default_user, authenticate, get_effective_user,
    get_public_permissions, get_user_info,
    hash_password, verify_password,
    search_users, list_all_users, update_user_groups,
    update_user_instruments,
    delete_user, load_users, save_users,
    load_science_groups, save_science_groups, get_users_for_instrument,
    load_apero_profiles, save_apero_profiles,
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
        ud.set_ari_dir(self.args.data_dir or str(Path.home() / '.ari'))
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
        # Configure session lifetime for "remember me"
        self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        # Register context processors and routes
        self._register_context_processors()
        self._register_routes()
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
                login_as = session.get('login_as')
            else:
                perms = get_public_permissions()
                logged_in = False
                username = None
                login_as = None

            nav_pages = get_nav_pages(perms, self.ari_pages)
            logo_path = STATIC_DIR / 'images' / 'apero_logo.png'

            return {
                'logged_in': logged_in,
                'username': username,
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

        # Async tasks API routes
        self.add_url_rule('/api/admin/async-tasks/list',
                  'api_async_tasks_list',
                  self._api_async_tasks_list)
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
        self.add_url_rule('/data_portal/<profile_id>/<path:objname>',
              'ri_object_page',
              self._ri_object_page_view)
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

    def _build_sidebar_context(self, page_id: str, perms):
        """Build sidebar context dict for pages with full-nav."""
        nav_root = find_full_nav_root(page_id, self.ari_pages)
        if not nav_root:
            return {}
        root_def = self.ari_pages[nav_root]
        sidebar_tree = get_sidebar_tree(
            nav_root, perms, self.ari_pages, page_id
        )
        return {
            'sidebar_root': nav_root,
            'sidebar_label': root_def.get('label', ''),
            'sidebar_icon': root_def.get('icon', ''),
            'sidebar_url': page_id_to_url(nav_root),
            'sidebar_tree': sidebar_tree,
        }

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

            # Sidebar context for full-nav sections
            nav_root = find_full_nav_root(page_id, self.ari_pages)
            if nav_root:
                context.update(self._build_sidebar_context(page_id, perms))
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

            # Science groups page: inject user's instruments
            if page_id == 'home.admin.science_groups' and user_info:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                user_instr = user_info.get('instruments', [])
                # Filter to instruments the user has
                context['instruments'] = [
                    i for i in all_instr if i in user_instr
                ]

            # Async tasks page: inject instruments
            if page_id == 'home.admin.async_tasks' and user_info:
                params = load_parameters()
                all_instr = params.get('instruments', {}).get('value', [])
                context['instruments'] = all_instr

            # APERO profiles page: inject instruments + groups meta
            if page_id == 'home.admin.apero_profiles' and user_info:
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

            # Data portal: inject accessible profiles
            if page_id == 'home.data_portal':
                db_ctx = self._build_ri_context(user_info)
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
            if page_id == 'home.admin.calendar' and user_info:
                context.update(
                    self._build_admin_instrument_context(user_info, perms))

            # Admin links
            if page_id == 'home.admin.links' and user_info:
                context.update(
                    self._build_admin_instrument_context(user_info, perms))

            # Admin email settings
            if page_id == 'home.admin.email':
                context.update(self._build_admin_email_context(perms))

            # Admin index: inject card health status
            if page_id == 'home.admin':
                context['card_health'] = self._build_admin_card_health(
                    user_info, perms)

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

    def _build_ri_context(self, user_info):
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

        # Custom sidebar listing accessible profiles
        sidebar_tree = []
        for prof in accessible:
            sidebar_tree.append({
                'id': f'home.data_portal.{prof["profile_id"]}',
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{prof["profile_id"]}',
                'depth': 0,
                'active': False,
                'expanded': False,
                'has_children': False,
            })

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

    def _build_admin_card_health(self, user_info, perms) -> dict:
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
                    health['home.admin.users'] = {
                        'status': 'warning',
                        'message': f'{unreviewed} user(s) with only "public" access – may need group assignment.',
                    }
                else:
                    health['home.admin.users'] = {'status': 'ok', 'message': ''}
            except Exception:
                pass

        # ── Email: error if enabled but connection fails ──────────────────
        if 'view.admin' in perms:
            try:
                email_cfg = eb.load_email_config()
                if not email_cfg.get('enabled', False):
                    health['home.admin.email'] = {
                        'status': 'warning',
                        'message': 'Email delivery is not enabled. Verification codes go to log file.',
                    }
                else:
                    test = eb.test_email_connection(email_cfg)
                    if test['ok']:
                        health['home.admin.email'] = {'status': 'ok', 'message': ''}
                    else:
                        health['home.admin.email'] = {
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
                    health['home.admin.apero_profiles'] = {
                        'status': 'error',
                        'message': (
                            f'Some APERO profiles need attention. '
                            f'{"; ".join(profile_errors[:3])}'
                            f'{"; ..." if len(profile_errors) > 3 else ""}'
                        ),
                    }
                else:
                    health['home.admin.apero_profiles'] = {'status': 'ok', 'message': ''}
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
                    health['home.admin.async_tasks'] = {
                        'status': 'error',
                        'message': (
                            f'{len(failed_tasks)} active task(s) in error: '
                            f'{", ".join(failed_tasks[:3])}'
                            f'{" ..." if len(failed_tasks) > 3 else ""}'
                        ),
                    }
                else:
                    health['home.admin.async_tasks'] = {'status': 'ok', 'message': ''}
            except Exception:
                pass

        return health

    def _build_apero_profiles_overview_status(self) -> dict:
        """Build all-instruments APERO profile readiness and issue details."""
        profiles_by_instrument = load_apero_profiles()
        path_keys = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
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
                    cfg.get('DATABASE_MODE', ''),
                    cfg.get('DATABASE_HOST', ''),
                    cfg.get('DATABASE_USERNAME', ''),
                    cfg.get('DATABASE_PASSWORD', ''),
                    cfg.get('DATABASE_NAME', ''),
                )
                if not db.get('valid', False):
                    db_error = str(db.get('error', '') or 'connection failed').strip()
                    reason_parts.append(f'Database error: {db_error}')

                invalid_paths = []
                for key in path_keys:
                    path_val = str(cfg.get(key, '')).strip()
                    if not path_val or not Path(path_val).is_dir():
                        invalid_paths.append(key)
                if invalid_paths:
                    reason_parts.append(
                        'Invalid paths: ' + ', '.join(invalid_paths)
                    )

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

        # Sub-page section cards
        section_cards = [
            {
                'key': 'object_table',
                'label': 'Astrophysical Object Table',
                'icon': 'fa-solid fa-star',
                'url': f'/data_portal/{profile_id}/object-table',
                'description': 'Browse and search astrophysical objects '
                               'in this reduction profile.',
            },
            {
                'key': 'obs_table',
                'label': 'Observation Table',
                'icon': 'fa-solid fa-binoculars',
                'url': f'/data_portal/{profile_id}/observation-table',
                'description': 'View night-by-night observations '
                               'and their reduction status.',
            },
            {
                'key': 'query_db',
                'label': 'Database Query',
                'icon': 'fa-solid fa-terminal',
                'description': 'Run custom queries against the '
                               'reduction database tables.',
            },
            {
                'key': 'qc_graphs',
                'label': 'Quality Control Graphs',
                'icon': 'fa-solid fa-chart-line',
                'description': 'Interactive plots of quality control '
                               'metrics over time.',
            },
        ]

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
        sidebar_tree = []
        for prof in accessible:
            pid = f'home.data_portal.{prof["profile_id"]}'
            is_current = prof['profile_id'] == profile_id
            sidebar_tree.append({
                'id': pid,
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{prof["profile_id"]}',
                'depth': 0,
                'active': pid == page_id,
                'expanded': is_current,
                'has_children': True,
            })
            if is_current:
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.object_table',
                    'label': 'Astrophysical Object Table',
                    'icon': 'fa-solid fa-star',
                    'url': f'/data_portal/{prof["profile_id"]}/object-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.obs_table',
                    'label': 'Observation Table',
                    'icon': 'fa-solid fa-binoculars',
                    'url': f'/data_portal/{prof["profile_id"]}/observation-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.query_db',
                    'label': 'Database Query',
                    'icon': 'fa-solid fa-server',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.qc_graphs',
                    'label': 'Quality Control Graphs',
                    'icon': 'fa-solid fa-chart-line',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })
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
            cfg.get('DATABASE_MODE', ''),
            cfg.get('DATABASE_HOST', ''),
            cfg.get('DATABASE_USERNAME', ''),
            cfg.get('DATABASE_PASSWORD', ''),
            cfg.get('DATABASE_NAME', ''),
        )

        # -- Path checks --
        path_keys = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]
        path_results = {}
        all_paths_ok = True
        for key in path_keys:
            val = cfg.get(key, '')
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
        """Handle login page: show form or process login."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            user = authenticate(username, password)
            if user:
                session['user'] = user['username']
                session['last_login'] = user.get('last_login')
                session.pop('login_as', None)
                # Handle "remember me"
                if request.form.get('remember'):
                    session.permanent = True
                else:
                    session.permanent = False
                flash(f'Welcome, {user["username"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'danger')

        # If already logged in, show the logged-in state
        logged_in = get_effective_user(session) is not None
        return render_template('home/login.html',
                               page_label='Login' if not logged_in
                               else 'Account',
                               page_icon='fa-solid fa-right-to-bracket',
                               logged_in_state=logged_in)

    def _logout_view(self):
        """Clear session and redirect to home."""
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

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
        return bool(re.match(r'^[a-z][a-z0-9._-]{2,63}$', username))

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
                           error='Username must be lowercase and 3+ chars.'), 400
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
        context.update(self._build_sidebar_context(page_id, perms))
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

        # Build sidebar: all profiles, with sub-items under the current one
        sidebar_tree = []
        for prof in accessible:
            pid = f'home.data_portal.{prof["profile_id"]}'
            is_current = prof['profile_id'] == profile_id
            sidebar_tree.append({
                'id': pid,
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{prof["profile_id"]}',
                'depth': 0,
                'active': False,
            })
            if is_current:
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.object_table',
                    'label': 'Astrophysical Object Table',
                    'icon': 'fa-solid fa-star',
                    'url': f'/data_portal/{prof["profile_id"]}/object-table',
                    'depth': 1,
                    'active': True,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.obs_table',
                    'label': 'Observation Table',
                    'icon': 'fa-solid fa-binoculars',
                    'url': f'/data_portal/{prof["profile_id"]}/observation-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.query_db',
                    'label': 'Database Query',
                    'icon': 'fa-solid fa-server',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.qc_graphs',
                    'label': 'Quality Control Graphs',
                    'icon': 'fa-solid fa-chart-line',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })

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
        from apero_ri.core.auth import ARI_DIR

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
        tasks_dir = ARI_DIR / 'tasks' / instrument
        json_path = tasks_dir / f'object_table_{profile_id}.json'

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

        all_rows = data.get('rows', [])
        generated_at = (data.get('generated_at')
                        or data.get('metadata', {}).get('GENERATED_AT'))

        # Filter rows based on accessible run_ids
        filtered = []
        for row in all_rows:
            raw = str(row.get('RUN_ID', '') or '')
            row_rids = {r.strip() for r in raw.split(',') if r.strip()}
            if row_rids & accessible_run_ids:
                filtered.append(row)

        # Build column list (exclude RUN_ID)
        skip = {'RUN_ID'}
        columns = [c for c in (all_rows[0].keys() if all_rows else [])
                   if c not in skip]

        # Strip skipped columns from each row
        clean_rows = [
            {k: v for k, v in row.items() if k not in skip}
            for row in filtered
        ]

        return jsonify(
            success=True,
            rows=clean_rows,
            columns=columns,
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

        sidebar_tree = []
        for prof in accessible:
            pid = f'home.data_portal.{prof["profile_id"]}'
            is_current = prof['profile_id'] == profile_id
            sidebar_tree.append({
                'id': pid,
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{prof["profile_id"]}',
                'depth': 0,
                'active': False,
            })
            if is_current:
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.object_table',
                    'label': 'Astrophysical Object Table',
                    'icon': 'fa-solid fa-star',
                    'url': f'/data_portal/{prof["profile_id"]}/object-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': page_id,
                    'label': 'Observation Table',
                    'icon': 'fa-solid fa-binoculars',
                    'url': f'/data_portal/{prof["profile_id"]}/observation-table',
                    'depth': 1,
                    'active': True,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.query_db',
                    'label': 'Database Query',
                    'icon': 'fa-solid fa-server',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.qc_graphs',
                    'label': 'Quality Control Graphs',
                    'icon': 'fa-solid fa-chart-line',
                    'url': '',
                    'depth': 1,
                    'active': False,
                    'disabled': True,
                })

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

        sidebar_tree = []
        for prof in accessible:
            pid = f'home.data_portal.{prof["profile_id"]}'
            is_current = prof['profile_id'] == profile_id
            sidebar_tree.append({
                'id': pid,
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/data_portal/{prof["profile_id"]}',
                'depth': 0,
                'active': False,
            })
            if is_current:
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.object_table',
                    'label': 'Astrophysical Object Table',
                    'icon': 'fa-solid fa-star',
                    'url': f'/data_portal/{prof["profile_id"]}/object-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': f'home.data_portal.{prof["profile_id"]}.obs_table',
                    'label': 'Observation Table',
                    'icon': 'fa-solid fa-binoculars',
                    'url': f'/data_portal/{prof["profile_id"]}/observation-table',
                    'depth': 1,
                    'active': False,
                })
                sidebar_tree.append({
                    'id': page_id,
                    'label': objname,
                    'icon': page_icon,
                    'url': f'/data_portal/{prof["profile_id"]}/{objname}',
                    'depth': 1,
                    'active': True,
                })

        context = {
            'page_id': page_id,
            'page_label': page_label,
            'page_icon': page_icon,
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            'objname': objname,
            'sidebar_root': 'home.data_portal',
            'sidebar_label': 'Data Portal',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/data_portal',
            'sidebar_tree': sidebar_tree,
        }
        return render_template('data_portal/object_page.html', **context)

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
        json_path = tasks_dir / f'obs_table_{profile_id}.json'

        # Backward compatibility for older task outputs.
        if not json_path.exists():
            legacy_path = tasks_dir / f'observation_table_{profile_id}.json'
            if legacy_path.exists():
                json_path = legacy_path

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

        all_rows = data.get('rows', [])
        generated_at = (data.get('generated_at')
                        or data.get('metadata', {}).get('GENERATED_AT'))

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

        clean_rows = [
            {k: v for k, v in row.items() if k not in skip}
            for row in filtered
        ]

        return jsonify(
            success=True,
            rows=clean_rows,
            columns=columns,
            generated_at=generated_at,
            total_rows=len(all_rows),
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

        return jsonify(
            success=True,
            groups=group_names,
            run_ids=run_ids,
            available_users=available_users,
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

        # Keys stored per profile
        _DB_KEYS = [
            'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_USERNAME',
            'DATABASE_PASSWORD', 'DATABASE_NAME',
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
            'SCIENCE_FIBER',
        ]
        _PATH_KEYS = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
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
                entry[k] = cfg.get(k, '')
            # SCIENCE_TYPES is a list
            entry['SCIENCE_TYPES'] = cfg.get('SCIENCE_TYPES', [])
            # Copy path fields with exists check
            all_paths_ok = True
            for k in _PATH_KEYS:
                val = cfg.get(k, '')
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
                cfg.get('DATABASE_MODE', ''),
                cfg.get('DATABASE_HOST', ''),
                cfg.get('DATABASE_USERNAME', ''),
                cfg.get('DATABASE_PASSWORD', ''),
                cfg.get('DATABASE_NAME', ''),
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
        _TEXT_KEYS = [
            'apero_version', 'reduction_server',
            'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_USERNAME',
            'DATABASE_PASSWORD', 'DATABASE_NAME',
            'ASTROM_TABLENAME', 'CALIB_TABLENAME', 'FINDEX_TABLENAME',
            'LOG_TABLENAME', 'TELLU_TABLENAME', 'REJECT_TABLENAME',
            'SCIENCE_FIBER',
        ]
        _PATH_KEYS = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]

        values = {}
        for k in _TEXT_KEYS:
            val = data.get(k, '').strip()
            if not val:
                return jsonify(
                    success=False,
                    error=f'{k} is required'
                ), 400
            values[k] = val

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
            values[k] = val

        # SCIENCE_TYPES: accepted as a list or comma-separated string
        science_types_raw = data.get('SCIENCE_TYPES', [])
        if isinstance(science_types_raw, str):
            science_types = [t.strip() for t in science_types_raw.split(',') if t.strip()]
        else:
            science_types = [str(t).strip() for t in science_types_raw if str(t).strip()]
        if not science_types:
            return jsonify(success=False, error='SCIENCE_TYPES is required'), 400
        values['SCIENCE_TYPES'] = science_types

        # Validate DATABASE_MODE
        if values['DATABASE_MODE'] not in ('mysql+pymysql',):
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
        inst_profiles[name] = profile_data
        save_apero_profiles(all_profiles)
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

    def _api_async_tasks_list(self):
        """List async task configs for an instrument, merged with runtime state."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        instrument = request.args.get('instrument', '').strip()
        if not instrument:
            return jsonify(success=False, error='No instrument'), 400

        all_tasks = load_async_tasks()
        inst_tasks = all_tasks.get(instrument, [])

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
                    'is_current': False,
                    'is_queued': False,
                    'error': tc.get('error', ''),
                    'run_count': tc.get('run_count', 0),
                }
            entry['runtime'] = rt
            result.append(entry)

        queue_status = task_runner.get_status()
        return jsonify(success=True, tasks=result, queue=queue_status)

    def _api_async_tasks_task_list(self):
        """Return available task classes from apero_ri.tasks.TASK_LIST."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        from apero_ri import tasks as task_module
        opts = []
        for key, cls in task_module.TASK_LIST.items():
            inst = cls()
            opts.append({
                'key': key,
                'name': inst.name,
                'description': inst.description,
            })
        return jsonify(success=True, tasks=opts)

    def _api_async_tasks_save(self):
        """Create or update an async task configuration."""
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

        if not instrument or not task_key:
            return jsonify(success=False, error='Missing fields'), 400
        if frequency <= 0:
            return jsonify(success=False, error='Frequency must be > 0'), 400
        if daily_copies < 0 or weekly_copies < 0:
            return jsonify(success=False,
                           error='Backup copy counts must be non-negative'), 400
        if (task_key == 'ARI_LOCAL_DATA_BACKUP'
                and daily_copies + weekly_copies <= 0):
            return jsonify(success=False,
                           error='Backup task needs at least one retained daily or weekly copy'), 400

        from apero_ri import tasks as task_module
        if task_key not in task_module.TASK_LIST:
            return jsonify(success=False, error='Invalid task key'), 400

        all_tasks = load_async_tasks()
        inst_tasks = all_tasks.get(instrument, [])

        if task_id:
            found = False
            for t in inst_tasks:
                if t.get('id') == task_id:
                    t['task_key'] = task_key
                    t['frequency'] = frequency
                    t['active'] = active
                    t['daily_copies'] = daily_copies
                    t['weekly_copies'] = weekly_copies
                    found = True
                    break
            if not found:
                return jsonify(success=False, error='Task not found'), 404
        else:
            import uuid
            task_id = str(uuid.uuid4())
            inst_tasks.append({
                'id': task_id,
                'task_key': task_key,
                'frequency': frequency,
                'active': active,
                'daily_copies': daily_copies,
                'weekly_copies': weekly_copies,
                'order': len(inst_tasks) + 1,
            })

        all_tasks[instrument] = inst_tasks
        save_async_tasks(all_tasks)
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
        for t in all_tasks.get(instrument, []):
            if t.get('id') == task_id:
                t['active'] = not t.get('active', True)
                save_async_tasks(all_tasks)
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
        task_cfg = next(
            (t for t in all_tasks.get(instrument, [])
             if t.get('id') == task_id),
            None
        )
        if not task_cfg:
            return jsonify(success=False, error='Task not found'), 404

        from apero_ri import tasks as task_module
        task_key = task_cfg.get('task_key', '')
        task_cls = task_module.TASK_LIST.get(task_key)
        if not task_cls:
            return jsonify(success=False, error='Unknown task class'), 400

        all_profiles = load_apero_profiles()
        run_params = task_runner.build_run_params(
            instrument, local_data_dir, all_profiles, task_cfg
        )
        instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
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
        inst_tasks = sorted(
            all_tasks.get(instrument, []),
            key=lambda t: t.get('order', 999)
        )

        from apero_ri import tasks as task_module
        all_profiles = load_apero_profiles()

        added = []
        for task_cfg in inst_tasks:
            if not task_cfg.get('active', True):
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
            instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
            task_runner.enqueue(instrument, tid, instance, run_params)
            added.append(tid)

        return jsonify(success=True, added=added)

    def _api_async_tasks_stop(self):
        """Clear the pending queue (does not interrupt the running task)."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401
        task_runner.stop_and_clear()
        return jsonify(success=True)

    def _api_async_tasks_status(self):
        """Poll runtime status for a set of task ids and the full queue."""
        user_info, perms = self._require_async_tasks_perm()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

        ids_param = request.args.get('ids', '').strip()
        task_ids = [i for i in ids_param.split(',') if i.strip()]

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

        if isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                columns = []
                seen = set()
                for item in data:
                    for key in item.keys():
                        skey = str(key)
                        if skey not in seen:
                            seen.add(skey)
                            columns.append(skey)

                rows = []
                for item in data[:max_rows]:
                    row = {}
                    for col in columns:
                        row[col] = _cell(item.get(col, ''))
                    rows.append(row)

                return {
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(data),
                    'truncated': len(data) > max_rows,
                }

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
        slim = [{k: v for k, v in n.items() if k != 'content'}
                for n in notes]
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
