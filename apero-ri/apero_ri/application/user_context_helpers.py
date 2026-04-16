"""User page context helper functions for ARIApp."""

from flask import jsonify

from apero_ri.core.auth import get_accessible_profiles
from apero_ri.core.auth import load_users
from apero_ri.core.auth import load_science_groups
from apero_ri.core.permissions import get_inherited_groups
from apero_ri.core.permissions import load_parameters
from apero_ri.core import email_backend as eb
from apero_ri.core import user_data as ud
from apero_ri.core import download_tracker as dt
from apero_ri.core import api_tokens as at
from apero_ri.application import instrument_color_helpers


def build_user_data_access_context(app, user_info):
    """Build summary of user's data access by instrument."""
    params = load_parameters()
    all_instr = params.get('instruments', {}).get('value', [])
    user_instr = set(user_info.get('instruments', []))
    if user_instr:
        instruments = [i for i in all_instr if i in user_instr]
    else:
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
        member_groups = []
        run_ids = set()
        for gname, gdata in groups.items():
            if username in gdata.get('users', []):
                member_groups.append(gname)
                for rid in gdata.get('run_ids', []):
                    rid_s = str(rid).strip()
                    if rid_s:
                        run_ids.add(rid_s)

        access_rows.append({
            'instrument': inst,
            'profiles': profiles_by_inst.get(inst, []),
            'science_groups': sorted(member_groups),
            'run_ids': sorted(run_ids),
        })

    return {
        'data_access': access_rows,
    }


def build_user_support_context(app, user_info):
    """Build support contact lists grouped by instrument and role."""
    params = load_parameters()
    all_instr = params.get('instruments', {}).get('value', [])
    user_instr = set(user_info.get('instruments', []))
    if user_instr:
        instruments = [i for i in all_instr if i in user_instr]
    else:
        instruments = list(all_instr)

    users = load_users()
    role_order = ['admin', 'moderator', 'developer', 'monitor']
    role_to_key = {
        'admin': 'admins',
        'moderator': 'moderators',
        'developer': 'developers',
        'monitor': 'monitors',
    }

    support_rows = []
    for inst in instruments:
        grouped = {
            'admins': [],
            'moderators': [],
            'developers': [],
            'monitors': [],
        }

        for username, user_data in users.items():
            u_instr = user_data.get('instruments', [])
            if isinstance(u_instr, str):
                u_instr = [u_instr]
            u_instr = [str(val).strip()
                       for val in (u_instr or [])
                       if str(val).strip()]
            if inst not in u_instr:
                continue

            direct_groups = set(user_data.get('groups', []))
            all_groups = set(direct_groups)
            for group_name in list(direct_groups):
                all_groups |= get_inherited_groups(group_name,
                                                   app.ari_groups)

            role_name = None
            for candidate in role_order:
                if candidate in all_groups:
                    role_name = candidate
                    break
            if role_name is None:
                continue

            first_names = str(user_data.get('first_names', '')).strip()
            last_name = str(user_data.get('last_name', '')).strip()
            full_name = f'{first_names} {last_name}'.strip()
            if not full_name:
                full_name = username

            grouped[role_to_key[role_name]].append({
                'username': username,
                'full_name': full_name,
                'email': str(user_data.get('primary_email', '')).strip(),
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

    return {
        'profile_cards': profile_cards,
        'shown_instruments': shown,
        'instrument_colors': colors,
        'no_profile_instruments': no_profile,
        'sidebar_tree': sidebar_tree,
    }


def build_user_links_context(user_info):
    """Build context for user links page."""
    username = user_info['username']
    params = load_parameters()
    all_instr = params.get('instruments', {}).get('value', [])
    user_instr = user_info.get('instruments', [])
    instruments = (
        [inst for inst in all_instr if inst in user_instr]
        or list(all_instr)
    )
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


def build_user_calendar_context(user_info):
    """Build context for user calendar page."""
    username = user_info['username']
    params = load_parameters()
    all_instr = params.get('instruments', {}).get('value', [])
    user_instr = user_info.get('instruments', [])
    instruments = (
        [inst for inst in all_instr if inst in user_instr]
        or list(all_instr)
    )
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


def build_admin_instrument_context(user_info, perms):
    """Build instruments context for admin calendar/links pages."""
    params = load_parameters()
    all_instr = params.get('instruments', {}).get('value', [])
    can_manage = ('manage.admin.calendar' in perms
                  or 'manage.admin.links' in perms)
    return {
        'instruments': list(all_instr),
        'can_manage': can_manage,
    }
