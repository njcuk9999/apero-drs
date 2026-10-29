"""Tests for the queue GUI Info tab and its shared ARI docs include."""
from apero.tools.module.documentation import ari_docs
from apero.tools.module.processing import drs_queue_gui


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
