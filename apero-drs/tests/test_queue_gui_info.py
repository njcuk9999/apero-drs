"""Tests for the queue GUI Info tab and its shared ARI docs include."""
import http.client
import json
import subprocess
import threading
import webbrowser
from http.server import ThreadingHTTPServer
from typing import Any

import pytest

from apero import dev
from apero.tools.module.documentation import ari_docs
from apero.tools.module.processing import drs_queue_gui


def test_runtime_info_reports_git_snapshot(monkeypatch: Any) -> None:
    """Report the checkout and whether its queue sources were modified.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    dev.get_base_params('SPIROU')
    calls = []

    def run(command: list[str], **kwargs: Any) -> Any:
        """Return deterministic Git results for the startup snapshot."""
        calls.append(command)
        if 'show' in command:
            output = 'abc123\n2026-11-20T10:00:00+00:00\n'
        elif 'rev-parse' in command:
            output = 'main\n'
        elif 'status' in command:
            output = ' M drs_queue.py\n'
        else:
            output = ''
        return subprocess.CompletedProcess(command, 0, stdout=output)

    monkeypatch.setattr(drs_queue_gui.subprocess, 'run', run)
    monkeypatch.setenv('DRS_UCONFIG', '/config/profile')
    info = drs_queue_gui.get_runtime_info()
    assert info['version'] == drs_queue_gui.__version__
    assert info['queue_source'].endswith('drs_queue.py')
    assert info['config'] == '/config/profile'
    assert info['git'] == dict(commit='abc123',
                               commit_date='2026-11-20T10:00:00+00:00',
                               branch='main', queue_sources_modified=True)
    assert 'ls-files' in calls[0]


def test_runtime_info_exposes_git_failure(monkeypatch: Any) -> None:
    """A missing Git executable is reported rather than silently hidden.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    dev.get_base_params('SPIROU')

    def fail(*args: Any, **kwargs: Any) -> None:
        """Simulate an unavailable Git executable."""
        raise FileNotFoundError('git unavailable')

    monkeypatch.setattr(drs_queue_gui.subprocess, 'run', fail)
    info = drs_queue_gui.get_runtime_info()
    assert 'git unavailable' in info['git']['error']


def test_runtime_info_handles_git_timeout_output(monkeypatch: Any) -> None:
    """Keep timeout output JSON serializable even if it is bytes.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    dev.get_base_params('SPIROU')

    def fail(*args: Any, **kwargs: Any) -> None:
        """Simulate Git timing out after producing stderr."""
        raise subprocess.TimeoutExpired('git', 5, stderr=b'git timed out')

    monkeypatch.setattr(drs_queue_gui.subprocess, 'run', fail)
    info = drs_queue_gui.get_runtime_info()
    assert json.loads(json.dumps(info))['git']['error'] == 'git timed out'


def test_runtime_info_api_is_a_startup_snapshot(monkeypatch: Any) -> None:
    """Serve the worker snapshot unchanged through the dashboard API.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    dev.get_base_params('SPIROU')
    calls = []

    def snapshot() -> dict[str, Any]:
        """Record snapshot creation."""
        calls.append(True)
        return dict(version='worker-version', git=dict(commit='abc123'))

    monkeypatch.setattr(drs_queue_gui, 'get_runtime_info', snapshot)
    handler = drs_queue_gui._make_handler(
        drs_queue_gui.ParamDict(), drs_queue_gui.GuiState(), 100)
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        for _ in range(2):
            connection = http.client.HTTPConnection(
                *server.server_address, timeout=5)
            try:
                connection.request('GET', '/api/runtime_info')
                response = connection.getresponse()
                assert response.status == 200
                assert json.loads(response.read())['git']['commit'] == 'abc123'
            finally:
                connection.close()
        assert calls == [True]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_reset_action_blocks_queue_actions() -> None:
    """Keep the reset active until its worker and cleanup have finished.

    :return: None.
    """
    state = drs_queue_gui.GuiState()
    started = threading.Event()
    release = threading.Event()

    def reset_worker() -> None:
        """Simulate a reset that remains active until released."""
        started.set()
        release.wait(timeout=5)

    assert state.start_action('Reset', reset_worker, ())
    try:
        assert started.wait(timeout=5)
        assert state.active_action == 'Reset'
        result = drs_queue_gui.action_queue(
            drs_queue_gui.ParamDict(), state, 'stop_all_running')
        assert not result['success']
        assert not state.cancel.is_set()
    finally:
        release.set()
        assert state.worker is not None
        state.worker.join(timeout=5)
    assert not state.busy
    assert state.active_action is None


def test_queue_state_reset_releases_busy_on_error(monkeypatch: Any) -> None:
    """A failed synchronous reset must not leave the dashboard blocked.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    state = drs_queue_gui.GuiState()

    def failing_reset(*values: Any, **options: Any) -> int:
        """Observe the active reset before simulating a cleanup error."""
        assert state.busy
        assert state.active_action == 'Reset'
        raise RuntimeError('reset failed')

    monkeypatch.setattr(drs_queue_gui.drs_queue, 'reset_queue', failing_reset)
    with pytest.raises(RuntimeError, match='reset failed'):
        drs_queue_gui.action_reset(drs_queue_gui.ParamDict(), state)
    assert not state.busy
    assert state.active_action is None


@pytest.mark.parametrize(('headless', 'worker_port', 'open_count'), [
    (False, None, 1),
    (True, None, 0),
    (False, '63307', 0),
    (True, '63307', 0),
])
def test_queue_gui_headless_suppresses_browser(
    monkeypatch: Any, headless: bool, worker_port: str | None,
    open_count: int,
) -> None:
    """Keep the dashboard running without opening a browser when requested.

    :param monkeypatch: Pytest monkeypatch fixture.
    :param headless: Whether browser launching should be suppressed.
    :param worker_port: Private worker port, or None for the public server.
    :param open_count: Expected number of browser launch calls.
    :return: None.
    """
    dev.get_base_params('SPIROU')
    served = []
    messages = []

    class FakeServer:
        """Minimal server stand-in for the dashboard lifecycle."""

        def __init__(
            self,
            address: tuple[str, int],
            command: Any,
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
    if worker_port is not None:
        monkeypatch.setenv(
            drs_queue_gui.drs_queue_server.WORKER_PORT_ENV, worker_port)
    monkeypatch.setattr(drs_queue_gui, 'ThreadingHTTPServer', FakeServer)
    monkeypatch.setattr(drs_queue_gui, '_stale_watcher', lambda *args: None)
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
    monkeypatch.setattr(
        drs_queue_gui, 'WLOG',
        lambda params, level, message: messages.append(message))
    monkeypatch.setattr(webbrowser, 'open', lambda url: opened.append(url))

    drs_queue_gui.queue_gui(params)

    assert len(opened) == open_count
    assert served == [True]
    message_key = '40-513-00028' if worker_port is None else '40-513-00047'
    port = drs_queue_gui.GUI_DEFAULT_PORT if worker_port is None else worker_port
    url = 'http://127.0.0.1:{0}/'.format(port)
    assert messages[0] == drs_queue_gui.textentry(message_key, args=[url])


def test_render_info_html_lists_every_control_tab():
    html = drs_queue_gui.render_info_html()
    for tab in ['Info', 'Generate', 'Run', 'Batch', 'Chain', 'Actions',
                'Template']:
        assert '<li><strong>{0}</strong>:'.format(tab) in html
    assert html.count('<ul>') == html.count('</ul>') == 1
    assert '<code>apero_queue.py run</code>' in html


def test_chain_array_help_is_rendered_and_associated(
    monkeypatch: Any,
) -> None:
    """Render the localized explanation alongside its chain input.

    :param monkeypatch: Pytest monkeypatch fixture.
    :return: None.
    """
    params = dev.get_base_params('SPIROU')
    monkeypatch.setattr(drs_queue_gui.drs_queue, 'get_queue_path',
                        lambda params: '/queue')
    monkeypatch.setattr(drs_queue_gui.drs_queue, 'get_queue_mpmode',
                        lambda params: 'linear')
    html = drs_queue_gui.render_dashboard(params)
    assert 'aria-describedby="chain-per-help"' in html
    for key in ['40-513-00052', '40-513-00053', '40-513-00054']:
        assert drs_queue_gui.textentry(key) in html


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
