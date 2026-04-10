#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Permission and group management.

Reads ``groups.yaml`` and ``pages.yaml`` from the resources directory
and provides permission resolution, page visibility filtering, and
sidebar tree building for the Flask application.

Created on 2024-01-01

@author: cook
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.permissions"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# resource paths
RESOURCES_DIR = Path(__file__).parent.parent / "resources"
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
GROUPS_FILE = RESOURCES_DIR / "groups.yaml"
PAGES_FILE = RESOURCES_DIR / "pages.yaml"
PARAMS_FILE = RESOURCES_DIR / "parameters.yaml"


# =============================================================================
# Define YAML loader functions
# =============================================================================
def load_groups() -> Dict[str, dict]:
    """
    Load group definitions from ``groups.yaml``.

    :return: dict mapping group names to group definition dicts
    :rtype: dict
    """
    with open(GROUPS_FILE, "r") as fio:
        return yaml.safe_load(fio)


def load_pages() -> Dict[str, dict]:
    """
    Load page definitions from ``pages.yaml``.

    :return: dict mapping page IDs to page definition dicts
    :rtype: dict
    """
    with open(PAGES_FILE, "r") as fio:
        return yaml.safe_load(fio)


def load_parameters() -> Dict[str, dict]:
    """
    Load parameter definitions from ``parameters.yaml``.

    :return: dict mapping parameter names to parameter definition dicts
    :rtype: dict
    """
    with open(PARAMS_FILE, "r") as fio:
        return yaml.safe_load(fio) or {}


# =============================================================================
# Define page side-nav helpers
# =============================================================================
def _side_nav_value(page_def: Dict[str, object], key: str) -> object:
    """
    Return a nested ``side-nav`` value with legacy key fallback.

    :param page_def: dict, a page definition dict from pages.yaml
    :param key: str, the side-nav key to look up

    :return: the resolved value, or None if absent
    :rtype: Any
    """
    side_nav = page_def.get("side-nav", {})
    if isinstance(side_nav, dict) and key in side_nav:
        return side_nav.get(key)
    # -------------------------------------------------------------------------
    # backward compatibility for old pages.yaml keys
    if key == "top-level":
        return page_def.get("full-nav", False)
    if key == "show":
        return not page_def.get("no-nav", False)
    if key == "pinned":
        return False
    return None


def is_side_nav_top_level(page_def: Dict[str, object]) -> bool:
    """
    Return True if this page is a top-level root for a sidebar tree.

    :param page_def: dict, a page definition dict from pages.yaml

    :return: bool
    :rtype: bool
    """
    return bool(_side_nav_value(page_def, "top-level"))


def is_side_nav_shown(page_def: Dict[str, object]) -> bool:
    """
    Return True if this page should appear in side-nav or card trees.

    :param page_def: dict, a page definition dict from pages.yaml

    :return: bool
    :rtype: bool
    """
    return bool(_side_nav_value(page_def, "show"))


def is_side_nav_pinned(page_def: Dict[str, object]) -> bool:
    """
    Return True if this page should always be pinned in sidebars.

    :param page_def: dict, a page definition dict from pages.yaml

    :return: bool
    :rtype: bool
    """
    return bool(_side_nav_value(page_def, "pinned"))


# =============================================================================
# Define permission resolution functions
# =============================================================================
def resolve_group_permissions(
    group_name: str,
    groups: Dict[str, dict],
    _visited: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Recursively resolve all permissions for a group, including those
    inherited from sub-groups.

    :param group_name: str, name of the group to resolve
    :param groups: dict, all group definitions from groups.yaml
    :param _visited: set or None, tracks visited groups to prevent
                     circular references (internal use)

    :return: set of permission strings
    :rtype: set
    """
    if _visited is None:
        _visited = set()
    # -------------------------------------------------------------------------
    # prevent circular references
    if group_name in _visited or group_name not in groups:
        return set()
    _visited.add(group_name)

    group_def = groups[group_name]
    permissions = set(group_def.get("permissions", []))
    # -------------------------------------------------------------------------
    # inherit from sub-groups
    for sub_group in group_def.get("groups", []):
        if sub_group and sub_group != "None":
            permissions |= resolve_group_permissions(
                sub_group, groups, _visited
            )
    return permissions


def resolve_user_permissions(
    user_groups: List[str], groups: Dict[str, dict]
) -> Set[str]:
    """
    Resolve all permissions for a user based on their group
    memberships.

    :param user_groups: list of str, the user's group names
    :param groups: dict, all group definitions from groups.yaml

    :return: set of permission strings
    :rtype: set
    """
    permissions: Set[str] = set()
    for group_name in user_groups:
        permissions |= resolve_group_permissions(group_name, groups)

    # Super-admin gets all permissions plus group/instrument/login_as
    # control for every known group.
    if "super_admin" in set(user_groups or []):
        for group_name in groups:
            permissions |= resolve_group_permissions(group_name, groups)
            permissions.add(f"manage.group.{group_name}")
            permissions.add(f"manage.instrument.{group_name}")
            permissions.add(f"login_as.{group_name}")
        permissions.add("add.instrument")
    return permissions


def get_inherited_groups(
    group_name: str,
    groups: Dict[str, dict],
    _visited: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Get all groups inherited (encompassed) by *group_name*, excluding
    itself.

    :param group_name: str, the group to resolve inheritance for
    :param groups: dict, all group definitions from groups.yaml
    :param _visited: set or None, tracks visited groups (internal)

    :return: set of inherited group name strings
    :rtype: set
    """
    if _visited is None:
        _visited = set()
    if group_name in _visited or group_name not in groups:
        return set()
    _visited.add(group_name)
    result: Set[str] = set()
    for sub in groups[group_name].get("groups", []):
        if sub and sub != "None" and sub in groups:
            result.add(sub)
            result |= get_inherited_groups(sub, groups, _visited)
    return result


# =============================================================================
# Define page tree and URL helpers
# =============================================================================
def get_children(page_id: str, pages: Dict[str, dict]) -> List[str]:
    """
    Return direct child page IDs for a given parent page.

    :param page_id: str, parent page ID
    :param pages: dict, all page definitions from pages.yaml

    :return: list of str child page IDs
    :rtype: list
    """
    children = []
    for pid, pdef in pages.items():
        if pdef.get("parent") == page_id:
            children.append(pid)
    return children


def is_parent_page(page_id: str, pages: Dict[str, dict]) -> bool:
    """
    Return True if *page_id* has at least one child page.

    :param page_id: str, the page ID to check
    :param pages: dict, all page definitions from pages.yaml

    :return: bool
    :rtype: bool
    """
    return len(get_children(page_id, pages)) > 0


def page_id_to_url(page_id: str) -> str:
    """
    Convert a page ID to a URL path.

    :param page_id: str, dot-separated page ID

    :return: str URL path
    :rtype: str
    """
    if page_id == "home":
        return "/"
    parts = page_id.split(".")
    return "/" + "/".join(parts[1:])


def _resolved_page_url(page_id: str, page_def: Dict[str, object]) -> str:
    """
    Resolve the URL for a page, preferring ``external-url`` when set.

    :param page_id: str, dot-separated page ID
    :param page_def: dict, page definition dict from pages.yaml

    :return: str, resolved URL path
    :rtype: str
    """
    ext_url = str(page_def.get("external-url", "") or "").strip()
    if ext_url:
        return ext_url
    return page_id_to_url(page_id)


def page_id_to_template(page_id: str, pages: Dict[str, dict]) -> str:
    """
    Convert a page ID to its Jinja2 template path.

    :param page_id: str, dot-separated page ID
    :param pages: dict, all page definitions from pages.yaml

    :return: str, relative template path
    :rtype: str
    """
    # -------------------------------------------------------------------------
    # special cases
    if page_id == "home":
        return "home/index.html"
    if page_id == "home.login":
        return "home/login.html"
    if page_id == "home.logout":
        return "home/login.html"

    parts = page_id.split(".")
    has_children = is_parent_page(page_id, pages)
    # -------------------------------------------------------------------------
    # two-part page IDs
    if len(parts) == 2:
        name = parts[1]
        # keep template folder compatibility after nav-id rename
        template_name = "admin" if name == "admin_portal" else name
        subdir_template = TEMPLATE_DIR / template_name / "index.html"
        if has_children or subdir_template.exists():
            return f"{template_name}/index.html"
        else:
            return f"home/{template_name}.html"
    # -------------------------------------------------------------------------
    # three-or-more part page IDs
    if len(parts) >= 3:
        parent_name = parts[1]
        template_parent = (
            "admin" if parent_name == "admin_portal" else parent_name
        )
        name = parts[-1]
        if has_children:
            return f"{template_parent}/{name}/index.html"
        else:
            return f"{template_parent}/{name}.html"
    return "general/coming_soon.html"


def page_id_to_endpoint(page_id: str) -> str:
    """
    Convert a page ID to a Flask endpoint name.

    :param page_id: str, dot-separated page ID

    :return: str Flask endpoint name (dots replaced with underscores)
    :rtype: str
    """
    return page_id.replace(".", "_")


# =============================================================================
# Define user-visible page filters
# =============================================================================
def get_visible_pages(
    user_permissions: Set[str], pages: Dict[str, dict]
) -> Dict[str, dict]:
    """
    Filter pages to only those visible to the user.

    :param user_permissions: set of str, resolved user permissions
    :param pages: dict, all page definitions from pages.yaml

    :return: dict of page definitions the user may view
    :rtype: dict
    """
    visible = {}
    for pid, pdef in pages.items():
        view_perm = pdef.get("view-permission", "")
        if view_perm in user_permissions:
            visible[pid] = pdef
    return visible


def get_nav_pages(
    user_permissions: Set[str], pages: Dict[str, dict]
) -> List[dict]:
    """
    Get pages that should appear in the quick-nav menu.

    :param user_permissions: set of str, resolved user permissions
    :param pages: dict, all page definitions from pages.yaml

    :return: list of nav-item dicts with keys id, label, icon, url
    :rtype: list
    """
    nav_pages = []
    for pid, pdef in pages.items():
        if not pdef.get("quick-nav", False):
            continue
        if not is_side_nav_shown(pdef):
            continue
        view_perm = pdef.get("view-permission", "")
        if view_perm not in user_permissions:
            continue
        # skip login/logout — handled separately in nav
        if pid in ("home.login", "home.logout"):
            continue
        nav_pages.append(
            {
                "id": pid,
                "label": pdef["label"],
                "icon": pdef.get("icon", ""),
                "url": _resolved_page_url(pid, pdef),
            }
        )
    return nav_pages


def get_visible_cards(
    parent_id: str,
    user_permissions: Set[str],
    pages: Dict[str, dict],
    logged_in: bool = False,
) -> List[dict]:
    """
    Get card data for children of a parent page that are visible to
    the user.

    :param parent_id: str, parent page ID
    :param user_permissions: set of str, resolved user permissions
    :param pages: dict, all page definitions from pages.yaml
    :param logged_in: bool, whether a user is currently logged in

    :return: list of card dicts with keys id, label, icon, url,
             has_children
    :rtype: list
    """
    children = get_children(parent_id, pages)
    cards = []
    for child_id in children:
        child_def = pages[child_id]
        if not is_side_nav_shown(child_def):
            continue
        view_perm = child_def.get("view-permission", "")
        if view_perm not in user_permissions:
            continue
        # always skip logout from cards
        if child_id == "home.logout":
            continue
        # show login card only when not logged in
        if child_id == "home.login" and logged_in:
            continue
        # show user card only when logged in
        if child_id == "home.user_portal" and not logged_in:
            continue
        cards.append(
            {
                "id": child_id,
                "label": child_def["label"],
                "icon": child_def.get("icon", ""),
                "url": _resolved_page_url(child_id, child_def),
                "has_children": is_parent_page(child_id, pages),
            }
        )
    return cards


# =============================================================================
# Define sidebar tree builders
# =============================================================================
def find_full_nav_root(page_id: str, pages: Dict[str, dict]) -> Optional[str]:
    """
    Walk up from *page_id* to find the nearest ancestor with
    ``side-nav: top-level: True``.

    :param page_id: str, starting page ID
    :param pages: dict, all page definitions from pages.yaml

    :return: str page ID of the top-level ancestor, or None
    :rtype: str | None
    """
    current = page_id
    while current:
        page_def = pages.get(current)
        if not page_def:
            return None
        if is_side_nav_top_level(page_def):
            return current
        parent = page_def.get("parent")
        if parent and parent != "None":
            current = str(parent)
        else:
            return None
    return None


def get_sidebar_tree(
    root_id: str,
    user_permissions: Set[str],
    pages: Dict[str, dict],
    active_page_id: str,
) -> List[dict]:
    """
    Build a flat sidebar tree for all descendants of *root_id*.

    Only pages the user has permission to view are included.

    :param root_id: str, root page ID for the tree
    :param user_permissions: set of str, resolved user permissions
    :param pages: dict, all page definitions from pages.yaml
    :param active_page_id: str, the currently active page ID

    :return: list of node dicts with keys id, label, icon, url,
             depth, active, expanded, has_children
    :rtype: list
    """
    result: List[dict] = []

    def _walk(parent_id: str, depth: int) -> None:
        children = get_children(parent_id, pages)
        for child_id in children:
            child_def = pages[child_id]
            if not is_side_nav_shown(child_def):
                continue
            view_perm = child_def.get("view-permission", "")
            if view_perm not in user_permissions:
                continue
            # skip special pages
            if child_id in ("home.login", "home.logout", "home.user_portal"):
                continue
            is_active = child_id == active_page_id
            is_expanded = is_active or active_page_id.startswith(child_id + ".")
            result.append(
                {
                    "id": child_id,
                    "label": child_def.get("label", ""),
                    "icon": child_def.get("icon", ""),
                    "url": _resolved_page_url(child_id, child_def),
                    "depth": depth,
                    "active": is_active,
                    "expanded": is_expanded,
                    "has_children": is_parent_page(child_id, pages),
                }
            )
            # only recurse into expanded subtrees
            if is_expanded and is_parent_page(child_id, pages):
                _walk(child_id, depth + 1)

    _walk(root_id, 0)
    return result


def get_pinned_sidebar_items(
    user_permissions: Set[str],
    pages: Dict[str, dict],
    active_page_id: str = "",
    logged_in: bool = False,
    username: str = "",
) -> List[dict]:
    """
    Get side-nav pinned items to render above section-specific trees.

    :param user_permissions: set of str, resolved user permissions
    :param pages: dict, all page definitions from pages.yaml
    :param active_page_id: str, the currently active page ID
    :param logged_in: bool, whether a user is currently logged in
    :param username: str, display username for label substitution

    :return: list of pinned-item dicts
    :rtype: list
    """
    items = []
    for pid, pdef in pages.items():
        if not is_side_nav_pinned(pdef):
            continue
        if not is_side_nav_shown(pdef):
            continue
        view_perm = pdef.get("view-permission", "")
        if view_perm not in user_permissions:
            continue
        # -----------------------------------------------------------------
        # auth-state specific pinned pages
        if pid == "home.login" and logged_in:
            continue
        if pid == "home.logout" and not logged_in:
            continue

        label = str(pdef.get("label", ""))
        if "{username}" in label:
            label = label.replace("{username}", username)
        items.append(
            {
                "id": pid,
                "label": label,
                "icon": pdef.get("icon", ""),
                "url": _resolved_page_url(pid, pdef),
                "depth": 0,
                "active": (pid == active_page_id),
                "expanded": False,
                "has_children": False,
                "pinned": True,
            }
        )
    # preserve insertion order from pages.yaml
    return items


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
