#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Permission and group management.

Reads groups.yaml and pages.yaml from resources/ and provides
permission resolution for the application.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# =============================================================================
# Define variables
# =============================================================================
RESOURCES_DIR = Path(__file__).parent.parent / 'resources'
TEMPLATE_DIR = Path(__file__).parent.parent / 'templates'
GROUPS_FILE = RESOURCES_DIR / 'groups.yaml'
PAGES_FILE = RESOURCES_DIR / 'pages.yaml'


# =============================================================================
# Define functions
# =============================================================================
def load_groups() -> Dict[str, dict]:
    """Load group definitions from groups.yaml."""
    with open(GROUPS_FILE, 'r') as f:
        return yaml.safe_load(f)


def load_pages() -> Dict[str, dict]:
    """Load page definitions from pages.yaml."""
    with open(PAGES_FILE, 'r') as f:
        return yaml.safe_load(f)


def resolve_group_permissions(group_name: str,
                              groups: Dict[str, dict],
                              _visited: Optional[Set[str]] = None
                              ) -> Set[str]:
    """Recursively resolve all permissions for a group, including inherited."""
    if _visited is None:
        _visited = set()
    # prevent circular references
    if group_name in _visited or group_name not in groups:
        return set()
    _visited.add(group_name)

    group_def = groups[group_name]
    permissions = set(group_def.get('permissions', []))

    # inherit from sub-groups
    for sub_group in group_def.get('groups', []):
        if sub_group and sub_group != 'None':
            permissions |= resolve_group_permissions(sub_group, groups,
                                                     _visited)
    return permissions


def resolve_user_permissions(user_groups: List[str],
                             groups: Dict[str, dict]) -> Set[str]:
    """Resolve all permissions for a user based on their group memberships."""
    permissions = set()
    for group_name in user_groups:
        permissions |= resolve_group_permissions(group_name, groups)
    return permissions


def get_children(page_id: str, pages: Dict[str, dict]) -> List[str]:
    """Get direct child page IDs for a given parent page."""
    children = []
    for pid, pdef in pages.items():
        if pdef.get('parent') == page_id:
            children.append(pid)
    return children


def is_parent_page(page_id: str, pages: Dict[str, dict]) -> bool:
    """Check if a page has children (is a parent page)."""
    return len(get_children(page_id, pages)) > 0


def page_id_to_url(page_id: str) -> str:
    """Convert a page ID to a URL path."""
    if page_id == 'home':
        return '/'
    parts = page_id.split('.')
    return '/' + '/'.join(parts[1:])


def page_id_to_template(page_id: str, pages: Dict[str, dict]) -> str:
    """Convert a page ID to its template path."""
    # Special cases
    if page_id == 'home':
        return 'home/index.html'
    if page_id == 'home.login':
        return 'home/login.html'
    if page_id == 'home.logout':
        return 'home/login.html'

    parts = page_id.split('.')
    has_children = is_parent_page(page_id, pages)

    if len(parts) == 2:
        name = parts[1]
        # Use the subdirectory template if the directory exists,
        # even when no children are defined in pages.yaml yet
        subdir_template = TEMPLATE_DIR / name / 'index.html'
        if has_children or subdir_template.exists():
            return f'{name}/index.html'
        else:
            return f'home/{name}.html'
    elif len(parts) >= 3:
        parent_name = parts[1]
        name = parts[-1]
        if has_children:
            return f'{parent_name}/{name}/index.html'
        else:
            return f'{parent_name}/{name}.html'
    return 'coming_soon.html'


def page_id_to_endpoint(page_id: str) -> str:
    """Convert a page ID to a Flask endpoint name."""
    return page_id.replace('.', '_')


def get_visible_pages(user_permissions: Set[str],
                      pages: Dict[str, dict]) -> Dict[str, dict]:
    """Filter pages to only those visible to the user."""
    visible = {}
    for pid, pdef in pages.items():
        view_perm = pdef.get('view-permission', '')
        if view_perm in user_permissions:
            visible[pid] = pdef
    return visible


def get_nav_pages(user_permissions: Set[str],
                  pages: Dict[str, dict]) -> List[dict]:
    """Get pages that should appear in the quick-nav menu."""
    nav_pages = []
    for pid, pdef in pages.items():
        if not pdef.get('quick-nav', False):
            continue
        view_perm = pdef.get('view-permission', '')
        if view_perm not in user_permissions:
            continue
        # Skip login/logout - handled separately in nav
        if pid in ('home.login', 'home.logout'):
            continue
        nav_pages.append({
            'id': pid,
            'label': pdef['label'],
            'icon': pdef.get('icon', ''),
            'url': page_id_to_url(pid),
        })
    return nav_pages


def get_visible_cards(parent_id: str,
                      user_permissions: Set[str],
                      pages: Dict[str, dict],
                      logged_in: bool = False) -> List[dict]:
    """Get card data for children of a parent page visible to the user."""
    children = get_children(parent_id, pages)
    cards = []
    for child_id in children:
        child_def = pages[child_id]
        view_perm = child_def.get('view-permission', '')
        if view_perm not in user_permissions:
            continue
        # Always skip logout from cards
        if child_id == 'home.logout':
            continue
        # Show login card only when not logged in
        if child_id == 'home.login' and logged_in:
            continue
        # Show user card only when logged in
        if child_id == 'home.user' and not logged_in:
            continue
        cards.append({
            'id': child_id,
            'label': child_def['label'],
            'icon': child_def.get('icon', ''),
            'url': page_id_to_url(child_id),
            'has_children': is_parent_page(child_id, pages),
        })
    return cards
