#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the generic browser gui framework (aperocore.gui)

Covers the side by side diff, the comment preserving yaml outline / edits,
the safe file access rules, batch scripts / templates, the process
registry job directory, markdown rendering, the interactive job runner and
the GuiApp routing (static assets, built-in routes, 404s).
"""
import json
import os
import sys
import time
from pathlib import Path

import pytest

from aperocore.gui import diff
from aperocore.gui import files
from aperocore.gui import jobs
from aperocore.gui import procs
from aperocore.gui import slurm
from aperocore.gui import webapp
from aperocore.gui import yaml_outline

# a small commented yaml (layout as written by ConstDict.save_yaml)
YAML_TEXT = """# header comment
# =====================================
# global settings
# =====================================
GLOBAL:
  # the data path
  DATA_PATH: /data   # inline comment
  FLAG: true
MOD:
  INPUTS:
    # files to use
    FILES:
    - a.fits
    - b.fits
    NAME: 'abc'
"""


# =============================================================================
# Define tests
# =============================================================================
def test_diff_rows_and_stats() -> None:
    """Changed lines pair up with character spans; inserts are counted."""
    result = diff.side_by_side('a\nhello world\nc\n', 'a\nhello there\nc\nd\n')
    assert result['stats'] == dict(added=1, removed=0, changed=1)
    tags = [row['tag'] for row in result['rows']]
    assert tags == ['equal', 'replace', 'equal', 'insert']
    changed = result['rows'][1]
    assert changed['lspans'] and changed['rspans']
    assert result['changes'] == [1, 3]
    assert not result['identical']


def test_diff_fold_keeps_context() -> None:
    """Long equal runs fold, keeping context rows next to changes."""
    left = '\n'.join(str(it) for it in range(100))
    right = left.replace('50', 'fifty')
    result = diff.side_by_side(left, right, context=2)
    folds = [row for row in result['rows'] if row['tag'] == 'fold']
    assert len(folds) == 2
    assert sum(fold['count'] for fold in folds) == 99 - 4
    assert diff.side_by_side('x', 'x')['identical']


def test_yaml_outline_sections_comments_lists() -> None:
    """The outline finds paths, comments, sections and block lists."""
    out = yaml_outline.outline(YAML_TEXT)
    assert out['error'] is None
    nodes = {'.'.join(node['path']): node for node in out['nodes']}
    assert nodes['GLOBAL']['section'] == 'global settings'
    assert nodes['GLOBAL.DATA_PATH']['comment'] == 'the data path'
    assert nodes['GLOBAL.DATA_PATH']['inline'] == 'inline comment'
    assert nodes['GLOBAL.FLAG']['vtype'] == 'bool'
    assert nodes['MOD.INPUTS.FILES']['kind'] == 'list'
    assert nodes['MOD.INPUTS.FILES']['items'] == ['a.fits', 'b.fits']
    assert nodes['MOD.INPUTS']['kind'] == 'map'


def test_yaml_apply_edits_preserves_layout() -> None:
    """Edits only change values; comments and other lines are kept."""
    nodes = {'.'.join(node['path']): node
             for node in yaml_outline.outline(YAML_TEXT)['nodes']}
    edits = [dict(line=nodes['GLOBAL.DATA_PATH']['line'], key='DATA_PATH',
                  value='/new'),
             dict(line=nodes['MOD.INPUTS.FILES']['line'], key='FILES',
                  items=['c.fits'])]
    result = yaml_outline.apply_edits(YAML_TEXT, edits)
    assert result['errors'] == []
    text = result['text']
    assert '  DATA_PATH: /new  # inline comment' in text
    assert '- c.fits' in text and 'a.fits' not in text
    assert '# files to use' in text and '# header comment' in text
    # a stale edit (key no longer on that line) is refused
    stale = yaml_outline.apply_edits(YAML_TEXT, [dict(line=0, key='X',
                                                      value='1')])
    assert stale['errors'] and stale['applied'] == 0


def test_yaml_apply_mapping_edit() -> None:
    """A key (short or long form) can be rewritten as a mapping; the
    comments around it are kept."""
    text = ('A:\n'
            '  # about F\n'
            '  F:  # inline\n'
            '  # about G\n'
            '  G:\n'
            '    filelist:\n'
            '    - a.fits\n'
            '    source: mast\n'
            '    pid: 1\n'
            '  H: 2\n')
    nodes = {node['key']: node
             for node in yaml_outline.outline(text)['nodes']}
    edits = [dict(line=nodes['F']['line'], key='F',
                  mapping=[dict(key='filelist', value='x.fits'),
                           dict(key='source', value='pogos'),
                           dict(key='url', value='')]),
             dict(line=nodes['G']['line'], key='G',
                  mapping=[dict(key='filelist', items=['a.fits']),
                           dict(key='source', value='local')])]
    result = yaml_outline.apply_edits(text, edits)
    assert result['errors'] == []
    import yaml
    values = yaml.safe_load(result['text'])['A']
    assert values['F'] == dict(filelist='x.fits', source='pogos', url=None)
    assert values['G'] == dict(filelist=['a.fits'], source='local')
    assert values['H'] == 2
    assert '# about G' in result['text']
    assert '  F:  # inline' in result['text']
    # an empty mapping turns the key back into the short (empty) form
    back = yaml_outline.apply_edits(text, [dict(line=nodes['G']['line'],
                                                key='G', mapping=[])])
    assert yaml.safe_load(back['text'])['A']['G'] is None


def test_progress_steps_and_marks() -> None:
    """Steps nest, marks end each other and failures close open steps."""
    from aperocore import progress
    events = []
    progress.set_writer(lambda event, **fields: events.append(
        (event, '/'.join(fields.get('path') or []),
         fields.get('status'))))
    try:
        with progress.step('A', items=['x']):
            progress.mark('m1')
            progress.mark('m2')
        with pytest.raises(ValueError):
            with progress.step('B'):
                progress.start('C')
                raise ValueError('boom')
    finally:
        progress.set_writer(None)
    assert events == [('step_start', 'A', None),
                      ('step_start', 'A/m1', None),
                      ('step_end', 'A/m1', 'complete'),
                      ('step_start', 'A/m2', None),
                      ('step_end', 'A/m2', 'complete'),
                      ('step_end', 'A', 'complete'),
                      ('step_start', 'B', None),
                      ('step_start', 'B/C', None),
                      ('step_end', 'B/C', 'failed'),
                      ('step_end', 'B', 'failed')]
    # without a writer nothing is recorded (and nothing breaks)
    with progress.step('D'):
        progress.mark('E')
    assert not progress.active()


def test_code_view_functions_and_blocks(tmp_path: Path) -> None:
    """Functions are found by parsing (source + docstring), blocks end at
    the next progress mark, and only python path code is readable."""
    from aperocore.gui import code_view
    found = code_view.find_function('aperocore.gui.code_view.read_block')
    assert found['error'] is None
    assert found['lines'][0][1].startswith('def read_block(')
    assert found['doc'].startswith('Read the code starting at a line')
    method = code_view.find_function(
        'aperocore.gui.webapp.Response.error')
    assert method['error'] is None and method['line'] > 1
    missing = code_view.find_function('aperocore.gui.code_view.nothing')
    assert 'not found' in missing['error']
    assert code_view.find_function('not a path')['error']
    # a block runs to the next mark at the same indent
    import aperocore.progress as progress_module
    source = progress_module.__file__
    lines = open(source).read().splitlines()
    first = [it + 1 for it, line in enumerate(lines)
             if line.startswith('def mark(')][0]
    block = code_view.read_block(source, first)
    assert block['error'] is None and block['end'] > first
    # files outside the python path are refused
    outside = tmp_path / 'x.py'
    outside.write_text('print(1)\n')
    assert not code_view.allowed_file(str(outside))
    assert code_view.read_block(str(outside), 1)['error']


def test_progress_named_nodes_and_call_sites() -> None:
    """named_node reads KEY / KEY_FUNC / KEY_DESC; steps record where the
    code marked them."""
    from aperocore import progress
    space = dict(STEP='A step', STEP_FUNC='pkg.mod.func',
                 STEP_DESC='Does things', OTHER='Other')
    assert progress.named_node(space, 'STEP') == dict(
        name='A step', children=[], loop=False, desc='Does things',
        func='pkg.mod.func')
    assert progress.named_node(space, 'OTHER')['func'] is None
    events = []
    progress.set_writer(lambda event, **fields: events.append(fields))
    try:
        with progress.step('A'):
            # the line of the mark call (the next line)
            line = sys._getframe().f_lineno + 1
            progress.mark('B')
    finally:
        progress.set_writer(None)
    starts = [event for event in events if 'src_file' in event]
    assert all(event['src_file'] == __file__ for event in starts)
    assert starts[1]['src_line'] == line


class _PlanDemo:
    """A class with decorated step methods (for the plan tests)."""
    from aperocore import progress as _progress
    _NS = dict(A='Step A', B='Step B', SAVE='Save', SAVE_DESC='Saves')

    def process(self) -> None:
        """Run the steps (one is commented out)."""
        self.step_a()
        # self.step_b()
        self.save('_x.fits')
        self.save('_y.fits')
        self.helper()

    @_progress.step_method(_NS, 'A')
    def step_a(self) -> None:
        """Step a docstring."""
        self.step_b()

    @_progress.step_method(_NS, 'B')
    def step_b(self) -> None:
        """Step b docstring."""

    @_progress.step_method(_NS, 'SAVE', label_arg=0)
    def save(self, suffix: str) -> None:
        """Save docstring."""

    def helper(self) -> None:
        """Not a step."""


def test_progress_plan_from_calls() -> None:
    """The plan of a method lists its decorated calls in source order
    (nested calls become children; comments are not code) and the calls
    record matching steps."""
    from aperocore import progress
    plan = progress.plan_from_calls(_PlanDemo, 'process')
    assert [n['name'] for n in plan] == ['Step A', 'Save (_x.fits)',
                                         'Save (_y.fits)']
    assert [c['name'] for c in plan[0]['children']] == ['Step B']
    assert plan[0]['func'].endswith('_PlanDemo.step_a')
    assert plan[1]['desc'] == 'Saves'
    events = []
    progress.set_writer(lambda event, **fields: events.append(
        (event, '/'.join(fields.get('path') or []))))
    try:
        _PlanDemo().process()
    finally:
        progress.set_writer(None)
    starts = [path for event, path in events if event == 'step_start']
    assert starts == ['Step A', 'Step A/Step B', 'Save (_x.fits)',
                      'Save (_y.fits)']
    # without a writer the methods just run
    _PlanDemo().process()


def test_app_icon(tmp_path: Path) -> None:
    """An application icon is added to the page (tab icon + corner icon)
    only when its file exists."""
    icon = webapp.app_icon_html('static/app/x.ico', 'Demo <app>')
    assert icon['head'] == '<link rel="icon" href="static/app/x.ico">'
    assert 'class="gui-app-icon"' in icon['body']
    assert 'Demo &lt;app&gt;' in icon['body']
    template = tmp_path / 'page.html'
    template.write_text('<head>XX_CORE_HEAD_XX</head><body>XX_CORE_BODY_XX'
                        '</body>')

    class App(webapp.GuiApp):
        name = 'Demo'
        template_path = str(template)
        app_static_dir = str(tmp_path)
        icon_name = 'demo.ico'

    app = App()
    assert 'gui-app-icon' not in app.render_page()
    (tmp_path / 'demo.ico').write_bytes(b'ico')
    page = app.render_page()
    assert 'rel="icon" href="static/app/demo.ico' in page
    assert 'class="gui-app-icon"' in page


def test_files_roots_are_enforced(tmp_path: Path) -> None:
    """Paths outside the roots, roots themselves and links are protected."""
    root = tmp_path / 'root'
    (root / 'sub').mkdir(parents=True)
    (root / 'sub' / 'f.txt').write_text('hello')
    outside = tmp_path / 'outside.txt'
    outside.write_text('keep')
    (root / 'link').symlink_to(outside)
    roots = [str(root)]
    with pytest.raises(files.FileAccessError):
        files.check_path(str(outside), roots)
    with pytest.raises(files.FileAccessError):
        files.check_path(str(root / '..' / 'outside.txt'), roots)
    listing = files.list_directory(str(root), roots)
    assert [ent['name'] for ent in listing['entries']][0] == 'sub'
    result = files.delete_paths([str(root), str(outside),
                                 str(root / 'link')], roots)
    assert outside.exists() and root.exists()
    # the link itself is removed, never its target
    assert not (root / 'link').exists()
    assert len(result['errors']) == 2
    assert files.read_text(str(root / 'sub' / 'f.txt'), roots)['text'] == (
        'hello')


def test_write_text_keeps_backup(tmp_path: Path) -> None:
    """Writing a file keeps a time stamped backup of the old version."""
    target = tmp_path / 'a.yaml'
    target.write_text('old')
    result = files.write_text(str(target), 'new', [str(tmp_path)],
                              backup_dir=str(tmp_path / 'bak'))
    assert target.read_text() == 'new'
    assert Path(result['backup']).read_text() == 'old'


def test_batch_templates_and_script(tmp_path: Path) -> None:
    """Templates round trip and scripts contain header + activation."""
    tdir = str(tmp_path / 'tpl')
    template, path = slurm.update_template(
        tdir, 'my/../name', dict(mem='8G', account='abc',
                                 activation='conda activate x\n\n'))
    assert os.path.basename(path) == 'my____name.yaml'
    assert slurm.list_templates(tdir) == ['default', 'my____name']
    loaded = slurm.load_template(tdir, 'my____name')
    assert loaded['activation'] == ['conda activate x']
    text = slurm.build_script(loaded, 'job', ['run_me'], '/x/log.out',
                              rc_path='/x/rc')
    assert '#SBATCH --mem=8G' in text and '#SBATCH --account=abc' in text
    assert 'conda activate x\n' in text and 'run_me\n' in text
    assert "echo \"$status\" > /x/rc" in text
    assert '--partition' not in text


def test_procs_job_dir_and_remove(tmp_path: Path) -> None:
    """Removing a record deletes its logs only inside the job directory."""
    proc_dir = procs.get_proc_dir(str(tmp_path), 'reg')
    assert os.path.basename(proc_dir) == 'reg'
    job_dir = tmp_path / 'my_jobs'
    job_dir.mkdir()
    owned = job_dir / 'a.log'
    owned.write_text('x')
    proc_id = procs.register(proc_dir, 'run', 'label',
                             log_paths=[str(owned)])
    procs.finish(proc_dir, proc_id, 0)
    assert procs.proc_status(procs.load(proc_dir, proc_id), None) == (
        'complete')
    assert procs.remove(proc_dir, [proc_id], job_dir_name='my_jobs') == 1
    assert not owned.exists()


def test_markdown_render_escapes() -> None:
    """Markdown renders headings, lists, code and escapes html."""
    html = webapp.render_markdown('## T\n\n- a `<b>`\n\n```\nx < y\n```')
    assert '<h3>T</h3>' in html
    assert '<code>&lt;b&gt;</code>' in html
    assert 'x &lt; y' in html


def test_interactive_job_roundtrip(tmp_path: Path) -> None:
    """An interactive job receives browser input and is registered."""
    state = webapp.GuiState()
    proc_dir = procs.get_proc_dir(str(tmp_path))
    job_dir = str(tmp_path / 'jobs')
    os.makedirs(job_dir)
    manager = jobs.JobManager(state, lambda: proc_dir, lambda: job_dir)
    code = 'name = input("name? "); print("hello " + name)'
    started = manager.start('main', 'test', [sys.executable, '-c', code],
                            interactive=True)
    assert started['started']
    # wait for the prompt, answer it, wait for the end
    for _ in range(100):
        if manager.processes.get('main') is not None:
            break
        time.sleep(0.05)
    assert manager.send_input('main', 'world')['success']
    for _ in range(100):
        if not manager.running('main'):
            break
        time.sleep(0.05)
    job = manager.get('main')
    assert job['returncode'] == 0
    assert 'hello world' in '\n'.join(job['lines'])
    records = procs.load_all(proc_dir)
    assert len(records) == 1 and records[0]['finished']


class _App(webapp.GuiApp):
    """A minimal gui application for routing tests"""
    name = 'Test'

    def __init__(self, root: str) -> None:
        """
        Initialise with one file root

        :param root: str, the root directory

        :return: None
        """
        self.root = root
        super().__init__()

    def state_dir(self) -> str:
        """
        The state directory (inside the root)

        :return: str, the state directory
        """
        return os.path.join(self.root, 'state')

    def file_roots(self) -> list:
        """
        The file roots

        :return: list of str, the roots
        """
        return [self.root]


def test_app_routing(tmp_path: Path) -> None:
    """Core assets, built-in routes and unknown routes."""
    app = _App(str(tmp_path))
    response = app.handle(webapp.Request('GET', '/static/core/gui_core.js',
                                         None, '127.0.0.1'))
    assert response.code == 200 and b'GUI' in response.body
    response = app.handle(webapp.Request('GET', '/static/core/../x', None,
                                         '127.0.0.1'))
    assert response.code == 404
    response = app.handle(webapp.Request('GET', '/api/state', None,
                                         '127.0.0.1'))
    assert 'data_version' in json.loads(response.body)
    response = app.handle(webapp.Request('GET', '/api/fs/raw?path=/etc/hosts',
                                         None, '127.0.0.1'))
    assert response.code == 403
    response = app.handle(webapp.Request('GET', '/api/nope', None,
                                         '127.0.0.1'))
    assert response.code == 404
    body = dict(left_text='a\n', right_text='b\n')
    response = app.handle(webapp.Request('POST', '/api/diff', body,
                                         '127.0.0.1'))
    assert json.loads(response.body)['stats']['changed'] == 1


def test_mpl_stream_backend(tmp_path: Path) -> None:
    """plt.show() streams figures (png + index) and closes them."""
    import subprocess
    code = ('import matplotlib.pyplot as plt\n'
            'plt.plot([1, 2]); plt.title("one"); plt.show()\n'
            'plt.figure(); plt.show(block=True)\n'
            'plt.figure().gui_info = dict(title="T", description="D")\n'
            'plt.show()\n'
            'print(len(plt.get_fignums()))\n')
    env = dict(os.environ, MPLBACKEND='module://aperocore.gui.mpl_stream',
               APEROCORE_PLOT_STREAM_DIR=str(tmp_path))
    output = subprocess.run([sys.executable, '-c', code], env=env,
                            capture_output=True, text=True, timeout=120)
    assert output.returncode == 0, output.stderr
    assert output.stdout.strip() == '0'
    entries = [json.loads(line) for line in
               (tmp_path / 'index.jsonl').read_text().splitlines()]
    assert [entry['title'] for entry in entries] == ['one', '', 'T']
    assert entries[2]['description'] == 'D'
    assert all((tmp_path / entry['file']).exists() for entry in entries)


def test_mpl_stream_interactive_and_step(tmp_path: Path) -> None:
    """Streamed figures are pickled and tagged with the open step."""
    import subprocess
    code = ('import matplotlib.pyplot as plt\n'
            'from aperocore import progress\n'
            'progress.set_writer(lambda event, **kw: None)\n'
            'progress.set_tags(level="L", flavour="F")\n'
            'with progress.step("A"):\n'
            '    with progress.step("B"):\n'
            '        plt.plot([1, 2]); plt.show()\n')
    env = dict(os.environ, MPLBACKEND='module://aperocore.gui.mpl_stream',
               APEROCORE_PLOT_STREAM_DIR=str(tmp_path))
    output = subprocess.run([sys.executable, '-c', code], env=env,
                            capture_output=True, text=True, timeout=120)
    assert output.returncode == 0, output.stderr
    entry = json.loads((tmp_path / 'index.jsonl').read_text())
    assert entry['step'] == dict(level='L', flavour='F', path=['A', 'B'])
    assert entry['figure'].endswith('.mplfig')
    # a zero size limit keeps figures png only
    env['APEROCORE_PLOT_STREAM_MAX_MB'] = '0'
    (tmp_path / 'index.jsonl').unlink()
    output = subprocess.run([sys.executable, '-c', code], env=env,
                            capture_output=True, text=True, timeout=120)
    assert output.returncode == 0, output.stderr
    entry = json.loads((tmp_path / 'index.jsonl').read_text())
    assert 'figure' not in entry and entry['static_reason']


def test_mpl_view_session_toolbar_and_roots(tmp_path: Path) -> None:
    """A pickled figure runs matplotlib's toolbar (shared axes zoom)."""
    import pickle
    from matplotlib.figure import Figure
    from aperocore.gui import mpl_view
    figure = Figure(figsize=(4, 3))
    top = figure.add_subplot(211)
    bottom = figure.add_subplot(212, sharex=top)
    top.plot([0, 10], [0, 5])
    bottom.plot([0, 10], [5, 0])
    path = tmp_path / 'fig.mplfig'
    path.write_bytes(pickle.dumps(figure))
    data = mpl_view.open_figure(str(path), [str(tmp_path)])
    session = mpl_view.get_session(data['id'])
    # matplotlib sends the size and asks for a refresh on connect
    first = [json.loads(m)['type'] for m in session.poll(0)]
    assert 'resize' in first and 'refresh' in first
    session.handle(['{"type": "refresh"}', {'type': 'draw'},
                    {'type': 'supports_binary', 'value': False}])
    assert any(m.startswith('data:image/png;base64,')
               for m in session.poll(0))
    # a box zoom in the top axes also zooms the shared x of the bottom
    event = dict(button=0, buttons=0, modifiers=[], guiEvent={})
    session.handle([{'type': 'toolbar_button', 'name': 'zoom'},
                    dict(event, type='button_press', x=150, y=60,
                         buttons=1),
                    dict(event, type='motion_notify', x=300, y=100,
                         buttons=1),
                    dict(event, type='button_release', x=300, y=100)])
    top_lim, bottom_lim = [axis.get_xlim()
                           for axis in session.manager.canvas.figure.axes]
    assert top_lim == bottom_lim and top_lim[1] - top_lim[0] < 10
    mpl_view.close_figure(data['id'])
    with pytest.raises(mpl_view.FigureViewError):
        mpl_view.get_session(data['id'])
    # refused: no roots, outside the roots, not a figure
    other = tmp_path / 'other.txt'
    other.write_text('x')
    for bad, roots in [(str(path), []), (str(path), [str(tmp_path / 'sub')]),
                       (str(other), [str(tmp_path)])]:
        with pytest.raises(mpl_view.FigureViewError):
            mpl_view.open_figure(bad, roots)
    # the matplotlib assets
    assert 'mpl.figure' in mpl_view.javascript()
    assert mpl_view.toolbar_image('home.png')
    assert mpl_view.toolbar_image('../x.png') is None
