/* global ARI_NOTES */
'use strict';

let _notes = [];
let _activeId = null;
let _previewMode = true;
let _dirty = false;

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(url, opts);
    return r.json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('notes-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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

function _renderNoteList(filter = '') {
    const listEl = document.getElementById('notes-list');
    const lf = filter.toLowerCase();
    const visible = lf
        ? _notes.filter(n =>
            (n.title || '').toLowerCase().includes(lf) ||
            (n.section || '').toLowerCase().includes(lf))
        : _notes;
    if (visible.length === 0) {
        listEl.innerHTML = '<p class="ari-ud-empty-inline">No notes found.</p>';
        return;
    }
    listEl.innerHTML = visible.map(n =>
        `<div class="ari-note-card ${n.id === _activeId ? 'ari-note-card--active' : ''}"
              data-id="${_esc(n.id)}"
              style="border-left-color:${_esc(n.color || '#ffd966')};">
            <span class="ari-note-card-title">${_esc(n.title || 'Untitled')}</span>
            ${n.section ? `<span class="ari-note-card-section">${_esc(n.section)}</span>` : ''}
         </div>`
    ).join('');
    document.querySelectorAll('.ari-note-card').forEach(card => {
        card.addEventListener('click', () => _openNote(card.dataset.id));
    });
}

async function _openNote(id) {
    if (_dirty && !confirm('You have unsaved changes. Discard?')) return;
    const r = await _api(`${ARI_NOTES.getUrl}?id=${encodeURIComponent(id)}`);
    if (!r.success) { _toast(r.error || 'Failed to load note', false); return; }
    const note = r.note;
    _activeId = id;
    _dirty = false;
    _previewMode = true;
    document.getElementById('notes-title').value = note.title || '';
    document.getElementById('notes-section').value = note.section || '';
    document.getElementById('notes-color').value = note.color || '#ffd966';
    document.getElementById('notes-content').value = note.content || '';
    document.getElementById('notes-editor').style.display = 'flex';
    await _setPreviewMode(true);
    _renderNoteList(document.getElementById('notes-search').value);
}

async function _loadNotes() {
    const r = await _api(ARI_NOTES.listUrl);
    if (r.success) {
        _notes = r.notes || [];
        _renderNoteList();
    } else {
        _toast(r.error || 'Failed to load notes', false);
    }
}

async function _saveNote() {
    const id = _activeId;
    const title = document.getElementById('notes-title').value.trim();
    const section = document.getElementById('notes-section').value.trim();
    const color = document.getElementById('notes-color').value;
    const content = document.getElementById('notes-content').value;
    const body = { id, title: title || 'Untitled', section, color, content };
    const r = await _api(ARI_NOTES.saveUrl, 'POST', body);
    if (r.success) {
        _dirty = false;
        _activeId = r.note.id;
        // Update in-list or prepend
        const idx = _notes.findIndex(n => n.id === r.note.id);
        const slim = { id: r.note.id, title: r.note.title, section: r.note.section, color: r.note.color };
        if (idx >= 0) _notes[idx] = slim; else _notes.unshift(slim);
        _renderNoteList(document.getElementById('notes-search').value);
        _toast('Note saved.');
    } else { _toast(r.error || 'Save failed', false); }
}

async function _saveAsNewNote() {
    const title = document.getElementById('notes-title').value.trim();
    const section = document.getElementById('notes-section').value.trim();
    const color = document.getElementById('notes-color').value;
    const content = document.getElementById('notes-content').value;
    const body = { id: '', title: title || 'Untitled', section, color, content };
    const r = await _api(ARI_NOTES.saveUrl, 'POST', body);
    if (r.success) {
        const slim = { id: r.note.id, title: r.note.title, section: r.note.section, color: r.note.color };
        _notes.unshift(slim);
        _activeId = r.note.id;
        _dirty = false;
        _renderNoteList(document.getElementById('notes-search').value);
        _toast('Saved as a new note.');
    } else {
        _toast(r.error || 'Save failed', false);
    }
}

async function _deleteNote() {
    if (!_activeId) return;
    if (!confirm('Delete this note?')) return;
    const r = await _api(ARI_NOTES.deleteUrl, 'POST', { id: _activeId });
    if (r.success) {
        _notes = _notes.filter(n => n.id !== _activeId);
        _activeId = null;
        _dirty = false;
        document.getElementById('notes-editor').style.display = 'none';
        _renderNoteList();
        _toast('Note deleted.');
    } else { _toast(r.error || 'Delete failed', false); }
}

async function _renderPreviewOnly() {
    const content = document.getElementById('notes-content').value;
    const r = await _api(ARI_NOTES.renderUrl, 'POST', { content });
    document.getElementById('notes-preview').innerHTML = r.success ? r.html : '<p>Render failed.</p>';
}

async function _setPreviewMode(enabled) {
    const contentEl = document.getElementById('notes-content');
    const previewEl = document.getElementById('notes-preview');
    const btn = document.getElementById('notes-preview-btn');
    _previewMode = !!enabled;
    if (_previewMode) {
        await _renderPreviewOnly();
        contentEl.style.display = 'none';
        previewEl.style.display = 'block';
        btn.innerHTML = '<i class="fa-solid fa-pencil"></i> Edit Markdown';
    } else {
        contentEl.style.display = 'block';
        previewEl.style.display = 'none';
        btn.innerHTML = '<i class="fa-solid fa-eye"></i> Rendered View';
    }
}

async function _togglePreview() {
    await _setPreviewMode(!_previewMode);
}

document.addEventListener('DOMContentLoaded', () => {
    _loadNotes();

    document.getElementById('notes-new-btn').addEventListener('click', () => {
        if (_dirty && !confirm('You have unsaved changes. Discard?')) return;
        _activeId = null;
        _dirty = false;
        _previewMode = false;
        document.getElementById('notes-title').value = '';
        document.getElementById('notes-section').value = '';
        document.getElementById('notes-color').value = '#ffd966';
        document.getElementById('notes-content').value = '';
        document.getElementById('notes-editor').style.display = 'flex';
        document.getElementById('notes-content').style.display = 'block';
        document.getElementById('notes-preview').style.display = 'none';
        document.getElementById('notes-preview-btn').innerHTML = '<i class="fa-solid fa-eye"></i> Rendered View';
        _renderNoteList(document.getElementById('notes-search').value);
        document.getElementById('notes-title').focus();
    });

    document.getElementById('notes-save-btn').addEventListener('click', _saveNote);
    document.getElementById('notes-save-new-btn').addEventListener('click', _saveAsNewNote);
    document.getElementById('notes-delete-btn').addEventListener('click', _deleteNote);
    document.getElementById('notes-preview-btn').addEventListener('click', _togglePreview);

    document.querySelectorAll('#notes-md-toolbar .js-md').forEach(btn => {
        btn.addEventListener('click', () => {
            _applyMarkdownCommand(btn.dataset.cmd || '');
        });
    });

    document.getElementById('notes-search').addEventListener('input', e => {
        _renderNoteList(e.target.value);
    });

    // Mark dirty on content/title change
    ['notes-title', 'notes-content', 'notes-section'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => { _dirty = true; });
    });

    document.getElementById('notes-content').addEventListener('input', () => {
        if (_previewMode) {
            _renderPreviewOnly();
        }
    });

    // Ctrl+S to save
    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            if (document.getElementById('notes-editor').style.display !== 'none') _saveNote();
        }
    });
});
