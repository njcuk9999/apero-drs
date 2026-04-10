"""Sidebar construction helpers for ARIApp."""

from typing import Optional

from apero_ri.core.permissions import get_pinned_sidebar_items


def build_data_portal_sidebar_tree(
    app,
    accessible_profiles: list,
    active_page_id: str,
    user_permissions,
    user_info=None,
    current_profile_id: Optional[str] = None,
    objname: Optional[str] = None,
    include_children: bool = True,
) -> list:
    """Build data portal sidebar tree from pages.yaml templates."""
    sidebar_tree = []
    pinned_tree = get_pinned_sidebar_items(
        user_permissions,
        app.ari_pages,
        active_page_id,
        logged_in=(user_info is not None),
        username=(user_info or {}).get("username", ""),
    )
    sidebar_tree.extend(pinned_tree)
    for prof in accessible_profiles:
        profile_id = prof["profile_id"]
        page_id = f"home.data_portal.{profile_id}"
        profile_meta = app._page_template_meta(
            "home.data_portal.{apero_profile}",
            apero_profile=profile_id,
        )
        is_current = profile_id == current_profile_id
        sidebar_tree.append(
            {
                "id": page_id,
                "label": profile_meta.get("label") or profile_id,
                "icon": profile_meta.get("icon") or "fa-solid fa-laptop-code",
                "url": f"/data_portal/{profile_id}",
                "depth": 0,
                "active": active_page_id == page_id,
                "expanded": is_current,
                "has_children": include_children,
            }
        )

        if not include_children or not is_current:
            continue

        # Build child items in pages.yaml definition order so that
        # reordering pages.yaml automatically updates the sidebar.
        child_url_map = {
            "object_table": (f"/data_portal/{profile_id}/object-table", False),
            "obs_table": (
                f"/data_portal/{profile_id}/observation-table",
                False,
            ),
            "query_db": (f"/data_portal/{profile_id}/query-db", False),
            "fav_objects": (f"/data_portal/{profile_id}/fav-objects", False),
            "favourites_objects": (
                f"/data_portal/{profile_id}/fav-objects",
                False,
            ),
            "qc_graphs": (f"/data_portal/{profile_id}/qc-graphs", False),
            "basket": (f"/data_portal/{profile_id}/basket", False),
        }
        child_items = []
        for tpl_key, tpl_def in app._page_templates.items():
            if not isinstance(tpl_def, dict):
                continue
            if tpl_def.get("parent") != "home.data_portal.{apero_profile}":
                continue
            suffix = tpl_key.split(".")[-1]
            if "{" in suffix:  # skip {objname} template entries
                continue
            child_url, disabled = child_url_map.get(suffix, ("", False))
            child_items.append((suffix, tpl_key, child_url, disabled))

        child_items.sort(
            key=lambda item: (item[0] in ("fav_objects", "favourites_objects"),)
        )

        for suffix, tpl_id, child_url, disabled in child_items:
            child_id = f"{page_id}.{suffix}"
            child_meta = app._page_template_meta(
                tpl_id,
                apero_profile=profile_id,
            )
            sidebar_tree.append(
                {
                    "id": child_id,
                    "label": child_meta.get("label") or suffix,
                    "icon": child_meta.get("icon", ""),
                    "url": child_url,
                    "depth": 1,
                    "active": active_page_id == child_id,
                    "disabled": disabled,
                }
            )

        if objname:
            obj_id = f"{page_id}.{objname}"
            obj_meta = app._page_template_meta(
                "home.data_portal.{apero_profile}.{objname}",
                apero_profile=profile_id,
                objname=objname,
            )
            sidebar_tree.append(
                {
                    "id": obj_id,
                    "label": f"Object Page: {objname}",
                    "icon": obj_meta.get("icon") or "fa-solid fa-star",
                    "url": f"/data_portal/{profile_id}/{objname}",
                    "depth": 1,
                    "active": active_page_id == obj_id,
                }
            )

    seen = set()
    deduped_tree = []
    for item in sidebar_tree:
        item_id = item.get("id", "")
        if item_id in seen:
            continue
        seen.add(item_id)
        deduped_tree.append(item)
    return deduped_tree
