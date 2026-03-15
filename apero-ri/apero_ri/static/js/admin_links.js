/* global ARI_ADMIN_LINKS */
'use strict';

let _linksData = { sections: [], links: {} };
let _editTarget = null;

function _currentInstrument() {
    const sel = document.getElementById('admin-links-instr');
    return sel ? sel.value : '';
}

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('admin-links-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function _renderLinks() {
    const container = document.getElementById('admin-links-container');
    const allSections = _linksData.sections || [];
    if (allSections.length === 0) {
        container.className = 'ari-ud-empty';
        container.innerHTML = '<i class="fa-solid fa-bookmark"></i><p>No links yet. Add a section to get started.</p>';
        return;
    }
    container.className = '';
    let html = '';
    for (const section of allSections) {
        const links = (_linksData.links || {})[section] || {};
        html += `<div class="ari-links-section" data-section="${_esc(section)}">
            <div class="ari-links-section-header">
                <span class="ari-links-section-title"><i class="fa-solid fa-folder-open"></i> ${_esc(section)}</span>
                <div class="ari-links-section-actions">`;
        if (ARI_ADMIN_LINKS.canManage) {
            html += `<button class="ari-btn ari-btn--secondary ari-btn--xs js-admin-add-to-section" data-section="${_esc(section)}" title="Add link"><i class="fa-solid fa-plus"></i></button>
                     <button class="ari-btn ari-btn--danger ari-btn--xs js-admin-remove-section" data-section="${_esc(section)}" title="Delete section"><i class="fa-solid fa-trash"></i></button>`;
        }
        html += `</div></div><div class="ari-links-list">`;
        for (const [name, link] of Object.entries(links)) {
            html += `<div class="ari-link-row">
                <a class="ari-link-href" href="${_esc(link.url)}" target="_blank" rel="noopener noreferrer">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    <span class="ari-link-name">${_esc(name)}</span>
                    ${link.description ? `<span class="ari-link-desc">${_esc(link.description)}</span>` : ''}
                </a>`;
            if (ARI_ADMIN_LINKS.canManage) {
                html += `<div class="ari-link-actions">
                    <button class="ari-btn ari-btn--secondary ari-btn--xs js-admin-edit-link" data-section="${_esc(section)}" data-name="${_esc(name)}" title="Edit"><i class="fa-solid fa-pencil"></i></button>
                    <button class="ari-btn ari-btn--danger ari-btn--xs js-admin-remove-link" data-section="${_esc(section)}" data-name="${_esc(name)}" title="Remove"><i class="fa-solid fa-xmark"></i></button>
                </div>`;
            }
            html += '</div>';
        }
        if (Object.keys(links).length === 0) {
            html += '<p class="ari-links-empty-section">No links in this section yet.</p>';
        }
        html += '</div></div>';
    }
    container.innerHTML = html;
    _bindActions();
}

function _populateSectionSelect() {
    const sel = document.getElementById('admin-links-modal-section');
    if (!sel) return;
    sel.innerHTML = (_linksData.sections || []).map(s =>
        `<option value="${_esc(s)}">${_esc(s)}</option>`
    ).join('');
}

function _bindActions() {
    document.querySelectorAll('.js-admin-add-to-section').forEach(btn => {
        btn.addEventListener('click', () => {
            _editTarget = null;
            _populateSectionSelect();
            if (document.getElementById('admin-links-modal-section'))
                document.getElementById('admin-links-modal-section').value = btn.dataset.section;
            document.getElementById('admin-links-modal-name').value = '';
            document.getElementById('admin-links-modal-url').value = '';
            document.getElementById('admin-links-modal-desc').value = '';
            document.getElementById('admin-links-modal-title').textContent = 'Add Link';
            document.getElementById('admin-links-modal').style.display = 'flex';
        });
    });
    document.querySelectorAll('.js-admin-edit-link').forEach(btn => {
        btn.addEventListener('click', () => {
            const { section, name } = btn.dataset;
            const link = ((_linksData.links || {})[section] || {})[name] || {};
            _editTarget = { section, name };
            _populateSectionSelect();
            document.getElementById('admin-links-modal-section').value = section;
            document.getElementById('admin-links-modal-name').value = name;
            document.getElementById('admin-links-modal-url').value = link.url || '';
            document.getElementById('admin-links-modal-desc').value = link.description || '';
            document.getElementById('admin-links-modal-title').textContent = 'Edit Link';
            document.getElementById('admin-links-modal').style.display = 'flex';
        });
    });
    document.querySelectorAll('.js-admin-remove-link').forEach(btn => {
        btn.addEventListener('click', async () => {
            const { section, name } = btn.dataset;
            if (!confirm(`Remove link "${name}" from "${section}"?`)) return;
            const instr = _currentInstrument();
            const r = await _api(ARI_ADMIN_LINKS.removeUrl, 'POST', { instrument: instr, section, name });
            if (r.success) { _linksData = r.data; _renderLinks(); _toast('Link removed.'); }
            else _toast(r.error || 'Error', false);
        });
    });
    document.querySelectorAll('.js-admin-remove-section').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm(`Delete section "${btn.dataset.section}" and all its links?`)) return;
            const r = await _api(ARI_ADMIN_LINKS.removeSectionUrl, 'POST', {
                instrument: _currentInstrument(), section: btn.dataset.section
            });
            if (r.success) { _linksData = r.data; _renderLinks(); _toast('Section deleted.'); }
            else _toast(r.error || 'Error', false);
        });
    });
}

async function _loadLinks() {
    const instr = _currentInstrument();
    if (!instr) return;
    const r = await _api(`${ARI_ADMIN_LINKS.getUrl}?instrument=${encodeURIComponent(instr)}`);
    if (r.success) { _linksData = r.data; _renderLinks(); }
    else _toast(r.error || 'Failed to load links', false);
}

document.addEventListener('DOMContentLoaded', () => {
    _loadLinks();

    const instrSel = document.getElementById('admin-links-instr');
    if (instrSel) instrSel.addEventListener('change', _loadLinks);

    const addSectionBtn = document.getElementById('admin-links-add-section-btn');
    if (addSectionBtn) addSectionBtn.addEventListener('click', () => {
        document.getElementById('admin-links-section-name').value = '';
        document.getElementById('admin-links-section-modal').style.display = 'flex';
    });

    const addLinkBtn = document.getElementById('admin-links-add-link-btn');
    if (addLinkBtn) addLinkBtn.addEventListener('click', () => {
        if ((_linksData.sections || []).length === 0) { _toast('Create a section first.', false); return; }
        _editTarget = null;
        _populateSectionSelect();
        document.getElementById('admin-links-modal-name').value = '';
        document.getElementById('admin-links-modal-url').value = '';
        document.getElementById('admin-links-modal-desc').value = '';
        document.getElementById('admin-links-modal-title').textContent = 'Add Link';
        document.getElementById('admin-links-modal').style.display = 'flex';
    });

    const cancelBtn = document.getElementById('admin-links-modal-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', () => {
        document.getElementById('admin-links-modal').style.display = 'none';
    });

    const saveBtn = document.getElementById('admin-links-modal-save');
    if (saveBtn) saveBtn.addEventListener('click', async () => {
        const section = document.getElementById('admin-links-modal-section').value.trim();
        const name = document.getElementById('admin-links-modal-name').value.trim();
        const url = document.getElementById('admin-links-modal-url').value.trim();
        const description = document.getElementById('admin-links-modal-desc').value.trim();
        if (!section || !name || !url) { _toast('Section, name, and URL are required.', false); return; }
        const instr = _currentInstrument();
        let r;
        if (_editTarget) {
            r = await _api(ARI_ADMIN_LINKS.updateUrl, 'POST', {
                instrument: instr, section: _editTarget.section, name: _editTarget.name,
                new_name: name, url, description,
            });
        } else {
            r = await _api(ARI_ADMIN_LINKS.addUrl, 'POST', { instrument: instr, section, name, url, description });
        }
        if (r.success) {
            _linksData = r.data;
            _renderLinks();
            document.getElementById('admin-links-modal').style.display = 'none';
            _toast(_editTarget ? 'Link updated.' : 'Link added.');
        } else { _toast(r.error || 'Error', false); }
    });

    const sectionCancelBtn = document.getElementById('admin-links-section-cancel');
    if (sectionCancelBtn) sectionCancelBtn.addEventListener('click', () => {
        document.getElementById('admin-links-section-modal').style.display = 'none';
    });

    const sectionSaveBtn = document.getElementById('admin-links-section-save');
    if (sectionSaveBtn) sectionSaveBtn.addEventListener('click', async () => {
        const section = document.getElementById('admin-links-section-name').value.trim();
        if (!section) { _toast('Section name is required.', false); return; }
        const r = await _api(ARI_ADMIN_LINKS.addSectionUrl, 'POST', {
            instrument: _currentInstrument(), section
        });
        if (r.success) {
            _linksData = r.data;
            _renderLinks();
            document.getElementById('admin-links-section-modal').style.display = 'none';
            _toast('Section created.');
        } else { _toast(r.error || 'Error', false); }
    });

    ['admin-links-modal', 'admin-links-section-modal'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', e => { if (e.target.id === id) e.target.style.display = 'none'; });
    });
});
