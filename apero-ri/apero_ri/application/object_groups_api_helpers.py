#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: API handlers for shared object groups.

Permissions
-----------
- Any authenticated user with profile access can list groups and
  add objects to groups.
- Only users with ``monitor.{INSTRUMENT}`` (or higher) can delete
  or rename groups, or remove objects from groups.
- The Object Groups page filters out objects the user cannot see
  (via science-group run_id intersection).
"""
import io
import ast
import html
import json
import math
import queue
import threading
import types
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import numpy as np
try:
    from astropy.time import Time as _AstropyTime
except Exception:
    _AstropyTime = None

from apero_ri.components.target_info_sections import (
    build_target_info_property_catalog,
    flatten_target_info_properties,
)
from apero_ri.core.object_funcs import (
    build_object_page_stats,
    load_object_htable_rows,
)
from apero_ri.application.user_favourites_api_helpers import (
    _load_object_table,
    _name_match_row,
    _resolve_objname,
)
from apero_ri.core import object_groups as og
from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
)
from apero_ri.core.permissions import (
    get_inherited_groups,
    resolve_user_permissions,
)
from flask import jsonify, request, send_file, session

# ================================================================
# Module name
# ================================================================
__NAME__ = 'apero_ri.application.object_groups_api_helpers'


_ALLOWED_STR_METHODS = {
    'upper',
    'lower',
    'title',
    'strip',
    'lstrip',
    'rstrip',
    'replace',
    'split',
    'join',
    'startswith',
    'endswith',
    'find',
    'count',
}

_ALLOWED_BUILTIN_FUNCS = {
    'str',
    'int',
    'float',
    'bool',
    'abs',
    'round',
    'len',
    'min',
    'max',
}

_ALLOWED_EXTRA_FUNCS = {
    'Time',
}

_ALLOWED_TIME_ATTRS = {
    'jd',
    'mjd',
    'iso',
    'isot',
    'jyear',
    'byear',
    'unix',
    'value',
}

_ALLOWED_EXPR_FILENAME = 'allowed_python_expressions.json'
_ADMIN_CUSTOM_COLUMNS_FILENAME = 'custom_columns.json'

_DEFAULT_ALLOWED_EXPRESSION_ROWS = [
    dict(expression='str = str', comment='Convert to string'),
    dict(expression='int = int', comment='Convert to integer'),
    dict(expression='float = float', comment='Convert to float'),
    dict(expression='bool = bool', comment='Convert to boolean'),
    dict(expression='abs = abs', comment='Absolute value'),
    dict(expression='round = round', comment='Round value'),
    dict(expression='len = len', comment='Length of value'),
    dict(expression='min = min', comment='Minimum value'),
    dict(expression='max = max', comment='Maximum value'),
    dict(expression='math = math', comment='Python math module'),
    dict(expression='np = np', comment='NumPy module'),
    dict(expression='sqrt = math.sqrt', comment='Square root'),
    dict(expression='mean = np.mean', comment='Mean value'),
    dict(expression='median = np.median', comment='Median value'),
    dict(expression='Time = astropy.time.Time', comment='Astropy Time'),
    dict(expression='op:+', comment='Addition'),
    dict(expression='op:-', comment='Subtraction'),
    dict(expression='op:*', comment='Multiplication'),
    dict(expression='op:/', comment='Division'),
    dict(expression='op://', comment='Floor division'),
    dict(expression='op:%', comment='Modulo'),
    dict(expression='op:**', comment='Power'),
    dict(expression='op:==', comment='Equal'),
    dict(expression='op:!=', comment='Not equal'),
    dict(expression='op:<', comment='Less than'),
    dict(expression='op:<=', comment='Less or equal'),
    dict(expression='op:>', comment='Greater than'),
    dict(expression='op:>=', comment='Greater or equal'),
    dict(expression='op:u+', comment='Unary plus'),
    dict(expression='op:u-', comment='Unary minus'),
    dict(expression='op:not', comment='Unary not'),
    dict(expression='.upper', comment='String method'),
    dict(expression='.lower', comment='String method'),
    dict(expression='.title', comment='String method'),
    dict(expression='.strip', comment='String method'),
    dict(expression='.lstrip', comment='String method'),
    dict(expression='.rstrip', comment='String method'),
    dict(expression='.replace', comment='String method'),
    dict(expression='.split', comment='String method'),
    dict(expression='.join', comment='String method'),
    dict(expression='.startswith', comment='String method'),
    dict(expression='.endswith', comment='String method'),
    dict(expression='.find', comment='String method'),
    dict(expression='.count', comment='String method'),
    dict(expression='time.jd', comment='Time attribute'),
    dict(expression='time.mjd', comment='Time attribute'),
    dict(expression='time.iso', comment='Time attribute'),
    dict(expression='time.isot', comment='Time attribute'),
    dict(expression='time.jyear', comment='Time attribute'),
    dict(expression='time.byear', comment='Time attribute'),
    dict(expression='time.unix', comment='Time attribute'),
    dict(expression='time.value', comment='Time attribute'),
    dict(expression='time.strftime', comment='Time method'),
    dict(expression='time.to_value', comment='Time method'),
]

_BIN_OP_MAP = {
    '+': ast.Add,
    '-': ast.Sub,
    '*': ast.Mult,
    '/': ast.Div,
    '//': ast.FloorDiv,
    '%': ast.Mod,
    '**': ast.Pow,
}

_CMP_OP_MAP = {
    '==': ast.Eq,
    '!=': ast.NotEq,
    '<': ast.Lt,
    '<=': ast.LtE,
    '>': ast.Gt,
    '>=': ast.GtE,
}

_UNARY_OP_MAP = {
    'u+': ast.UAdd,
    'u-': ast.USub,
    'not': ast.Not,
}

_EXPR_RULES_CACHE = dict(
    path='',
    mtime=-1.0,
    rows=[],
    warnings=[],
    compiled=dict(),
)


class _EvalTimeoutError(Exception):
    """Raised when custom expression evaluation exceeds timeout."""


# ================================================================
# Helpers
# ================================================================
def _can_moderate(user_info, app, instrument):
    """Check if user has monitor.{instrument} privileges."""
    user_groups = set(user_info.get('groups', []))
    all_groups = set(user_groups)
    for g in list(user_groups):
        all_groups |= get_inherited_groups(g, app.ari_groups)
    target = 'monitor.{}'.format(instrument)
    return target in all_groups


def _resolve_profile(app, user_info, profile_id):
    """Find an accessible profile or return None."""
    accessible = get_accessible_profiles(
        user_info, app.ari_groups
    )
    for prof in accessible:
        if prof['profile_id'] == profile_id:
            return prof
    return None


def _resolve_query(app, profile, query):
    """Resolve *query* to (objname, nickname, error, candidates).

    Returns a 4-tuple:
    - objname:    canonical APERO name (or None on failure)
    - nickname:   the user-typed query when it differs from objname
    - error:      error string (or None on success)
    - candidates: list of partial-match names (or [])
    """
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    instrument = profile['instrument']
    profile_id = profile['profile_id']

    rows = _load_object_table(
        base_dir, instrument, profile_id
    )
    if rows is None:
        # No object table — accept query as literal
        return query, '', None, []

    resolved = _resolve_objname(rows, query)
    if resolved is not None:
        if resolved.upper() == query.strip().upper():
            nickname = ''
        else:
            nickname = query.strip()
        return resolved, nickname, None, []

    # Direct exact OBJNAME match (belt-and-suspenders)
    exact = [
        r for r in rows
        if (str(r.get('OBJNAME', '')).strip().upper()
            == query.upper())
    ]
    if exact:
        return str(exact[0]['OBJNAME']).strip(), '', None, []

    partial = [
        str(r['OBJNAME']).strip()
        for r in rows
        if _name_match_row(r, query)
    ]
    if not partial:
        msg = (
            "Object '{}' not found in profile "
            "'{}'.".format(query, profile_id)
        )
        return None, '', msg, []

    if len(partial) > 1:
        msg = (
            "Query '{}' matches multiple objects."
            .format(query)
        )
        return None, '', msg, partial[:20]

    nickname = (
        '' if partial[0].upper() == query.strip().upper()
        else query.strip()
    )
    return partial[0], nickname, None, []


def _summary_catalog_items():
    """Return summary-property catalog and lookup by property ID."""
    catalog = build_target_info_property_catalog()
    counts = dict()
    for item in catalog:
        label = str(item.get('label') or item.get('id') or '').strip()
        counts[label] = counts.get(label, 0) + 1

    out = []
    by_id = dict()
    for item in catalog:
        clean = dict(item)
        label = str(
            clean.get('label') or clean.get('id') or ''
        ).strip()
        section_title = str(
            clean.get('section_title') or ''
        ).strip()
        if counts.get(label, 0) > 1 and section_title:
            display_label = '{0} ({1})'.format(
                label, section_title
            )
        else:
            display_label = label
        clean['display_label'] = display_label
        out.append(clean)
        by_id[clean['id']] = clean
    return out, by_id


def _humanize_key(text):
    """Return a compact display label from a snake/camel key."""
    raw = str(text or '').strip()
    if not raw:
        return ''
    out = raw.replace('_', ' ')
    out = out.replace('::', ': ')
    out = out.replace('  ', ' ')
    return out


def _section_title(section_key):
    """Return display title for a section key."""
    names = dict(
        target_info='target info',
        admin_custom='Custom',
        header='header',
        spectrum='spectrum',
        lbl='lbl stats',
        ccf='ccf',
        time_series='time series',
        debug='debug',
    )
    return names.get(section_key, _humanize_key(section_key).lower())


def _property_parts(section_key, prefix, prop_label):
    """Return category/sub-category/LBL category/property parts."""
    category = _section_title(section_key)
    subcategory = 'general'
    lbl_category = ''

    tokens = [str(part) for part in prefix]
    prop_tokens = list(tokens)

    if section_key == 'target_info':
        subcategory = 'target info'
        prop_tokens = [str(prop_label)]
    elif (
        section_key == 'lbl'
        and len(tokens) >= 3
        and tokens[0] == 'flavors'
    ):
        subcategory = 'flavors'
        lbl_category = str(tokens[1])
        prop_tokens = tokens[2:]
    elif len(tokens) >= 2:
        subcategory = _humanize_key(tokens[0]).lower()
        prop_tokens = tokens[1:]
    elif len(tokens) == 1:
        subcategory = 'general'
        prop_tokens = tokens

    property_name = _humanize_key(':'.join(prop_tokens)).strip()
    if not property_name:
        property_name = _humanize_key(str(prop_label)).strip() or 'value'

    hierarchy = [category, subcategory]
    if lbl_category:
        hierarchy.append(lbl_category)
    hierarchy_text = ' / '.join(
        part for part in hierarchy if str(part).strip()
    )

    return dict(
        category=category,
        subcategory=subcategory,
        lbl_category=lbl_category,
        property_name=property_name,
        hierarchy=hierarchy_text,
    )


def _display_label(meta):
    """Return default column label for one summary property."""
    return str(meta.get('property_name') or '').strip()


def _is_lbl_self_pair(flavor_id):
    """Return True when flavor_id matches science_companion self-pair."""
    text = str(flavor_id or '').strip()
    if not text:
        return False
    parts = text.split('_')
    if len(parts) != 2:
        return False
    return parts[0].strip() == parts[1].strip()


def _add_property(
    out,
    prop_id,
    section_key,
    prop_label,
    value,
    prefix=None,
    subcategory=None,
    preserve_raw=False,
):
    """Insert one flattened property into *out*."""
    if prefix is None:
        prefix = []
    meta = _property_parts(section_key, prefix, prop_label)
    if subcategory:
        meta['subcategory'] = str(subcategory).strip().lower()
        meta['hierarchy'] = ' / '.join(
            part
            for part in [
                meta['category'],
                meta['subcategory'],
                meta.get('lbl_category', ''),
            ]
            if str(part).strip()
        )
    display = _display_label(meta)
    out[prop_id] = dict(
        id=prop_id,
        label=display,
        property_name=meta['property_name'],
        category=meta['category'],
        subcategory=meta['subcategory'],
        lbl_category=meta['lbl_category'],
        hierarchy=meta['hierarchy'],
        token=prop_id,
        section_id=section_key,
        section_title=meta['category'],
        section_description='',
        units='',
        value=value if preserve_raw else _summary_value(value),
    )


def _add_time_series_binned_properties(out, rows):
    """Add time-series values aggregated by observation directory."""
    if not isinstance(rows, list):
        return

    skip_keys = {
        'obs_dir',
        'ext_files_label',
        'tcorr_files_label',
        'request_ext_files',
        'request_tcorr_files',
    }
    grouped = dict()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            text_key = str(key or '').strip()
            if (not text_key) or (text_key in skip_keys):
                continue
            if value is None:
                continue
            grouped.setdefault(text_key, []).append(value)

    for key in sorted(grouped.keys()):
        values = grouped.get(key, [])
        if not values:
            continue
        label = '{0} [binned by observation directory]'.format(
            _humanize_key(key),
        )
        prop_id = 'time_series::binned::{0}'.format(key)
        out[prop_id] = dict(
            id=prop_id,
            label=label,
            property_name=label,
            category='time series',
            subcategory='binned by observation directory',
            lbl_category='',
            hierarchy='time series / binned by observation directory',
            token=prop_id,
            section_id='time_series',
            section_title='time series',
            section_description='',
            units='',
            value=values,
        )


def _add_header_summary_properties(app, profile, objname, props):
    """Add htable-backed header values from the first available row."""
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    objects_dir = (
        base_dir
        / 'tasks'
        / str(profile.get('instrument', '')).strip()
        / str(profile.get('profile_id', '')).strip()
        / 'objects'
    )
    rows = load_object_htable_rows(objects_dir, objname)
    first_row = None
    for row in rows:
        if isinstance(row, dict):
            first_row = row
            break
    if not isinstance(first_row, dict):
        return

    for key in sorted(first_row.keys()):
        text_key = str(key or '').strip()
        if not text_key:
            continue
        prop_id = 'header::{0}'.format(text_key)
        _add_property(
            props,
            prop_id,
            'header',
            _humanize_key(text_key),
            first_row.get(key),
            prefix=[text_key],
            subcategory='htable',
        )


def _add_admin_custom_summary_properties(app, profile, props):
    """Add persisted admin custom columns as summary properties."""
    local_data_dir = app._resolve_local_data_dir()
    catalog_map = {
        str(prop_id): dict(id=str(prop_id))
        for prop_id in props.keys()
    }
    rows_raw = _admin_custom_profile_rows(
        local_data_dir,
        profile.get('profile_id', ''),
    )
    for row in rows_raw:
        if not isinstance(row, dict):
            continue
        name = str(row.get('name', '')).strip()
        if not name:
            continue
        pid = 'admin_custom::{0}'.format(name)
        catalog_map[pid] = dict(id=pid)

    _seed_catalog_with_custom_var_ids(catalog_map, rows_raw)

    rows = _normalise_custom_columns(rows_raw, catalog_map)
    if not rows:
        return

    expr_rules, _, _ = _get_compiled_expression_rules(local_data_dir)
    row_map = dict()
    for row in rows:
        name = str(row.get('name', '')).strip()
        if not name:
            continue
        row_map['admin_custom::{0}'.format(name)] = row

    for prop_id in sorted(row_map.keys()):
        row = row_map[prop_id]
        name = str(row.get('name', '')).strip()
        value = _resolve_admin_custom_test_value(
            prop_id,
            props,
            row_map,
            expr_rules,
        )
        _add_property(
            props,
            prop_id,
            'admin_custom',
            name,
            value,
            prefix=[name],
            subcategory='admin custom',
            preserve_raw=True,
        )


def _flatten_section_values(out, section_key, prefix, value):
    """Flatten nested section data into summary properties."""
    if value is None:
        return
    if isinstance(value, dict):
        for key in sorted(value.keys()):
            if key in {'ext_files_label', 'tcorr_files_label'}:
                continue
            _flatten_section_values(
                out,
                section_key,
                prefix + [str(key)],
                value.get(key),
            )
        return
    if isinstance(value, list):
        if not value:
            return
        if all(isinstance(item, dict) for item in value):
            if section_key == 'time_series':
                _add_time_series_binned_properties(out, value)
                return
            for idx, item in enumerate(value):
                obj_key = str(
                    item.get('obs_dir')
                    or item.get('flavor_id')
                    or item.get('id')
                    or str(idx + 1)
                )
                if (
                    section_key == 'lbl'
                    and len(prefix) == 1
                    and prefix[0] == 'flavors'
                ):
                    if not _is_lbl_self_pair(obj_key):
                        continue
                _flatten_section_values(
                    out,
                    section_key,
                    prefix + [obj_key],
                    item,
                )
        else:
            prop_id = '{0}::{1}'.format(
                section_key,
                ':'.join(prefix),
            )
            _add_property(
                out,
                prop_id,
                section_key,
                _humanize_key(':'.join(prefix)),
                value,
                prefix=prefix,
            )
        return

    prop_id = '{0}::{1}'.format(
        section_key,
        ':'.join(prefix),
    )
    _add_property(
        out,
        prop_id,
        section_key,
        _humanize_key(':'.join(prefix)),
        value,
        prefix=prefix,
    )


def _add_lbl_uncertainties(out, lbl_info):
    """Add explicit per-flavor LBL uncertainty percentile properties."""
    flavors = lbl_info.get('flavors', [])
    if not isinstance(flavors, list):
        return
    for flavor in flavors:
        if not isinstance(flavor, dict):
            continue
        flavor_id = str(flavor.get('flavor_id') or '').strip()
        if not flavor_id:
            continue
        unc = flavor.get('rv_uncertainty_percentiles')
        if isinstance(unc, dict):
            for ukey, uval in unc.items():
                if uval is None:
                    continue
                pname = '{0}:Uncertainty:{1}'.format(
                    flavor_id,
                    str(ukey),
                )
                pid = 'lbl::{0}'.format(pname)
                _add_property(
                    out,
                    pid,
                    'lbl',
                    pname,
                    uval,
                )


def _collect_object_summary_properties(
    app,
    profile,
    obj_row,
    objname,
    accessible_rids,
):
    """Return full summary properties for one object."""
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    profile_data = profile.get('data') or {}
    instrument_profile_file = str(
        profile_data.get('APERO_INSTRUMENT_PROFILE', '')
        or profile_data.get('apero_instrument_profile', '')
        or ''
    ).strip()
    path_lbl = str(
        app._profile_get_path(profile_data, 'PATH_LBL', '') or ''
    ).strip()

    props = dict()
    # Canonical target-info properties
    entry = _load_astrometric_entry(app, objname)
    target_props = flatten_target_info_properties(entry, obj_row)
    for item in target_props.values():
        prop_id = 'target_info::{0}'.format(item['id'])
        _add_property(
            props,
            prop_id,
            'target_info',
            item.get('label') or item.get('id'),
            item.get('value'),
            prefix=[str(item.get('id') or '')],
            subcategory=item.get('section_title') or 'target info',
        )

    sections = build_object_page_stats(
        base_dir=base_dir,
        instrument=profile['instrument'],
        profile_id=profile['profile_id'],
        obj_row=obj_row,
        objname=objname,
        accessible_run_ids=accessible_rids,
        instrument_profile_file=instrument_profile_file,
        path_lbl=path_lbl,
    )
    for section_key in [
        'spectrum',
        'lbl',
        'ccf',
        'time_series',
        'debug',
    ]:
        section_val = sections.get(section_key)
        if section_val is None:
            continue
        _flatten_section_values(
            props,
            section_key,
            [],
            section_val,
        )

    _add_header_summary_properties(
        app,
        profile,
        objname,
        props,
    )
    _add_admin_custom_summary_properties(
        app,
        profile,
        props,
    )

    return props


def _normalise_summary_columns(columns, catalog_map):
    """Return the valid, de-duplicated summary property IDs."""
    result = []
    seen = set()
    for column in columns:
        text = str(column).strip()
        if text and ('::' not in text):
            legacy = 'target_info::{0}'.format(text)
            if legacy in catalog_map:
                text = legacy
        if not text or text in seen:
            continue
        if text not in catalog_map:
            continue
        seen.add(text)
        result.append(text)
    return result


def _summary_value(value):
    """Normalise values for summary-table display and export."""
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(str(item) for item in value if item is not None)
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, dict):
        parts = []
        for key, val in value.items():
            parts.append('{0}={1}'.format(key, val))
        return ', '.join(parts)
    return str(value)


def _is_null_value(value):
    """Return True for null-like values used in custom columns."""
    if value is None:
        return True
    if isinstance(value, str) and (not value.strip()):
        return True
    if isinstance(value, (list, tuple)) and (len(value) == 0):
        return True
    if isinstance(value, np.ndarray) and (value.size == 0):
        return True
    return False


def _is_number_value(value):
    """Return True when *value* is numeric and not boolean."""
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float, np.number))


def _allowed_expr_rules_path(local_data_dir):
    """Return JSON path used for allowed expression rows."""
    return (
        Path(local_data_dir)
        / 'monitor_apero_checks'
        / _ALLOWED_EXPR_FILENAME
    )


def _default_allowed_expression_rows():
    """Return fresh default rows for allowed expression rules."""
    out = []
    for row in _DEFAULT_ALLOWED_EXPRESSION_ROWS:
        out.append(dict(
            expression=str(row.get('expression', '')).strip(),
            comment=str(row.get('comment', '')).strip(),
        ))
    return out


def _normalise_allowed_expression_rows(rows):
    """Normalise allowed expression rows from JSON payload/file."""
    out = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if isinstance(row, str):
            expr = str(row).strip()
            comment = ''
        elif isinstance(row, dict):
            expr = str(row.get('expression', '')).strip()
            comment = str(row.get('comment', '')).strip()
        else:
            continue
        if not expr:
            continue
        out.append(dict(expression=expr, comment=comment))
    return out


def _load_allowed_expression_rows(local_data_dir):
    """Load persisted allowed expression rows (or defaults)."""
    path = _allowed_expr_rules_path(local_data_dir)
    defaults = _default_allowed_expression_rows()
    if not path.exists():
        return defaults

    rows = []
    try:
        with path.open('r', encoding='utf-8') as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            rows = _normalise_allowed_expression_rows(
                payload.get('rows', [])
            )
        else:
            rows = _normalise_allowed_expression_rows(payload)
    except Exception:
        rows = []

    if not rows:
        return defaults

    merged = []
    seen = set()
    for row in rows + defaults:
        expr = str(row.get('expression', '')).strip()
        if not expr or expr in seen:
            continue
        merged.append(dict(
            expression=expr,
            comment=str(row.get('comment', '')).strip(),
        ))
        seen.add(expr)
    return merged


def _save_allowed_expression_rows(local_data_dir, rows):
    """Persist allowed expression rows atomically."""
    clean_rows = _normalise_allowed_expression_rows(rows)
    if not clean_rows:
        clean_rows = _default_allowed_expression_rows()

    path = _allowed_expr_rules_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(
        version=1,
        updated_at=datetime.now(timezone.utc).isoformat(),
        rows=clean_rows,
    )
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with tmp_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2)
    tmp_path.replace(path)
    return clean_rows


def _admin_custom_columns_path(local_data_dir):
    """Return JSON path used for persisted admin custom columns."""
    return (
        Path(local_data_dir)
        / 'monitor_apero_checks'
        / _ADMIN_CUSTOM_COLUMNS_FILENAME
    )


def _load_admin_custom_columns(local_data_dir):
    """Load persisted admin custom columns payload from disk."""
    path = _admin_custom_columns_path(local_data_dir)
    if not path.exists():
        return dict(
            rows_by_profile=dict(),
            test_object_by_profile=dict(),
            legacy_rows=[],
        )

    rows_by_profile = dict()
    test_object_by_profile = dict()
    legacy_rows = []
    try:
        with path.open('r', encoding='utf-8') as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            raw_by_profile = payload.get('rows_by_profile', dict())
            if isinstance(raw_by_profile, dict):
                for key, value in raw_by_profile.items():
                    pid = str(key or '').strip()
                    if not pid or not isinstance(value, list):
                        continue
                    rows_by_profile[pid] = value

            raw_test_objects = payload.get(
                'test_object_by_profile',
                dict(),
            )
            if isinstance(raw_test_objects, dict):
                for key, value in raw_test_objects.items():
                    pid = str(key or '').strip()
                    if not pid:
                        continue
                    test_object_by_profile[pid] = str(value or '').strip()

            raw_legacy = payload.get('legacy_rows', payload.get('rows', []))
            if isinstance(raw_legacy, list):
                legacy_rows = raw_legacy
        else:
            if isinstance(payload, list):
                legacy_rows = payload
    except Exception:
        rows_by_profile = dict()
        test_object_by_profile = dict()
        legacy_rows = []

    return dict(
        rows_by_profile=rows_by_profile,
        test_object_by_profile=test_object_by_profile,
        legacy_rows=legacy_rows,
    )


def _admin_custom_profile_rows(local_data_dir, profile_id):
    """Return persisted admin custom columns for one profile."""
    payload = _load_admin_custom_columns(local_data_dir)
    pid = str(profile_id or '').strip()
    rows_by_profile = payload.get('rows_by_profile', dict())
    legacy_rows = payload.get('legacy_rows', [])
    if pid and isinstance(rows_by_profile, dict):
        rows = rows_by_profile.get(pid)
        if isinstance(rows, list):
            return rows
    if isinstance(legacy_rows, list):
        return legacy_rows
    return []


def _admin_custom_profile_test_object(local_data_dir, profile_id):
    """Return remembered test object for one profile."""
    payload = _load_admin_custom_columns(local_data_dir)
    pid = str(profile_id or '').strip()
    test_map = payload.get('test_object_by_profile', dict())
    if not pid or not isinstance(test_map, dict):
        return ''
    return str(test_map.get(pid, '') or '').strip()


def _save_admin_custom_columns(
    local_data_dir,
    profile_id,
    rows=None,
    default_test_object=None,
):
    """Persist admin custom columns atomically for one profile."""
    payload_in = _load_admin_custom_columns(local_data_dir)
    rows_by_profile = payload_in.get('rows_by_profile', dict())
    test_object_by_profile = payload_in.get(
        'test_object_by_profile',
        dict(),
    )
    legacy_rows = payload_in.get('legacy_rows', [])
    if not isinstance(rows_by_profile, dict):
        rows_by_profile = dict()
    if not isinstance(test_object_by_profile, dict):
        test_object_by_profile = dict()
    if not isinstance(legacy_rows, list):
        legacy_rows = []

    pid = str(profile_id or '').strip()
    if pid and rows is not None:
        rows_by_profile[pid] = list(rows or [])
    if pid and default_test_object is not None:
        test_object_by_profile[pid] = str(
            default_test_object or '',
        ).strip()

    path = _admin_custom_columns_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(
        version=3,
        updated_at=datetime.now(timezone.utc).isoformat(),
        rows_by_profile=rows_by_profile,
        test_object_by_profile=test_object_by_profile,
        legacy_rows=legacy_rows,
    )
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with tmp_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2)
    tmp_path.replace(path)


def _build_admin_custom_catalog(app, user_info, profile_id=''):
    """Build broad summary-property catalog for admin custom-column editor."""
    catalog_map = dict()

    base_catalog, _ = _summary_catalog_items()
    for item in base_catalog:
        pid = 'target_info::{0}'.format(item['id'])
        merged = dict(item)
        merged['id'] = pid
        merged['token'] = pid
        merged['label'] = item['label']
        merged['property_name'] = item.get('label') or item['id']
        merged['category'] = 'target info'
        merged['subcategory'] = 'target info'
        merged['lbl_category'] = ''
        merged['hierarchy'] = 'target info / target info'
        merged['section_id'] = 'target_info'
        merged['section_title'] = 'target info'
        catalog_map[pid] = merged

    local_data_dir = app._resolve_local_data_dir()
    for row in _admin_custom_profile_rows(local_data_dir, profile_id):
        if not isinstance(row, dict):
            continue
        name = str(row.get('name', '')).strip()
        if not name:
            continue
        pid = 'admin_custom::{0}'.format(name)
        if pid in catalog_map:
            continue
        catalog_map[pid] = dict(
            id=pid,
            label=name,
            property_name=name,
            category='Custom',
            subcategory='admin custom',
            lbl_category='',
            hierarchy='Custom / admin custom',
            token=pid,
            section_id='admin_custom',
            section_title='Custom',
            section_description='Saved admin custom column',
            units='',
        )

    profiles = get_accessible_profiles(
        user_info,
        app.ari_groups,
    )
    target_profile = str(profile_id or '').strip()
    if target_profile:
        profiles = [
            profile
            for profile in list(profiles or [])
            if str(profile.get('profile_id', '')).strip() == target_profile
        ]
    for profile in list(profiles or []):
        instrument = str(profile.get('instrument') or '').strip()
        if not instrument:
            continue
        accessible_rids = app._get_user_accessible_run_ids(
            user_info,
            instrument,
        )
        obj_rows = _load_profile_object_row_map(app, profile)
        row_items = list(obj_rows.items())[:40]
        for objname, obj_row in row_items:
            props = _collect_object_summary_properties(
                app,
                profile,
                obj_row,
                objname,
                accessible_rids,
            )
            for pid, item in props.items():
                if pid in catalog_map:
                    continue
                section_id = str(item.get('section_id') or '').strip().lower()
                category = str(
                    item.get('category') or item.get('section_title') or ''
                ).strip().lower()
                subcategory = str(
                    item.get('subcategory') or ''
                ).strip().lower()
                if section_id == 'lbl':
                    continue
                if category == 'lbl stats' or subcategory == 'flavors':
                    continue
                catalog_map[pid] = dict(
                    id=pid,
                    label=item.get('label') or pid,
                    property_name=(
                        item.get('property_name')
                        or item.get('label')
                        or pid
                    ),
                    category=(
                        item.get('category')
                        or item.get('section_title')
                        or ''
                    ),
                    subcategory=item.get('subcategory') or 'general',
                    lbl_category=item.get('lbl_category') or '',
                    hierarchy=item.get('hierarchy') or '',
                    token=pid,
                    section_id=item.get('section_id') or '',
                    section_title=item.get('section_title') or '',
                    section_description='',
                    units=item.get('units') or '',
                )

    return [
        catalog_map[key]
        for key in sorted(catalog_map.keys())
    ]


def _resolve_allowed_target(target):
    """Resolve one safe target path used by allow-rule aliases."""
    cleaned = str(target or '').strip()
    if not cleaned:
        return None

    astropy_ns = _astropy_namespace()
    safe_map = dict(
        str=str,
        int=int,
        float=float,
        bool=bool,
        abs=abs,
        round=round,
        len=len,
        min=min,
        max=max,
        math=math,
        np=np,
        **{
            'math.sqrt': math.sqrt,
            'np.mean': np.mean,
            'np.median': np.median,
            'astropy': astropy_ns,
            'astropy.time.Time': _AstropyTime,
        }
    )
    value = safe_map.get(cleaned)
    if value is None:
        return None
    return value


def _compile_allowed_expression_rows(rows):
    """Compile rows into validator/evaluator rule structures."""
    warnings = []
    env = dict(__builtins__=dict())
    callables = set()
    allowed_names = set()
    module_roots = set()
    str_methods = set()
    time_attrs = set()
    bin_ops = set()
    cmp_ops = set()
    unary_ops = set()

    for row in _normalise_allowed_expression_rows(rows):
        expr = str(row.get('expression', '')).strip()
        if not expr:
            continue

        if expr.startswith('.'):
            method_name = expr[1:].strip()
            if method_name.isidentifier():
                str_methods.add(method_name)
            else:
                warnings.append(
                    'Invalid string method rule: {0}'.format(expr)
                )
            continue

        if expr.startswith('time.'):
            attr_name = expr[5:].strip()
            if attr_name.isidentifier():
                time_attrs.add(attr_name)
            else:
                warnings.append(
                    'Invalid time attribute rule: {0}'.format(expr)
                )
            continue

        if expr.startswith('op:'):
            token = expr[3:].strip()
            if token in _BIN_OP_MAP:
                bin_ops.add(_BIN_OP_MAP[token])
                continue
            if token in _CMP_OP_MAP:
                cmp_ops.add(_CMP_OP_MAP[token])
                continue
            if token in _UNARY_OP_MAP:
                unary_ops.add(_UNARY_OP_MAP[token])
                continue
            warnings.append('Unknown operator rule: {0}'.format(expr))
            continue

        alias = ''
        target = ''
        if '=' in expr:
            parts = expr.split('=', 1)
            alias = str(parts[0]).strip()
            target = str(parts[1]).strip()
        else:
            alias = expr
            target = expr

        if not alias.isidentifier():
            warnings.append('Invalid alias rule: {0}'.format(expr))
            continue

        value = _resolve_allowed_target(target)
        if value is None:
            warnings.append('Unknown target in rule: {0}'.format(expr))
            continue

        env[alias] = value
        allowed_names.add(alias)
        if callable(value):
            callables.add(alias)
        if isinstance(value, (types.ModuleType, types.SimpleNamespace)):
            module_roots.add(alias)

    compiled = dict(
        env=env,
        callables=callables,
        allowed_names=allowed_names,
        module_roots=module_roots,
        allowed_str_methods=str_methods,
        allowed_time_attrs=time_attrs,
        allowed_bin_ops=tuple(bin_ops),
        allowed_cmp_ops=tuple(cmp_ops),
        allowed_unary_ops=tuple(unary_ops),
    )
    return compiled, warnings


def _get_compiled_expression_rules(local_data_dir):
    """Return compiled expression rules with simple file-mtime cache."""
    path = _allowed_expr_rules_path(local_data_dir)
    path_text = str(path)
    mtime = -1.0
    if path.exists():
        try:
            mtime = float(path.stat().st_mtime)
        except Exception:
            mtime = -1.0

    cached = _EXPR_RULES_CACHE
    if (
        cached.get('path') == path_text
        and float(cached.get('mtime', -1.0)) == mtime
        and isinstance(cached.get('compiled'), dict)
        and cached.get('compiled')
    ):
        return (
            cached.get('compiled'),
            cached.get('rows', []),
            cached.get('warnings', []),
        )

    rows = _load_allowed_expression_rows(local_data_dir)
    compiled, warnings = _compile_allowed_expression_rows(rows)
    _EXPR_RULES_CACHE['path'] = path_text
    _EXPR_RULES_CACHE['mtime'] = mtime
    _EXPR_RULES_CACHE['rows'] = rows
    _EXPR_RULES_CACHE['warnings'] = warnings
    _EXPR_RULES_CACHE['compiled'] = compiled
    return compiled, rows, warnings


def _validate_expr_node(node, var_names, rules):
    """Validate AST node for safe custom expressions."""
    allowed_bin = tuple(rules.get('allowed_bin_ops', tuple()))
    allowed_unary = tuple(rules.get('allowed_unary_ops', tuple()))
    allowed_cmp = tuple(rules.get('allowed_cmp_ops', tuple()))
    allowed_names = set(rules.get('allowed_names', set()))
    allowed_callables = set(rules.get('callables', set()))
    allowed_modules = set(rules.get('module_roots', set()))
    allowed_methods = set(rules.get('allowed_str_methods', set()))
    allowed_time_attrs = set(rules.get('allowed_time_attrs', set()))

    def _is_allowed_module_chain(attr_node):
        current = attr_node
        while isinstance(current, ast.Attribute):
            if str(current.attr).startswith('__'):
                return False
            current = current.value
        if isinstance(current, ast.Name):
            return current.id in allowed_modules
        return False

    if isinstance(node, ast.Expression):
        return _validate_expr_node(node.body, var_names, rules)

    if isinstance(node, ast.Constant):
        return True, ''

    if isinstance(node, ast.Name):
        allowed = set(var_names) | allowed_names
        if node.id in allowed:
            return True, ''
        return False, 'Unknown variable or function: {0}'.format(node.id)

    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, allowed_bin):
            return False, 'Operator not allowed.'
        ok, msg = _validate_expr_node(node.left, var_names, rules)
        if not ok:
            return ok, msg
        return _validate_expr_node(node.right, var_names, rules)

    if isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, allowed_unary):
            return False, 'Unary operator not allowed.'
        return _validate_expr_node(node.operand, var_names, rules)

    if isinstance(node, ast.BoolOp):
        for value in node.values:
            ok, msg = _validate_expr_node(value, var_names, rules)
            if not ok:
                return ok, msg
        return True, ''

    if isinstance(node, ast.Compare):
        for op in node.ops:
            if not isinstance(op, allowed_cmp):
                return False, 'Comparison operator not allowed.'
        ok, msg = _validate_expr_node(node.left, var_names, rules)
        if not ok:
            return ok, msg
        for comp in node.comparators:
            ok, msg = _validate_expr_node(comp, var_names, rules)
            if not ok:
                return ok, msg
        return True, ''

    if isinstance(node, ast.IfExp):
        ok, msg = _validate_expr_node(node.test, var_names, rules)
        if not ok:
            return ok, msg
        ok, msg = _validate_expr_node(node.body, var_names, rules)
        if not ok:
            return ok, msg
        return _validate_expr_node(node.orelse, var_names, rules)

    if isinstance(node, ast.Attribute):
        if str(node.attr).startswith('__'):
            return False, 'Dunder attributes are not allowed.'
        if _is_allowed_module_chain(node):
            return True, ''
        if isinstance(node.value, ast.Name):
            if node.value.id in allowed_modules:
                return True, ''
        ok, msg = _validate_expr_node(node.value, var_names, rules)
        if not ok:
            return ok, msg
        if node.attr in allowed_methods:
            return True, ''
        if node.attr in allowed_time_attrs:
            return True, ''
        return False, 'Method not allowed: {0}'.format(node.attr)

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id not in allowed_callables:
                return False, 'Function not allowed: {0}'.format(
                    node.func.id
                )
        elif isinstance(node.func, ast.Attribute):
            ok, msg = _validate_expr_node(node.func, var_names, rules)
            if not ok:
                return ok, msg
        else:
            return False, 'Callable expression not allowed.'

        for arg in node.args:
            ok, msg = _validate_expr_node(arg, var_names, rules)
            if not ok:
                return ok, msg
        for keyword in node.keywords:
            ok, msg = _validate_expr_node(
                keyword.value,
                var_names,
                rules,
            )
            if not ok:
                return ok, msg
        return True, ''

    if isinstance(node, ast.Subscript):
        ok, msg = _validate_expr_node(node.value, var_names, rules)
        if not ok:
            return ok, msg
        if isinstance(node.slice, ast.Slice):
            parts = [
                node.slice.lower,
                node.slice.upper,
                node.slice.step,
            ]
            for part in parts:
                if part is None:
                    continue
                ok, msg = _validate_expr_node(part, var_names, rules)
                if not ok:
                    return ok, msg
            return True, ''
        # Python 3.8 uses ast.Index around direct index expressions.
        if hasattr(ast, 'Index') and isinstance(node.slice, ast.Index):
            return _validate_expr_node(node.slice.value, var_names, rules)
        # Python 3.9+ stores direct index nodes in node.slice
        # (e.g. x[0], x['key']); validate index expression recursively.
        return _validate_expr_node(node.slice, var_names, rules)

    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            ok, msg = _validate_expr_node(elt, var_names, rules)
            if not ok:
                return ok, msg
        return True, ''

    return False, 'Expression element not allowed: {0}'.format(
        type(node).__name__
    )


def _contains_time_name(node):
    """Return True when AST uses ``Time`` or ``astropy.time.Time``."""
    for subnode in ast.walk(node):
        if isinstance(subnode, ast.Name) and subnode.id == 'Time':
            return True
        if isinstance(subnode, ast.Attribute):
            if (
                isinstance(subnode.value, ast.Attribute)
                and isinstance(subnode.value.value, ast.Name)
                and subnode.value.value.id == 'astropy'
                and subnode.value.attr == 'time'
                and subnode.attr == 'Time'
            ):
                return True
    return False


def _astropy_namespace():
    """Return a minimal astropy namespace for safe eval."""
    if _AstropyTime is None:
        return None
    return types.SimpleNamespace(
        time=types.SimpleNamespace(Time=_AstropyTime)
    )


def _with_eval_timeout(timeout_sec, callback):
    """Run callback with a thread-safe timeout."""
    if timeout_sec <= 0:
        return callback()

    result_queue = queue.Queue(maxsize=1)

    def _runner():
        try:
            result = callback()
            result_queue.put((True, result))
        except Exception as exc:
            result_queue.put((False, exc))

    worker = threading.Thread(target=_runner, daemon=True)
    worker.start()
    worker.join(float(timeout_sec))
    if worker.is_alive():
        raise _EvalTimeoutError('Expression timed out')

    try:
        ok, payload = result_queue.get_nowait()
    except queue.Empty:
        raise _EvalTimeoutError('Expression timed out')

    if ok:
        return payload
    raise payload


def _eval_custom_expression(expression, var_values, rules):
    """Evaluate one custom expression with strict safety checks."""
    values = dict(var_values)
    for value in values.values():
        if _is_null_value(value):
            return '', None

    try:
        tree = ast.parse(str(expression), mode='eval')
    except SyntaxError as exc:
        msg = str(exc.msg or 'invalid syntax')
        if exc.lineno and exc.offset:
            return None, 'Syntax error at {0}:{1}: {2}'.format(
                exc.lineno,
                exc.offset,
                msg,
            )
        return None, 'Syntax error: {0}'.format(msg)
    except Exception as exc:
        return None, 'Expression parse error: {0}'.format(str(exc))

    names = set(values.keys())
    valid, reason = _validate_expr_node(tree, names, rules)
    if not valid:
        return None, 'Expression not allowed: {0}'.format(reason)

    env = dict(rules.get('env', dict()))

    if _contains_time_name(tree) and (_AstropyTime is None):
        return None, 'astropy.time.Time is not available here.'

    def _run_eval():
        code = compile(tree, '<custom-column>', 'eval')
        return eval(code, env, values)

    try:
        result = _with_eval_timeout(5, _run_eval)
    except _EvalTimeoutError:
        return None, 'Expression timed out after 5 seconds.'
    except Exception as exc:
        return None, 'Expression error: {0}: {1}'.format(
            type(exc).__name__,
            str(exc),
        )

    if isinstance(result, np.ndarray):
        result = result.tolist()

    if isinstance(result, np.generic):
        result = result.item()

    if not isinstance(result, (int, float, str, bool, list, tuple)):
        return None, 'Expression must return a scalar or list value.'

    return result, None


def _normalise_custom_columns(custom_columns, catalog_map):
    """Normalise custom column definitions from API payload."""
    result = []
    seen = set()
    if not isinstance(custom_columns, list):
        return result

    for row in custom_columns:
        if not isinstance(row, dict):
            continue
        name = str(row.get('name', '')).strip()
        expr = str(row.get('expression', '')).strip()
        variables = row.get('variables', dict())
        if not name or not expr:
            continue
        name_key = name.lower()
        if name_key in seen:
            continue
        if not isinstance(variables, dict):
            continue

        vars_clean = dict()
        for key, value in variables.items():
            letter = str(key).strip().lower()
            prop_id = str(value).strip()
            if len(letter) != 1 or (not letter.isalpha()):
                continue
            if prop_id not in catalog_map:
                continue
            vars_clean[letter] = prop_id
        if not vars_clean:
            continue

        result.append(
            dict(
                name=name,
                expression=expr,
                variables=vars_clean,
            )
        )
        seen.add(name_key)
    return result


def _find_duplicate_custom_column_name(rows):
    """Return first duplicate custom column name (case-insensitive)."""
    seen = set()
    if not isinstance(rows, list):
        return ''
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get('name', '')).strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            return name
        seen.add(key)
    return ''


def _seed_catalog_with_custom_var_ids(catalog_map, custom_rows):
    """Ensure variable property IDs exist in *catalog_map* placeholders."""
    if not isinstance(catalog_map, dict):
        return
    if not isinstance(custom_rows, list):
        return
    for row in custom_rows:
        if not isinstance(row, dict):
            continue
        variables = row.get('variables', dict())
        if not isinstance(variables, dict):
            continue
        for prop_id in variables.values():
            pid = str(prop_id or '').strip()
            if not pid:
                continue
            if pid in catalog_map:
                continue
            catalog_map[pid] = dict(id=pid)


def _load_astrometric_entry(app, objname):
    """Load one astrometric YAML entry for *objname*."""
    from apero.core import drs_astrometrics as dra

    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    astrom_dir = base_dir / 'apero-assets' / 'astrometrics'
    try:
        entry = dra.find_by_name(str(astrom_dir), objname)
    except Exception:
        entry = None
    return entry if isinstance(entry, dict) else dict()


def _load_profile_object_row_map(app, profile):
    """Return ``OBJNAME -> object_table row`` for one profile."""
    base_dir = Path(
        app.args.data_dir or str(Path.home() / '.ari')
    )
    rows = _load_object_table(
        base_dir,
        profile['instrument'],
        profile['profile_id'],
    )
    if rows is None:
        return dict()
    row_map = dict()
    for row in rows:
        objname = str(row.get('OBJNAME', '')).strip()
        if not objname:
            continue
        row_map[objname] = row
    return row_map


def _resolve_summary_group(app, user_info, profile_id, group_name):
    """Resolve a visible profile/group pair for summary actions."""
    if not user_info:
        return None, None, None, (
            jsonify(success=False, error='Unauthorized'),
            401,
        )

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return None, None, None, (
            jsonify(success=False, error='Profile not found'),
            404,
        )

    group = og.get_group(profile_id, group_name)
    if not isinstance(group, dict):
        return None, None, None, (
            jsonify(success=False, error='Group not found'),
            404,
        )

    accessible_rids = app._get_user_accessible_run_ids(
        user_info, profile['instrument']
    )
    return profile, group, accessible_rids, None


def _normalise_summary_source(source):
    """Return canonical summary source name."""
    text = str(source or 'group').strip().lower()
    if text in {'fav', 'favourite', 'favourites', 'favorite', 'favorites'}:
        return 'favourites'
    return 'group'


def _favourites_summary_path(local_data_dir, username):
    """Return per-user favourites summary settings path."""
    base = Path(local_data_dir or str(Path.home() / '.ari'))
    return base / 'users' / str(username) / 'favourite_summary.yaml'


def _load_favourites_summary_data(local_data_dir, username):
    """Load per-user favourites summary settings."""
    path = _favourites_summary_path(local_data_dir, username)
    if not path.exists():
        return {'profiles': dict()}
    try:
        import yaml

        with open(path, 'r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
    except Exception:
        return {'profiles': dict()}
    if not isinstance(data, dict):
        return {'profiles': dict()}
    profiles = data.get('profiles', dict())
    if not isinstance(profiles, dict):
        profiles = dict()
    return {'profiles': profiles}


def _save_favourites_summary_data(local_data_dir, username, data):
    """Persist per-user favourites summary settings."""
    import yaml

    path = _favourites_summary_path(local_data_dir, username)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data if isinstance(data, dict) else {'profiles': dict()}
    with open(path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def _get_favourites_summary_entry(local_data_dir, username, profile_id,
                                 section_name):
    """Return one per-section favourites summary settings entry."""
    data = _load_favourites_summary_data(local_data_dir, username)
    profiles = data.get('profiles', dict())
    profile_data = profiles.get(str(profile_id), dict())
    if not isinstance(profile_data, dict):
        return dict()
    sections = profile_data.get('sections', dict())
    if not isinstance(sections, dict):
        return dict()
    entry = sections.get(str(section_name), dict())
    return entry if isinstance(entry, dict) else dict()


def _set_favourites_summary_entry(local_data_dir, username, profile_id,
                                 section_name, entry):
    """Update one per-section favourites summary settings entry."""
    data = _load_favourites_summary_data(local_data_dir, username)
    profiles = data.get('profiles', dict())
    if not isinstance(profiles, dict):
        profiles = dict()
    profile_key = str(profile_id)
    profile_data = profiles.get(profile_key, dict())
    if not isinstance(profile_data, dict):
        profile_data = dict()
    sections = profile_data.get('sections', dict())
    if not isinstance(sections, dict):
        sections = dict()
    sections[str(section_name)] = entry if isinstance(entry, dict) else dict()
    profile_data['sections'] = sections
    profiles[profile_key] = profile_data
    data['profiles'] = profiles
    _save_favourites_summary_data(local_data_dir, username, data)


def _resolve_summary_target(app, user_info, profile_id, group_name,
                           source='group', section_name=''):
    """Resolve summary source objects for group or favourites."""
    if not user_info:
        return None, None, None, None, (
            jsonify(success=False, error='Unauthorized'),
            401,
        )

    source_name = _normalise_summary_source(source)
    section = str(section_name or group_name or '').strip()

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return None, None, None, None, (
            jsonify(success=False, error='Profile not found'),
            404,
        )
    accessible_rids = app._get_user_accessible_run_ids(
        user_info, profile['instrument']
    )

    if source_name == 'favourites':
        username = str((user_info or {}).get('username', '')).strip()
        from apero_ri.core import user_data as ud

        payload = ud.get_profile_fav_sections(username, profile_id)
        sections = payload.get('sections', [])
        if not isinstance(sections, list):
            sections = []
        target = None
        for one in sections:
            if str(one.get('name', '')).strip() == section:
                target = one
                break
        if not isinstance(target, dict):
            return None, None, None, None, (
                jsonify(success=False, error='Favourite section not found'),
                404,
            )
        objects = []
        for item in list(target.get('items', []) or []):
            objname = str(item.get('objname', '')).strip()
            if not objname:
                continue
            objects.append({'objname': objname})
        settings = dict(
            type='favourites',
            username=username,
            section=section,
        )
        return profile, objects, accessible_rids, settings, None

    group = og.get_group(profile_id, group_name)
    if not isinstance(group, dict):
        return None, None, None, None, (
            jsonify(success=False, error='Group not found'),
            404,
        )
    objects = list(group.get('objects', []) or [])
    settings = dict(
        type='group',
        group=str(group_name),
    )
    return profile, objects, accessible_rids, settings, None


def _get_summary_saved_columns(local_data_dir, profile_id, settings):
    """Return persisted summary columns for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        columns = entry.get('summary_columns', [])
        return columns if isinstance(columns, list) else []
    return og.get_summary_columns(profile_id, settings.get('group', ''))


def _set_summary_saved_columns(local_data_dir, profile_id, settings,
                              columns):
    """Persist summary columns for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        entry['summary_columns'] = list(columns or [])
        _set_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
            entry,
        )
        return True
    return og.set_summary_columns(profile_id, settings.get('group', ''),
                                  columns)


def _get_summary_saved_aliases(local_data_dir, profile_id, settings):
    """Return persisted summary aliases for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        aliases = entry.get('summary_aliases', dict())
        return aliases if isinstance(aliases, dict) else dict()
    return og.get_summary_aliases(profile_id, settings.get('group', ''))


def _set_summary_saved_aliases(local_data_dir, profile_id, settings,
                              aliases):
    """Persist summary aliases for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        entry['summary_aliases'] = dict(aliases or dict())
        _set_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
            entry,
        )
        return True
    return og.set_summary_aliases(profile_id, settings.get('group', ''),
                                  aliases)


def _get_summary_saved_custom(local_data_dir, profile_id, settings):
    """Return persisted custom columns for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        rows = entry.get('summary_custom_columns', [])
        return rows if isinstance(rows, list) else []
    return og.get_summary_custom_columns(profile_id, settings.get('group', ''))


def _set_summary_saved_custom(local_data_dir, profile_id, settings,
                             custom_columns):
    """Persist custom columns for current summary source."""
    if str(settings.get('type')) == 'favourites':
        entry = _get_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
        )
        entry['summary_custom_columns'] = list(custom_columns or [])
        _set_favourites_summary_entry(
            local_data_dir,
            settings.get('username', ''),
            profile_id,
            settings.get('section', ''),
            entry,
        )
        return True
    return og.set_summary_custom_columns(
        profile_id,
        settings.get('group', ''),
        custom_columns,
    )


def _build_group_summary_payload(
    app,
    user_info,
    profile_id,
    group_name,
    source='group',
    section_name='',
    columns=None,
):
    """Return summary-table payload or a Flask error response."""
    profile, objects_raw, accessible_rids, settings, error = (
        _resolve_summary_target(
            app,
            user_info,
            profile_id,
            group_name,
            source=source,
            section_name=section_name,
        )
    )
    if error is not None:
        return False, error

    local_data_dir = app._resolve_local_data_dir()
    expr_rules, _, _ = _get_compiled_expression_rules(
        local_data_dir,
    )
    object_rows = _load_profile_object_row_map(app, profile)
    temp_group = {'objects': objects_raw}
    objects = _filter_group_objects(
        app,
        profile_id,
        temp_group,
        accessible_rids,
    )

    properties_by_object = dict()
    catalog_map = dict()
    for obj in objects:
        objname = str(obj.get('objname', '')).strip()
        if not objname:
            continue
        obj_row = object_rows.get(objname, dict(OBJNAME=objname))
        try:
            props = _collect_object_summary_properties(
                app,
                profile,
                obj_row,
                objname,
                accessible_rids,
            )
        except Exception:
            # Keep summary usable even if one object has malformed metadata.
            continue
        properties_by_object[objname] = props
        for pid, item in props.items():
            if pid not in catalog_map:
                catalog_map[pid] = dict(
                    id=pid,
                    label=item.get('label') or pid,
                    property_name=(
                        item.get('property_name')
                        or item.get('label')
                        or pid
                    ),
                    category=(
                        item.get('category')
                        or item.get('section_title')
                        or ''
                    ),
                    subcategory=item.get('subcategory') or 'general',
                    lbl_category=item.get('lbl_category') or '',
                    hierarchy=item.get('hierarchy') or '',
                    token=pid,
                    section_id=item.get('section_id') or '',
                    section_title=item.get('section_title') or '',
                    section_description='',
                    units=item.get('units') or '',
                )

    # Include canonical target-info catalog IDs for empty groups.
    base_catalog, _ = _summary_catalog_items()
    for item in base_catalog:
        pid = 'target_info::{0}'.format(item['id'])
        if pid in catalog_map:
            continue
        merged = dict(item)
        merged['id'] = pid
        merged['token'] = pid
        merged['label'] = item['label']
        merged['property_name'] = item.get('label') or item['id']
        merged['category'] = 'target info'
        merged['subcategory'] = 'target info'
        merged['lbl_category'] = ''
        merged['hierarchy'] = 'target info / target info'
        merged['section_id'] = 'target_info'
        merged['section_title'] = 'target info'
        catalog_map[pid] = merged

    catalog = [
        catalog_map[key]
        for key in sorted(catalog_map.keys())
    ]

    if columns is None:
        selected = _get_summary_saved_columns(
            local_data_dir,
            profile_id,
            settings,
        )
    else:
        selected = columns
    selected = _normalise_summary_columns(selected, catalog_map)
    aliases = _get_summary_saved_aliases(
        local_data_dir,
        profile_id,
        settings,
    )
    custom_columns = _get_summary_saved_custom(
        local_data_dir,
        profile_id,
        settings,
    )
    custom_columns = _normalise_custom_columns(
        custom_columns,
        catalog_map,
    )

    columns_out = ['OBJNAME']
    column_ids = dict(OBJNAME='OBJNAME')
    labels_by_id = dict()
    used_labels = {'OBJNAME'}
    column_meta = dict(
        OBJNAME=dict(
            sortable=True,
            filterable=True,
            removable=False,
            default=True,
            type='string',
        )
    )
    for prop_id in selected:
        item = catalog_map[prop_id]
        base_label = str(aliases.get(prop_id) or item['label']).strip()
        if not base_label:
            base_label = str(prop_id)
        label = base_label
        idx = 2
        while label in used_labels:
            label = '{0} ({1})'.format(base_label, idx)
            idx += 1
        used_labels.add(label)
        labels_by_id[prop_id] = label
        columns_out.append(label)
        column_ids[label] = prop_id
        column_meta[label] = dict(
            sortable=True,
            filterable=True,
            removable=True,
            default=True,
            type='string',
        )

    custom_label_by_name = dict()
    for row in custom_columns:
        base_label = str(row.get('name', '')).strip()
        if not base_label:
            continue
        label = base_label
        idx = 2
        while label in used_labels:
            label = '{0} ({1})'.format(base_label, idx)
            idx += 1
        used_labels.add(label)
        custom_label_by_name[base_label] = label
        columns_out.append(label)
        column_ids[label] = 'custom::{0}'.format(base_label)
        column_meta[label] = dict(
            sortable=True,
            filterable=True,
            removable=True,
            default=True,
            type='string',
            custom=True,
        )

    rows = []
    for obj in objects:
        objname = str(obj.get('objname', '')).strip()
        if not objname:
            continue
        flat = properties_by_object.get(objname, dict())

        out_row = dict(OBJNAME=objname)
        for prop_id in selected:
            prop = flat.get(prop_id, dict())
            col_name = labels_by_id[prop_id]
            out_row[col_name] = _summary_value(
                prop.get('value')
            )

        for row in custom_columns:
            cname = str(row.get('name', '')).strip()
            col_name = custom_label_by_name.get(cname)
            if not col_name:
                continue
            var_map = row.get('variables', dict())
            var_values = dict()
            has_null = False
            for letter, prop_id in var_map.items():
                raw_prop = flat.get(prop_id, dict())
                value = raw_prop.get('value')
                if _is_null_value(value):
                    has_null = True
                    break
                var_values[str(letter)] = value
            if has_null:
                out_row[col_name] = ''
                continue
            value, error = _eval_custom_expression(
                row.get('expression', ''),
                var_values,
                expr_rules,
            )
            if error is not None:
                out_row[col_name] = ''
            else:
                out_row[col_name] = _summary_value(value)
        rows.append(out_row)

    payload = dict(
        success=True,
        group_name=group_name,
        rows=rows,
        columns=columns_out,
        column_ids=column_ids,
        column_meta=column_meta,
        selected_columns=selected,
        selected_aliases=aliases,
        custom_columns=custom_columns,
        property_catalog=catalog,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_rows=len(rows),
        message=(
            'No visible objects in this group.'
            if not rows else ''
        ),
    )
    return True, payload


def _latex_escape(value):
    """Escape a value for simple LaTeX table export."""
    text = str(value)
    repl = [
        ('\\', '\\textbackslash{}'),
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]
    for old, new in repl:
        text = text.replace(old, new)
    return text


def _summary_filename(profile_id, group_name, ext):
    """Return a filesystem-safe download filename."""
    safe_group = quote(group_name, safe='') or 'group'
    return 'object_group_summary_{0}_{1}.{2}'.format(
        profile_id,
        safe_group,
        ext,
    )


def _summary_html_document(
    profile_id,
    group_name,
    columns,
    rows,
):
    """Build a standalone HTML summary table document."""
    title = 'Summary table: {0} ({1})'.format(group_name, profile_id)
    escaped_title = html.escape(title)
    header_cells = ''.join(
        '<th>{0}</th>'.format(html.escape(str(col)))
        for col in columns
    )

    body_rows = []
    for row in rows:
        cells = ''.join(
            '<td>{0}</td>'.format(
                html.escape(str(row.get(col, '')))
            )
            for col in columns
        )
        body_rows.append('<tr>{0}</tr>'.format(cells))

    if not body_rows:
        body_rows.append(
            '<tr><td colspan="{0}">No rows in this summary.</td></tr>'.format(
                max(1, len(columns))
            )
        )

    style = (
        'body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;'
        'background:#f6f8fb;color:#1e293b;margin:0;padding:1.2rem;}'
        '.wrap{max-width:1400px;margin:0 auto;background:#fff;border:1px '
        'solid #dbe4f0;border-radius:12px;box-shadow:0 8px 24px '
        'rgba(15,23,42,.08);overflow:hidden;}'
        '.hdr{padding:1rem 1.2rem;background:linear-gradient(135deg,#1f4f7a,'
        '#2f6a9c);color:#fff;font-weight:700;}'
        '.meta{padding:.55rem 1.2rem;color:#475569;font-size:.9rem;border-top:'
        '1px solid #dbe4f0;background:#f8fbff;}'
        '.tbl-wrap{overflow:auto;}'
        'table{width:100%;border-collapse:collapse;font-size:.9rem;}'
        'thead th{position:sticky;top:0;background:#17436c;color:#fff;'
        'font-weight:700;text-align:left;padding:.5rem .6rem;border:1px solid '
        '#2a5c8c;white-space:nowrap;}'
        'tbody td{padding:.45rem .6rem;border:1px solid #dbe4f0;vertical-align:'
        'top;}'
        'tbody tr:nth-child(odd) td{background:#f8fbff;}'
    )

    doc = [
        '<!doctype html>',
        '<html lang="en">',
        '<head><meta charset="utf-8"><title>{0}</title>'.format(
            escaped_title
        ),
        '<style>{0}</style></head>'.format(style),
        '<body><div class="wrap">',
        '<div class="hdr">{0}</div>'.format(escaped_title),
        '<div class="meta">Rows: {0} | Columns: {1}</div>'.format(
            len(rows),
            len(columns),
        ),
        '<div class="tbl-wrap"><table><thead><tr>{0}</tr></thead>'.format(
            header_cells
        ),
        '<tbody>{0}</tbody></table></div>'.format(''.join(body_rows)),
        '</div></body></html>',
    ]
    return ''.join(doc)


def _summary_table_figure(
    columns,
    rows,
    title,
    subtitle,
):
    """Create a styled matplotlib figure for summary table export."""
    import matplotlib.pyplot as plt

    ncols = max(1, len(columns))
    nrows = max(1, len(rows))
    fig_w = min(22.0, max(9.0, 1.3 + (0.95 * ncols)))
    fig_h = min(28.0, max(4.2, 1.9 + (0.34 * nrows)))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis('off')
    fig.patch.set_facecolor('#f6f8fb')
    fig.suptitle(title, fontsize=12, fontweight='bold', color='#15334f')
    if subtitle:
        ax.text(
            0.0,
            1.0,
            subtitle,
            transform=ax.transAxes,
            ha='left',
            va='bottom',
            fontsize=8,
            color='#3e4b5b',
        )

    cell_text = [
        [str(row.get(col, '')) for col in columns]
        for row in rows
    ]
    if not cell_text:
        cell_text = [['' for _ in columns]]

    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        cellLoc='left',
        colLoc='left',
        loc='center',
        bbox=[0.0, 0.0, 1.0, 0.96],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1.0, 1.23)

    for (row_idx, _), cell in table.get_celld().items():
        cell.set_edgecolor('#d0d8e3')
        cell.set_linewidth(0.6)
        if row_idx == 0:
            cell.set_facecolor('#1f4f7a')
            cell.set_text_props(color='white', weight='bold')
            continue
        if row_idx % 2 == 1:
            cell.set_facecolor('#f8fbff')
        else:
            cell.set_facecolor('white')

    return fig


# ================================================================
# API endpoints — group CRUD
# ================================================================
def api_object_groups_list(app):
    """GET  list all groups for a profile."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    if not profile_id:
        return jsonify(
            success=False, error='profile_id required'
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)

    groups = og.list_groups(profile_id)
    items = []
    for g in groups:
        entry = dict(g)
        entry['object_count'] = len(g.get('objects', []))
        entry['can_edit'] = can_mod
        entry['can_delete'] = can_mod
        items.append(entry)

    return jsonify(
        success=True, groups=items, can_moderate=can_mod
    )


def api_object_groups_for_object(app):
    """GET  groups containing a specific object."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    objname = request.args.get('objname', '').strip()
    if not profile_id or not objname:
        return jsonify(
            success=False,
            error='profile_id and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    group_names = og.get_groups_for_object(
        profile_id, objname
    )
    all_groups = og.list_groups(profile_id)
    all_group_names = [
        g.get('name', '') for g in all_groups
    ]

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)

    return jsonify(
        success=True,
        member_groups=group_names,
        all_groups=all_group_names,
        can_moderate=can_mod,
    )


def api_object_groups_create(app):
    """POST  create a new group."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    name = str(body.get('name', '')).strip()
    if not profile_id or not name:
        return jsonify(
            success=False,
            error='profile_id and name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    username = user_info.get('username', '')
    group = og.create_group(profile_id, name, username)
    if group is None:
        return jsonify(
            success=False,
            error='Group already exists',
        ), 409

    instrument = profile['instrument']
    can_mod = _can_moderate(user_info, app, instrument)
    group['object_count'] = 0
    group['can_edit'] = can_mod
    group['can_delete'] = can_mod
    return jsonify(success=True, group=group)


def api_object_groups_delete(app):
    """POST  delete a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    name = str(body.get('name', '')).strip()
    if not profile_id or not name:
        return jsonify(
            success=False,
            error='profile_id and name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.delete_group(profile_id, name):
        return jsonify(
            success=False, error='Group not found'
        ), 404

    return jsonify(success=True)


def api_object_groups_rename(app):
    """POST  rename a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    old_name = str(body.get('old_name', '')).strip()
    new_name = str(body.get('new_name', '')).strip()
    if not profile_id or not old_name or not new_name:
        return jsonify(
            success=False,
            error='profile_id, old_name and '
                  'new_name required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.rename_group(profile_id, old_name, new_name):
        return jsonify(
            success=False,
            error='Rename failed (not found or name taken)',
        ), 400

    return jsonify(success=True)


# ================================================================
# API endpoints — object membership
# ================================================================
def api_object_groups_add_object(app):
    """POST  add an object to a group (resolves aliases)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    group_name = str(body.get('group', '')).strip()
    query = str(body.get('objname', '')).strip()
    if not profile_id or not group_name or not query:
        return jsonify(
            success=False,
            error='profile_id, group and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    objname, nickname, error, candidates = _resolve_query(
        app, profile, query
    )
    if error:
        code = 404 if not candidates else 400
        return jsonify(
            success=False, error=error,
            candidates=candidates,
        ), code

    username = user_info.get('username', '')
    err = og.add_object_to_group(
        profile_id, group_name, objname, username
    )
    if err:
        return jsonify(success=False, error=err), 400

    return jsonify(
        success=True,
        resolved_objname=objname,
        nickname=nickname,
    )


def api_object_groups_add_objects_bulk(app):
    """POST  (multipart) bulk-add objects from text/csv.

    Each line is resolved through alias lookup. Lines that
    cannot be resolved are reported as ``not_found``.
    """
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = str(
        request.form.get('profile_id', '')
    ).strip()
    group_name = str(
        request.form.get('group', '')
    ).strip()
    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify(
            success=False, error='No file uploaded'
        ), 400

    raw = uploaded.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')

    queries = []
    for line in io.StringIO(text):
        name = line.strip().split(',')[0].strip()
        if name:
            queries.append(name)

    username = user_info.get('username', '')
    added = 0
    skipped = 0
    not_found = []

    for query in queries:
        objname, nickname, error, _cand = _resolve_query(
            app, profile, query
        )
        if error or objname is None:
            not_found.append(query)
            continue
        err = og.add_object_to_group(
            profile_id, group_name, objname, username
        )
        if err:
            skipped += 1
        else:
            added += 1

    return jsonify(
        success=True,
        added=added,
        skipped=skipped,
        not_found=not_found,
    )


def api_object_groups_add_objects_json(app):
    """POST  bulk-add objects from a JSON list of names.

    Expected JSON body::

        {
            "profile_id": "<str>",
            "group": "<str>",
            "objnames": ["OBJ1", "OBJ2", ...]
        }

    Objects that cannot be resolved are reported in
    ``not_found``.  Objects already in the group are
    silently counted as ``skipped``.
    """
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(
            success=False, error='Unauthorized'
        ), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(
        body.get('profile_id', '')
    ).strip()
    group_name = str(
        body.get('group', '')
    ).strip()
    objnames = body.get('objnames', [])

    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400
    if not isinstance(objnames, list) or not objnames:
        return jsonify(
            success=False,
            error='objnames must be a non-empty list',
        ), 400
    # Cap at 5000 to prevent abuse
    if len(objnames) > 5000:
        return jsonify(
            success=False,
            error='Too many objects (max 5000)',
        ), 400

    profile = _resolve_profile(
        app, user_info, profile_id
    )
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    username = user_info.get('username', '')
    added = 0
    skipped = 0
    not_found = []

    for raw_name in objnames:
        name = str(raw_name).strip()
        if not name:
            continue
        # Resolve through alias lookup
        objname, _nick, error, _cand = (
            _resolve_query(app, profile, name)
        )
        if error or objname is None:
            not_found.append(name)
            continue
        err = og.add_object_to_group(
            profile_id, group_name,
            objname, username,
        )
        if err:
            skipped += 1
        else:
            added += 1

    return jsonify(
        success=True,
        added=added,
        skipped=skipped,
        not_found=not_found,
    )


def api_object_groups_remove_object(app):
    """POST  remove an object from a group (monitor only)."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    group_name = str(body.get('group', '')).strip()
    objname = str(body.get('objname', '')).strip()
    if not profile_id or not group_name or not objname:
        return jsonify(
            success=False,
            error='profile_id, group and objname required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    if not _can_moderate(user_info, app, instrument):
        return jsonify(
            success=False,
            error='Insufficient permissions',
        ), 403

    if not og.remove_object_from_group(
        profile_id, group_name, objname
    ):
        return jsonify(
            success=False,
            error='Object not in group',
        ), 404

    return jsonify(success=True)


def api_object_groups_objects(app):
    """GET  list objects in a group, filtered by user access."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    group_name = request.args.get('group', '').strip()
    if not profile_id or not group_name:
        return jsonify(
            success=False,
            error='profile_id and group required',
        ), 400

    profile = _resolve_profile(app, user_info, profile_id)
    if not profile:
        return jsonify(
            success=False, error='Profile not found'
        ), 404

    instrument = profile['instrument']
    accessible_rids = app._get_user_accessible_run_ids(
        user_info, instrument
    )

    groups = og.list_groups(profile_id)
    group = None
    for g in groups:
        if g.get('name') == group_name:
            group = g
            break
    if group is None:
        return jsonify(
            success=False, error='Group not found'
        ), 404

    # Filter objects by user's science-group run_ids
    obj_list = _filter_group_objects(
        app, profile_id, group, accessible_rids
    )

    can_mod = _can_moderate(user_info, app, instrument)
    return jsonify(
        success=True, objects=obj_list,
        can_moderate=can_mod,
    )


def api_object_groups_summary_config(app):
    """GET/POST summary-table column config for one group."""
    user_info = get_effective_user(session)
    profile_id = ''
    group_name = ''
    source = 'group'
    section_name = ''
    columns = []
    custom_columns = []

    if request.method == 'POST':
        body = request.get_json(silent=True) or {}
        profile_id = str(body.get('profile_id', '')).strip()
        group_name = str(body.get('group', '')).strip()
        source = _normalise_summary_source(body.get('source', 'group'))
        section_name = str(body.get('section', '')).strip()
        columns = body.get('columns', [])
        custom_columns = body.get('custom_columns', [])
    else:
        profile_id = request.args.get('profile_id', '').strip()
        group_name = request.args.get('group', '').strip()
        source = _normalise_summary_source(
            request.args.get('source', 'group')
        )
        section_name = request.args.get('section', '').strip()

    target_name = section_name if source == 'favourites' else group_name
    if not profile_id or not target_name:
        return jsonify(
            success=False,
            error='profile_id and target required',
        ), 400

    profile, objects_raw, accessible_rids, settings, error = (
        _resolve_summary_target(
            app,
            user_info,
            profile_id,
            target_name,
            source=source,
            section_name=section_name,
        )
    )
    if error is not None:
        return error

    try:
        ok, base_payload = _build_group_summary_payload(
            app,
            user_info,
            profile_id,
            target_name,
            source=source,
            section_name=section_name,
        )
    except Exception as exc:
        return jsonify(
            success=False,
            error='Failed loading summary properties: {0}'.format(
                str(exc),
            ),
        ), 500
    if not ok:
        return base_payload

    local_data_dir = app._resolve_local_data_dir()
    catalog = base_payload['property_catalog']
    catalog_map = {
        str(item.get('id')): item
        for item in catalog
        if str(item.get('id', '')).strip()
    }
    aliases = dict()
    if request.method == 'POST':
        if not isinstance(columns, list):
            return jsonify(
                success=False,
                error='columns must be a list',
            ), 400
        aliases = body.get('aliases', dict())
        if aliases is None:
            aliases = dict()
        if not isinstance(aliases, dict):
            return jsonify(
                success=False,
                error='aliases must be a mapping',
            ), 400
        clean = _normalise_summary_columns(columns, catalog_map)
        clean_custom = _normalise_custom_columns(
            custom_columns,
            catalog_map,
        )
        if not _set_summary_saved_columns(
            local_data_dir,
            profile_id,
            settings,
            clean,
        ):
            return jsonify(
                success=False,
                error='Summary target not found',
            ), 404
        clean_aliases = dict()
        for key, value in aliases.items():
            pid = str(key).strip()
            label = str(value).strip()
            if pid and label:
                clean_aliases[pid] = label
        _set_summary_saved_aliases(
            local_data_dir,
            profile_id,
            settings,
            clean_aliases,
        )
        _set_summary_saved_custom(
            local_data_dir,
            profile_id,
            settings,
            clean_custom,
        )

    selected = _normalise_summary_columns(
        _get_summary_saved_columns(
            local_data_dir,
            profile_id,
            settings,
        ),
        catalog_map,
    )
    selected_aliases = _get_summary_saved_aliases(
        local_data_dir,
        profile_id,
        settings,
    )
    selected_custom = _get_summary_saved_custom(
        local_data_dir,
        profile_id,
        settings,
    )
    selected_custom = _normalise_custom_columns(
        selected_custom,
        catalog_map,
    )
    admin_custom_rows_raw = _admin_custom_profile_rows(
        local_data_dir,
        profile_id,
    )
    _seed_catalog_with_custom_var_ids(
        catalog_map,
        admin_custom_rows_raw,
    )
    admin_custom_rows = _normalise_custom_columns(
        admin_custom_rows_raw,
        catalog_map,
    )
    temp_group = {'objects': objects_raw}
    visible_count = len(
        _filter_group_objects(
            app,
            profile_id,
            temp_group,
            accessible_rids,
        )
    )

    if source == 'favourites':
        summary_page_url = (
            '/data_portal/{0}/fav-objects/{1}/summary-table'.format(
                profile_id,
                quote(target_name, safe=''),
            )
        )
    else:
        summary_page_url = (
            '/data_portal/{0}/object-groups/{1}/summary-table'.format(
                profile_id,
                quote(target_name, safe=''),
            )
        )

    return jsonify(
        success=True,
        profile_id=profile['profile_id'],
        group_name=target_name,
        source=source,
        section_name=section_name,
        selected_columns=selected,
        selected_aliases=selected_aliases,
        custom_columns=selected_custom,
        admin_custom_columns=admin_custom_rows,
        property_catalog=catalog,
        allowed_expression_rows=_load_allowed_expression_rows(
            app._resolve_local_data_dir()
        ),
        visible_object_count=visible_count,
        summary_page_url=summary_page_url,
    )


def api_object_groups_summary_custom_test(app):
    """POST test one custom summary column expression."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get('profile_id', '')).strip()
    group_name = str(body.get('group', '')).strip()
    source = _normalise_summary_source(body.get('source', 'group'))
    section_name = str(body.get('section', '')).strip()
    expression = str(body.get('expression', '')).strip()
    variables = body.get('variables', dict())

    target_name = section_name if source == 'favourites' else group_name

    if not profile_id or not target_name:
        return jsonify(
            success=False,
            error='profile_id and target required',
        ), 400
    if not expression:
        return jsonify(
            success=False,
            error='expression required',
        ), 400
    if not isinstance(variables, dict):
        return jsonify(
            success=False,
            error='variables must be a mapping',
        ), 400

    profile, objects_raw, accessible_rids, _, error = _resolve_summary_target(
        app,
        user_info,
        profile_id,
        target_name,
        source=source,
        section_name=section_name,
    )
    if error is not None:
        return error

    object_rows = _load_profile_object_row_map(app, profile)
    temp_group = {'objects': objects_raw}
    objects = _filter_group_objects(
        app,
        profile_id,
        temp_group,
        accessible_rids,
    )

    catalog_map = dict()
    for obj in objects:
        objname = str(obj.get('objname', '')).strip()
        if not objname:
            continue
        obj_row = object_rows.get(objname, dict(OBJNAME=objname))
        props = _collect_object_summary_properties(
            app,
            profile,
            obj_row,
            objname,
            accessible_rids,
        )
        for pid, item in props.items():
            if pid not in catalog_map:
                catalog_map[pid] = item

    base_catalog, _ = _summary_catalog_items()
    for item in base_catalog:
        pid = 'target_info::{0}'.format(item['id'])
        if pid not in catalog_map:
            catalog_map[pid] = dict(id=pid, label=item['label'])
    normalised = _normalise_custom_columns(
        [
            dict(
                name='test',
                expression=expression,
                variables=variables,
            )
        ],
        catalog_map,
    )
    if not normalised:
        return jsonify(
            success=False,
            error='Invalid variable mapping.',
        ), 400
    test_def = normalised[0]

    var_map = test_def.get('variables', dict())
    first_values = None

    for obj in objects:
        objname = str(obj.get('objname', '')).strip()
        if not objname:
            continue
        obj_row = object_rows.get(objname, dict(OBJNAME=objname))
        props = _collect_object_summary_properties(
            app,
            profile,
            obj_row,
            objname,
            accessible_rids,
        )
        values = dict()
        has_null = False
        for letter, prop_id in var_map.items():
            entry = props.get(str(prop_id), dict())
            value = entry.get('value')
            if _is_null_value(value):
                has_null = True
                break
            values[str(letter)] = value
        if has_null:
            continue
        first_values = values
        break

    if first_values is None:
        return jsonify(
            success=False,
            error='No row has all variables populated.',
        ), 400

    expr_rules, _, _ = _get_compiled_expression_rules(
        app._resolve_local_data_dir()
    )

    value, error = _eval_custom_expression(
        test_def.get('expression', ''),
        first_values,
        expr_rules,
    )
    if error is not None:
        return jsonify(
            success=False,
            error=error,
        ), 400

    return jsonify(
        success=True,
        sample_variables=first_values,
        sample_result=value,
    )


def api_object_groups_allowed_expressions(app):
    """GET/POST allowed-python-expression rows for admin tools."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info.get('groups', []),
        app.ari_groups,
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    local_data_dir = app._resolve_local_data_dir()

    if request.method == 'POST':
        body = request.get_json(silent=True) or dict()
        rows = _normalise_allowed_expression_rows(
            body.get('rows', [])
        )
        saved_rows = _save_allowed_expression_rows(
            local_data_dir,
            rows,
        )
        compiled, _, warnings = _get_compiled_expression_rules(
            local_data_dir
        )
        return jsonify(
            success=True,
            rows=saved_rows,
            warnings=warnings,
            callables=sorted(compiled.get('callables', set())),
        )

    compiled, rows, warnings = _get_compiled_expression_rules(
        local_data_dir
    )
    return jsonify(
        success=True,
        rows=rows,
        warnings=warnings,
        callables=sorted(compiled.get('callables', set())),
    )


def _resolve_admin_custom_test_value(
    prop_id,
    props,
    admin_custom_map,
    expr_rules,
    stack=None,
):
    """Resolve one raw or admin-custom property value for tests."""
    prop_key = str(prop_id or '').strip()
    if not prop_key:
        return None

    entry = props.get(prop_key)
    if entry is not None and 'value' in entry:
        return entry.get('value')

    if not prop_key.startswith('admin_custom::'):
        return None

    if stack is None:
        stack = set()
    if prop_key in stack:
        return None

    row = admin_custom_map.get(prop_key)
    if not isinstance(row, dict):
        return None

    stack.add(prop_key)
    var_values = dict()
    for letter, child_prop_id in row.get('variables', dict()).items():
        value = _resolve_admin_custom_test_value(
            child_prop_id,
            props,
            admin_custom_map,
            expr_rules,
            stack,
        )
        if _is_null_value(value):
            stack.discard(prop_key)
            props[prop_key] = dict(id=prop_key, label=row.get('name'), value='')
            return None
        var_values[str(letter)] = value

    value, error = _eval_custom_expression(
        row.get('expression', ''),
        var_values,
        expr_rules,
    )
    stack.discard(prop_key)
    props[prop_key] = dict(
        id=prop_key,
        label=row.get('name'),
        value='' if error is not None else value,
    )
    return props[prop_key].get('value')


def _find_admin_custom_test_sample(
    app,
    user_info,
    var_map,
    profile_id='',
    preferred_objname='',
):
    """Find the first sampled variable map with non-null values."""
    local_data_dir = app._resolve_local_data_dir()
    expr_rules, _, _ = _get_compiled_expression_rules(
        local_data_dir,
    )
    catalog = _build_admin_custom_catalog(
        app,
        user_info,
        profile_id,
    )
    catalog_map = {
        str(item.get('id')): item
        for item in catalog
        if str(item.get('id', '')).strip()
    }
    admin_custom_rows = _normalise_custom_columns(
        _admin_custom_profile_rows(local_data_dir, profile_id),
        catalog_map,
    )
    admin_custom_map = dict()
    for row in admin_custom_rows:
        name = str(row.get('name', '')).strip()
        if not name:
            continue
        admin_custom_map['admin_custom::{0}'.format(name)] = row

    profiles = get_accessible_profiles(
        user_info,
        app.ari_groups,
    )
    target_profile = str(profile_id or '').strip()
    if target_profile:
        profiles = [
            profile
            for profile in list(profiles or [])
            if str(profile.get('profile_id', '')).strip() == target_profile
        ]
    preferred_name = str(preferred_objname or '').strip()
    for profile in list(profiles or []):
        instrument = str(profile.get('instrument') or '').strip()
        if not instrument:
            continue
        accessible_rids = app._get_user_accessible_run_ids(
            user_info,
            instrument,
        )
        obj_rows = _load_profile_object_row_map(app, profile)
        row_items = list(obj_rows.items())[:120]
        if preferred_name and preferred_name in obj_rows:
            preferred_item = (preferred_name, obj_rows[preferred_name])
            row_items = [preferred_item] + [
                item
                for item in row_items
                if str(item[0]) != preferred_name
            ]
        for objname, obj_row in row_items:
            props = _collect_object_summary_properties(
                app,
                profile,
                obj_row,
                objname,
                accessible_rids,
            )
            values = dict()
            has_null = False
            for letter, prop_id in var_map.items():
                value = _resolve_admin_custom_test_value(
                    prop_id,
                    props,
                    admin_custom_map,
                    expr_rules,
                )
                if _is_null_value(value):
                    has_null = True
                    break
                values[str(letter)] = value
            if not has_null:
                return dict(objname=objname, values=values)
    return None


def api_object_groups_admin_custom_columns(app):
    """GET/POST admin-managed custom summary column definitions."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info.get('groups', []),
        app.ari_groups,
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    profiles = get_accessible_profiles(
        user_info,
        app.ari_groups,
    )
    profile_rows = []
    for profile in list(profiles or []):
        pid = str(profile.get('profile_id', '')).strip()
        if not pid:
            continue
        instrument = str(profile.get('instrument', '')).strip()
        label = pid
        if instrument:
            label = '{0} ({1})'.format(pid, instrument)
        profile_rows.append(
            dict(
                profile_id=pid,
                instrument=instrument,
                label=label,
            )
        )

    allowed_profiles = {
        str(row.get('profile_id', '')).strip()
        for row in profile_rows
        if str(row.get('profile_id', '')).strip()
    }

    local_data_dir = app._resolve_local_data_dir()
    profiles_only = str(
        request.args.get('profiles_only', '')
    ).strip().lower() in {'1', 'true', 'yes'}
    requested_profile = ''
    if request.method == 'POST':
        body = request.get_json(silent=True) or dict()
        requested_profile = str(body.get('profile_id', '')).strip()
    else:
        body = dict()
        requested_profile = str(
            request.args.get('profile_id', '')
        ).strip()

    active_profile = requested_profile
    if active_profile not in allowed_profiles:
        active_profile = ''
    if not active_profile and profile_rows:
        active_profile = profile_rows[0]['profile_id']

    default_test_object = _admin_custom_profile_test_object(
        local_data_dir,
        active_profile,
    )

    if request.method == 'GET' and profiles_only:
        return jsonify(
            success=True,
            profile_id=active_profile,
            profiles=profile_rows,
            default_test_object=default_test_object,
        )

    catalog = _build_admin_custom_catalog(
        app,
        user_info,
        active_profile,
    )
    catalog_map = {
        str(item.get('id')): item
        for item in catalog
        if str(item.get('id', '')).strip()
    }
    saved_rows = _admin_custom_profile_rows(
        local_data_dir,
        active_profile,
    )
    _seed_catalog_with_custom_var_ids(catalog_map, saved_rows)

    if request.method == 'POST':
        default_test_object = str(
            body.get('default_test_object', default_test_object),
        ).strip()
        duplicate_name = _find_duplicate_custom_column_name(
            body.get('rows', []),
        )
        if duplicate_name:
            return jsonify(
                success=False,
                error=(
                    'Duplicate custom column name: {0}. '
                    'Column names must be unique.'
                ).format(duplicate_name),
            ), 400
        rows = _normalise_custom_columns(
            body.get('rows', []),
            catalog_map,
        )
        _save_admin_custom_columns(
            local_data_dir,
            active_profile,
            rows,
            default_test_object=default_test_object,
        )
        return jsonify(
            success=True,
            rows=rows,
            property_catalog=catalog,
            profile_id=active_profile,
            profiles=profile_rows,
            default_test_object=default_test_object,
        )

    rows = _normalise_custom_columns(saved_rows, catalog_map)
    return jsonify(
        success=True,
        rows=rows,
        property_catalog=catalog,
        profile_id=active_profile,
        profiles=profile_rows,
        default_test_object=default_test_object,
    )


def api_object_groups_admin_custom_test(app):
    """POST test one admin custom-column expression."""
    user_info = app._get_api_user()
    if not user_info:
        return jsonify(success=False, error='Login required'), 401

    perms = resolve_user_permissions(
        user_info.get('groups', []),
        app.ari_groups,
    )
    if 'manage.apero_profile' not in set(perms or set()):
        return jsonify(success=False, error='Admin access required'), 403

    body = request.get_json(silent=True) or dict()
    profile_id = str(body.get('profile_id', '')).strip()
    preferred_objname = str(body.get('default_test_object', '')).strip()
    expression = str(body.get('expression', '')).strip()
    variables = body.get('variables', dict())
    rows = body.get('rows', [])
    test_all = bool(body.get('test_all'))
    if not test_all and not expression:
        return jsonify(success=False, error='expression required'), 400
    if not test_all and not isinstance(variables, dict):
        return jsonify(
            success=False,
            error='variables must be a mapping',
        ), 400

    catalog = _build_admin_custom_catalog(
        app,
        user_info,
        profile_id,
    )
    catalog_map = {
        str(item.get('id')): item
        for item in catalog
        if str(item.get('id', '')).strip()
    }
    _seed_catalog_with_custom_var_ids(catalog_map, rows)
    expr_rules, _, _ = _get_compiled_expression_rules(
        app._resolve_local_data_dir()
    )
    if test_all:
        normalised_rows = _normalise_custom_columns(rows, catalog_map)
        if not normalised_rows:
            return jsonify(success=False, error='No valid rows to test.'), 400

        results = []
        all_passed = True
        for row in normalised_rows:
            sample = _find_admin_custom_test_sample(
                app,
                user_info,
                row.get('variables', dict()),
                profile_id,
                preferred_objname,
            )
            if sample is None:
                all_passed = False
                results.append(
                    dict(
                        name=row.get('name', ''),
                        success=False,
                        error='No row has all variables populated.',
                    )
                )
                continue

            value, error = _eval_custom_expression(
                row.get('expression', ''),
                sample.get('values', dict()),
                expr_rules,
            )
            if error is not None:
                all_passed = False
                results.append(
                    dict(
                        name=row.get('name', ''),
                        success=False,
                        error=error,
                        sample_object=sample.get('objname', ''),
                    )
                )
                continue

            results.append(
                dict(
                    name=row.get('name', ''),
                    success=True,
                    sample_result=value,
                    sample_variables=sample.get('values', dict()),
                    sample_object=sample.get('objname', ''),
                )
            )

        return jsonify(success=all_passed, results=results)

    normalised = _normalise_custom_columns(
        [dict(name='test', expression=expression, variables=variables)],
        catalog_map,
    )
    if not normalised:
        return jsonify(success=False, error='Invalid variable mapping.'), 400

    test_def = normalised[0]
    sample = _find_admin_custom_test_sample(
        app,
        user_info,
        test_def.get('variables', dict()),
        profile_id,
        preferred_objname,
    )
    if sample is None:
        return jsonify(
            success=False,
            error='No row has all variables populated.',
        ), 400

    value, error = _eval_custom_expression(
        test_def.get('expression', ''),
        sample.get('values', dict()),
        expr_rules,
    )
    if error is not None:
        return jsonify(success=False, error=error), 400

    return jsonify(
        success=True,
        sample_variables=sample.get('values', dict()),
        sample_result=value,
        sample_object=sample.get('objname', ''),
    )


def api_object_groups_summary_table(app):
    """GET summary-table rows for one object group."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    group_name = request.args.get('group', '').strip()
    source = _normalise_summary_source(
        request.args.get('source', 'group')
    )
    section_name = request.args.get('section', '').strip()
    target_name = section_name if source == 'favourites' else group_name
    if not profile_id or not target_name:
        return jsonify(
            success=False,
            error='profile_id and target required',
        ), 400

    ok, payload = _build_group_summary_payload(
        app,
        user_info,
        profile_id,
        target_name,
        source=source,
        section_name=section_name,
    )
    if not ok:
        return payload
    return jsonify(**payload)


def api_object_groups_summary_export(app):
    """Download one group summary as csv, latex, fits, pdf, png, or html."""
    user_info = get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401

    profile_id = request.args.get('profile_id', '').strip()
    group_name = request.args.get('group', '').strip()
    fmt = request.args.get('format', '').strip().lower()
    source = _normalise_summary_source(
        request.args.get('source', 'group')
    )
    section_name = request.args.get('section', '').strip()
    target_name = section_name if source == 'favourites' else group_name
    if not profile_id or not target_name or not fmt:
        return jsonify(
            success=False,
            error='profile_id, target and format required',
        ), 400

    ok, payload = _build_group_summary_payload(
        app,
        user_info,
        profile_id,
        target_name,
        source=source,
        section_name=section_name,
    )
    if not ok:
        return payload

    rows = payload.get('rows', [])
    columns = payload.get('columns', [])

    if fmt == 'csv':
        import csv

        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, '') for col in columns})
        data = io.BytesIO(stream.getvalue().encode('utf-8'))
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='text/csv',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'csv',
            ),
        )

    if fmt == 'latex':
        lines = []
        lines.append('\\begin{tabular}{' + ('l' * len(columns)) + '}')
        lines.append('\\hline')
        header_line = ' & '.join(
            _latex_escape(col) for col in columns
        )
        lines.append(header_line + ' \\\\')
        lines.append('\\hline')
        for row in rows:
            vals = [_latex_escape(row.get(col, '')) for col in columns]
            lines.append(' & '.join(vals) + ' \\\\')
        lines.append('\\hline')
        lines.append('\\end{tabular}')
        data = io.BytesIO('\n'.join(lines).encode('utf-8'))
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='application/x-tex',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'tex',
            ),
        )

    if fmt == 'fits':
        from astropy.table import Table

        table = Table(
            rows=[
                [row.get(col, '') for col in columns]
                for row in rows
            ],
            names=columns,
        )
        data = io.BytesIO()
        table.write(data, format='fits')
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='application/fits',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'fits',
            ),
        )

    if fmt == 'html':
        body = _summary_html_document(
            profile_id,
            target_name,
            columns,
            rows,
        )
        data = io.BytesIO(body.encode('utf-8'))
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='text/html',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'html',
            ),
        )

    if fmt == 'pdf':
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages

        data = io.BytesIO()
        rows_per_page = 30
        with PdfPages(data) as pdf:
            total_pages = max(1, int(math.ceil(len(rows) / rows_per_page)))
            for page_num in range(total_pages):
                start = page_num * rows_per_page
                end = start + rows_per_page
                chunk = rows[start:end]
                title = 'Summary table: {0} ({1})'.format(
                    target_name,
                    profile_id,
                )
                subtitle = 'Page {0}/{1}'.format(
                    page_num + 1,
                    total_pages,
                )
                fig = _summary_table_figure(columns, chunk, title, subtitle)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='application/pdf',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'pdf',
            ),
        )

    if fmt == 'png':
        import matplotlib.pyplot as plt

        max_rows = 110
        chunk = rows[:max_rows]
        title = 'Summary table: {0} ({1})'.format(
            target_name,
            profile_id,
        )
        subtitle = 'Rows: {0}'.format(len(rows))
        if len(rows) > max_rows:
            subtitle += ' (showing first {0})'.format(max_rows)
        fig = _summary_table_figure(columns, chunk, title, subtitle)
        data = io.BytesIO()
        fig.savefig(data, format='png', dpi=180, bbox_inches='tight')
        plt.close(fig)
        data.seek(0)
        return send_file(
            data,
            as_attachment=True,
            mimetype='image/png',
            download_name=_summary_filename(
                profile_id,
                target_name,
                'png',
            ),
        )

    return jsonify(
        success=False,
        error='Unsupported format',
    ), 400


def _filter_group_objects(
    app, profile_id, group, accessible_rids
):
    """Return list of objects the user can see.

    If accessible_rids is empty the user can see nothing.
    Objects are matched against the object_table.json to
    determine their run_ids.
    """
    import json as _json
    from pathlib import Path

    base_dir = Path.home() / '.ari'
    # Need object_table to map objname -> run_ids
    objs_raw = group.get('objects', [])
    if not objs_raw:
        return []

    # Try to load the object table for run_id lookup
    run_id_map = _load_run_id_map(app, profile_id)

    result = []
    for obj_entry in objs_raw:
        if not isinstance(obj_entry, dict):
            continue
        objname = obj_entry.get('objname', '')
        if not objname:
            continue
        # Check if user can see this object
        obj_rids = run_id_map.get(objname, set())
        if obj_rids and not (obj_rids & accessible_rids):
            continue
        result.append(dict(
            objname=objname,
            added_by=obj_entry.get('added_by', ''),
            added_at=obj_entry.get('added_at', ''),
        ))
    return result


def _load_run_id_map(app, profile_id):
    """Build objname -> set(run_id) mapping from cache."""
    import json as _json
    from pathlib import Path

    if not hasattr(app, '_obj_group_rid_cache'):
        app._obj_group_rid_cache = {}

    if profile_id in app._obj_group_rid_cache:
        return app._obj_group_rid_cache[profile_id]

    base = Path.home() / '.ari'
    accessible = get_accessible_profiles(None, app.ari_groups)
    # find instrument for this profile
    instrument = None
    for prof in get_accessible_profiles(
        {'groups': ['super_admin']}, app.ari_groups
    ):
        if prof['profile_id'] == profile_id:
            instrument = prof['instrument']
            break

    if not instrument:
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    tasks_dir = base / 'tasks' / instrument
    json_path = tasks_dir / profile_id / 'object_table.json'
    if not json_path.exists():
        legacy = tasks_dir / (
            'object_table_{}.json'.format(profile_id)
        )
        if legacy.exists():
            json_path = legacy

    if not json_path.exists():
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    try:
        with open(json_path, encoding='utf-8') as f:
            data = _json.load(f)
    except Exception:
        app._obj_group_rid_cache[profile_id] = {}
        return {}

    rid_map = {}
    for row in data.get('rows', []):
        objname = str(row.get('OBJNAME', '')).strip()
        if not objname:
            continue
        raw = str(row.get('RUN_ID', '') or '')
        rids = {
            r.strip() for r in raw.split(',') if r.strip()
        }
        if objname in rid_map:
            rid_map[objname] |= rids
        else:
            rid_map[objname] = rids

    app._obj_group_rid_cache[profile_id] = rid_map
    return rid_map
