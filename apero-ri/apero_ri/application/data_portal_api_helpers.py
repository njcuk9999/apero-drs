"""Data Portal API helper functions for ARIApp."""

import json as _json
import multiprocessing as mp
import queue
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_public_permissions,
    load_apero_profiles,
)
from apero_ri.core.object_funcs import (
    build_object_page_stats,
    load_object_ftable_rows,
    load_object_htable_rows,
    load_object_preset,
    load_object_table_row,
)
from apero_ri.core.permissions import resolve_user_permissions
from flask import (
    Response,
    jsonify,
    request,
    send_file,
    stream_with_context,
)


# In-process TTL cache for api_object_page responses. Keyed by
# (profile_id, objname_lower, rid_tag); value is
# (expires_at_epoch, payload_dict). Page data changes only when
# the underlying object_table.json or astrometric YAMLs change,
# so a 60-second TTL is safe and dramatically speeds up rapid
# back-and-forth navigation between objects.
_OBJECT_PAGE_CACHE = {}
_OBJECT_PAGE_CACHE_LOCK = threading.Lock()
_OBJECT_PAGE_CACHE_TTL = 60.0  # seconds


def _run_tessilator_stream_worker(
    objname,
    cache_root,
    instrument,
    aliases,
    log_q,
    result_q,
):
    """Run tessilator in an isolated process for clean log streaming."""
    try:
        from apero_ri.core.run_tessilator import run_tessilator

        result = run_tessilator(
            objname=objname,
            cache_root=cache_root,
            instrument=instrument,
            aliases=aliases,
            log_queue=log_q,
        )
    except Exception as exc:
        result = dict(
            success=False,
            error=str(exc),
        )
    try:
        result_q.put(result)
    finally:
        log_q.put(None)


def _object_page_cache_get(key):
    with _OBJECT_PAGE_CACHE_LOCK:
        hit = _OBJECT_PAGE_CACHE.get(key)
        if hit is None:
            return None
        expires_at, payload = hit
        if expires_at < time.time():
            _OBJECT_PAGE_CACHE.pop(key, None)
            return None
        return payload


def _set_request_theme_from_args() -> str:
    """Read ?theme=... from the request and set the thread-local
    Bokeh theme so every plot built within this request uses it.

    Returns the normalised theme string ('default'|'light'|'dark') so
    callers can fold it into cache keys (otherwise dark/light requests
    would serve each other's cached white-background plots).
    """
    try:
        from apero_ri.plots.bokeh_theme import (
            set_request_theme, normalise_theme,
        )
    except Exception:  # noqa: BLE001
        return "default"
    raw = request.args.get("theme", "default")
    theme = normalise_theme(raw)
    try:
        set_request_theme(theme)
    except Exception:  # noqa: BLE001
        pass
    return theme


def _object_page_cache_set(key, payload):
    with _OBJECT_PAGE_CACHE_LOCK:
        # Bound the cache (LRU-style by simple eviction)
        if len(_OBJECT_PAGE_CACHE) > 256:
            _OBJECT_PAGE_CACHE.clear()
        _OBJECT_PAGE_CACHE[key] = (
            time.time() + _OBJECT_PAGE_CACHE_TTL, payload)


def api_ri_profile_health(app):
    """Run database and path health checks for a profile."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    profile_id = data.get("profile_id", "").strip()
    if not profile_id:
        return jsonify(success=False, error="Missing profile_id"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Access denied"), 403

    cfg = profile["data"]
    db_result = app._validate_profile_database(cfg)

    path_keys = [
        "PATH_RAW",
        "PATH_PP",
        "PATH_RED",
        "PATH_CALIB",
        "PATH_OUT",
        "PATH_TELLU",
        "PATH_LOG",
        "PATH_LBL",
        "PATH_CHECK",
        "PATH_OTHER",
    ]
    path_results = {}
    all_paths_ok = True
    for key in path_keys:
        val = app._profile_get_path(cfg, key, "")
        exists = bool(val) and Path(val).is_dir()
        path_results[key] = exists
        if not exists:
            all_paths_ok = False

    return jsonify(
        success=True,
        database={
            "ok": db_result["valid"],
            "error": db_result.get("error", ""),
        },
        paths={"ok": all_paths_ok, "details": path_results},
    )


def api_debug_plots(app):
    """Generate debug plots on demand (called via AJAX)."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()
    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    # Apply requested theme to every Bokeh figure built in this request
    # and fold the theme into the cache key so dark/light don't pollute
    # each other's cached payloads (a cached light plot served on the
    # dark theme is the most common cause of "white background").
    theme = _set_request_theme_from_args()

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    force_regen = bool(str(request.args.get("_ts", "")).strip())
    if not profile_id or not objname:
        return (
            jsonify(success=False, error="Missing profile_id or objname"),
            400,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

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

    from apero_ri.core.plot_cache import check_and_serve

    rid_tag = app._rid_cache_tag(accessible_run_ids)
    cache_key = f"{objname}__{rid_tag}__{theme}"
    if not force_regen:
        cached = check_and_serve(
            base_dir,
            instrument,
            profile_id,
            "debug_plots",
            cache_key,
            aparams=profile_data,
        )
        if cached is not None:
            return jsonify(**cached)

    htable_rows = load_object_htable_rows(objects_dir, objname)
    preset = load_object_preset(instrument_profile_file)

    ftable_tcorr_rows = load_object_ftable_rows(objects_dir, objname, "tcorr")

    htable_rows, ftables = app._filter_plot_rows(
        htable_rows,
        {"tcorr": ftable_tcorr_rows},
        accessible_run_ids,
    )
    ftable_tcorr_rows = ftables["tcorr"]

    path_red = str(app._profile_get_path(profile_data, "PATH_RED", "") or "")
    paths = {"PATH_RED": path_red} if path_red else None

    from apero_ri.plots.plot_debug import generate_debug_plots

    _t0_debug = time.time()
    result = generate_debug_plots(
        htable_rows, objname, preset, ftable_tcorr_rows, paths
    )
    _gen_time_debug = time.time() - _t0_debug
    if isinstance(result, dict):
        result["updated_at"] = datetime.now(timezone.utc).isoformat()

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
                instrument,
                profile_id,
                "debug_plots",
                cache_key,
                result,
                _gen_time_debug,
            )
            pdir = _profile_dir(cache_root, instrument, profile_id)
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

    return jsonify(**result)


def api_tcorr_map_generate(app):
    """Generate the telluric correction map on demand (called via AJAX)."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()
    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    # Pick up theme so the matplotlib telluric map renders with the
    # right palette (see plot_debug._render_mpl_to_b64).
    _set_request_theme_from_args()

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    if not profile_id or not objname:
        return (
            jsonify(success=False, error="Missing profile_id or objname"),
            400,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(
        user_info, instrument
    )

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
    ftable_tcorr_rows = load_object_ftable_rows(objects_dir, objname, "tcorr")

    htable_rows, ftables = app._filter_plot_rows(
        htable_rows,
        {"tcorr": ftable_tcorr_rows},
        accessible_run_ids,
    )
    ftable_tcorr_rows = ftables["tcorr"]

    path_red = str(
        app._profile_get_path(profile_data, "PATH_RED", "") or ""
    )
    paths = {"PATH_RED": path_red} if path_red else {}

    from apero_ri.plots.plot_debug import generate_single_debug_plot

    result = generate_single_debug_plot(
        "tcorr_map",
        htable_rows,
        objname,
        preset=preset,
        ftable_tcorr_rows=ftable_tcorr_rows,
        paths=paths,
    )
    result["success"] = result.get("has_plot", False)
    return jsonify(**result)


def api_object_lbl_plots(app):
    """Return Bokeh JSON plot payloads for all LBL flavors of an object."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    theme = _set_request_theme_from_args()

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="Missing profile_id or objname",
            ),
            400,
        )
    force_regen = bool(str(request.args.get("_ts", "")).strip())

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

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

    from apero_ri.core.plot_cache import check_and_serve

    rid_tag = app._rid_cache_tag(accessible_run_ids)
    cache_key = f"{objname}__{rid_tag}__{theme}"
    if not force_regen:
        cached = check_and_serve(
            base_dir,
            instrument,
            profile_id,
            "lbl_plots",
            cache_key,
            aparams=profile_data,
        )
        if cached is not None:
            return jsonify(**cached)

    preset = load_object_preset(instrument_profile_file)
    path_lbl = str(app._profile_get_path(profile_data, "PATH_LBL", "") or "")

    ftable_lbl_rdb_rows = load_object_ftable_rows(
        objects_dir, objname, "lbl_rdb"
    )
    from apero_ri.core.basket_funcs import filter_accessible_rows

    ftable_lbl_rdb_rows = filter_accessible_rows(
        ftable_lbl_rdb_rows, accessible_run_ids
    )

    htable_rows = load_object_htable_rows(objects_dir, objname)
    # Note: htable_rows are indexed by IDENTIFIER (not KW_RUN_ID) so we do
    # NOT filter them by accessible_run_ids; they are already scoped to the
    # object and are used only for supplemental SNR annotation.

    from apero_ri.plots.plot_objects import build_lbl_plots_json

    _t0_lbl = time.time()
    try:
        plots = build_lbl_plots_json(
            ftable_lbl_rdb_rows,
            path_lbl,
            preset,
            htable_rows=htable_rows,
            objname=objname,
        )
    except Exception:
        plots = {}
    _gen_time_lbl = time.time() - _t0_lbl

    result = dict(
        success=True,
        plots=plots,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    try:
        from apero_ri.core.plot_cache import (
            load_cache_config,
            put_cached,
            resolve_cache_root,
        )

        cfg = load_cache_config(base_dir)
        if cfg.get("enabled"):
            cache_root = resolve_cache_root(base_dir, cfg)
            put_cached(
                cache_root,
                instrument,
                profile_id,
                "lbl_plots",
                cache_key,
                result,
                _gen_time_lbl,
            )
    except Exception:
        pass

    return jsonify(**result)


def api_filename_plot(app):
    """Return a Bokeh JSON plot for a single file (filename-click feature)."""
    from apero_ri.base.base import BLOCK_KIND as block_kind_map
    from apero_ri.plots.plots_filename import build_filename_plot_json

    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    block_kind = request.args.get("block_kind", "").strip().lower()
    obs_dir = request.args.get("obs_dir", "").strip()
    filename = request.args.get("filename", "").strip()
    kw_output = request.args.get("kw_output", "").strip()
    kw_fiber = request.args.get("kw_fiber", "").strip() or "AB"
    kw_run_id = request.args.get("kw_run_id", "").strip()

    if not all([profile_id, block_kind, filename, kw_output]):
        return jsonify(success=False, error="Missing required params"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)
    if kw_run_id and kw_run_id not in accessible_run_ids:
        return (
            jsonify(
                success=False,
                error="Access denied for this run_id",
            ),
            403,
        )

    path_key = block_kind_map.get(block_kind)
    if not path_key:
        return (
            jsonify(
                success=False,
                error=f"Unknown block_kind: {block_kind}",
            ),
            400,
        )

    profile_data = profile.get("data") or {}
    base_path_str = str(
        app._profile_get_path(profile_data, path_key, "") or ""
    ).strip()
    if not base_path_str:
        return (
            jsonify(
                success=False,
                error=f"No path configured for {path_key}",
            ),
            400,
        )

    try:
        base_path = Path(base_path_str).resolve()
        obs_part = Path(obs_dir.strip("/")) if obs_dir else Path("")
        filepath = (base_path / obs_part / filename).resolve()
        filepath.relative_to(base_path)
    except (ValueError, OSError) as exc:
        return jsonify(success=False, error=f"Path error: {exc}"), 400

    if not filepath.is_file():
        return (
            jsonify(
                success=False,
                has_plot=False,
                message=f"File not found: {filename}",
            ),
            404,
        )

    try:
        result = build_filename_plot_json(filepath, kw_output, kw_fiber)
    except Exception:
        result = {"has_plot": False, "message": "Plot build failed"}
    return jsonify(success=True, **result)


def _resolve_target_context(app, user_info, accessible):
    """Resolve target context from either ``(profile_id, objname)`` or
    ``name=``.

    When ``name=`` is provided the astrometric YAML database is
    consulted via :func:`drs_astrometrics.find_by_name` and the
    user's first accessible profile is used to source the
    instrument-specific finder/TESS configuration.  The cache key
    is the canonical APERO_NAME, so cache entries are shared with
    object-page lookups for the same target.

    :param app: ARIApp instance
    :param user_info: dict or None - the result of ``_get_api_user``
    :param accessible: list of accessible profile dicts
    :return: tuple ``(ok, payload)`` where ``ok`` is bool; on
             success ``payload`` is a dict with keys
             ``instrument``, ``profile_id``, ``profile``,
             ``profile_data``, ``objname``, ``obj_props``,
             ``preset``, ``yaml_entry`` (None for legacy mode).
             On failure ``payload`` is a Flask response tuple.
    """
    name_arg = (request.args.get('name') or '').strip()
    profile_id = (request.args.get('profile_id') or '').strip()
    objname = (request.args.get('objname') or '').strip()

    if name_arg:
        # YAML-resolved mode (resolve target page).  Uses the
        # caller's first accessible profile as the source of the
        # instrument-specific finder/TESS configuration.
        from apero.core import drs_astrometrics as dra
        from apero_ri.core.yaml_obj_props import yaml_to_obj_props

        base_dir = Path(
            app.args.data_dir or str(Path.home() / '.ari'))
        astrom_dir = (
            base_dir / 'apero-assets' / 'astrometrics')
        try:
            entry = dra.find_by_name(str(astrom_dir), name_arg)
        except Exception as exc:  # noqa: BLE001
            return False, (jsonify(
                success=False,
                error=f'Astrometric lookup failed: {exc}'), 500)
        if not entry:
            return False, (jsonify(
                success=False,
                error=f'No astrometric entry for {name_arg!r}'),
                404)
        profiles = list(accessible or [])
        if not profiles:
            # For public astrometrics usage (logged-out users), pick a
            # deterministic fallback profile to source instrument presets.
            all_profiles = load_apero_profiles(hydrate=True)
            for inst in sorted(all_profiles.keys()):
                inst_profiles = all_profiles.get(inst) or {}
                for pid in sorted(inst_profiles.keys()):
                    pdata = inst_profiles.get(pid) or {}
                    profiles.append(
                        dict(
                            profile_id=pid,
                            instrument=inst,
                            data=pdata,
                        )
                    )
            if not profiles:
                return False, (
                    jsonify(
                        success=False,
                        error='No APERO profiles available',
                    ),
                    404,
                )
        profile = profiles[0]
        profile_id = profile['profile_id']
        instrument = profile['instrument']
        profile_data = profile.get('data') or {}
        instrument_profile_file = str(
            profile_data.get('APERO_INSTRUMENT_PROFILE', '')
            or profile_data.get('apero_instrument_profile', '')
            or '').strip()
        preset = load_object_preset(instrument_profile_file)
        obj_props = yaml_to_obj_props(entry)
        objname = (entry.get('APERO_NAME')
                   or obj_props.get('OBJNAME') or name_arg)
        return True, dict(
            instrument=instrument,
            profile_id=profile_id,
            profile=profile,
            profile_data=profile_data,
            objname=objname,
            obj_props=obj_props,
            preset=preset,
            yaml_entry=entry,
        )

    # Legacy (object-page) mode
    if not profile_id or not objname:
        return False, (jsonify(
            success=False,
            error='Missing profile_id/objname or name'), 400)
    profile = next(
        (p for p in accessible
         if p['profile_id'] == profile_id), None)
    if not profile:
        return False, (jsonify(
            success=False, error='Profile not found'), 404)
    instrument = profile['instrument']
    profile_data = profile.get('data') or {}
    instrument_profile_file = str(
        profile_data.get('APERO_INSTRUMENT_PROFILE', '')
        or profile_data.get('apero_instrument_profile', '')
        or '').strip()
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari'))
    objects_dir = (base_dir / 'tasks' / instrument
                   / profile_id / 'objects')
    obj_props = load_object_table_row(objects_dir, objname)
    preset = load_object_preset(instrument_profile_file)
    return True, dict(
        instrument=instrument,
        profile_id=profile_id,
        profile=profile,
        profile_data=profile_data,
        objname=objname,
        obj_props=obj_props,
        preset=preset,
        yaml_entry=None,
    )


def api_finder_chart(app):
    """Generate finder charts on demand (called via AJAX)."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()
    name_mode = bool((request.args.get('name') or '').strip())
    if "view.data_portal" not in perms and not name_mode:
        return jsonify(success=False, error="Unauthorized"), 401

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    ok, ctx = _resolve_target_context(app, user_info, accessible)
    if not ok:
        return ctx
    instrument = ctx['instrument']
    profile_id = ctx['profile_id']
    profile_data = ctx['profile_data']
    objname = ctx['objname']
    obj_props = ctx['obj_props']
    preset = ctx['preset']
    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))
    force_regen = bool(str(request.args.get("_ts", "")).strip())

    from apero_ri.core.plot_cache import (
        _db_fingerprint_matches,
        _load_meta,
        _profile_dir,
        _save_meta,
        get_finder_cached,
        is_cache_enabled,
        load_cache_config,
        put_finder_cached,
        resolve_cache_root,
    )

    cfg = load_cache_config(base_dir)
    if is_cache_enabled(cfg=cfg) and not force_regen:
        cache_root = resolve_cache_root(base_dir, cfg)
        pdir = _profile_dir(cache_root, instrument, profile_id)
        meta = _load_meta(pdir)
        db_upd = profile_data.get("database-update", {})
        if (
            isinstance(db_upd, dict)
            and db_upd
            and _db_fingerprint_matches(meta, db_upd)
        ):
            hit = get_finder_cached(cache_root, instrument, profile_id, objname)
            if hit is not None:
                return jsonify(**hit)

    from apero_ri.core.object_finder import generate_finder_charts

    result = generate_finder_charts(obj_props, preset)

    try:
        if is_cache_enabled(cfg=cfg):
            cache_root = resolve_cache_root(base_dir, cfg)
            put_finder_cached(
                cache_root, instrument, profile_id, objname, result
            )
            pdir = _profile_dir(cache_root, instrument, profile_id)
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

    return jsonify(**result)


def api_finder_chart_stream(app):
    """SSE endpoint: stream finder chart generation live.

    Each event is a JSON object with a ``type`` field:
      - ``log``   - a line of console output
      - ``done``  - final result (images, bands, ...)
      - ``error`` - something went wrong
    """
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    name_mode = bool((request.args.get('name') or '').strip())
    if 'view.data_portal' not in perms and not name_mode:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    ok, ctx = _resolve_target_context(app, user_info, accessible)
    if not ok:
        return ctx
    instrument = ctx['instrument']
    profile_id = ctx['profile_id']
    profile_data = ctx['profile_data']
    objname = ctx['objname']
    obj_props = ctx['obj_props']
    preset = ctx['preset']
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari'))

    from apero_ri.core.plot_cache import (
        _db_fingerprint_matches,
        _load_meta,
        _profile_dir,
        _save_meta,
        get_finder_cached,
        is_cache_enabled,
        load_cache_config,
        put_finder_cached,
        resolve_cache_root,
    )

    cfg = load_cache_config(base_dir)
    # if cached, return instantly as a single SSE event
    force = bool(
        str(request.args.get('_ts', '')).strip()
    )
    if not force and is_cache_enabled(cfg=cfg):
        cache_root = resolve_cache_root(base_dir, cfg)
        pdir = _profile_dir(
            cache_root, instrument, profile_id
        )
        meta = _load_meta(pdir)
        db_upd = profile_data.get(
            'database-update', {}
        )
        if (
            isinstance(db_upd, dict)
            and db_upd
            and _db_fingerprint_matches(meta, db_upd)
        ):
            hit = get_finder_cached(
                cache_root, instrument,
                profile_id, objname,
            )
            if hit is not None:
                payload = _json.dumps(
                    dict(type='done', result=hit)
                )

                def _cached():
                    yield f'data: {payload}\n\n'

                return Response(
                    stream_with_context(_cached()),
                    mimetype='text/event-stream',
                )

    # shared queue for real-time log lines
    log_q = queue.Queue()
    # holder for result from the background thread
    result_holder = [None]

    def _worker():
        from apero_ri.core.object_finder import (
            generate_finder_charts,
        )
        try:
            result_holder[0] = generate_finder_charts(
                obj_props, preset,
                log_func=lambda msg: log_q.put(msg),
            )
        except Exception as exc:
            result_holder[0] = dict(
                success=False,
                error=str(exc),
            )
        finally:
            log_q.put(None)  # sentinel

    t = threading.Thread(
        target=_worker, daemon=True
    )
    t.start()

    def _generate():
        while True:
            try:
                item = log_q.get(timeout=30)
            except queue.Empty:
                # keep-alive comment
                yield ': keepalive\n\n'
                continue
            if item is None:
                break
            evt = _json.dumps(
                dict(type='log', text=item)
            )
            yield f'data: {evt}\n\n'

        # final result
        result = result_holder[0]
        if result is None:
            result = dict(
                success=False,
                error='No result from finder chart.',
            )
        # cache the result
        try:
            if is_cache_enabled(cfg=cfg):
                cache_root = resolve_cache_root(
                    base_dir, cfg
                )
                put_finder_cached(
                    cache_root, instrument,
                    profile_id, objname, result,
                )
                pdir = _profile_dir(
                    cache_root, instrument,
                    profile_id,
                )
                meta = _load_meta(pdir)
                db_upd = profile_data.get(
                    'database-update', {}
                )
                if isinstance(db_upd, dict) and db_upd:
                    meta['db_updates'] = dict(db_upd)
                from datetime import datetime as _dt
                from datetime import timezone as _tz
                meta['last_cached'] = (
                    _dt.now(_tz.utc).isoformat()
                )
                _save_meta(pdir, meta)
        except Exception:
            pass

        if result.get('success'):
            payload = _json.dumps(
                dict(type='done', result=result)
            )
        else:
            payload = _json.dumps(dict(
                type='error',
                error=result.get('error', 'Failed'),
            ))
        yield f'data: {payload}\n\n'

    return Response(
        stream_with_context(_generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )


def api_object_table(app):
    """Return object table rows for a profile, filtered by science group."""
    import concurrent.futures as _futures
    import json as _json
    import math
    import re

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))

    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    if not profile_id:
        return jsonify(success=False, error="Missing profile_id"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]

    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    tasks_dir = base_dir / "tasks" / instrument
    json_path = tasks_dir / profile_id / "object_table.json"

    if not json_path.exists():
        legacy_path = tasks_dir / f"object_table_{profile_id}.json"
        if legacy_path.exists():
            json_path = legacy_path

    if not json_path.exists():
        return jsonify(
            success=True,
            rows=[],
            columns=[],
            generated_at=None,
            total_rows=0,
            message=(
                "No object table data found. "
                "Run the object table task first."
            ),
        )

    try:
        with open(json_path, encoding="utf-8") as f:
            data = _json.load(f)
    except Exception as exc:
        return jsonify(success=False, error=f"Failed to load data: {exc}"), 500

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    all_rows = data.get("rows", [])
    generated_at = data.get("generated_at") or metadata.get("GENERATED_AT")
    raw_column_meta = metadata.get("COLUMN_META", {})
    if not isinstance(raw_column_meta, dict):
        raw_column_meta = {}

    hidden_by_meta = {
        col
        for col, meta in raw_column_meta.items()
        if isinstance(meta, dict) and bool(meta.get("hidden", False))
    }

    filtered = []
    for row in all_rows:
        raw = str(row.get("RUN_ID", "") or "")
        row_rids = {r.strip() for r in raw.split(",") if r.strip()}
        if row_rids & accessible_run_ids:
            # Copy raw run-id list into user-visible column
            row["Run ID"] = raw
            filtered.append(row)

    find_only = str(request.args.get("find_only", "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    name_query = str(request.args.get("name_query", "") or "").strip()

    ra_raw = str(request.args.get("ra", "") or "").strip()
    dec_raw = str(request.args.get("dec", "") or "").strip()
    sep_raw = str(request.args.get("separation", "") or "").strip()
    sep_unit = (
        str(request.args.get("separation_unit", "arcsec") or "").strip().lower()
    )

    def _norm_variants(value: str):
        text = str(value or "").strip().lower()
        if not text:
            return set()
        variants = {
            re.sub(r"[^a-z0-9]+", "", text),
            re.sub(r"[^a-z0-9]+", "", text.replace("+", "p").replace("-", "m")),
        }
        return {v for v in variants if v}

    def _name_match_row(row, query):
        qvars = _norm_variants(query)
        if not qvars:
            return True
        names = [str(row.get("OBJNAME", "") or "")]
        aliases = str(row.get("ALIASES", "") or "")
        if aliases:
            names.extend(
                part.strip() for part in aliases.split("|") if part.strip()
            )

        for name in names:
            nvars = _norm_variants(name)
            if any(qv in nv for qv in qvars for nv in nvars):
                return True
        return False

    def _row_ra_dec_deg(row):
        ra_keys = ("RA [Deg]", "RA", "OBJRA", "OBJ_RA")
        dec_keys = ("Dec [Deg]", "DEC", "Dec", "OBJDEC", "OBJ_DEC")
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
            return (
                jsonify(
                    success=False, error="Invalid RA/Dec/separation values."
                ),
                400,
            )

        if sep_unit == "deg":
            sep_deg = sep
        elif sep_unit == "arcmin":
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
            message=(
                "Type at least 1 character for object search "
                "or provide RA/Dec + separation."
            ),
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
            cos_sep = math.sin(dec0r) * math.sin(dec1r) + math.cos(
                dec0r
            ) * math.cos(dec1r) * math.cos(ra0r - ra1r)
            if cos_sep >= cos_sep_max:
                coord_filtered.append(row)
        filtered = coord_filtered

    skip = {"RUN_ID", "run_id", "ALL_RUN_IDS", "all_run_ids"}
    columns = [
        c
        for c in (all_rows[0].keys() if all_rows else [])
        if c not in skip and c not in hidden_by_meta
    ]

    column_meta = {
        col: dict(meta)
        for col, meta in raw_column_meta.items()
        if (
            col not in skip
            and col not in hidden_by_meta
            and isinstance(meta, dict)
        )
    }
    if "OBJNAME" in columns and "OBJNAME" not in column_meta:
        column_meta["OBJNAME"] = {
            "sortable": True,
            "filterable": True,
            "removable": False,
            "default": True,
            "type": "string",
        }

    clean_rows = [
        {
            k: v
            for k, v in row.items()
            if k not in skip and k not in hidden_by_meta
        }
        for row in filtered
    ]

    def _date_only(value):
        if value is None:
            return value
        text = str(value).strip()
        if not text:
            return value
        if "T" in text:
            return text.split("T", 1)[0]
        if " " in text:
            return text.split(" ", 1)[0]
        return text

    _date_cols = {"last obs", "latest obs", "last modified"}
    for row in clean_rows:
        for col in _date_cols:
            if col in row:
                row[col] = _date_only(row.get(col))

    _FKIND_COLS = [
        ("raw", "raw files"),
        ("pp", "pp files"),
        ("ext", "ext files"),
        ("tcorr", "tcorr files"),
        ("ccf", "ccf files"),
        ("efits", "e.fits files"),
        ("tfits", "t.fits files"),
        ("lbl", "lbl files"),
    ]

    _objects_dir = tasks_dir / profile_id / "objects"

    def _read_ftable(objname, fkind):
        _path = _objects_dir / f"ftable_{fkind}_{objname}.json"
        try:
            with open(_path, encoding="utf-8") as _fh:
                _d = _json.load(_fh)
            _rows = _d.get("rows") or []
            _m = len(_rows)
            _n = sum(
                1
                for _r in _rows
                if str(_r.get("KW_RUN_ID", "") or "") in accessible_run_ids
            )
            return _n, _m
        except FileNotFoundError:
            return None, None
        except Exception:
            return None, None

    _ftable_tasks = [
        (row.get("OBJNAME", ""), fkind)
        for row in clean_rows
        for fkind, _ in _FKIND_COLS
        if row.get("OBJNAME", "")
    ]

    _ftable_results = {}
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

    for row in clean_rows:
        _objname = row.get("OBJNAME", "")
        for _fkind, _colname in _FKIND_COLS:
            _n_val, _m_val = _ftable_results.get(
                (_objname, _fkind), (None, None)
            )
            row[_colname] = None if _n_val is None else f"{_n_val} ({_m_val})"

    _fcount_cols = [_colname for _, _colname in _FKIND_COLS]
    columns = list(columns) + _fcount_cols
    column_meta.update(
        {
            _colname: {
                "sortable": True,
                "filterable": True,
                "removable": True,
                "default": True,
                "hidden": False,
                "type": "count",
            }
            for _, _colname in _FKIND_COLS
        }
    )

    payload = dict(
        success=True,
        rows=clean_rows,
        columns=columns,
        column_meta=column_meta,
        generated_at=generated_at,
        total_rows=len(all_rows),
    )
    if find_only and not clean_rows and (has_name_filter or has_coord_filter):
        payload["message"] = "No objects matched the current search criteria."

    return jsonify(**payload)


def api_object_plots(app):
    """Return Bokeh JSON plot payloads for object plots."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    # Apply the requested theme (default/light/dark) to every Bokeh
    # figure built within this request via the thread-local set in
    # apero_ri.plots.bokeh_theme.
    try:
        from apero_ri.plots.bokeh_theme import set_request_theme
        set_request_theme(request.args.get("theme", "default"))
    except Exception:  # noqa: BLE001
        pass

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    plot_group = (
        str(request.args.get("plot_group", "all") or "all").strip().lower()
    )
    valid_groups = {
        "all",
        "spectrum",
        "ccf",
        "ccf_rv",
        "ccf_profile",
        "time_series",
        "target_info",
    }
    if plot_group not in valid_groups:
        return (
            jsonify(
                success=False,
                error=(
                    "Invalid plot_group. Use one of: "
                    "all, spectrum, ccf, ccf_rv, ccf_profile, time_series"
                ),
            ),
            400,
        )
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="Missing profile_id or objname",
            ),
            400,
        )

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
    force_regen = bool(str(request.args.get("_ts", "")).strip())

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = next(
        (p for p in accessible if p["profile_id"] == profile_id), None
    )
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

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

    from apero_ri.core.plot_cache import check_and_serve

    rid_tag = app._rid_cache_tag(accessible_run_ids)
    cache_key = (
        f"{plot_group}__{objname}__{rid_tag}"
        if vsys_ms is None
        else f"{plot_group}__{objname}__vsys{vsys_ms}__{rid_tag}"
    )
    if plot_group in {"all", "ccf", "ccf_profile"} and (
        ccf_mjd_start is not None or ccf_mjd_end is not None
    ):
        cache_key += (
            f'__ccfmjd_{ccf_mjd_start if ccf_mjd_start is not None else ""}'
            f'_{ccf_mjd_end if ccf_mjd_end is not None else ""}'
        )
    if plot_group in {"all", "ccf", "ccf_profile"}:
        cache_key += f"__ccfnobs_{int(ccf_nobs)}"
    if plot_group in {"all", "time_series"}:
        cache_key += "__tsaxis_v2"
    # Fold the active theme into the cache key so dark/light don't
    # serve each other's cached light-bg payloads.
    try:
        from apero_ri.plots.bokeh_theme import get_request_theme
        cache_key += f"__th_{get_request_theme()}"
    except Exception:  # noqa: BLE001
        pass
    if not force_regen:
        cached = check_and_serve(
            base_dir,
            instrument,
            profile_id,
            "object_plots",
            cache_key,
            aparams=profile_data,
        )
        if cached is not None:
            app.logger.info(
                "OBJECT_PLOTS cache_hit profile=%s object=%s group=%s",
                profile_id,
                objname,
                plot_group,
            )
            return jsonify(**cached)

    htable_rows = load_object_htable_rows(objects_dir, objname)
    preset = load_object_preset(instrument_profile_file)
    obj_props = load_object_table_row(objects_dir, objname)

    need_ext = plot_group in {"all", "spectrum", "time_series"}
    need_tcorr = plot_group in {"all", "spectrum"}
    need_ccf = plot_group in {"all", "ccf", "ccf_profile"}
    ftable_ext_rows = (
        load_object_ftable_rows(objects_dir, objname, "ext") if need_ext else []
    )
    ftable_tcorr_rows = (
        load_object_ftable_rows(objects_dir, objname, "tcorr")
        if need_tcorr
        else []
    )
    ftable_ccf_rows = (
        load_object_ftable_rows(objects_dir, objname, "ccf") if need_ccf else []
    )

    htable_rows, ftables = app._filter_plot_rows(
        htable_rows,
        {
            "ext": ftable_ext_rows,
            "tcorr": ftable_tcorr_rows,
            "ccf": ftable_ccf_rows,
        },
        accessible_run_ids,
    )
    ftable_ext_rows = ftables["ext"]
    ftable_tcorr_rows = ftables["tcorr"]
    ftable_ccf_rows = ftables["ccf"]

    path_red = str(app._profile_get_path(profile_data, "PATH_RED", "") or "")
    path_lbl = str(app._profile_get_path(profile_data, "PATH_LBL", "") or "")
    paths = {"PATH_RED": path_red, "PATH_LBL": path_lbl}

    from apero_ri.plots.plot_objects import (
        build_berv_plot_json,
        build_ccf_profile_plot_json,
        build_ccf_rv_plot_json,
        build_hr_plot_json,
        build_sed_plot_json,
        build_snr_plot_json,
        build_spec_plot_json,
        build_ts_airmass_plot_json,
        build_ts_snr_plot_json,
        load_or_query_20pc_neighborhood,
    )

    _no_plot = {"has_plot": False, "message": "Plot build failed"}
    timings_ms = {}

    def _timed_build(name, func):
        t0 = time.perf_counter()
        ok = True
        try:
            payload = func()
        except Exception as _exc:
            # Surface the exception details so that "Plot build failed"
            # is debuggable from the response and the server log
            # (previously the traceback was silently swallowed).
            import traceback as _tb
            _tb_str = _tb.format_exc()
            try:
                app.logger.exception(
                    "OBJECT_PLOTS build EXCEPTION profile=%s object=%s "
                    "group=%s plot=%s err=%s",
                    profile_id, objname, plot_group, name, _exc,
                )
            except Exception:
                pass
            payload = {
                "has_plot": False,
                "message": (
                    f"Plot build failed: {type(_exc).__name__}: {_exc}"
                ),
                "error": str(_exc),
                "traceback": _tb_str,
            }
            ok = False
        dt_ms = (time.perf_counter() - t0) * 1000.0
        timings_ms[name] = round(dt_ms, 2)
        app.logger.info(
            (
                "OBJECT_PLOTS build profile=%s object=%s group=%s "
                "plot=%s ok=%s ms=%.2f"
            ),
            profile_id,
            objname,
            plot_group,
            name,
            ok,
            dt_ms,
        )
        return payload

    result = dict(success=True, plot_group=plot_group)

    if plot_group in {"all", "spectrum"}:
        result["snr"] = _timed_build(
            "snr", lambda: build_snr_plot_json(htable_rows, preset)
        )
        result["berv"] = _timed_build(
            "berv",
            lambda: build_berv_plot_json(
                htable_rows, vsys_ms, preset, obj_props=obj_props
            ),
        )
        result["spec"] = _timed_build(
            "spec",
            lambda: build_spec_plot_json(
                htable_rows, ftable_ext_rows, ftable_tcorr_rows, paths, preset
            ),
        )

    if plot_group in {"all", "ccf_rv"}:
        result["ccf_rv"] = _timed_build(
            "ccf_rv",
            lambda: build_ccf_rv_plot_json(
                htable_rows,
                preset,
            ),
        )

    if plot_group in {"all", "ccf", "ccf_profile"}:
        ccf_profile_payload = _timed_build(
            "ccf_profile",
            lambda: build_ccf_profile_plot_json(
                htable_rows,
                ftable_ccf_rows,
                paths,
                preset,
                ccf_mjd_start=ccf_mjd_start,
                ccf_mjd_end=ccf_mjd_end,
                ccf_nobs=ccf_nobs,
            ),
        )
        result["ccf_profile"] = ccf_profile_payload
        if plot_group == "ccf":
            result["ccf"] = ccf_profile_payload

    if plot_group in {"all", "time_series"}:
        result["ts_snr"] = _timed_build(
            "ts_snr",
            lambda: build_ts_snr_plot_json(
                htable_rows, ftable_ext_rows, preset
            ),
        )
        result["ts_airmass"] = _timed_build(
            "ts_airmass",
            lambda: build_ts_airmass_plot_json(
                htable_rows, ftable_ext_rows, preset
            ),
        )
    if plot_group in {"all", "target_info"}:
        # Resolve the astrometric YAML entry for this target.
        # SED + HR plots are interactive Bokeh figures driven by
        # the photometry / Teff / parallax stored in the entry.
        try:
            from apero.core import drs_astrometrics as _dra
            astrom_dir = base_dir / "apero-assets" / "astrometrics"
            yaml_entry = _dra.find_by_name(
                str(astrom_dir), objname)
        except Exception:
            yaml_entry = None
        # 20-pc Gaia neighborhood (cached)
        try:
            nb_cache = (
                base_dir / "cache" / "_shared"
                / "gaia_20pc" / "neighborhood.json")
            neighborhood = load_or_query_20pc_neighborhood(
                cache_path=str(nb_cache))
        except Exception:
            neighborhood = []
        result["sed"] = _timed_build(
            "sed",
            lambda: build_sed_plot_json(yaml_entry),
        )
        result["hr"] = _timed_build(
            "hr",
            lambda: build_hr_plot_json(
                yaml_entry, neighborhood=neighborhood),
        )
    result["updated_at"] = datetime.now(timezone.utc).isoformat()
    result["server_timings_ms"] = timings_ms

    try:
        from apero_ri.core.plot_cache import (
            _load_meta,
            _profile_dir,
            _save_meta,
            is_cache_enabled,
            load_cache_config,
            put_cached,
            resolve_cache_root,
        )

        cfg = load_cache_config(base_dir)
        if cfg.get("enabled"):
            cache_root = resolve_cache_root(base_dir, cfg)
            put_cached(
                cache_root,
                instrument,
                profile_id,
                "object_plots",
                cache_key,
                result,
            )
            pdir = _profile_dir(cache_root, instrument, profile_id)
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

    app.logger.info(
        "OBJECT_PLOTS done profile=%s object=%s group=%s total_ms=%.2f rows=%d",
        profile_id,
        objname,
        plot_group,
        sum(timings_ms.values()),
        len(htable_rows),
    )

    return jsonify(**result)


def api_object_page(app):
    """Return object-page data for a profile/object."""
    import json as _json

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))

    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    objname = request.args.get("objname", "").strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="Missing profile_id or objname",
            ),
            400,
        )

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    # ---- TTL cache lookup -------------------------------------
    rid_tag = app._rid_cache_tag(accessible_run_ids)
    cache_key = (profile_id, objname.lower(), rid_tag)
    cached = _object_page_cache_get(cache_key)
    if cached is not None:
        return jsonify(**cached)

    tasks_dir = base_dir / "tasks" / instrument
    profile_dir = tasks_dir / profile_id
    object_table_path = profile_dir / "object_table.json"

    if not object_table_path.exists():
        legacy_path = tasks_dir / f"object_table_{profile_id}.json"
        if legacy_path.exists():
            object_table_path = legacy_path

    if not object_table_path.exists():
        return (
            jsonify(
                success=False,
                error="No object table data found for this profile.",
            ),
            404,
        )

    try:
        with open(object_table_path, encoding="utf-8") as _fh:
            object_table = _json.load(_fh)
    except Exception as exc:
        return (
            jsonify(
                success=False,
                error=f"Failed to load object table: {exc}",
            ),
            500,
        )

    all_rows = object_table.get("rows", [])

    def _row_accessible(row):
        raw = str(row.get("RUN_ID", "") or "")
        row_rids = {r.strip() for r in raw.split(",") if r.strip()}
        return bool(row_rids & accessible_run_ids)

    obj_row = None
    for row in all_rows:
        name = str(row.get("OBJNAME", "") or "")
        if name.lower() == objname.lower() and _row_accessible(row):
            obj_row = row
            break

    if obj_row is None:
        return (
            jsonify(
                success=False,
                error="Object not found or not accessible for this user.",
            ),
            404,
        )

    profile_data = profile.get("data") if isinstance(profile, dict) else {}
    if not isinstance(profile_data, dict):
        profile_data = {}
    instrument_profile_file = str(
        profile_data.get("APERO_INSTRUMENT_PROFILE", "")
        or profile_data.get("apero_instrument_profile", "")
        or ""
    ).strip()

    path_lbl = str(
        app._profile_get_path(profile_data, "PATH_LBL", "") or ""
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
    labels = sections.pop("labels", {})

    # ------------------------------------------------------------
    # Target Information shared payload (single source of truth).
    # The shared component in apero_ri.components.target_info_sections
    # is the ONLY supported renderer -- there is no legacy plain-text
    # fallback.  If the build fails we emit an empty {sections: []}
    # payload carrying an `error` field so the front-end can surface
    # the failure instead of silently rendering nothing.
    # ------------------------------------------------------------
    try:
        from apero.core import drs_astrometrics as _dra
        from apero_ri.components.target_info_sections import (
            build_target_info_payload as _build_ti,
        )
        astrom_dir = base_dir / "apero-assets" / "astrometrics"
        entry = _dra.find_by_name(str(astrom_dir), objname)
        if not entry:
            raise RuntimeError(
                "No astrometric YAML entry found for "
                f"{objname!r} in {astrom_dir}"
            )
        apero_name = entry.get("APERO_NAME", objname)
        # main Target Information card: keep all data sections
        # (incl. Status). SED and HR Diagram are rendered as
        # their own page-level cards (see payloads below).
        shared_payload = _build_ti(
            entry,
            obj_row=obj_row,
            include_charts=False,
            exclude_ids=['sed', 'hr_diagram'],
        )
        shared_payload["apero_name"] = apero_name
        sections["target_info"] = shared_payload

        # standalone single-section payloads used by the
        # dedicated SED and HR Diagram cards on the page.
        sed_payload = _build_ti(
            entry,
            obj_row=obj_row,
            include_charts=True,
            only_ids=['sed'],
        )
        sed_payload["apero_name"] = apero_name
        sections["target_sed"] = sed_payload

        hr_payload = _build_ti(
            entry,
            obj_row=obj_row,
            include_charts=True,
            only_ids=['hr_diagram'],
        )
        hr_payload["apero_name"] = apero_name
        sections["target_hr_diagram"] = hr_payload
    except Exception as _ti_exc:  # noqa: BLE001
        # Loud failure: log full traceback and emit an explicit
        # empty payload with an `error` so the user sees the real
        # cause instead of a silently-blank Target Information
        # card.  No legacy plain-text fallback is permitted.
        app.logger.exception(
            "Target Information build FAILED for profile=%s "
            "object=%s: %s",
            profile_id, objname, _ti_exc,
        )
        sections["target_info"] = {
            "sections": [],
            "error": (
                "Target Information build failed: "
                + str(_ti_exc)
            ),
            "apero_name": objname,
        }
        sections["target_sed"] = {
            "sections": [],
            "error": str(_ti_exc),
            "apero_name": objname,
        }
        sections["target_hr_diagram"] = {
            "sections": [],
            "error": str(_ti_exc),
            "apero_name": objname,
        }

    response_payload = dict(
        success=True,
        object_name=obj_row.get("OBJNAME", objname),
        profile_id=profile_id,
        generated_at=object_table.get("generated_at"),
        sections=sections,
        labels=labels,
    )
    _object_page_cache_set(cache_key, response_payload)
    return jsonify(**response_payload)


def api_obs_table(app):
    """Return observation table rows for a profile."""
    import json as _json

    base_dir = Path(app.args.data_dir or str(Path.home() / ".ari"))

    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    else:
        perms = get_public_permissions()

    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = request.args.get("profile_id", "").strip()
    if not profile_id:
        return jsonify(success=False, error="Missing profile_id"), 400

    accessible = get_accessible_profiles(user_info, app.ari_groups)
    profile = None
    for prof in accessible:
        if prof["profile_id"] == profile_id:
            profile = prof
            break
    if not profile:
        return jsonify(success=False, error="Profile not found"), 404

    instrument = profile["instrument"]
    accessible_run_ids = app._get_user_accessible_run_ids(user_info, instrument)

    tasks_dir = base_dir / "tasks" / instrument
    json_path = tasks_dir / profile_id / "obs_table.json"

    if not json_path.exists():
        legacy_path1 = tasks_dir / f"obs_table_{profile_id}.json"
        legacy_path2 = tasks_dir / f"observation_table_{profile_id}.json"
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
            message=(
                "No observation table data found. "
                "Run the observation table task first."
            ),
        )

    try:
        with open(json_path, encoding="utf-8") as f:
            data = _json.load(f)
    except Exception as exc:
        return jsonify(success=False, error=f"Failed to load data: {exc}"), 500

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    all_rows = data.get("rows", [])
    generated_at = data.get("generated_at") or metadata.get("GENERATED_AT")
    raw_column_meta = metadata.get("COLUMN_META", {})
    if not isinstance(raw_column_meta, dict):
        raw_column_meta = {}

    filtered = []
    for row in all_rows:
        raw = str(
            row.get("RUN_ID", "")
            or row.get("run_id", "")
            or row.get("ALL_RUN_IDS", "")
            or row.get("all_run_ids", "")
            or ""
        )
        row_rids = {r.strip() for r in raw.split(",") if r.strip()}
        if row_rids & accessible_run_ids:
            filtered.append(row)

    skip = {"RUN_ID", "run_id", "ALL_RUN_IDS", "all_run_ids"}
    columns = [
        c for c in (all_rows[0].keys() if all_rows else []) if c not in skip
    ]

    column_meta = {
        col: dict(meta)
        for col, meta in raw_column_meta.items()
        if col not in skip and isinstance(meta, dict)
    }
    if "NIGHT" in columns and "NIGHT" not in column_meta:
        column_meta["NIGHT"] = {
            "sortable": True,
            "filterable": True,
            "removable": False,
            "default": True,
            "type": "night",
        }
    if "OBJNAME" in columns and "OBJNAME" not in column_meta:
        column_meta["OBJNAME"] = {
            "sortable": True,
            "filterable": True,
            "removable": False,
            "default": True,
            "type": "string",
        }

    clean_rows = [
        {k: v for k, v in row.items() if k not in skip} for row in filtered
    ]

    return jsonify(
        success=True,
        rows=clean_rows,
        columns=columns,
        column_meta=column_meta,
        generated_at=generated_at,
        total_rows=len(all_rows),
    )


# ====================================================================
# TESS rotation periods (tessilator)
# ====================================================================

def api_tess_rotation(app):
    """Generate TESS rotation period plots on demand."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    name_mode = bool((request.args.get('name') or '').strip())
    if 'view.data_portal' not in perms and not name_mode:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    accessible = get_accessible_profiles(
        user_info, app.ari_groups)
    ok, ctx = _resolve_target_context(
        app, user_info, accessible)
    if not ok:
        return ctx
    instrument = ctx['instrument']
    objname = ctx['objname']
    obj_props = ctx['obj_props']
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari'))

    from apero_ri.core.plot_cache import (
        is_cache_enabled,
        load_cache_config,
        resolve_cache_root,
    )
    from apero_ri.core.run_tessilator import get_tess_cached

    cfg = load_cache_config(base_dir)
    cache_root = resolve_cache_root(base_dir, cfg)

    # Return cached result if available
    force = bool(
        str(request.args.get('_ts', '')).strip()
    )
    if not force:
        hit = get_tess_cached(
            cache_root, instrument, objname
        )
        if hit is not None:
            return jsonify(**hit)

    # Gather all known aliases for this object
    aliases_raw = str(obj_props.get('ALIASES', '') or '')
    aliases = [
        a.strip() for a in aliases_raw.split('|')
        if a.strip()
    ]

    result = run_tessilator(
        objname=objname,
        cache_root=cache_root,
        instrument=instrument,
        aliases=aliases,
    )

    return jsonify(**result)


def api_tess_rotation_lc(app):
    """Download a cached TESS light-curve CSV for one sector."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if 'view.data_portal' not in perms:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    profile_id = request.args.get(
        'profile_id', ''
    ).strip()
    objname = request.args.get('objname', '').strip()
    sector_str = request.args.get('sector', '').strip()
    if not profile_id or not objname or not sector_str:
        return jsonify(
            success=False,
            error='Missing profile_id, objname or sector',
        ), 400

    try:
        sector = int(sector_str)
    except ValueError:
        return jsonify(
            success=False, error='Invalid sector'
        ), 400

    accessible = get_accessible_profiles(
        user_info, app.ari_groups
    )
    profile = next(
        (p for p in accessible
         if p['profile_id'] == profile_id), None
    )
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )

    from apero_ri.core.plot_cache import (
        load_cache_config,
        resolve_cache_root,
    )
    from apero_ri.core.run_tessilator import (
        get_tess_lc_csv_path,
    )

    cfg = load_cache_config(base_dir)
    cache_root = resolve_cache_root(base_dir, cfg)

    csv_path = get_tess_lc_csv_path(
        cache_root, instrument, objname, sector
    )
    if csv_path is None:
        return jsonify(
            success=False,
            error='Period results not found',
        ), 404

    dl_name = f'{objname}_periods.ecsv'
    return send_file(
        str(csv_path),
        as_attachment=True,
        download_name=dl_name,
    )


def api_tess_rotation_data(app):
    """Download a cached TESS data file (light curve, etc.)."""
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if 'view.data_portal' not in perms:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    profile_id = request.args.get(
        'profile_id', ''
    ).strip()
    objname = request.args.get(
        'objname', ''
    ).strip()
    filename = request.args.get(
        'filename', ''
    ).strip()
    if not profile_id or not objname or not filename:
        return jsonify(
            success=False,
            error=(
                'Missing profile_id, objname '
                'or filename'
            ),
        ), 400

    accessible = get_accessible_profiles(
        user_info, app.ari_groups
    )
    profile = next(
        (p for p in accessible
         if p['profile_id'] == profile_id), None
    )
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    base_dir = Path(
        app.args.data_dir
        or str(Path.home() / '.ari')
    )

    from apero_ri.core.plot_cache import (
        load_cache_config,
        resolve_cache_root,
    )
    from apero_ri.core.run_tessilator import (
        get_tess_data_file_path,
    )

    cfg = load_cache_config(base_dir)
    cache_root = resolve_cache_root(base_dir, cfg)

    file_path = get_tess_data_file_path(
        cache_root, instrument, objname, filename,
    )
    if file_path is None:
        return jsonify(
            success=False,
            error='Data file not found',
        ), 404

    dl_name = f'{objname}_{file_path.name}'
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=dl_name,
    )


def api_tess_rotation_stream(app):
    """SSE endpoint: stream tessilator console output live.

    Each event is a JSON object with a ``type`` field:
      - ``log``   – a line of console output
      - ``done``  – final result (sectors, images, …)
      - ``error`` – something went wrong
    """
    user_info = app._get_api_user()
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    name_mode = bool((request.args.get('name') or '').strip())
    if 'view.data_portal' not in perms and not name_mode:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    accessible = get_accessible_profiles(
        user_info, app.ari_groups)
    ok, ctx = _resolve_target_context(
        app, user_info, accessible)
    if not ok:
        return ctx
    instrument = ctx['instrument']
    objname = ctx['objname']
    obj_props = ctx['obj_props']
    base_dir = Path(
        app.args.data_dir
        or str(Path.home() / '.ari')
    )

    from apero_ri.core.plot_cache import (
        load_cache_config,
        resolve_cache_root,
    )
    from apero_ri.core.run_tessilator import (
        get_tess_cached,
        run_tessilator,
    )

    cfg = load_cache_config(base_dir)
    cache_root = resolve_cache_root(base_dir, cfg)

    # If cached (and no force), return instantly
    force = bool(
        str(request.args.get('_ts', '')).strip()
    )
    if not force:
        hit = get_tess_cached(
            cache_root, instrument, objname
        )
        if hit is not None:
            payload = _json.dumps(
                dict(type='done', result=hit)
            )

            def _cached():
                yield f'data: {payload}\n\n'

            return Response(
                stream_with_context(_cached()),
                mimetype='text/event-stream',
            )

    # Gather aliases
    aliases_raw = str(obj_props.get('ALIASES', '') or '')
    aliases = [
        a.strip() for a in aliases_raw.split('|')
        if a.strip()
    ]

    # Use a separate process so stdout/stderr capture inside
    # tessilator cannot leak unrelated request logs into this
    # stream.
    log_q = mp.Queue()
    result_q = mp.Queue()
    proc = mp.Process(
        target=_run_tessilator_stream_worker,
        args=(
            objname,
            cache_root,
            instrument,
            aliases,
            log_q,
            result_q,
        ),
        daemon=True,
    )
    proc.start()

    def _generate():
        while True:
            try:
                item = log_q.get(timeout=30)
            except queue.Empty:
                # keep-alive comment
                yield ': keepalive\n\n'
                continue
            if item is None:
                break
            evt = _json.dumps(
                dict(type='log', text=item)
            )
            yield f'data: {evt}\n\n'

        # Final result
        result = None
        try:
            result = result_q.get_nowait()
        except queue.Empty:
            pass

        if result is None:
            result = dict(
                success=False,
                error='No result from tessilator',
            )
        if result.get('success'):
            payload = _json.dumps(
                dict(type='done', result=result)
            )
        else:
            payload = _json.dumps(dict(
                type='error',
                error=result.get('error', 'Failed'),
            ))
        yield f'data: {payload}\n\n'

    return Response(
        stream_with_context(_generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )
