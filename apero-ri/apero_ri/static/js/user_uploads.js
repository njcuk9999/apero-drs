/* user_uploads.js – User: My Uploads */
(function () {
    'use strict';

    /* ------------------------------------------------------------------ */
    /* State                                                                */
    /* ------------------------------------------------------------------ */
    var _data = [];   // [{id, name, type, quota, files}]

    /* ------------------------------------------------------------------ */
    /* DOM shortcuts                                                        */
    /* ------------------------------------------------------------------ */
    function $$(id) { return document.getElementById(id); }

    /* ------------------------------------------------------------------ */
    /* Load data                                                            */
    /* ------------------------------------------------------------------ */
    function load() {
        fetch('/api/user/uploads/list')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) return;
                _data = data.directories || [];
                render();
            });
    }

    /* ------------------------------------------------------------------ */
    /* Render all directory sections                                        */
    /* ------------------------------------------------------------------ */
    function render() {
        var container = $$('uu-sections');
        var noDirs    = $$('uu-no-dirs');
        container.innerHTML = '';

        if (!_data.length) {
            noDirs.style.display = '';
            return;
        }
        noDirs.style.display = 'none';

        _data.forEach(function (dir) {
            container.appendChild(buildDirSection(dir));
        });
    }

    function buildDirSection(dir) {
        var section = document.createElement('div');
        section.className = 'at-section-card uu-section';
        section.dataset.dirId = dir.id;

        /* Header */
        var header = document.createElement('div');
        header.className = 'at-section-card__header';
        header.innerHTML =
            '<span class="uu-section-title">' +
                '<i class="fa-solid fa-folder"></i> ' +
                esc(dir.name) +
                (dir.type === 'global'
                    ? ' <span class="uu-type-badge uu-type-badge--global">' +
                        'Global</span>'
                    : ' <span class="uu-type-badge uu-type-badge--peruser">' +
                        'My folder</span>') +
            '</span>' +
            '<button class="ari-btn ari-btn--sm ari-btn--primary uu-upload-btn"' +
                ' data-dir-id="' + esc(dir.id) + '">' +
                '<i class="fa-solid fa-upload"></i> Upload' +
            '</button>';
        section.appendChild(header);

        /* Quota bar */
        var body  = document.createElement('div');
        body.className = 'at-section-card__body';
        body.appendChild(buildQuotaBar(dir.quota, dir.id));

        /* File table */
        var tableWrap = document.createElement('div');
        tableWrap.className = 'uu-table-wrap';
        tableWrap.id = 'uu-table-' + dir.id;
        tableWrap.appendChild(buildFileTable(dir));
        body.appendChild(tableWrap);
        section.appendChild(body);

        /* Wire upload button */
        header.querySelector('.uu-upload-btn')
            .addEventListener('click', function () {
                openUploadModal(dir);
            });

        return section;
    }

    /* ------------------------------------------------------------------ */
    /* Quota bar                                                            */
    /* ------------------------------------------------------------------ */
    function buildQuotaBar(q, dirId) {
        var pct      = Math.min(100, q ? (q.pct || 0) : 0);
        var barClass = pct >= 90 ? 'uu-quota-bar--red'
            : pct >= 80          ? 'uu-quota-bar--yellow'
            : 'uu-quota-bar--green';
        var wrap = document.createElement('div');
        wrap.className = 'uu-quota-wrap';
        wrap.id = 'uu-quota-' + dirId;
        wrap.innerHTML =
            '<div class="uu-quota-label">' +
                '<span>' +
                    (q ? fmtBytes(q.used_bytes) : '0 B') +
                    ' used' +
                '</span>' +
                '<span>' +
                    (q ? q.quota_gb.toFixed(1) : '–') + ' GB quota' +
                '</span>' +
            '</div>' +
            '<div class="uu-quota-track">' +
                '<div class="uu-quota-fill ' + barClass +
                    '" style="width:' + pct + '%">' +
                '</div>' +
            '</div>' +
            '<div class="uu-quota-pct">' + pct.toFixed(1) + '%</div>';
        return wrap;
    }

    function refreshQuotaBar(dirId, q) {
        var wrap = $$('uu-quota-' + dirId);
        if (!wrap) return;
        var pct = Math.min(100, q ? (q.pct || 0) : 0);
        var barClass = pct >= 90 ? 'uu-quota-bar--red'
            : pct >= 80          ? 'uu-quota-bar--yellow'
            : 'uu-quota-bar--green';
        var fill  = wrap.querySelector('.uu-quota-fill');
        var label = wrap.querySelector('.uu-quota-label');
        var pctEl = wrap.querySelector('.uu-quota-pct');
        if (fill) {
            fill.style.width = pct + '%';
            fill.className   = 'uu-quota-fill ' + barClass;
        }
        if (label) {
            label.innerHTML =
                '<span>' + fmtBytes(q ? q.used_bytes : 0) + ' used</span>' +
                '<span>' + (q ? q.quota_gb.toFixed(1) : '–') + ' GB quota</span>';
        }
        if (pctEl) pctEl.textContent = pct.toFixed(1) + '%';
    }

    /* ------------------------------------------------------------------ */
    /* File table                                                           */
    /* ------------------------------------------------------------------ */
    function buildFileTable(dir) {
        var files = dir.files || [];
        if (!files.length) {
            var empty = document.createElement('p');
            empty.className = 'uu-no-files';
            empty.innerHTML = '<i class="fa-solid fa-inbox"></i> ' +
                'No files uploaded yet.';
            return empty;
        }

        var table = document.createElement('table');
        table.className = 'ari-table uu-file-table';
        table.innerHTML =
            '<thead><tr>' +
            '<th>Filename</th>' +
            '<th>Size</th>' +
            '<th>Modified</th>' +
            '<th>Actions</th>' +
            '</tr></thead>';
        var tbody = document.createElement('tbody');
        files.forEach(function (f) {
            tbody.appendChild(buildFileRow(dir.id, f));
        });
        table.appendChild(tbody);
        return table;
    }

    function buildFileRow(dirId, f) {
        var tr = document.createElement('tr');
        tr.id  = 'uu-row-' + dirId + '-' + encodeRow(f.filename);
        var mod = f.modified_iso
            ? new Date(f.modified_iso).toLocaleDateString()
            : '–';
        tr.innerHTML =
            '<td class="uu-fname">' + esc(f.filename) + '</td>' +
            '<td class="uu-fsize">' + fmtBytes(f.size_bytes) + '</td>' +
            '<td class="uu-fmod">'  + esc(mod) + '</td>' +
            '<td class="uu-faction">' +
                '<button class="ari-btn ari-btn--sm ari-btn--secondary' +
                    ' uu-btn-share"' +
                    ' data-dir="' + esc(dirId) + '"' +
                    ' data-file="' + esc(f.filename) + '"' +
                    ' title="Share">' +
                    '<i class="fa-solid fa-share-nodes"></i>' +
                '</button>' +
                ' <button class="ari-btn ari-btn--sm ari-btn--danger' +
                    ' uu-btn-del"' +
                    ' data-dir="' + esc(dirId) + '"' +
                    ' data-file="' + esc(f.filename) + '"' +
                    ' title="Delete">' +
                    '<i class="fa-solid fa-trash"></i>' +
                '</button>' +
            '</td>';

        tr.querySelector('.uu-btn-share').addEventListener('click',
            function () { openShareModal(dirId, f.filename); });
        tr.querySelector('.uu-btn-del').addEventListener('click',
            function () { deleteFile(dirId, f.filename); });
        return tr;
    }

    function refreshDirSection(dirId, files, quota) {
        /* Refresh the file table */
        var wrap = $$('uu-table-' + dirId);
        if (!wrap) return;
        var dir = { id: dirId, files: files };
        wrap.innerHTML = '';
        wrap.appendChild(buildFileTable(dir));
        refreshQuotaBar(dirId, quota);
    }

    function encodeRow(s) {
        return encodeURIComponent(s).replace(/%/g, '_');
    }

    /* ------------------------------------------------------------------ */
    /* Upload modal                                                         */
    /* ------------------------------------------------------------------ */
    function openUploadModal(dir) {
        $$('uu-upload-dir-id').value = dir.id;
        $$('uu-upload-error').style.display  = 'none';
        $$('uu-upload-ok').style.display     = 'none';
        $$('uu-upload-progress').style.display = 'none';
        $$('uu-drop-zone').classList.remove('uu-drop-zone--active');
        $$('uu-file-input').value = '';
        $$('uu-upload-title').innerHTML =
            '<i class="fa-solid fa-upload"></i> Upload to ' + esc(dir.name);
        var q = dir.quota;
        $$('uu-quota-hint').textContent = q
            ? 'Available: ' +
                fmtBytes(Math.max(0,
                    (q.quota_gb * 1024 ** 3) - q.used_bytes
                ))
            : '';
        $$('uu-upload-overlay').style.display = '';
    }

    function closeUploadModal() {
        $$('uu-upload-overlay').style.display = 'none';
    }

    function doUpload(file) {
        var dirId = $$('uu-upload-dir-id').value;
        if (!dirId || !file) return;

        $$('uu-upload-error').style.display  = 'none';
        $$('uu-upload-ok').style.display     = 'none';
        $$('uu-upload-progress').style.display = '';
        $$('uu-progress-bar').style.width = '0%';
        $$('uu-progress-label').textContent  = 'Uploading…';

        var form = new FormData();
        form.append('dir_id', dirId);
        form.append('file', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/user/uploads/upload');

        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                var pct = Math.round(e.loaded / e.total * 100);
                $$('uu-progress-bar').style.width = pct + '%';
                $$('uu-progress-label').textContent =
                    'Uploading… ' + pct + '%';
            }
        });

        xhr.addEventListener('load', function () {
            $$('uu-upload-progress').style.display = 'none';
            var data;
            try { data = JSON.parse(xhr.responseText); }
            catch (e) { data = { success: false, error: 'Parse error' }; }

            if (!data.success) {
                $$('uu-upload-error').textContent =
                    data.error || 'Upload failed';
                $$('uu-upload-error').style.display = '';
                return;
            }
            $$('uu-upload-ok').textContent =
                'Uploaded: ' + data.filename;
            $$('uu-upload-ok').style.display = '';
            $$('uu-file-input').value = '';
            refreshDirSection(dirId, data.files, data.quota);
            /* Update local state */
            var d = _data.find(function (x) { return x.id === dirId; });
            if (d) {
                d.files = data.files;
                d.quota = data.quota;
            }
            setTimeout(function () {
                closeUploadModal();
            }, 1200);
        });

        xhr.addEventListener('error', function () {
            $$('uu-upload-progress').style.display = 'none';
            $$('uu-upload-error').textContent = 'Network error';
            $$('uu-upload-error').style.display = '';
        });

        xhr.send(form);
    }

    /* ------------------------------------------------------------------ */
    /* Delete file                                                          */
    /* ------------------------------------------------------------------ */
    function deleteFile(dirId, filename) {
        if (!confirm('Delete "' + filename + '"?\nThis cannot be undone.')) {
            return;
        }
        fetch('/api/user/uploads/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dir_id: dirId, filename: filename }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                alert('Error: ' + (data.error || 'Delete failed'));
                return;
            }
            refreshDirSection(dirId, data.files, data.quota);
            var d = _data.find(function (x) { return x.id === dirId; });
            if (d) {
                d.files = data.files;
                d.quota = data.quota;
            }
        });
    }

    /* ------------------------------------------------------------------ */
    /* Share modal                                                          */
    /* ------------------------------------------------------------------ */
    function openShareModal(dirId, filename) {
        fetch('/api/user/uploads/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dir_id: dirId, filename: filename }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                alert('Error: ' + (data.error || 'Share failed'));
                return;
            }
            var url = window.location.origin +
                '/uploads/share/' + data.token;
            $$('uu-share-filename').textContent = filename;
            $$('uu-share-url').value = url;
            $$('uu-share-copied').style.display = 'none';
            $$('uu-share-overlay').style.display = '';
        });
    }

    function closeShareModal() {
        $$('uu-share-overlay').style.display = 'none';
    }

    /* ------------------------------------------------------------------ */
    /* Utilities                                                            */
    /* ------------------------------------------------------------------ */
    function esc(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function fmtBytes(b) {
        if (b < 1024)        return b + ' B';
        if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
        if (b < 1024 ** 3)   return (b / (1024 * 1024)).toFixed(1) + ' MB';
        return (b / (1024 ** 3)).toFixed(2) + ' GB';
    }

    /* ------------------------------------------------------------------ */
    /* Bootstrap                                                            */
    /* ------------------------------------------------------------------ */
    document.addEventListener('DOMContentLoaded', function () {
        load();

        /* Upload modal events */
        $$('uu-upload-close').addEventListener('click', closeUploadModal);
        $$('uu-upload-overlay').addEventListener('click', function (e) {
            if (e.target === this) closeUploadModal();
        });

        /* Drag & drop */
        var dropZone   = $$('uu-drop-zone');
        var fileInput  = $$('uu-file-input');

        dropZone.addEventListener('click', function () {
            fileInput.click();
        });
        dropZone.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') fileInput.click();
        });
        fileInput.addEventListener('change', function () {
            if (fileInput.files && fileInput.files[0]) {
                doUpload(fileInput.files[0]);
            }
        });
        dropZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            dropZone.classList.add('uu-drop-zone--active');
        });
        dropZone.addEventListener('dragleave', function () {
            dropZone.classList.remove('uu-drop-zone--active');
        });
        dropZone.addEventListener('drop', function (e) {
            e.preventDefault();
            dropZone.classList.remove('uu-drop-zone--active');
            var file = e.dataTransfer.files && e.dataTransfer.files[0];
            if (file) doUpload(file);
        });

        /* Share modal events */
        $$('uu-share-close').addEventListener('click', closeShareModal);
        $$('uu-share-overlay').addEventListener('click', function (e) {
            if (e.target === this) closeShareModal();
        });
        $$('uu-share-copy').addEventListener('click', function () {
            var input = $$('uu-share-url');
            input.select();
            try {
                navigator.clipboard.writeText(input.value).then(
                    function () {
                        $$('uu-share-copied').style.display = '';
                        setTimeout(function () {
                            $$('uu-share-copied').style.display = 'none';
                        }, 2000);
                    }
                );
            } catch (e) {
                document.execCommand('copy');
            }
        });
    });
}());
