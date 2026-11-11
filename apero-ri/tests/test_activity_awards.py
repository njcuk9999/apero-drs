#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused, profile-free activity award integration tests."""
import datetime
import json
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace
from typing import Any

import pytest
from flask import Flask

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.core import awards
from tests.test_awards_views import awards_app


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_activity_awards'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')
_ROOT = Path(__file__).resolve().parents[1] / 'apero_ri'


# =============================================================================
# Define functions
# =============================================================================
def _write_preview(html: str, path: Path) -> None:
    """Write an isolated browser preview using the real local static assets.

    :param html: Rendered template content.
    :param path: Temporary output HTML file.
    :return: None.
    """
    html = html.replace('/static/', (_ROOT / 'static').as_uri() + '/')
    path.write_text(html, encoding='utf-8')
    print(f'Activity browser preview: {path}')


def test_activity_merge(monkeypatch: pytest.MonkeyPatch,
                        tmp_path: Path) -> None:
    """Merge activity-only accounts and preserve existing award fields.

    :param monkeypatch: Fixture replacing profile-dependent data sources.
    :param tmp_path: Isolated ARI data directory.
    :return: None.
    """
    from apero_ri import core

    activity = dict()
    activity['reader'] = dict(active_days=12, activity_medal='gold')
    activity['monitor'] = dict(active_days=8, activity_medal='silver')
    module = ModuleType('apero_ri.core.user_statistics')

    def activity_awards(data_dir: Path) -> dict:
        """Return the agreed activity contract for the isolated directory.

        :param data_dir: Requested ARI data directory.
        :return: Activity totals and medals by username.
        """
        assert data_dir == tmp_path
        return activity

    module.activity_awards = activity_awards
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(core, 'user_statistics', module, raising=False)
    hours = dict(monitor=dict(who='Monitor', total_hours=100,
                              instruments=dict()))
    monkeypatch.setattr(awards, 'compute_user_hours', lambda *args: hours)
    monkeypatch.setattr(awards, 'compute_resolved_issue_counts',
                        lambda *args: dict(resolver=500))
    usage = [dict(username='downloader', total_bytes=1024, total_files=4)]
    monkeypatch.setattr(awards.download_tracker, 'list_all_usage',
                        lambda category: usage if category == 'api' else [])
    records = awards.compute_awards(tmp_path, [])
    assert set(records) == {'reader', 'monitor', 'resolver', 'downloader'}
    assert records['reader']['active_days'] == 12
    assert records['reader']['activity_medal'] == 'gold'
    assert records['reader']['download_bytes'] == 0
    assert records['monitor']['service_medal'] == 'silver'
    assert records['monitor']['activity_medal'] == 'silver'
    assert records['resolver']['issues_medal'] == 'silver'
    assert records['downloader']['download_medals']['bytes'] == 'gold'
    for username in ('resolver', 'downloader'):
        assert records[username]['active_days'] == 0
        assert records[username]['activity_medal'] is None


def test_distinct_activity_totals(tmp_path: Path) -> None:
    """Award tied positive totals equally and exclude unqualified visits.

    :param tmp_path: Isolated activity storage directory.
    :return: None.
    """
    from apero_ri.core import user_statistics

    assert user_statistics.activity_awards(tmp_path) == dict()
    assert not list(tmp_path.iterdir())
    scores = dict(first=5, tied=5, second=4, third=2, fourth=1)
    first_day = datetime.date(2026, 1, 1)
    for username, total in scores.items():
        for offset in range(total):
            day = first_day + datetime.timedelta(days=offset)
            record_kwargs = dict(day=day)
            view_args = [tmp_path, username, '/home']
            user_statistics.record_page_view(*view_args, **record_kwargs)
            view_args[-1] = '/user_portal/awards'
            user_statistics.record_page_view(*view_args, **record_kwargs)
    user_statistics.record_page_view(tmp_path, 'candidate', '/home')
    records = user_statistics.activity_awards(tmp_path)
    assert set(records) == set(scores)
    expected = dict(first='gold', tied='gold', second='silver',
                    third='bronze', fourth=None)
    for username, total in scores.items():
        assert records[username] == dict(
            active_days=total, activity_medal=expected[username])


def test_public_summary_privacy() -> None:
    """Expose activity totals and medals without private dates or geography.

    :return: None.
    """
    from apero_ri.application import notifications_api_helpers as helpers

    entry = dict(active_days=7, activity_medal='silver',
                 days=['2026-01-01'], country='FR', region='Private')
    summary = helpers._user_award_summary(dict(reader=entry), 'reader')
    assert summary['active_days'] == 7
    assert summary['activity_medal'] == 'silver'
    assert not {'days', 'country', 'region'}.intersection(summary)
    assert '2026-01-01' not in json.dumps(summary)
    for records in (dict(), dict(reader=dict(total_hours=10))):
        defaults = helpers._user_award_summary(records, 'reader')
        assert defaults['active_days'] == 0
        assert defaults['activity_medal'] is None


@pytest.mark.parametrize('portal', ['user_portal', 'monitor_portal'])
@pytest.mark.parametrize('language, heading, days_label', [
    ('en', 'Most active users', 'Active days'),
    ('fr', 'Utilisateurs les plus actifs', 'Jours actifs'),
    ('es', 'Usuarios más activos', 'Días activos'),
])
def test_activity_leaderboard(
    awards_app: tuple[Flask, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    portal: str, language: str,
    heading: str, days_label: str,
) -> None:
    """Render activity-only users with registered names in both portals.

    :param awards_app: Existing isolated awards application fixture.
    :param monkeypatch: Fixture replacing the award source.
    :param tmp_path: Temporary browser preview directory.
    :param portal: Portal whose shared awards page is requested.
    :param language: Request-local language.
    :param heading: Translated activity section heading.
    :param days_label: Translated total label.
    :return: None.
    """
    from apero_ri.application import monitor_view_helpers as helpers

    app, state = awards_app
    state['permissions'] = {'view.user', 'monitor.SPIROU'}
    state['accounts']['active'] = dict(first_names='Ada', last_name='User')
    records = dict(active=dict(username='active', who='Stale schedule name',
                               active_days=9, activity_medal='gold'))
    monkeypatch.setattr(helpers.awards_core, 'compute_awards',
                        lambda *args: records)
    response = app.test_client().get(
        f'/{portal}/awards', headers={'Accept-Language': language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert heading in html
    assert days_label in html
    assert 'data-aw-kind="activity"' in html
    assert html.count('class="aw-board"') == 6
    payload = html.split('<script id="aw-data" type="application/json">')[1]
    rows = json.loads(payload.split('</script>')[0])
    assert rows[0]['who'] == 'Ada User'
    assert rows[0]['active_days'] == 9
    assert rows[0]['activity_medal'] == 'gold'
    assert rows[0]['total_hours'] == 0
    if language == 'en' and portal == 'user_portal':
        _write_preview(html, tmp_path / 'activity-awards.html')


@pytest.mark.parametrize('active_days, medal', [(7, 'gold'), (1, None),
                                               (0, None)])
def test_nonmonitor_activity_profile(
    awards_app: tuple[Flask, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    active_days: int, medal: str | None,
) -> None:
    """Show activity even without monitoring, downloads, or any award record.

    :param awards_app: Existing isolated template application fixture.
    :param monkeypatch: Fixture replacing authentication and award lookup.
    :param tmp_path: Isolated ARI data root.
    :param active_days: Profile total, including zero for an absent record.
    :param medal: Expected medal or None for a non-winning total.
    :return: None.
    """
    from apero_ri.application import user_portal_view_helpers as helpers

    app, state = awards_app
    owner = SimpleNamespace(args=SimpleNamespace(data_dir=str(tmp_path)),
                            ari_groups=dict())
    account = dict(groups=['general.SPIROU'])
    monkeypatch.setattr(helpers, 'get_effective_user',
                        lambda session: state['user'])
    monkeypatch.setattr(helpers, 'resolve_user_permissions',
                        lambda *args: {'view.user'})
    monkeypatch.setattr(helpers, 'load_users', lambda: dict(reader=account))
    records = dict()
    if active_days:
        records['reader'] = dict(active_days=active_days,
                                 activity_medal=medal)
    monkeypatch.setattr(helpers.awards_core, 'compute_awards',
                        lambda *args: records)
    app.add_url_rule('/profile', 'activity_test_profile',
                     lambda: helpers.user_portal_user_card_view(
                         owner, 'reader'))
    response = app.test_client().get('/profile')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Most active users' in html
    assert 'Active days' in html
    assert f'\n                    {active_days}\n' in html
    assert 'Monitoring statistics' not in html
    if medal:
        assert f'upu-medal--{medal}' in html
    else:
        assert 'fa-solid fa-medal' not in html
    _write_preview(html, tmp_path / 'activity-profile.html')


def test_activity_directory(
    awards_app: tuple[Flask, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Supply localized activity labels and preview active/idle user cards.

    :param awards_app: Existing isolated template application fixture.
    :param monkeypatch: Fixture replacing authentication.
    :param tmp_path: Temporary browser preview directory.
    :return: None.
    """
    from apero_ri.application import user_portal_view_helpers as helpers

    app, state = awards_app
    owner = SimpleNamespace(ari_groups=dict())
    monkeypatch.setattr(helpers, 'get_effective_user',
                        lambda session: state['user'])
    monkeypatch.setattr(helpers, 'resolve_user_permissions',
                        lambda *args: {'view.user'})
    app.add_url_rule('/directory', 'activity_test_directory',
                     lambda: helpers.user_portal_users_view(owner))
    response = app.test_client().get('/directory')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"active_days": "Active days"' in html
    assert '"active_users": "Most active users"' in html
    assert 'v=20261111b' in html
    users = [dict(username='reader', first_names='Ada', last_name='User',
                  groups=['general.SPIROU'], awards=dict(
                      active_days=9, activity_medal='gold')),
             dict(username='idle', awards=dict(active_days=0))]
    payload = json.dumps(dict(success=True, users=users))
    stub = ('<script>window.fetch = function () { return Promise.resolve('
            '{json: function () { return Promise.resolve('
            + payload + '); }}); };</script>')
    html = html.replace('</head>', stub + '</head>')
    _write_preview(html, tmp_path / 'activity-directory.html')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================