/* global ARI_TODO */
'use strict';

let _items = [];
let _metadata = { projects: ['Unknown'], tags: ['Unknown'] };
let _filterProject = '';
let _filterTag = '';
let _collapsed = new Set();
let _editingId = null;
let _detailsId = null;
let _manageKind = 'projects';

const _STATUS_ORDER = ['in-progress', 'todo', 'blocked', 'done'];
const _STATUS_LABELS = {
    'in-progress': 'In Progress',
    'todo': 'To Do',
    'blocked': 'Blocked',
    'done': 'Done'
};
const _STATUS_ICONS = {
    'in-progress': 'fa-solid fa-rotate',
    'todo': 'fa-solid fa-list-check',
    'blocked': 'fa-solid fa-ban',
    'done': 'fa-solid fa-circle-check'
};

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('todo-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 2500);
}

function _esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function _normalizeLabels(values) {
    if (typeof values === 'string') values = [values];
    if (!Array.isArray(values)) values = [];
    const out = [];
    const seen = new Set();
    values.forEach(v => {
        const t = String(v || '').trim();
        if (!t || seen.has(t)) return;
        seen.add(t);
        out.push(t);
    });
    return out.length ? out : ['Unknown'];
}

function _itemPriority(item) {
    const n = Number(item.priority);
    return Number.isFinite(n) ? n : 0;
}

function _ensureItem(item) {
    const status = _STATUS_ORDER.includes(item.status) ? item.status : (item.done ? 'done' : 'todo');
    return {
        id: String(item.id || ''),
        title: String(item.title || 'Untitled'),
        status,
        size: ['xs', 'sm', 'md', 'lg', 'xl'].includes(String(item.size || '').toLowerCase())
            ? String(item.size || '').toLowerCase() : 'md',
        priority: _itemPriority(item),
        date_added: String(item.date_added || item.created || '').slice(0, 10),
        created: String(item.created || ''),
        projects: _normalizeLabels(item.projects),
        tags: _normalizeLabels(item.tags),
        comments: String(item.comments || ''),
        link_url: String(item.link_url || ''),
        done: status === 'done'
    };
}

function _saveCollapsed() {
    localStorage.setItem('ari_todo_collapsed', JSON.stringify(Array.from(_collapsed)));
}

function _loadCollapsed() {
    try {
        const raw = localStorage.getItem('ari_todo_collapsed');
        if (!raw) return;
        const vals = JSON.parse(raw);
        if (Array.isArray(vals)) {
            _collapsed = new Set(vals.filter(v => _STATUS_ORDER.includes(v)));
        }
    } catch (_e) {
        _collapsed = new Set();
    }
}

function _renderFilterOptions() {
    const projectSel = document.getElementById('todo-filter-project');
    const tagSel = document.getElementById('todo-filter-tag');
    if (!projectSel || !tagSel) return;

    projectSel.innerHTML = '<option value="">All Projects</option>'
        + (_metadata.projects || []).map(p => `<option value="${_esc(p)}">${_esc(p)}</option>`).join('');
    tagSel.innerHTML = '<option value="">All Tags</option>'
        + (_metadata.tags || []).map(t => `<option value="${_esc(t)}">${_esc(t)}</option>`).join('');

    projectSel.value = _filterProject;
    tagSel.value = _filterTag;
}

function _filteredItems() {
    return _items.filter(item => {
        const pOk = !_filterProject || (item.projects || []).includes(_filterProject);
        const tOk = !_filterTag || (item.tags || []).includes(_filterTag);
        return pOk && tOk;
    });
}

function _renderStats() {
    const items = _filteredItems();
    const el = document.getElementById('todo-stats');
    if (!el) return;
    el.innerHTML = [
        ['Total', items.length],
        ['Done', items.filter(i => i.status === 'done').length],
        ['In Progress', items.filter(i => i.status === 'in-progress').length],
        ['Blocked', items.filter(i => i.status === 'blocked').length]
    ].map(([label, value]) => (
        `<div class="ari-qt-stat"><div class="ari-qt-stat__value">${value}</div><div class="ari-qt-stat__label">${label}</div></div>`
    )).join('');
}

function _renderSections() {
    const container = document.getElementById('todo-sections');
    if (!container) return;

    const visible = _filteredItems();
    if (!visible.length) {
        container.innerHTML = '<p class="ari-ud-empty-inline">No tasks found.</p>';
        _renderStats();
        return;
    }

    const grouped = {};
    _STATUS_ORDER.forEach(status => {
        grouped[status] = visible
            .filter(item => item.status === status)
            .sort((a, b) => _itemPriority(b) - _itemPriority(a));
    });

    container.innerHTML = _STATUS_ORDER.map(status => {
        const list = grouped[status] || [];
        const collapsed = _collapsed.has(status);
        return `
            <section class="ari-qt-section ${collapsed ? 'is-collapsed' : ''}" data-status="${status}">
                <header class="ari-qt-section__head js-todo-section-head" data-status="${status}">
                    <div>
                        <i class="${_STATUS_ICONS[status]}"></i>
                        <strong>${_STATUS_LABELS[status]}</strong>
                    </div>
                    <span class="ari-qt-section__count">${list.length}</span>
                </header>
                <div class="ari-qt-section__body" style="display:${collapsed ? 'none' : 'block'};">
                    ${list.length ? _renderTable(list) : '<p class="ari-ud-empty-inline">No tasks in this section.</p>'}
                </div>
            </section>
        `;
    }).join('');

    container.querySelectorAll('.js-todo-section-head').forEach(btn => {
        btn.addEventListener('click', () => {
            const status = btn.getAttribute('data-status') || '';
            if (!status) return;
            if (_collapsed.has(status)) _collapsed.delete(status); else _collapsed.add(status);
            _saveCollapsed();
            _renderSections();
        });
    });

    _bindRowActions(container);
    _renderStats();
}

function _renderTable(list) {
    return `
        <div class="ari-qt-table-wrap">
            <table class="ari-qt-table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Projects</th>
                        <th>Tags</th>
                        <th>Size</th>
                        <th>Priority</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${list.map(_renderRow).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function _renderRow(item) {
    const title = item.link_url
        ? `<a href="${_esc(item.link_url)}" target="_blank" rel="noopener noreferrer">${_esc(item.title)}</a>`
        : `<a href="#" data-id="${_esc(item.id)}" class="js-open-details">${_esc(item.title)}</a>`;
    return `
        <tr data-id="${_esc(item.id)}">
            <td>${title} <button class="ari-qt-meta-btn js-open-details" data-id="${_esc(item.id)}" title="Comments / link">${item.comments ? '💬' : '✏️'}</button></td>
            <td>${_esc((item.projects || []).join(', '))}</td>
            <td>${_esc((item.tags || []).join(', '))}</td>
            <td><span class="ari-qt-size ari-qt-size--${_esc(item.size)}">${_esc(item.size.toUpperCase())}</span></td>
            <td>${_esc(String(item.priority))}</td>
            <td>${_esc(item.date_added || '')}</td>
            <td class="ari-qt-actions">
                <button class="ari-btn ari-btn--secondary ari-btn--xs js-edit" data-id="${_esc(item.id)}">Edit</button>
                <button class="ari-btn ari-btn--secondary ari-btn--xs js-duplicate" data-id="${_esc(item.id)}">Copy</button>
                <select class="ari-qt-move js-move-select" data-id="${_esc(item.id)}">
                    <option value="">Move…</option>
                    <option value="todo">To Do</option>
                    <option value="in-progress">In Progress</option>
                    <option value="blocked">Blocked</option>
                    <option value="done">Done</option>
                </select>
                <button class="ari-btn ari-btn--danger ari-btn--xs js-delete" data-id="${_esc(item.id)}">Delete</button>
            </td>
        </tr>
    `;
}

function _bindRowActions(container) {
    container.querySelectorAll('.js-edit').forEach(btn => {
        btn.addEventListener('click', () => {
            _openTaskModal(btn.dataset.id || '');
        });
    });

    container.querySelectorAll('.js-delete').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id || '';
            const item = _items.find(i => i.id === id);
            if (!item) return;
            if (!confirm(`Delete "${item.title}"?`)) return;
            const r = await _api(ARI_TODO.deleteUrl, 'POST', { id });
            if (!r.success) {
                _toast(r.error || 'Delete failed', false);
                return;
            }
            _items = _items.filter(i => i.id !== id);
            _renderSections();
        });
    });

    container.querySelectorAll('.js-move-select').forEach(sel => {
        sel.addEventListener('change', async () => {
            const id = sel.dataset.id || '';
            const status = sel.value || '';
            if (!_STATUS_ORDER.includes(status)) return;
            const item = _items.find(i => i.id === id);
            if (!item) return;
            await _saveItem({ ...item, status, done: status === 'done' });
            sel.value = '';
        });
    });

    container.querySelectorAll('.js-duplicate').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id || '';
            const item = _items.find(i => i.id === id);
            if (!item) return;
            await _saveItem({
                ...item,
                id: '',
                title: `${item.title} (copy)`,
            });
        });
    });

    container.querySelectorAll('.js-open-details').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            _openDetailsModal(btn.dataset.id || '');
        });
    });
}

function _populateMultiSelect(id, values, selected) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = values.map(v => `<option value="${_esc(v)}">${_esc(v)}</option>`).join('');
    Array.from(el.options).forEach(opt => {
        opt.selected = (selected || []).includes(opt.value);
    });
}

function _selectedValues(id) {
    const el = document.getElementById(id);
    if (!el) return ['Unknown'];
    const vals = Array.from(el.selectedOptions).map(opt => opt.value);
    return vals.length ? vals : ['Unknown'];
}

function _openTaskModal(id) {
    const item = id ? _items.find(i => i.id === id) : null;
    _editingId = item ? item.id : null;
    document.getElementById('todo-task-modal-title').textContent = item ? 'Edit Task' : 'New Task';
    document.getElementById('todo-modal-title').value = item ? item.title : (document.getElementById('todo-new-title').value.trim() || '');
    document.getElementById('todo-modal-status').value = item ? item.status : 'todo';
    document.getElementById('todo-modal-size').value = item ? item.size : 'md';
    document.getElementById('todo-modal-priority').value = item ? item.priority : 0;
    _populateMultiSelect('todo-modal-projects', _metadata.projects || ['Unknown'], item ? item.projects : ['Unknown']);
    _populateMultiSelect('todo-modal-tags', _metadata.tags || ['Unknown'], item ? item.tags : ['Unknown']);
    document.getElementById('todo-task-modal').style.display = 'flex';
}

function _closeTaskModal() {
    _editingId = null;
    document.getElementById('todo-task-modal').style.display = 'none';
}

function _openDetailsModal(id) {
    const item = _items.find(i => i.id === id);
    if (!item) return;
    _detailsId = id;
    document.getElementById('todo-details-title').textContent = `Details: ${item.title}`;
    document.getElementById('todo-details-link').value = item.link_url || '';
    document.getElementById('todo-details-comments').value = item.comments || '';
    document.getElementById('todo-details-modal').style.display = 'flex';
}

function _closeDetailsModal() {
    _detailsId = null;
    document.getElementById('todo-details-modal').style.display = 'none';
}

function _openManage(kind) {
    _manageKind = kind;
    document.getElementById('todo-manage-title').textContent = kind === 'projects' ? 'Manage Projects' : 'Manage Tags';
    document.getElementById('todo-manage-input').value = '';
    _renderManageList();
    document.getElementById('todo-manage-modal').style.display = 'flex';
}

function _closeManage() {
    document.getElementById('todo-manage-modal').style.display = 'none';
}

function _renderManageList() {
    const list = document.getElementById('todo-manage-list');
    if (!list) return;
    const values = (_manageKind === 'projects' ? _metadata.projects : _metadata.tags) || [];
    list.innerHTML = values.map(v => {
        const locked = v === 'Unknown';
        return `<div class="ari-qt-manage-item"><span>${_esc(v)}</span>${locked
            ? '<span class="ari-qt-manage-locked">Required</span>'
            : `<button class="ari-btn ari-btn--danger ari-btn--xs js-remove-meta" data-value="${_esc(v)}">Remove</button>`}</div>`;
    }).join('');
    list.querySelectorAll('.js-remove-meta').forEach(btn => {
        btn.addEventListener('click', async () => {
            const value = btn.dataset.value || '';
            if (!value) return;
            await _updateMetadata('remove', value);
        });
    });
}

async function _updateMetadata(op, value) {
    const r = await _api(ARI_TODO.reorderUrl, 'POST', {
        action: 'metadata',
        kind: _manageKind,
        op,
        value
    });
    if (!r.success) {
        _toast(r.error || 'Metadata update failed', false);
        return;
    }
    _metadata = r.metadata || _metadata;
    _renderFilterOptions();
    _renderManageList();
    _renderSections();
}

async function _saveItem(item) {
    const payload = {
        id: item.id || '',
        title: item.title || 'Untitled',
        status: item.status || 'todo',
        size: item.size || 'md',
        priority: Number(item.priority || 0),
        date_added: item.date_added || '',
        created: item.created || '',
        projects: _normalizeLabels(item.projects),
        tags: _normalizeLabels(item.tags),
        comments: item.comments || '',
        link_url: item.link_url || '',
        done: item.status === 'done'
    };
    const r = await _api(ARI_TODO.saveUrl, 'POST', payload);
    if (!r.success) {
        _toast(r.error || 'Save failed', false);
        return false;
    }
    const saved = _ensureItem(r.item || payload);
    const idx = _items.findIndex(i => i.id === saved.id);
    if (idx >= 0) _items[idx] = saved; else _items.unshift(saved);

    _metadata.projects = Array.from(new Set([...( _metadata.projects || ['Unknown']), ...(saved.projects || ['Unknown'])]));
    _metadata.tags = Array.from(new Set([...( _metadata.tags || ['Unknown']), ...(saved.tags || ['Unknown'])]));
    _renderFilterOptions();
    _renderSections();
    return true;
}

async function _loadItems() {
    const r = await _api(ARI_TODO.listUrl);
    if (r.success) {
        _items = (r.items || []).map(_ensureItem);
        _metadata = {
            projects: _normalizeLabels((r.metadata || {}).projects || ['Unknown']),
            tags: _normalizeLabels((r.metadata || {}).tags || ['Unknown'])
        };
        _renderFilterOptions();
        _renderSections();
    }
    else _toast(r.error || 'Failed to load', false);
}

async function _addItem(defaultStatus) {
    const titleEl = document.getElementById('todo-new-title');
    const title = titleEl.value.trim();
    if (!title) {
        _openTaskModal('');
        document.getElementById('todo-modal-status').value = defaultStatus || 'todo';
        return;
    }
    const ok = await _saveItem({
        id: '',
        title,
        status: defaultStatus || 'todo',
        size: 'md',
        priority: 0,
        projects: ['Unknown'],
        tags: ['Unknown'],
        comments: '',
        link_url: ''
    });
    if (ok) {
        titleEl.value = '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    _loadCollapsed();
    _loadItems();

    document.getElementById('todo-add-btn').addEventListener('click', () => _addItem('todo'));
    document.getElementById('todo-add-progress-btn').addEventListener('click', () => _addItem('in-progress'));
    document.getElementById('todo-new-title').addEventListener('keydown', e => {
        if (e.key === 'Enter') _addItem('todo');
    });

    document.getElementById('todo-filter-project').addEventListener('change', e => {
        _filterProject = e.target.value || '';
        _renderSections();
    });
    document.getElementById('todo-filter-tag').addEventListener('change', e => {
        _filterTag = e.target.value || '';
        _renderSections();
    });

    document.getElementById('todo-manage-projects-btn').addEventListener('click', () => {
        _openManage('projects');
    });
    document.getElementById('todo-manage-tags-btn').addEventListener('click', () => {
        _openManage('tags');
    });

    document.getElementById('todo-task-modal').addEventListener('click', e => {
        if (e.target.id === 'todo-task-modal') _closeTaskModal();
    });
    document.getElementById('todo-modal-cancel').addEventListener('click', _closeTaskModal);
    document.getElementById('todo-modal-save').addEventListener('click', async () => {
        const title = document.getElementById('todo-modal-title').value.trim();
        if (!title) {
            _toast('Title is required.', false);
            return;
        }
        const item = _editingId ? (_items.find(i => i.id === _editingId) || {}) : {};
        const ok = await _saveItem({
            ...item,
            id: _editingId || '',
            title,
            status: document.getElementById('todo-modal-status').value,
            size: document.getElementById('todo-modal-size').value,
            priority: Number(document.getElementById('todo-modal-priority').value || 0),
            projects: _selectedValues('todo-modal-projects'),
            tags: _selectedValues('todo-modal-tags')
        });
        if (ok) _closeTaskModal();
    });

    document.getElementById('todo-details-modal').addEventListener('click', e => {
        if (e.target.id === 'todo-details-modal') _closeDetailsModal();
    });
    document.getElementById('todo-details-cancel').addEventListener('click', _closeDetailsModal);
    document.getElementById('todo-details-save').addEventListener('click', async () => {
        if (!_detailsId) return;
        const item = _items.find(i => i.id === _detailsId);
        if (!item) return;
        const ok = await _saveItem({
            ...item,
            comments: document.getElementById('todo-details-comments').value,
            link_url: document.getElementById('todo-details-link').value.trim()
        });
        if (ok) _closeDetailsModal();
    });

    document.getElementById('todo-manage-modal').addEventListener('click', e => {
        if (e.target.id === 'todo-manage-modal') _closeManage();
    });
    document.getElementById('todo-manage-close').addEventListener('click', _closeManage);
    document.getElementById('todo-manage-add').addEventListener('click', async () => {
        const el = document.getElementById('todo-manage-input');
        const value = (el.value || '').trim();
        if (!value) return;
        await _updateMetadata('add', value);
        el.value = '';
    });
    document.getElementById('todo-manage-input').addEventListener('keydown', async e => {
        if (e.key !== 'Enter') return;
        const value = (e.target.value || '').trim();
        if (!value) return;
        await _updateMetadata('add', value);
        e.target.value = '';
    });
});
