(function () {
    'use strict';

    var cfg = window.ARI_ACCOUNT;

    var username = document.getElementById('acc-username');
    var firstNames = document.getElementById('acc-first-names');
    var lastName = document.getElementById('acc-last-name');
    var primaryEmail = document.getElementById('acc-primary-email');
    var emailsWrap = document.getElementById('acc-emails');
    var instWrap = document.getElementById('acc-inst');
    var primaryInst = document.getElementById('acc-primary-inst');

    var currentPass = document.getElementById('acc-current-password');
    var newPass = document.getElementById('acc-new-password');
    var confirmPass = document.getElementById('acc-confirm-password');

    var addEmailBtn = document.getElementById('acc-add-email');
    var addInstBtn = document.getElementById('acc-add-inst');
    var requestPrimaryBtn = document.getElementById('acc-request-primary');
    var confirmPrimaryBtn = document.getElementById('acc-confirm-primary');
    var primaryVerifyBox = document.getElementById('acc-primary-verify');
    var primaryCode = document.getElementById('acc-primary-code');
    var saveBtn = document.getElementById('acc-save');

    var toast = document.getElementById('acc-toast');

    function showToast(msg, type) {
        toast.textContent = msg;
        toast.className = 'ari-toast ari-toast--' + (type || 'info');
        toast.style.display = 'block';
        clearTimeout(toast._t);
        toast._t = setTimeout(function () { toast.style.display = 'none'; }, 3000);
    }

    function makeRow(value, placeholder) {
        var row = document.createElement('div');
        row.style.display = 'flex';
        row.style.gap = '0.5rem';
        row.style.marginBottom = '0.4rem';

        var inp = document.createElement('input');
        inp.type = 'text';
        inp.className = 'ari-ap-input';
        inp.placeholder = placeholder;
        inp.value = value || '';

        var del = document.createElement('button');
        del.type = 'button';
        del.className = 'ari-btn ari-btn--secondary ari-btn--sm';
        del.innerHTML = '<i class="fa-solid fa-xmark"></i>';
        del.addEventListener('click', function () {
            if (row.parentNode.children.length <= 1) return;
            row.parentNode.removeChild(row);
            refreshPrimaryInstitutionSelect();
        });

        row.appendChild(inp);
        row.appendChild(del);
        return row;
    }

    function getValues(wrap) {
        return Array.prototype.slice.call(wrap.querySelectorAll('input'))
            .map(function (el) { return el.value.trim(); })
            .filter(Boolean);
    }

    function refreshPrimaryInstitutionSelect(preferred) {
        var values = getValues(instWrap);
        primaryInst.innerHTML = '';
        values.forEach(function (v) {
            var opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            primaryInst.appendChild(opt);
        });
        if (!values.length) {
            var opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No institutions';
            primaryInst.appendChild(opt);
            primaryInst.value = '';
            return;
        }
        if (preferred && values.indexOf(preferred) >= 0) primaryInst.value = preferred;
        else primaryInst.value = values[0];
    }

    function populate(data) {
        username.value = data.username || '';
        firstNames.value = data.first_names || '';
        lastName.value = data.last_name || '';
        primaryEmail.value = data.primary_email || '';

        emailsWrap.innerHTML = '';
        (data.emails || ['']).forEach(function (e) {
            emailsWrap.appendChild(makeRow(e, 'email@example.org'));
        });

        instWrap.innerHTML = '';
        (data.institutions || ['']).forEach(function (i) {
            instWrap.appendChild(makeRow(i, 'Institution name'));
        });
        refreshPrimaryInstitutionSelect(data.primary_institution || '');
    }

    function loadAccount() {
        fetch(cfg.getUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    showToast(data.error || 'Failed to load account', 'error');
                    return;
                }
                populate(data.account || {});
            })
            .catch(function () { showToast('Failed to load account', 'error'); });
    }

    addEmailBtn.addEventListener('click', function () {
        emailsWrap.appendChild(makeRow('', 'other.email@example.org'));
    });

    addInstBtn.addEventListener('click', function () {
        instWrap.appendChild(makeRow('', 'Other institution'));
        refreshPrimaryInstitutionSelect(primaryInst.value);
    });

    instWrap.addEventListener('input', function () {
        refreshPrimaryInstitutionSelect(primaryInst.value);
    });

    requestPrimaryBtn.addEventListener('click', function () {
        requestPrimaryBtn.disabled = true;
        fetch(cfg.requestPrimaryUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_primary_email: primaryEmail.value.trim() })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            requestPrimaryBtn.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Failed to send code', 'error');
                return;
            }
            primaryVerifyBox.style.display = '';
            showToast('Verification code sent.', 'success');
        })
        .catch(function () {
            requestPrimaryBtn.disabled = false;
            showToast('Request failed', 'error');
        });
    });

    confirmPrimaryBtn.addEventListener('click', function () {
        confirmPrimaryBtn.disabled = true;
        fetch(cfg.confirmPrimaryUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: primaryCode.value.trim() })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            confirmPrimaryBtn.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Primary email verification failed', 'error');
                return;
            }
            primaryVerifyBox.style.display = 'none';
            primaryCode.value = '';
            showToast('Primary email updated.', 'success');
            loadAccount();
        })
        .catch(function () {
            confirmPrimaryBtn.disabled = false;
            showToast('Request failed', 'error');
        });
    });

    saveBtn.addEventListener('click', function () {
        saveBtn.disabled = true;
        fetch(cfg.updateUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_names: firstNames.value.trim(),
                last_name: lastName.value.trim(),
                emails: getValues(emailsWrap),
                institutions: getValues(instWrap),
                primary_institution: primaryInst.value,
                current_password: currentPass.value,
                new_password: newPass.value,
                confirm_password: confirmPass.value
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            saveBtn.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Save failed', 'error');
                return;
            }
            currentPass.value = '';
            newPass.value = '';
            confirmPass.value = '';
            showToast('Account updated.', 'success');
            loadAccount();
        })
        .catch(function () {
            saveBtn.disabled = false;
            showToast('Save failed', 'error');
        });
    });

    loadAccount();
})();
