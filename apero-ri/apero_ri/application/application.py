#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Flask application class.

ARIApp inherits from Flask and wires up all routes, authentication,
and permission handling from groups.yaml / pages.yaml.
"""
import argparse
import os
import re
import secrets
import socket
from datetime import timedelta
from pathlib import Path

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
    search_users, list_all_users, update_user_groups,
    update_user_instruments,
    delete_user, load_users,
    load_science_groups, save_science_groups, get_users_for_instrument,
    load_apero_profiles, save_apero_profiles,
    validate_path_exists, validate_database_connection,
    get_accessible_profiles,
)
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
        # Logout route (special)
        self.add_url_rule('/logout', 'logout', self._logout_view)

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

        # Dynamic reduction interface profile sub-pages
        self.add_url_rule('/reduction_interface/<profile_id>',
                          'ri_profile',
                          self._ri_profile_view)

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

            # Reduction interface: inject accessible profiles
            if page_id == 'home.reduction_interface':
                db_ctx = self._build_ri_context(user_info)
                context.update(db_ctx)

            return render_template(template, **context)

        # Give the function a unique name for Flask
        view_func.__name__ = page_id_to_endpoint(page_id)
        return view_func

    # -----------------------------------------------------------------
    # Reduction interface helpers
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

    def _build_ri_context(self, user_info):
        """Build template context for the reduction interface page."""
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
                'url': f'/reduction_interface/{prof["profile_id"]}',
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
                'id': f'home.reduction_interface.{prof["profile_id"]}',
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/reduction_interface/{prof["profile_id"]}',
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

    def _ri_profile_view(self, profile_id):
        """View function for dynamic reduction interface profile sub-pages."""
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info['groups'], self.ari_groups
            )
        else:
            perms = get_public_permissions()

        if 'view.reduction_interface' not in perms:
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
            return redirect(url_for('home_reduction_interface'))

        page_id = f'home.reduction_interface.{profile_id}'
        colors = self._instrument_colors()
        color = colors.get(profile['instrument'],
                           self._INSTRUMENT_PALETTE[0])

        context = {
            'page_id': page_id,
            'page_label': profile_id,
            'page_icon': 'fa-solid fa-laptop-code',
            'is_parent': False,
            'profile': profile,
            'profile_color': color,
            # Sidebar
            'sidebar_root': 'home.reduction_interface',
            'sidebar_label': 'Reduction Interface',
            'sidebar_icon': 'fa-solid fa-database',
            'sidebar_url': '/reduction_interface',
        }

        # Build sidebar tree with current page highlighted
        sidebar_tree = []
        for prof in accessible:
            pid = f'home.reduction_interface.{prof["profile_id"]}'
            sidebar_tree.append({
                'id': pid,
                'label': prof['profile_id'],
                'icon': 'fa-solid fa-laptop-code',
                'url': f'/reduction_interface/{prof["profile_id"]}',
                'depth': 0,
                'active': pid == page_id,
                'expanded': False,
                'has_children': False,
            })
        context['sidebar_tree'] = sidebar_tree

        return render_template('reduction_interface/profile.html', **context)

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

        query = request.args.get('q', '').strip()
        if query:
            results = search_users(query)
        else:
            results = list_all_users()

        # Build group metadata for the editing user
        all_groups = list(self.ari_groups.keys())
        # Which groups can the editor manage?
        can_add = {g for g in all_groups if f'manage.group.{g}' in perms}
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
        can_add_instrument = 'add.instrument' in perms

        return jsonify(
            success=True,
            users=results,
            all_groups=all_groups,
            can_add_groups=sorted(can_add),
            inherited_map=inherited_map,
            all_instruments=all_instruments,
            editor_instruments=editor_instruments,
            can_add_instrument=can_add_instrument,
            editor_username=user_info['username'],
        )

    def _api_user_update_groups(self):
        """Update a target user's groups."""
        user_info, perms = self._require_admin_user()
        if not user_info:
            return jsonify(success=False, error='Unauthorized'), 401

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

        old_groups = set(target_info.get('groups', []))
        changed = (set(new_groups) - old_groups) | (old_groups - set(new_groups))
        for g in changed:
            if f'manage.group.{g}' not in perms:
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

        data = request.get_json()
        if not data or 'username' not in data or 'instruments' not in data:
            return jsonify(success=False, error='Missing data'), 400

        target = data['username']
        new_instruments = data['instruments']

        # Must have add.instrument permission OR only editing own instruments
        if 'add.instrument' not in perms:
            if target != user_info['username']:
                return jsonify(
                    success=False,
                    error='No permission to manage instruments'
                ), 403

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

        # Also get available run ids and users for this instrument
        run_ids = ['1111', '2222', '3333']  # Proxy for now
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
        ]
        _PATH_KEYS = [
            'PATH_RAW', 'PATH_PP', 'PATH_RED', 'PATH_CALIB',
            'PATH_TELLU', 'PATH_LOG', 'PATH_LBL',
        ]

        # Build list with validation status, sorted by DISPLAY_ORDER
        profiles = []
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
            profiles.append(entry)
        profiles.sort(key=lambda p: p['DISPLAY_ORDER'])
        return jsonify(success=True, profiles=profiles)

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

        # Preserve existing groups when editing
        existing_groups = []
        if name in inst_profiles:
            existing_groups = inst_profiles[name].get('groups', [])

        # Require at least one group
        if not existing_groups and name not in inst_profiles:
            # New profile – groups will be set after first save via cards
            pass

        profile_data = {'DISPLAY_ORDER': order, 'groups': existing_groups}
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
