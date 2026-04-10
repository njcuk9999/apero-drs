"""Data Portal view helper functions for ARIApp."""

from pathlib import Path

from apero_ri.application import instrument_color_helpers
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
    get_public_permissions,
)
from apero_ri.core.object_funcs import (
    load_object_ftable_rows,
    load_object_htable_rows,
    load_object_preset,
    load_object_table_row,
)
from apero_ri.core.permissions import resolve_user_permissions
from flask import (
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def ri_profile_view(app, profile_id):
    """View function for dynamic data portal profile sub-pages."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    card_url_map = {
        "object_table": f"/data_portal/{profile_id}/object-table",
        "obs_table": f"/data_portal/{profile_id}/observation-table",
        "query_db": f"/data_portal/{profile_id}/query-db",
        "fav_objects": f"/data_portal/{profile_id}/fav-objects",
        "favourites_objects": f"/data_portal/{profile_id}/fav-objects",
        "qc_graphs": f"/data_portal/{profile_id}/qc-graphs",
        "basket": f"/data_portal/{profile_id}/basket",
    }
    card_desc_map = {
        "object_table": "Browse and search astrophysical objects "
        "in this reduction profile.",
        "obs_table": "View night-by-night observations "
        "and their reduction status.",
        "query_db": "Run custom queries against the "
        "reduction database tables.",
        "fav_objects": "Manage your starred objects and open "
        "their object pages quickly.",
        "favourites_objects": "Manage your starred objects and open "
        "their object pages quickly.",
        "qc_graphs": "Interactive plots of quality control "
        "metrics over time.",
        "basket": "Collect and download files from this " "reduction profile.",
    }
    section_cards = []
    for tpl_key, tpl_def in app._page_templates.items():
        if not isinstance(tpl_def, dict):
            continue
        if tpl_def.get("parent") != "home.data_portal.{apero_profile}":
            continue
        suffix = tpl_key.split(".")[-1]
        if "{" in suffix:
            continue
        card = {
            "key": suffix,
            "label": tpl_def.get("label", suffix),
            "icon": tpl_def.get("icon", ""),
            "url": card_url_map.get(suffix, ""),
            "description": card_desc_map.get(suffix, ""),
        }
        section_cards.append(card)

    section_cards.sort(
        key=lambda card: (
            card.get("key") in ("fav_objects", "favourites_objects"),
        )
    )

    context = {
        "page_id": page_id,
        "page_label": profile_id,
        "page_icon": "fa-solid fa-laptop-code",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "section_cards": section_cards,
        "health_url": "/api/ri/profile-health",
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
    }

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )
    context["sidebar_tree"] = sidebar_tree

    return render_template("data_portal/profile.html", **context)


def ri_object_page_view(app, profile_id, objname):
    """Serve placeholder page for a specific object within a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_tpl_id = "home.data_portal.{apero_profile}.{objname}"
    page_tpl = app._page_templates.get(page_tpl_id, {})
    label_tpl = str(page_tpl.get("label", "{apero profile}: {objname}"))
    page_label = label_tpl.replace("{apero profile}", profile_id).replace(
        "{objname}", objname
    )
    page_icon = page_tpl.get("icon", "fa-solid fa-star")

    page_id = f"home.data_portal.{profile_id}.{objname}"

    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
        objname=objname,
    )

    finder_cached = False
    try:
        from apero_ri.core.plot_cache import (
            _db_fingerprint_matches,
            _load_meta,
            _profile_dir,
            get_finder_cached,
            is_cache_enabled,
            load_cache_config,
            resolve_cache_root,
        )

        base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
        cfg = load_cache_config(base_dir)
        if is_cache_enabled(cfg=cfg):
            cache_root = resolve_cache_root(base_dir, cfg)
            profile_data = profile.get("data") or {}
            pdir = _profile_dir(cache_root, profile["instrument"], profile_id)
            meta = _load_meta(pdir)
            db_upd = profile_data.get("database-update", {})
            if (
                isinstance(db_upd, dict)
                and db_upd
                and _db_fingerprint_matches(meta, db_upd)
            ):
                fc_hit = get_finder_cached(
                    cache_root, profile["instrument"], profile_id, objname
                )
                finder_cached = fc_hit is not None
    except Exception:
        pass

    context = {
        "page_id": page_id,
        "page_label": page_label,
        "page_icon": page_icon,
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "objname": objname,
        "api_url": "/api/data-portal/object-page",
        "finder_chart_cached": finder_cached,
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/object_page.html", **context)


def ri_object_table_view(app, profile_id):
    """Serve the astrophysical object table page for a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.object_table"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Object Table",
        "page_icon": "fa-solid fa-star",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "api_url": "/api/data-portal/object-table",
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/object_table.html", **context)


def ri_obs_table_view(app, profile_id):
    """Serve the observation table page for a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.obs_table"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Observation Table",
        "page_icon": "fa-solid fa-binoculars",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "api_url": "/api/data-portal/obs-table",
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/obs_table.html", **context)


def ri_qc_graphs_view(app, profile_id):
    """Serve interactive quality-control graphs for a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.qc_graphs"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    from apero_ri.plots.plots_qc import build_qc_plot_payload

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))

    from apero_ri.core.plot_cache import check_and_serve

    profile_data = profile.get("data") or {}
    cached_qc = check_and_serve(
        base_dir,
        profile["instrument"],
        profile_id,
        "qc_graphs",
        "payload",
        aparams=profile_data,
    )
    if cached_qc is not None:
        qc_payload = cached_qc
    else:
        qc_payload = build_qc_plot_payload(base_dir=base_dir, profile=profile)
        try:
            from apero_ri.core.plot_cache import (
                _load_meta,
                _profile_dir,
                _save_meta,
                load_cache_config,
                put_cached,
                resolve_cache_root,
            )

            cfg = load_cache_config(base_dir)
            if cfg.get("enabled"):
                cache_root = resolve_cache_root(base_dir, cfg)
                put_cached(
                    cache_root,
                    profile["instrument"],
                    profile_id,
                    "qc_graphs",
                    "payload",
                    qc_payload,
                )
                pdir = _profile_dir(
                    cache_root, profile["instrument"], profile_id
                )
                meta = _load_meta(pdir)
                db_upd = profile_data.get("database-update", {})
                if isinstance(db_upd, dict) and db_upd:
                    meta["db_updates"] = dict(db_upd)
                from datetime import datetime as _dt
                from datetime import timezone as _tz

                meta["last_cached"] = _dt.now(_tz.utc).isoformat()
                _save_meta(pdir, meta)
        except Exception:
            pass

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Quality Control Graphs",
        "page_icon": "fa-solid fa-chart-line",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "qc_payload": qc_payload,
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/qc_graphs.html", **context)


def ri_qc_graphs_max_view(app, profile_id, section, metric_key, view_key):
    """Serve a standalone maximized QC plot page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    from apero_ri.plots.plots_qc import build_qc_single_plot_payload

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    plot_payload = build_qc_single_plot_payload(
        base_dir=base_dir,
        profile=profile,
        section=section,
        metric_key=metric_key,
        view_key=view_key,
    )

    context = {
        "profile": profile,
        "plot_payload": plot_payload,
        "return_url": url_for("ri_qc_graphs", profile_id=profile_id),
    }
    return render_template("data_portal/qc_graphs_max.html", **context)


def ri_query_db_view(app, profile_id):
    """Serve the database query explorer page for a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.query_db"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    query_presets = app._load_query_db_presets(profile)

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Database Query",
        "page_icon": "fa-solid fa-terminal",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "schema_api_url": "/api/data-portal/query-db/schema",
        "run_api_url": "/api/data-portal/query-db/run",
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
        "query_presets": query_presets,
    }
    return render_template("data_portal/query_db.html", **context)


def ri_basket_view(app, profile_id):
    """Serve the download basket page for a profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.basket"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Download Basket",
        "page_icon": "fa-solid fa-basket-shopping",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/basket.html", **context)


def ri_favourites_objects_view(app, profile_id):
    """Serve per-profile favourite and last-viewed object cards."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break

    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    page_id = f"home.data_portal.{profile_id}.fav_objects"
    colors = app._instrument_colors()
    color = colors.get(
        profile["instrument"],
        instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
    )

    username = ""
    if isinstance(user_info, dict):
        username = str(user_info.get("username", "")).strip()
    from apero_ri.core import user_data as ud

    fav_payload = ud.get_profile_favourite_objects(username, profile_id)
    favourite_objects = fav_payload.get("favourites", [])
    if not isinstance(favourite_objects, list):
        favourite_objects = []
    favourite_objects = [
        str(objname).strip()
        for objname in favourite_objects
        if str(objname).strip()
    ]
    last_object = str(fav_payload.get("last_object", "")).strip()
    last_object_url = ""
    if last_object:
        last_object_url = url_for(
            "ri_object_page",
            profile_id=profile["profile_id"],
            objname=last_object,
        )

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id=page_id,
        user_permissions=perms,
        user_info=user_info,
        current_profile_id=profile_id,
    )

    context = {
        "page_id": page_id,
        "page_label": f"{profile_id}: Favourite Objects",
        "page_icon": "fa-solid fa-star",
        "is_parent": False,
        "profile": profile,
        "profile_color": color,
        "favourite_objects": favourite_objects,
        "last_object": last_object,
        "last_object_url": last_object_url,
        "remove_api_url": "/api/user/favourite-objects/remove",
        "reorder_api_url": "/api/user/favourite-objects/reorder",
        "sidebar_root": "home.data_portal",
        "sidebar_label": "Data Portal",
        "sidebar_icon": "fa-solid fa-database",
        "sidebar_url": "/data_portal",
        "sidebar_tree": sidebar_tree,
    }
    return render_template("data_portal/fav_objects.html", **context)


def ri_object_plot_max_view(app, profile_id, objname, plot_key):
    """Serve a standalone maximized object plot page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        flash("You do not have permission to view this page.", "warning")
        return redirect(url_for("login"))

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        flash("Profile not found or access denied.", "warning")
        return redirect(url_for("home_data_portal"))

    vsys_ms = None
    vsys_ms_str = request.args.get("vsys_ms", "").strip()
    if vsys_ms_str:
        try:
            vsys_ms = float(vsys_ms_str)
        except ValueError:
            pass

    ccf_mjd_start = None
    ccf_mjd_start_str = request.args.get("ccf_mjd_start", "").strip()
    if ccf_mjd_start_str:
        try:
            ccf_mjd_start = float(ccf_mjd_start_str)
        except ValueError:
            pass

    ccf_mjd_end = None
    ccf_mjd_end_str = request.args.get("ccf_mjd_end", "").strip()
    if ccf_mjd_end_str:
        try:
            ccf_mjd_end = float(ccf_mjd_end_str)
        except ValueError:
            pass
    ccf_nobs = 100
    ccf_nobs_str = request.args.get("ccf_nobs", "").strip()
    if ccf_nobs_str:
        try:
            ccf_nobs = max(1, min(1000, int(float(ccf_nobs_str))))
        except ValueError:
            ccf_nobs = 100
    if (
        ccf_mjd_start is not None
        and ccf_mjd_end is not None
        and ccf_mjd_start > ccf_mjd_end
    ):
        ccf_mjd_start, ccf_mjd_end = ccf_mjd_end, ccf_mjd_start

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    profile_data = profile.get("data") or {}
    instrument_profile_file = str(
        profile_data.get("APERO_INSTRUMENT_PROFILE", "")
        or profile_data.get("apero_instrument_profile", "")
        or ""
    ).strip()

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    objects_dir = base_dir / "tasks" / instrument / profile_id / "objects"

    htable_rows = load_object_htable_rows(objects_dir, objname)
    preset = load_object_preset(instrument_profile_file)
    obj_props = load_object_table_row(objects_dir, objname)

    _ftable_ext = load_object_ftable_rows(objects_dir, objname, "ext")
    _ftable_tcorr = load_object_ftable_rows(objects_dir, objname, "tcorr")
    _ftable_ccf = load_object_ftable_rows(objects_dir, objname, "ccf")
    _ftable_lbl = load_object_ftable_rows(objects_dir, objname, "lbl_rdb")

    htable_rows, ftables = app._filter_plot_rows(
        htable_rows,
        {
            "ext": _ftable_ext,
            "tcorr": _ftable_tcorr,
            "ccf": _ftable_ccf,
            "lbl_rdb": _ftable_lbl,
        },
        accessible_run_ids,
    )
    _ftable_ext = ftables["ext"]
    _ftable_tcorr = ftables["tcorr"]
    _ftable_ccf = ftables["ccf"]
    _ftable_lbl = ftables["lbl_rdb"]

    from apero_ri.plots.plot_objects import (
        build_berv_plot_components,
        build_ccf_profile_plot_components,
        build_ccf_rv_plot_components,
        build_snr_plot_components,
        build_spec_plot_components,
        build_ts_airmass_plot_components,
        build_ts_snr_plot_components,
    )

    safe_key = str(plot_key or "").strip().lower()
    if safe_key == "snr":
        plot_payload = build_snr_plot_components(htable_rows, preset)
        display_name = "SNR vs Time"
    elif safe_key == "berv":
        plot_payload = build_berv_plot_components(
            htable_rows, vsys_ms, preset, obj_props=obj_props
        )
        display_name = "BERV Coverage"
    elif safe_key == "spec":
        path_red = str(
            app._profile_get_path(profile_data, "PATH_RED", "") or ""
        )
        paths = {"PATH_RED": path_red}
        plot_payload = build_spec_plot_components(
            htable_rows,
            _ftable_ext,
            _ftable_tcorr,
            paths,
            preset,
            maximize=True,
        )
        display_name = "Median Spectrum"
    elif safe_key == "ccf_rv":
        plot_payload = build_ccf_rv_plot_components(
            htable_rows,
            preset,
        )
        display_name = "CCF RV vs Time"
    elif safe_key in {"ccf", "ccf_profile"}:
        path_red = str(
            app._profile_get_path(profile_data, "PATH_RED", "") or ""
        )
        paths = {"PATH_RED": path_red}
        plot_payload = build_ccf_profile_plot_components(
            htable_rows,
            _ftable_ccf,
            paths,
            preset,
            ccf_mjd_start=ccf_mjd_start,
            ccf_mjd_end=ccf_mjd_end,
            ccf_nobs=ccf_nobs,
        )
        display_name = "Median CCF Profile"
    elif safe_key == "ts_snr":
        plot_payload = build_ts_snr_plot_components(
            htable_rows, _ftable_ext, preset
        )
        display_name = "SNR per Night"
    elif safe_key == "ts_airmass":
        plot_payload = build_ts_airmass_plot_components(
            htable_rows, _ftable_ext, preset
        )
        display_name = "Airmass per Night"
    elif safe_key == "lbl":
        from apero_ri.plots.plot_objects import build_lbl_plot_components

        lbl_file = str(request.args.get("lbl_file", "")).strip()
        path_lbl = str(
            app._profile_get_path(profile_data, "PATH_LBL", "") or ""
        )
        plot_payload = build_lbl_plot_components(
            _ftable_lbl, path_lbl, preset, lbl_file
        )
        display_name = (
            f"LBL Velocity - {lbl_file}" if lbl_file else "LBL Velocity"
        )
    elif safe_key == "finder":
        band_idx_str = str(request.args.get("band_idx", "0")).strip()
        try:
            band_idx = int(band_idx_str)
        except ValueError:
            band_idx = 0
        plot_payload = app._build_finder_max_payload(
            profile, objname, obj_props, preset, band_idx
        )
        display_name = "Finder Chart"
    elif safe_key.startswith("debug_"):
        debug_plot_key = safe_key[6:]
        from apero_ri.plots.plot_debug import (
            DEBUG_PLOT_DEFS,
            generate_single_debug_plot,
        )

        paths = None
        if debug_plot_key == "tcorr_map":
            path_red = str(
                app._profile_get_path(profile_data, "PATH_RED", "") or ""
            )
            paths = {"PATH_RED": path_red}
        plot_payload = generate_single_debug_plot(
            debug_plot_key,
            htable_rows,
            objname,
            preset,
            _ftable_tcorr if debug_plot_key == "tcorr_map" else None,
            paths,
        )
        defn = DEBUG_PLOT_DEFS.get(debug_plot_key, {})
        display_name = defn.get("title", debug_plot_key)
    else:
        plot_payload = {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": f"Unknown plot key: {plot_key}",
        }
        display_name = str(plot_key)

    return_url = url_for(
        "ri_object_page",
        profile_id=profile_id,
        objname=objname,
    )
    context = {
        "profile": profile,
        "objname": objname,
        "plot_key": safe_key,
        "display_name": display_name,
        "plot_payload": plot_payload,
        "return_url": return_url,
    }
    return render_template("data_portal/object_plot_max.html", **context)
