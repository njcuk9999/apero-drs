/* ==========================================================================
   APERO setup gui - page logic (namespace S)

   Built on the shared aperocore gui scripts (GUI namespace), like
   pogos_gui. Sections:
     S          helpers, profile lists, tool tips / docs links
     S.setup    Setup tab (apero_setup.py form)
     S.edit     Edit tab (DRS_UCONFIG files, re-run setup)
     S.val      Validate tab (state report, apero_validate.py)
     S.docs     Docs tab (constants, guides)
   ========================================================================== */
GUI.config.storagePrefix = 'apero-setup-gui';
// probes (constants / state report) can take a while
GUI.config.timeout = 300000;
var S = {choices: null, profiles: [], extraProfiles: [], params: {},
         argHelp: {}};

/* ---- helpers ------------------------------------------------------------ */
S.$ = function (id) { return document.getElementById(id); };

S.debounce = function (fn, ms) {
    // call fn once, ms after the last call
    var timer = null;
    return function () {
        var args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () { fn.apply(null, args); }, ms);
    };
};

S.fmtBytes = function (n) {
    return (n === null || n === undefined) ? 'unknown' : GUI.fmtBytes(n);
};

S.statusPill = function (level, text) {
    // a coloured pill for ok / info / warn / bad
    var cls = {ok: 'ok', info: '', warn: 'warn', bad: 'bad'}[level] || '';
    return '<span class="pill ' + cls + '">' + GUI.esc(text || level) +
        '</span>';
};

S.refreshAll = function () {
    S.loadProfiles();
    if (S.edit.profile) { S.edit.loadProfile(S.edit.profile); }
};

/* ---- profiles (Setup "start from", Edit, Validate) ---------------------- */
S.PROFILE_SELECTS = ['setup-from', 'edit-profile', 'val-profile',
                     'data-profile'];

S.loadProfiles = function () {
    return GUI.get('api/setup/profiles').then(function (data) {
        S.profiles = data.profiles || [];
        S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
        S.val.updateCli();
    }).catch(GUI.fail);
};

S.profileOf = function (path) {
    var all = S.profiles.concat(S.extraProfiles);
    for (var it = 0; it < all.length; it++) {
        if (all[it].path === path) { return all[it]; }
    }
    return null;
};

S.fillProfileSelect = function (id) {
    var select = S.$(id);
    var current = select.value || GUI.recall('profile-' + id, '');
    var html = '<option value="">-- choose a profile (' + S.profiles.length +
        ' in ~/.apero/profiles.ini) --</option>';
    S.profiles.forEach(function (p) {
        html += '<option value="' + GUI.esc(p.path) + '"' + (p.valid ? '' :
            ' disabled') + '>' + GUI.esc(p.name) + (p.instrument ? '  [' +
            GUI.esc(p.instrument) + ']' : '') + (p.valid ? '' :
            '  (missing)') + '  ' + GUI.esc(p.path) + '</option>';
    });
    if (S.extraProfiles.length) {
        html += '<optgroup label="Other directories">';
        S.extraProfiles.forEach(function (p) {
            html += '<option value="' + GUI.esc(p.path) + '">' +
                GUI.esc(p.path) + '</option>';
        });
        html += '</optgroup>';
    }
    select.innerHTML = html;
    if (current && S.profileOf(current)) { select.value = current; }
};

S.browseProfile = function (selectId) {
    // choose any profile directory (DRS_UCONFIG) on disk
    return GUI.pickFile({title: 'Choose a profile directory (DRS_UCONFIG)',
                         any: true, dirs: true}).then(function (path) {
        if (!path) { return null; }
        path = path.replace(/\/+$/, '');
        if (!S.profileOf(path)) {
            S.extraProfiles.push({path: path, name: GUI.basename(path),
                                  valid: true});
            S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
        }
        S.$(selectId).value = path;
        GUI.store('profile-' + selectId, path);
        return path;
    });
};

/* ---- tool tips: setup arguments (data-arg) and constants (data-param) --- */
S.tipEl = null;
S.TIP_MAX = 420;

S.paramMeta = function (info) {
    // "type: int | options: 0, 1 | file: user_config.yaml" line
    if (!info) { return ''; }
    var parts = [];
    if (info.dtype) { parts.push('type: ' + info.dtype); }
    if (info.options && info.options.length) {
        parts.push('options: ' + info.options.join(', '));
    }
    if (info.minimum !== null && info.minimum !== undefined) {
        parts.push('min: ' + info.minimum); }
    if (info.maximum !== null && info.maximum !== undefined) {
        parts.push('max: ' + info.maximum); }
    if (info.unit) { parts.push('unit: ' + info.unit); }
    if (info.file) { parts.push('set in: ' + info.file); }
    return parts.join('  |  ');
};

S.showTip = function (el, ev) {
    var html = '';
    var arg = el.getAttribute('data-arg');
    var key = el.getAttribute('data-param');
    if (arg && S.choices && S.choices.args[arg]) {
        var info = S.choices.args[arg];
        html = '<span class="pt-key">' + GUI.esc(info.argname) + '</span>' +
            GUI.esc(info.help) + '<span class="pt-meta">default: ' +
            GUI.esc(String(info.default)) + (info.apero_name ? '  |  sets ' +
            GUI.esc(info.apero_name) : '') + (info.database_name ?
            '  |  database.yaml ' + GUI.esc(info.database_name) : '') +
            '</span>';
    } else if (key && (S.params[key] || S.argHelp[key])) {
        var pinfo = S.params[key];
        var text = pinfo ? pinfo.description : S.argHelp[key];
        var cut = text.length > S.TIP_MAX;
        if (cut) { text = text.slice(0, S.TIP_MAX).replace(/\s+\S*$/, '') +
                   ' ...'; }
        html = '<span class="pt-key">' + GUI.esc(key) + '</span>' +
            GUI.esc(text) + (pinfo ? '<span class="pt-meta">' +
            GUI.esc(S.paramMeta(pinfo)) + '<br>Click the name for the full ' +
            'description (Docs)</span>' : '');
    }
    if (!html) { return; }
    if (!S.tipEl) {
        S.tipEl = document.createElement('div');
        S.tipEl.className = 'param-tip';
        document.body.appendChild(S.tipEl);
    }
    S.tipEl.innerHTML = html;
    S.tipEl.style.display = 'block';
    S.moveTip(ev);
};

S.moveTip = function (ev) {
    if (!S.tipEl || S.tipEl.style.display !== 'block') { return; }
    var x = ev.clientX + 14;
    var y = ev.clientY + 16;
    var w = S.tipEl.offsetWidth;
    var h = S.tipEl.offsetHeight;
    if (x + w > window.innerWidth - 8) { x = window.innerWidth - w - 8; }
    if (y + h > window.innerHeight - 8) { y = ev.clientY - h - 12; }
    S.tipEl.style.left = Math.max(4, x) + 'px';
    S.tipEl.style.top = Math.max(4, y) + 'px';
};

S.hideTip = function () {
    if (S.tipEl) { S.tipEl.style.display = 'none'; }
};

document.addEventListener('mouseover', function (ev) {
    var el = ev.target.closest ?
        ev.target.closest('[data-arg],[data-param]') : null;
    if (el) { S.showTip(el, ev); } else { S.hideTip(); }
});
document.addEventListener('mousemove', S.moveTip);
document.addEventListener('scroll', S.hideTip, true);
document.addEventListener('click', function (ev) {
    if (!ev.target.closest) { return; }
    // constant names show their full description (Docs popup)
    var doc = ev.target.closest('[data-doc]');
    if (doc) {
        ev.preventDefault();
        S.hideTip();
        S.docs.popup(doc.getAttribute('data-doc'));
        return;
    }
    // links between docs pages open on the Docs tab
    var guide = ev.target.closest('[data-guide]');
    if (guide) {
        ev.preventDefault();
        S.docs.openGuide(guide.getAttribute('data-guide'));
    }
});

/* ==========================================================================
   Setup
   ========================================================================== */
S.setup = {dirMode: 'datadir', form: null, expected: null};

S.setup.init = function () {
    return GUI.get('api/setup/choices').then(function (data) {
        S.choices = data;
        // help of the setup values stored in the profile files (Edit tab)
        Object.keys(data.args).forEach(function (name) {
            var arg = data.args[name];
            if (arg.apero_name) { S.argHelp[arg.apero_name] = arg.help; }
            if (arg.database_name) { S.argHelp[arg.database_name] =
                                     arg.help; }
        });
        S.profiles = data.profiles || [];
        S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
        S.setup.build();
        // command line values (--gui --name=...) win over the saved form
        var saved = GUI.recall('setup-form', null);
        var initial = SETUP_INITIAL || {};
        S.setup.fill(Object.keys(initial).length ? Object.assign(
            {}, saved || {}, initial) : (saved || {}));
    }).catch(GUI.fail);
};

S.setup.arg = function (name) { return S.choices.args[name]; };

S.setup.choiceHtml = function (group, value, title, desc, arg) {
    // one radio card
    return '<label class="choice"' + (arg ? ' data-arg="' + arg + '"' : '') +
        '><input type="radio" name="' + group + '" value="' +
        GUI.esc(value) + '"><span><span class="choice-title">' +
        GUI.esc(title) + '</span>' + (desc ? '<span class="choice-desc">' +
        GUI.esc(desc) + '</span>' : '') + '</span></label>';
};

S.setup.build = function () {
    // build the choice cards and the directory / table fields
    var ch = S.choices;
    S.$('setup-language').innerHTML = ch.languages.map(function (lang) {
        return '<option>' + GUI.esc(lang) + '</option>';
    }).join('');
    S.$('setup-instruments').innerHTML = ch.instruments.map(function (inst) {
        return S.setup.choiceHtml('setup-inst', inst.name, inst.name,
                                  inst.desc);
    }).join('');
    S.$('setup-db-modes').innerHTML = ch.db_modes.map(function (mode) {
        return S.setup.choiceHtml('setup-dbmode', mode, mode,
                                  mode.indexOf('mysql') === 0 ?
                                  'MySQL / MariaDB server' : '');
    }).join('');
    S.$('setup-plot-modes').innerHTML = ch.plot_modes.map(function (mode) {
        return S.setup.choiceHtml('setup-plot', mode.value, mode.value + ': ' +
                                  mode.desc, '');
    }).join('');
    S.$('setup-ext-type').innerHTML = ch.external_types.map(function (kind) {
        return S.setup.choiceHtml('setup-exttype', kind, kind, kind ===
            'symlink' ? 'Symbolic links (works across file systems)' :
            'Hard links (same file system only)');
    }).join('');
    // one field per data directory
    S.$('setup-dirs').innerHTML = ch.dir_args.map(function (name) {
        var arg = ch.args[name];
        return '<div class="field"><label class="field-label" data-arg="' +
            name + '">' + GUI.esc(name) + ' <span class="muted">(' +
            GUI.esc(arg.apero_name || '') + ')</span></label><input ' +
            'type="text" spellcheck="false" data-field="' + name + '">' +
            '<div class="dir-preview" data-preview="' + name + '"></div>' +
            '</div>';
    }).join('');
    S.$('setup-db-tables').innerHTML = ch.table_args.map(function (name) {
        var arg = ch.args[name];
        return '<div class="field"><label class="field-label" data-arg="' +
            name + '">' + GUI.esc(name) + ' (' + GUI.esc(arg.argname) +
            ')</label><input type="text" spellcheck="false" data-field="' +
            name + '"></div>';
    }).join('');
    // every change updates the cli equivalent
    var tab = S.$('tab-setup');
    tab.addEventListener('input', S.setup.changed);
    tab.addEventListener('change', function (ev) {
        if (ev.target.type === 'radio') { S.setup.markChoices(); }
        S.setup.changed();
    });
    S.$('setup-name').addEventListener('input', S.setup.checkName);
};

S.setup.markChoices = function () {
    document.querySelectorAll('#tab-setup .choice').forEach(function (el) {
        var input = el.querySelector('input');
        el.classList.toggle('selected', !!(input && input.checked));
    });
};

S.setup.radio = function (group) {
    var input = document.querySelector('input[name="' + group +
                                       '"]:checked');
    return input ? input.value : '';
};

S.setup.setRadio = function (group, value) {
    document.querySelectorAll('input[name="' + group + '"]').forEach(
        function (input) { input.checked = String(input.value) ===
                           String(value); });
};

S.setup.setDirMode = function (mode) {
    S.setup.dirMode = mode;
    S.$('setup-dir-datadir').classList.toggle('active', mode === 'datadir');
    S.$('setup-dir-separate').classList.toggle('active', mode === 'separate');
    S.$('setup-datadir-row').style.display = mode === 'datadir' ? '' : 'none';
    // the directory fields are previews in DATADIR mode
    document.querySelectorAll('#setup-dirs input').forEach(function (input) {
        input.style.display = mode === 'separate' ? '' : 'none';
    });
    S.setup.changed();
};

S.setup.fields = function () {
    // every [data-field] input of the setup tab
    return Array.prototype.slice.call(
        S.$('tab-setup').querySelectorAll('[data-field]'));
};

S.setup.form = function () {
    // the form sent to the server (setup argument name -> value)
    var form = {dir_mode: S.setup.dirMode,
                INSTRUMENT: S.setup.radio('setup-inst'),
                DATABASE_MODE: S.setup.radio('setup-dbmode'),
                PLOT_MODE: S.setup.radio('setup-plot'),
                EXTERNAL_RAW_TYPE: S.setup.radio('setup-exttype')};
    S.setup.fields().forEach(function (el) {
        var name = el.getAttribute('data-field');
        form[name] = el.type === 'checkbox' ? el.checked : el.value.trim();
    });
    if (S.setup.passFrom) { form.pass_from_profile = S.setup.passFrom; }
    return form;
};

S.setup.fill = function (values) {
    // fill the form from values (missing ones use the setup defaults)
    var args = S.choices.args;
    var get = function (name) {
        if (values[name] !== undefined && values[name] !== null) {
            return values[name]; }
        return args[name] ? args[name].default : null;
    };
    S.setup.fields().forEach(function (el) {
        var name = el.getAttribute('data-field');
        var value = get(name);
        if (name === 'DATABASE_PASS') { value = ''; }
        if (el.type === 'checkbox') {
            el.checked = value === true || String(value).toLowerCase() ===
                'true';
        } else if (el.tagName === 'SELECT') {
            el.value = value === null ? S.choices.default_language : value;
        } else {
            el.value = (value === null || value === 'None') ? '' :
                String(value);
        }
    });
    S.setup.setRadio('setup-inst', get('INSTRUMENT') || '');
    S.setup.setRadio('setup-dbmode', get('DATABASE_MODE') ||
                     S.choices.db_modes[0]);
    S.setup.setRadio('setup-plot', get('PLOT_MODE'));
    S.setup.setRadio('setup-exttype', get('EXTERNAL_RAW_TYPE') || 'symlink');
    S.setup.passFrom = values.pass_from_profile || null;
    S.$('setup-db-pass').placeholder = S.setup.passFrom ?
        (values.has_password ? '(unchanged - from ' +
         GUI.basename(S.setup.passFrom) + ')' : '(not set in profile)') : '';
    S.setup.markChoices();
    S.setup.setDirMode(values.dir_mode || (values.RAWDIR && !values.DATADIR ?
                                           'separate' : 'datadir'));
    S.setup.checkName();
};

S.setup.reset = function () {
    S.setup.fill({});
    GUI.store('setup-form', null);
};

S.setup.loadFrom = function () {
    var path = S.$('setup-from').value;
    if (!path) { GUI.toast('Choose a profile first', 'bad'); return; }
    GUI.post('api/setup/profile_form', {profile: path}).then(function (res) {
        S.setup.fill(res.form);
        GUI.toast('Filled in from ' + GUI.basename(path) + ' - change the ' +
                  'name to create a new profile', 'ok');
    }).catch(GUI.fail);
};

S.setup.browse = function (id) {
    GUI.pickFile({title: 'Choose a directory', any: true, dirs: true,
                  start: S.$(id).value || ''}).then(function (path) {
        if (path) { S.$(id).value = path; S.setup.changed(); }
    });
};

S.setup.checkName = function () {
    // restricted characters (as apero_setup checks them)
    var name = S.$('setup-name').value.trim();
    var arg = S.setup.arg('name');
    var bad = (arg.restricted || []).filter(function (ch) {
        return name.indexOf(ch) >= 0; }).map(function (ch) {
            return ch === ' ' ? 'space' : ch; });
    S.$('setup-name').classList.toggle('bad', bad.length > 0);
    S.$('setup-name-help').innerHTML = bad.length ?
        '<span style="color:var(--danger)">Not allowed: ' +
        GUI.esc(bad.join(' ')) + '</span>' :
        'No spaces or punctuation (except _).';
};

S.setup.updateHints = function (form) {
    // section visibility and the path / table name previews
    var datadir = form.DATADIR;
    S.choices.dir_args.forEach(function (name) {
        var preview = document.querySelector('[data-preview="' + name + '"]');
        var sets = S.choices.args.DATADIR.sets;
        preview.textContent = S.setup.dirMode === 'datadir' ? (datadir ?
            sets[name].replace('{DATADIR}', datadir.replace(/\/$/, '')) :
            sets[name]) : '';
    });
    S.$('setup-ext-row').style.display = form.USE_EXTERNAL_RAW ? '' : 'none';
    S.$('setup-db-tables').style.display = form.EDIT_DBTABLES ? '' : 'none';
    var sets = S.choices.args.EDIT_DBTABLES.sets;
    S.$('setup-db-tables-help').textContent = form.EDIT_DBTABLES ? '' :
        'Tables: ' + Object.keys(sets).map(function (key) {
            return sets[key].replace('{NAME}', form.name || '{name}');
        }).join(', ');
    S.$('setup-clean-note').style.display = form.CLEAN_START ? '' : 'none';
    var config = (form.config_path || '{config}').replace(/\/$/, '');
    S.$('setup-config-help').innerHTML = 'The profile files are written to ' +
        '<code>' + GUI.esc(config + '/' + (form.name || '{name}')) +
        '</code> (this becomes <code>DRS_UCONFIG</code>).';
    // the cards of the sections that are complete
    var done = {1: form.name && form.config_path, 2: !!form.INSTRUMENT,
                3: S.setup.dirMode === 'datadir' ? !!form.DATADIR :
                    S.choices.dir_args.every(function (n) { return form[n]; }),
                4: !form.USE_EXTERNAL_RAW || !!form.EXTERNAL_RAW,
                5: !!form.DATABASE_MODE && !!form.DATABASE_HOST, 6: true};
    Object.keys(done).forEach(function (num) {
        S.$('setup-sec-' + num).classList.toggle('done', !!done[num]);
    });
};

S.setup.validate = function (form) {
    return GUI.post('api/setup/preview', {action: 'setup', form: form});
};

S.setup.changed = S.debounce(function () {
    if (!S.choices) { return; }
    var form = S.setup.form();
    S.setup.updateHints(form);
    // remember the form (never the password)
    var saved = Object.assign({}, form);
    delete saved.DATABASE_PASS;
    GUI.store('setup-form', saved);
    S.setup.validate(form).then(function (res) {
        GUI.setCli('cli-setup', res.display || '');
        S.$('setup-cli-note').textContent = res.errors.length ?
            '(incomplete - ' + res.errors.length + ' item(s) to fix)' : '';
        var exists = S.$('setup-exists');
        exists.style.display = res.exists ? '' : 'none';
        exists.innerHTML = res.exists ? 'The profile <code>' +
            GUI.esc(res.profile) + '</code> already exists - its files are ' +
            'written again.' : '';
    }).catch(function () { return null; });
}, 250);

S.setup.run = function () {
    // validate everything; problems are listed in a popup, otherwise
    //   apero_setup.py runs
    var form = S.setup.form();
    S.$('btn-setup').disabled = true;
    S.setup.validate(form).then(function (res) {
        S.$('btn-setup').disabled = false;
        if (res.errors.length) {
            GUI.dialog({id: 'setup-invalid', narrow: true,
                        title: 'Setup is not complete',
                        body: '<p>Please fix the following before saving:' +
                              '</p><ul class="setup-errors">' +
                              res.errors.map(function (err) {
                                  return '<li>' + GUI.esc(err) + '</li>';
                              }).join('') + '</ul>',
                        buttons: [{label: 'OK', cls: 'primary'}]});
            return;
        }
        var start = function () {
            S.setup.expected = res.profile;
            S.$('setup-after').style.display = 'none';
            GUI.startJob('api/setup/run', {form: form}, GUI.consoles.setup);
        };
        // a clean start without the reset prompt needs a typed RESET
        if (form.CLEAN_START && !form.CLEAN_PROMPT) {
            GUI.confirmTyped({title: 'Clean start', word: 'RESET',
                              html: '<p>Setup will run <code>apero_reset' +
                              '</code> without asking: every reduced file ' +
                              'and database entry of <code>' +
                              GUI.esc(res.profile) + '</code> is removed.' +
                              '</p>'}).then(function (ok) {
                if (ok) { start(); } });
            return;
        }
        start();
    }).catch(function (err) {
        S.$('btn-setup').disabled = false;
        GUI.fail(err);
    });
};

S.setup.done = function (job) {
    // apero_setup finished: offer the next steps
    S.loadProfiles();
    var box = S.$('setup-after');
    var path = S.setup.expected;
    if (job.returncode !== 0 || !path) { return; }
    box.style.display = '';
    box.innerHTML = 'Setup finished: <code>' + GUI.esc(path) + '</code>. ' +
        'Activate it with <code>source ' + GUI.esc(path) + '/setup.sh</code>' +
        ' (or <code>apero_profile.sh ' + GUI.esc(GUI.basename(path)) +
        '</code>). <button class="small" id="setup-open-edit">Review in Edit' +
        '</button> <button class="small primary" id="setup-open-val">' +
        'Validate</button>';
    S.$('setup-open-edit').onclick = function () { S.edit.open(path); };
    S.$('setup-open-val').onclick = function () { S.val.open(path); };
};

/* ==========================================================================
   Edit
   ========================================================================== */
S.edit = {profile: null, name: null, info: null, original: '', text: '',
          mtime: null, outline: null, edits: {}, view: 'form', open: {},
          editable: true, changed: null};

S.edit.init = function () {
    S.$('edit-filter').oninput = S.debounce(function () {
        S.edit.renderForm(); }, 200);
    var raw = S.$('edit-raw');
    raw.addEventListener('input', function () {
        S.edit.text = raw.value;
        S.edit.updateGutter();
        S.edit.updateDirty();
    });
    raw.addEventListener('scroll', function () {
        S.$('edit-gutter').scrollTop = raw.scrollTop;
    });
    document.addEventListener('keydown', function (ev) {
        if ((ev.ctrlKey || ev.metaKey) && ev.key === 's' &&
            GUI.currentTab === 'edit' && S.edit.name) {
            ev.preventDefault();
            S.edit.save();
        }
    });
    window.addEventListener('beforeunload', function (ev) {
        if (S.edit.dirty()) { ev.preventDefault(); ev.returnValue = ''; }
    });
    GUI.onTab('edit', function () {
        var path = S.$('edit-profile').value;
        if (!S.edit.profile && path) { S.edit.loadProfile(path); }
    });
};

S.edit.dirty = function () {
    return !!S.edit.name && (Object.keys(S.edit.edits).length > 0 ||
                             S.edit.text !== S.edit.original);
};

S.edit.confirmDiscard = function () {
    if (!S.edit.dirty()) { return Promise.resolve(true); }
    return GUI.confirm('Unsaved changes', 'Discard the unsaved changes to ' +
                       '<code>' + GUI.esc(S.edit.name) + '</code>?',
                       'Discard');
};

S.edit.selectProfile = function () {
    var path = S.$('edit-profile').value;
    GUI.store('profile-edit-profile', path);
    S.edit.confirmDiscard().then(function (ok) {
        if (ok) { S.edit.loadProfile(path); }
        else { S.$('edit-profile').value = S.edit.profile || ''; }
    });
};

S.edit.browseProfile = function () {
    S.browseProfile('edit-profile').then(function (path) {
        if (path) { S.edit.selectProfile(); }
    });
};

S.edit.openSecs = {};
// the parameters added since the file was loaded (highlighted)
S.edit.added = {};

S.edit.open = function (path) {
    // open a profile from another tab
    if (!S.profileOf(path)) {
        S.extraProfiles.push({path: path, name: GUI.basename(path),
                              valid: true});
        S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
    }
    S.$('edit-profile').value = path;
    GUI.setTab('edit');
    S.edit.loadProfile(path);
};

S.edit.reload = function () {
    if (!S.edit.profile) { return; }
    S.edit.confirmDiscard().then(function (ok) {
        if (ok) { S.edit.loadProfile(S.edit.profile, S.edit.name); }
    });
};

S.edit.loadProfile = function (path, name) {
    // the profile summary, its file chips and the cli equivalents
    if (!path) { return; }
    S.edit.profile = path;
    S.edit.changed = null;
    S.$('edit-changes').disabled = true;
    var info = S.profileOf(path) || {path: path, name: GUI.basename(path)};
    S.$('edit-summary').innerHTML = '<span class="path">' + GUI.esc(path) +
        '</span>' + (info.instrument ? ' <span class="pill run">' +
        GUI.esc(info.instrument) + '</span>' : '') + (info.mtime ?
        ' <span class="muted">installed ' + GUI.fmtAge(info.mtime) +
        '</span>' : '');
    var names = Object.keys({'install.yaml': 1, 'database.yaml': 1,
                             'user_config.yaml': 1, 'user_constants.yaml': 1,
                             'user_keywords.yaml': 1, 'setup.sh': 1,
                             'setup.bat': 1, 'install_script.sh': 1});
    S.$('edit-files').innerHTML = names.map(function (fname) {
        var has = !info.files || info.files.indexOf(fname) >= 0;
        return '<button class="chip file-chip' + (has ? '' : ' missing') +
            '" data-file="' + fname + '">' + GUI.esc(fname) + '</button>';
    }).join('');
    S.$('edit-files').querySelectorAll('[data-file]').forEach(function (b) {
        b.onclick = function () {
            var fname = b.getAttribute('data-file');
            S.edit.confirmDiscard().then(function (ok) {
                if (ok) { S.edit.load(fname); } });
        };
    });
    GUI.post('api/setup/preview', {action: 'update', profile: path})
        .then(function (res) {
            GUI.setCli('cli-update', res.display || res.errors.join('\n'));
        });
    S.edit.load(name || GUI.recall('edit-file', 'user_config.yaml'));
};

S.edit.load = function (name) {
    var profile = S.edit.profile;
    return GUI.get('api/setup/file', {profile: profile, name: name})
        .then(function (data) {
            S.edit.name = name;
            S.edit.path = data.path;
            S.edit.original = data.text;
            S.edit.text = data.text;
            S.edit.mtime = data.mtime;
            S.edit.edits = {};
            S.edit.added = {};
            S.edit.inst = data.instrument ?
                String(data.instrument).toUpperCase() : null;
            S.edit.editable = data.editable && data.exists;
            GUI.store('edit-file', name);
            S.$('edit-files').querySelectorAll('[data-file]').forEach(
                function (b) { b.classList.toggle(
                    'active', b.getAttribute('data-file') === name); });
            S.$('edit-card').style.display = '';
            S.$('edit-save').disabled = !S.edit.editable;
            S.$('edit-add').style.display = S.edit.addKind() ? '' : 'none';
            S.$('edit-add').disabled = !S.edit.editable;
            var note = S.$('edit-note');
            note.style.display = S.edit.editable ? 'none' : '';
            note.textContent = !data.exists ? name + ' does not exist in ' +
                'this profile (re-run setup to create it).' :
                name + ' is written by apero_setup (read only here - ' +
                're-run setup to regenerate it).';
            S.$('edit-raw').value = data.text;
            S.$('edit-raw').readOnly = !S.edit.editable;
            S.edit.updateGutter();
            // shell / batch files have no parameter form
            var isYaml = /\.ya?ml$/.test(name);
            S.$('edit-view-form').disabled = !isYaml;
            if (!isYaml && S.edit.view !== 'raw') {
                S.edit.view = 'form';
                return S.edit.setView('raw');
            }
            return S.edit.refreshOutline();
        }).catch(GUI.fail);
};

S.edit.refreshOutline = function () {
    return GUI.post('api/yaml/outline', {text: S.edit.text})
        .then(function (outline) {
            S.edit.outline = outline;
            var err = S.$('edit-error');
            err.style.display = outline.error ? '' : 'none';
            err.textContent = outline.error ? 'YAML error: ' + outline.error :
                '';
            S.edit.renderForm();
            S.edit.updateDirty();
        });
};

S.edit.currentText = function () {
    // the text with the pending form edits applied (promise)
    var edits = Object.keys(S.edit.edits).map(function (line) {
        return S.edit.edits[line];
    });
    if (S.edit.view === 'raw' || edits.length === 0) {
        return Promise.resolve(S.edit.text);
    }
    return GUI.post('api/yaml/apply', {text: S.edit.text, edits: edits})
        .then(function (res) {
            if (res.errors.length) { GUI.toast(res.errors.join('\n'), 'bad'); }
            return res.text;
        });
};

S.edit.setView = function (view) {
    if (view === S.edit.view) { return Promise.resolve(); }
    var done;
    if (view === 'raw') {
        done = S.edit.currentText().then(function (text) {
            S.edit.text = text;
            S.edit.edits = {};
            S.$('edit-raw').value = text;
            S.edit.updateGutter();
        });
    } else {
        S.edit.text = S.$('edit-raw').value;
        done = S.edit.refreshOutline();
    }
    return done.then(function () {
        S.edit.view = view;
        S.$('edit-view-form').classList.toggle('active', view === 'form');
        S.$('edit-view-raw').classList.toggle('active', view === 'raw');
        S.$('edit-form').style.display = view === 'form' ? '' : 'none';
        S.$('edit-raw-wrap').style.display = view === 'raw' ? '' : 'none';
        S.$('edit-filter').style.display = view === 'form' ? '' : 'none';
        S.edit.updateDirty();
    });
};

S.edit.updateGutter = function () {
    var count = S.$('edit-raw').value.split('\n').length;
    var nums = [];
    for (var it = 1; it <= count; it++) { nums.push(it); }
    S.$('edit-gutter').textContent = nums.join('\n');
};

S.edit.updateDirty = function () {
    var pill = S.$('edit-dirty');
    var nedits = Object.keys(S.edit.edits).length;
    var dirty = S.edit.dirty();
    pill.className = 'pill' + (dirty ? ' warn' : ' ok');
    pill.textContent = dirty ? (nedits ? nedits + ' unsaved change(s)' :
                                'unsaved changes') : 'saved';
};

S.edit.nodeValue = function (node) {
    var edit = S.edit.edits[node.line];
    if (edit) { return edit.items ? edit.items.join('\n') : edit.value; }
    return node.kind === 'list' ? node.items.join('\n') : node.value;
};

S.edit.inputHtml = function (node, key) {
    // the editor widget of one node
    var value = S.edit.nodeValue(node);
    var attrs = ' data-line="' + node.line + '"' + (S.edit.editable ? '' :
                                                   ' disabled');
    if (node.kind === 'list') {
        return '<textarea' + attrs + ' rows="' +
            Math.min(8, Math.max(2, node.items.length + 1)) + '" ' +
            'placeholder="one item per line">' + GUI.esc(value) +
            '</textarea>';
    }
    if (node.kind !== 'scalar') {
        return '<div class="yf-readonly">(' + GUI.esc(node.kind) + ' - edit ' +
            'in Raw text)</div>';
    }
    // the database password is never shown in the form
    if (/PASSWD$/.test(key)) {
        return '<input type="password" autocomplete="off"' + attrs +
            ' value="' + GUI.esc(value) + '">';
    }
    if (node.vtype === 'bool' || /^(true|false)$/i.test(value)) {
        var lower = String(value).toLowerCase();
        return '<select' + attrs + '><option' + (lower === 'true' ?
            ' selected' : '') + '>true</option><option' + (lower === 'false' ?
            ' selected' : '') + '>false</option></select>';
    }
    var info = S.params[key];
    if (info && info.options && info.options.length) {
        var opts = info.options.slice();
        var clean = String(value).replace(/^['"]|['"]$/g, '');
        if (opts.indexOf(clean) < 0) { opts.unshift(clean); }
        return '<select' + attrs + '>' + opts.map(function (opt) {
            return '<option' + (opt === clean ? ' selected' : '') + '>' +
                GUI.esc(opt) + '</option>';
        }).join('') + '</select>';
    }
    return '<input type="text"' + attrs + ' value="' + GUI.esc(value) +
        '" spellcheck="false" placeholder="(empty)">';
};

S.HELP_MAX = 240;

S.edit.rowHtml = function (node) {
    // one row: key (click for Docs), widget, help, type / instrument line
    var key = node.path.join('.');
    var info = S.params[key];
    var help = info ? info.description : (S.argHelp[key] || node.comment ||
                                          '');
    var more = help.length > S.HELP_MAX;
    var shown = more ? help.slice(0, S.HELP_MAX).replace(/\s+\S*$/, '') +
        '...' : help;
    var inst = S.edit.instrument();
    var defValue = info && info.values && inst ? info.values[inst] :
        undefined;
    var changed = !!S.edit.edits[node.line] || !!S.edit.added[key];
    return '<div class="yf-row' + (changed ? ' changed' : '') +
        '" data-row="' + node.line + '"><div class="yf-key" data-param="' +
        GUI.esc(key) + '"' + (info ? ' data-doc="' + GUI.esc(key) + '"' : '') +
        '>' + GUI.esc(node.key) + S.edit.removeHtml(key) +
        '<span class="yf-path">' +
        GUI.esc(node.path.slice(0, -1).join('.')) + ' &middot; line ' +
        (node.line + 1) + '</span></div><div class="yf-value">' +
        S.edit.inputHtml(node, key) + (shown ? '<div class="yf-help">' +
        GUI.esc(shown) + (info && more ? ' <a class="doc-link" data-doc="' +
        GUI.esc(key) + '">more in Docs</a>' : '') + '</div>' : '') +
        (info ? '<div class="yf-meta">' + GUI.esc(S.paramMeta(info)) +
         (defValue !== undefined ? '  |  ' + inst + ' default: ' +
          GUI.esc(JSON.stringify(defValue)) : '') + '</div>' : '') +
        '</div></div>';
};

S.edit.removeHtml = function (key) {
    // the "remove" button of a known parameter of a user yaml
    if (!S.edit.editable || !S.edit.addKind() || !S.params[key]) {
        return '';
    }
    return '<button type="button" class="yf-remove" data-remove="' +
        GUI.esc(key) + '" title="Remove ' + GUI.esc(key) + ' from the ' +
        'file (use the default value)">&#10005;</button>';
};

S.edit.isChanged = function (node) {
    // edited in the form, or added since the file was loaded
    return !!S.edit.edits[node.line] || !!S.edit.added[node.path.join('.')];
};

S.edit.instrument = function () {
    // from the open file (install.yaml) or the profile list
    if (S.edit.inst) { return S.edit.inst; }
    var info = S.profileOf(S.edit.profile);
    return info && info.instrument ? String(info.instrument).toUpperCase() :
        null;
};

S.edit.renderForm = function () {
    var outline = S.edit.outline;
    var holder = S.$('edit-form');
    if (!outline) { holder.innerHTML = ''; return; }
    var filter = S.$('edit-filter').value.toLowerCase();
    var changedOnly = S.$('edit-changed-only').checked;
    // group the nodes by their top level key
    var sections = [];
    var current = null;
    outline.nodes.forEach(function (node) {
        if (node.depth === 0) {
            current = {node: node, rows: []};
            sections.push(current);
            if (node.kind === 'map') { return; }
        }
        if (current) { current.rows.push(node); }
    });
    var matches = function (node, key) {
        var info = S.params[key];
        var help = info ? info.description : (S.argHelp[key] || '');
        return !filter || (key + ' ' + S.edit.nodeValue(node) + ' ' + help)
            .toLowerCase().indexOf(filter) >= 0;
    };
    var html = '';
    sections.forEach(function (sec) {
        var rows = '';
        var shown = 0;
        sec.rows.forEach(function (node) {
            var key = node.path.join('.');
            if (node.kind === 'map') {
                // a sub section heading (e.g. OBJ.LBL)
                if (!filter && !changedOnly) {
                    rows += '<div class="yf-group" data-param="' +
                        GUI.esc(key) + '">' + GUI.esc(key) +
                        (node.section ? ' <span class="yf-group-desc">- ' +
                         GUI.esc(node.section) + '</span>' : '') + '</div>';
                }
                return;
            }
            if (changedOnly && !S.edit.isChanged(node)) { return; }
            if (!matches(node, key)) { return; }
            shown++;
            rows += S.edit.rowHtml(node);
        });
        var single = sec.node.kind !== 'map';
        if (single) {
            if ((changedOnly && !S.edit.isChanged(sec.node)) ||
                !matches(sec.node, sec.node.path.join('.'))) { return; }
            rows = S.edit.rowHtml(sec.node);
            shown = 1;
        }
        if ((filter || changedOnly) && shown === 0) { return; }
        var name = sec.node.key;
        var saved = S.edit.openSecs[name];
        var isOpen = saved !== undefined ? saved :
            (single || !!filter || changedOnly || sections.length <= 3);
        html += '<details class="yf-section" data-sec="' + GUI.esc(name) +
            '"' + (isOpen ? ' open' : '') + '><summary data-param="' +
            GUI.esc(name) + '">' + GUI.esc(name) + ' <span ' +
            'class="yf-count">' + (sec.node.section ? GUI.esc(
                sec.node.section) + ' &middot; ' : '') + shown +
            ' parameter(s)</span></summary>' + rows + '</details>';
    });
    holder.innerHTML = html || '<p class="muted">No parameters' +
        (filter || changedOnly ? ' match' : ' in this file') + '.</p>';
    holder.querySelectorAll('details').forEach(function (det) {
        det.addEventListener('toggle', function () {
            S.edit.openSecs[det.getAttribute('data-sec')] = det.open;
        });
    });
    holder.querySelectorAll('[data-remove]').forEach(function (btn) {
        btn.onclick = function (ev) {
            // (not the Docs link of the key around it)
            ev.preventDefault();
            ev.stopPropagation();
            S.edit.removeParam(btn.getAttribute('data-remove'));
        };
    });
    holder.querySelectorAll('[data-line]').forEach(function (input) {
        var handler = function () { S.edit.fieldChanged(input); };
        input.addEventListener('input', handler);
        input.addEventListener('change', handler);
    });
};

S.edit.fieldChanged = function (input) {
    var line = Number(input.getAttribute('data-line'));
    var node = S.edit.outline.nodes.filter(function (n) {
        return n.line === line; })[0];
    if (!node) { return; }
    var original = node.kind === 'list' ? node.items.join('\n') : node.value;
    var value = input.value;
    if (input.tagName === 'SELECT' && node.kind === 'scalar' &&
        /^['"].*['"]$/.test(node.value) && value !== original) {
        // keep the quoting of quoted option values
        value = "'" + value.replace(/'/g, "''") + "'";
    }
    if (value === original || (input.tagName === 'SELECT' &&
        value === original.replace(/^['"]|['"]$/g, ''))) {
        delete S.edit.edits[line];
    } else if (node.kind === 'list') {
        S.edit.edits[line] = {line: line, key: node.key,
                              items: value.split('\n').filter(function (v) {
                                  return v.trim() !== ''; })};
    } else {
        S.edit.edits[line] = {line: line, key: node.key, value: value};
    }
    var row = input.closest('.yf-row');
    if (row) { row.classList.toggle('changed', !!S.edit.edits[line]); }
    S.edit.updateDirty();
};

S.edit.revert = function () {
    if (!S.edit.name) { return; }
    S.edit.confirmDiscard().then(function (ok) {
        if (!ok) { return; }
        S.edit.text = S.edit.original;
        S.edit.edits = {};
        S.edit.added = {};
        S.$('edit-raw').value = S.edit.text;
        S.edit.updateGutter();
        S.edit.refreshOutline();
    });
};

S.edit.review = function () {
    if (!S.edit.name) { return; }
    S.edit.currentText().then(function (text) {
        GUI.showDiff({left_text: S.edit.original, right_text: text,
                      left_name: S.edit.name + ' (on disk)',
                      right_name: S.edit.name + ' (edited)',
                      title: 'Review changes'});
    });
};

S.edit.compareBackup = function () {
    // compare the file on disk with one of its gui backups
    if (!S.edit.name) { return; }
    GUI.get('api/setup/backups', {profile: S.edit.profile,
                                  name: S.edit.name}).then(function (data) {
        if (!data.backups.length) {
            GUI.toast('No backups of ' + S.edit.name + ' yet (one is kept ' +
                      'every time the gui saves it)');
            return;
        }
        GUI.dialog({id: 'edit-backups', narrow: true,
                    title: 'Backups of ' + S.edit.name,
                    body: '<select id="edit-backup-pick" style="width:100%">' +
                          data.backups.map(function (b) {
                              return '<option value="' + GUI.esc(b.path) +
                                  '">' + GUI.esc(GUI.basename(b.path)) +
                                  ' (' + GUI.fmtAge(b.mtime) + ')</option>';
                          }).join('') + '</select>',
                    buttons: [{label: 'Cancel'},
                              {label: 'Compare', cls: 'primary',
                               onclick: function (close) {
                                   var path = S.$('edit-backup-pick').value;
                                   close();
                                   GUI.showDiff({left: path,
                                                 right: S.edit.path, any: true,
                                                 title: 'Backup vs current'});
                               }}]});
    }).catch(GUI.fail);
};

// ---- add parameters (any config value / constant / keyword) ----
// the user yaml each kind of parameter belongs to
S.edit.KIND_FILES = {config: 'user_config.yaml',
                     constants: 'user_constants.yaml',
                     keywords: 'user_keywords.yaml'};

S.edit.addKind = function () {
    // the kind of parameter the open file holds (null: not a user yaml)
    var kinds = Object.keys(S.edit.KIND_FILES).filter(function (kind) {
        return S.edit.KIND_FILES[kind] === S.edit.name; });
    return kinds.length ? kinds[0] : null;
};

S.edit.presentKeys = function () {
    // every key already in the open file (sections included)
    var keys = {};
    ((S.edit.outline || {}).nodes || []).forEach(function (node) {
        keys[node.path.join('.')] = true;
    });
    return keys;
};

S.edit.defaultOf = function (info) {
    // the default of a parameter for the profile instrument
    var inst = S.edit.instrument();
    var values = info.values || {};
    if (inst && values.hasOwnProperty(inst)) { return values[inst]; }
    var insts = Object.keys(values);
    return insts.length ? values[insts[0]] : null;
};

S.edit.addDialog = function () {
    var kind = S.edit.addKind();
    if (!kind || !S.edit.editable) {
        GUI.toast('Parameters can only be added to user_config.yaml, ' +
                  'user_constants.yaml and user_keywords.yaml');
        return;
    }
    if (Object.keys(S.params).length === 0) {
        GUI.toast('The parameter list is still loading (or failed - see ' +
                  'the Docs tab)', 'bad');
        S.docs.loadParams();
        return;
    }
    var label = {config: 'config values', constants: 'constants',
                 keywords: 'header keywords'}[kind];
    var inst = S.edit.instrument();
    GUI.addParams({
        title: 'Add ' + label + ' to ' + S.edit.name,
        intro: 'Click <b>+</b> to add a parameter with its ' +
               GUI.esc(inst || '') + ' default value. It is added to the ' +
               'file as an unsaved change: edit its value in the form, ' +
               'then review and save. Click a name for its full ' +
               'description.',
        defaultLabel: 'Default (' + (inst || 'instrument') + ')',
        section: '',
        params: function () {
            // the parameters of this file's kind
            var out = {};
            Object.keys(S.params).forEach(function (key) {
                var info = S.params[key];
                if (info.kind !== kind) { return; }
                out[key] = {description: info.description, dtype: info.dtype,
                            group: info.group, advanced: !info.user,
                            value: S.edit.defaultOf(info)};
            });
            return out;
        },
        present: S.edit.presentKeys,
        add: S.edit.addParams
    });
};

S.edit.addParams = function (keys) {
    // add parameters to the open file (as an unsaved change)
    var entries = keys.map(function (key) {
        var info = S.params[key] || {};
        return {key: key, value: S.edit.defaultOf(info),
                description: info.description || '',
                dtype: info.dtype || null};
    });
    if (S.edit.view === 'raw') { S.edit.text = S.$('edit-raw').value; }
    return S.edit.currentText().then(function (text) {
        return GUI.yamlAdd(text, entries);
    }).then(function (res) {
        if (res.errors && res.errors.length) {
            GUI.toast(res.errors.join('\n'), 'bad');
        }
        if (!res.added || !res.added.length) { return false; }
        S.edit.text = res.text;
        S.edit.edits = {};
        S.$('edit-raw').value = res.text;
        // highlight the added rows until the file is saved / reloaded
        res.added.forEach(function (key) { S.edit.added[key] = true; });
        S.edit.updateGutter();
        // open the sections of the added parameters
        res.added.forEach(function (key) {
            S.edit.openSecs[key.split('.')[0]] = true;
        });
        GUI.toast('Added ' + res.added.join(', ') + ' (not saved yet)');
        return S.edit.refreshOutline().then(function () { return true; });
    }).catch(function (err) { GUI.fail(err); return false; });
};

S.edit.removeParam = function (key) {
    // take a parameter out of the open file (as an unsaved change) so the
    //   instrument default is used again
    var info = S.params[key] || {};
    var node = ((S.edit.outline || {}).nodes || []).filter(function (n) {
        return n.path.join('.') === key; })[0];
    var inst = S.edit.instrument();
    GUI.confirmRemove({key: key, file: S.edit.name, known: !!S.params[key],
                       current: node ? S.edit.nodeValue(node) : '',
                       value: S.edit.defaultOf(info),
                       defaultLabel: (inst || 'instrument') + ' default'})
        .then(function (ok) {
            if (!ok) { return; }
            if (S.edit.view === 'raw') { S.edit.text = S.$('edit-raw').value; }
            return S.edit.currentText().then(function (text) {
                return GUI.yamlRemove(text, [key]);
            }).then(function (res) {
                if (res.errors && res.errors.length) {
                    GUI.toast(res.errors.join('\n'), 'bad');
                }
                if (!res.removed || !res.removed.length) { return; }
                S.edit.text = res.text;
                S.edit.edits = {};
                S.$('edit-raw').value = res.text;
                res.removed.forEach(function (k) { delete S.edit.added[k]; });
                S.edit.updateGutter();
                GUI.toast('Removed ' + res.removed.join(', ') + ' (not ' +
                          'saved yet)');
                return S.edit.refreshOutline();
            });
        }).catch(GUI.fail);
};

S.edit.save = function () {
    if (!S.edit.name || !S.edit.editable) { return; }
    S.edit.currentText().then(function (text) {
        if (text === S.edit.original) { GUI.toast('No changes to save');
                                        return; }
        var doSave = function (force) {
            return GUI.post('api/setup/file_save', {
                profile: S.edit.profile, name: S.edit.name, text: text,
                mtime: S.edit.mtime, force: force
            }).then(function (res) {
                if (res.conflict) {
                    return GUI.confirm('File changed on disk', GUI.esc(
                        res.message), 'Save anyway').then(function (ok) {
                        if (ok) { return doSave(true); }
                    });
                }
                GUI.toast(res.message, res.success ? 'ok' : 'bad');
                if (res.success) { return S.edit.load(S.edit.name); }
            }).catch(GUI.fail);
        };
        GUI.showDiff({left_text: S.edit.original, right_text: text,
                      left_name: S.edit.name + ' (on disk)',
                      right_name: S.edit.name + ' (to be saved)',
                      title: 'Save ' + S.edit.name + '?',
                      buttons: [{label: 'Cancel'},
                                {label: 'Save', cls: 'primary',
                                 onclick: function (close) {
                                     close();
                                     doSave(false);
                                 }}]});
    });
};

S.edit.rerun = function (installSh) {
    // re-run apero_setup.py --update (or --install_sh) for the profile
    if (!S.edit.profile) { GUI.toast('Choose a profile first', 'bad');
                           return; }
    var start = function () {
        S.edit.changed = null;
        GUI.startJob('api/setup/update', {profile: S.edit.profile,
                                          install_sh: installSh},
                     GUI.consoles.edit);
    };
    var warn = S.edit.dirty() ? '<p><b>You have unsaved changes</b> - setup ' +
        'reads the files on disk (save first).</p>' : '';
    if (installSh) {
        if (!warn) { start(); return; }
        GUI.confirm('Regenerate install_script.sh', warn, 'Continue')
            .then(function (ok) { if (ok) { start(); } });
        return;
    }
    GUI.confirm('Re-run setup', warn + '<p>Run <code>apero_setup.py --update' +
                '</code> for <code>' + GUI.esc(S.edit.profile) + '</code>? ' +
                'The user yamls are written again from the APERO defaults ' +
                'plus the setup values; if <code>CLEAN_START</code> is true ' +
                'in <code>install.yaml</code> the profile is also cleaned ' +
                '(apero_reset).</p>', 'Re-run setup')
        .then(function (ok) { if (ok) { start(); } });
};

S.edit.done = function (job) {
    // a re-run finished: reload the file and offer the changes
    S.loadProfiles();
    if (!S.edit.profile) { return; }
    S.edit.load(S.edit.name || 'user_config.yaml');
    GUI.get('api/setup/rerun_diff', {profile: S.edit.profile})
        .then(function (data) {
            S.edit.changed = data.changed;
            S.$('edit-changes').disabled = !data.snapshot;
            S.$('edit-changes').textContent = 'Show what changed (' +
                data.changed.length + ' file(s))';
            if (job.returncode === 0) {
                GUI.toast('Setup finished: ' + data.changed.length +
                          ' file(s) changed', 'ok');
            }
        }).catch(GUI.fail);
};

S.edit.showChanges = function () {
    var changed = S.edit.changed || [];
    if (!changed.length) { GUI.toast('No config file changed'); return; }
    GUI.dialog({id: 'edit-changed', narrow: true, title: 'Files changed by ' +
                'the re-run',
                body: '<p class="muted small">Click a file to compare it ' +
                      'with its content before the re-run.</p>' +
                      changed.map(function (item, it) {
                          return '<div><a class="doc-link" data-changed="' +
                              it + '">' + GUI.esc(item.name) + '</a></div>';
                      }).join(''),
                buttons: [{label: 'Close', cls: 'primary'}]});
    document.querySelectorAll('[data-changed]').forEach(function (el) {
        el.onclick = function () {
            var item = changed[Number(el.getAttribute('data-changed'))];
            GUI.showDiff({left_text: item.old, right_text: item.new,
                          left_name: item.name + ' (before)',
                          right_name: item.name + ' (after)',
                          title: item.name + ': before / after the re-run'});
        };
    });
};

/* ==========================================================================
   Validate
   ========================================================================== */
S.val = {data: null};

S.val.profile = function () { return S.$('val-profile').value; };

S.val.selected = function () {
    GUI.store('profile-val-profile', S.val.profile());
    S.val.data = null;
    S.$('val-result').innerHTML = '';
    ['val-download', 'val-copy', 'val-save'].forEach(function (id) {
        S.$(id).disabled = true; });
    S.val.updateCli();
};

S.val.browseProfile = function () {
    S.browseProfile('val-profile').then(function (path) {
        if (path) { S.val.selected(); }
    });
};

S.val.open = function (path) {
    if (!S.profileOf(path)) {
        S.extraProfiles.push({path: path, name: GUI.basename(path),
                              valid: true});
        S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
    }
    S.$('val-profile').value = path;
    GUI.setTab('validate');
    S.val.selected();
    S.val.check(false);
};

S.val.updateCli = function () {
    var profile = S.val.profile();
    if (!profile) { GUI.setCli('cli-validate', ''); return; }
    GUI.post('api/setup/preview', {action: 'validate', profile: profile,
                                   report: S.$('val-with-report').checked})
        .then(function (res) {
            GUI.setCli('cli-validate', res.display || res.errors.join('\n'));
        }).catch(function () { return null; });
};

S.val.check = function (refresh) {
    var profile = S.val.profile();
    if (!profile) { GUI.toast('Choose a profile first', 'bad'); return; }
    S.$('val-check').disabled = true;
    S.$('val-result').innerHTML = '<div class="section-card muted">' +
        'Checking ' + GUI.esc(profile) + ' (loads the profile and connects ' +
        'to the database - this can take a while)...</div>';
    GUI.post('api/setup/report', {profile: profile, refresh: refresh},
             GUI.config.timeout).then(function (data) {
        S.$('val-check').disabled = false;
        S.val.data = data;
        ['val-download', 'val-copy', 'val-save'].forEach(function (id) {
            S.$(id).disabled = false; });
        S.val.render(data.report, data.collected);
    }).catch(function (err) {
        S.$('val-check').disabled = false;
        S.$('val-result').innerHTML = '<div class="notice bad">' +
            GUI.esc(err.message) + '</div>';
    });
};

S.val.table = function (head, rows) {
    return '<table><tr>' + head.map(function (h) {
        return '<th>' + GUI.esc(h) + '</th>'; }).join('') + '</tr>' +
        rows.join('') + '</table>';
};

S.val.kv = function (values, keys) {
    // a key / value table
    return '<table>' + (keys || Object.keys(values || {})).map(function (k) {
        var v = values[k];
        if (v === undefined) { return ''; }
        return '<tr><th>' + GUI.esc(k) + '</th><td class="mono">' +
            GUI.esc(typeof v === 'object' && v !== null ? JSON.stringify(v) :
                    String(v)) + '</td></tr>';
    }).join('') + '</table>';
};

S.val.card = function (title, level, body, wide) {
    return '<div class="section-card rep-card' + (wide ? ' rep-wide' : '') +
        '"><h3>' + GUI.esc(title) + (level ? ' ' + S.statusPill(level) : '') +
        '</h3>' + body + '</div>';
};

S.val.sectionLevel = function (report, section) {
    // the worst check level of one section
    var order = ['ok', 'info', 'warn', 'bad'];
    var worst = 'ok';
    (report.checks || []).forEach(function (chk) {
        if (chk.section === section && order.indexOf(chk.level) >
            order.indexOf(worst)) { worst = chk.level; }
    });
    return worst;
};

S.val.render = function (rep, collected) {
    var summary = rep.summary || {};
    var level = function (sec) { return S.val.sectionLevel(rep, sec); };
    var checks = (rep.checks || []).slice().sort(function (a, b) {
        var order = ['bad', 'warn', 'info', 'ok'];
        return order.indexOf(a.level) - order.indexOf(b.level);
    });
    var html = '<div class="section-card"><div class="rep-head"><span ' +
        'class="rep-status ' + GUI.esc(summary.status) + '">' +
        GUI.esc((summary.status || '?').toUpperCase()) + '</span><span>' +
        GUI.esc(rep.profile && rep.profile.values ?
                rep.profile.values.drs_uconfig : '') + '</span><span ' +
        'class="muted small">APERO ' + GUI.esc(rep.meta.apero_version) +
        ' &middot; checked ' + (collected ? GUI.fmtAge(collected) : '') +
        '</span></div><ul class="rep-checks">' + (checks.length ?
        checks.map(function (chk) {
            return '<li>' + S.statusPill(chk.level) + ' <b>' +
                GUI.esc(chk.section) + '</b>: ' + GUI.esc(chk.message) +
                '</li>';
        }).join('') : '<li>' + S.statusPill('ok') + ' no problems found' +
        '</li>') + '</ul></div><div class="rep-grid">';
    // profile
    var prof = rep.profile || {};
    html += S.val.card('Profile', level('profile'), prof.error ?
        GUI.esc(prof.error) : S.val.kv(prof.values));
    // machine
    var mach = (rep.machine || {}).values || {};
    var mem = mach.memory_total ? S.fmtBytes(mach.memory_available) +
        ' free of ' + S.fmtBytes(mach.memory_total) : 'unknown';
    html += S.val.card('Machine', level('machine'), S.val.kv(
        {host: mach.hostname, user: mach.user, platform: mach.platform,
         cpus: mach.cpus + (mach.cpus_physical ? ' (' + mach.cpus_physical +
         ' physical)' : ''), memory: mem,
         load: (mach.load_average || []).join(' / '),
         slurm: mach.slurm ? 'sbatch available' : 'no'}));
    // config files
    var files = (rep.config || {}).files || [];
    html += S.val.card('Config files (DRS_UCONFIG)', level('config'),
        S.val.table(['file', 'status', 'written by', 'modified'],
        files.map(function (f) {
            var st = !f.exists ? S.statusPill('info', 'missing') :
                (f.parse && f.parse !== 'ok' ? S.statusPill('bad', 'parse ' +
                 'error') : S.statusPill('ok', 'ok'));
            return '<tr><td class="mono">' + GUI.esc(f.name) + '</td><td>' +
                st + '</td><td>' + GUI.esc(f.written_by || '') + '</td><td>' +
                GUI.esc(f.modified || '') + '</td></tr>';
        })), true);
    // paths
    var paths = (rep.paths || {}).paths || [];
    var fss = (rep.paths || {}).filesystems || [];
    html += S.val.card('Data paths', level('paths'), S.val.table(
        ['key', 'path', 'status', 'entries'], paths.map(function (p) {
            var st = !p.path ? S.statusPill('bad', 'not set') :
                (!p.exists ? S.statusPill('bad', 'missing') :
                 (p.writable === false && p.key !== 'PATH.EXTERNAL_RAW' ?
                  S.statusPill('bad', 'read only') : S.statusPill('ok', 'ok'))) +
                (p.symlink ? ' <span class="pill">symlink</span>' : '');
            return '<tr><td>' + GUI.esc(p.key) + '<div class="muted small">' +
                GUI.esc(p.label) + '</div></td><td class="mono">' +
                GUI.esc(p.path || '') + '</td><td>' + st + '</td><td ' +
                'class="num">' + GUI.esc(p.entries === undefined ? '' :
                                         String(p.entries)) + '</td></tr>';
        })) + '<h4>Disk space</h4>' + S.val.table(['file system (e.g.)',
        'free', 'used'], fss.map(function (fs) {
            var used = fs.total ? 1 - fs.free / fs.total : 0;
            return '<tr><td class="mono">' + GUI.esc(fs.example) + '</td>' +
                '<td class="num">' + S.fmtBytes(fs.free) + ' / ' +
                S.fmtBytes(fs.total) + '</td><td><div class="rep-bar"><span ' +
                'style="width:' + Math.round(used * 100) + '%"></span></div>' +
                Math.round(used * 100) + '%</td></tr>';
        })), true);
    // database
    var db = rep.database || {};
    var tables = db.tables || [];
    html += S.val.card('Databases', level('database'), (db.error ?
        '<div class="notice bad">' + GUI.esc(db.error) + '</div>' : '') +
        S.val.kv(db.settings || {}) + S.val.table(['database', 'table / ' +
        'store', 'rows', 'break down'], tables.map(function (t) {
            var groups = t.groups ? Object.keys(t.groups).map(function (g) {
                return GUI.esc(g) + ': ' + t.groups[g]; }).join(', ') +
                (t.ngroups > Object.keys(t.groups).length ? ', ...' : '') : '';
            var status = t.error ? S.statusPill('bad', t.error) :
                (t.exists === false ? S.statusPill('bad', 'missing') : '');
            return '<tr><td><b>' + GUI.esc(t.kind) + '</b></td><td ' +
                'class="mono">' + GUI.esc(t.table || t.path || '') + ' ' +
                status + '</td><td class="num">' + GUI.esc(
                t.rows === undefined ? '' : String(t.rows)) + '</td><td ' +
                'class="rep-groups">' + (t.groupby ? GUI.esc(t.groupby) +
                ' &rarr; ' : '') + groups + '</td></tr>';
        })), true);
    // modules
    var mods = rep.modules || {};
    var py = mods.python || {};
    var apero = mods.apero || {};
    var gitText = function (info) {
        if (!info || !info.git) { return ''; }
        if (info.git.error) { return info.git.error; }
        return info.git.branch + ' @ ' + info.git.commit +
            (info.git.dirty ? ' (uncommitted changes)' : '');
    };
    var pkgs = mods.packages || [];
    var nbad = pkgs.filter(function (p) { return p.status !== 'ok'; }).length;
    html += S.val.card('Python modules', level('modules'), S.val.kv(
        {python: py.version, executable: py.executable,
         conda_env: py.conda_env, apero: apero.apero ? apero.apero.version +
         '  ' + gitText(apero.apero) : '', aperocore: apero.aperocore ?
         apero.aperocore.version + '  ' + gitText(apero.aperocore) : ''}) +
        '<details' + (nbad ? ' open' : '') + '><summary>' + pkgs.length +
        ' package(s), ' + nbad + ' not as required</summary>' +
        S.val.table(['package', 'installed', 'required', ''],
        pkgs.map(function (p) {
            return '<tr><td>' + GUI.esc(p.name) + '</td><td class="mono">' +
                GUI.esc(p.installed || '-') + '</td><td class="mono">' +
                GUI.esc(p.required || '') + '</td><td>' + S.statusPill(
                p.status === 'ok' ? 'ok' : (p.status === 'missing' ?
                'info' : 'warn'), p.status) + '</td></tr>';
        })) + '</details>', true);
    html += '</div>';
    S.$('val-result').innerHTML = html;
};

S.val.download = function () {
    if (!S.val.data) { return; }
    var blob = new Blob([S.val.data.text], {type: 'text/plain'});
    var link = document.createElement('a');
    var name = GUI.basename(S.val.profile()) || 'apero';
    var stamp = new Date().toISOString().replace(/[-:]/g, '')
        .replace('T', '_').slice(0, 15);
    link.href = URL.createObjectURL(blob);
    link.download = 'apero_report_' + name + '_' + stamp + '.txt';
    document.body.appendChild(link);
    link.click();
    setTimeout(function () { URL.revokeObjectURL(link.href); link.remove(); },
               1000);
};

S.val.copy = function (button) {
    if (S.val.data) { GUI.copyText(S.val.data.text, button); }
};

S.val.save = function () {
    GUI.post('api/setup/report_save', {profile: S.val.profile()})
        .then(function (res) { GUI.toast(res.message, 'ok'); })
        .catch(GUI.fail);
};

S.val.runValidate = function () {
    var profile = S.val.profile();
    if (!profile) { GUI.toast('Choose a profile first', 'bad'); return; }
    GUI.startJob('api/setup/validate', {profile: profile,
                                        report: S.$('val-with-report')
                                            .checked},
                 GUI.consoles.validate);
};

/* ==========================================================================
   Data manager (data directories of a profile, apero_reset.py)
   ========================================================================== */
S.data = {profile: null, dirs: [], parts: [], dir: null, root: null,
          listing: null, checked: {}, stats: {}, part: 'all',
          sort: {key: 'name', asc: true}};

S.data.init = function () {
    S.$('data-filter').oninput = S.debounce(S.data.render, 150);
    document.querySelectorAll('#tab-data th[data-sort]').forEach(
        function (th) {
            th.onclick = function () {
                var key = th.getAttribute('data-sort');
                S.data.sort = {key: key, asc: S.data.sort.key === key ?
                               !S.data.sort.asc : true};
                S.data.render();
            };
        });
    GUI.onTab('data', function () {
        var path = S.$('data-profile').value;
        if (path && path !== S.data.profile) { S.data.load(path); }
    });
};

S.data.open = function (path) {
    // open a profile in the Data tab (deep links, other tabs)
    if (!S.profileOf(path)) {
        S.extraProfiles.push({path: path, name: GUI.basename(path),
                              valid: true});
        S.PROFILE_SELECTS.forEach(S.fillProfileSelect);
    }
    S.$('data-profile').value = path;
    GUI.setTab('data');
    S.data.selected();
};

S.data.selected = function () {
    var path = S.$('data-profile').value;
    GUI.store('profile-data-profile', path);
    S.data.load(path);
};

S.data.browseProfile = function () {
    S.browseProfile('data-profile').then(function (path) {
        if (path) { S.data.load(path); }
    });
};

S.data.reload = function () {
    S.data.stats = {};
    if (S.data.profile) { S.data.load(S.data.profile, S.data.dir); }
};

S.data.load = function (path, dir) {
    // the data directories of a profile (setup must have been run)
    var err = S.$('data-error');
    S.data.profile = path || null;
    S.data.root = null;
    S.$('data-dirs').innerHTML = '';
    S.$('data-browser').style.display = 'none';
    S.$('data-reset-card').style.display = 'none';
    err.style.display = 'none';
    if (!path) { return Promise.resolve(); }
    return GUI.post('api/setup/data_dirs', {profile: path})
        .then(function (res) {
            S.data.dirs = res.dirs;
            S.data.parts = res.reset_parts;
            S.data.renderDirs();
            S.data.renderParts();
            S.$('data-reset-card').style.display = '';
            S.data.updateCli();
            S.data.loadStats();
            // reopen the directory shown before (or the reduced data)
            var open = null;
            if (dir) {
                open = S.data.dirs.filter(function (d) {
                    return dir.indexOf(d.path) === 0; })[0];
            }
            open = open || S.data.dirs.filter(function (d) {
                return d.label === GUI.recall('data-dir', 'red'); })[0] ||
                S.data.dirs[0];
            if (open) { S.data.openDir(open, dir); }
        }).catch(function (error) {
            err.style.display = '';
            err.textContent = error.message;
        });
};

S.data.statText = function (info) {
    if (!info.exists) { return 'missing'; }
    var st = S.data.stats[info.path];
    if (!st) { return '...'; }
    if (st.error) { return '?'; }
    return (st.complete ? '' : '&ge; ') + st.nfiles +
        (st.nfiles === 1 ? ' file' : ' files') + ' &middot; ' +
        GUI.fmtBytes(st.size);
};

S.data.renderDirs = function () {
    var holder = S.$('data-dirs');
    holder.innerHTML = S.data.dirs.map(function (info, index) {
        var active = S.data.root === info.path;
        return '<button class="data-dir' + (active ? ' active' : '') +
            (info.exists ? '' : ' missing') + '" data-index="' + index +
            '" data-param="' + GUI.esc(info.key) + '" title="' +
            GUI.esc(info.path) + '"><span class="data-dir-name">' +
            GUI.esc(info.label) + (info.protected ? ' &#128274;' : '') +
            '</span><span class="data-dir-stat">' + S.data.statText(info) +
            '</span></button>';
    }).join('');
    holder.querySelectorAll('[data-index]').forEach(function (btn) {
        btn.onclick = function () {
            S.data.openDir(S.data.dirs[Number(btn.getAttribute(
                'data-index'))]);
        };
    });
};

S.data.loadStats = function () {
    // count the files of each directory, one after the other
    var profile = S.data.profile;
    var todo = S.data.dirs.filter(function (info) {
        return info.exists && !S.data.stats[info.path]; });
    var next = function () {
        if (!todo.length || S.data.profile !== profile) { return; }
        var info = todo.shift();
        GUI.post('api/setup/dir_stats', {path: info.path})
            .then(function (st) { S.data.stats[info.path] = st; })
            .catch(function () {
                S.data.stats[info.path] = {error: true}; })
            .then(function () {
                if (S.data.profile === profile) { S.data.renderDirs(); }
                next();
            });
    };
    next();
};

S.data.current = function () {
    return S.data.dirs.filter(function (d) {
        return d.path === S.data.root; })[0] || null;
};

S.data.openDir = function (info, sub) {
    S.data.root = info.path;
    GUI.store('data-dir', info.label);
    S.data.renderDirs();
    S.$('data-browser').style.display = '';
    S.$('data-dir-title').textContent = info.label + ' (' + info.key + ')';
    S.$('data-dir-desc').textContent = S.argHelp[info.key] ||
        (info.key === 'DRS_UCONFIG' ? 'The profile directory: the files ' +
         'apero_setup.py wrote (edit them in the Edit tab)' : '');
    S.$('data-dir-ro').style.display = info.protected ? '' : 'none';
    S.$('data-del-selected').disabled = info.protected;
    if (!info.exists) {
        S.data.listing = null;
        S.$('data-crumbs').textContent = info.path;
        S.$('data-note').textContent = '';
        S.$('data-body').innerHTML = '<tr><td colspan="6" class="muted">' +
            'This directory does not exist (re-run setup to create ' +
            'it).</td></tr>';
        return;
    }
    S.data.list(sub && sub.indexOf(info.path) === 0 ? sub : info.path);
};

S.data.list = function (dir) {
    return GUI.get('api/fs/list', {path: dir}).then(function (data) {
        S.data.dir = data.path;
        S.data.listing = data;
        S.data.checked = {};
        S.$('data-all').checked = false;
        var root = S.data.root;
        S.$('data-up').disabled = data.path === root;
        // bread crumbs below the data directory
        var rel = data.path.indexOf(root) === 0 ?
            data.path.substring(root.length) : data.path;
        var html = '<a data-p="' + GUI.esc(root) + '">' + GUI.esc(root) +
            '</a>';
        var acc = root;
        rel.split('/').filter(Boolean).forEach(function (part) {
            acc += '/' + part;
            html += ' / <a data-p="' + GUI.esc(acc) + '">' + GUI.esc(part) +
                '</a>';
        });
        var crumbs = S.$('data-crumbs');
        crumbs.innerHTML = html;
        crumbs.querySelectorAll('a').forEach(function (a) {
            a.onclick = function () { S.data.list(a.getAttribute('data-p')); };
        });
        S.data.render();
    }).catch(GUI.fail);
};

S.data.up = function () {
    var data = S.data.listing;
    if (data && data.parent && S.data.dir !== S.data.root) {
        S.data.list(data.parent);
    }
};

S.data.render = function () {
    var data = S.data.listing;
    var body = S.$('data-body');
    if (!data) { return; }
    var info = S.data.current() || {};
    var filter = S.$('data-filter').value.toLowerCase();
    var sort = S.data.sort;
    var entries = data.entries.filter(function (ent) {
        return !filter || ent.name.toLowerCase().indexOf(filter) >= 0;
    });
    entries.sort(function (a, b) {
        if ((a.kind === 'dir') !== (b.kind === 'dir')) {
            return a.kind === 'dir' ? -1 : 1;
        }
        var va = a[sort.key] || 0;
        var vb = b[sort.key] || 0;
        if (sort.key === 'name') { va = a.name.toLowerCase();
                                   vb = b.name.toLowerCase(); }
        var cmp = va < vb ? -1 : (va > vb ? 1 : 0);
        return sort.asc ? cmp : -cmp;
    });
    S.$('data-note').textContent = entries.length + ' item(s)' +
        (data.truncated ? ' (listing truncated)' : '') +
        (data.error ? ' - ' + data.error : '');
    if (entries.length === 0) {
        body.innerHTML = '<tr><td colspan="6" class="muted">Empty ' +
            'directory.</td></tr>';
        return;
    }
    body.innerHTML = entries.map(function (ent, index) {
        var actions = '';
        if (ent.kind === 'fits') {
            actions += '<button data-act="view">Header / data</button>';
        } else if (ent.kind !== 'dir') {
            actions += '<button data-act="view">View</button>';
        }
        if (ent.kind !== 'dir') {
            actions += '<a href="' + GUI.rawUrl(ent.path, '&download=1') +
                '"><button>Download</button></a>';
        }
        if (!info.protected) {
            actions += '<button class="danger" data-act="delete">Delete' +
                '</button>';
        }
        return '<tr data-index="' + index + '"><td><input type="checkbox">' +
            '</td><td class="fb-icon">' + (GUI.FILE_ICONS[ent.kind] || '') +
            '</td><td class="fb-name">' + GUI.esc(ent.name) + '</td><td ' +
            'class="num small">' + (ent.kind === 'dir' ? '' :
            GUI.fmtBytes(ent.size)) + '</td><td class="small nowrap ' +
            'muted">' + GUI.fmtTime(ent.mtime) + '</td><td ' +
            'class="row-actions">' + actions + '</td></tr>';
    }).join('');
    body.querySelectorAll('tr').forEach(function (tr) {
        var ent = entries[Number(tr.getAttribute('data-index'))];
        tr.querySelector('input').onchange = function () {
            S.data.checked[ent.path] = this.checked;
        };
        tr.querySelector('.fb-name').onclick = function () {
            if (ent.kind === 'dir') { S.data.list(ent.path); }
            else { GUI.viewFile(ent.path); }
        };
        tr.querySelectorAll('[data-act]').forEach(function (btn) {
            btn.onclick = function () {
                var act = btn.getAttribute('data-act');
                if (act === 'view') { GUI.viewFile(ent.path); }
                if (act === 'delete') { S.data.remove([ent.path]); }
            };
        });
    });
};

S.data.selectAll = function (on) {
    document.querySelectorAll('#data-body input[type=checkbox]')
        .forEach(function (box) {
            box.checked = on;
            box.dispatchEvent(new Event('change'));
        });
};

S.data.checkedPaths = function () {
    return Object.keys(S.data.checked).filter(function (path) {
        return S.data.checked[path]; });
};

S.data.remove = function (paths) {
    if (paths.length === 0) { GUI.toast('Select files first'); return; }
    var list = paths.slice(0, 12).map(function (p) {
        return '<li><code>' + GUI.esc(p) + '</code></li>'; }).join('') +
        (paths.length > 12 ? '<li>... and ' + (paths.length - 12) +
         ' more</li>' : '');
    GUI.confirm('Delete ' + paths.length + ' item(s)', '<p>Permanently ' +
                'delete (directories with everything inside):</p><ul>' +
                list + '</ul><p class="muted small">The APERO databases ' +
                'are not updated: entries for deleted files stay in the ' +
                'databases. Use <b>Reset</b> to clean a whole part of the ' +
                'profile consistently.</p>', 'Delete').then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/fs/delete', {paths: paths}).then(function (res) {
            GUI.toast(res.message, res.success ? 'ok' : 'bad');
            delete S.data.stats[S.data.root];
            S.data.list(S.data.dir);
            S.data.loadStats();
        }).catch(GUI.fail);
    });
};

S.data.deleteSelected = function () {
    S.data.remove(S.data.checkedPaths());
};

S.data.diffSelected = function () {
    var paths = S.data.checkedPaths();
    if (paths.length !== 2) { GUI.toast('Select exactly 2 files', 'bad');
                              return; }
    GUI.showDiff({left: paths[0], right: paths[1], title: 'Compare files'});
};

/* ---- reset ---- */
S.data.renderParts = function () {
    var paths = {};
    S.data.dirs.forEach(function (d) { paths[d.key] = d.path; });
    var parts = [{name: 'all', key: null, help: 'Every part below: ' +
                  'assets, all databases and every data directory ' +
                  'except raw'}]
        .concat(S.data.parts);
    var holder = S.$('data-reset-parts');
    holder.innerHTML = parts.map(function (part) {
        var desc = part.help + (part.key && paths[part.key] ? ' - ' +
                                paths[part.key] : '');
        return S.setup.choiceHtml('data-reset-part', part.name,
                                  part.name === 'all' ? 'Everything' :
                                  part.name, desc, null);
    }).join('');
    S.setup.setRadio('data-reset-part', S.data.part);
    holder.onchange = function () {
        S.data.part = S.setup.radio('data-reset-part') || 'all';
        S.data.markParts();
        S.data.updateCli();
    };
    S.data.markParts();
};

S.data.markParts = function () {
    S.$('data-reset-parts').querySelectorAll('.choice').forEach(
        function (el) {
            el.classList.toggle('selected', el.querySelector('input')
                .checked);
        });
};

S.data.resetArgs = function () {
    return {profile: S.data.profile, part: S.data.part,
            ask: S.$('data-reset-ask').checked,
            nolog: S.$('data-reset-nolog').checked};
};

S.data.updateCli = function () {
    if (!S.data.profile) { GUI.setCli('cli-reset', ''); return; }
    var args = S.data.resetArgs();
    args.action = 'reset';
    GUI.post('api/setup/preview', args).then(function (res) {
        GUI.setCli('cli-reset', res.display || res.errors.join('\n'));
    }).catch(function () { return null; });
};

S.data.reset = function () {
    if (!S.data.profile) { GUI.toast('Choose a profile first', 'bad');
                           return; }
    var args = S.data.resetArgs();
    var what = args.part === 'all' ? 'everything (assets, all databases ' +
        'and all data except raw)' : 'the ' + args.part + ' part';
    var name = GUI.basename(S.data.profile);
    var start = function () {
        GUI.startJob('api/setup/reset', args, GUI.consoles.data);
    };
    var html = '<p>Reset ' + GUI.esc(what) + ' of profile <code>' +
        GUI.esc(S.data.profile) + '</code> with <code>apero_reset.py' +
        '</code>. This cannot be undone.</p>';
    if (args.ask) {
        GUI.confirm('Reset ' + name, html + '<p>apero_reset.py asks ' +
                    'before each part: answer in the console below.</p>',
                    'Start reset').then(function (ok) {
            if (ok) { start(); }
        });
    } else {
        GUI.confirmTyped({title: 'Reset ' + name, word: name,
                          label: 'Reset', html: html + '<p><b>No ' +
                          'questions will be asked</b> (--nowarn).</p>'})
            .then(function (ok) { if (ok) { start(); } });
    }
};

S.data.done = function () {
    // a reset finished: count the files again
    S.data.stats = {};
    if (S.data.profile) { S.data.load(S.data.profile, S.data.dir); }
};

/* ==========================================================================
   Docs (constants + guides)
   ========================================================================== */
S.docs = {menu: 'constants', kind: '', inst: '', key: null, section: null,
          guides: [], guide: null, instruments: []};
S.DOC_KINDS = [['', 'All'], ['config', 'Config (user_config.yaml)'],
               ['constants', 'Constants (user_constants.yaml)'],
               ['keywords', 'Header keywords (user_keywords.yaml)']];

S.docs.init = function () {
    S.$('docs-filter').oninput = S.debounce(S.docs.renderList, 150);
    S.$('docs-user-only').onchange = S.docs.renderList;
    GUI.onTab('docs', function () {
        S.docs.setMenu(GUI.recall('docs-menu', 'constants'));
    });
};

S.docs.loadParams = function () {
    // every constant (probed once by the server)
    return GUI.get('api/setup/params').then(function (data) {
        S.params = data.params || {};
        S.docs.instruments = data.instruments || [];
        if (S.edit.outline) { S.edit.renderForm(); }
        if (GUI.currentTab === 'docs') { S.docs.renderList(); }
    }).catch(function (err) {
        S.docs.paramError = err.message;
        if (GUI.currentTab === 'docs') { S.docs.renderList(); }
    });
};

S.docs.setMenu = function (menu) {
    S.docs.menu = menu;
    GUI.store('docs-menu', menu);
    S.$('docs-menu-constants').classList.toggle('active', menu ===
                                                'constants');
    S.$('docs-menu-guides').classList.toggle('active', menu === 'guides');
    var isConst = menu === 'constants';
    S.$('docs-kind-row').style.display = isConst ? '' : 'none';
    S.$('docs-inst-row').style.display = isConst ? '' : 'none';
    S.$('docs-user-label').style.display = isConst ? '' : 'none';
    if (menu === 'guides') { S.docs.loadGuides(); }
    S.docs.renderList();
};

S.docs.chips = function (id, items, current, onpick) {
    var holder = S.$(id);
    holder.innerHTML = items.map(function (item) {
        return '<button class="chip' + (item[0] === current ? ' active' : '') +
            '" data-chip="' + GUI.esc(item[0]) + '">' + GUI.esc(item[1]) +
            '</button>';
    }).join('');
    holder.querySelectorAll('[data-chip]').forEach(function (btn) {
        btn.onclick = function () { onpick(btn.getAttribute('data-chip')); };
    });
};

S.docs.group = function (key) {
    // the list group of a key: its group (or first part of the name)
    var info = S.params[key];
    if (info && info.group && info.kind !== 'keywords') { return info.group; }
    if (info && info.kind === 'keywords') {
        return 'KEYWORDS' + (info.group ? '.' + info.group : ''); }
    return key.split('.')[0];
};

S.docs.matches = function () {
    var filter = S.$('docs-filter').value.toLowerCase();
    var userOnly = S.$('docs-user-only').checked;
    var groups = {};
    Object.keys(S.params).sort().forEach(function (key) {
        var info = S.params[key];
        if (S.docs.kind && info.kind !== S.docs.kind) { return; }
        if (userOnly && !info.user) { return; }
        if (filter && (key + ' ' + info.description).toLowerCase()
            .indexOf(filter) < 0) { return; }
        var group = S.docs.group(key);
        (groups[group] = groups[group] || []).push(key);
    });
    return groups;
};

S.docs.renderList = function () {
    if (S.docs.menu === 'guides') { S.docs.renderGuideList(); return; }
    var holder = S.$('docs-list');
    S.docs.chips('docs-kinds', S.DOC_KINDS, S.docs.kind, function (kind) {
        S.docs.kind = kind;
        S.docs.renderList();
    });
    S.docs.chips('docs-insts', [['', 'All instruments']].concat(
        S.docs.instruments.map(function (inst) { return [inst, inst]; })),
                 S.docs.inst, function (inst) {
        S.docs.inst = inst;
        S.docs.renderList();
        if (S.docs.key) { S.docs.render(S.docs.key); }
    });
    if (Object.keys(S.params).length === 0) {
        holder.innerHTML = '<p class="muted">' + (S.docs.paramError ?
            'Could not load the constants: ' + GUI.esc(S.docs.paramError) :
            'Loading the constant descriptions (a few seconds)...') + '</p>';
        return;
    }
    var groups = S.docs.matches();
    var names = Object.keys(groups).sort();
    S.$('docs-count').textContent = names.reduce(function (n, g) {
        return n + groups[g].length; }, 0) + ' entries in ' + names.length +
        ' group(s)';
    holder.innerHTML = names.map(function (group) {
        return '<div class="doc-group' + (group === S.docs.section &&
            !S.docs.key ? ' active' : '') + '" data-group="' +
            GUI.esc(group) + '"><span>' + GUI.esc(group) + '</span><span ' +
            'class="doc-group-n">' + groups[group].length + '</span></div>' +
            groups[group].map(function (key) {
                var info = S.params[key];
                var short = key.indexOf(group + '.') === 0 ?
                    key.substring(group.length + 1) : key;
                return '<div class="doc-item' + (key === S.docs.key ?
                    ' active' : '') + '" data-key="' + GUI.esc(key) + '">' +
                    GUI.esc(short) + (info.user ? ' <span class="pill ok">' +
                    'user</span>' : '') + '</div>';
            }).join('');
    }).join('') || '<p class="muted">Nothing matches.</p>';
    holder.querySelectorAll('.doc-item').forEach(function (el) {
        el.onclick = function () { S.docs.render(el.getAttribute('data-key'));
                                   S.docs.markActive(); };
    });
    holder.querySelectorAll('.doc-group').forEach(function (el) {
        el.onclick = function () {
            S.docs.renderGroup(el.getAttribute('data-group'));
            S.docs.markActive();
        };
    });
};

S.docs.markActive = function () {
    document.querySelectorAll('#docs-list .doc-item').forEach(function (el) {
        el.classList.toggle('active', el.getAttribute('data-key') ===
                            S.docs.key);
    });
    document.querySelectorAll('#docs-list .doc-group').forEach(function (el) {
        el.classList.toggle('active', !S.docs.key &&
                            el.getAttribute('data-group') === S.docs.section);
    });
};

S.docs.valueText = function (value) {
    if (value === null || value === undefined) { return 'None'; }
    return typeof value === 'object' ? JSON.stringify(value) : String(value);
};

S.docs.constHtml = function (key, level) {
    // one constant: name, pills, meta line, values per instrument, text
    var info = S.params[key];
    var tag = level === 3 ? 'h3' : 'h2';
    var insts = S.docs.inst ? [S.docs.inst] : S.docs.instruments;
    var values = info.values || {};
    var valueHead = info.kind === 'keywords' ? 'header card / default / ' +
        'comment' : 'value';
    return '<' + tag + ' class="mono doc-key">' + GUI.esc(key) + '</' + tag +
        '><div class="yaml-summary"><span class="pill">' + GUI.esc(info.kind) +
        '</span>' + (info.user ? '<span class="pill ok">user setting (' +
        GUI.esc(info.file) + ')</span>' : '<span class="pill">not in the user ' +
        'yamls</span>') + (info.source ? '<span class="muted small">' +
        GUI.esc(info.source) + '</span>' : '') + '</div>' +
        '<div class="yf-meta" style="margin:8px 0">' +
        GUI.esc(S.paramMeta(info)) + '</div><table class="doc-values">' +
        '<tr><th>instrument</th><th>' + valueHead + '</th></tr>' +
        insts.map(function (inst) {
            return '<tr><td>' + GUI.esc(inst) + '</td><td class="mono">' +
                GUI.esc(S.docs.valueText(values[inst])) + '</td></tr>';
        }).join('') + '</table><pre class="doc-text">' +
        GUI.esc(info.description || '(no description)') + '</pre>';
};

S.docs.renderGroup = function (group) {
    S.docs.key = null;
    S.docs.section = group;
    var keys = S.docs.matches()[group] || [];
    var box = S.$('docs-detail');
    box.innerHTML = '<h2 class="mono">' + GUI.esc(group) + '</h2><div ' +
        'class="muted small">' + keys.length + ' entries - click a name to ' +
        'show it on its own.</div>' + keys.map(function (key) {
            return '<div class="doc-entry" data-key="' + GUI.esc(key) + '">' +
                S.docs.constHtml(key, 3) + '</div>';
        }).join('');
    box.querySelectorAll('.doc-entry .doc-key').forEach(function (el) {
        el.onclick = function () {
            S.docs.render(el.parentNode.getAttribute('data-key'));
            S.docs.markActive();
        };
    });
    box.scrollTop = 0;
};

S.docs.render = function (key) {
    S.docs.key = key;
    var info = S.params[key];
    var box = S.$('docs-detail');
    if (!info) {
        box.innerHTML = '<p class="muted">Unknown constant ' + GUI.esc(key) +
            '</p>';
        return;
    }
    var group = S.docs.group(key);
    S.docs.section = group;
    var inEdit = S.edit.outline && S.edit.outline.nodes.some(function (n) {
        return n.path.join('.') === key; });
    box.innerHTML = '<div class="doc-crumb"><a id="docs-to-group">' +
        GUI.esc(group) + '</a> &rsaquo;</div>' + S.docs.constHtml(key, 2) +
        (inEdit ? '<button class="primary" id="docs-to-edit">Show in Edit (' +
        GUI.esc(S.edit.name) + ')</button>' : '');
    S.$('docs-to-group').onclick = function () {
        S.docs.renderGroup(group);
        S.docs.markActive();
    };
    var btn = S.$('docs-to-edit');
    if (btn) {
        btn.onclick = function () {
            S.$('edit-filter').value = key;
            GUI.setTab('edit');
            S.edit.renderForm();
        };
    }
};

S.docs.popup = function (key) {
    if (!S.params[key]) { GUI.toast('No description for ' + key, 'bad');
                          return; }
    GUI.dialog({id: 'docs-popup', title: 'Docs: ' + key,
                body: S.docs.constHtml(key, 2),
                buttons: [{label: 'Open in the Docs tab', onclick:
                           function (close) { close(); S.docs.show(key); }},
                          {label: 'Close', cls: 'primary'}]});
};

S.docs.show = function (key) {
    // open the Docs tab on one constant
    GUI.setTab('docs');
    S.docs.setMenu('constants');
    S.$('docs-filter').value = '';
    S.docs.kind = '';
    S.docs.renderList();
    S.docs.render(key);
    S.docs.markActive();
    var el = document.querySelector('.doc-item[data-key="' +
                                    key.replace(/"/g, '\\"') + '"]');
    if (el) { el.scrollIntoView({block: 'center'}); }
};

/* ---- docs: guides (the apero-ri documentation pages) -------------------- */
S.docs.loadGuides = function () {
    if (S.docs.guides.length) { return Promise.resolve(); }
    return GUI.get('api/setup/guides').then(function (data) {
        S.docs.guides = data.guides || [];
        S.docs.renderGuideList();
        if (!S.docs.guide && S.docs.guides.length) {
            S.docs.renderGuide(S.docs.guides[0].ref);
        }
    }).catch(GUI.fail);
};

S.docs.renderGuideList = function () {
    S.$('docs-count').textContent = S.docs.guides.length + ' guide(s) from ' +
        'the APERO documentation';
    S.$('docs-list').innerHTML = S.docs.guides.map(function (g) {
        return '<div class="doc-item' + (g.ref === S.docs.guide ? ' active' :
            '') + '" data-guide="' + GUI.esc(g.ref) + '">' + GUI.esc(g.title) +
            '<div class="muted small">' + GUI.esc(g.ref) + '</div></div>';
    }).join('') || '<p class="muted">The documentation is not available in ' +
        'this installation.</p>';
};

S.docs.openGuide = function (ref) {
    GUI.setTab('docs');
    S.docs.setMenu('guides');
    S.docs.renderGuide(ref);
};

S.docs.renderGuide = function (ref) {
    S.docs.guide = ref;
    GUI.get('api/setup/guide', {ref: ref}).then(function (data) {
        S.$('docs-detail').innerHTML = '<div class="doc-crumb muted small">' +
            GUI.esc(data.path || ref) + '</div><div class="info-md">' +
            data.html + '</div>';
        S.$('docs-detail').scrollTop = 0;
        S.docs.renderGuideList();
    }).catch(GUI.fail);
};

/* ==========================================================================
   start up
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {
    // consoles (one per page) and the processes table
    new GUI.Console('setup', 'console-setup', {
        title: 'Console (apero_setup.py)', onDone: S.setup.done});
    new GUI.Console('edit', 'console-edit', {
        title: 'Console (apero_setup.py --update)', onDone: S.edit.done});
    new GUI.Console('validate', 'console-validate', {
        title: 'Console (apero_validate.py)', onDone: S.loadProfiles});
    new GUI.Console('data', 'console-data', {
        title: 'Console (apero_reset.py)', onDone: S.data.done});
    new GUI.Processes('processes', {tab: 'processes'});
    S.edit.init();
    S.data.init();
    S.docs.init();
    S.setup.init().then(function () {
        // reopen the remembered profiles
        var edit = S.$('edit-profile').value;
        if (edit && GUI.currentTab === 'edit') { S.edit.loadProfile(edit); }
        S.val.updateCli();
    });
    S.docs.loadParams();
    // deep links: #edit:/path, #validate:/path or #data:/path (profile)
    var link = /^#(edit|validate|data):(.+)$/.exec(location.hash);
    if (link) { history.replaceState(null, '', '#' + link[1]); }
    GUI.init('info');
    if (link) {
        var target = decodeURIComponent(link[2]);
        S.loadProfiles().then(function () {
            if (link[1] === 'edit') { S.edit.open(target); }
            else if (link[1] === 'data') { S.data.open(target); }
            else { S.val.open(target); }
        });
    }
});
