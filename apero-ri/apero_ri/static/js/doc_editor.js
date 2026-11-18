/* APERO RI – Documentation Editor */
document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.getElementById('editor-textarea');
    var preview = document.getElementById('editor-preview');
    var saveBtn = document.getElementById('editor-save');
    var uploadInput = document.getElementById('image-upload-input');
    var conf = window.ARI_EDITOR;

    if (!textarea || !preview || !conf) return;

    // Configure marked for rendering
    marked.setOptions({
        gfm: true,
        breaks: false,
        highlight: function (code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, {language: lang}).value;
            }
            return hljs.highlightAuto(code).value;
        }
    });

    // ----------------------------------------------------------------
    // Live preview
    // ----------------------------------------------------------------
    function updatePreview() {
        preview.innerHTML = marked.parse(textarea.value);
    }

    // Debounce preview to avoid lag on large docs
    var previewTimer = null;
    textarea.addEventListener('input', function () {
        clearTimeout(previewTimer);
        previewTimer = setTimeout(updatePreview, 200);
    });

    // Initial render
    updatePreview();

    // ----------------------------------------------------------------
    // Toolbar actions
    // ----------------------------------------------------------------
    function wrapSelection(before, after) {
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var sel = textarea.value.substring(start, end);
        var replacement = before + (sel || 'text') + after;
        textarea.setRangeText(replacement, start, end, 'select');
        textarea.focus();
        updatePreview();
    }

    function insertAtCursor(text) {
        var start = textarea.selectionStart;
        textarea.setRangeText(text, start, start, 'end');
        textarea.focus();
        updatePreview();
    }

    function prependLines(prefix) {
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var val = textarea.value;
        // Find line boundaries
        var lineStart = val.lastIndexOf('\n', start - 1) + 1;
        var lineEnd = val.indexOf('\n', end);
        if (lineEnd === -1) lineEnd = val.length;
        var lines = val.substring(lineStart, lineEnd).split('\n');
        var result = lines.map(function (l) { return prefix + l; }).join('\n');
        textarea.setRangeText(result, lineStart, lineEnd, 'select');
        textarea.focus();
        updatePreview();
    }

    var actions = {
        bold: function () { wrapSelection('**', '**'); },
        italic: function () { wrapSelection('*', '*'); },
        strikethrough: function () { wrapSelection('~~', '~~'); },
        h1: function () { prependLines('# '); },
        h2: function () { prependLines('## '); },
        h3: function () { prependLines('### '); },
        code: function () { wrapSelection('`', '`'); },
        codeblock: function () { wrapSelection('\n```\n', '\n```\n'); },
        quote: function () { prependLines('> '); },
        ul: function () { prependLines('- '); },
        ol: function () {
            var start = textarea.selectionStart;
            var end = textarea.selectionEnd;
            var val = textarea.value;
            var lineStart = val.lastIndexOf('\n', start - 1) + 1;
            var lineEnd = val.indexOf('\n', end);
            if (lineEnd === -1) lineEnd = val.length;
            var lines = val.substring(lineStart, lineEnd).split('\n');
            var result = lines.map(function (l, i) {
                return (i + 1) + '. ' + l;
            }).join('\n');
            textarea.setRangeText(result, lineStart, lineEnd, 'select');
            textarea.focus();
            updatePreview();
        },
        link: function () {
            var sel = textarea.value.substring(
                textarea.selectionStart, textarea.selectionEnd
            ) || 'link text';
            wrapSelection('[', '](url)');
        },
        image: function () {
            insertAtCursor('![alt text](/doc-images/filename.png)');
        },
        upload: function () {
            uploadInput.click();
        },
        table: function () {
            insertAtCursor(
                '\n| Header 1 | Header 2 | Header 3 |\n' +
                '|----------|----------|----------|\n' +
                '| Cell 1   | Cell 2   | Cell 3   |\n' +
                '| Cell 4   | Cell 5   | Cell 6   |\n'
            );
        },
        hr: function () { insertAtCursor('\n---\n'); }
    };

    // Bind toolbar buttons
    document.querySelectorAll('.ari-editor-toolbar__btn[data-action]').forEach(
        function (btn) {
            btn.addEventListener('click', function () {
                var action = btn.getAttribute('data-action');
                if (actions[action]) actions[action]();
            });
        }
    );

    // Keyboard shortcuts
    textarea.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            actions.bold();
        } else if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
            e.preventDefault();
            actions.italic();
        } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            doSave();
        } else if (e.key === 'Tab') {
            e.preventDefault();
            insertAtCursor('    ');
        }
    });

    // ----------------------------------------------------------------
    // Image upload
    // ----------------------------------------------------------------
    uploadInput.addEventListener('change', function () {
        var file = uploadInput.files[0];
        if (!file) return;

        var formData = new FormData();
        formData.append('image', file);
        formData.append('page_ref', conf.docRef);

        fetch(conf.uploadUrl, {
            method: 'POST',
            body: formData
        })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
            if (data.success) {
                insertAtCursor('![' + data.filename + '](/doc-images/' + data.filename + ')');
            } else {
                alert('Upload failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(function (err) {
            alert('Upload failed: ' + err.message);
        });

        // Reset input so same file can be uploaded again
        uploadInput.value = '';
    });

    // ----------------------------------------------------------------
    // Save
    // ----------------------------------------------------------------
    function doSave() {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

        fetch(conf.saveUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                version: conf.versionId,
                content: textarea.value
            })
        })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
            if (data.success) {
                window.location.href = conf.viewUrl;
            } else {
                alert('Save failed: ' + (data.error || 'Unknown error'));
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save';
            }
        })
        .catch(function (err) {
            alert('Save failed: ' + err.message);
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save';
        });
    }

    saveBtn.addEventListener('click', doSave);
});
