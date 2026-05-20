"""User account and password reset helper functions for ARIApp."""

import secrets
from datetime import datetime, timedelta, timezone

from apero_ri.core import email_backend as eb
from apero_ri.core.auth import (
    hash_password,
    load_users,
    save_users,
    verify_password,
)
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def api_auth_register_start(app):
    """Start user registration by sending a 6-digit verification code."""
    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    username = str(data.get("username", "")).strip()
    first_names = str(data.get("first_names", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    password = str(data.get("password", ""))
    password_confirm = str(data.get("password_confirm", ""))

    emails_raw = data.get("emails", [])
    institutions_raw = data.get("institutions", [])
    if isinstance(emails_raw, str):
        emails_raw = [emails_raw]
    if isinstance(institutions_raw, str):
        institutions_raw = [institutions_raw]

    emails = [str(e).strip() for e in emails_raw if str(e).strip()]
    institutions = [str(i).strip() for i in institutions_raw if str(i).strip()]

    if not app._is_valid_username(username):
        return (
            jsonify(
                success=False,
                error=(
                    "Username must be 3+ chars, lowercase, and use "
                    "only letters, numbers, or underscore (_)."
                ),
            ),
            400,
        )
    if not first_names or not last_name:
        return (
            jsonify(
                success=False, error="First name(s) and last name are required."
            ),
            400,
        )
    if not emails:
        return (
            jsonify(success=False, error="At least one email is required."),
            400,
        )
    if not institutions:
        return (
            jsonify(
                success=False, error="At least one institution is required."
            ),
            400,
        )
    if password != password_confirm:
        return jsonify(success=False, error="Passwords do not match."), 400
    if len(password) < 8:
        return (
            jsonify(
                success=False, error="Password must be at least 8 characters."
            ),
            400,
        )

    users = load_users()
    if username in users:
        return jsonify(success=False, error="Username already exists."), 409

    # Reject registration if any supplied email is already registered
    existing_emails = set()
    for udata in users.values():
        stored = udata.get('emails') or []
        if isinstance(stored, str):
            stored = [stored]
        for addr in stored:
            existing_emails.add(str(addr).lower().strip())
    for addr in emails:
        if addr.lower() in existing_emails:
            return (
                jsonify(
                    success=False,
                    error=(
                        f"The email address {addr!r} is already "
                        "associated with another account."
                    ),
                ),
                409,
            )

    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = (
        (datetime.now(timezone.utc) + timedelta(minutes=15))
    ).isoformat()

    err = app._send_verification_email(emails[0], code, "registration")
    if err:
        return (
            jsonify(
                success=False, error=f"Failed to send verification email: {err}"
            ),
            500,
        )

    session["pending_registration"] = {
        "username": username,
        "first_names": first_names,
        "last_name": last_name,
        "emails": emails,
        "primary_email": emails[0],
        "institutions": institutions,
        "primary_institution": institutions[0],
        "password_hash": hash_password(password),
        "code": code,
        "expires_at": expires_at,
    }
    return jsonify(success=True)


def api_auth_register_verify(app):
    """Verify registration code and create user account."""
    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    pending = session.get("pending_registration")
    if not pending:
        return (
            jsonify(success=False, error="No pending registration found."),
            400,
        )

    code = str(data.get("code", "")).strip()
    if code != str(pending.get("code", "")):
        return jsonify(success=False, error="Invalid verification code."), 400

    exp = pending.get("expires_at")
    if not exp or datetime.now(timezone.utc) > datetime.fromisoformat(exp):
        session.pop("pending_registration", None)
        return (
            jsonify(
                success=False, error="Verification code expired. Start again."
            ),
            400,
        )

    username = pending["username"]
    users = load_users()
    if username in users:
        session.pop("pending_registration", None)
        return jsonify(success=False, error="Username already exists."), 409

    users[username] = {
        "password": pending["password_hash"],
        "groups": ["public"],
        "instruments": [],
        "first_names": pending["first_names"],
        "last_name": pending["last_name"],
        "emails": pending["emails"],
        "primary_email": pending["primary_email"],
        "email_verified": True,
        "institutions": pending["institutions"],
        "primary_institution": pending["primary_institution"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login": None,
    }
    save_users(users)

    session.pop("pending_registration", None)
    session["user"] = username
    session["last_login"] = None
    session.pop("login_as", None)
    return jsonify(success=True)


def forgot_password_view(app):
    """Request a password reset email without revealing account existence."""
    if request.method == "POST":
        ip = app._get_request_ip()
        wait_seconds = app._register_forgot_pw_attempt(ip)
        if wait_seconds is not None:
            flash(
                "Too many password reset attempts from this IP. "
                f"Please wait {wait_seconds}s before trying again.",
                "warning",
            )
            return redirect(url_for("forgot_password"))

        identifier = str(request.form.get("identifier", "")).strip()
        generic_msg = (
            "If an account matches that username/email, "
            "a reset link has been sent."
        )

        users = load_users()
        changed = app._cleanup_expired_reset_tokens(users)
        identifier_l = identifier.lower()

        matched_username = None
        recipient_email = ""

        if identifier:
            for username, user in users.items():
                if username.lower() == identifier_l:
                    matched_username = username
                    recipient_email = app._get_primary_contact_email(user)
                    break

            if matched_username is None:
                for username, user in users.items():
                    emails = user.get("emails", [])
                    if not isinstance(emails, list):
                        emails = []
                    primary = str(user.get("primary_email", "")).strip()
                    candidates = [e for e in emails if str(e).strip()]
                    if primary:
                        candidates.append(primary)
                    if any(
                        str(e).strip().lower() == identifier_l
                        for e in candidates
                    ):
                        matched_username = username
                        recipient_email = (
                            primary or app._get_primary_contact_email(user)
                        )
                        break

        if matched_username and recipient_email:
            token = secrets.token_urlsafe(32)
            expires_at = (
                datetime.now(timezone.utc) + timedelta(minutes=30)
            ).isoformat()
            users[matched_username]["password_reset"] = {
                "token_hash": hash_password(token),
                "expires_at": expires_at,
                "requested_at": datetime.now(timezone.utc).isoformat(),
            }
            changed = True

            reset_link = url_for("reset_password", token=token, _external=True)
            subject = "APERO RI password reset request"
            body = (
                "A request was received to reset your APERO RI password.\n\n"
                "Use this link to set a new password "
                f"(valid for 30 minutes):\n{reset_link}\n\n"
                "If you did not request this, you can ignore this email."
            )
            err = eb.send_email(recipient_email, subject, body)
            if err:
                print(
                    f"Password reset email failed for {matched_username}: {err}"
                )

        if changed:
            save_users(users)

        flash(generic_msg, "info")
        return redirect(url_for("forgot_password"))

    return render_template(
        "home/forgot_password.html",
        page_label="Forgot Password",
        page_icon="fa-solid fa-key",
    )


def api_user_account_update(app):
    """Update account fields except primary email change verification."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    username = user_info["username"]
    users = load_users()
    if username not in users:
        return jsonify(success=False, error="User not found"), 404
    user = users[username]

    first_names = str(data.get("first_names", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    emails_raw = data.get("emails", [])
    institutions_raw = data.get("institutions", [])
    primary_institution = str(data.get("primary_institution", "")).strip()

    if isinstance(emails_raw, str):
        emails_raw = [emails_raw]
    if isinstance(institutions_raw, str):
        institutions_raw = [institutions_raw]

    emails = [str(e).strip() for e in emails_raw if str(e).strip()]
    institutions = [str(i).strip() for i in institutions_raw if str(i).strip()]

    if not first_names or not last_name:
        return (
            jsonify(
                success=False, error="First name(s) and last name are required."
            ),
            400,
        )
    if not emails:
        return (
            jsonify(success=False, error="At least one email is required."),
            400,
        )
    if not institutions:
        return (
            jsonify(
                success=False, error="At least one institution is required."
            ),
            400,
        )
    if not primary_institution:
        return (
            jsonify(success=False, error="Primary institution is required."),
            400,
        )
    if primary_institution not in institutions:
        return (
            jsonify(
                success=False,
                error="Primary institution must be in institutions list.",
            ),
            400,
        )

    primary_email = user.get("primary_email", emails[0])
    if primary_email not in emails:
        emails.insert(0, primary_email)

    user["first_names"] = first_names
    user["last_name"] = last_name
    user["emails"] = emails
    user["institutions"] = institutions
    user["primary_institution"] = primary_institution

    current_password = str(data.get("current_password", ""))
    new_password = str(data.get("new_password", ""))
    confirm_password = str(data.get("confirm_password", ""))
    if current_password or new_password or confirm_password:
        if not (current_password and new_password and confirm_password):
            return (
                jsonify(
                    success=False,
                    error="Fill all password fields to change password.",
                ),
                400,
            )
        if not verify_password(current_password, user.get("password", "")):
            return (
                jsonify(success=False, error="Current password is incorrect."),
                400,
            )
        if new_password != confirm_password:
            return (
                jsonify(success=False, error="New passwords do not match."),
                400,
            )
        if len(new_password) < 8:
            return (
                jsonify(
                    success=False,
                    error="New password must be at least 8 characters.",
                ),
                400,
            )
        user["password"] = hash_password(new_password)

    users[username] = user
    save_users(users)
    return jsonify(success=True)


def api_user_account_request_primary_email(app):
    """Send a verification code to confirm a new primary email address."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    new_email = str(data.get("new_primary_email", "")).strip()
    if not new_email or "@" not in new_email or " " in new_email:
        return (
            jsonify(
                success=False, error="Valid new_primary_email is required."
            ),
            400,
        )

    username = user_info["username"]
    users = load_users()
    user = users.get(username)
    if not user:
        return jsonify(success=False, error="User not found"), 404

    current_primary = str(user.get("primary_email", "")).strip()
    if new_email.lower() == current_primary.lower():
        return jsonify(success=True, already_primary=True)

    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=15)
    ).isoformat()

    err = app._send_verification_email(new_email, code, "primary_email_change")
    if err:
        return (
            jsonify(
                success=False, error=f"Failed to send verification email: {err}"
            ),
            500,
        )

    session["pending_primary_email_change"] = {
        "username": username,
        "new_primary_email": new_email,
        "code": code,
        "expires_at": expires_at,
    }
    return jsonify(success=True)


def api_user_account_confirm_primary_email(app):
    """Verify code and update the user's primary email."""
    user_info = app._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    pending = session.get("pending_primary_email_change")
    if not pending:
        return (
            jsonify(success=False, error="No pending primary email change."),
            400,
        )

    if str(pending.get("username", "")) != str(user_info.get("username", "")):
        session.pop("pending_primary_email_change", None)
        return (
            jsonify(
                success=False, error="Pending primary email change is invalid."
            ),
            400,
        )

    code = str(data.get("code", "")).strip()
    if code != str(pending.get("code", "")):
        return jsonify(success=False, error="Invalid verification code."), 400

    exp = pending.get("expires_at")
    if not exp or datetime.now(timezone.utc) > datetime.fromisoformat(exp):
        session.pop("pending_primary_email_change", None)
        return (
            jsonify(
                success=False,
                error="Verification code expired. Request a new one.",
            ),
            400,
        )

    username = user_info["username"]
    users = load_users()
    user = users.get(username)
    if not user:
        session.pop("pending_primary_email_change", None)
        return jsonify(success=False, error="User not found"), 404

    new_email = str(pending.get("new_primary_email", "")).strip()
    emails = user.get("emails", []) or []
    emails = [str(e).strip() for e in emails if str(e).strip()]
    if new_email and new_email not in emails:
        emails.insert(0, new_email)
    user["emails"] = emails
    user["primary_email"] = new_email
    user["email_verified"] = True
    users[username] = user
    save_users(users)

    session.pop("pending_primary_email_change", None)
    return jsonify(success=True)


def register_forgot_pw_attempt(app, ip: str):
    """Record forgot-password attempt and return wait seconds if blocked."""
    now_ts = datetime.now(timezone.utc).timestamp()
    app._prune_forgot_pw_rate_limit(now_ts)

    state = app._forgot_pw_rate_limit.get(
        ip,
        {
            "attempts": 0,
            "penalty": 0,
            "blocked_until": 0.0,
            "last_seen": 0.0,
        },
    )

    blocked_until = float(state.get("blocked_until", 0.0) or 0.0)
    if now_ts < blocked_until:
        remaining = int(blocked_until - now_ts + 0.999)
        state["last_seen"] = now_ts
        app._forgot_pw_rate_limit[ip] = state
        return max(1, remaining)

    last_seen = float(state.get("last_seen", 0.0) or 0.0)
    if last_seen and (now_ts - last_seen) > 600.0:
        state["attempts"] = 0
        state["penalty"] = 0

    state["attempts"] = int(state.get("attempts", 0) or 0) + 1
    state["last_seen"] = now_ts

    if state["attempts"] > app._forgot_pw_max_attempts:
        penalty = int(state.get("penalty", 0) or 0) + 1
        wait_seconds = min(
            app._forgot_pw_base_wait * (2 ** (penalty - 1)),
            app._forgot_pw_max_wait,
        )
        state["penalty"] = penalty
        state["attempts"] = 0
        state["blocked_until"] = now_ts + float(wait_seconds)
        app._forgot_pw_rate_limit[ip] = state
        return int(wait_seconds)

    state["blocked_until"] = 0.0
    app._forgot_pw_rate_limit[ip] = state
    return None
