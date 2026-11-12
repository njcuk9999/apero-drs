"""Tests for the queue GUI Info tab and its shared ARI docs include."""
import webbrowser
from typing import Any

import pytest

from apero.tools.module.documentation import ari_docs
from apero.tools.module.processing import drs_queue_gui


@pytest.mark.parametrize(('headless', 'open_count'), [
    (False, 1),
    (True, 0),
])
def test_queue_gui_headless_suppresses_browser(
    monkeypatch: Any, headless: bool, open_count: int,
) -> None:
    """Keep the dashboard running without opening a browser when requested.

    :param monkeypatch: Pytest monkeypatch fixture.
    :param headless: Whether browser launching should be suppressed.
    :param open_count: Expected number of browser launch calls.
    :return: None.
    """
    served = []

    class FakeServer:
        """Minimal server stand-in for the dashboard lifecycle."""

        def __init__(
            self,
            address: tuple[str, int],
            command: list[str],
        ) -> None:
            self.server_address = address

        def start_worker(self) -> None:
            pass

        def worker_request(self, path: str) -> dict[str, bool]:
            return dict(busy=False)

        def serve_forever(self) -> None:
            served.append(True)
            raise KeyboardInterrupt

        def server_close(self) -> None:
            pass

        def finish_worker(self) -> None:
            pass

    opened = []
    params = dict(INPUTS=dict(
        HOST='None',
        PORT='None',
        ROWS='None',
        HEADLESS=headless,
    ))
    monkeypatch.delenv(
        drs_queue_gui.drs_queue_server.WORKER_PORT_ENV,
        raising=False,
    )
    monkeypatch.setattr(
        drs_queue_gui.drs_queue,
        'setup_queue_directories',
        lambda params: None,
    )
    monkeypatch.setattr(
        drs_queue_gui.drs_queue_server,
        'QueueServer',
        FakeServer,
    )
    monkeypatch.setattr(
        drs_queue_gui,
        '_make_handler',
        lambda params, state, rows: object,
    )
    monkeypatch.setattr(drs_queue_gui, 'WLOG', lambda *args, **kwargs: None)
    monkeypatch.setattr(webbrowser, 'open', lambda url: opened.append(url))

    drs_queue_gui.queue_gui(params)

    assert len(opened) == open_count
    assert served == [True]


def test_render_info_html_lists_every_control_tab():
    html = drs_queue_gui.render_info_html()
    for tab in ['Info', 'Generate', 'Run', 'Batch', 'Chain', 'Actions',
                'Template']:
        assert '<li><strong>{0}</strong>:'.format(tab) in html
    assert html.count('<ul>') == html.count('</ul>') == 1
    assert '<code>apero_queue.py run</code>' in html


def test_render_info_html_escapes_html(tmp_path):
    path = tmp_path / 'info.md'
    path.write_text('## Title\n\nA <b>tag</b> and `x`\n', encoding='utf-8')
    html = drs_queue_gui.render_info_html(str(path))
    assert '<h3>Title</h3>' in html
    assert '&lt;b&gt;tag&lt;/b&gt;' in html
    assert '<code>x</code>' in html


def test_job_tail_keeps_ansi_only_when_asked(tmp_path):
    path = tmp_path / 'job.log'
    path.write_text('\x1b[31mred\x1b[0m\rdone\n', encoding='utf-8')
    coloured = drs_queue_gui._job_tail(str(path), 10, keep_ansi=True)
    assert coloured == ['\x1b[31mred\x1b[0m', 'done']
    assert drs_queue_gui._job_tail(str(path), 10) == ['red', 'done']


def test_status_details_read_once_per_qid(tmp_path, monkeypatch):
    run = tmp_path / 'run.yaml'
    run.write_text('priority: 1\nrecipe: r.py\nrunstring: r.py a\n',
                   encoding='utf-8')
    entry = dict(state='pending', group='G', run='R', path=str(run))
    monkeypatch.setattr(drs_queue_gui.drs_queue, 'list_queue_entries',
                        lambda params, states=None: [dict(entry)])
    monkeypatch.setattr(drs_queue_gui.drs_queue, 'get_queue_path',
                        lambda params: str(tmp_path))
    first = drs_queue_gui.get_status_data(None)['entries'][0]
    assert first['recipe'] == 'r.py'
    # a moved file (different path) still uses the cached details
    entry['state'], entry['path'] = 'complete', str(tmp_path / 'gone.yaml')
    second = drs_queue_gui.get_status_data(None)['entries'][0]
    assert second['state'] == 'complete'
    assert second['runstring'] == 'r.py a'


def test_queue_description_includes_gui_info():
    _, body = ari_docs.read_description('spirou', 'user_tools',
                                        'apero_queue')
    info = open(drs_queue_gui.GUI_INFO_PATH, encoding='utf-8').read()
    assert 'include:' not in body
    assert info.strip() in body


def test_activity_messages_are_separate_and_bounded() -> None:
    """Each page retains only its own bounded activity history.

    :return: None.
    """
    state = drs_queue_gui.GuiState()
    state.add_message('run progress')
    state.add_message('generate progress', 'generate')
    state.add_message('action result', 'actions')
    assert state.activity_messages['run'][0].endswith('run progress')
    assert state.activity_messages['generate'][0].endswith(
        'generate progress')
    assert state.activity_messages['actions'][0].endswith('action result')
    for index in range(drs_queue_gui.GUI_MAX_MESSAGES + 1):
        state.add_message(str(index), 'generate')
    assert len(state.activity_messages['generate']) == (
        drs_queue_gui.GUI_MAX_MESSAGES)
    assert len(state.activity_messages['run']) == 1
    assert len(state.activity_messages['actions']) == 1


def test_console_jobs_are_retained_per_page(tmp_path) -> None:
    """Later reset output does not replace the Generate console.

    :param tmp_path: Path, pytest temporary directory.
    :return: None.
    """
    state = drs_queue_gui.GuiState()
    for channel in ['generate', 'actions']:
        path = tmp_path / (channel + '.log')
        path.write_text(channel + ' output\n', encoding='utf-8')
        state.jobs[channel] = dict(kind=channel, path=str(path))
    state.job = state.jobs['actions']
    generated = drs_queue_gui.get_job_data(state, 'generate')
    reset = drs_queue_gui.get_job_data(state, 'actions')
    assert generated['lines'] == ['generate output']
    assert reset['lines'] == ['actions output']
    assert drs_queue_gui.get_job_data(state, 'run') == {}
    assert drs_queue_gui.get_job_data(state)['kind'] == 'actions'
