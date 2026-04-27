/* global ARI_LINKS */
'use strict';

let _linksData = { sections: [], links: {}, instrument_sections: [] };
let _editing = null;

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
    const el = document.getElementById('links-toast');
    if (!el) return;
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _renderSectionsManager() {
    const list = document.getElementById('sections-list');
    if (!list) return;
    const sections = _linksData.sections || [];
    list.innerHTML = sections.map(section => `
        <div class="ari-oln-manage-item">
            <span>${_esc(section)}</span>
            <button class="ari-btn ari-btn--danger ari-btn--xs js-delete-section" data-section="${_esc(section)}">Delete</button>
        </div>
    `).join('');

    list.querySelectorAll('.js-delete-section').forEach(btn => {
        btn.addEventListener('click', async () => {
            const section = btn.dataset.section || '';
            if (!section) return;
            if (!confirm(`Delete section "${section}" and all its links?`)) return;
            const r = await _api(ARI_LINKS.removeSectionUrl, 'POST', { section });
            if (!r.success) {
                _toast(r.error || 'Failed to delete section', false);
                return;
            }
            _linksData = r.data || _linksData;
            _renderLinks();
            _renderSectionsManager();
            _toast('Section deleted.');
        });
    });
}

function _renderLinks() {
    const container = document.getElementById('links-container');
    const sectionSel = document.getElementById('link-section');
    if (!container || !sectionSel) return;

    const sections = _linksData.sections || [];
    const instrSections = _linksData.instrument_sections || [];
    const hasAny = sections.length || instrSections.length;
    sectionSel.innerHTML = sections.map(s => `<option value="${_esc(s)}">${_esc(s)}</option>`).join('');

    if (!hasAny) {
        container.className = 'ari-oln-sections ari-ud-empty';
        container.innerHTML = '<i class="fa-solid fa-link"></i><p>No links yet. Add a section to get started.</p>';
        return;
    }

    container.className = 'ari-oln-sections';
    let html = '';
    for (const section of sections) {
        const links = (_linksData.links || {})[section] || {};
        html += `
        <section class="ari-oln-link-section">
            <h3>${_esc(section)}</h3>
            <div class="ari-oln-link-grid">
        `;
        for (const [name, link] of Object.entries(links)) {
            html += `
            <article class="ari-oln-link-card">
                <h4><a href="${_esc(link.url)}" target="_blank" rel="noopener noreferrer">${_esc(name)}</a></h4>
                ${link.description ? `<p>${_esc(link.description)}</p>` : '<p class="is-empty">No description</p>'}
                <div class="ari-oln-link-actions">
                    <button class="ari-btn ari-btn--secondary ari-btn--xs js-edit-link" data-section="${_esc(section)}" data-name="${_esc(name)}">Edit</button>
                    <button class="ari-btn ari-btn--danger ari-btn--xs js-delete-link" data-section="${_esc(section)}" data-name="${_esc(name)}">Delete</button>
                </div>
            </article>
            `;
        }
        if (!Object.keys(links).length) {
            html += '<p class="ari-ud-empty-inline">No links in this section yet.</p>';
        }
        html += '</div></section>';
    }

    for (const section of instrSections) {
        const links = (_linksData.links || {})[section] || {};
        html += `
        <section class="ari-oln-link-section ari-oln-link-section--readonly">
            <h3>${_esc(section)} <span class="ari-links-readonly-badge">read-only</span></h3>
            <div class="ari-oln-link-grid">
        `;
        for (const [name, link] of Object.entries(links)) {
            html += `
            <article class="ari-oln-link-card">
                <h4><a href="${_esc(link.url)}" target="_blank" rel="noopener noreferrer">${_esc(name)}</a></h4>
                ${link.description ? `<p>${_esc(link.description)}</p>` : '<p class="is-empty">No description</p>'}
            </article>
            `;
        }
        if (!Object.keys(links).length) {
            html += '<p class="ari-ud-empty-inline">No instrument links in this section.</p>';
        }
        html += '</div></section>';
    }

    container.innerHTML = html;

    container.querySelectorAll('.js-delete-link').forEach(btn => {
        btn.addEventListener('click', async () => {
            const section = btn.dataset.section || '';
            const name = btn.dataset.name || '';
            if (!section || !name) return;
            if (!confirm(`Delete link "${name}"?`)) return;
            const r = await _api(ARI_LINKS.removeUrl, 'POST', { section, name });
            if (!r.success) {
                _toast(r.error || 'Failed to delete link', false);
                return;
            }
            _linksData = r.data || _linksData;
            _renderLinks();
            _toast('Link deleted.');
        });
    });

    container.querySelectorAll('.js-edit-link').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section || '';
            const name = btn.dataset.name || '';
            const link = ((_linksData.links || {})[section] || {})[name] || {};
            _editing = { section, name };
            document.getElementById('link-section').value = section;
            document.getElementById('link-name').value = name;
            document.getElementById('link-url').value = link.url || '';
            document.getElementById('link-desc').value = link.description || '';
            document.getElementById('add-link-container').style.display = 'block';
            document.getElementById('toggle-add-link-btn').innerHTML = '<i class="fa-solid fa-minus"></i> Hide Form';
            document.getElementById('link-name').focus();
        });
    });
}

async function _loadLinks() {
    const instr = (document.getElementById('links-instr-select') || {}).value || '';
    const url = instr ? `${ARI_LINKS.getUrl}?instrument=${encodeURIComponent(instr)}` : ARI_LINKS.getUrl;
    const r = await _api(url);
    if (!r.success) {
        _toast(r.error || 'Failed to load links', false);
        return;
    }
    _linksData = r.data || _linksData;
    _renderLinks();
    _renderSectionsManager();
}

document.addEventListener('DOMContentLoaded', () => {
    _loadLinks();

    const instrSel = document.getElementById('links-instr-select');
    if (instrSel) instrSel.addEventListener('change', _loadLinks);

    document.getElementById('toggle-add-link-btn').addEventListener('click', () => {
        const panel = document.getElementById('add-link-container');
        const btn = document.getElementById('toggle-add-link-btn');
        const open = panel.style.display === 'none';
        panel.style.display = open ? 'block' : 'none';
        btn.innerHTML = open
            ? '<i class="fa-solid fa-minus"></i> Hide Form'
            : '<i class="fa-solid fa-plus"></i> Add Link';
        if (!open) {
            _editing = null;
            document.getElementById('add-link-form').reset();
        }
    });

    document.getElementById('manage-sections-btn').addEventListener('click', () => {
        _renderSectionsManager();
        document.getElementById('sections-modal').style.display = 'flex';
    });

    document.getElementById('close-sections-modal').addEventListener('click', () => {
        document.getElementById('sections-modal').style.display = 'none';
    });

    document.getElementById('sections-modal').addEventListener('click', e => {
        if (e.target.id === 'sections-modal') e.target.style.display = 'none';
    });

    document.getElementById('add-section-btn').addEventListener('click', async () => {
        const section = (document.getElementById('new-section-name').value || '').trim();
        if (!section) {
            _toast('Section name is required.', false);
            return;
        }
        const r = await _api(ARI_LINKS.addSectionUrl, 'POST', { section });
        if (!r.success) {
            _toast(r.error || 'Failed to add section', false);
            return;
        }
        document.getElementById('new-section-name').value = '';
        _linksData = r.data || _linksData;
        _renderLinks();
        _renderSectionsManager();
        _toast('Section added.');
    });

    document.getElementById('add-link-form').addEventListener('submit', async e => {
        e.preventDefault();
        const section = (document.getElementById('link-section').value || '').trim();
        const name = (document.getElementById('link-name').value || '').trim();
        const url = (document.getElementById('link-url').value || '').trim();
        const description = (document.getElementById('link-desc').value || '').trim();
        if (!section || !name || !url) {
            _toast('Section, name and URL are required.', false);
            return;
        }

        let r;
        if (_editing) {
            r = await _api(ARI_LINKS.updateUrl, 'POST', {
                section: _editing.section,
                name: _editing.name,
                new_name: name,
                url,
                description,
            });
        } else {
            r = await _api(ARI_LINKS.addUrl, 'POST', {
                section,
                name,
                url,
                description,
            });
        }
        if (!r.success) {
            _toast(r.error || 'Failed to save link', false);
            return;
        }

        _linksData = r.data || _linksData;
        _editing = null;
        document.getElementById('add-link-form').reset();
        _renderLinks();
        _toast('Link saved.');
    });
});
