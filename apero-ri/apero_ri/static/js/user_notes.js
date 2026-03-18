/* global ARI_NOTES */
'use strict';

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
