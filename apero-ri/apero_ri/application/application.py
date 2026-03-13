#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Flask application class.

ARIApp inherits from Flask and wires up all routes, authentication,
and permission handling from groups.yaml / pages.yaml.
"""
import argparse
import os
import secrets
import socket
from datetime import timedelta
from pathlib import Path

from flask import (Flask, render_template, redirect, url_for,
                   request, session, flash)

from apero_ri.core.permissions import (
    load_groups, load_pages, resolve_user_permissions,
    get_children, is_parent_page, page_id_to_url,
    page_id_to_template, page_id_to_endpoint,
    get_nav_pages, get_visible_cards,
)
from apero_ri.core.auth import (
    ensure_default_user, authenticate, get_effective_user,
    get_public_permissions, get_user_info,
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

    # -----------------------------------------------------------------
    # View factories
    # -----------------------------------------------------------------
    def _make_page_view(self, page_id: str):
        """Create a view function for a page defined in pages.yaml."""
        page_def = self.ari_pages[page_id]
        view_perm = page_def.get('view-permission', '')
        template = page_id_to_template(page_id, self.ari_pages)
        # A page acts as parent if it has children or uses a subdir template
        is_parent = (is_parent_page(page_id, self.ari_pages)
                     or template.endswith('/index.html'))

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

            if is_parent:
                context['cards'] = get_visible_cards(
                    page_id, perms, self.ari_pages,
                    logged_in=(user_info is not None),
                )

            return render_template(template, **context)

        # Give the function a unique name for Flask
        view_func.__name__ = page_id_to_endpoint(page_id)
        return view_func

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
