"""User page context helper functions for ARIApp."""

from pathlib import Path
from urllib.parse import quote

from flask import jsonify, request

from apero_ri.core.auth import get_accessible_profiles
from apero_ri.core.auth import load_users
from apero_ri.core.auth import load_science_groups
from apero_ri.core.permissions import get_inherited_groups
from apero_ri.core.permissions import get_user_instruments
from apero_ri.core.permissions import load_parameters
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import email_backend as eb
from apero_ri.core import user_data as ud
from apero_ri.core import download_tracker as dt
from apero_ri.core import api_tokens as at
from apero_ri.core.issues import create_issue, list_issues
from apero_ri.application import instrument_color_helpers


def build_user_data_access_context(app, user_info):
    """Build summary of user's data access by instrument."""
    perms = resolve_user_permissions(
        user_info.get('groups', []), app.ari_groups
    )
    can_manage_sci_group = 'manage.sci_group' in set(perms or ())

    instruments = get_user_instruments(
        user_info.get('groups', []), app.ari_groups
    )
    if not instruments:
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        instruments = list(all_instr)

    username = user_info.get('username', '')
    accessible_profiles = get_accessible_profiles(
        user_info,
        app.ari_groups,
    )
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
        all_group_names = sorted(groups.keys(), key=lambda item: item.lower())
        member_groups = []
        grouped_run_ids = []
        run_ids = set()
        for gname, gdata in groups.items():
            if username in gdata.get('users', []):
                member_groups.append(gname)
                group_run_ids = set()
                for rid in gdata.get('run_ids', []):
                    rid_s = str(rid).strip()
                    if rid_s:
                        group_run_ids.add(rid_s)
                        run_ids.add(rid_s)
                grouped_run_ids.append(
                    dict(name=gname, run_ids=sorted(group_run_ids))
                )

        grouped_run_ids.sort(key=lambda item: item['name'].lower())

        access_rows.append({
            'instrument': inst,
            'profiles': profiles_by_inst.get(inst, []),
            'science_groups': sorted(member_groups),
            'all_science_groups': all_group_names,
            'run_ids_by_group': grouped_run_ids,
            'run_ids': sorted(run_ids),
        })

    return {
        'data_access': access_rows,
        'can_manage_sci_group': can_manage_sci_group,
    }


def api_user_data_access_request(app):
    """Create a monitor issue from user data-access request form."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    body = request.get_json(silent=True) or {}
    instrument = str(body.get('instrument') or '').strip()
    reason = str(body.get('reason') or '').strip()
    suggested = str(body.get('suggested_science_group') or '').strip()
    run_ids_raw = body.get('run_ids') or []

    if not instrument:
        return jsonify(success=False, error='Missing instrument'), 400
    if not reason:
        return jsonify(success=False, error='Missing reason'), 400
    if len(reason) > 80:
        return jsonify(
            success=False,
            error='Reason must be 80 characters or fewer',
        ), 400

    if isinstance(run_ids_raw, str):
        run_ids_raw = [run_ids_raw]

    normalized_run_ids = []
    for raw in run_ids_raw:
        for part in str(raw or '').split(','):
            run_id = part.strip()
            if run_id and run_id not in normalized_run_ids:
                normalized_run_ids.append(run_id)

    if not normalized_run_ids:
        return jsonify(success=False, error='Add at least one run ID'), 400

    reason_lines = [reason]
    suggested_norm = suggested.strip()
    if suggested_norm and suggested_norm.upper() != 'N/A':
        reason_lines.append(
            'Suggested science group: {0}'.format(suggested_norm)
        )
    issue_reason = '\n'.join(reason_lines)
    issue_title = '{0}: {1}'.format(
        instrument,
        ', '.join(normalized_run_ids),
    )

    origin_url = '/admin_portal/science_groups'
    issue_action = 'Go to Admin Science Groups'

    data_dir = Path(app.args.data_dir or str(Path.home() / '.ari'))
    created_by = user_info.get('username') or 'anonymous'
    run_id_value = ', '.join(normalized_run_ids)

    # De-dupe identical open requests from the same user.
    existing = list_issues(
        data_dir,
        visibility='admin',
        status='open',
        instrument=instrument,
        kind='Data access',
        type_='Request',
        created_by=created_by,
    )
    for row in existing:
        same_title = str(row.get('title') or '').strip() == issue_title
        same_reason = str(row.get('reason') or '').strip() == issue_reason
        same_value = str(row.get('value') or '').strip() == run_id_value
        if same_title and same_reason and same_value:
            return jsonify(success=True, issue=row, deduped=True)

    issue = create_issue(
        data_dir,
        kind='Data access',
        type_='Request',
        reason=issue_reason,
        created_by=created_by,
        instrument=instrument,
        visibility='monitor',
        title=issue_title,
        origin_url=origin_url,
        action=issue_action,
        value=run_id_value,
        label='data-access-request',
    )
    return jsonify(success=True, issue=issue)


def build_user_support_context(app, user_info):
    """Build support contact lists grouped by instrument and role."""
    instruments = get_user_instruments(
        user_info.get('groups', []), app.ari_groups
    )
    if not instruments:
        params = load_parameters()
        all_instr = params.get('instruments', {}).get('value', [])
        instruments = list(all_instr)

    users = load_users()
    role_order = [
        'super_admin', 'admin', 'moderator', 'developer', 'monitor'
    ]
    role_to_key = {
        'super_admin': 'super_admins',
        'admin': 'admins',
        'moderator': 'moderators',
        'developer': 'developers',
        'monitor': 'monitors',
    }

    support_rows = []
    for inst in instruments:
        grouped = {
            'super_admins': [],
            'admins': [],
            'moderators': [],
            'developers': [],
            'monitors': [],
        }

        for username, user_data in users.items():
            direct_groups = set(user_data.get('groups', []))
            all_groups = set(direct_groups)
            for group_name in list(direct_groups):
                all_groups |= get_inherited_groups(
                    group_name, app.ari_groups
                )

            # derive user instruments from groups
            u_instr = get_user_instruments(
                user_data.get('groups', []),
                app.ari_groups,
            )
            is_super_admin = 'super_admin' in all_groups
            if not is_super_admin and inst not in u_instr:
                continue

            role_name = None
            for candidate in role_order:
                # match exact name or instrument-scoped
                cond1 = candidate in all_groups
                scoped = f'{candidate}.{inst}'
                cond2 = scoped in all_groups
                if cond1 or cond2:
                    role_name = candidate
                    break
            if role_name is None:
                continue

            first_names = str(user_data.get('first_names', '')).strip()
            last_name = str(user_data.get('last_name', '')).strip()
            full_name = f'{first_names} {last_name}'.strip()
            if not full_name:
                full_name = username
            primary_email = str(
                user_data.get('primary_email', '')
            ).strip()

            grouped[role_to_key[role_name]].append({
                'username': username,
                'first_names': first_names,
                'last_name': last_name,
                'full_name': full_name,
                'email': primary_email,
                'role': role_name,
                'can_show_email': role_name in (
                    'super_admin',
                    'admin',
                    'moderator',
                    'developer',
                ),
                'profile_url': (
                    '/user_portal/users/' + quote(username, safe='')
                ),
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


def build_ri_context(app, user_info, user_permissions):
    """Build template context for the data portal page."""
    params = load_parameters()
    all_instruments = params.get('instruments', {}).get('value', [])
    colors = app._instrument_colors()
    accessible = get_accessible_profiles(user_info, app.ari_groups)

    shown = list(all_instruments)

    profile_cards = []
    for prof in accessible:
        color = colors.get(
            prof['instrument'],
            instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
        )
        profile_cards.append({
            'instrument': prof['instrument'],
            'profile_id': prof['profile_id'],
            'url': f'/data_portal/{prof["profile_id"]}',
            'color': color,
            'apero_version': prof['data'].get('apero_version', ''),
            'reduction_server': prof['data'].get('reduction_server', ''),
        })

    instruments_with = {p['instrument'] for p in accessible}
    no_profile = [inst for inst in shown if inst not in instruments_with]

    sidebar_tree = app._build_data_portal_sidebar_tree(
        accessible_profiles=accessible,
        active_page_id='home.data_portal',
        user_permissions=user_permissions,
        user_info=user_info,
        include_children=False,
    )

    pset = set(user_permissions or set())
    can_manage_apero_profiles = 'manage.apero_profile' in pset
    can_manage_science_groups = (
        'manage.sci_group' in pset
        or any(
            isinstance(item, str)
            and item.startswith('manage.sci_group.')
            for item in pset
        )
    )

    return {
        'profile_cards': profile_cards,
        'shown_instruments': shown,
        'instrument_colors': colors,
        'no_profile_instruments': no_profile,
        'sidebar_tree': sidebar_tree,
        'can_manage_apero_profiles': can_manage_apero_profiles,
        'can_manage_science_groups': can_manage_science_groups,
    }


def build_user_links_context(app, user_info):
    """Build context for user links page."""
    username = user_info['username']
    instruments = get_user_instruments(
        user_info.get('groups', []), app.ari_groups
    )
    if not instruments:
        params = load_parameters()
        all_instr = params.get(
            'instruments', {}
        ).get('value', [])
        instruments = list(all_instr)
    links_data = ud.load_links(username)
    instr_links = {
        inst: ud.load_instrument_links(inst) for inst in instruments
    }
    return {
        'links_data': links_data,
        'instr_links': instr_links,
        'instruments': instruments,
    }


def build_user_api_access_context(user_info):
    """Build context for user API access page."""
    username = user_info['username']
    api_usage = dt.get_user_usage(username, 'api')
    basket_usage = dt.get_user_usage(username, 'basket')
    token_info = at.get_user_token_info(username)

    def _fmt_ts(raw):
        if not raw:
            return 'Never'
        try:
            from datetime import datetime as _dt
            ts = _dt.fromisoformat(raw)
            return ts.strftime('%d %b %Y, %H:%M UTC')
        except Exception:
            return str(raw)[:19]

    return {
        'token_info': token_info,
        'api_usage': {
            'total_bytes': api_usage.get('total_bytes', 0),
            'total_files': api_usage.get('total_files', 0),
            'total_size_fmt': dt.format_bytes(api_usage.get('total_bytes', 0)),
            'last_download': _fmt_ts(api_usage.get('last_download_at', '')),
        },
        'basket_usage': {
            'total_bytes': basket_usage.get('total_bytes', 0),
            'total_files': basket_usage.get('total_files', 0),
            'total_size_fmt': dt.format_bytes(
                basket_usage.get('total_bytes', 0)
            ),
            'last_download': _fmt_ts(basket_usage.get('last_download_at', '')),
        },
    }


def build_user_calendar_context(app, user_info):
    """Build context for user calendar page."""
    username = user_info['username']
    instruments = get_user_instruments(
        user_info.get('groups', []), app.ari_groups
    )
    if not instruments:
        params = load_parameters()
        all_instr = params.get(
            'instruments', {}
        ).get('value', [])
        instruments = list(all_instr)
    events = ud.list_events(username)
    instr_events = {
        inst: ud.load_instrument_calendar(inst).get('events', [])
        for inst in instruments
    }
    user_tz = ud.get_user_timezone(username)
    try:
        ics_feeds = ud.list_ics_feeds(username)
    except Exception:
        ics_feeds = []
    return {
        'events': events,
        'instr_events': instr_events,
        'instruments': instruments,
        'user_timezone': user_tz,
        'ics_feeds': ics_feeds,
    }


def build_admin_instrument_context(
    user_info, perms, manage_prefix
):
    """Build instruments context for admin calendar/links pages.

    :param manage_prefix: e.g. ``'manage.admin.calendar'`` or
        ``'manage.admin.links'``.  Per-instrument management is
        determined by ``{manage_prefix}.{INSTRUMENT}`` in
        *perms*.
    """
    params = load_parameters()
    all_instr = params.get('instruments', {}).get(
        'value', []
    )
    manageable = [
        i for i in all_instr
        if f"{manage_prefix}.{i}" in perms
    ]
    return {
        'instruments': list(all_instr),
        'can_manage': bool(manageable),
        'manageable_instruments': manageable,
    }
