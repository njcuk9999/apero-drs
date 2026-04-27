/* ==========================================================================
   Comments & Groups tab logic for the object page.
   Depends on window.ARI_OBJECT_PAGE being set before this runs.
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_PAGE || {};

    /* ── DOM refs ────────────────────────────────────────────────── */
    var commentsLoading = document.getElementById(
        'op-cg-comments-loading'
    );
    var commentsError = document.getElementById(
        'op-cg-comments-error'
    );
    var commentsList = document.getElementById(
        'op-cg-comments-list'
    );
    var commentsEmpty = document.getElementById(
        'op-cg-comments-empty'
    );
    var commentCount = document.getElementById(
        'op-cg-comment-count'
    );
    var commentInput = document.getElementById(
        'op-cg-comment-input'
    );
    var commentSubmit = document.getElementById(
        'op-cg-comment-submit'
    );

    var groupsLoading = document.getElementById(
        'op-cg-groups-loading'
    );
    var groupsError = document.getElementById(
        'op-cg-groups-error'
    );
    var groupsList = document.getElementById(
        'op-cg-groups-list'
    );
    var groupsEmpty = document.getElementById(
        'op-cg-groups-empty'
    );
    var groupSelect = document.getElementById(
        'op-cg-group-select'
    );
    var groupAddBtn = document.getElementById(
        'op-cg-group-add-btn'
    );
    var groupNewBtn = document.getElementById(
        'op-cg-group-new-btn'
    );
    var groupsPageLink = document.getElementById(
        'op-cg-groups-page-link'
    );

    var commentsLoaded = false;
    var groupsLoaded = false;
    var currentComments = [];
    var editingCommentId = null;

    /* ── Wire the groups page link ──────────────────────────────── */
    if (groupsPageLink && cfg.objectGroupsPageUrl) {
        groupsPageLink.href = cfg.objectGroupsPageUrl;
    }

    /* ── Helpers ─────────────────────────────────────────────────── */
    function hide(el) {
        if (el) el.style.display = 'none';
    }
    function show(el) {
        if (el) el.style.display = '';
    }
    function esc(text) {
        var d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }
    function timeAgo(iso) {
        if (!iso) return '';
        var d = new Date(iso);
        var now = new Date();
        var sec = Math.floor((now - d) / 1000);
        if (sec < 60) return 'just now';
        var min = Math.floor(sec / 60);
        if (min < 60) return min + 'm ago';
        var hr = Math.floor(min / 60);
        if (hr < 24) return hr + 'h ago';
        var day = Math.floor(hr / 24);
        if (day < 30) return day + 'd ago';
        return d.toLocaleDateString();
    }
    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(function (r) { return r.json(); });
    }
    function getJson(url) {
        return fetch(url).then(function (r) {
            return r.json();
        });
    }

    /* ================================================================
       COMMENTS
       ================================================================ */
    function loadComments() {
        hide(commentsError);
        hide(commentsEmpty);
        hide(commentsList);
        show(commentsLoading);

        var url = cfg.commentsListApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId) +
            '&objname=' +
            encodeURIComponent(cfg.objname);

        getJson(url).then(function (data) {
            hide(commentsLoading);
            if (!data.success) {
                commentsError.textContent = data.error ||
                    'Failed to load comments.';
                show(commentsError);
                return;
            }
            commentsLoaded = true;
            currentComments = data.comments || [];
            renderComments(currentComments);
        }).catch(function () {
            hide(commentsLoading);
            commentsError.textContent =
                'Network error loading comments.';
            show(commentsError);
        });
    }

    function renderComments(items) {
        if (!items.length) {
            hide(commentsList);
            show(commentsEmpty);
            commentCount.textContent = '';
            return;
        }
        hide(commentsEmpty);
        commentCount.textContent = String(items.length);

        var html = '';
        items.forEach(function (c) {
            var isEditing = (editingCommentId === c.id);
            html += '<div class="op-cg-comment-card"' +
                ' data-comment-id="' + esc(c.id) + '">';
            html += '<div class="op-cg-comment-meta">';
            html += '<strong>' + esc(c.username) + '</strong>';
            html += ' &middot; ' + esc(timeAgo(c.created_at));
            if (c.updated_at && c.updated_at !== c.created_at) {
                html += ' <em>(edited)</em>';
            }
            html += '<span class="op-cg-comment-actions">';
            if (c.can_edit) {
                html += ' <button class="ari-btn ari-btn--sm' +
                    ' ari-btn--secondary op-cg-edit-btn"' +
                    ' data-id="' + esc(c.id) + '"' +
                    ' title="Edit">' +
                    '<i class="fa-solid fa-pen"></i></button>';
            }
            if (c.can_delete) {
                html += ' <button class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger op-cg-delete-btn"' +
                    ' data-id="' + esc(c.id) + '"' +
                    ' title="Delete">' +
                    '<i class="fa-solid fa-trash"></i></button>';
            }
            html += '</span>';
            html += '</div>';

            if (isEditing) {
                html += '<textarea class="ari-input' +
                    ' op-cg-edit-textarea"' +
                    ' rows="3">' + esc(c.comment) +
                    '</textarea>';
                html += '<div style="margin-top:0.3rem;">';
                html += '<button class="ari-btn ari-btn--sm' +
                    ' ari-btn--primary op-cg-save-edit-btn"' +
                    ' data-id="' + esc(c.id) + '">' +
                    '<i class="fa-solid fa-check"></i>' +
                    ' Save</button>';
                html += ' <button class="ari-btn ari-btn--sm' +
                    ' ari-btn--secondary' +
                    ' op-cg-cancel-edit-btn">' +
                    'Cancel</button>';
                html += '</div>';
            } else {
                html += '<div class="op-cg-comment-body">' +
                    esc(c.comment) + '</div>';
            }

            html += '</div>';
        });
        commentsList.innerHTML = html;
        show(commentsList);
        wireCommentButtons();
    }

    function wireCommentButtons() {
        commentsList.querySelectorAll(
            '.op-cg-edit-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                editingCommentId = btn.dataset.id;
                renderComments(currentComments);
            });
        });
        commentsList.querySelectorAll(
            '.op-cg-cancel-edit-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                editingCommentId = null;
                renderComments(currentComments);
            });
        });
        commentsList.querySelectorAll(
            '.op-cg-save-edit-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                var cid = btn.dataset.id;
                var card = btn.closest('.op-cg-comment-card');
                var ta = card.querySelector(
                    '.op-cg-edit-textarea'
                );
                var text = ta ? ta.value.trim() : '';
                if (!text) return;
                btn.disabled = true;
                postJson(cfg.commentsEditApiUrl, {
                    profile_id: cfg.profileId,
                    objname: cfg.objname,
                    comment_id: cid,
                    comment: text,
                }).then(function (data) {
                    btn.disabled = false;
                    editingCommentId = null;
                    if (data.success) {
                        loadComments();
                    } else {
                        alert(data.error ||
                            'Failed to edit comment.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
        commentsList.querySelectorAll(
            '.op-cg-delete-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (!confirm(
                    'Delete this comment?'
                )) return;
                var cid = btn.dataset.id;
                btn.disabled = true;
                postJson(cfg.commentsDeleteApiUrl, {
                    profile_id: cfg.profileId,
                    objname: cfg.objname,
                    comment_id: cid,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadComments();
                    } else {
                        alert(data.error ||
                            'Failed to delete comment.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* Post new comment */
    if (commentSubmit) {
        commentSubmit.addEventListener('click', function () {
            var text = commentInput.value.trim();
            if (!text) return;
            commentSubmit.disabled = true;
            postJson(cfg.commentsAddApiUrl, {
                profile_id: cfg.profileId,
                objname: cfg.objname,
                comment: text,
            }).then(function (data) {
                commentSubmit.disabled = false;
                if (data.success) {
                    commentInput.value = '';
                    loadComments();
                } else {
                    alert(data.error ||
                        'Failed to add comment.');
                }
            }).catch(function () {
                commentSubmit.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* ================================================================
       GROUPS (object membership on the object page)
       ================================================================ */
    function loadGroupsForObject() {
        hide(groupsError);
        hide(groupsEmpty);
        hide(groupsList);
        show(groupsLoading);

        var url = cfg.groupsForObjectApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId) +
            '&objname=' +
            encodeURIComponent(cfg.objname);

        getJson(url).then(function (data) {
            hide(groupsLoading);
            if (!data.success) {
                groupsError.textContent = data.error ||
                    'Failed to load groups.';
                show(groupsError);
                return;
            }
            groupsLoaded = true;
            renderObjectGroups(
                data.member_groups || [],
                data.all_groups || [],
                data.can_moderate || false
            );
        }).catch(function () {
            hide(groupsLoading);
            groupsError.textContent =
                'Network error loading groups.';
            show(groupsError);
        });
    }

    function renderObjectGroups(
        memberGroups, allGroups, canModerate
    ) {
        /* Populate select with groups the object is NOT in */
        if (groupSelect) {
            groupSelect.innerHTML =
                '<option value="">-- select group --</option>';
            allGroups.forEach(function (name) {
                if (memberGroups.indexOf(name) === -1) {
                    var opt = document.createElement('option');
                    opt.value = name;
                    opt.textContent = name;
                    groupSelect.appendChild(opt);
                }
            });
        }

        /* Show member groups */
        if (!memberGroups.length) {
            hide(groupsList);
            show(groupsEmpty);
            return;
        }
        hide(groupsEmpty);
        var html = '';
        memberGroups.forEach(function (name) {
            html += '<span class="ari-tag">';
            html += '<i class="fa-solid fa-layer-group"></i> ';
            html += esc(name);
            if (canModerate) {
                html += ' <button class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger' +
                    ' op-cg-remove-from-group"' +
                    ' data-group="' + esc(name) + '"' +
                    ' title="Remove from group">' +
                    '<i class="fa-solid fa-xmark"></i>' +
                    '</button>';
            }
            html += '</span> ';
        });
        groupsList.innerHTML = html;
        show(groupsList);

        /* Wire remove buttons */
        groupsList.querySelectorAll(
            '.op-cg-remove-from-group'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                var grp = btn.dataset.group;
                btn.disabled = true;
                postJson(cfg.groupsRemoveObjectApiUrl, {
                    profile_id: cfg.profileId,
                    group: grp,
                    objname: cfg.objname,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadGroupsForObject();
                    } else {
                        alert(data.error ||
                            'Failed to remove.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* Add to group button */
    if (groupAddBtn) {
        groupAddBtn.addEventListener('click', function () {
            var name = groupSelect.value;
            if (!name) return;
            groupAddBtn.disabled = true;
            postJson(cfg.groupsAddObjectApiUrl, {
                profile_id: cfg.profileId,
                group: name,
                objname: cfg.objname,
            }).then(function (data) {
                groupAddBtn.disabled = false;
                if (data.success) {
                    loadGroupsForObject();
                } else {
                    alert(data.error || 'Failed to add.');
                }
            }).catch(function () {
                groupAddBtn.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* New group button */
    if (groupNewBtn) {
        groupNewBtn.addEventListener('click', function () {
            var name = prompt('Enter new group name:');
            if (!name || !name.trim()) return;
            groupNewBtn.disabled = true;
            postJson(cfg.groupsCreateApiUrl, {
                profile_id: cfg.profileId,
                name: name.trim(),
            }).then(function (data) {
                groupNewBtn.disabled = false;
                if (data.success) {
                    loadGroupsForObject();
                } else {
                    alert(data.error ||
                        'Failed to create group.');
                }
            }).catch(function () {
                groupNewBtn.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* ================================================================
       Tab activation hook — lazy-load on first show
       ================================================================ */
    document.addEventListener('ARI_TAB_ACTIVATED',
        function (e) {
            var key = (e.detail || {}).tabKey;
            if (key !== 'comments_groups') return;
            if (!commentsLoaded) loadComments();
            if (!groupsLoaded) loadGroupsForObject();
        }
    );
}());
