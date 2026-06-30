#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Small Flask app used for first-run APERO RI setup."""

import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

from apero_ri.core import auth
from apero_ri.core import email_backend as eb
from apero_ri.core.permissions import load_parameters
from apero_ri.setup.bootstrap import (
    ensure_directory_layout,
    is_setup_complete,
    load_setup_state,
    save_bootstrap_config,
    save_setup_state,
)
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.setup.setup_app"

PACKAGE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

USERNAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,63}$")


# =============================================================================
# Define classes
# =============================================================================
class SetupApp(Flask):
    """Flask app for first-run setup."""

    def __init__(self, local_data_dir: Path, test_mode: bool = False, **kwargs):
        super().__init__(
            __name__,
            template_folder=str(TEMPLATE_DIR),
            static_folder=str(STATIC_DIR),
            **kwargs,
        )
        self.local_data_dir = Path(local_data_dir).expanduser()
        self.test_mode = test_mode
        self.secret_key = secrets.token_hex(32)
        self.config["SESSION_COOKIE_NAME"] = "apero_ri_setup"
        self.config["SESSION_COOKIE_HTTPONLY"] = True
        self.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        auth.set_ari_dir(str(self.local_data_dir))
        self._register_context_processors()
        self._register_routes()

    @staticmethod
    def _normalize_data_dir(raw_path: str) -> Path:
        """Normalize a local data directory path for setup use."""
        text = str(raw_path or "").strip()
        if not text:
            return (Path.home() / ".ari").expanduser().resolve()
        return Path(text).expanduser().resolve()

    def _set_local_data_dir(self, new_dir: Path) -> None:
        """Switch setup runtime to a new local data directory."""
        self.local_data_dir = Path(new_dir).expanduser().resolve()
        os.environ["ARI_DIR"] = str(self.local_data_dir)
        auth.set_ari_dir(str(self.local_data_dir))

    def _completed_step(self) -> int:
        """Compute wizard completion progress for tab lock/unlock state."""
        completed = 1
        email_cfg = eb.load_email_config()
        if self._email_configured(email_cfg):
            completed = 2
        state = load_setup_state(self.local_data_dir)
        if str(state.get("admin_username", "")).strip():
            completed = 3
        if bool(state.get("completed", False)):
            completed = 4
        return completed

    def _register_context_processors(self) -> None:
        @self.context_processor
        def inject_setup_context() -> Dict[str, object]:
            email_cfg = eb.load_email_config()
            state = load_setup_state(self.local_data_dir)
            active_routes = {
                "setup_welcome",
                "setup_email",
                "setup_admin",
                "setup_complete",
            }
            active_step = (
                request.endpoint
                if request.endpoint in active_routes
                else "setup_welcome"
            )
            return {
                "local_data_dir": str(self.local_data_dir),
                "provider_defaults": eb.PROVIDER_DEFAULTS,
                "setup_email_configured": self._email_configured(email_cfg),
                "setup_complete": bool(state.get("completed", False)),
                "setup_admin_username": state.get("admin_username", ""),
                "active_step": active_step,
                "completed_step": self._completed_step(),
                "test_mode": self.test_mode,
            }

    def _register_routes(self) -> None:
        self.add_url_rule("/", "setup_index", self._index)
        self.add_url_rule(
            "/welcome",
            "setup_welcome",
            self._welcome_step,
            methods=["GET", "POST"],
        )
        self.add_url_rule(
            "/email", "setup_email", self._email_step, methods=["GET", "POST"]
        )
        self.add_url_rule(
            "/admin", "setup_admin", self._admin_step, methods=["GET", "POST"]
        )
        self.add_url_rule("/complete", "setup_complete", self._complete_step)
        self.add_url_rule(
            "/api/browse-dirs", "setup_browse_dirs", self._browse_dirs
        )

    @staticmethod
    def _split_list(raw_value: str) -> List[str]:
        values = []
        for item in raw_value.replace("\n", ",").split(","):
            cleaned = item.strip()
            if cleaned and cleaned not in values:
                values.append(cleaned)
        return values

    @staticmethod
    def _email_configured(email_cfg: Dict[str, object]) -> bool:
        if not email_cfg:
            return False
        if not email_cfg.get("enabled", False):
            return False
        provider = str(email_cfg.get("provider", "")).strip().lower()
        if provider == "log":
            return True
        return bool(str(email_cfg.get("smtp_user", "")).strip())

    @staticmethod
    def _build_email_config(form_data) -> Dict[str, object]:
        provider = str(form_data.get("provider", "gmail")).strip().lower()
        defaults = eb.PROVIDER_DEFAULTS.get(
            provider, eb.PROVIDER_DEFAULTS["custom"]
        )
        port_text = str(
            form_data.get("smtp_port", defaults.get("smtp_port", 587))
        ).strip()
        try:
            smtp_port = int(port_text or defaults.get("smtp_port", 587))
        except ValueError:
            smtp_port = int(defaults.get("smtp_port", 587))
        cfg = {
            "enabled": True,
            "provider": provider,
            "from_address": str(form_data.get("from_address", "")).strip(),
            "smtp_host": (
                str(form_data.get("smtp_host", "")).strip()
                or defaults.get("smtp_host", "")
            ),
            "smtp_port": smtp_port,
            "smtp_ssl": bool(form_data.get("smtp_ssl")),
            "smtp_tls": bool(form_data.get("smtp_tls")),
            "smtp_user": str(form_data.get("smtp_user", "")).strip(),
        }

        if provider != "custom":
            cfg["smtp_host"] = defaults.get("smtp_host", cfg["smtp_host"])
            cfg["smtp_port"] = defaults.get("smtp_port", cfg["smtp_port"])
            cfg["smtp_ssl"] = defaults.get("smtp_ssl", cfg["smtp_ssl"])
            cfg["smtp_tls"] = defaults.get("smtp_tls", cfg["smtp_tls"])

        raw_password = str(form_data.get("smtp_password", "")).strip()
        if raw_password:
            cfg["smtp_password"] = raw_password
        else:
            existing_cfg = eb.load_email_config()
            existing_pw = str(existing_cfg.get("smtp_password_enc", "")).strip()
            if existing_pw:
                cfg["smtp_password_enc"] = existing_pw
        return cfg

    @staticmethod
    def _all_instruments() -> List[str]:
        """Return the configured instrument list from parameters.yaml."""
        params = load_parameters()
        values = params.get("instruments", {}).get("value", [])
        if not isinstance(values, list):
            return []
        return [str(item) for item in values if str(item).strip()]

    def _index(self):
        if is_setup_complete(self.local_data_dir):
            return redirect(url_for("setup_complete"))
        return redirect(url_for("setup_welcome"))

    def _welcome_step(self):
        if request.method == "POST":
            target_dir = self._normalize_data_dir(
                request.form.get("local_data_dir", "")
            )
            try:
                if self.test_mode:
                    flash(
                        "[TEST MODE] Local data directory accepted "
                        "but not created.",
                        "success",
                    )
                else:
                    ensure_directory_layout(target_dir)
                    save_bootstrap_config(str(target_dir))
                    flash(
                        f"Local data directory set to: {target_dir}", "success"
                    )
                self._set_local_data_dir(target_dir)
                session.pop("setup_pending_admin", None)
                return redirect(url_for("setup_email"))
            except Exception as exc:
                flash(f"Could not use local data directory: {exc}", "error")
                return render_template(
                    "setup/welcome.html",
                    page_title="Setup Welcome",
                    selected_dir=str(target_dir),
                )

        return render_template(
            "setup/welcome.html",
            page_title="Setup Welcome",
            selected_dir=str(self.local_data_dir),
        )

    def _browse_dirs(self):
        """Return a list of sub-directories for server-side path browsing."""
        raw_path = str(request.args.get("path", "") or "").strip()
        if not raw_path:
            current = self.local_data_dir
        else:
            try:
                current = Path(raw_path).expanduser().resolve()
            except Exception:
                current = self.local_data_dir

        if not current.exists():
            fallback = (
                current.parent if current.parent.exists() else Path.home()
            )
            current = fallback
        if current.exists() and not current.is_dir():
            current = current.parent

        dirs = []
        try:
            for child in sorted(
                current.iterdir(), key=lambda item: item.name.lower()
            ):
                if child.is_dir():
                    dirs.append(
                        {
                            "name": child.name,
                            "path": str(child),
                        }
                    )
        except Exception:
            dirs = []

        return jsonify(
            success=True,
            path=str(current),
            parent=str(current.parent),
            dirs=dirs[:500],
        )

    def _email_step(self):
        email_cfg = eb.load_email_config()
        if request.method == "POST":
            cfg = self._build_email_config(request.form)
            provider = str(cfg.get("provider", "")).strip().lower()
            if (
                not str(cfg.get("from_address", "")).strip()
                and provider != "log"
            ):
                flash("From address is required.", "error")
                return render_template(
                    "setup/email.html", page_title="Setup Email", email_cfg=cfg
                )
            if provider != "log" and not str(cfg.get("smtp_user", "")).strip():
                flash("SMTP username is required.", "error")
                return render_template(
                    "setup/email.html", page_title="Setup Email", email_cfg=cfg
                )

            if self.test_mode:
                flash(
                    "[TEST MODE] Email config validated but NOT saved.",
                    "success",
                )
                return redirect(url_for("setup_admin"))

            eb.save_email_config(dict(cfg))
            test_result = eb.test_email_connection(eb.load_email_config())
            if not test_result.get("ok", False):
                flash(
                    f"Email settings saved, but connection test failed: {
                        test_result.get(
                            'error',
                            'unknown error')}",
                    "error",
                )
                return render_template(
                    "setup/email.html", page_title="Setup Email", email_cfg=cfg
                )

            flash("Email settings saved and verified.", "success")
            return redirect(url_for("setup_admin"))

        if not email_cfg:
            email_cfg = {
                "enabled": True,
                "provider": "gmail",
                "smtp_host": eb.PROVIDER_DEFAULTS["gmail"]["smtp_host"],
                "smtp_port": eb.PROVIDER_DEFAULTS["gmail"]["smtp_port"],
                "smtp_ssl": eb.PROVIDER_DEFAULTS["gmail"]["smtp_ssl"],
                "smtp_tls": eb.PROVIDER_DEFAULTS["gmail"]["smtp_tls"],
                "from_address": "",
                "smtp_user": "",
            }
        return render_template(
            "setup/email.html", page_title="Setup Email", email_cfg=email_cfg
        )

    def _admin_step(self):
        email_cfg = eb.load_email_config()
        if not self._email_configured(email_cfg):
            flash(
                "Configure email before creating the initial admin account.",
                "error",
            )
            return redirect(url_for("setup_email"))

        users = auth.load_users()
        pending = session.get("setup_pending_admin")

        if request.method == "POST":
            action = str(request.form.get("action", "send_code")).strip()
            if action == "verify_code":
                if not pending:
                    flash(
                        "No pending verification request. Start again.", "error"
                    )
                    return redirect(url_for("setup_admin"))
                entered_code = str(
                    request.form.get("verification_code", "")
                ).strip()
                if entered_code != str(pending.get("code", "")):
                    flash("Invalid verification code.", "error")
                    return render_template(
                        "setup/admin.html",
                        page_title="Create Initial Admin",
                        form_data=pending,
                        pending_verification=True,
                        existing_user=bool(pending.get("existing_user")),
                    )
                expires_at = str(pending.get("expires_at", "")).strip()
                if not expires_at or datetime.now(
                    timezone.utc
                ) > datetime.fromisoformat(expires_at):
                    session.pop("setup_pending_admin", None)
                    flash(
                        "Verification code expired. Request a new one.", "error"
                    )
                    return redirect(url_for("setup_admin"))

                username = pending["username"]
                existing_user = users.get(username, {})
                created_at = existing_user.get(
                    "created_at", datetime.now(timezone.utc).isoformat()
                )
                last_login = existing_user.get("last_login")
                configured_instruments = self._all_instruments()
                existing_instruments = existing_user.get("instruments", [])
                if not isinstance(existing_instruments, list):
                    existing_instruments = []
                instruments = sorted(
                    set(configured_instruments) | set(existing_instruments)
                )
                users[username] = {
                    "password": pending["password_hash"],
                    "groups": ["super_admin"],
                    "instruments": instruments,
                    "first_names": pending["first_names"],
                    "last_name": pending["last_name"],
                    "emails": pending["emails"],
                    "primary_email": pending["primary_email"],
                    "email_verified": True,
                    "institutions": pending["institutions"],
                    "primary_institution": pending["primary_institution"],
                    "created_at": created_at,
                    "last_login": last_login,
                }
                if self.test_mode:
                    session.pop("setup_pending_admin", None)
                    flash(
                        "[TEST MODE] Admin account validated but NOT saved.",
                        "success",
                    )
                    return redirect(url_for("setup_complete"))
                auth.save_users(users)
                save_setup_state(
                    self.local_data_dir, username, email_configured=True
                )
                session.pop("setup_pending_admin", None)
                flash(
                    "Initial admin account verified and setup completed.",
                    "success",
                )
                return redirect(url_for("setup_complete"))

            username = str(request.form.get("username", "")).strip()
            first_names = str(request.form.get("first_names", "")).strip()
            last_name = str(request.form.get("last_name", "")).strip()
            emails = self._split_list(
                str(request.form.get("emails", "")).strip()
            )
            institutions = self._split_list(
                str(request.form.get("institutions", "")).strip()
            )
            password = str(request.form.get("password", ""))
            password_confirm = str(request.form.get("password_confirm", ""))
            existing_user = users.get(username, {})

            form_data = {
                "username": username,
                "first_names": first_names,
                "last_name": last_name,
                "emails": ", ".join(emails),
                "institutions": ", ".join(institutions),
            }

            if not USERNAME_RE.match(username):
                flash(
                    "Username must use lowercase letters, numbers, "
                    "or underscore only.",
                    "error",
                )
                return render_template(
                    "setup/admin.html",
                    page_title="Create Initial Admin",
                    form_data=form_data,
                    pending_verification=False,
                    existing_user=bool(existing_user),
                )
            if not first_names or not last_name:
                flash("First name(s) and last name are required.", "error")
                return render_template(
                    "setup/admin.html",
                    page_title="Create Initial Admin",
                    form_data=form_data,
                    pending_verification=False,
                    existing_user=bool(existing_user),
                )
            if not emails:
                flash("At least one email address is required.", "error")
                return render_template(
                    "setup/admin.html",
                    page_title="Create Initial Admin",
                    form_data=form_data,
                    pending_verification=False,
                    existing_user=bool(existing_user),
                )
            if not institutions:
                flash("At least one institution is required.", "error")
                return render_template(
                    "setup/admin.html",
                    page_title="Create Initial Admin",
                    form_data=form_data,
                    pending_verification=False,
                    existing_user=bool(existing_user),
                )

            if password or password_confirm:
                if password != password_confirm:
                    flash("Passwords do not match.", "error")
                    return render_template(
                        "setup/admin.html",
                        page_title="Create Initial Admin",
                        form_data=form_data,
                        pending_verification=False,
                        existing_user=bool(existing_user),
                    )
                if len(password) < 8:
                    flash("Password must be at least 8 characters.", "error")
                    return render_template(
                        "setup/admin.html",
                        page_title="Create Initial Admin",
                        form_data=form_data,
                        pending_verification=False,
                        existing_user=bool(existing_user),
                    )
                password_hash = auth.hash_password(password)
            else:
                existing_password = str(
                    existing_user.get("password", "")
                ).strip()
                if not existing_password:
                    flash(
                        "Provide a password for a new admin account.", "error"
                    )
                    return render_template(
                        "setup/admin.html",
                        page_title="Create Initial Admin",
                        form_data=form_data,
                        pending_verification=False,
                        existing_user=bool(existing_user),
                    )
                password_hash = existing_password

            code = f"{secrets.randbelow(1_000_000):06d}"
            err = eb.send_verification_email(
                emails[0], code, "initial admin setup"
            )
            if err:
                flash(f"Failed to send verification code: {err}", "error")
                return render_template(
                    "setup/admin.html",
                    page_title="Create Initial Admin",
                    form_data=form_data,
                    pending_verification=False,
                    existing_user=bool(existing_user),
                )

            pending = {
                "username": username,
                "first_names": first_names,
                "last_name": last_name,
                "emails": emails,
                "primary_email": emails[0],
                "institutions": institutions,
                "primary_institution": institutions[0],
                "password_hash": password_hash,
                "code": code,
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(minutes=15)
                ).isoformat(),
                "existing_user": bool(existing_user),
            }
            session["setup_pending_admin"] = pending
            flash(
                "Verification code sent. Enter it below to finish setup.",
                "success",
            )
            return render_template(
                "setup/admin.html",
                page_title="Create Initial Admin",
                form_data=pending,
                pending_verification=True,
                existing_user=bool(existing_user),
            )

        form_data = {}
        existing_user = False
        if pending:
            form_data = pending
            existing_user = bool(pending.get("existing_user"))
            return render_template(
                "setup/admin.html",
                page_title="Create Initial Admin",
                form_data=form_data,
                pending_verification=True,
                existing_user=existing_user,
            )

        preferred = users.get("njcuk9999", {})
        if preferred and auth.user_has_admin_privileges(
            preferred.get("groups", [])
        ):
            form_data = {
                "username": "njcuk9999",
                "first_names": preferred.get("first_names", ""),
                "last_name": preferred.get("last_name", ""),
                "emails": ", ".join(
                    preferred.get("emails", [])
                    or [preferred.get("primary_email", "")]
                ),
                "institutions": ", ".join(
                    preferred.get("institutions", [])
                    or [preferred.get("primary_institution", "")]
                ),
            }
            existing_user = True
        return render_template(
            "setup/admin.html",
            page_title="Create Initial Admin",
            form_data=form_data,
            pending_verification=False,
            existing_user=existing_user,
        )

    def _complete_step(self):
        state = load_setup_state(self.local_data_dir)
        email_cfg = eb.load_email_config()
        return render_template(
            "setup/complete.html",
            page_title="Setup Complete",
            setup_state=state,
            email_cfg=email_cfg,
        )


# =============================================================================
# Define functions
# =============================================================================
def create_setup_app(local_data_dir: Path, test_mode: bool = False) -> SetupApp:
    """Factory for the first-run setup app."""
    return SetupApp(local_data_dir, test_mode=test_mode)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
