#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Admin-only views and visualisations for qualified UTC user activity."""
from datetime import datetime
from functools import lru_cache
from html import escape
from io import BytesIO
import json
from pathlib import Path
from typing import Any

from bokeh.embed import json_item
from bokeh.models import ColorBar, ColumnDataSource
from bokeh.models import HoverTool, LinearColorMapper
from bokeh.palettes import Viridis256
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import abort, jsonify, render_template, request, send_file, session
from flask import Response

from aperocore.drs_lang import textentry
from apero_ri.base import base
from apero_ri.core import ari_lang_support as lang
from apero_ri.core import auth
from apero_ri.core import permissions
from apero_ri.core import user_statistics
from apero_ri.plots.bokeh_theme import apply_bokeh_theme, theme_palette


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.user_statistics_helpers'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
PAGE_ID = 'home.admin_portal.user_statistics'
PERMISSION = 'view.admin.user_statistics'
UI_TEXT = dict(
    TITLE='User Statistics', UNAUTHORIZED='Authentication required.',
    FORBIDDEN='User statistics permission required.',
    USER_DAYS='User-days', ACTIVE_USERS='Active users',
    REGISTERED_USERS='Registered users', CALENDAR_DAYS='Calendar days',
    WEEKLY='Weekly user-days', WORLD='Users by country',
    COUNTRY='Country', REGION='Region', USERS='Users', WEEK='Week',
    COUNTRIES='Countries', REGIONS='Regions', START='Start date',
    END='End date', PERIOD='Selected period', EXPORT='Export PDF',
    UNKNOWN='Unknown', EMPTY='No qualified activity in this period.',
    LOADING='Loading user statistics...',
    ERROR='Unable to load user statistics.',
    INVALID='Enter valid ISO dates with start on or before end.',
    PRIVACY=('A user-day requires two distinct successful navigations per '
             'UTC day. Counts begin at rollout; no IP addresses are saved. '
             'Unavailable locations are listed as unknown.'))
_GEOMETRY = (Path(__file__).resolve().parents[1] / 'static' / 'data'
             / 'countries.geojson')


# =============================================================================
# Define functions
# =============================================================================
def labels() -> dict[str, str]:
    """Return request-local labels through the APERO language database.

    :return: Translated labels indexed by USER_STATISTICS key suffix.
    """
    result = dict()
    for key, english in UI_TEXT.items():
        translated = lang.translate(english)
        entry = textentry('USER_STATISTICS_' + key, message=translated)
        result[key] = str(entry)
    return result


def _require_statistics(app: Any) -> tuple[dict[str, Any], set[str]]:
    """Require dedicated statistics access, not general admin visibility.

    :param app: ARI application with the configured group hierarchy.
    :return: Authenticated effective account and its resolved permissions.
    :raises HTTPException: 401 when logged out or 403 without permission.
    """
    user = auth.get_effective_user(session)
    if not user:
        abort(401, description=labels()['UNAUTHORIZED'])
    perms = permissions.resolve_user_permissions(user['groups'], app.ari_groups)
    if PERMISSION not in perms:
        abort(403, description=labels()['FORBIDDEN'])
    return user, perms


def page(app: Any) -> str:
    """Render the admin page using the shared sidebar and local Bokeh assets.

    :param app: ARI application providing sidebar context.
    :return: Rendered statistics HTML after permission enforcement.
    """
    user, perms = _require_statistics(app)
    context = app._build_sidebar_context(PAGE_ID, perms, user)
    context.update(page_id=PAGE_ID, page_label=labels()['TITLE'])
    context.update(page_icon='fa-solid fa-chart-column')
    context.update(statistics_labels=labels(), bokeh_js=_bokeh_resources())
    return render_template('admin/user_statistics.html', **context)


@lru_cache(maxsize=1)
def _bokeh_resources() -> str:
    """Load version-matched Bokeh JavaScript without a browser CDN request.

    :return: Script tags supplied by the installed Bokeh distribution.
    """
    return INLINE.render_js()


def _selected_summary(app: Any) -> dict[str, Any]:
    """Read the inclusive selected range and current registered account count.

    :param app: ARI application resolving its local data root.
    :return: Real core summary plus registered_users.
    :raises ValueError: Invalid or reversed ISO date filters.
    """
    filters = dict(start=request.args.get('start') or None,
                   end=request.args.get('end') or None)
    data_dir = Path(app._resolve_local_data_dir())
    data = user_statistics.summary(data_dir, **filters)
    data['registered_users'] = len(auth.load_users())
    return data


def api(app: Any, pdf: bool = False) -> Any:
    """Serve the same authorized selected summary as JSON plots or a PDF.

    :param app: ARI application resolving accounts and local activity data.
    :param pdf: Return a downloadable PDF instead of JSON.
    :return: A no-store Flask response; invalid dates return HTTP 400.
    """
    _require_statistics(app)
    ui = labels()
    try:
        data = _selected_summary(app)
    except (ValueError, OverflowError):
        return jsonify(error=ui['INVALID']), 400
    if pdf:
        from apero_ri.core import fail_report
        from apero_ri.core.user_statistics_pdf import build_report

        payload = build_report(data, ui)
        filename = f'user-statistics-{data["start"]}-{data["end"]}.pdf'
        fail_report.store_report_pdf(payload, dict(filename=filename))
        response = send_file(BytesIO(payload), mimetype='application/pdf',
                             as_attachment=True, download_name=filename)
    else:
        theme = request.args.get('theme', 'default')
        payload = dict(summary=data, plots=_plots(data, ui, theme))
        response = Response(json.dumps(payload), mimetype='application/json')
    response.headers['Cache-Control'] = 'private, no-store'
    return response


@lru_cache(maxsize=1)
def _country_geometry() -> dict[str, Any]:
    """Load the public-domain country polygons vendored with the application.

    :return: GeoJSON FeatureCollection; callers must not mutate it.
    """
    return json.loads(_GEOMETRY.read_text(encoding='utf-8'))


def _tooltip(rows: list[tuple[str, str]]) -> str:
    """Build escaped Bokeh tooltip labels using inherited ARI theme variables.

    :param rows: Translated labels paired with Bokeh field specifications.
    :return: Tooltip HTML with no fixed palette colors.
    """
    content = ''.join(f'<div>{escape(label)}: {field}</div>'
                      for label, field in rows)
    style = ('<style>:host {background:var(--ari-card-bg);'
             'color:var(--ari-text);border-color:var(--ari-border);}</style>')
    wrapper = ('<div style="background:var(--ari-card-bg);'
               'color:var(--ari-text);padding:0.4rem">')
    return style + wrapper + content + '</div>'


def _plots(data: dict[str, Any], ui: dict[str, str], theme: str) -> dict:
    """Build themed weekly and interactive country choropleth Bokeh items.

    :param data: Selected core summary and current registered user count.
    :param ui: Request-local interface labels.
    :param theme: Requested ARI theme.
    :return: Bokeh JSON items keyed by weekly and world.
    """
    weekly = data['weekly']
    source = ColumnDataSource(dict(
        week=[datetime.fromisoformat(row['week']) for row in weekly],
        user_days=[row['user_days'] for row in weekly],
        users=[row['users'] for row in weekly]))
    plot_kwargs = dict(height=290, sizing_mode='stretch_width',
                       x_axis_type='datetime', tools='pan,xwheel_zoom,reset',
                       active_scroll='xwheel_zoom', toolbar_location='above')
    weekly_fig = figure(**plot_kwargs)
    weekly_fig.vbar(x='week', top='user_days', source=source,
                    width=5 * 86400000, color=Viridis256[135])
    weekly_fig.y_range.start = 0
    weekly_fig.yaxis.axis_label = ui['USER_DAYS']
    weekly_rows = [(ui['WEEK'], '@week{%F}'),
                   (ui['USER_DAYS'], '@user_days'), (ui['USERS'], '@users')]
    hover = HoverTool(tooltips=_tooltip(weekly_rows))
    hover.formatters = {'@week': 'datetime'}
    weekly_fig.add_tools(hover)
    apply_bokeh_theme(weekly_fig, theme)

    counts = {row['country']: row for row in data['countries']}
    map_data = dict(xs=[], ys=[], name=[], user_days=[], users=[], intensity=[])
    for original in _country_geometry()['features']:
        props = original['properties']
        count = counts.get(props['country'], dict())
        geometry = original['geometry']
        polygons = geometry['coordinates']
        if geometry['type'] == 'Polygon':
            polygons = [polygons]
        for axis, key in enumerate(('xs', 'ys')):
            rings = [[[point[axis] for point in ring] for ring in polygon]
                     for polygon in polygons]
            map_data[key].append(rings)
        map_data['name'].append(props['name'])
        map_data['user_days'].append(count.get('user_days', 0))
        map_data['users'].append(count.get('users', 0))
        map_data['intensity'].append(count.get('users') or float('nan'))
    geo_source = ColumnDataSource(map_data)
    maximum = max([row['users'] for row in data['countries']] or [1])
    palette = theme_palette(theme)
    mapper = LinearColorMapper(palette=Viridis256[65:], low=0,
                               high=max(maximum, 1), nan_color=palette['grid'])
    map_kwargs = dict(height=380, sizing_mode='stretch_width',
                      tools='pan,wheel_zoom,reset,tap',
                      active_scroll=None, toolbar_location='above',
                      match_aspect=True)
    world = figure(**map_kwargs)
    world.x_range.range_padding = 0
    world.y_range.range_padding = 0
    glyph_kwargs = dict(source=geo_source, line_color=palette['grid'],
                        line_width=0.5,
                        fill_color=dict(field='intensity', transform=mapper))
    renderer = world.multi_polygons('xs', 'ys', **glyph_kwargs)
    map_rows = [(ui['COUNTRY'], '@name'), (ui['USER_DAYS'], '@user_days'),
                (ui['USERS'], '@users')]
    world.add_tools(HoverTool(renderers=[renderer],
                              tooltips=_tooltip(map_rows)))
    world.axis.visible = False
    world.grid.visible = False
    bar = ColorBar(color_mapper=mapper, location=(0, 0),
                   background_fill_color=palette['bg'],
                   major_label_text_color=palette['text'],
                   title_text_color=palette['text'], title=ui['USERS'])
    world.add_layout(bar, 'below')
    apply_bokeh_theme(world, theme)
    return dict(weekly=json_item(weekly_fig, 'us-weekly'),
                world=json_item(world, 'us-world'))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================