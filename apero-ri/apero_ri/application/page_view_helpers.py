"""Page view factory helpers for ARIApp."""

from datetime import datetime, timezone
from pathlib import Path
import json
import time as _time

import yaml
from apero_ri.core import apero_checks as checks_core
from apero_ri.core import user_data as ud
from apero_ri.core.auth import (
    get_effective_user,
    load_apero_profiles,
    get_public_permissions,
    load_admin_health_config,
    user_has_admin_privileges,
)
from apero_ri.apero_monitoring.checks import CHECKS as MONITOR_CHECKS
from apero_ri.core.docs import (
    get_default_version,
    get_doc_cards,
    get_doc_sidebar_tree,
    render_markdown,
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


_APERO_POLICY_CACHE = dict(
    signature=None,
    payload=dict(),
    updated_at='',
    last_checked_at=0.0,
)

# How long (seconds) to serve the cached policy payload without
# re-scanning the check YAML directories on network mounts.
_POLICY_CACHE_TTL_S = 120

# Keep a persistent cache on disk to avoid expensive cold-start scans.
_POLICY_DISK_CACHE_TTL_S = 21600
_POLICY_DISK_CACHE_FILE = 'apero_checks_policy_cache.json'


def _policy_now_utc() -> str:
    """Return UTC timestamp text for policy-page last-updated label."""
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%d %H:%M:%S (UTC)')


def _safe_mtime_ns(path_obj: Path) -> int:
    """Return st_mtime_ns safely for one path."""
    try:
        return int(path_obj.stat().st_mtime_ns)
    except Exception:
        return 0


def _collect_policy_roots(local_data_dir, checks_cfg):
    """Collect profile entries and their resolved checks roots."""
    out = []
    profiles_data = load_apero_profiles(hydrate=True)
    configured = checks_cfg.get('checks_root', '')
    for instrument, instr_profiles in profiles_data.items():
        if not isinstance(instr_profiles, dict):
            continue
        for profile_id, profile_data in instr_profiles.items():
            if not isinstance(profile_data, dict):
                continue
            checks_root = checks_core.resolve_checks_root(
                local_data_dir,
                profile_data,
                configured,
            )
            out.append(
                {
                    'instrument': str(instrument or '').strip(),
                    'profile_id': str(profile_id or '').strip(),
                    'profile_data': profile_data,
                    'checks_root': Path(checks_root),
                }
            )
    return out


def _collect_root_signatures(profile_rows):
    """Collect per-root YAML files and mtime signatures."""
    root_files = dict()
    root_signature = []
    roots = sorted({
        str(row.get('checks_root') or '')
        for row in profile_rows
        if str(row.get('checks_root') or '') != ''
    })
    for root in roots:
        path_obj = Path(root)
        files = checks_core.list_yaml_files(path_obj)
        max_mtime = 0
        for file_obj in files:
            mtime = _safe_mtime_ns(file_obj)
            if mtime > max_mtime:
                max_mtime = mtime
        root_files[root] = files
        root_signature.append((root, len(files), max_mtime))
    return tuple(root_signature), root_files


def _policy_disk_cache_path(local_data_dir: Path) -> Path:
    """Return path for persistent policy payload cache."""
    return Path(local_data_dir) / 'cache' / _POLICY_DISK_CACHE_FILE


def _load_policy_disk_cache(local_data_dir: Path):
    """Load persistent policy payload when still fresh."""
    path = _policy_disk_cache_path(local_data_dir)
    if (not path.exists()) or (not path.is_file()):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle) or dict()
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    built_at = float(data.get('built_at_monotonic') or 0.0)
    if built_at <= 0:
        return None
    age = _time.monotonic() - built_at
    if age < 0:
        return None
    if age >= _POLICY_DISK_CACHE_TTL_S:
        return None

    payload = data.get('payload')
    if not isinstance(payload, dict):
        return None
    return dict(payload)


def _save_policy_disk_cache(local_data_dir: Path, payload: dict) -> None:
    """Persist policy payload for cold-start reuse."""
    path = _policy_disk_cache_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    data = dict(
        built_at_monotonic=_time.monotonic(),
        payload=dict(payload),
    )
    with open(tmp_path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, sort_keys=False)
    tmp_path.replace(path)


def _empty_check_stats():
    """Return a blank counters mapping for one check."""
    out = dict()
    out['passed'] = 0
    out['overridden'] = 0
    out['monitored'] = 0
    out['mixed'] = 0
    out['failed'] = 0
    out['total'] = 0
    return out


def _row_state(bucket: str, row: dict) -> str:
    """Return status label for one pass/failure row."""
    has_override = bool((row or {}).get('override'))
    has_monitor = bool((row or {}).get('monitor'))
    if has_override and has_monitor:
        return 'mixed'
    if has_override:
        return 'overridden'
    if has_monitor:
        return 'monitored'
    if str(bucket or '') == 'passes':
        return 'passed'
    return 'failed'


def _policy_obsdir_counts(loaded: dict, ignored_set) -> dict:
    """Return lightweight per-obsdir state counters for policy page."""
    failures = loaded.get('failures', dict())
    if not isinstance(failures, dict):
        failures = dict()

    override_count = 0
    monitor_count = 0
    active_failure_count = 0
    for key, failure in failures.items():
        if key in ignored_set:
            continue
        has_override = bool((failure or {}).get('override'))
        has_monitor = bool((failure or {}).get('monitor'))
        if has_override:
            override_count += 1
        if has_monitor:
            monitor_count += 1
        if (not has_override) and (not has_monitor):
            active_failure_count += 1

    if active_failure_count > 0:
        card_color = 'failed'
    elif (override_count > 0) and (monitor_count > 0):
        if override_count > monitor_count:
            card_color = 'overridden'
        elif monitor_count > override_count:
            card_color = 'monitored'
        else:
            card_color = 'overridden_monitored'
    elif override_count > 0:
        card_color = 'overridden'
    elif monitor_count > 0:
        card_color = 'monitored'
    else:
        card_color = 'ok'

    return dict(card_color=card_color)


def _dominant_state(counts):
    """Return dominant state key for color coding."""
    values = dict()
    values['passed'] = int(counts.get('passed', 0) or 0)
    values['overridden'] = int(counts.get('overridden', 0) or 0)
    values['monitored'] = int(counts.get('monitored', 0) or 0)
    values['failed'] = int(counts.get('failed', 0) or 0)
    values['mixed'] = int(counts.get('mixed', 0) or 0)
    if sum(values.values()) == 0:
        return 'neutral'
    max_count = max(values.values())
    leaders = {
        key for key, val in values.items()
        if val == max_count
    }
    priority = ['failed', 'overridden', 'monitored', 'mixed', 'passed']
    for key in priority:
        if key in leaders:
            return key
    return 'neutral'


def _policy_text(value) -> str:
    """Convert one policy-view value to a compact text string."""
    if isinstance(value, list):
        parts = [str(item or '').strip() for item in value]
        parts = [item for item in parts if item != '']
        return ', '.join(parts) if parts else 'None'
    if value in [None, '']:
        return 'None'
    return str(value)


def _admin_section(title: str, rows: list) -> dict:
    """Build one admin info section with non-empty rows only."""
    clean_rows = []
    for row in list(rows or []):
        label = str((row or {}).get('label') or '').strip()
        if label == '':
            continue
        clean_rows.append({
            'label': label,
            'value': _policy_text((row or {}).get('value')),
        })
    return dict(title=str(title or '').strip(), rows=clean_rows)


def _check_metadata_status(check_obj) -> dict:
    """Return documentation-metadata completeness for one check."""
    missing_fields = []
    description = str(getattr(check_obj, 'description', '') or '').strip()
    what_to_do = str(getattr(check_obj, 'what_to_do', '') or '').strip()
    contact_list = getattr(check_obj, 'contact_list', {})
    has_contacts = isinstance(contact_list, dict) and len(contact_list) > 0

    if description == '':
        missing_fields.append('CHECK.description')
    if what_to_do == '':
        missing_fields.append('CHECK.what_to_do')
    if not has_contacts:
        missing_fields.append('CHECK.contact_list')

    return dict(
        missing_fields=missing_fields,
        has_missing_metadata=len(missing_fields) > 0,
    )


def _build_check_info_payload(check_obj, profiles_data=None) -> dict:
    """Build admin-check info sections and rendered logic payload."""
    info_sections = []
    metadata = _check_metadata_status(check_obj)
    info_sections.append(_admin_section(
        'Identity',
        [
            dict(label='CHECK_NAME',
                 value=getattr(check_obj, 'name', '')),
            dict(label='CHECK_HUMAN_NAME',
                 value=getattr(check_obj, 'string_name', '')),
            dict(label='CHECK_TYPE',
                 value=str(getattr(check_obj, 'check_type', '') or '')
                 .upper()),
        ],
    ))
    info_sections.append(_admin_section(
        'Coverage',
        [
            dict(label='INSTRUMENTS',
                 value=list(getattr(check_obj, 'instruments', []) or [])),
            dict(label='DEPENDENCIES',
                 value=list(getattr(check_obj, 'dependencies', []) or [])),
        ],
    ))

    simple_check = getattr(check_obj, 'simple_check', None)
    logic_markdown = ''
    logic_tabs = []
    if simple_check is not None:
        logic_markdown = str(simple_check.get_logic_markdown() or '').strip()
        for tab in list(
            simple_check.get_logic_tab_groups(
                profiles_data=profiles_data,
            ) or []
        ):
            tab_logic = str(tab.get('logic_markdown') or '').strip()
            tab_rows = []
            for row in list(tab.get('rows') or []):
                label = str((row or {}).get('label') or '').strip()
                if label == '':
                    continue
                tab_rows.append(
                    dict(
                        label=label,
                        value=_policy_text((row or {}).get('value')),
                    )
                )
            logic_tabs.append(
                dict(
                    kind=str(tab.get('kind') or '').strip(),
                    title=str(tab.get('title') or '').strip(),
                    profiles=list(tab.get('profiles') or []),
                    rows=tab_rows,
                    logic_markdown=tab_logic,
                    logic_html=(
                        render_markdown(tab_logic)
                        if tab_logic != ''
                        else ''
                    ),
                )
            )
        info_sections.extend(list(simple_check.get_admin_sections() or []))
    else:
        logic_markdown = str(getattr(check_obj, 'description', '') or '')
        logic_markdown = logic_markdown.strip()

    what_to_do = str(getattr(check_obj, 'what_to_do', '') or '').strip()
    if what_to_do != '':
        info_sections.append(_admin_section(
            'Actions',
            [dict(label='WHAT_TO_DO', value=what_to_do)],
        ))

    if metadata['has_missing_metadata']:
        rows = []
        for field_name in metadata['missing_fields']:
            rows.append(dict(label='MISSING', value=field_name))
        info_sections.append(_admin_section(
            'Documentation Completeness',
            rows,
        ))

    clean_sections = []
    for section in info_sections:
        title = str((section or {}).get('title') or '').strip()
        rows = list((section or {}).get('rows') or [])
        if title == '' or len(rows) == 0:
            continue
        clean_sections.append(dict(title=title, rows=rows))

    logic_html = ''
    if logic_markdown != '':
        logic_html = render_markdown(logic_markdown)

    return dict(
        info_sections=clean_sections,
        logic_markdown=logic_markdown,
        logic_html=logic_html,
        logic_tabs=logic_tabs,
        missing_fields=metadata['missing_fields'],
        has_missing_metadata=metadata['has_missing_metadata'],
    )


def _build_checks_policy_health(
    checks_catalog: list,
    ignored_checks,
) -> dict:
    """Summarise APERO checks-policy health from the checks catalog."""
    ignored_set = {
        str(k or '').strip().upper()
        for k in (ignored_checks or [])
    }
    failed = []
    missing_meta = []
    for item in list(checks_catalog or []):
        key = str(item.get('check_key') or '').strip().upper()
        if key == '' or key in ignored_set:
            continue
        name = str(
            item.get('check_name') or item.get('check_key') or key
        ).strip()
        if item.get('dominant_state') == 'failed':
            failed.append(name)
        if item.get('has_missing_metadata'):
            missing_meta.append(name)

    if failed:
        return dict(
            status='error',
            message=(
                f"{len(failed)} active check(s) have more failures "
                "than passes: "
                + ', '.join(failed[:3])
                + (', ...' if len(failed) > 3 else '')
            ),
            details=[f"Failed: {n}" for n in failed],
        )
    if missing_meta:
        return dict(
            status='warning',
            message=(
                f"{len(missing_meta)} check(s) have incomplete "
                "documentation metadata: "
                + ', '.join(missing_meta[:3])
                + (', ...' if len(missing_meta) > 3 else '')
            ),
            details=[f"Missing metadata: {n}" for n in missing_meta],
        )
    return dict(
        status='ok',
        message=(
            'All active checks are passing with complete documentation.'
        ),
        details=[],
    )


def _build_apero_policy_payload(
    local_data_dir,
    checks_cfg,
    ignored_checks,
    override_allowed,
):
    """Build cached payload for the APERO checks policy page."""
    # Fast path: if we have a valid cached payload built within the
    # TTL window, skip the expensive network-mount filesystem scan.
    _now = _time.monotonic()
    _age = _now - float(
        _APERO_POLICY_CACHE.get('last_checked_at') or 0.0
    )
    if (
        _APERO_POLICY_CACHE.get('signature') is not None
        and _APERO_POLICY_CACHE.get('payload')
        and _age < _POLICY_CACHE_TTL_S
    ):
        payload = dict(_APERO_POLICY_CACHE.get('payload', {}))
        payload['policy_last_updated'] = str(
            _APERO_POLICY_CACHE.get('updated_at', '')
        )
        return payload

    # Cold-start fast path: reuse a fresh disk cache built by a prior
    # worker process to avoid immediate heavy YAML scanning.
    disk_payload = _load_policy_disk_cache(local_data_dir)
    if isinstance(disk_payload, dict) and disk_payload:
        _APERO_POLICY_CACHE['payload'] = dict(disk_payload)
        _APERO_POLICY_CACHE['updated_at'] = str(
            disk_payload.get('policy_last_updated', '')
        )
        _APERO_POLICY_CACHE['last_checked_at'] = _time.monotonic()
        return dict(disk_payload)

    profile_rows = _collect_policy_roots(local_data_dir, checks_cfg)
    profile_sig = tuple(sorted(
        (
            str(row.get('instrument') or ''),
            str(row.get('profile_id') or ''),
            str(row.get('checks_root') or ''),
        )
        for row in profile_rows
    ))
    root_sig, root_files = _collect_root_signatures(profile_rows)
    ignore_sig = tuple(sorted(
        str(item or '').strip()
        for item in list(ignored_checks or [])
        if str(item or '').strip() != ''
    ))
    override_sig = tuple(sorted(
        str(item or '').strip()
        for item in list(override_allowed or [])
        if str(item or '').strip() != ''
    ))
    signature = (profile_sig, root_sig, ignore_sig, override_sig)
    if signature == _APERO_POLICY_CACHE.get('signature'):
        payload = dict(_APERO_POLICY_CACHE.get('payload', {}))
        payload['policy_last_updated'] = str(
            _APERO_POLICY_CACHE.get('updated_at', '')
        )
        _APERO_POLICY_CACHE['last_checked_at'] = _time.monotonic()
        return payload

    ignored_set = set(ignored_checks or [])
    override_set = set(override_allowed or [])
    checks_data = dict()
    for check_key in sorted(MONITOR_CHECKS):
        check_obj = MONITOR_CHECKS.get(check_key)
        if check_obj is None:
            continue
        key = str(check_key or '').strip()
        if key == '':
            continue
        checks_data[key] = {
            'check_key': key,
            'check_name': str(getattr(check_obj, 'name', '') or key),
            'check_human_name': str(
                getattr(check_obj, 'string_name', '') or key
            ),
            'check_type': str(getattr(check_obj, 'check_type', '') or ''),
            'instruments': sorted({
                str(item or '').strip()
                for item in list(
                    getattr(check_obj, 'instruments', []) or []
                )
                if str(item or '').strip() != ''
            }),
            'dependencies': [
                str(item or '').strip()
                for item in list(
                    getattr(check_obj, 'dependencies', []) or []
                )
                if str(item or '').strip() != ''
            ],
            'description': str(
                getattr(check_obj, 'description', '') or ''
            ),
            'info_sections': [],
            'logic_markdown': '',
            'logic_html': '',
            'is_ignored': key in ignored_set,
            'override_allowed': key in override_set,
            'doc_url': url_for(
                'doc_dynamic_view',
                page_ref=f'monitor/checks/{str(key).lower()}',
            ),
            'counts': _empty_check_stats(),
        }
        # Only compute cheap metadata on the policy list page.
        # Full check info (logic tabs, info sections) is built separately
        # on the individual check info page.
        checks_data[key].update(_check_metadata_status(check_obj))
    profile_summaries = []
    for row in profile_rows:
        counts = _empty_check_stats()
        root_key = str(row.get('checks_root') or '')
        for yaml_path in root_files.get(root_key, []):
            loaded = checks_core.load_check_file(yaml_path)
            summary = _policy_obsdir_counts(loaded, ignored_set)
            counts['total'] += 1
            color = str(summary.get('card_color') or 'ok')
            if color == 'failed':
                counts['failed'] += 1
            elif color == 'overridden':
                counts['overridden'] += 1
            elif color == 'monitored':
                counts['monitored'] += 1
            elif color == 'overridden_monitored':
                counts['mixed'] += 1
            else:
                counts['passed'] += 1

            for bucket in ('failures', 'passes'):
                rows = loaded.get(bucket, {})
                if not isinstance(rows, dict):
                    continue
                for key, check_row in rows.items():
                    check_key = str(key or '').strip()
                    if check_key == '' or check_key in ignored_set:
                        continue
                    if check_key not in checks_data:
                        checks_data[check_key] = {
                            'check_key': check_key,
                            'check_name': check_key,
                            'check_human_name': check_key,
                            'check_type': str(
                                (check_row or {}).get('type') or ''
                            ),
                            'instruments': [],
                            'dependencies': [],
                            'description': '',
                            'info_sections': [],
                            'logic_markdown': '',
                            'logic_html': '',
                            'is_ignored': check_key in ignored_set,
                            'override_allowed': check_key in override_set,
                            'doc_url': url_for(
                                'doc_dynamic_view',
                                page_ref=(
                                    'monitor/checks/'
                                    f'{str(check_key).lower()}'
                                ),
                            ),
                            'counts': _empty_check_stats(),
                            'missing_fields': [
                                'CHECK.description',
                                'CHECK.what_to_do',
                                'CHECK.contact_list',
                            ],
                            'has_missing_metadata': True,
                        }
                    state = _row_state(bucket, check_row)
                    cdict = checks_data[check_key]['counts']
                    cdict[state] += 1
                    cdict['total'] += 1

        profile_summaries.append(
            {
                'profile_id': str(row.get('profile_id') or ''),
                'instrument': str(row.get('instrument') or ''),
                'checks_root': root_key,
                'counts': counts,
                'dominant_state': _dominant_state(counts),
            }
        )

    checks_catalog = []
    for key in sorted(checks_data):
        item = dict(checks_data[key])
        item['dominant_state'] = _dominant_state(item['counts'])
        checks_catalog.append(item)

    payload = dict()
    payload['checks_catalog'] = checks_catalog
    payload['profile_summaries'] = profile_summaries
    updated_at = _policy_now_utc()
    payload['policy_last_updated'] = updated_at
    _APERO_POLICY_CACHE['signature'] = signature
    _APERO_POLICY_CACHE['payload'] = payload
    _APERO_POLICY_CACHE['updated_at'] = updated_at
    _APERO_POLICY_CACHE['last_checked_at'] = _time.monotonic()
    _save_policy_disk_cache(local_data_dir, payload)
    return payload


def make_page_view(app, page_id: str, package_dir: Path):
    """Create a page view function from pages.yaml entry."""
    page_def = app.ari_pages[page_id]
    view_perm = str(page_def.get("view-permission", "") or "").strip()
    template = page_id_to_template(page_id, app.ari_pages)
    is_parent = is_parent_page(page_id, app.ari_pages) or template.endswith(
        "/index.html"
    )

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

        if page_id == "home.docs":
            version = context.get("current_version")
            view_mode = str(request.args.get('view', 'cards') or 'cards')
            if view_mode not in {'cards', 'list'}:
                view_mode = 'cards'

            doc_cards, current_ver, _ = get_doc_cards("", version)
            context["cards"] = doc_cards
            context["current_version"] = current_ver
            context['view_mode'] = view_mode
            context['doc_self_url'] = '/docs'

            docs_sidebar = get_doc_sidebar_tree('', current_ver)
            context['docs_sidebar_tree'] = docs_sidebar
            base_sidebar = list(context.get('sidebar_tree', []))
            pinned = [
                item for item in base_sidebar
                if item.get('pinned', False)
            ]
            context['sidebar_tree'] = pinned + docs_sidebar

            query_parts = []
            if current_ver:
                query_parts.append(f'v={current_ver}')
            if view_mode == 'list':
                query_parts.append('view=list')

            query_suffix = ''
            if query_parts:
                query_suffix = '?' + '&'.join(query_parts)
            context['doc_query_suffix'] = query_suffix

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

        if page_id == "home.admin_portal.apero_checks_policy" and user_info:
            local_data_dir = app._resolve_local_data_dir()
            checks_cfg = checks_core.load_config(local_data_dir)
            ignored_checks = checks_core.load_ignored_checks(local_data_dir)
            override_allowed = checks_core.load_override_allowed(
                local_data_dir
            )
            context["apero_checks_config"] = {
                "ignored_checks": ignored_checks,
                "override_allowed": override_allowed,
                "checks_root": str(checks_cfg.get("checks_root") or ""),
            }
            # Keep initial page render lightweight. Heavy policy sections
            # are loaded asynchronously via API after first paint.
            context['checks_catalog'] = []
            context['profile_summaries'] = []
            context['policy_last_updated'] = ''
            context['checks_health'] = None
            context['policy_sections_api_url'] = url_for(
                'api_apero_checks_policy_sections'
            )

        if page_id == 'home.admin_portal.apero_check_info' and user_info:
            local_data_dir = app._resolve_local_data_dir()
            checks_cfg = checks_core.load_config(local_data_dir)
            ignored_checks = checks_core.load_ignored_checks(local_data_dir)
            override_allowed = checks_core.load_override_allowed(
                local_data_dir
            )
            payload = _build_apero_policy_payload(
                local_data_dir,
                checks_cfg,
                ignored_checks,
                override_allowed,
            )
            requested_key = str(
                request.args.get('check', '') or ''
            ).strip().upper()
            selected = None
            for item in list(payload.get('checks_catalog', []) or []):
                item_key = str(item.get('check_key') or '').strip().upper()
                if item_key == requested_key and item_key != '':
                    selected = dict(item)
                    break

            if selected is None:
                flash('Please choose a valid APERO check.', 'warning')
                return redirect(
                    url_for('home_admin_portal_apero_checks_policy')
                )

            check_obj = MONITOR_CHECKS.get(selected.get('check_key'))
            profiles_data = load_apero_profiles(hydrate=True)
            if check_obj is not None:
                selected.update(
                    _build_check_info_payload(
                        check_obj,
                        profiles_data=profiles_data,
                    )
                )

            context['apero_check_item'] = selected
            profile_options = []
            for row in list(payload.get('profile_summaries', []) or []):
                profile_id = str(row.get('profile_id') or '').strip()
                if profile_id == '':
                    continue
                profile_options.append(profile_id)
            context['apero_check_profile_options'] = sorted(
                set(profile_options)
            )
            context['apero_checks_config'] = {
                'ignored_checks': ignored_checks,
                'override_allowed': override_allowed,
                'checks_root': str(checks_cfg.get('checks_root') or ''),
            }
            context['policy_last_updated'] = payload.get(
                'policy_last_updated', ''
            )

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
