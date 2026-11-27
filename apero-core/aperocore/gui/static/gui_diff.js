/* ==========================================================================
   aperocore gui - side by side diff viewer

   GUI.renderDiff(container, data, opts) draws a two pane diff (see
   aperocore.gui.diff.side_by_side): line numbers, removed / added /
   changed lines coloured, changed characters highlighted, folded equal
   regions (click to expand) and next / previous change navigation.

   GUI.showDiff(opts) asks the server for the diff of two files or texts
   and shows it in a (wide) dialog; extra footer buttons (e.g. "Save")
   can be added with opts.buttons.
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

GUI.diffSpans = function (text, spans, cls) {
    // escape a line and wrap the changed character spans
    if (text === null || text === undefined) { return ''; }
    if (!spans || spans.length === 0) { return GUI.esc(text); }
    var out = '';
    var last = 0;
    spans.forEach(function (span) {
        out += GUI.esc(text.slice(last, span[0]));
        out += '<span class="' + cls + '">' +
            GUI.esc(text.slice(span[0], span[1])) + '</span>';
        last = span[1];
    });
    return out + GUI.esc(text.slice(last));
};

GUI.diffRowHtml = function (row, index) {
    // one table row of the diff
    if (row.tag === 'fold') {
        return '<tr class="fold" data-fold="' + index + '"><td colspan="5">' +
            '&#8597; ' + row.count + ' unchanged line(s) (from line ' +
            row.lstart + ') - click to show</td></tr>';
    }
    return '<tr class="' + row.tag + '" data-row="' + index + '">' +
        '<td class="ln">' + (row.lno || '') + '</td>' +
        '<td class="dt l">' + GUI.diffSpans(row.ltext, row.lspans, 'dl') +
        '</td><td class="sep"></td><td class="ln">' + (row.rno || '') +
        '</td><td class="dt r">' + GUI.diffSpans(row.rtext, row.rspans, 'da') +
        '</td></tr>';
};

GUI.renderDiff = function (container, data, opts) {
    opts = opts || {};
    var state = {current: -1, wrap: GUI.recall('diff-wrap', false)};
    var stats = data.stats;
    var html = '<div class="diff-toolbar"><span class="diff-stats">' +
        (data.identical ? '<span class="pill ok">identical</span>' :
         '<span class="add">+' + stats.added + '</span> added &nbsp; ' +
         '<span class="del">-' + stats.removed + '</span> removed &nbsp; ' +
         '<span class="mod">~' + stats.changed + '</span> changed') +
        '</span><span style="flex:1"></span>' +
        '<span class="muted small" data-role="pos"></span>' +
        '<button class="small" data-act="prev">&#9650; Previous change' +
        '</button><button class="small" data-act="next">&#9660; Next change' +
        '</button><button class="small" data-act="wrap">Wrap</button>' +
        (opts.foldable === false ? '' : '<button class="small" ' +
         'data-act="unfold">Expand all</button>') + '</div>' +
        '<div class="diff-names"><div title="' + GUI.esc(data.left_name) +
        '">&#9664; ' + GUI.esc(opts.leftLabel || data.left_name) + '</div>' +
        '<div title="' + GUI.esc(data.right_name) + '">&#9654; ' +
        GUI.esc(opts.rightLabel || data.right_name) + '</div></div>' +
        '<div class="diff-view"><table class="diff-table">' +
        // fixed layout takes its widths from the columns (not the first
        //   row, which may be a folded row spanning every column)
        '<colgroup><col class="c-ln"><col class="c-dt"><col class="c-sep">' +
        '<col class="c-ln"><col class="c-dt"></colgroup><tbody>' +
        data.rows.map(GUI.diffRowHtml).join('') + '</tbody></table>' +
        (data.rows.length === 0 ? '<div class="diff-empty">Both files are ' +
         'empty</div>' : '') + '</div>';
    container.innerHTML = html;
    var table = container.querySelector('.diff-table');
    var view = container.querySelector('.diff-view');
    table.classList.toggle('wrap', state.wrap);
    // expand folds on click
    var expand = function (tr) {
        var index = Number(tr.getAttribute('data-fold'));
        var fold = data.rows[index];
        var tmp = document.createElement('tbody');
        tmp.innerHTML = fold.rows.map(function (row) {
            return GUI.diffRowHtml(row, -1);
        }).join('');
        while (tmp.firstChild) { tr.parentNode.insertBefore(tmp.firstChild,
                                                            tr); }
        tr.remove();
    };
    table.addEventListener('click', function (ev) {
        var tr = ev.target.closest('tr.fold');
        if (tr) { expand(tr); }
    });
    var go = function (dir) {
        if (data.changes.length === 0) { return; }
        state.current = (state.current + dir + data.changes.length) %
            data.changes.length;
        var target = table.querySelector('tr[data-row="' +
                                         data.changes[state.current] + '"]');
        table.querySelectorAll('tr.current').forEach(function (tr) {
            tr.classList.remove('current');
        });
        if (target) {
            target.classList.add('current');
            view.scrollTop = target.offsetTop - view.clientHeight / 3;
        }
        container.querySelector('[data-role="pos"]').textContent =
            'change ' + (state.current + 1) + ' / ' + data.changes.length;
    };
    container.querySelector('[data-act="prev"]').onclick = function () {
        go(-1); };
    container.querySelector('[data-act="next"]').onclick = function () {
        go(1); };
    container.querySelector('[data-act="wrap"]').onclick = function () {
        state.wrap = !state.wrap;
        GUI.store('diff-wrap', state.wrap);
        table.classList.toggle('wrap', state.wrap);
    };
    var unfold = container.querySelector('[data-act="unfold"]');
    if (unfold) {
        unfold.onclick = function () {
            table.querySelectorAll('tr.fold').forEach(expand);
        };
    }
    container.querySelector('[data-role="pos"]').textContent =
        data.changes.length + ' change block(s)';
    // keyboard: F7 / Shift+F7 like IDEs, also n / p
    container.tabIndex = 0;
    container.onkeydown = function (ev) {
        if (ev.key === 'F7' || ev.key === 'n') {
            ev.preventDefault(); go(ev.shiftKey ? -1 : 1);
        } else if (ev.key === 'p') { go(-1); }
    };
    if (data.changes.length > 0 && opts.jumpFirst !== false) {
        setTimeout(function () { go(1); }, 30);
    }
};

GUI.showDiff = function (opts) {
    // opts = {left, right, any, left_text, right_text, left_name,
    //         right_name, title, leftLabel, rightLabel, context, buttons}
    var req = {left: opts.left, right: opts.right, any: opts.any ? 1 : 0,
               context: opts.context === undefined ? 4 : opts.context};
    if (opts.left_text !== undefined) {
        req.left_text = opts.left_text;
        req.left_name = opts.left_name || 'left';
    }
    if (opts.right_text !== undefined) {
        req.right_text = opts.right_text;
        req.right_name = opts.right_name || 'right';
    }
    return GUI.post('api/diff', req).then(function (data) {
        var dlg = GUI.dialog({id: 'diff-dialog', wide: true,
                              title: opts.title || 'Compare files',
                              body: '<div id="diff-holder" style="display:' +
                                    'flex;flex-direction:column;height:100%">' +
                                    '</div>',
                              buttons: opts.buttons});
        var holder = dlg.querySelector('#diff-holder');
        GUI.renderDiff(holder, data, opts);
        holder.focus();
        return data;
    }).catch(GUI.fail);
};
