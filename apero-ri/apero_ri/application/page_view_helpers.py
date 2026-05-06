"""Page view factory helpers for ARIApp."""

from pathlib import Path

import yaml
from apero_ri.core import user_data as ud
from apero_ri.core.auth import (
    get_effective_user,
    get_public_permissions,
    load_admin_health_config,
    user_has_admin_privileges,
)
from apero_ri.core.docs import (
    get_default_version,
    get_doc_content,
    get_versions,
)
from apero_ri.core.permissions import (
    find_full_nav_root,
    get_inherited_groups,
    get_visible_cards,
    has_view_permission,
    is_parent_page,
    load_parameters,
    page_id_to_endpoint,
    page_id_to_template,
    resolve_user_permissions,
)
from flask import flash, redirect, render_template, request, session, url_for


def make_page_view(app, page_id: str, package_dir: Path):
    """Create a page view function from pages.yaml entry."""
    page_def = app.ari_pages[page_id]
    view_perm = str(page_def.get("view-permission", "") or "").strip()
    template = page_id_to_template(page_id, app.ari_pages)
    is_parent = is_parent_page(page_id, app.ari_pages) or template.endswith(
        "/index.html"
    )
    is_doc = app._is_doc_leaf(page_id, app.ari_pages)

    def view_func():
        user_info = get_effective_user(session)
        if user_info:
            perms = resolve_user_permissions(
                user_info["groups"], app.ari_groups
            )
        else:
            perms = get_public_permissions()

        if view_perm and not has_view_permission(
            view_perm, perms
        ):
            flash("You do not have permission to view this page.", "warning")
            return redirect(url_for("login"))

        if page_id.startswith("home.user_portal") and not user_info:
            flash(
                "You must be logged in to access user portal pages.", "warning"
            )
            return redirect(url_for("login"))

        context = {
            "page_id": page_id,
            "page_label": page_def.get("label", ""),
            "page_icon": page_def.get("icon", ""),
            "is_parent": is_parent,
        }

        nav_root = find_full_nav_root(page_id, app.ari_pages)
        if nav_root:
            context.update(
                app._build_sidebar_context(page_id, perms, user_info)
            )
            if app._is_doc_page(page_id):
                version = request.args.get("v")
                context["doc_versions"] = get_versions()
                context["current_version"] = version or get_default_version()

        if is_parent:
            context["cards"] = get_visible_cards(
                page_id,
                perms,
                app.ari_pages,
                logged_in=(user_info is not None),
            )

        if is_doc:
            version = context.get("current_version")
            raw, html, current_ver = get_doc_content(page_id, version)
            doc_short = page_id.split(".")[-1]
            context.update(
                {
                    "doc_html": html,
                    "doc_raw": raw,
                    "current_version": current_ver,
                    "can_edit": f"edit.doc.{doc_short}" in perms,
                    "doc_ref": doc_short,
                }
            )
            return render_template("docs/doc_page.html", **context)

        if page_id == "home":
            context.update(app._build_home_page_context(user_info, perms))

        if page_id == "home.admin_portal.science_groups" and user_info:
            params = load_parameters()
            all_instr = params.get("instruments", {}).get(
                "value", []
            )
            context["instruments"] = [
                i for i in all_instr
                if f"manage.sci_group.{i}" in perms
            ]

        if page_id == "home.admin_portal.async_tasks" and user_info:
            params = load_parameters()
            instruments_entry = params.get("instruments", {})
            if isinstance(instruments_entry, dict):
                all_instr = instruments_entry.get("value", [])
            elif isinstance(instruments_entry, list):
                all_instr = instruments_entry
            else:
                all_instr = []
            context["instruments"] = (
                all_instr if isinstance(all_instr, list) else []
            )

        if page_id == "home.admin_portal.apero_profiles" and user_info:
            params = load_parameters()
            all_instr = params.get("instruments", {}).get("value", [])
            context["instruments"] = all_instr
            all_groups = list(app.ari_groups.keys())
            can_manage = sorted(
                g for g in all_groups if f"manage.group.{g}" in perms
            )
            inherited_map = {}
            for g in all_groups:
                inherited_map[g] = sorted(
                    get_inherited_groups(g, app.ari_groups)
                )
            context["all_groups"] = all_groups
            context["can_manage_groups"] = can_manage
            context["inherited_map"] = inherited_map

            _sci_profiles = {}
            _sci_dir = package_dir / "resources" / "aprofile_instruments"
            if _sci_dir.is_dir():
                for _yf in sorted(_sci_dir.glob("*.yaml")):
                    try:
                        with open(_yf, encoding="utf-8") as _f:
                            _yd = yaml.safe_load(_f) or {}
                        _gen = _yd.get("general", {})
                        _sf = str(_gen.get("science_fiber", "")).strip()
                        _st = _gen.get("science_types", [])
                        if not isinstance(_st, list):
                            _st = [str(_st)] if _st else []
                        _sci_profiles[_yf.name] = {
                            "science_fiber": _sf,
                            "science_types": _st,
                            "params": _yd,
                        }
                    except Exception:
                        pass
            context["sci_profiles"] = _sci_profiles

        if page_id == "home.admin_portal.user_db_access" and user_info:
            health, _, _ = app._get_admin_health(
                user_info=user_info,
                perms=perms,
                force=False,
                allow_async_refresh=True,
            )
            context["user_db_access_health"] = health.get(
                "home.admin_portal.user_db_access",
                {
                    "status": "info",
                    "message": (
                        "Configure group and column access to "
                        "APERO database tables by profile."
                    ),
                },
            )
            try:
                context["user_db_access_health_report"] = (
                    app._build_user_db_access_health_report(user_info)
                )
            except Exception:
                context["user_db_access_health_report"] = {
                    "status": "error",
                    "message": "User DB access health check failed.",
                    "checked_profiles": 0,
                    "warning_profiles": 0,
                    "profiles": [],
                }

        if page_id == "home.data_portal":
            db_ctx = app._build_ri_context(user_info, perms)
            context.update(db_ctx)

        if page_id == "home.user_portal.data_access" and user_info:
            context.update(app._build_user_data_access_context(user_info))

        if page_id == "home.user_portal.support" and user_info:
            context.update(app._build_user_support_context(user_info))

        if page_id == "home.user_portal.links" and user_info:
            context.update(app._build_user_links_context(user_info))

        if page_id == "home.user_portal.notes" and user_info:
            context["notes"] = ud.load_notes(user_info["username"])

        if page_id == "home.user_portal.calendar" and user_info:
            context.update(app._build_user_calendar_context(user_info))

        if page_id == "home.user_portal.todo" and user_info:
            context["todo_items"] = ud.list_todo_items(user_info["username"])

        if page_id == "home.user_portal.api_access" and user_info:
            context.update(app._build_user_api_access_context(user_info))

        if page_id == "home.admin_portal.calendar" and user_info:
            context.update(
                app._build_admin_instrument_context(
                    user_info, perms,
                    'manage.admin.calendar',
                )
            )

        if page_id == "home.admin_portal.links" and user_info:
            context.update(
                app._build_admin_instrument_context(
                    user_info, perms,
                    'manage.admin.links',
                )
            )

        if page_id == "home.admin_portal.email":
            context.update(app._build_admin_email_context(perms))

        if page_id == "home.admin_portal.backup_settings":
            context.update(app._build_admin_backup_context(perms))

        if page_id == "home.astrometrics":
            try:
                from pathlib import Path as _Path
                _astro = _Path(
                    app.args.data_dir or str(_Path.home() / ".ari")
                ) / "apero-assets" / "astrometrics"
                _n = sum(
                    1 for _p in _astro.glob("*.yaml")
                    if not _p.name.startswith(".")
                )
                # also count entries inside status sub-dirs so the
                # page header reflects all (verified+pending+rejected)
                for _sub in ("verified", "pending", "rejected"):
                    _sub_dir = _astro / _sub
                    if _sub_dir.is_dir():
                        _n += sum(
                            1 for _p in _sub_dir.glob("*.yaml")
                            if not _p.name.startswith(".")
                        )
                context["astrometrics_star_count"] = _n
            except Exception:  # noqa: BLE001
                context["astrometrics_star_count"] = None
            # gate the "Rejected object names" tab on monitor perm
            try:
                from apero_ri.application.astrometrics_api_helpers \
                    import _has_monitor_perm as _hmp
                context["astrometrics_can_manage_rejects"] = bool(
                    _hmp(perms, "")
                )
            except Exception:  # noqa: BLE001
                context["astrometrics_can_manage_rejects"] = False
            # gate the "History" tab on the dedicated history perm
            context["astrometrics_can_view_history"] = (
                "manage.astrometrics.history" in (perms or set())
            )
            context['astrometrics_can_manage_history'] = (
                user_has_admin_privileges(
                    list((user_info or {}).get('groups', []))
                )
            )

        if page_id == 'home.monitor_portal.rejection_list':
            try:
                from apero_ri.application \
                    import rejection_list_api_helpers as _rla
                context['rejection_list_tabs'] = _rla.get_rejection_tabs(
                    perms
                )
            except Exception:  # noqa: BLE001
                context['rejection_list_tabs'] = []
            context['rejection_list_can_view_history'] = (
                'manage.rejection_list.history' in (perms or set())
            )
            context['rejection_list_can_manage_history'] = (
                user_has_admin_privileges(
                    list((user_info or {}).get('groups', []))
                )
            )

        if page_id == "home.admin_portal.sshfs_management":
            context.update(app._build_admin_sshfs_context(perms))

        if page_id == "home.admin_portal.manage_instruments":
            context.update(
                app._build_admin_manage_instruments_context(perms)
            )

        if page_id == "home.admin_portal.database_setup":
            context.update(app._build_admin_db_tunnel_context(user_info, perms))

        if page_id == "home.admin_portal.cache_settings":
            context.update(app._build_admin_cache_context(perms))

        if page_id == "home.admin_portal.download_management":
            context.update(
                app._build_admin_download_mgmt_context(perms)
            )

        if page_id == "home.admin_portal.vault":
            context.update(
                app._build_admin_vault_context(perms)
            )

        if page_id in {"home.admin_portal", "home.admin_portal.health_status"}:
            health, updated_at, in_progress = app._get_admin_health(
                user_info=user_info,
                perms=perms,
                force=False,
                allow_async_refresh=True,
            )
            if page_id == "home.admin_portal":
                context["card_health"] = health
            context["admin_health_rows"] = app._build_admin_health_rows(health)
            context["admin_health_meta"] = {
                "updated_at": app._format_utc_datetime(updated_at),
                "in_progress": in_progress,
                "refresh_url": url_for("api_admin_health_update"),
            }
            context["admin_health_config"] = load_admin_health_config()
            context["admin_health_config_urls"] = {
                "get": url_for("api_admin_health_config_get"),
                "save": url_for("api_admin_health_config_save"),
            }

        return render_template(template, **context)

    view_func.__name__ = page_id_to_endpoint(page_id)
    return view_func
