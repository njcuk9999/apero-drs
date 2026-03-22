/* global ARI_NOTES */
'use strict';

// ── State ────────────────────────────────────────────────────────────────────
let _notes   = [];     // all notes (summary objects)
let _activeId = null;  // id of note currently open in view/edit pane
let _dirty   = false;  // unsaved edits in editor
let _previewTimer = null;

// ── Helpers ──────────────────────────────────────────────────────────────────
async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _esc(s) {
    return String(s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function _toast(msg, ok = true) {
    const el = document.getElementById('np-toast');
    if (!el) return;
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

// ── List rendering ────────────────────────────────────────────────────────────
function _renderList(filter) {
    const listEl = document.getElementById('np-list');
    if (!listEl) return;
    const f = String(filter || '').toLowerCase().trim();
    const visible = f
        ? _notes.filter(n =>
            String(n.title || '').toLowerCase().includes(f) ||
            String(n.content_preview || n.content || '').toLowerCase().includes(f))
        : _notes.slice();

    if (!visible.length) {
        listEl.innerHTML = `<p class="ari-np-empty">${f ? 'No matching notes.' : 'No notes yet. Click + to create one.'}</p>`;
        return;
    }

    listEl.innerHTML = visible.map(n => {
        const preview = String(n.content_preview || n.content || '').replace(/\s+/g,' ').trim().slice(0,120);
        const date    = String(n.created || '').slice(0,10);
        const active  = n.id === _activeId ? ' is-active' : '';
        return `<div class="ari-np-note-item${active}" data-id="${_esc(n.id)}">
            <div class="ari-np-note-item__title">${_esc(n.title || 'Untitled')}</div>
            <div class="ari-np-note-item__preview">${_esc(preview || 'No content')}</div>
            <div class="ari-np-note-item__date">${_esc(date)}</div>
            <button class="ari-np-note-item__del js-np-del" data-id="${_esc(n.id)}" title="Delete note">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>`;
    }).join('');

    listEl.querySelectorAll('.ari-np-note-item').forEach(el => {
        el.addEventListener('click', e => {
            if (e.target.closest('.js-np-del')) return;
            _openNoteView(el.dataset.id);
        });
        el.addEventListener('dblclick', e => {
            if (e.target.closest('.js-np-del')) return;
            _openNoteEdit(el.dataset.id);
        });
    });

    listEl.querySelectorAll('.js-np-del').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            _deleteNote(btn.dataset.id);
        });
    });
}

// ── Pane switching ────────────────────────────────────────────────────────────
function _showEmpty() {
    document.getElementById('np-empty-state').style.display = '';
    document.getElementById('np-view').style.display      = 'none';
    document.getElementById('np-editor').style.display    = 'none';
}

function _showView() {
    document.getElementById('np-empty-state').style.display = 'none';
    document.getElementById('np-view').style.display      = '';
    document.getElementById('np-editor').style.display    = 'none';
}

function _showEditor() {
    document.getElementById('np-empty-state').style.display = 'none';
    document.getElementById('np-view').style.display      = 'none';
    document.getElementById('np-editor').style.display    = '';
}

// ── View mode ─────────────────────────────────────────────────────────────────
async function _openNoteView(id) {
    if (_dirty && !confirm('Discard unsaved changes?')) return;
    _dirty = false;

    // Highlight in list
    _activeId = id;
    document.querySelectorAll('.ari-np-note-item').forEach(el =>
        el.classList.toggle('is-active', el.dataset.id === id));

    const r = await _api(`${ARI_NOTES.getUrl}?id=${encodeURIComponent(id)}`);
    if (!r.success) { _toast(r.error || 'Failed to load note', false); return; }

    const note = r.note || {};
    document.getElementById('np-view-title').textContent = note.title || 'Untitled';

    // Render markdown
    const rr = await _api(ARI_NOTES.renderUrl, 'POST', { content: note.content || '' });
    document.getElementById('np-view-body').innerHTML = rr.success ? rr.html : '<p>(empty)</p>';

    // Stash content for edit jump
    document.getElementById('np-textarea').dataset.loadedId = id;
    document.getElementById('np-textarea').value = note.content || '';
    document.getElementById('np-title-input').value = note.title || '';
    document.getElementById('np-title-input').dataset.loadedId = id;

    _showView();
}

// ── Edit mode ─────────────────────────────────────────────────────────────────
async function _openNoteEdit(id) {
    if (_dirty && id !== _activeId && !confirm('Discard unsaved changes?')) return;

    if (id !== _activeId) {
        // Need to load from server first
        const r = await _api(`${ARI_NOTES.getUrl}?id=${encodeURIComponent(id)}`);
        if (!r.success) { _toast(r.error || 'Failed to load note', false); return; }
        const note = r.note || {};
        _activeId = id;
        document.getElementById('np-textarea').value = note.content || '';
        document.getElementById('np-title-input').value = note.title || '';
        _dirty = false;
    }

    document.querySelectorAll('.ari-np-note-item').forEach(el =>
        el.classList.toggle('is-active', el.dataset.id === id));

    _showEditor();
    _refreshPreview();
    document.getElementById('np-title-input').focus();
}

function _openNoteNew() {
    if (_dirty && !confirm('Discard unsaved changes?')) return;
    _activeId = null;
    _dirty = false;
    document.getElementById('np-textarea').value = '';
    document.getElementById('np-title-input').value = '';
    document.querySelectorAll('.ari-np-note-item').forEach(el => el.classList.remove('is-active'));
    _showEditor();
    _refreshPreview();
    document.getElementById('np-title-input').focus();
}

// ── Preview debounce ──────────────────────────────────────────────────────────
async function _refreshPreview() {
    const content = document.getElementById('np-textarea').value;
    const rr = await _api(ARI_NOTES.renderUrl, 'POST', { content });
    document.getElementById('np-preview').innerHTML = rr.success ? rr.html : '';
}

function _schedulePreview() {
    clearTimeout(_previewTimer);
    _previewTimer = setTimeout(_refreshPreview, 400);
}

// ── CRUD ──────────────────────────────────────────────────────────────────────
async function _saveNote(then) {
    const title   = (document.getElementById('np-title-input').value || '').trim() || 'Untitled';
    const content = document.getElementById('np-textarea').value || '';
    const r = await _api(ARI_NOTES.saveUrl, 'POST', { id: _activeId || '', title, content });
    if (!r.success) { _toast(r.error || 'Failed to save', false); return; }

    const note = r.note || {};
    const idx = _notes.findIndex(n => n.id === note.id);
    if (idx >= 0) _notes[idx] = note; else _notes.unshift(note);
    _activeId = note.id;
    _dirty = false;
    _renderList(document.getElementById('np-search').value);
    _toast('Saved.');
    if (then === 'view')  _openNoteView(_activeId);
    if (then === 'close') { _activeId = null; _showEmpty(); document.querySelectorAll('.ari-np-note-item').forEach(el => el.classList.remove('is-active')); }
}

async function _deleteNote(id) {
    if (!id) return;
    const note = _notes.find(n => n.id === id);
    if (!confirm(`Delete "${note ? note.title : 'this note'}"?`)) return;
    const r = await _api(ARI_NOTES.deleteUrl, 'POST', { id });
    if (!r.success) { _toast(r.error || 'Failed to delete', false); return; }
    _notes = _notes.filter(n => n.id !== id);
    if (_activeId === id) { _activeId = null; _dirty = false; _showEmpty(); }
    _renderList(document.getElementById('np-search').value);
    _toast('Note deleted.');
}

// ── Markdown insert helpers ───────────────────────────────────────────────────
function _mdInsert(text) {
    const el = document.getElementById('np-textarea');
    const s = el.selectionStart, e = el.selectionEnd;
    el.value = el.value.slice(0, s) + text + el.value.slice(e);
    el.selectionStart = el.selectionEnd = s + text.length;
    _dirty = true; el.focus(); _schedulePreview();
}

function _mdWrap(before, after, placeholder) {
    const el = document.getElementById('np-textarea');
    const s = el.selectionStart, e = el.selectionEnd;
    const sel = el.value.slice(s, e) || placeholder;
    el.value = el.value.slice(0, s) + before + sel + after + el.value.slice(e);
    el.selectionStart = s + before.length;
    el.selectionEnd   = s + before.length + sel.length;
    _dirty = true; el.focus(); _schedulePreview();
}

function _applyMd(cmd) {
    switch (cmd) {
    case 'h1': _mdInsert('\n# Heading\n'); break;
    case 'h2': _mdInsert('\n## Heading\n'); break;
    case 'h3': _mdInsert('\n### Heading\n'); break;
    case 'bold':   _mdWrap('**','**','bold text'); break;
    case 'italic': _mdWrap('*','*','italic text'); break;
    case 'code':   _mdWrap('`','`','code'); break;
    case 'quote':  _mdInsert('\n> quote\n'); break;
    case 'ul':     _mdInsert('\n- item 1\n- item 2\n'); break;
    case 'ol':     _mdInsert('\n1. item 1\n2. item 2\n'); break;
    case 'task':   _mdInsert('\n- [ ] task 1\n- [ ] task 2\n'); break;
    case 'link':   _mdWrap('[','](https://example.com)','link text'); break;
    case 'hr':     _mdInsert('\n---\n'); break;
    default: break;
    }
}

// ── Load ──────────────────────────────────────────────────────────────────────
async function _loadNotes() {
    const r = await _api(ARI_NOTES.listUrl);
    if (!r.success) { _toast(r.error || 'Failed to load', false); return; }
    _notes = r.notes || [];
    _renderList();
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    _loadNotes();

    document.getElementById('np-new-btn').addEventListener('click', _openNoteNew);

    document.getElementById('np-search').addEventListener('input', e => {
        _renderList(e.target.value);
    });

    // View mode buttons
    document.getElementById('np-edit-btn').addEventListener('click', () => {
        if (_activeId) _openNoteEdit(_activeId);
    });
    document.getElementById('np-view-delete-btn').addEventListener('click', () => {
        if (_activeId) _deleteNote(_activeId);
    });

    // Editor buttons
    document.getElementById('np-save-close-btn').addEventListener('click', () => _saveNote('view'));
    document.getElementById('np-save-btn').addEventListener('click', () => _saveNote(null));
    document.getElementById('np-close-btn').addEventListener('click', () => {
        if (_dirty && !confirm('Discard unsaved changes?')) return;
        _dirty = false;
        if (_activeId) _openNoteView(_activeId);
        else { _showEmpty(); document.querySelectorAll('.ari-np-note-item').forEach(el => el.classList.remove('is-active')); }
    });
    document.getElementById('np-delete-btn').addEventListener('click', () => {
        if (_activeId) _deleteNote(_activeId);
    });

    // Textarea live preview & dirty flag
    document.getElementById('np-textarea').addEventListener('input', () => {
        _dirty = true;
        _schedulePreview();
    });
    document.getElementById('np-title-input').addEventListener('input', () => { _dirty = true; });

    // Markdown toolbar
    document.querySelectorAll('#np-md-toolbar .js-np-md').forEach(btn => {
        btn.addEventListener('click', () => _applyMd(btn.dataset.cmd || ''));
    });

    // Ctrl/Cmd+S saves
    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
            if (document.getElementById('np-editor').style.display !== 'none') {
                e.preventDefault();
                _saveNote(null);
            }
        }
    });
});


let _notes = [];
let _activeId = null;
let _previewMode = true;
let _viewMode = 'grid';
let _dirty = false;

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _esc(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function _toast(msg, ok = true) {
    const el = document.getElementById('notes-toast');
    if (!el) return;
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _notePreviewText(note) {
    return String(note.content_preview || note.content || '')
        .replace(/\s+/g, ' ')
        .trim()
        .slice(0, 180);
}

function _setViewMode(mode) {
    _viewMode = mode === 'list' ? 'list' : 'grid';
    const grid = document.getElementById('notes-grid');
    const list = document.getElementById('notes-list');
    const gridBtn = document.getElementById('notes-grid-btn');
    const listBtn = document.getElementById('notes-list-btn');
    if (!grid || !list || !gridBtn || !listBtn) return;
    if (_viewMode === 'list') {
        grid.style.display = 'none';
        list.style.display = 'block';
        gridBtn.classList.remove('ari-oln-view-btn--active');
        listBtn.classList.add('ari-oln-view-btn--active');
    } else {
        grid.style.display = 'grid';
        list.style.display = 'none';
        gridBtn.classList.add('ari-oln-view-btn--active');
        listBtn.classList.remove('ari-oln-view-btn--active');
    }
    localStorage.setItem('ari_notes_view_mode', _viewMode);
}

function _renderNotes(filter = '') {
    const grid = document.getElementById('notes-grid');
    const list = document.getElementById('notes-list');
    if (!grid || !list) return;

    const f = String(filter || '').toLowerCase().trim();
    const visible = f
        ? _notes.filter(n =>
            String(n.title || '').toLowerCase().includes(f) ||
            String(n.section || '').toLowerCase().includes(f) ||
            String(n.content_preview || n.content || '').toLowerCase().includes(f))
        : _notes.slice();

    if (!visible.length) {
        grid.innerHTML = '<p class="ari-ud-empty-inline">No notes found.</p>';
        list.innerHTML = '<p class="ari-ud-empty-inline">No notes found.</p>';
        return;
    }

    grid.innerHTML = visible.map(n => `
        <article class="ari-oln-note-card" data-id="${_esc(n.id)}" style="background:${_esc(n.color || '#fef3c7')}">
            <div class="ari-oln-note-card__actions">
                <button class="ari-btn ari-btn--secondary ari-btn--xs js-note-edit" data-id="${_esc(n.id)}">✏️</button>
                <button class="ari-btn ari-btn--danger ari-btn--xs js-note-delete" data-id="${_esc(n.id)}">🗑️</button>
            </div>
            <h4>${_esc(n.title || 'Untitled')}</h4>
            <p class="ari-oln-note-card__meta">${_esc(n.section || '')}</p>
            <p class="ari-oln-note-card__preview">${_esc(_notePreviewText(n) || 'No content')}</p>
            <p class="ari-oln-note-card__date">${_esc(n.created || '')}</p>
        </article>
    `).join('');

    list.innerHTML = visible.map(n => `
        <article class="ari-oln-note-row" data-id="${_esc(n.id)}">
            <div class="ari-oln-note-row__main">
                <h4>${_esc(n.title || 'Untitled')}</h4>
                <p>${_esc(_notePreviewText(n) || 'No content')}</p>
            </div>
            <div class="ari-oln-note-row__meta">${_esc(n.section || '')}</div>
            <div class="ari-oln-note-row__actions">
                <button class="ari-btn ari-btn--secondary ari-btn--xs js-note-edit" data-id="${_esc(n.id)}">✏️</button>
                <button class="ari-btn ari-btn--danger ari-btn--xs js-note-delete" data-id="${_esc(n.id)}">🗑️</button>
            </div>
        </article>
    `).join('');

    document.querySelectorAll('.js-note-edit').forEach(btn => {
        btn.addEventListener('click', () => _openNote(btn.dataset.id || ''));
    });
    document.querySelectorAll('.js-note-delete').forEach(btn => {
        btn.addEventListener('click', () => _deleteNote(btn.dataset.id || ''));
    });
}

function _openModal() {
    document.getElementById('notes-modal').style.display = 'flex';
}

function _closeModal(force = false) {
    if (!force && _dirty && !confirm('Discard unsaved note changes?')) return;
    document.getElementById('notes-modal').style.display = 'none';
    _activeId = null;
    _dirty = false;
    _previewMode = true;
}

async function _renderPreviewOnly() {
    const content = document.getElementById('notes-content').value;
    const r = await _api(ARI_NOTES.renderUrl, 'POST', { content });
    document.getElementById('notes-preview').innerHTML = r.success ? r.html : '<p>Render failed.</p>';
}

async function _setPreviewMode(enabled) {
    _previewMode = !!enabled;
    const content = document.getElementById('notes-content');
    const preview = document.getElementById('notes-preview');
    const btn = document.getElementById('notes-preview-btn');
    if (_previewMode) {
        await _renderPreviewOnly();
        content.style.display = 'none';
        preview.style.display = 'block';
        btn.innerHTML = '<i class="fa-solid fa-pencil"></i> Edit Markdown';
    } else {
        content.style.display = 'block';
        preview.style.display = 'none';
        btn.innerHTML = '<i class="fa-solid fa-eye"></i> Rendered View';
    }
}

function _mdInsert(text) {
    const el = document.getElementById('notes-content');
    if (!el) return;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    el.value = el.value.slice(0, start) + text + el.value.slice(end);
    el.selectionStart = el.selectionEnd = start + text.length;
    _dirty = true;
    _renderPreviewOnly();
    el.focus();
}

function _mdWrap(before, after, placeholder) {
    const el = document.getElementById('notes-content');
    if (!el) return;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const selected = el.value.slice(start, end) || placeholder;
    const inserted = `${before}${selected}${after}`;
    el.value = el.value.slice(0, start) + inserted + el.value.slice(end);
    el.selectionStart = start + before.length;
    el.selectionEnd = start + before.length + selected.length;
    _dirty = true;
    _renderPreviewOnly();
    el.focus();
}

function _applyMarkdownCommand(cmd) {
    switch (cmd) {
    case 'h1': _mdInsert('\n# Heading\n'); break;
    case 'h2': _mdInsert('\n## Heading\n'); break;
    case 'h3': _mdInsert('\n### Heading\n'); break;
    case 'bold': _mdWrap('**', '**', 'bold text'); break;
    case 'italic': _mdWrap('*', '*', 'italic text'); break;
    case 'strike': _mdWrap('~~', '~~', 'strikethrough'); break;
    case 'code': _mdWrap('`', '`', 'code'); break;
    case 'quote': _mdInsert('\n> quote\n'); break;
    case 'ul': _mdInsert('\n- item 1\n- item 2\n'); break;
    case 'ol': _mdInsert('\n1. item 1\n2. item 2\n'); break;
    case 'task': _mdInsert('\n- [ ] task 1\n- [ ] task 2\n'); break;
    case 'link': _mdWrap('[', '](https://example.com)', 'link text'); break;
    case 'image': _mdWrap('![', '](https://example.com/image.png)', 'alt text'); break;
    case 'table': _mdInsert('\n| Column | Column |\n| --- | --- |\n| Value | Value |\n'); break;
    case 'hr': _mdInsert('\n---\n'); break;
    default: break;
    }
}

async function _openNote(id) {
    if (!id) return;
    if (_dirty && !confirm('Discard unsaved note changes?')) return;
    const r = await _api(`${ARI_NOTES.getUrl}?id=${encodeURIComponent(id)}`);
    if (!r.success) {
        _toast(r.error || 'Failed to load note', false);
        return;
    }
    const note = r.note || {};
    _activeId = note.id || id;
    _dirty = false;
    document.getElementById('notes-modal-title').textContent = 'Edit Note';
    document.getElementById('notes-id').value = _activeId;
    document.getElementById('notes-title').value = note.title || '';
    document.getElementById('notes-section').value = note.section || '';
    document.getElementById('notes-color').value = note.color || '#fef3c7';
    document.getElementById('notes-content').value = note.content || '';
    _openModal();
    await _setPreviewMode(true);
}

function _newNote() {
    if (_dirty && !confirm('Discard unsaved note changes?')) return;
    _activeId = null;
    _dirty = false;
    document.getElementById('notes-modal-title').textContent = 'Add Note';
    document.getElementById('notes-id').value = '';
    document.getElementById('notes-title').value = '';
    document.getElementById('notes-section').value = '';
    document.getElementById('notes-color').value = '#fef3c7';
    document.getElementById('notes-content').value = '';
    _openModal();
    _setPreviewMode(false);
    document.getElementById('notes-title').focus();
}

async function _saveNote(saveAsNew = false) {
    const id = saveAsNew ? '' : (document.getElementById('notes-id').value || _activeId || '');
    const title = (document.getElementById('notes-title').value || '').trim() || 'Untitled';
    const section = (document.getElementById('notes-section').value || '').trim();
    const color = document.getElementById('notes-color').value || '#fef3c7';
    const content = document.getElementById('notes-content').value || '';

    const r = await _api(ARI_NOTES.saveUrl, 'POST', { id, title, section, color, content });
    if (!r.success) {
        _toast(r.error || 'Failed to save note', false);
        return;
    }

    const note = r.note || {};
    const idx = _notes.findIndex(n => n.id === note.id);
    if (idx >= 0) _notes[idx] = note;
    else _notes.unshift(note);
    _activeId = note.id;
    _dirty = false;
    _renderNotes(document.getElementById('notes-search').value || '');
    _toast(saveAsNew ? 'Saved as new note.' : 'Note saved.');
}

async function _deleteNote(idArg = '') {
    const id = idArg || _activeId;
    if (!id) return;
    if (!confirm('Delete this note?')) return;
    const r = await _api(ARI_NOTES.deleteUrl, 'POST', { id });
    if (!r.success) {
        _toast(r.error || 'Failed to delete note', false);
        return;
    }
    _notes = _notes.filter(n => n.id !== id);
    if (_activeId === id) _closeModal(true);
    _renderNotes(document.getElementById('notes-search').value || '');
    _toast('Note deleted.');
}

async function _loadNotes() {
    const r = await _api(ARI_NOTES.listUrl);
    if (!r.success) {
        _toast(r.error || 'Failed to load notes', false);
        return;
    }
    _notes = r.notes || [];
    _renderNotes();
}

document.addEventListener('DOMContentLoaded', () => {
    const storedMode = localStorage.getItem('ari_notes_view_mode');
    _setViewMode(storedMode === 'list' ? 'list' : 'grid');
    _loadNotes();

    document.getElementById('notes-grid-btn').addEventListener('click', () => _setViewMode('grid'));
    document.getElementById('notes-list-btn').addEventListener('click', () => _setViewMode('list'));

    document.getElementById('notes-new-btn').addEventListener('click', _newNote);
    document.getElementById('notes-cancel-btn').addEventListener('click', () => _closeModal(false));
    document.getElementById('notes-modal').addEventListener('click', e => {
        if (e.target.id === 'notes-modal') _closeModal(false);
    });

    document.getElementById('notes-save-btn').addEventListener('click', () => _saveNote(false));
    document.getElementById('notes-save-new-btn').addEventListener('click', () => _saveNote(true));
    document.getElementById('notes-delete-btn').addEventListener('click', () => _deleteNote());
    document.getElementById('notes-preview-btn').addEventListener('click', async () => {
        await _setPreviewMode(!_previewMode);
    });

    document.querySelectorAll('#notes-md-toolbar .js-md').forEach(btn => {
        btn.addEventListener('click', () => _applyMarkdownCommand(btn.dataset.cmd || ''));
    });

    document.getElementById('notes-search').addEventListener('input', e => {
        _renderNotes(e.target.value || '');
    });

    ['notes-title', 'notes-section', 'notes-content', 'notes-color'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            _dirty = true;
            if (_previewMode) _renderPreviewOnly();
        });
    });

    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
            if (document.getElementById('notes-modal').style.display !== 'none') {
                e.preventDefault();
                _saveNote(false);
            }
        }
    });
});
