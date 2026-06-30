(function () {
    'use strict';

    var cfg = window.ARI_REGISTER;
    var step1 = document.getElementById('register-step-1');
    var step2 = document.getElementById('register-step-2');

    var username = document.getElementById('reg-username');
    var firstNames = document.getElementById('reg-first-names');
    var lastName = document.getElementById('reg-last-name');
    var password = document.getElementById('reg-password');
    var password2 = document.getElementById('reg-password2');

    var emailsWrap = document.getElementById('reg-emails');
    var instWrap = document.getElementById('reg-institutions');
    var addEmailBtn = document.getElementById('reg-add-email');
    var addInstBtn = document.getElementById('reg-add-inst');

    var submitBtn = document.getElementById('reg-submit');
    var verifyBtn = document.getElementById('reg-verify');
    var codeInput = document.getElementById('reg-code');
    var toast = document.getElementById('reg-toast');

    function showToast(msg, type) {
        toast.textContent = msg;
        toast.className = 'ari-toast ari-toast--' + (type || 'info');
        toast.style.display = 'block';
        clearTimeout(toast._t);
        toast._t = setTimeout(function () { toast.style.display = 'none'; }, 3000);
    }

    function makeRow(placeholder) {
        var row = document.createElement('div');
        row.style.display = 'flex';
        row.style.gap = '0.5rem';
        row.style.marginBottom = '0.4rem';

        var inp = document.createElement('input');
        inp.type = 'text';
        inp.className = 'ari-ap-input';
        inp.placeholder = placeholder;

        var del = document.createElement('button');
        del.type = 'button';
        del.className = 'ari-btn ari-btn--secondary ari-btn--sm';
        del.innerHTML = '<i class="fa-solid fa-xmark"></i>';
        del.addEventListener('click', function () {
            if (row.parentNode.children.length <= 1) return;
            row.parentNode.removeChild(row);
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

    function initRows() {
        emailsWrap.innerHTML = '';
        instWrap.innerHTML = '';
        emailsWrap.appendChild(makeRow('email@example.org'));
        instWrap.appendChild(makeRow('Institution name'));
    }

    addEmailBtn.addEventListener('click', function () {
        emailsWrap.appendChild(makeRow('other.email@example.org'));
    });

    addInstBtn.addEventListener('click', function () {
        instWrap.appendChild(makeRow('Other institution'));
    });

    submitBtn.addEventListener('click', function () {
        var payload = {
            username: username.value.trim(),
            first_names: firstNames.value.trim(),
            last_name: lastName.value.trim(),
            emails: getValues(emailsWrap),
            institutions: getValues(instWrap),
            password: password.value,
            password_confirm: password2.value
        };

        submitBtn.disabled = true;
        fetch(cfg.startUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            submitBtn.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Registration failed', 'error');
                return;
            }
            showToast('Verification code sent to your primary email.', 'success');
            step1.style.display = 'none';
            step2.style.display = '';
            codeInput.focus();
        })
        .catch(function () {
            submitBtn.disabled = false;
            showToast('Request failed', 'error');
        });
    });

    verifyBtn.addEventListener('click', function () {
        verifyBtn.disabled = true;
        fetch(cfg.verifyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: codeInput.value.trim() })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            verifyBtn.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Verification failed', 'error');
                return;
            }
            showToast('Account created. Redirecting...', 'success');
            setTimeout(function () { window.location.href = cfg.homeUrl; }, 700);
        })
        .catch(function () {
            verifyBtn.disabled = false;
            showToast('Request failed', 'error');
        });
    });

    initRows();
})();
