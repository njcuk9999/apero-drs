/* ==========================================================================
   aperocore gui - "add parameters" dialog for yaml editors

   A yaml file usually holds only some of the constants a program knows.
   GUI.addParams(opts) shows every known constant that is not in the file
   yet (name, default, description) in a filterable table with a "+"
   button per row; the application adds the chosen keys to its text
   (normally with GUI.yamlAdd, which only inserts new lines).

   opts = {
       title: str, the dialog title
       intro: str (html), shown above the table (optional)
       params: function () -> {key: {description, dtype, group, value,
               advanced}} - value is the default written, advanced marks
               constants not written by default (optional flag)
       present: function () -> {key: true}, the keys already in the file
       defaultLabel: str, the default column title (default "Default")
       section: str, the first section shown: '' (all), 'file' (the
               sections already in the file) or a section name
       add: function (keys) -> Promise (truthy when added)
   }

   GUI.yamlAdd(text, entries) posts to /api/yaml/add and resolves to
   dict(text, added, errors) (see aperocore.gui.yaml_outline.add_entries).

   The reverse: GUI.confirmRemove(opts) asks before a key is taken out of
   the file (showing the default it falls back to) and GUI.yamlRemove(text,
   keys) posts to /api/yaml/remove -> dict(text, removed, errors) (see
   aperocore.gui.yaml_outline.remove_entries).
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

// the most rows drawn at once (refine the filter to see the rest)
GUI.ADD_PARAMS_MAX = 300;
// descriptions longer than this are cut (the full text is in the docs)
GUI.ADD_PARAMS_HELP = 240;

GUI.yamlAdd = function (text, entries) {
    return GUI.post('api/yaml/add', {text: text, entries: entries});
};

GUI.yamlRemove = function (text, keys) {
    return GUI.post('api/yaml/remove', {text: text, keys: keys});
};

GUI.confirmRemove = function (opts) {
    // opts = {key, file, current: str (the value in the file), known: bool
    //   (a known constant), value: the default it falls back to,
    //   defaultLabel: str (e.g. "SPIROU default")}; resolves true/false
    var value = GUI.paramValueText(opts.value);
    var current = opts.current === undefined ? '' : String(opts.current);
    var html = '<p>Remove <code>' + GUI.esc(opts.key) + '</code> from <b>' +
        GUI.esc(opts.file || 'the file') + '</b>?</p>' + (current !== '' ?
        '<p class="small">Value in the file: <code>' + GUI.esc(current) +
        '</code></p>' : '');
    if (opts.known) {
        html += '<p>It will then use the default value: ' + (value === '' ?
            '<span class="muted">none (null)</span>' : '<code>' +
            GUI.esc(value) + '</code>') + (opts.defaultLabel ? ' <span ' +
            'class="muted small">(' + GUI.esc(opts.defaultLabel) + ')' +
            '</span>' : '') + '</p>';
        if (value === '') {
            html += '<p class="notice warn small">With no default, a ' +
                'program that needs this parameter stops until it is set ' +
                'again.</p>';
        }
    } else {
        html += '<p class="notice warn small">This is not a known ' +
            'parameter, so there is no default to fall back to.</p>';
    }
    html += '<p class="muted small">The key, its comment and any sub keys ' +
        'are removed as an unsaved change - review and save to apply it ' +
        '(Revert brings it back).</p>';
    return GUI.confirm('Remove ' + opts.key, html, 'Remove');
};

GUI.paramValueText = function (value) {
    // a default as short text ('' for none)
    if (value === null || value === undefined) { return ''; }
    return typeof value === 'string' ? value : JSON.stringify(value);
};

GUI.addParams = function (opts) {
    var state = {opts: opts};
    GUI.addParams.state = state;
    var params = opts.params();
    // the top level sections (first part of the keys)
    var sections = {};
    Object.keys(params).forEach(function (key) {
        sections[key.split('.')[0]] = true;
    });
    var names = Object.keys(sections).sort();
    var hasAdvanced = Object.keys(params).some(function (key) {
        return params[key].advanced; });
    var sectionHtml = '<select id="gui-add-section" title="Only show the ' +
        'constants of one section">' +
        '<option value="">All sections</option>' +
        '<option value="file">Sections already in the file</option>' +
        names.map(function (name) {
            return '<option value="' + GUI.esc(name) + '">' +
                GUI.esc(name) + '</option>';
        }).join('') + '</select>';
    GUI.dialog({
        id: 'gui-add-params', wide: true, title: opts.title || 'Add',
        body: '<div class="add-head"><input id="gui-add-filter" ' +
              'type="search" placeholder="Filter (name, value, ' +
              'description, group)">' + (names.length > 1 ? sectionHtml :
              '') + (hasAdvanced ? '<label class="inline small"><input ' +
              'id="gui-add-user" type="checkbox"> Usual settings only' +
              '</label>' : '') + '<label class="inline small"><input ' +
              'id="gui-add-present" type="checkbox"> Show those already ' +
              'in the file</label></div>' + (opts.intro ? '<p class="muted ' +
              'small">' + opts.intro + '</p>' : '') +
              '<div id="gui-add-list" class="add-list"></div>',
        buttons: [{grow: true, html: '<span id="gui-add-count"></span>'},
                  {label: 'Done', cls: 'primary'}]
    });
    var section = document.getElementById('gui-add-section');
    if (section) {
        section.value = opts.section || '';
        section.onchange = GUI.addParams.render;
    }
    var filter = document.getElementById('gui-add-filter');
    var timer = null;
    filter.oninput = function () {
        clearTimeout(timer);
        timer = setTimeout(GUI.addParams.render, 150);
    };
    ['gui-add-user', 'gui-add-present'].forEach(function (id) {
        var box = document.getElementById(id);
        if (box) { box.onchange = GUI.addParams.render; }
    });
    GUI.addParams.render();
    filter.focus();
};

GUI.addParams.render = function () {
    var holder = document.getElementById('gui-add-list');
    var state = GUI.addParams.state;
    if (!holder || !state) { return; }
    var opts = state.opts;
    var params = opts.params();
    var present = opts.present() || {};
    var get = function (id) { return document.getElementById(id); };
    var filter = get('gui-add-filter').value.toLowerCase().trim();
    var userOnly = get('gui-add-user') ? get('gui-add-user').checked : false;
    var showPresent = get('gui-add-present').checked;
    var section = get('gui-add-section') ? get('gui-add-section').value : '';
    // the sections already in the file
    var inFile = {};
    Object.keys(present).forEach(function (key) {
        inFile[key.split('.')[0]] = true; });
    var keys = Object.keys(params).filter(function (key) {
        var info = params[key];
        var top = key.split('.')[0];
        if (section === 'file' && !inFile[top]) { return false; }
        if (section && section !== 'file' && top !== section) {
            return false;
        }
        if (userOnly && info.advanced) { return false; }
        if (!showPresent && present[key]) { return false; }
        if (!filter) { return true; }
        var text = key + ' ' + GUI.paramValueText(info.value) + ' ' +
            (info.description || '') + ' ' + (info.group || '');
        return text.toLowerCase().indexOf(filter) >= 0;
    }).sort();
    var shown = keys.slice(0, GUI.ADD_PARAMS_MAX);
    var rows = shown.map(function (key) {
        var info = params[key];
        var isIn = !!present[key];
        var value = GUI.paramValueText(info.value);
        var desc = info.description || '';
        if (desc.length > GUI.ADD_PARAMS_HELP) {
            desc = desc.slice(0, GUI.ADD_PARAMS_HELP)
                .replace(/\s+\S*$/, '') + '...';
        }
        return '<tr' + (isIn ? ' class="in-file"' : '') + '><td>' +
            (isIn ? '<span class="pill ok" title="already in the file">' +
             'in file</span>' : '<button class="small primary" ' +
             'data-add="' + GUI.esc(key) + '" title="Add ' + GUI.esc(key) +
             '">+</button>') + '</td><td><a class="doc-link add-key" ' +
            'data-doc="' + GUI.esc(key) + '" data-param="' + GUI.esc(key) +
            '">' + GUI.esc(key) + '</a>' + (info.advanced ? ' <span ' +
            'class="muted small" title="not one of the settings written ' +
            'by default">advanced</span>' : '') + '<div class="muted ' +
            'small">' + GUI.esc(info.dtype || '') + (info.group ?
            ' &middot; ' + GUI.esc(info.group) : '') + '</div></td>' +
            '<td class="add-val">' + (value === '' ? '<span class="muted">' +
            'none</span>' : '<code>' + GUI.esc(value) + '</code>') +
            '</td><td class="add-desc">' + GUI.esc(desc) + '</td></tr>';
    }).join('');
    holder.innerHTML = keys.length ? '<table class="add-table"><thead>' +
        '<tr><th></th><th>Name</th><th>' +
        GUI.esc(opts.defaultLabel || 'Default') + '</th><th>Description' +
        '</th></tr></thead><tbody>' + rows + '</tbody></table>' :
        '<p class="muted">No parameters match.</p>';
    get('gui-add-count').textContent = keys.length > shown.length ?
        'Showing ' + shown.length + ' of ' + keys.length + ' - refine the ' +
        'filter to see the rest' : keys.length + ' parameter(s)';
    holder.querySelectorAll('[data-add]').forEach(function (btn) {
        btn.onclick = function () {
            btn.disabled = true;
            Promise.resolve(opts.add([btn.getAttribute('data-add')]))
                .then(function (ok) {
                    if (ok) { GUI.addParams.render(); }
                    else { btn.disabled = false; }
                }).catch(function (err) {
                    btn.disabled = false;
                    GUI.fail(err);
                });
        };
    });
};
