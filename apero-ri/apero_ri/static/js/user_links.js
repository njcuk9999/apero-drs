/* global ARI_LINKS */
'use strict';

let _linksData = { sections: [], links: {}, instrument_sections: [] };
let _editTarget = null;  // {section, name} when editing existing link

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(url, opts);
    return r.json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('links-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _renderLinks() {
    const container = document.getElementById('links-container');
    const allSections = _linksData.sections || [];
    const instrSections = _linksData.instrument_sections || [];
    if (allSections.length === 0 && instrSections.length === 0) {
        container.className = 'ari-ud-empty';
        container.innerHTML = '<i class="fa-solid fa-link"></i><p>No links yet. Add a section to get started.</p>';
        return;
    }
    container.className = '';
    let html = '';
    for (const section of allSections) {
        const links = (_linksData.links || {})[section] || {};
        html += `<div class="ari-links-section" data-section="${_esc(section)}">
            <div class="ari-links-section-header">
                <span class="ari-links-section-title"><i class="fa-solid fa-folder-open"></i> ${_esc(section)}</span>
                <div class="ari-links-section-actions">
                    <button class="ari-btn ari-btn--secondary ari-btn--xs js-add-to-section" data-section="${_esc(section)}" title="Add link to this section"><i class="fa-solid fa-plus"></i></button>
                    <button class="ari-btn ari-btn--danger ari-btn--xs js-remove-section" data-section="${_esc(section)}" title="Delete section"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            <div class="ari-links-list">`;
        for (const [name, link] of Object.entries(links)) {
            html += `<div class="ari-link-row">
                <a class="ari-link-href" href="${_esc(link.url)}" target="_blank" rel="noopener noreferrer">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    <span class="ari-link-name">${_esc(name)}</span>
                    ${link.description ? `<span class="ari-link-desc">${_esc(link.description)}</span>` : ''}
                </a>
                <div class="ari-link-actions">
                    <button class="ari-btn ari-btn--secondary ari-btn--xs js-edit-link" data-section="${_esc(section)}" data-name="${_esc(name)}" title="Edit link"><i class="fa-solid fa-pencil"></i></button>
                    <button class="ari-btn ari-btn--danger ari-btn--xs js-remove-link" data-section="${_esc(section)}" data-name="${_esc(name)}" title="Remove link"><i class="fa-solid fa-xmark"></i></button>
                </div>
            </div>`;
        }
        if (Object.keys(links).length === 0) {
            html += '<p class="ari-links-empty-section">No links in this section yet.</p>';
        }
        html += `</div></div>`;
    }
    // Instrument / read-only sections
    for (const section of instrSections) {
        const links = (_linksData.links || {})[section] || {};
        html += `<div class="ari-links-section ari-links-section--readonly" data-section="${_esc(section)}">
            <div class="ari-links-section-header">
                <span class="ari-links-section-title"><i class="fa-solid fa-satellite-dish"></i> ${_esc(section)} <span class="ari-links-readonly-badge">read-only</span></span>
            </div>
            <div class="ari-links-list">`;
        for (const [name, link] of Object.entries(links)) {
            html += `<div class="ari-link-row">
                <a class="ari-link-href" href="${_esc(link.url)}" target="_blank" rel="noopener noreferrer">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    <span class="ari-link-name">${_esc(name)}</span>
                    ${link.description ? `<span class="ari-link-desc">${_esc(link.description)}</span>` : ''}
                </a>
            </div>`;
        }
        if (Object.keys(links).length === 0) {
            html += '<p class="ari-links-empty-section">No links yet.</p>';
        }
        html += `</div></div>`;
    }
    container.innerHTML = html;
    _bindSectionActions();
}

function _esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function _populateSectionSelect() {
    const sel = document.getElementById('links-modal-section');
    sel.innerHTML = (_linksData.sections || []).map(s =>
        `<option value="${_esc(s)}">${_esc(s)}</option>`
    ).join('');
}

function _bindSectionActions() {
    document.querySelectorAll('.js-add-to-section').forEach(btn => {
        btn.addEventListener('click', () => {
            _editTarget = null;
            _populateSectionSelect();
            document.getElementById('links-modal-section').value = btn.dataset.section;
            document.getElementById('links-modal-name').value = '';
            document.getElementById('links-modal-url').value = '';
            document.getElementById('links-modal-desc').value = '';
            document.getElementById('links-modal-title').textContent = 'Add Link';
            document.getElementById('links-modal').style.display = 'flex';
        });
    });
    document.querySelectorAll('.js-edit-link').forEach(btn => {
        btn.addEventListener('click', () => {
            const { section, name } = btn.dataset;
            const link = ((_linksData.links || {})[section] || {})[name] || {};
            _editTarget = { section, name };
            _populateSectionSelect();
            document.getElementById('links-modal-section').value = section;
            document.getElementById('links-modal-name').value = name;
            document.getElementById('links-modal-url').value = link.url || '';
            document.getElementById('links-modal-desc').value = link.description || '';
            document.getElementById('links-modal-title').textContent = 'Edit Link';
            document.getElementById('links-modal').style.display = 'flex';
        });
    });
    document.querySelectorAll('.js-remove-link').forEach(btn => {
        btn.addEventListener('click', async () => {
            const { section, name } = btn.dataset;
            if (!confirm(`Remove link "${name}" from "${section}"?`)) return;
            const r = await _api(ARI_LINKS.removeUrl, 'POST', { section, name });
            if (r.success) { _linksData = r.data; _renderLinks(); _toast('Link removed.'); }
            else _toast(r.error || 'Error', false);
        });
    });
    document.querySelectorAll('.js-remove-section').forEach(btn => {
        btn.addEventListener('click', async () => {
            const { section } = btn.dataset;
            if (!confirm(`Delete section "${section}" and all its links?`)) return;
            const r = await _api(ARI_LINKS.removeSectionUrl, 'POST', { section });
            if (r.success) { _linksData = r.data; _renderLinks(); _toast('Section deleted.'); }
            else _toast(r.error || 'Error', false);
        });
    });
}

async function _loadLinks() {
    const instr = (document.getElementById('links-instr-select') || {}).value || '';
    const url = instr ? `${ARI_LINKS.getUrl}?instrument=${encodeURIComponent(instr)}` : ARI_LINKS.getUrl;
    const r = await _api(url);
    if (r.success) { _linksData = r.data; _renderLinks(); }
    else _toast(r.error || 'Failed to load links', false);
}

document.addEventListener('DOMContentLoaded', () => {
    _loadLinks();

    const instrSel = document.getElementById('links-instr-select');
    if (instrSel) instrSel.addEventListener('change', _loadLinks);

    document.getElementById('links-add-section-btn').addEventListener('click', () => {
        document.getElementById('links-section-name').value = '';
        document.getElementById('links-section-modal').style.display = 'flex';
    });

    document.getElementById('links-add-link-btn').addEventListener('click', () => {
        if ((_linksData.sections || []).length === 0) {
            _toast('Create a section first.', false);
            return;
        }
        _editTarget = null;
        _populateSectionSelect();
        document.getElementById('links-modal-name').value = '';
        document.getElementById('links-modal-url').value = '';
        document.getElementById('links-modal-desc').value = '';
        document.getElementById('links-modal-title').textContent = 'Add Link';
        document.getElementById('links-modal').style.display = 'flex';
    });

    document.getElementById('links-modal-cancel').addEventListener('click', () => {
        document.getElementById('links-modal').style.display = 'none';
    });

    document.getElementById('links-modal-save').addEventListener('click', async () => {
        const section = document.getElementById('links-modal-section').value.trim();
        const name = document.getElementById('links-modal-name').value.trim();
        const url = document.getElementById('links-modal-url').value.trim();
        const description = document.getElementById('links-modal-desc').value.trim();
        if (!section || !name || !url) { _toast('Section, name, and URL are required.', false); return; }
        let r;
        if (_editTarget) {
            r = await _api(ARI_LINKS.updateUrl, 'POST', {
                section: _editTarget.section, name: _editTarget.name,
                new_name: name, url, description,
            });
        } else {
            r = await _api(ARI_LINKS.addUrl, 'POST', { section, name, url, description });
        }
        if (r.success) {
            _linksData = r.data;
            _renderLinks();
            document.getElementById('links-modal').style.display = 'none';
            _toast(_editTarget ? 'Link updated.' : 'Link added.');
        } else { _toast(r.error || 'Error', false); }
    });

    document.getElementById('links-section-cancel').addEventListener('click', () => {
        document.getElementById('links-section-modal').style.display = 'none';
    });

    document.getElementById('links-section-save').addEventListener('click', async () => {
        const section = document.getElementById('links-section-name').value.trim();
        if (!section) { _toast('Section name is required.', false); return; }
        const r = await _api(ARI_LINKS.addSectionUrl, 'POST', { section });
        if (r.success) {
            _linksData = r.data;
            _renderLinks();
            document.getElementById('links-section-modal').style.display = 'none';
            _toast('Section created.');
        } else { _toast(r.error || 'Error', false); }
    });

    // Close modals on backdrop click
    ['links-modal', 'links-section-modal'].forEach(id => {
        document.getElementById(id).addEventListener('click', e => {
            if (e.target.id === id) e.target.style.display = 'none';
        });
    });
});
