"""ARIApp extracted implementation functions.

This module contains function bodies delegated from ARIApp methods in
apero_ri.application.application.
"""

import argparse
import atexit
import json
import os
import re
import secrets
import smtplib
import socket
import threading
import time
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfoNotFoundError

import yaml
from apero_ri.application import (
    admin_backup_api_helpers,
    admin_cache_helpers,
    admin_health_helpers,
    admin_sshfs_api_helpers,
    admin_user_api_helpers,
    apero_profiles_api_helpers,
    async_task_helpers,
    async_tasks_api_helpers,
    basket_api_helpers,
    data_portal_api_helpers,
    data_portal_view_helpers,
    db_tunnel_api_helpers,
    doc_views_helpers,
    page_view_helpers,
    profile_utils,
    query_db_api_helpers,
    query_helpers,
)
from apero_ri.application import routes as app_routes
from apero_ri.application import sci_groups_api_helpers
from apero_ri.application import sidebar as app_sidebar
from apero_ri.application import (
    user_account_api_helpers,
    user_context_helpers,
    user_db_access_api_helpers,
    user_favourites_api_helpers,
    user_pins_api_helpers,
)
from apero_ri.core import api_tokens as at
from apero_ri.core import audit_log
from apero_ri.core import health_history
from apero_ri.core import auth
from apero_ri.core import backup_backend as bb
from apero_ri.core import basket_funcs as bk
from apero_ri.core import docs
from apero_ri.core import download_tracker as dt
from apero_ri.core import email_backend as eb
from apero_ri.core import object_funcs
from apero_ri.core import permissions as perms
from apero_ri.core import secret_store as ss
from apero_ri.core import sshfs_backend as sb
from apero_ri.core import task_runner
from apero_ri.core import upload_data as upd
from apero_ri.core import user_data as ud
from apero_ri.core.log import configure_logging, get_logger
from apero_ri.tasks import apero_async

log = get_logger(__name__)
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

permissions_mod = perms

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.application.application"
PACKAGE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

_SIDEBAR_CTX_CACHE_LOCK = threading.Lock()
_SIDEBAR_CTX_CACHE = dict()
_SIDEBAR_CTX_CACHE_TTL_S = 20.0


def _heal_duplicated_template(text: str) -> Optional[str]:
    """Best-effort repair of a duplicated/corrupted Jinja template.

    A specific corruption keeps recurring on this codebase: a stale
    editor buffer saves a file that contains its full prior content
    appended after the current content, so the file ends up with two
    ``{% extends ... %}`` tags and duplicate top-level ``{% block %}``
    declarations. Jinja then refuses to compile and the page 500s.

    Heuristic:
      * If two or more ``{% extends ... %}`` tags are present, treat the
        text from the *second* one onwards as garbage and discard it.
      * Otherwise, if any top-level block name appears more than once,
        keep the first occurrence and drop subsequent duplicates.

    Returns the healed text, or None if no repair was possible / needed.
    """
    extends_re = re.compile(r"{%-?\s*extends\b[^%]*%}")
    block_open_re = re.compile(
        r"{%-?\s*block\s+([A-Za-z_][\w]*)\s*-?%}")
    block_close_re = re.compile(r"{%-?\s*endblock\b[^%]*%}")
    extends_hits = list(extends_re.finditer(text))
    healed = None
    if len(extends_hits) >= 2:
        cut = extends_hits[1].start()
        healed = text[:cut].rstrip() + "\n"
    candidate = healed if healed is not None else text
    # Now drop duplicate top-level blocks (depth-aware).
    seen = set()
    out: List[str] = []
    i = 0
    depth = 0
    n = len(candidate)
    while i < n:
        m_open = block_open_re.match(candidate, i)
        m_close = block_close_re.match(candidate, i) if depth else None
        if m_open and depth == 0:
            name = m_open.group(1)
            # Walk forward to the matching {% endblock %} to grab the
            # whole block. Track nested {% block %}.
            j = m_open.end()
            d2 = 1
            while j < n and d2 > 0:
                no = block_open_re.match(candidate, j)
                nc = block_close_re.match(candidate, j)
                if no:
                    d2 += 1
                    j = no.end()
                elif nc:
                    d2 -= 1
                    j = nc.end()
                else:
                    j += 1
            if name in seen:
                # Skip this duplicate block entirely.
                healed = healed if healed is not None else text
                i = j
                # also swallow a trailing newline so we don't leave a gap
                if i < n and candidate[i] == '\n':
                    i += 1
                continue
            seen.add(name)
            out.append(candidate[i:j])
            i = j
            continue
        out.append(candidate[i])
        i += 1
    final = ''.join(out)
    if healed is None and final == text:
        return None
    return final


def _install_self_healing_loader(loader):
    """Wrap a Jinja loader so ``get_source`` runs through the healer.

    We monkey-patch the bound ``get_source`` on the loader instance
    rather than subclassing because Flask has already constructed the
    loader for us. Jinja's ``BaseLoader.load`` calls
    ``self.get_source(env, template)``, so monkey-patching the bound
    method is enough — and avoids the wrapper-class pitfall where
    ``load`` (inherited from the unwrapped inner) bypasses the
    wrapper's ``get_source``.
    """
    if getattr(loader, "_apero_ri_self_healing", False):
        return loader
    original = loader.get_source

    def get_source(environment, template):
        source, filename, uptodate = original(environment, template)
        healed = _heal_duplicated_template(source)
        if healed is None or healed == source:
            return source, filename, uptodate
        import sys as _sys
        print(
            f"[apero_ri] AUTO-HEAL: repaired duplicated template "
            f"{template!r} (size {len(source)} -> {len(healed)} "
            f"bytes); rewriting on disk.",
            file=_sys.stderr,
            flush=True,
        )
        if filename:
            try:
                p = Path(filename)
                tmp = p.with_name(p.name + ".heal-tmp")
                with open(tmp, "w", encoding="utf-8") as fio:
                    fio.write(healed)
                os.replace(tmp, p)
            except OSError as exc:
                print(
                    f"[apero_ri] AUTO-HEAL: failed to rewrite "
                    f"{filename}: {exc}",
                    file=_sys.stderr,
                    flush=True,
                )
        return healed, filename, uptodate

    loader.get_source = get_source
    loader._apero_ri_self_healing = True
    return loader


def _check_template_duplicate_blocks(template_dir: Path) -> List[str]:
    """Scan every Jinja template for duplicate ``{% block <name> %}``.

    Jinja raises ``TemplateAssertionError: block '<name>' defined twice``
    only at render time, so a corrupted template (e.g. accidentally
    duplicated content from an editor or codegen accident) goes
    undetected until a user hits that page. We catch this at server
    startup by scanning all .html templates and reporting offenders, so
    the bug is visible in the boot log instead of only on a 500 page.

    Returns a list of human-readable messages describing each offender.
    """
    import re as _re

    block_re = _re.compile(r"{%-?\s*block\s+([A-Za-z_][\w]*)\s*-?%}")
    bad: List[str] = []
    if not template_dir.is_dir():
        return bad
    for path in sorted(template_dir.rglob("*.html")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        seen: Dict[str, int] = {}
        for m in block_re.finditer(text):
            name = m.group(1)
            seen[name] = seen.get(name, 0) + 1
        dups = [n for n, c in seen.items() if c > 1]
        if dups:
            try:
                rel = path.relative_to(template_dir)
            except ValueError:
                rel = path
            bad.append(
                f"{rel}: duplicate block(s) {dups}"
            )
    return bad


# Identifiers we know are browser/Jinja-provided globals and should
# never be flagged as "undefined" by the inline-script lint below.
_JS_GLOBAL_IDENTS: frozenset = frozenset({
    "window", "document", "console", "navigator", "location",
    "localStorage", "sessionStorage", "history", "fetch", "alert",
    "confirm", "prompt", "Math", "Date", "JSON", "Number", "String",
    "Boolean", "Array", "Object", "Map", "Set", "Promise", "Error",
    "URL", "URLSearchParams", "FormData", "Blob", "File",
    "setTimeout", "clearTimeout", "setInterval", "clearInterval",
    "requestAnimationFrame", "cancelAnimationFrame",
    "Bokeh", "bootstrap", "jQuery", "$", "io", "performance",
    "CustomEvent", "Event", "MutationObserver", "IntersectionObserver",
    "encodeURIComponent", "decodeURIComponent", "atob", "btoa",
    "parseInt", "parseFloat", "isNaN", "isFinite",
})


def _check_template_inline_js(template_dir: Path) -> List[str]:
    """Static lint for undefined-identifier bugs in inline ``<script>``.

    JavaScript ``ReferenceError`` (e.g. ``fType is not defined``) only
    surfaces when the user opens the page. This scans every inline
    ``<script>`` block in every Jinja template and, for each usage of
    the form ``IDENT.addEventListener(``, verifies ``IDENT`` is either
    declared locally (``const/let/var``, ``function``, function
    parameter) or is a known browser global. Anything else is flagged
    so it shows up in the boot log instead of a user-visible crash.

    The lint is deliberately narrow: it only looks at the
    ``.addEventListener`` usage pattern (the shape that has repeatedly
    regressed on the Issues page) so it almost never produces false
    positives across unrelated templates.
    """
    import re as _re

    script_re = _re.compile(
        r"<script\b[^>]*>(.*?)</script>", _re.DOTALL | _re.IGNORECASE)
    # Skip scripts that are modules or external (have a src=).
    src_attr_re = _re.compile(r"<script\b[^>]*\bsrc\s*=", _re.IGNORECASE)
    decl_re = _re.compile(
        r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)")
    func_re = _re.compile(
        r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)")
    # Anonymous functions: ``function (x, y) {``. No name, but params
    # are declarations inside the closure.
    anon_func_re = _re.compile(
        r"\bfunction\s*\(([^)]*)\)")
    arrow_params_re = _re.compile(
        r"\(([^)]*)\)\s*=>")
    # Single-arg arrow funcs: ``x => ...`` with no parens.
    arrow_single_re = _re.compile(
        r"(?<![\w$])([A-Za-z_$][\w$]*)\s*=>")
    class_re = _re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)")
    listener_re = _re.compile(
        r"\b([A-Za-z_$][\w$]*)\s*\.\s*addEventListener\s*\(")
    ident_re = _re.compile(r"[A-Za-z_$][\w$]*")

    bad: List[str] = []
    if not template_dir.is_dir():
        return bad
    for path in sorted(template_dir.rglob("*.html")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Re-locate each <script> block and skip external ones.
        for m in script_re.finditer(text):
            head_start = max(0, m.start() - 200)
            head = text[head_start:m.start() + 8]
            if src_attr_re.search(head):
                continue
            body = m.group(1)
            declared = set()
            for dm in decl_re.finditer(body):
                declared.add(dm.group(1))
            for fm in func_re.finditer(body):
                declared.add(fm.group(1))
                for p in ident_re.findall(fm.group(2) or ""):
                    declared.add(p)
            for fm in anon_func_re.finditer(body):
                for p in ident_re.findall(fm.group(1) or ""):
                    declared.add(p)
            for am in arrow_params_re.finditer(body):
                for p in ident_re.findall(am.group(1) or ""):
                    declared.add(p)
            for am in arrow_single_re.finditer(body):
                declared.add(am.group(1))
            for cm in class_re.finditer(body):
                declared.add(cm.group(1))
            undefined: List[str] = []
            for lm in listener_re.finditer(body):
                name = lm.group(1)
                if name in declared:
                    continue
                if name in _JS_GLOBAL_IDENTS:
                    continue
                if name not in undefined:
                    undefined.append(name)
            if undefined:
                try:
                    rel = path.relative_to(template_dir)
                except ValueError:
                    rel = path
                bad.append(
                    f"{rel}: inline <script> uses undefined "
                    f"identifier(s) {undefined} with "
                    f".addEventListener(...)"
                )
    return bad



_ISSUE_MONITOR_INTERVAL_S = 6 * 3600


def _start_issue_monitor(app) -> None:
    """Start a daemon thread that periodically scans for new issues.

    Runs :func:`scan_pending_verification` (and any future scanners)
    every :data:`_ISSUE_MONITOR_INTERVAL_S` seconds, so that the
    per-request ``/api/issues/list`` handler never has to do this
    scan itself.
    """
    import sys as _sys
    from pathlib import Path as _Path
    from apero_ri.core.astrometric_scanner import scan_pending_verification

    data_dir = _Path(app.args.data_dir or str(_Path.home() / '.ari'))
    astrom_root = data_dir / 'apero-assets' / 'astrometrics'

    def _loop():
        while True:
            try:
                scan_pending_verification(
                    data_dir, astrom_root,
                    created_by='astrometric-scanner',
                    visibility='monitor')
            except Exception as exc:  # noqa: BLE001
                print(f'[apero_ri] issue monitor scan failed: {exc}',
                      file=_sys.stderr, flush=True)
            time.sleep(_ISSUE_MONITOR_INTERVAL_S)

    t = threading.Thread(target=_loop, name='ari-issue-monitor',
                          daemon=True)
    t.start()


def ariapp_run(self, host, port, debug, **kwargs):
    """Run the ARI Flask application.

    Uses values from command-line args unless explicitly overridden.
    """
    """Run the ARI Flask application.

    Uses values from command-line args unless explicitly overridden.

    Werkzeug's ``ThreadingMixIn`` uses ``block_on_close=True``, which
    means ``server_close()`` joins every active request-handler thread
    before returning.  If any handler is long-running (SSE poll, slow
    DB/SSHFS call) this blocks indefinitely on Ctrl+C.

    A SIGINT handler is installed that:
    1. Starts a 5-second watchdog daemon thread.
    2. Re-raises ``KeyboardInterrupt`` to unblock ``serve_forever()``.
    3. Watchdog calls ``os._exit(130)`` if the server has not returned
       within 5 seconds, guaranteeing the port is always released.
    """
    import signal
    import sys as _sys

    if host is None:
        host = self._resolve_host(self.args.host)
    if port is None:
        port = self.args.port
    kwargs.setdefault("use_reloader", False)

    _start_issue_monitor(self)

    # Production mode: serve with waitress (multi-threaded, no dev-server
    # warnings, robust connection handling) instead of the Flask dev server.
    if getattr(self.args, "production", False):
        import sys as _sys
        try:
            from waitress import serve as _waitress_serve
        except ImportError:
            print(
                "[apero_ri] --production requires waitress "
                "(pip install waitress); falling back to the "
                "development server.",
                file=_sys.stderr,
                flush=True,
            )
        else:
            threads = max(2, int(getattr(self.args, "threads", 16) or 16))
            print(
                f"[apero_ri] Starting production server (waitress) on "
                f"{host}:{port} with {threads} threads",
                file=_sys.stderr,
                flush=True,
            )
            try:
                if host == "::":
                    # Bind both IPv6 and IPv4 stacks.
                    _waitress_serve(
                        self, listen=f"*:{port}", threads=threads
                    )
                else:
                    _waitress_serve(
                        self, host=host, port=port, threads=threads
                    )
            except KeyboardInterrupt:
                pass
            finally:
                self.shutdown()
            return

    if debug:
        print(
            f"[apero_ri] Starting server on {host}:{port}"
            f" (debug={debug}, reloader=off)",
            file=_sys.stderr,
            flush=True,
        )

    _cleanup_done = threading.Event()

    def _watchdog(timeout_s: float) -> None:
        """Force-exit if clean shutdown takes longer than *timeout_s* s.

        Werkzeug's ThreadingMixIn block_on_close=True can hang
        server_close() waiting for long-running request threads
        (e.g. SSE, slow SSHFS/DB calls).  After the timeout we call
        os._exit() which bypasses atexit but releases the port
        immediately.  Daemon threads (task worker, scheduler) are
        killed by the OS on process exit.
        """
        if not _cleanup_done.wait(timeout_s):
            if debug:
                print(
                    f"\n[apero_ri] Shutdown watchdog fired after "
                    f"{timeout_s}s — a request-handler thread did not "
                    f"finish in time.  Forcing exit. "
                    f"(Port will be released.)",
                    file=_sys.stderr,
                    flush=True,
                )
            os._exit(130)

    _watchdog_thread = None
    _original_sigint = signal.getsignal(signal.SIGINT)

    def _sigint_handler(signum, frame):
        nonlocal _watchdog_thread
        # Restore the previous handler so a *second* Ctrl+C forces
        # the original behaviour (usually raising KeyboardInterrupt
        # directly, which unblocks if still stuck).
        signal.signal(signal.SIGINT, _original_sigint)
        if debug:
            print(
                "\n[apero_ri] Ctrl+C received — shutting down...",
                file=_sys.stderr,
                flush=True,
            )
        # Arm watchdog before re-raising so Werkzeug block_on_close
        # cannot hang us beyond the timeout.
        if _watchdog_thread is None:
            _watchdog_thread = threading.Thread(
                target=_watchdog,
                args=(5.0,),
                daemon=True,
                name="ari-shutdown-watchdog",
            )
            _watchdog_thread.start()
            if debug:
                print(
                    "[apero_ri] Shutdown watchdog armed (5s timeout).",
                    file=_sys.stderr,
                    flush=True,
                )
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint_handler)
    try:
        Flask.run(self, host=host, port=port, debug=debug, **kwargs)
    except KeyboardInterrupt:
        pass
    finally:
        signal.signal(signal.SIGINT, _original_sigint)
        if debug:
            print(
                "[apero_ri] Server stopped — running shutdown hook...",
                file=_sys.stderr,
                flush=True,
            )
        self.shutdown()
        # Signal the watchdog that cleanup finished; it will not fire.
        _cleanup_done.set()


def ariapp_init(self, **kwargs):
    configure_logging()
    Flask.__init__(
        self,
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
        **kwargs,
    )
    # Rate limiter — applied selectively to auth endpoints.
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    self._limiter = Limiter(
        app=self,
        key_func=get_remote_address,
        default_limits=[],          # no global limit; applied per-route
        storage_uri="memory://",    # in-process; swap for redis:// in prod
    )
    # Install a self-healing wrapper around Flask's Jinja loader so a
    # template that was accidentally saved with duplicated content
    # (extra {% extends %} + duplicate blocks — a recurring stale-
    # editor-buffer corruption) is auto-repaired on load instead of
    # 500-ing the page. The wrapper rewrites the on-disk file once.
    if self.jinja_loader is not None:
        _install_self_healing_loader(self.jinja_loader)
    # Sanity: scan templates for duplicate {% block ... %} declarations
    # right now (boot time). If found, attempt the same auto-heal so
    # the file is fixed before any request hits Jinja.
    try:
        _bad_tpls = _check_template_duplicate_blocks(TEMPLATE_DIR)
    except Exception:
        _bad_tpls = []
    if _bad_tpls:
        import sys as _sys

        print(
            "[apero_ri] WARNING: Jinja templates with duplicate "
            "{% block %} declarations detected — attempting auto-heal:",
            file=_sys.stderr,
            flush=True,
        )
        for _line in _bad_tpls:
            print(f"  - {_line}", file=_sys.stderr, flush=True)
        _flagged_rel = set()
        for _line in _bad_tpls:
            _rel_str = _line.split(":", 1)[0].strip()
            if _rel_str:
                _flagged_rel.add(_rel_str)
        for _rel_str in sorted(_flagged_rel):
            _path = TEMPLATE_DIR / _rel_str
            if not _path.is_file():
                continue
            try:
                _txt = _path.read_text(
                    encoding="utf-8", errors="replace")
            except OSError:
                continue
            _healed = _heal_duplicated_template(_txt)
            if _healed is None or _healed == _txt:
                continue
            try:
                _tmp = _path.with_name(_path.name + ".heal-tmp")
                with open(_tmp, "w", encoding="utf-8") as _fio:
                    _fio.write(_healed)
                os.replace(_tmp, _path)
                print(
                    f"[apero_ri] AUTO-HEAL: rewrote {_path}",
                    file=_sys.stderr,
                    flush=True,
                )
            except OSError as _exc:
                print(
                    f"[apero_ri] AUTO-HEAL: failed to rewrite "
                    f"{_path}: {_exc}",
                    file=_sys.stderr,
                    flush=True,
                )
    # Sanity: scan inline <script> blocks for undefined identifiers
    # used with .addEventListener(...). These throw ReferenceError in
    # the browser only when a user opens the page, so catch them here.
    try:
        _bad_js = _check_template_inline_js(TEMPLATE_DIR)
    except Exception:
        _bad_js = []
    if _bad_js:
        import sys as _sys

        print(
            "[apero_ri] WARNING: Jinja templates with inline <script> "
            "blocks that reference undeclared identifiers in "
            ".addEventListener(...) — these pages will throw "
            "ReferenceError in the browser until fixed:",
            file=_sys.stderr,
            flush=True,
        )
        for _line in _bad_js:
            print(f"  - {_line}", file=_sys.stderr, flush=True)
    # Parse command-line arguments
    self.args = self._get_arguments()
    os.environ["ARI_DIR"] = str(
        Path(self.args.data_dir).expanduser()
        if self.args.data_dir
        else (Path.home() / ".ari")
    )
    ud.set_ari_dir(self.args.data_dir or str(Path.home() / ".ari"))
    auth.set_ari_dir(self.args.data_dir or str(Path.home() / ".ari"))
    audit_log.set_ari_dir(self.args.data_dir or str(Path.home() / ".ari"))
    health_history.set_ari_dir(self.args.data_dir or str(Path.home() / ".ari"))
    dt.set_ari_dir(
        Path(self.args.data_dir).expanduser()
        if self.args.data_dir
        else Path.home() / ".ari"
    )
    # Secret key for sessions
    self.secret_key = self._load_or_create_secret()
    # Load YAML definitions
    # ari_groups is a live-reloading property on ARIApp; ari_pages is
    # static and set once here.
    self.ari_pages = perms.load_pages()
    # Remove template entries (with {placeholders}) — they are
    # expanded dynamically at request time from apero_profiles.yaml
    self._page_templates = {}
    for pid in list(self.ari_pages.keys()):
        if "{" in pid:
            self._page_templates[pid] = self.ari_pages.pop(pid)
    # Ensure default admin user exists
    auth.ensure_default_user()
    # In-memory throttle state for forgot-password requests
    self._forgot_pw_rate_limit = {}
    self._forgot_pw_max_attempts = 3
    self._forgot_pw_base_wait = 30
    self._forgot_pw_max_wait = 600
    # Cached admin health checks (expensive DB/SMTP checks)
    self._admin_health_cache = {}
    self._admin_health_cache_ttl = timedelta(hours=1)
    self._admin_health_cache_lock = threading.Lock()
    ari_root = Path(self.args.data_dir or str(Path.home() / ".ari"))
    self._admin_health_cache_file = (
        ari_root / "admin" / "health" / "health_cache.json"
    )
    self._admin_health_cache_legacy_file = (
        ari_root / "admin" / "health_cache.json"
    )
    self._load_health_cache_from_disk()
    self._shutdown_lock = threading.Lock()
    self._shutdown_started = False
    # Configure session lifetime for "remember me"
    self.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    self.config["SESSION_COOKIE_NAME"] = "apero_ri"
    self.config["SESSION_COOKIE_HTTPONLY"] = True
    self.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    self.config["SESSION_REFRESH_EACH_REQUEST"] = True
    self._configure_production_hardening()
    # Register context processors and routes
    self._register_context_processors()
    self._register_routes()
    self._start_admin_health_refresher()
    task_runner.start_background_services(
        self.args.data_dir or str(Path.home() / ".ari")
    )
    atexit.register(self.shutdown)


def ariapp_get_instrument_run_ids(instrument):
    """Return sorted list of all unique run_ids from object table JSONs.

    Only scans profiles that currently exist in apero_profiles to avoid
    picking up orphaned task files from deleted profiles.
    """
    import json as _json

    # Get current profiles; only scan their task files
    all_profiles = auth.load_apero_profiles(hydrate=False)
    current_profile_names = set()
    if instrument in all_profiles:
        inst_profiles = all_profiles[instrument]
        if isinstance(inst_profiles, dict):
            current_profile_names = set(inst_profiles.keys())

    tasks_dir = auth.ARI_DIR / "tasks" / instrument
    run_ids = set()
    if tasks_dir.exists():
        # New layout: tasks/<instrument>/<apero_profile>/object_table.json
        # Only scan directories that correspond to current profiles
        for profile_dir in tasks_dir.iterdir():
            if not profile_dir.is_dir():
                continue
            profile_name = profile_dir.name
            if profile_name not in current_profile_names:
                continue  # Skip orphaned profile dirs
            jf = profile_dir / "object_table.json"
            if jf.exists():
                try:
                    with open(jf, encoding="utf-8") as f:
                        data = _json.load(f)
                    for row in data.get("rows", []):
                        raw = str(row.get("RUN_ID", "") or "")
                        for rid in raw.split(","):
                            rid = rid.strip()
                            if rid:
                                run_ids.add(rid)
                except Exception:
                    pass

        # Legacy layout: tasks/<instrument>/object_table_<profile>.json
        # Check these only if they correspond to current profiles
        for jf in tasks_dir.glob("object_table_*.json"):
            # Extract profile name from filename (object_table_<profile>.json)
            fname = jf.name
            if fname.startswith("object_table_") and fname.endswith(".json"):
                profile_name = fname[len("object_table_"): -len(".json")]
                if profile_name not in current_profile_names:
                    continue  # Skip orphaned legacy files
                try:
                    with open(jf, encoding="utf-8") as f:
                        data = _json.load(f)
                    for row in data.get("rows", []):
                        raw = str(row.get("RUN_ID", "") or "")
                        for rid in raw.split(","):
                            rid = rid.strip()
                            if rid:
                                run_ids.add(rid)
                except Exception:
                    pass
    return sorted(run_ids)


def ariapp_get_instrument_run_id_pi_names(instrument):
    """Return run_id -> PI name map from object table JSON rows."""
    import json as _json

    all_profiles = auth.load_apero_profiles(hydrate=False)
    current_profile_names = set()
    if instrument in all_profiles:
        inst_profiles = all_profiles[instrument]
        if isinstance(inst_profiles, dict):
            current_profile_names = set(inst_profiles.keys())

    def _clean_pi_name(raw_value):
        pi_name = str(raw_value or '').strip()
        if not pi_name:
            return ''
        if pi_name.lower() in {'none', 'null', 'unknown'}:
            return ''
        return pi_name

    def _split_multi(raw_value):
        if isinstance(raw_value, list):
            return [str(x).strip() for x in raw_value if str(x).strip()]
        text = str(raw_value or '').strip()
        if not text:
            return []
        if ';' in text:
            parts = text.split(';')
        else:
            parts = text.split(',')
        return [part.strip() for part in parts if part.strip()]

    def _get_pi_raw(row):
        pi_keys = (
            'PI_NAMES',
            'PI_NAME',
            'KW_PI_NAMES',
            'KW_PI_NAME',
        )
        for key in pi_keys:
            if key in row:
                return row.get(key, '')
        return ''

    def _update_map(run_id_map, rows):
        for row in rows:
            raw_run = row.get('RUN_ID', '')
            raw_pi = _get_pi_raw(row)
            run_parts = _split_multi(raw_run)
            pi_parts = _split_multi(raw_pi)
            for idx, run_id in enumerate(run_parts):
                if run_id in run_id_map:
                    continue
                pi_candidate = ''
                if pi_parts:
                    if idx < len(pi_parts):
                        pi_candidate = _clean_pi_name(pi_parts[idx])
                    elif len(pi_parts) == 1:
                        pi_candidate = _clean_pi_name(pi_parts[0])
                if pi_candidate:
                    run_id_map[run_id] = pi_candidate

    tasks_dir = auth.ARI_DIR / 'tasks' / instrument
    run_id_pi_names = dict()
    if tasks_dir.exists():
        for profile_dir in tasks_dir.iterdir():
            if not profile_dir.is_dir():
                continue
            profile_name = profile_dir.name
            if profile_name not in current_profile_names:
                continue
            jf = profile_dir / 'object_table.json'
            if not jf.exists():
                continue
            try:
                with open(jf, encoding='utf-8') as fhandle:
                    data = _json.load(fhandle)
                _update_map(run_id_pi_names, data.get('rows', []))
            except Exception:
                continue

        for jf in tasks_dir.glob('object_table_*.json'):
            fname = jf.name
            if not fname.startswith('object_table_'):
                continue
            if not fname.endswith('.json'):
                continue
            profile_name = fname[len('object_table_'): -len('.json')]
            if profile_name not in current_profile_names:
                continue
            try:
                with open(jf, encoding='utf-8') as fhandle:
                    data = _json.load(fhandle)
                _update_map(run_id_pi_names, data.get('rows', []))
            except Exception:
                continue

    return run_id_pi_names


def ariapp_sync_all_science_group(self, instrument, groups, run_ids, persist):
    """Ensure reserved All science group mirrors instrument run IDs."""
    if groups is None:
        groups = auth.load_science_groups(instrument)
    if not isinstance(groups, dict):
        groups = {}

    if run_ids is None:
        run_ids = self._get_instrument_run_ids(instrument)
    normalized_run_ids = sorted(
        {str(rid).strip() for rid in run_ids if str(rid).strip()}
    )

    changed = False
    canonical_name = "All"
    all_entry = groups.get(canonical_name)
    if not isinstance(all_entry, dict):
        all_entry = {}
        changed = True

    # Merge any legacy/case-variant "all" group names into canonical "All".
    for gname in list(groups.keys()):
        if gname == canonical_name:
            continue
        if self._is_all_science_group(gname):
            legacy_entry = groups.pop(gname)
            if isinstance(legacy_entry, dict):
                legacy_users = legacy_entry.get("users", [])
                if isinstance(legacy_users, list) and "users" not in all_entry:
                    all_entry["users"] = legacy_users
            changed = True

    users = all_entry.get("users", [])
    if not isinstance(users, list):
        users = []
        changed = True

    desired_all = {
        "run_ids": normalized_run_ids,
        "users": users,
    }
    if groups.get(canonical_name) != desired_all:
        groups[canonical_name] = desired_all
        changed = True

    if changed and persist:
        auth.save_science_groups(instrument, groups)

    return groups, normalized_run_ids


def ariapp_api_db_ssh_tunnel_save(self):
    """Create or update one DB tunnel definition."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "") or "").strip()
    ssh_config_host = str(body.get("ssh_config_host", "") or "").strip()
    remote_host = str(body.get("remote_host", "") or "").strip()
    remote_port = str(body.get("remote_port", "") or "").strip()
    local_port = str(body.get("local_port", "") or "").strip()
    ssh_mode = str(body.get("ssh_mode", "apero") or "apero").strip()
    username = str(
        body.get("DB_USERNAME_TEST", body.get("DATABASE_USERNAME", ""))
        or ""
    ).strip()
    password = str(
        body.get("DB_PASSWORD_TEST", body.get("DATABASE_PASSWORD", ""))
        or ""
    )
    db_name = str(
        body.get("DB_NAME_TEST", body.get("DATABASE_NAME", ""))
        or ""
    ).strip()
    notes = str(body.get("notes", "") or "").strip()

    if not name:
        return jsonify(success=False, error="name is required"), 400
    if not re.match(r"^[A-Za-z0-9_\-]+$", name):
        return (
            jsonify(
                success=False,
                error="name must be alphanumeric, dash, or underscore",
            ),
            400,
        )
    if not ssh_config_host:
        return jsonify(success=False, error="ssh_config_host is required"), 400
    if not remote_host:
        return jsonify(success=False, error="remote_host is required"), 400
    if not local_port:
        return jsonify(success=False, error="local_port is required"), 400
    if not str(remote_port).isdigit() or not str(local_port).isdigit():
        return (
            jsonify(
                success=False,
                error="local_port and remote_port must be numeric",
            ),
            400,
        )
    if ssh_mode not in ["apero", "simple"]:
        return (
            jsonify(
                success=False,
                error='ssh_mode must be either "apero" or "simple"',
            ),
            400,
        )

    tunnels = self._load_db_tunnel_definitions()
    tunnels[name] = {
        "ssh_config_host": ssh_config_host,
        "remote_host": remote_host,
        "remote_port": remote_port,
        "local_port": local_port,
        "ssh_mode": ssh_mode,
        "DB_USERNAME_TEST": username,
        "DB_PASSWORD_TEST": password,
        "DB_NAME_TEST": db_name,
        "notes": notes,
    }
    self._save_db_tunnel_definitions(tunnels)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_shutdown(self):
    """Clean up background services and interactive child processes."""
    import sys as _sys

    with self._shutdown_lock:
        if self._shutdown_started:
            return
        self._shutdown_started = True

    _debug = self.debug

    if _debug:
        print(
            "[apero_ri] Saving admin health cache...",
            file=_sys.stderr,
            flush=True,
        )
    try:
        self._save_health_cache_to_disk()
        if _debug:
            print(
                "[apero_ri]   health cache saved.", file=_sys.stderr, flush=True
            )
    except Exception as _exc:
        if _debug:
            print(
                f"[apero_ri]   health cache save failed: {_exc}",
                file=_sys.stderr,
                flush=True,
            )

    if _debug:
        print(
            "[apero_ri] Stopping background task worker/scheduler...",
            file=_sys.stderr,
            flush=True,
        )
    try:
        task_runner.shutdown_background_services(debug=_debug)
        if _debug:
            print(
                "[apero_ri]   background services stopped.",
                file=_sys.stderr,
                flush=True,
            )
    except Exception as _exc:
        if _debug:
            print(
                f"[apero_ri]   background services stop failed: {_exc}",
                file=_sys.stderr,
                flush=True,
            )

    if _debug:
        print(
            "[apero_ri] Closing interactive SSHFS sessions...",
            file=_sys.stderr,
            flush=True,
        )
    try:
        from apero_ri.core.sshfs_interactive import close_all_sessions

        result = close_all_sessions()
        if _debug:
            n = result.get("closed", 0)
            print(
                f"[apero_ri]   closed {n} interactive session(s).",
                file=_sys.stderr,
                flush=True,
            )
    except Exception as _exc:
        if _debug:
            print(
                f"[apero_ri]   SSHFS session cleanup failed: {_exc}",
                file=_sys.stderr,
                flush=True,
            )

    if _debug:
        print("[apero_ri] Shutdown complete.", file=_sys.stderr, flush=True)


def ariapp_list_db_tunnel_rows(self):
    """List DB tunnel definitions with live health details."""
    tunnels = self._load_db_tunnel_definitions()
    rows = []
    for name in sorted(tunnels.keys()):
        tunnel_def = tunnels.get(name, {})
        test_user = str(
            tunnel_def.get(
                "DB_USERNAME_TEST", tunnel_def.get("DATABASE_USERNAME", "")
            )
            or ""
        ).strip()
        test_pass = str(
            tunnel_def.get(
                "DB_PASSWORD_TEST", tunnel_def.get("DATABASE_PASSWORD", "")
            )
            or ""
        )
        test_db_name = str(
            tunnel_def.get(
                "DB_NAME_TEST", tunnel_def.get("DATABASE_NAME", "")
            )
            or ""
        ).strip()
        params = self._build_db_tunnel_runtime_params(name, tunnel_def)
        ssh_host = str(params.get("DATABASE_SSH_CONFIG_HOST", "") or "")
        remote_host = str(params.get("DATABASE_HOST", "") or "")
        local_port = str(params.get("DATABASE_SSH_LOCAL_PORT", "") or "")
        valid = bool(name and ssh_host and remote_host and local_port)

        status = {
            "active": False,
            "control_alive": False,
            "local_port_open": False,
            "local_host": "127.0.0.1",
            "local_port": local_port,
            "ssh_host": ssh_host,
            "remote_host": remote_host,
            "remote_port": str(
                params.get("DATABASE_SSH_REMOTE_PORT", "") or ""
            ),
            "created_at": "",
        }
        err = ""
        if valid:
            try:
                status = apero_async.get_db_tunnel_status(params)
            except Exception as exc:
                err = str(exc)
        else:
            err = (
                "Tunnel definition is incomplete. "
                "Require name, ssh_config_host, remote_host, local_port."
            )

        rows.append(
            {
                "name": name,
                "definition": tunnel_def,
                "DB_USERNAME_TEST": test_user,
                "DB_PASSWORD_TEST": test_pass,
                "DB_NAME_TEST": test_db_name,
                # Legacy aliases kept for existing UI/API consumers.
                "DATABASE_USERNAME": test_user,
                "DATABASE_PASSWORD": test_pass,
                "DATABASE_NAME": test_db_name,
                "ssh_mode": str(
                    tunnel_def.get("ssh_mode", "apero") or "apero"
                ),
                "valid_config": valid,
                "config_error": err if not valid else "",
                "status": status,
                "error": err if valid else "",
            }
        )

    return rows


def ariapp_reset_password_view(self, token):
    """Validate token and allow user to set a new password."""
    users = auth.load_users()
    changed = self._cleanup_expired_reset_tokens(users)
    username = self._find_reset_user(token, users)

    if request.method == "POST":
        if not username:
            if changed:
                auth.save_users(users)
            flash("This reset link is invalid or has expired.", "danger")
            return redirect(url_for("forgot_password"))

        new_password = str(request.form.get("new_password", ""))
        confirm_password = str(request.form.get("confirm_password", ""))

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template(
                "home/reset_password.html",
                page_label="Reset Password",
                page_icon="fa-solid fa-lock",
                token_valid=True,
            )
        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template(
                "home/reset_password.html",
                page_label="Reset Password",
                page_icon="fa-solid fa-lock",
                token_valid=True,
            )

        users[username]["password"] = auth.hash_password(new_password)
        users[username].pop("password_reset", None)
        auth.save_users(users)
        flash("Your password has been reset. You can now log in.", "success")
        return redirect(url_for("login"))

    if changed:
        auth.save_users(users)

    return render_template(
        "home/reset_password.html",
        page_label="Reset Password",
        page_icon="fa-solid fa-lock",
        token_valid=(username is not None),
    )


def ariapp_configure_production_hardening(self):
    """Apply production hardening: proxy support, limits, security headers.

    Environment variables:
      ARI_PROXY_COUNT  Number of trusted reverse proxies in front of the app
                       (e.g. 1 for a single nginx).  Enables ProxyFix so
                       request.remote_addr / scheme reflect the real client,
                       which keeps rate-limit keys and HTTPS detection
                       correct behind a proxy.  Default: 0 (disabled).
      ARI_HTTPS        Set to 1 when the site is served over HTTPS (directly
                       or via the proxy).  Marks session cookies Secure and
                       enables HSTS.  Default: off.
      ARI_MAX_CONTENT_MB  Maximum request body size in MB.  Default: 128.
    """
    # --- Reverse proxy support -------------------------------------------
    try:
        proxy_count = int(os.environ.get("ARI_PROXY_COUNT", "0") or "0")
    except ValueError:
        proxy_count = 0
    if proxy_count > 0:
        from werkzeug.middleware.proxy_fix import ProxyFix
        self.wsgi_app = ProxyFix(
            self.wsgi_app,
            x_for=proxy_count,
            x_proto=proxy_count,
            x_host=proxy_count,
            x_prefix=proxy_count,
        )

    # --- HTTPS cookie/transport hardening --------------------------------
    https_on = str(os.environ.get("ARI_HTTPS", "") or "").strip().lower() in (
        "1", "true", "yes", "on",
    )
    if https_on:
        self.config["SESSION_COOKIE_SECURE"] = True
        self.config["PREFERRED_URL_SCHEME"] = "https"

    # --- Request body size limit ------------------------------------------
    try:
        max_mb = int(os.environ.get("ARI_MAX_CONTENT_MB", "128") or "128")
    except ValueError:
        max_mb = 128
    self.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024

    # --- Static asset cache policy ---------------------------------------
    try:
        static_cache_s = int(
            os.environ.get('ARI_STATIC_CACHE_SECONDS', '604800')
            or '604800'
        )
    except ValueError:
        static_cache_s = 604800
    static_cache_s = max(0, static_cache_s)

    # --- Security headers on every response --------------------------------
    @self.after_request
    def _security_headers(response):
        hdrs = response.headers
        hdrs.setdefault("X-Content-Type-Options", "nosniff")
        hdrs.setdefault("X-Frame-Options", "SAMEORIGIN")
        hdrs.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        hdrs.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        if https_on:
            hdrs.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        req_path = str(getattr(request, 'path', '') or '')
        if static_cache_s > 0 and req_path.startswith('/static/'):
            hdrs['Cache-Control'] = (
                f'public, max-age={static_cache_s}, immutable'
            )
        return response


def ariapp_register_routes(self):
    """Register all routes from pages.yaml plus login/logout."""
    _lim = self._limiter

    # Login route — rate-limited to prevent brute-force attacks.
    self.add_url_rule(
        "/login", "login",
        _lim.limit("20 per minute; 100 per hour")(self._login_view),
        methods=["GET", "POST"],
    )
    self.add_url_rule(
        "/forgot-password",
        "forgot_password",
        _lim.limit("5 per minute; 20 per hour")(self._forgot_password_view),
        methods=["GET", "POST"],
    )
    self.add_url_rule(
        "/reset-password/<token>",
        "reset_password",
        _lim.limit("10 per minute")(self._reset_password_view),
        methods=["GET", "POST"],
    )
    self.add_url_rule(
        "/register", "register", self._register_view, methods=["GET"]
    )
    # Logout route (no limit needed)
    self.add_url_rule("/logout", "logout", self._logout_view)

    # Lightweight unauthenticated liveness probe for load balancers and
    # uptime monitors.  Deliberately does no DB/disk work.
    def _healthz():
        return jsonify(status="ok"), 200

    self.add_url_rule("/healthz", "healthz", _healthz)

    # ARI is a private reduction interface — opt out of search indexing.
    def _robots_txt():
        body = "User-agent: *\nDisallow: /\n"
        return body, 200, {"Content-Type": "text/plain; charset=utf-8"}

    self.add_url_rule("/robots.txt", "robots_txt", _robots_txt)

    # Static route blocks are delegated to helper module to keep
    # _register_routes focused on orchestration.
    app_routes.register_static_routes(self)

    # Dynamic Data Portal routes are split into a helper module to
    # keep this method shorter and easier to navigate.
    app_routes.register_data_portal_routes(self)

    # Register every page from pages.yaml
    for page_id, page_def in self.ari_pages.items():
        # Skip login/logout - already registered
        if page_id in ("home.login", "home.logout"):
            continue
        # External links are nav/cards only and do not map to Flask routes.
        if str(page_def.get("external-url", "") or "").strip():
            continue
        url = perms.page_id_to_url(page_id)
        endpoint = perms.page_id_to_endpoint(page_id)
        self.add_url_rule(
            url,
            endpoint,
            self._make_page_view(page_id),
        )

    # ------------------------------------------------------------------
    # HTTP error handlers
    # ------------------------------------------------------------------
    @self.errorhandler(400)
    def _handle_400(exc):
        if _request_wants_json():
            return jsonify({"error": "Bad Request", "detail": str(exc)}), 400
        return render_template("general/error.html", code=400,
                               title="Bad Request",
                               message="The server could not understand the request."), 400

    @self.errorhandler(403)
    def _handle_403(exc):
        if _request_wants_json():
            return jsonify({"error": "Forbidden"}), 403
        return render_template("general/error.html", code=403,
                               title="Forbidden",
                               message="You do not have permission to access this page."), 403

    @self.errorhandler(404)
    def _handle_404(exc):
        if _request_wants_json():
            return jsonify({"error": "Not Found"}), 404
        return render_template("general/error.html", code=404,
                               title="Page Not Found",
                               message="The page you are looking for does not exist."), 404

    @self.errorhandler(500)
    def _handle_500(exc):
        log.exception("Unhandled server error")
        if _request_wants_json():
            return jsonify({"error": "Internal Server Error"}), 500
        return render_template("general/error.html", code=500,
                               title="Internal Server Error",
                               message="An unexpected error occurred. Please try again later."), 500


def _request_wants_json() -> bool:
    """Return True if the request prefers a JSON response."""
    from flask import request as _req
    best = _req.accept_mimetypes.best_match(["application/json", "text/html"])
    return (
        best == "application/json"
        or _req.path.startswith("/api/")
        or _req.is_json
    )


def ariapp_execute_db_query(self, profile_cfg, query, query_params):
    """Execute a parameterized SELECT query against the profile's database.

    Uses SQLAlchemy's expanding bindparams for IN-clause list values.
    Only SELECT statements are accepted (validated by caller).
    """
    from urllib.parse import quote_plus

    from sqlalchemy import bindparam, create_engine, text

    db_params = self._profile_db_params(profile_cfg)
    mode = str(db_params.get("DATABASE_MODE", "")).strip()
    username = str(db_params.get("DATABASE_USERNAME", "")).strip()
    password = str(db_params.get("DATABASE_PASSWORD", "") or "")
    db_name = str(db_params.get("DATABASE_NAME", "")).strip()

    if not all([mode, username, db_name]):
        raise ValueError("Missing database connection configuration.")

    host, port = apero_async._resolve_database_endpoint(db_params)

    db_url = (
        f"{mode}://{quote_plus(username)}:{quote_plus(password)}"
        f"@{host}:{port}/{db_name}"
    )
    engine = create_engine(db_url, future=True)

    try:
        params = dict(query_params or {})
        stmt = text(query)
        # Apply expanding bindparams for list values (IN clauses)
        for key, val in params.items():
            if isinstance(val, (list, tuple)):
                stmt = stmt.bindparams(bindparam(key, expanding=True))
        with engine.begin() as conn:
            result = conn.execute(stmt, params)
            if result.returns_rows:
                return [dict(row) for row in result.mappings().all()]
            return []
    finally:
        engine.dispose()


def ariapp_api_apero_profiles_ssh_tunnel_start(self):
    """Start an interactive SSH tunnel session for DB access."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    from apero_ri.core.sshfs_interactive import start_interactive_ssh_tunnel

    body = request.get_json(silent=True) or {}
    ssh_config_host = str(body.get("ssh_config_host", "")).strip()
    local_port = body.get("local_port", 0)
    remote_host = str(body.get("remote_host", "")).strip()
    remote_port = body.get("remote_port", 3306)
    allow_multiple = bool(body.get("allow_multiple", False))
    simple_ssh = bool(body.get("simple_ssh", False))

    try:
        local_port = int(local_port)
        remote_port = int(remote_port)
    except (ValueError, TypeError):
        return jsonify(ok=False, error="Invalid port number"), 400

    if not allow_multiple:
        singleton = apero_async.ensure_single_db_tunnel_slot(
            {
                "DATABASE_SSH_CONFIG_HOST": ssh_config_host,
                "DATABASE_HOST": remote_host,
                "DATABASE_SSH_LOCAL_PORT": local_port,
                "DATABASE_SSH_REMOTE_PORT": remote_port,
                "LOCAL_DATA_DIR": str(self._resolve_local_data_dir()),
            }
        )
        if not singleton.get("ok"):
            return (
                jsonify(
                    ok=False,
                    error=singleton.get(
                        "error",
                        "Failed to enforce single active DB SSH tunnel policy.",
                    ),
                ),
                400,
            )

    result = start_interactive_ssh_tunnel(
        ssh_config_host=ssh_config_host,
        local_port=local_port,
        remote_host=remote_host,
        remote_port=remote_port,
        local_data_dir=str(self._resolve_local_data_dir()),
        simple_ssh=simple_ssh,
    )
    return jsonify(**result)


def ariapp_api_apero_profiles_delete(self):
    """Delete an APERO profile and remove all matching profile directories."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()
    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.get(instrument, {})
    if name not in inst_profiles:
        return jsonify(success=False, error="Profile not found"), 404

    del inst_profiles[name]
    all_profiles[instrument] = inst_profiles
    auth.save_apero_profiles(all_profiles)

    # Clean up all directories named after this profile from local data
    # directory
    import shutil

    local_data_dir = self._resolve_local_data_dir()
    if local_data_dir and os.path.isdir(local_data_dir):
        for item in Path(local_data_dir).rglob(name):
            if item.is_dir():
                try:
                    shutil.rmtree(item)
                except Exception:
                    # Log silently; do not block profile deletion on cleanup.
                    pass

    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_admin_cache_purge(self):
    """Purge cached data (all or per-profile)."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.admin" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    from apero_ri.core.plot_cache import (
        invalidate_all,
        invalidate_profile,
        load_cache_config,
        resolve_cache_root,
    )

    data_dir = self._resolve_local_data_dir()
    cfg = load_cache_config(data_dir)
    cache_root = resolve_cache_root(data_dir, cfg)
    body = request.get_json(silent=True) or {}
    scope = str(body.get("scope", "all")).strip()
    if scope == "section":
        instrument = str(body.get("instrument", "")).strip()
        profile_id = str(body.get("profile_id", "")).strip()
        section = str(body.get("section", "")).strip()
        if not instrument or not profile_id or not section:
            return (
                jsonify(
                    success=False,
                    error="Missing instrument, profile_id, or section",
                ),
                400,
            )
        removed = invalidate_profile(
            cache_root, instrument, profile_id, sections=[section]
        )
    elif scope == "profile":
        instrument = str(body.get("instrument", "")).strip()
        profile_id = str(body.get("profile_id", "")).strip()
        if not instrument or not profile_id:
            return (
                jsonify(
                    success=False, error="Missing instrument or profile_id"
                ),
                400,
            )
        removed = invalidate_profile(cache_root, instrument, profile_id)
    else:
        removed = invalidate_all(cache_root)
    return jsonify(success=True, removed=removed)


def ariapp_share_landing(self, token):
    """Public page for a shared download – no authentication required."""
    share_info = bk.get_share_job(str(token or ""))
    if share_info is None:
        return render_template("data_portal/share_expired.html"), 404

    meta = share_info["meta"]
    chunks = meta.get("chunks", [])
    safe_chunks = []
    for chunk in chunks:
        safe_chunks.append(
            {
                "index": chunk.get("index", 0),
                "filename": chunk.get("filename", ""),
                "size_bytes": chunk.get("size_bytes", 0),
                "file_count": chunk.get("file_count", 0),
                "download_url": url_for(
                    "share_download",
                    token=token,
                    chunk_idx=chunk.get("index", 0),
                ),
            }
        )

    expires_str = None
    try:
        created_at = datetime.fromisoformat(str(meta.get("created_at", "")))
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        expires_at = created_at + timedelta(
            hours=bk._normalize_expiry_hours(meta.get("expiry_hours", 24))
        )
        expires_str = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        pass

    return render_template(
        "data_portal/share_landing.html",
        chunks=safe_chunks,
        meta=meta,
        expires_at=expires_str,
        token=token,
    )


def ariapp_api_user_db_access_profiles(self):
    """List editor-accessible APERO profiles for DB access management."""
    user_info, perms = self._require_user_db_access_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    profiles = auth.get_accessible_profiles(user_info, self.ari_groups)
    db_access = auth.load_db_access()
    table_key_map = self._db_access_table_keys()

    out = []
    for prof in profiles:
        instrument = str(prof.get("instrument", "")).strip()
        profile_id = str(prof.get("profile_id", "")).strip()
        cfg = prof.get("data", {}) if isinstance(prof.get("data"), dict) else {}

        table_names = []
        for label, key in table_key_map.items():
            if str(self._profile_get_db(cfg, key, "")).strip():
                table_names.append(label)

        prof_entry = (
            (
                (
                    db_access.get(instrument, {})
                    if isinstance(db_access.get(instrument, {}), dict)
                    else {}
                ).get(profile_id, {})
            )
            if instrument and profile_id
            else {}
        )

        out.append(
            {
                "instrument": instrument,
                "profile_id": profile_id,
                "has_tables": bool(table_names),
                "health": self._profile_db_access_health(
                    prof_entry, table_names
                ),
            }
        )

    out.sort(key=lambda r: (r["instrument"], r["profile_id"]))
    return jsonify(success=True, profiles=out)


def ariapp_api_db_ssh_tunnel_delete(self):
    """Delete one DB tunnel definition."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "") or "").strip()
    if not name:
        return jsonify(success=False, error="name is required"), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    in_use = []
    for instrument, inst_profiles in (all_profiles or {}).items():
        if not isinstance(inst_profiles, dict):
            continue
        for profile_name, profile_cfg in inst_profiles.items():
            cfg = profile_cfg if isinstance(profile_cfg, dict) else {}
            source = self._normalize_db_source(
                self._profile_get_db(cfg, "DATABASE_SOURCE", "")
            )
            tname = self._resolve_tunnel_name_from_profile_cfg(cfg)
            if source == "db_ssh_tunnel" and tname == name:
                in_use.append(f"{instrument}/{profile_name}")

    if in_use:
        return (
            jsonify(
                success=False,
                error=("Tunnel is used by profile(s): " + ", ".join(in_use)),
            ),
            400,
        )

    tunnels = self._load_db_tunnel_definitions()
    if name not in tunnels:
        return jsonify(success=False, error="Tunnel not found"), 404

    del tunnels[name]
    self._save_db_tunnel_definitions(tunnels)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_database_setup_local_db_test(self):
    """Test one local database definition with supplied credentials."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.database_setup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json(silent=True) or {}
    persist_test_details = bool(body.get('persist_test_details', False))
    name = str(body.get('name', '') or '').strip()
    mode = str(body.get("DATABASE_MODE", "") or "").strip() or "mysql+pymysql"
    host = str(body.get("DATABASE_HOST", "") or "").strip()
    port = str(body.get("DATABASE_PORT", "") or "").strip() or "3306"
    req_username = str(body.get('DATABASE_USERNAME', '') or '').strip()
    req_password = str(body.get('DATABASE_PASSWORD', '') or '')
    req_db_name = str(body.get('DATABASE_NAME', '') or '').strip()
    username = req_username
    password = req_password
    db_name = req_db_name

    defs = None
    entry = None
    saved_test_details = False
    pending_user = ''
    pending_pass = ''
    pending_db_name = ''
    if name:
        defs = self._load_local_db_definitions()
        entry = defs.get(name, {})
        if not isinstance(entry, dict) or not entry:
            return jsonify(success=False, error='Local database not found'), 404

        mode = mode or str(entry.get('DATABASE_MODE', '') or '').strip()
        host = host or str(entry.get('DATABASE_HOST', '') or '').strip()
        port = (
            port
            or str(entry.get('DATABASE_PORT', '') or '').strip()
            or '3306'
        )
        username = (
            username
            or str(entry.get('DATABASE_USERNAME', '') or '').strip()
        )
        password = password or str(entry.get('DATABASE_PASSWORD', '') or '')
        db_name = db_name or str(entry.get('DATABASE_NAME', '') or '').strip()

        if persist_test_details:
            old_user = str(entry.get('DATABASE_USERNAME', '') or '').strip()
            old_pass = str(entry.get('DATABASE_PASSWORD', '') or '')
            old_db_name = str(entry.get('DATABASE_NAME', '') or '').strip()
            if req_username and not old_user:
                pending_user = req_username
            if req_password and not old_pass:
                pending_pass = req_password
            if req_db_name and not old_db_name:
                pending_db_name = req_db_name

    if mode not in ("mysql+pymysql",):
        return jsonify(success=False, error="Unsupported DATABASE_MODE"), 400
    if not host:
        return jsonify(success=False, error="DATABASE_HOST is required"), 400
    if not port.isdigit():
        return (
            jsonify(success=False, error="DATABASE_PORT must be numeric"),
            400,
        )
    if not username or not db_name:
        return (
            jsonify(
                success=False,
                error="DATABASE_USERNAME and DATABASE_NAME are required",
            ),
            400,
        )

    result = auth.validate_database_connection(
        mode,
        host,
        username,
        password,
        db_name,
        port=port,
        use_ssh_tunnel=False,
        ssh_config_host="",
        ssh_local_port="",
        ssh_remote_port="",
        local_data_dir=str(self._resolve_local_data_dir()),
    )
    if result.get('valid') and name and isinstance(entry, dict):
        updated = False
        if pending_user:
            entry['DATABASE_USERNAME'] = pending_user
            updated = True
        if pending_pass:
            entry['DATABASE_PASSWORD'] = pending_pass
            updated = True
        if pending_db_name:
            entry['DATABASE_NAME'] = pending_db_name
            updated = True
        if updated:
            defs[name] = entry
            self._save_local_db_definitions(defs)
            self._refresh_admin_health_after_change(user_info, perms)
            saved_test_details = True
    return jsonify(
        success=True,
        saved_test_details=saved_test_details,
        **result,
    )


def ariapp_api_admin_backups_oauth_start(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(ok=False, error="Insufficient permissions"), 403

    cfg = bb.load_backup_config()
    client_secret_path = Path(
        str(cfg.get("gdrive_oauth_client_secret_file", "")).strip()
    ).expanduser()
    if not client_secret_path.exists():
        return (
            jsonify(
                ok=False,
                error=(
                    "Google OAuth client secret file is missing. "
                    "Upload and save it first."
                ),
            ),
            400,
        )

    try:
        from google_auth_oauthlib.flow import Flow
    except Exception:
        return (
            jsonify(
                ok=False,
                error=(
                    "Google OAuth dependency missing. "
                    "Install google-auth-oauthlib."
                ),
            ),
            500,
        )

    redirect_uri = url_for("api_admin_backups_oauth_callback", _external=True)
    flow = Flow.from_client_secrets_file(
        str(client_secret_path),
        scopes=bb.GDRIVE_OAUTH_SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["ab_google_oauth_state"] = state
    session["ab_google_oauth_code_verifier"] = str(flow.code_verifier or "")
    return redirect(auth_url)


def ariapp_register_context_processors(self):
    @self.context_processor
    def inject_globals():
        user_info = auth.get_effective_user(session)
        if user_info:
            user_perms = permissions_mod.resolve_user_permissions(
                user_info["groups"], self.ari_groups
            )
            logged_in = True
            username = user_info["username"]
            first_names = str(user_info.get("first_names", "")).strip()
            welcome_name = first_names.split()[0] if first_names else username
            login_as = session.get("login_as")
        else:
            user_perms = auth.get_public_permissions()
            logged_in = False
            username = None
            welcome_name = None
            login_as = None

        nav_pages = permissions_mod.get_nav_pages(
            user_perms, self.ari_pages
        )
        logo_path = STATIC_DIR / "images" / "apero_logo.png"
        if username:
            current_theme = ud.load_user_prefs(username).get(
                "theme", "default"
            )
        else:
            current_theme = "default"

        return {
            "logged_in": logged_in,
            "username": username,
            "welcome_name": welcome_name,
            "login_as_user": login_as,
            "last_login": session.get("last_login"),
            "user_permissions": user_perms,
            "nav_pages": nav_pages,
            "ari_pages": self.ari_pages,
            "logo_exists": logo_path.exists(),
            "current_theme": current_theme,
        }


def ariapp_api_user_favourite_objects_toggle(self):
    """Toggle one object in the current user's favourite list."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    objname = str(body.get("objname", "")).strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="profile_id and objname are required",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    # Find which section (if any) this object is in
    found_in = None
    for sec in sections:
        for item in sec.get("items", []):
            if str(item.get("objname", "")).strip() == objname:
                found_in = sec
                break
        if found_in is not None:
            break

    if found_in is not None:
        # Remove from that section
        found_in["items"] = [
            it for it in found_in.get("items", [])
            if str(it.get("objname", "")).strip() != objname
        ]
        is_favourite = False
    else:
        # Adding — verify the user can see this object
        _ufh = user_favourites_api_helpers
        prof, instrument = _ufh._get_profile_info(
            self, profile_id, user_info,
        )
        if not prof:
            return (
                jsonify(
                    success=False,
                    error='Profile not found',
                ),
                404,
            )
        base_dir = Path(
            self.args.data_dir
            or str(Path.home() / '.ari')
        )
        rows = _ufh._load_object_table(
            base_dir, instrument, profile_id,
        )
        if not _ufh._is_object_accessible(
            self, user_info, instrument, rows, objname,
        ):
            return (
                jsonify(
                    success=False,
                    error=(
                        'Object not found or not'
                        ' accessible for this user.'
                    ),
                ),
                404,
            )
        # Add to default section
        default_sec = next(
            (s for s in sections if s.get("name") == "default"), None
        )
        if default_sec is None:
            default_sec = {
                "name": "default", "collapsed": False, "items": []
            }
            sections.insert(0, default_sec)
        default_sec["items"].append(
            {"objname": objname, "nickname": "", "note": ""}
        )
        is_favourite = True

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    flat = ud.get_profile_favourite_objects(username, profile_id)
    return jsonify(
        success=True,
        favourite=is_favourite,
        favourite_objects=flat,
        sections=updated.get("sections", []),
    )


def ariapp_api_apero_profiles_update_groups(self):
    """Update the groups assigned to an APERO profile."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = perms or set()

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    name = data.get("name", "").strip()
    new_groups = data.get("groups", [])
    if not instrument or not name:
        return jsonify(success=False, error="Missing fields"), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.get(instrument, {})
    if name not in inst_profiles:
        return jsonify(success=False, error="Profile not found"), 404

    old_groups = set(inst_profiles[name].get("groups", []))
    changed = (set(new_groups) - old_groups) | (old_groups - set(new_groups))
    for g in changed:
        if f"manage.group.{g}" not in perms:
            return (
                jsonify(
                    success=False, error=f"No permission to manage group: {g}"
                ),
                403,
            )

    inst_profiles[name]["groups"] = new_groups
    auth.save_apero_profiles(all_profiles)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_admin_backups_browse(self):
    try:
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        if "view.admin" not in (perms or set()):
            return jsonify(success=False, error="Insufficient permissions"), 403

        path = str(request.args.get("path", "/") or "/").strip()
        if not os.path.isabs(path):
            return jsonify(success=False, error="Path must be absolute"), 400

        target = Path(path).expanduser()
        if not target.is_dir():
            return jsonify(success=False, error="Not a directory"), 400

        dirs = []
        try:
            for entry in sorted(target.iterdir()):
                try:
                    is_dir = entry.is_dir()
                except PermissionError:
                    continue
                if is_dir and not entry.name.startswith("."):
                    dirs.append(entry.name)
        except PermissionError:
            return jsonify(success=False, error="Permission denied"), 403

        parent = str(target.parent) if str(target) != "/" else "/"
        return jsonify(success=True, path=str(target), parent=parent, dirs=dirs)
    except Exception as exc:
        return jsonify(success=False, error=f"Browse failed: {exc}"), 500


def ariapp_load_health_cache_from_disk(self):
    """Populate in-memory admin health cache from the persisted disk file."""
    try:
        cache_file = self._admin_health_cache_file
        if (
            not cache_file.exists()
            and self._admin_health_cache_legacy_file.exists()
        ):
            cache_file = self._admin_health_cache_legacy_file
        if not cache_file.exists():
            return
        with open(cache_file, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, dict):
            return
        restored = {}
        for key, entry in raw.items():
            if not isinstance(entry, dict):
                continue
            updated_at = None
            updated_at_str = entry.get("updated_at")
            if updated_at_str:
                try:
                    updated_at = datetime.fromisoformat(updated_at_str)
                except Exception:
                    pass
            restored[key] = {
                "health": entry.get("health", {}),
                "updated_at": updated_at,
                "in_progress": False,
                "perms": entry.get("perms", []),
            }
        with self._admin_health_cache_lock:
            self._admin_health_cache = restored
    except Exception:
        pass


def ariapp_api_apero_profiles_browse(self):
    """Browse server directories for the file browser."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    path = request.args.get("path", "/").strip()
    if not os.path.isabs(path):
        return jsonify(success=False, error="Must be absolute"), 400

    target = Path(path)
    if not target.is_dir():
        return jsonify(success=False, error="Not a directory"), 400

    show_hidden = str(request.args.get("show_hidden", "0") or "0").strip() in (
        "1", "true", "yes",
    )
    include_files = str(request.args.get("files", "0") or "0").strip() in (
        "1", "true", "yes",
    )

    dirs = []
    files = []
    try:
        for entry in sorted(target.iterdir()):
            if not show_hidden and entry.name.startswith("."):
                continue
            try:
                is_dir = entry.is_dir()
            except PermissionError:
                continue
            if is_dir:
                dirs.append(entry.name)
            elif include_files:
                files.append(entry.name)
    except PermissionError:
        return jsonify(success=False, error="Permission denied"), 403

    # Check if this directory exists
    validation = auth.validate_path_exists(str(target))
    return jsonify(
        success=True,
        path=str(target),
        dirs=dirs,
        files=files,
        validation=validation,
    )


def ariapp_build_home_page_context(self, user_info, perms):
    """Build the full context payload used by the home page."""
    from apero_ri.application.monitor_view_helpers import (
        _has_any_monitor_perm,
    )

    context = {
        "page_id": "home",
        "page_label": "Home",
        "page_icon": "fa-solid fa-house",
        "is_parent": True,
        "is_monitor": _has_any_monitor_perm(perms),
    }
    context.update(self._build_home_sidebar_context(perms, user_info))

    params = permissions_mod.load_parameters()
    all_instr = params.get("instruments", {}).get("value", [])
    instr_info = []
    for inst in all_instr:
        info = params.get(inst.lower(), {})
        instr_info.append(
            {
                "name": inst,
                "homepage": info.get("homepage", ""),
            }
        )
    context["instruments"] = instr_info

    pubs = params.get("publications", {})
    pub_list = []
    for _key, pub in pubs.items():
        pub_list.append(
            {
                "title": pub.get("title", ""),
                "url": pub.get("paper-url", ""),
            }
        )
    context["publications"] = pub_list
    context["cards"] = permissions_mod.get_visible_cards(
        "home",
        perms,
        self.ari_pages,
        logged_in=(user_info is not None),
    )

    # Surface admin-health status as small badges on matching home cards
    # (e.g. the APERO profiles card shows a warning dot when a profile
    # check is failing) — purely a glance-ahead, no extra computation.
    if user_info and "view.admin" in perms:
        cache_key = self._admin_health_cache_key(perms)
        with self._admin_health_cache_lock:
            cached = self._admin_health_cache.get(cache_key, {})
        health = cached.get("health", {}) or {}
        badges = {}
        for card in context["cards"]:
            entry = health.get(card.get("id", ""))
            if isinstance(entry, dict) and entry.get("status"):
                badges[card["id"]] = entry["status"]
        context["card_health_badges"] = badges

    return context


def ariapp_api_user_delete(self):
    """Delete a user account."""
    user_info, perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = perms or set()

    data = request.get_json()
    if not data or "username" not in data:
        return jsonify(success=False, error="Missing data"), 400

    target = data["username"]
    target_info = auth.get_user_info(target)
    if not target_info:
        return jsonify(success=False, error="User not found"), 404

    # Cannot delete yourself
    if target == user_info["username"]:
        return (
            jsonify(success=False, error="Cannot delete your own account"),
            403,
        )

    # Must have manage.group.{group} for ALL of the target's groups
    for g in target_info.get("groups", []):
        if f"manage.group.{g}" not in perms:
            return (
                jsonify(
                    success=False,
                    error=f"No permission to manage users in group: {g}",
                ),
                403,
            )

    if not auth.delete_user(target):
        return jsonify(success=False, error="Delete failed"), 500
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_user_links_get(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    username = user_info["username"]
    instrument = request.args.get("instrument", "").strip()
    if instrument == "__all__":
        instruments = perms.get_user_instruments(
            user_info.get('groups', []), self.ari_groups
        )
        if not instruments:
            params = perms.load_parameters()
            all_instr = params.get(
                'instruments', {}
            ).get('value', [])
            instruments = list(all_instr)

        data = ud.load_links(username)
        merged = {
            "sections": list(data.get("sections", [])),
            "types": dict(data.get("types", {})),
            "links": {s: dict(v) for s, v in data.get("links", {}).items()},
            "instrument_sections": [],
        }
        for inst in instruments:
            inst_data = ud.load_instrument_links(inst)
            for section in inst_data.get("sections", []):
                tag = f"[{inst}] {section}"
                merged["instrument_sections"].append(tag)
                merged["links"][tag] = dict(
                    inst_data.get("links", {}).get(section, {})
                )
        data = merged
    elif instrument:
        data = ud.get_merged_links(username, instrument)
    else:
        data = ud.load_links(username)
    return jsonify(success=True, data=data)


def ariapp_api_admin_backups_validate_dir(self):
    try:
        user_info, perms = self._require_admin_backup_perm()
        if not user_info:
            return jsonify(success=False, error="Unauthorized"), 401
        if "view.admin" not in (perms or set()):
            return jsonify(success=False, error="Insufficient permissions"), 403

        path = str(request.args.get("path", "") or "").strip()
        if not path:
            return jsonify(success=False, error="No path provided"), 400
        if not os.path.isabs(path):
            return jsonify(success=False, error="Path must be absolute"), 400

        target = Path(path).expanduser()
        if not target.exists():
            return jsonify(
                success=True,
                ok=False,
                path=str(target),
                message="Directory does not exist",
            )
        if not target.is_dir():
            return jsonify(
                success=True,
                ok=False,
                path=str(target),
                message="Path is not a directory",
            )
        try:
            _ = any(target.iterdir())
        except PermissionError:
            return jsonify(
                success=True,
                ok=False,
                path=str(target),
                message="Permission denied for this directory",
            )
        return jsonify(
            success=True,
            ok=True,
            path=str(target),
            message="Directory is valid",
        )
    except Exception as exc:
        return (
            jsonify(success=False, error=f"Validate directory failed: {exc}"),
            500,
        )


def ariapp_login_view(self):
    """Handle login via a modal rendered on top of the home page."""
    username_value = str(session.get("last_username", "") or "")
    user_info = auth.get_effective_user(session)
    if user_info:
        return redirect(url_for("home"))

    perms = auth.get_public_permissions()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        username_value = username
        session["last_username"] = username

        user = auth.authenticate(username, password)
        if user:
            session["user"] = user["username"]
            session["last_login"] = user.get("last_login")
            session.pop("login_as", None)
            session["last_username"] = user["username"]
            # Default to persistent login unless user opts out.
            session.permanent = request.form.get("remember", "1") == "1"
            flash(f'Welcome, {user["username"]}!', "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    context = self._build_home_page_context(None, perms)
    context.update(
        {
            "login_modal_open": True,
            "last_username": username_value,
        }
    )
    return render_template("home/index.html", **context)


def ariapp_filter_plot_rows(htable_rows, ftable_dict, accessible_run_ids):
    """Filter htable and ftable rows by accessible run_ids.

    Parameters
    ----------
    htable_rows : list of dict
    ftable_dict : dict of {label: list of dict}
    accessible_run_ids : set of str

    Returns
    -------
    filtered_htable : list of dict
    filtered_ftables : dict of {label: list of dict}
    """
    from apero_ri.core.basket_funcs import filter_accessible_rows

    filtered_ftables = {}
    accessible_ids = set()
    for label, rows in ftable_dict.items():
        filt = filter_accessible_rows(rows, accessible_run_ids)
        filtered_ftables[label] = filt
        for r in filt:
            ident = str(r.get("IDENTIFIER", "") or "").strip()
            if ident:
                accessible_ids.add(ident)
    if accessible_ids:
        filtered_htable = [
            r
            for r in htable_rows
            if str(r.get("IDENTIFIER", "") or "").strip() in accessible_ids
        ]
    else:
        filtered_htable = list(htable_rows)
    return filtered_htable, filtered_ftables


def ariapp_api_basket_download(self, job_id, chunk_idx):
    """Serve a compiled archive chunk for download."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]

    # Rate-limit check
    wait = dt.check_rate_limit(username, "basket")
    if wait is not None:
        return (
            jsonify(
                success=False,
                error=f"Rate limited – please wait {wait:.1f}s",
                retry_after=wait,
            ),
            429,
        )

    path = bk.get_job_chunk_path(username, job_id, chunk_idx)
    if path is None:
        return jsonify(success=False, error="File not found or not ready"), 404

    # Track the download
    try:
        file_bytes = path.stat().st_size
    except OSError:
        file_bytes = 0
    dt.record_download(username, "basket", file_bytes, 1)

    return send_file(
        str(path),
        as_attachment=True,
        download_name=path.name,
    )


def ariapp_api_basket_jobs(self):
    """Return recent compilation jobs for the user."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]
    bk.cleanup_expired_downloads(username)
    jobs = bk.list_recent_jobs(username, limit=10)
    usage = bk.get_downloads_usage(username)
    limit_bytes = bk.get_downloads_storage_limit_bytes(user_info.get("groups"))

    # Strip internal paths from job metadata for security
    safe_jobs = []
    for job in jobs:
        sj = {k: v for k, v in job.items() if k != "chunks"}
        safe_chunks = []
        for chunk in job.get("chunks", []):
            safe_chunks.append(
                {
                    "index": chunk.get("index"),
                    "filename": chunk.get("filename"),
                    "size_bytes": chunk.get("size_bytes"),
                    "file_count": chunk.get("file_count"),
                }
            )
        sj["chunks"] = safe_chunks
        safe_jobs.append(sj)

    return jsonify(
        success=True,
        jobs=safe_jobs,
        download_usage=usage,
        download_limit_bytes=limit_bytes,
        quota_reached=(usage.get("total_bytes", 0) >= limit_bytes),
    )


def ariapp_api_sci_groups_get(self):
    """Get details of a specific science group."""
    user_info, perms = self._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = request.args.get("instrument", "").strip()
    name = request.args.get("name", "").strip()
    if not instrument or not name:
        return jsonify(success=False, error="Missing params"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    groups = auth.load_science_groups(instrument)
    groups, run_ids = self._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=self._get_instrument_run_ids(instrument),
        persist=True,
    )
    canonical_name = "All" if self._is_all_science_group(name) else name
    if canonical_name not in groups:
        return jsonify(success=True, group={"run_ids": [], "users": []})

    entry = groups[canonical_name]
    return jsonify(
        success=True,
        group={
            "run_ids": entry.get("run_ids", []),
            "users": entry.get("users", []),
        },
    )


def ariapp_api_sci_groups_refresh_run_ids(self):
    """Re-scan instrument run IDs and sync the reserved All group only."""
    user_info, perms = self._require_sci_group_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    instrument = str(data.get("instrument", "") or "").strip()
    if not instrument:
        return jsonify(success=False, error="Missing instrument"), 400

    perm = f"manage.sci_group.{instrument}"
    if perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    params = permissions_mod.load_parameters()
    valid = params.get("instruments", {}).get("value", [])
    if instrument not in valid:
        return jsonify(success=False, error="Invalid instrument"), 400

    groups = auth.load_science_groups(instrument)
    run_ids = self._get_instrument_run_ids(instrument)
    _, run_ids = self._sync_all_science_group(
        instrument,
        groups=groups,
        run_ids=run_ids,
        persist=True,
    )
    self._refresh_admin_health_after_change(user_info, perms)

    return jsonify(
        success=True, run_ids=run_ids, removed_run_ids=0, message=(
            "Run ID list refreshed. User-defined group run IDs were "
            "left unchanged; the All group was synchronized automatically."
        ),
    )


def ariapp_api_apero_profiles_test_db(self):
    """Test a database connection with the given credentials."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    resolved = self._resolve_db_payload_for_test(data)
    if not resolved.get("ok") and resolved.get("requires_tunnel_admin"):
        return jsonify(
            success=True,
            valid=False,
            requires_tunnel_admin=True,
            error=resolved.get("error", "DB tunnel required."),
            tunnel_admin_url=resolved.get("tunnel_admin_url", ""),
        )
    if not resolved.get("ok"):
        return (
            jsonify(
                success=False,
                error=resolved.get("error", "Invalid database payload"),
            ),
            400,
        )

    result = auth.validate_database_connection(
        resolved["mode"],
        resolved["host"],
        resolved["username"],
        resolved["password"],
        resolved["db_name"],
        port=resolved["port"],
        use_ssh_tunnel=resolved["use_ssh_tunnel"],
        ssh_config_host=resolved["ssh_config_host"],
        ssh_local_port=resolved["ssh_local_port"],
        ssh_remote_port=resolved["ssh_remote_port"],
        local_data_dir=str(self._resolve_local_data_dir()),
    )
    return jsonify(success=True, **result)


def ariapp_api_async_tasks_reorder(self):
    """Update task order after a drag-reorder."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = async_task_helpers.normalize_task_scope(
        data.get('instrument', '')
    )
    order_list = data.get("order", [])
    if not instrument:
        return jsonify(success=False, error="Missing instrument"), 400

    all_tasks = auth.load_async_tasks()
    inst_tasks = all_tasks.get(instrument, [])
    task_map = {t.get("id"): t for t in inst_tasks}
    ordered_ids = set(order_list)

    reordered = []
    for idx, tid in enumerate(order_list, start=1):
        if tid in task_map:
            task_map[tid]["order"] = idx
            reordered.append(task_map[tid])
    # Append tasks not mentioned in order_list
    for t in inst_tasks:
        if t.get("id") not in ordered_ids:
            reordered.append(t)

    all_tasks[instrument] = reordered
    auth.save_async_tasks(all_tasks)
    return jsonify(success=True)


def ariapp_build_sidebar_context(self, page_id, perms, user_info):
    """Build sidebar context dict for pages with side-nav top-level."""
    username = ''
    if isinstance(user_info, dict):
        username = str(user_info.get('username') or '').strip()
    perms_key = tuple(sorted(
        str(item) for item in set(perms or set())
    ))
    cache_key = (
        str(page_id or ''),
        perms_key,
        bool(user_info),
        username,
    )
    now = time.monotonic()
    with _SIDEBAR_CTX_CACHE_LOCK:
        cached = _SIDEBAR_CTX_CACHE.get(cache_key)
        if cached is not None and cached.get('expires', 0.0) > now:
            return cached.get('value', dict())

    nav_root = permissions_mod.find_full_nav_root(page_id, self.ari_pages)
    if not nav_root:
        payload = {}
        with _SIDEBAR_CTX_CACHE_LOCK:
            _SIDEBAR_CTX_CACHE[cache_key] = dict(
                expires=now + _SIDEBAR_CTX_CACHE_TTL_S,
                value=payload,
            )
        return payload

    root_def = self.ari_pages[nav_root]
    section_tree = permissions_mod.get_sidebar_tree(
        nav_root, perms, self.ari_pages, page_id
    )
    pinned_tree = permissions_mod.get_pinned_sidebar_items(
        perms,
        self.ari_pages,
        page_id,
        logged_in=(user_info is not None),
        username=(user_info or {}).get("username", ""),
    )
    seen = set()
    sidebar_tree = []
    for item in pinned_tree + section_tree:
        item_id = item.get("id", "")
        if item_id in seen:
            continue
        seen.add(item_id)
        sidebar_tree.append(item)
    payload = {
        "sidebar_root": nav_root,
        "sidebar_label": root_def.get("label", ""),
        "sidebar_icon": root_def.get("icon", ""),
        "sidebar_url": permissions_mod.page_id_to_url(nav_root),
        "sidebar_tree": sidebar_tree,
    }
    with _SIDEBAR_CTX_CACHE_LOCK:
        if len(_SIDEBAR_CTX_CACHE) > 2048:
            _SIDEBAR_CTX_CACHE.clear()
        _SIDEBAR_CTX_CACHE[cache_key] = dict(
            expires=now + _SIDEBAR_CTX_CACHE_TTL_S,
            value=payload,
        )
    return payload


def ariapp_normalize_pinned_pages(value):
    """Normalize persisted pinned pages into a clean list of dicts."""
    if not isinstance(value, list):
        return []

    normalized = []
    seen_ids = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        page_id = str(item.get("page_id", "")).strip()
        label = str(item.get("label", "")).strip()
        url = str(item.get("url", "")).strip()
        icon = str(item.get("icon", "")).strip()
        pinned_at = str(item.get("pinned_at", "")).strip()

        if not page_id or not label or not url or not url.startswith("/"):
            continue
        if page_id in seen_ids:
            continue

        seen_ids.add(page_id)
        normalized.append(
            {
                "page_id": page_id,
                "label": label,
                "url": url,
                "icon": icon or "fa-solid fa-thumbtack",
                "pinned_at": pinned_at,
            }
        )

    return normalized


def ariapp_share_download(self, token, chunk_idx):
    """Direct file download for a shared job chunk – no auth required."""
    share_info = bk.get_share_job(str(token or ""))
    if share_info is None:
        return jsonify(success=False, error="Link expired or not found"), 404
    username = share_info["username"]

    # Rate-limit check (uses basket category for share links)
    wait = dt.check_rate_limit(username, "basket")
    if wait is not None:
        return (
            jsonify(
                success=False,
                error=f"Rate limited – please wait {wait:.1f}s",
                retry_after=wait,
            ),
            429,
        )

    path = bk.get_job_chunk_path(username, share_info["job_id"], chunk_idx)
    if path is None:
        return jsonify(success=False, error="File not found"), 404

    # Track the download
    try:
        file_bytes = path.stat().st_size
    except OSError:
        file_bytes = 0
    dt.record_download(username, "basket", file_bytes, 1)

    return send_file(str(path), as_attachment=True, download_name=path.name)


def ariapp_api_db_ssh_tunnel_ensure(self):
    """Ensure selected named tunnel is active."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    tunnel_name = str(body.get("tunnel_name", "") or "").strip()
    if not tunnel_name:
        return jsonify(success=False, error="tunnel_name is required"), 400

    tunnels = self._load_db_tunnel_definitions()
    tunnel_def = tunnels.get(tunnel_name, {})
    if not isinstance(tunnel_def, dict) or not tunnel_def:
        return jsonify(success=False, error="Tunnel not found"), 404

    db_params = self._build_db_tunnel_runtime_params(tunnel_name, tunnel_def)

    try:
        host, port = apero_async._ensure_ssh_tunnel(db_params)
        status = apero_async.get_db_tunnel_status(db_params)
        return jsonify(
            success=True,
            message="DB SSH tunnel is active (or started).",
            tunnel_name=tunnel_name,
            local_host=host,
            local_port=port,
            status=status,
        )
    except Exception as exc:
        return (
            jsonify(success=False, error=f"Failed to ensure DB tunnel: {exc}"),
            500,
        )


def ariapp_spawn_admin_health_refresh(self, cache_key, user_info, perms):
    """Spawn async refresh if one is not already in progress."""
    with self._admin_health_cache_lock:
        entry = self._admin_health_cache.get(cache_key, {})
        if entry.get("in_progress", False):
            return
        self._admin_health_cache[cache_key] = {
            "health": entry.get("health", {}),
            "updated_at": entry.get("updated_at"),
            "in_progress": True,
            "perms": sorted(perms),
        }

    def _runner():
        try:
            self._refresh_admin_health_entry(cache_key, user_info, perms)
        except Exception:
            with self._admin_health_cache_lock:
                existing = self._admin_health_cache.get(cache_key, {})
                existing["in_progress"] = False
                self._admin_health_cache[cache_key] = existing

    threading.Thread(
        target=_runner,
        daemon=True,
        name="admin-health-refresh-now",
    ).start()


def ariapp_load_user_object_section_pins(self, username):
    """Load per-user object section pin order and migrate legacy users.yaml."""
    file_pins = self._normalize_object_section_pins(
        ud.list_object_section_pins(username)
    )

    users = auth.load_users()
    user = users.get(username, {})
    legacy = user.get("object_section", {}) if isinstance(user, dict) else {}
    legacy_pins = self._normalize_object_section_pins(
        legacy.get("pinned", []) if isinstance(legacy, dict) else []
    )

    pins = file_pins or legacy_pins
    if pins != file_pins:
        ud.save_object_section(username, {"pinned": pins})

    if user and legacy_pins != pins:
        section_cfg = user.get("object_section", {})
        if not isinstance(section_cfg, dict):
            section_cfg = {}
        section_cfg["pinned"] = pins
        user["object_section"] = section_cfg
        users[username] = user
        auth.save_users(users)

    return pins


def ariapp_api_user_favourite_objects_remove(self):
    """Remove one object from the current user's favourite list."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    objname = str(body.get("objname", "")).strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="profile_id and objname are required",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    for sec in sections:
        sec["items"] = [
            it for it in sec.get("items", [])
            if str(it.get("objname", "")).strip() != objname
        ]

    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=None
    )
    flat = ud.get_profile_favourite_objects(username, profile_id)
    return jsonify(
        success=True,
        favourite_objects=flat,
        sections=updated.get("sections", []),
    )


def ariapp_api_basket_get(self):
    """Return the user's basket entries (filtered to accessible run_ids)."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]
    profile_id = request.args.get("profile_id", "").strip()
    accessible_run_ids = self._all_accessible_run_ids(user_info)

    entries = bk.load_basket(username)
    # Security: only return entries the user still has access to
    entries = [
        e
        for e in entries
        if str(e.get("kw_run_id", "") or "").strip() in accessible_run_ids
    ]
    if profile_id:
        entries = [e for e in entries if e.get("profile_id") == profile_id]

    profile_cfgs = self._build_profile_cfgs(user_info)
    summary = bk.basket_summary(
        username,
        profile_cfgs,
        accessible_run_ids,
        profile_id=profile_id,
    )

    return jsonify(
        success=True, entries=entries, summary=summary, total=len(entries)
    )


def ariapp_api_admin_backups_delete_all(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json() or {}
    period = str(body.get("period", "all")).strip().lower()
    target = str(body.get("target", "both")).strip().lower()
    method_id = str(body.get("method_id", "") or "").strip() or None
    if period not in {"daily", "weekly", "all"}:
        return jsonify(success=False, error="Invalid period"), 400
    if target not in {"local", "cloud", "both"}:
        return jsonify(success=False, error="Invalid target"), 400

    try:
        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        result = bb.delete_all_backups(
            period=period,
            target=target,
            local_data_dir=local_data_dir,
            cfg=cfg,
            method_id=method_id,
        )
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, data=result)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_build_db_tunnel_runtime_params(self, tunnel_name, tunnel_def, mode):
    """Build apero_async-compatible params for one tunnel definition."""
    _ = tunnel_name
    tdef = tunnel_def if isinstance(tunnel_def, dict) else {}
    remote_host = str(tdef.get("remote_host", "") or "").strip()
    remote_port = str(tdef.get("remote_port", "") or "").strip() or "3306"
    local_port = str(tdef.get("local_port", "") or "").strip()
    ssh_host = str(tdef.get("ssh_config_host", "") or "").strip()
    ssh_mode = str(tdef.get("ssh_mode", "apero") or "apero").strip()
    return {
        "DATABASE_MODE": str(mode or "mysql+pymysql").strip()
        or "mysql+pymysql",
        "DATABASE_HOST": remote_host,
        "DATABASE_PORT": local_port,
        "DATABASE_USER": "",
        "DATABASE_USERNAME": "",
        "DATABASE_PASSWORD": "",
        "DATABASE_NAME": "",
        "DATABASE_USE_SSH_TUNNEL": True,
        "DATABASE_SSH_CONFIG_HOST": ssh_host,
        "DATABASE_SSH_LOCAL_PORT": local_port,
        "DATABASE_SSH_REMOTE_PORT": remote_port,
        "DATABASE_SSH_SIMPLE_MODE": ssh_mode == "simple",
        # DB setup management supports multiple simultaneously active
        # tunnels; do not force-close other definitions for this path.
        "DATABASE_SSH_ALLOW_MULTIPLE": True,
        "LOCAL_DATA_DIR": str(self._resolve_local_data_dir()),
    }


def ariapp_list_ssh_config_hosts():
    """Return host aliases from ~/.ssh/config (excluding wildcards)."""
    cfg_path = Path.home() / ".ssh" / "config"
    if not cfg_path.exists() or not cfg_path.is_file():
        return []

    hosts: set = set()
    try:
        with open(cfg_path, "r", encoding="utf-8", errors="replace") as fobj:
            for raw_line in fobj:
                line = str(raw_line).strip()
                if not line or line.startswith("#"):
                    continue
                if not line.lower().startswith("host "):
                    continue
                parts = line.split()[1:]
                for token in parts:
                    tval = str(token or "").strip()
                    if not tval:
                        continue
                    if any(ch in tval for ch in ["*", "?", "!"]):
                        continue
                    hosts.add(tval)
    except Exception:
        return []

    return sorted(hosts)


def ariapp_api_user_object_sections_toggle(self):
    """Toggle a section id in the global object page pinned list."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json() or {}
    section_id = str(body.get("section_id", "")).strip()
    if not section_id:
        return jsonify(success=False, error="section_id is required"), 400
    section_id = self._normalize_object_section_pins([section_id])
    if not section_id:
        return jsonify(success=False, error="Invalid section_id"), 400
    section_id = section_id[0]

    username = user_info["username"]
    pinned = self._load_user_object_section_pins(username)
    if section_id in pinned:
        pinned = [sid for sid in pinned if sid != section_id]
        is_pinned = False
    else:
        pinned.append(section_id)
        is_pinned = True
    self._save_user_object_section_pins(username, pinned)
    return jsonify(
        success=True, pinned=is_pinned, object_section={"pinned": pinned}
    )


def ariapp_api_user_calendar_list(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    instrument = request.args.get("instrument", "").strip()
    if instrument == "__all__":
        instruments = perms.get_user_instruments(
            user_info.get('groups', []), self.ari_groups
        )
        if not instruments:
            params = perms.load_parameters()
            all_instr = params.get(
                'instruments', {}
            ).get('value', [])
            instruments = list(all_instr)

        events = list(ud.list_events(user_info["username"]))
        for inst in instruments:
            inst_events = ud.load_instrument_calendar(inst).get(
                "events", []
            )
            for ev in inst_events:
                tagged = dict(ev)
                tagged["_source"] = inst
                tagged["category"] = "instrument"
                events.append(tagged)
        events = ud.dedup_events(events)
    elif instrument:
        events = ud.get_merged_calendar(user_info["username"], instrument)
    else:
        events = ud.list_events(user_info["username"])
    return jsonify(success=True, events=events)


def ariapp_api_admin_backups_delete(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json() or {}
    rel = str(body.get("relative_path", "")).strip()
    target = str(body.get("target", "both")).strip().lower()
    method_id = str(body.get("method_id", "") or "").strip() or None
    if target not in {"local", "cloud", "both"}:
        return jsonify(success=False, error="Invalid target"), 400
    if not rel:
        return jsonify(success=False, error="relative_path is required"), 400

    try:
        cfg = bb.load_backup_config()
        local_data_dir = self._resolve_local_data_dir()
        result = bb.delete_backup(
            rel,
            target=target,
            local_data_dir=local_data_dir,
            cfg=cfg,
            method_id=method_id,
        )
        self._refresh_admin_health_after_change(user_info, perms)
        return jsonify(success=True, data=result)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_admin_sshfs_mounts_add(self):
    """Add a new SSHFS mount."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    data = request.get_json() or {}
    mount_config = {
        "connection_mode": data.get("connection_mode", "direct").strip(),
        "ssh_config_host": data.get("ssh_config_host", "").strip(),
        "name": data.get("name", "").strip(),
        "remote_host": data.get("remote_host", "").strip(),
        "remote_path": data.get("remote_path", "").strip(),
        "local_mount": data.get("local_mount", "").strip(),
        "ssh_key": data.get("ssh_key", "").strip(),
        "remote_user": data.get("remote_user", "").strip() or "root",
        "manual_mode": data.get("manual_mode", False),
    }

    result = sb.add_mount(mount_config)
    if result["ok"]:
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_update(self, mount_name):
    """Update an existing SSHFS mount."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    data = request.get_json() or {}
    mount_config = {
        "connection_mode": data.get("connection_mode", "direct").strip(),
        "ssh_config_host": data.get("ssh_config_host", "").strip(),
        "name": data.get("name", "").strip(),
        "remote_host": data.get("remote_host", "").strip(),
        "remote_path": data.get("remote_path", "").strip(),
        "local_mount": data.get("local_mount", "").strip(),
        "ssh_key": data.get("ssh_key", "").strip(),
        "remote_user": data.get("remote_user", "").strip() or "root",
        "manual_mode": data.get("manual_mode", False),
    }

    result = sb.update_mount(mount_name, mount_config)
    if result.get("ok"):
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_build_admin_sshfs_context(self, perms):
    """Build context for admin SSHFS management page."""
    # Keep initial page render fast.  Live mount checks can be slow on
    # stale/broken SSHFS targets, so we only preload static config here
    # and let the page fetch live status asynchronously via API.
    try:
        cfg = sb.load_sshfs_config()
        mounts_data = cfg.get("mounts", []) if isinstance(cfg, dict) else []
        if not isinstance(mounts_data, list):
            mounts_data = []
    except Exception:
        mounts_data = []

    try:
        ssh_keys = sb.list_ssh_keys()
        ssh_keys_data = (
            ssh_keys.get("keys", []) if isinstance(ssh_keys, dict) else []
        )
        if not isinstance(ssh_keys_data, list):
            ssh_keys_data = []
    except Exception:
        ssh_keys_data = []

    return {
        "can_manage": (
            "manage.admin.sshfs_setup" in perms or "view.admin" in perms
        ),
        "mounts_data": mounts_data,
        "ssh_keys_data": ssh_keys_data,
    }


def ariapp_api_async_tasks_delete(self):
    """Delete an async task configuration."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = async_task_helpers.normalize_task_scope(
        data.get('instrument', '')
    )
    task_id = data.get("id", "").strip()
    if not instrument or not task_id:
        return jsonify(success=False, error="Missing fields"), 400

    all_tasks = auth.load_async_tasks()
    inst_tasks = all_tasks.get(instrument, [])
    new_tasks = [t for t in inst_tasks if t.get("id") != task_id]
    if len(new_tasks) == len(inst_tasks):
        return jsonify(success=False, error="Task not found"), 404

    all_tasks[instrument] = new_tasks
    auth.save_async_tasks(all_tasks)
    task_runner.clear_instance(task_id)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_async_tasks_toggle(self):
    """Toggle a task's active/inactive state."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = async_task_helpers.normalize_task_scope(
        data.get('instrument', '')
    )
    task_id = data.get("id", "").strip()
    if not instrument or not task_id:
        return jsonify(success=False, error="Missing fields"), 400

    all_tasks = auth.load_async_tasks()
    inst_tasks, _ = self._merge_async_task_catalog(instrument, all_tasks)

    def _as_bool(value, default=True):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            text = value.strip().lower()
            if text in {"", "none", "null"}:
                return default
            if text in {"1", "true", "yes", "on", "y", "t"}:
                return True
            if text in {"0", "false", "no", "off", "n", "f"}:
                return False
        return default

    for t in inst_tasks:
        if t.get("id") == task_id:
            current_active = _as_bool(t.get("active", True), True)
            t["active"] = not current_active
            all_tasks[instrument] = inst_tasks
            auth.save_async_tasks(all_tasks)
            self._refresh_admin_health_after_change(user_info, perms)
            return jsonify(success=True, active=t["active"])

    return jsonify(success=False, error="Task not found"), 404


def ariapp_api_user_favourite_objects_last_opened(self):
    """Update last-opened object for a profile for the current user."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    profile_id = str(body.get("profile_id", "")).strip()
    objname = str(body.get("objname", "")).strip()
    if not profile_id or not objname:
        return (
            jsonify(
                success=False,
                error="profile_id and objname are required",
            ),
            400,
        )

    username = user_info["username"]
    payload = ud.get_profile_fav_sections(username, profile_id)
    sections = payload.get("sections", [])
    updated = ud.save_profile_fav_sections(
        username, profile_id, sections, last_object=objname
    )
    flat = ud.get_profile_favourite_objects(username, profile_id)
    return jsonify(success=True, favourite_objects=flat)


def ariapp_api_basket_jobs_extend(self):
    """Extend the expiry of a compilation job by 24 hours."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id", "") or "").strip()
    if not job_id:
        return jsonify(success=False, error="job_id is required"), 400

    expiry_hours = data.get("expiry_hours", None)
    username = user_info["username"]
    result = bk.extend_download_job(username, job_id)
    if expiry_hours is not None:
        result = bk.set_download_job_expiry(username, job_id, expiry_hours)
    if not result.get("success"):
        return jsonify(success=False, error=result.get("error", "Could not extend job")), 400
    return jsonify(success=True, expires_at=result.get("expires_at"))


def ariapp_api_basket_jobs_expiry(self):
    """Set a compilation job's expiry duration."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id", "") or "").strip()
    expiry_hours = data.get("expiry_hours", "")
    if not job_id:
        return jsonify(success=False, error="job_id is required"), 400

    username = user_info["username"]
    result = bk.set_download_job_expiry(username, job_id, expiry_hours)
    if not result.get("success"):
        return jsonify(success=False, error=result.get("error", "Could not set expiry")), 400
    return jsonify(success=True, expires_at=result.get("expires_at"))


def ariapp_api_basket_jobs_remove(self):
    """Remove one completed/failed compilation job for the user."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id", "") or "").strip()
    if not job_id:
        return jsonify(success=False, error="job_id is required"), 400

    username = user_info["username"]
    result = bk.remove_download_job(username, job_id)
    if not result.get("success"):
        return (
            jsonify(
                success=False, error=result.get("error", "Could not remove job")
            ),
            400,
        )
    usage = bk.get_downloads_usage(username)
    limit_bytes = bk.get_downloads_storage_limit_bytes(user_info.get("groups"))
    return jsonify(
        success=True,
        removed=result.get("removed", 0),
        download_usage=usage,
        download_limit_bytes=limit_bytes,
        quota_reached=(usage.get("total_bytes", 0) >= limit_bytes),
    )


def ariapp_api_apero_profiles_reorder(self):
    """Update the DISPLAY_ORDER of profiles after drag reorder."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    order_list = data.get("order", [])
    if not instrument or not order_list:
        return jsonify(success=False, error="Missing fields"), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    inst_profiles = all_profiles.get(instrument, {})

    for idx, name in enumerate(order_list, start=1):
        if name in inst_profiles:
            inst_profiles[name]["DISPLAY_ORDER"] = idx

    all_profiles[instrument] = inst_profiles
    auth.save_apero_profiles(all_profiles)
    return jsonify(success=True)


def ariapp_api_admin_calendar_save(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    if not instrument:
        return jsonify(success=False, error="instrument required"), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    event = {
        "id": str(body.get("id", "")).strip(),
        "title": str(body.get("title", "")).strip(),
        "date": str(body.get("date", "")).strip(),
        "time": str(body.get("time", "")).strip(),
        "color": str(body.get("color", "#7b5ea7")).strip(),
        "category": "instrument",
        "recurrence": str(body.get("recurrence", "none")).strip(),
        "status": str(body.get("status", "confirmed")).strip(),
        "timezone": str(body.get("timezone", "UTC")).strip(),
    }
    if not event["title"] or not event["date"]:
        return jsonify(success=False, error="title and date required"), 400
    saved = ud.save_instrument_event(instrument, event)
    return jsonify(success=True, event=saved)


def ariapp_api_admin_backups_download(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json() or {}
    relative_path = str(body.get("relative_path", "")).strip()
    method_id = str(body.get("method_id", "") or "").strip() or None
    if not relative_path:
        return jsonify(success=False, error="relative_path is required."), 400

    cfg = bb.load_backup_config()
    local_data_dir = self._resolve_local_data_dir()
    result = bb.download_cloud_backup(
        relative_path,
        local_data_dir=local_data_dir,
        cfg=cfg,
        method_id=method_id,
    )

    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(
        success=result.get("ok", False),
        path=result.get("path"),
        error=result.get("error"),
    )


def ariapp_doc_upload_image(self):
    """Handle image upload for the doc editor."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Not logged in"), 401

    page_ref = str(request.form.get('page_ref', '') or '').strip('/')
    perms = permissions_mod.resolve_user_permissions(
        user_info['groups'], self.ari_groups
    )
    if not doc_views_helpers._doc_edit_allowed(perms, page_ref):
        return jsonify(success=False, error='No permission'), 403

    if 'image' not in request.files:
        return jsonify(success=False, error='No file'), 400

    img = request.files['image']
    if not img.filename:
        return jsonify(success=False, error='Empty filename'), 400

    filename = docs.save_uploaded_image(page_ref, img.filename, img.read())
    return jsonify(success=True, filename=filename)


def ariapp_api_db_ssh_tunnel_list(self):
    """List DB tunnel definitions for setup UI and profile dropdowns."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    tunnels = self._load_db_tunnel_definitions()
    rows = []
    for name in sorted(tunnels.keys()):
        tdef = tunnels.get(name, {})
        if not isinstance(tdef, dict):
            continue
        test_user = str(
            tdef.get(
                "DB_USERNAME_TEST", tdef.get("DATABASE_USERNAME", "")
            )
            or ""
        ).strip()
        test_pass = str(
            tdef.get(
                "DB_PASSWORD_TEST", tdef.get("DATABASE_PASSWORD", "")
            )
            or ""
        )
        test_db_name = str(
            tdef.get("DB_NAME_TEST", tdef.get("DATABASE_NAME", "")) or ""
        ).strip()
        rows.append(
            {
                "name": name,
                "ssh_config_host": str(
                    tdef.get("ssh_config_host", "") or ""
                ).strip(),
                "remote_host": str(tdef.get("remote_host", "") or "").strip(),
                "remote_port": str(tdef.get("remote_port", "") or "").strip()
                or "3306",
                "local_port": str(tdef.get("local_port", "") or "").strip(),
                "DB_USERNAME_TEST": test_user,
                "DB_PASSWORD_TEST": test_pass,
                "DB_NAME_TEST": test_db_name,
                # Legacy aliases kept for existing UI/API consumers.
                "DATABASE_USERNAME": test_user,
                "DATABASE_PASSWORD": test_pass,
                "DATABASE_NAME": test_db_name,
                "notes": str(tdef.get("notes", "") or "").strip(),
            }
        )
    return jsonify(success=True, tunnels=rows)


def ariapp_api_user_todo_reorder(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}

    if str(body.get("action", "")).strip() == "metadata":
        kind = str(body.get("kind", "")).strip()
        op = str(body.get("op", "")).strip()
        value = str(body.get("value", "")).strip()
        if kind not in {"projects", "tags"}:
            return (
                jsonify(success=False, error="kind must be projects or tags"),
                400,
            )
        if op not in {"add", "remove"}:
            return jsonify(success=False, error="op must be add or remove"), 400
        metadata = ud.manage_todo_metadata(
            user_info["username"], kind, op, value
        )
        return jsonify(success=True, metadata=metadata)

    ordered_ids = body.get("ids", [])
    if not isinstance(ordered_ids, list):
        return jsonify(success=False, error="ids must be a list"), 400
    ordered_ids = [str(i) for i in ordered_ids]
    items = ud.reorder_todo_items(user_info["username"], ordered_ids)
    return jsonify(success=True, items=items)


def ariapp_build_admin_download_mgmt_context(self, perms):
    """Build context for admin download-management page."""
    settings = dt.load_settings()
    api_usage = dt.list_all_usage("api")
    basket_usage = dt.list_all_usage("basket")
    for row in api_usage:
        row["total_size_fmt"] = dt.format_bytes(row["total_bytes"])
        row["last_download_fmt"] = row["last_download_at"] or "Never"
    for row in basket_usage:
        row["total_size_fmt"] = dt.format_bytes(row["total_bytes"])
        row["last_download_fmt"] = row["last_download_at"] or "Never"
    api_total_bytes = sum(r["total_bytes"] for r in api_usage)
    basket_total_bytes = sum(r["total_bytes"] for r in basket_usage)
    return {
        "can_manage": "view.admin" in perms,
        "settings": settings,
        "api_usage": api_usage,
        "basket_usage": basket_usage,
        "api_total_size": dt.format_bytes(api_total_bytes),
        "api_total_files": sum(r["total_files"] for r in api_usage),
        "basket_total_size": dt.format_bytes(basket_total_bytes),
        "basket_total_files": sum(r["total_files"] for r in basket_usage),
    }


def ariapp_save_health_cache_to_disk(self):
    """Persist current in-memory admin health cache to disk."""
    try:
        with self._admin_health_cache_lock:
            snapshot = dict(self._admin_health_cache)
        serializable = {}
        for key, entry in snapshot.items():
            updated_at = entry.get("updated_at")
            serializable[key] = {
                "health": entry.get("health", {}),
                "updated_at": (updated_at.isoformat() if updated_at else None),
                "perms": entry.get("perms", []),
            }
        self._admin_health_cache_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._admin_health_cache_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(serializable, fh)
        tmp.replace(self._admin_health_cache_file)
    except Exception:
        pass


def ariapp_api_user_favourite_objects_get(self):
    """Get favourites and last-opened object for a profile."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    profile_id = str(request.args.get("profile_id", "")).strip()
    if not profile_id:
        return jsonify(success=False, error="profile_id is required"), 400

    objname = str(request.args.get("objname", "")).strip()
    username = user_info["username"]
    sec_payload = ud.get_profile_fav_sections(username, profile_id)
    flat = ud.get_profile_favourite_objects(username, profile_id)
    result = {
        "profile_id": profile_id,
        "favourites": flat.get("favourites", []),
        "last_object": flat.get("last_object", ""),
        "sections": sec_payload.get("sections", []),
    }
    if objname:
        result["is_favourite"] = objname in result["favourites"]
    return jsonify(success=True, favourite_objects=result)


def ariapp_api_user_db_access_health_check(self):
    """Run User DB Access health check and return detailed diagnostics."""
    user_info, perms = self._require_user_db_access_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    try:
        report = self._build_user_db_access_health_report(user_info)
        instrument = request.args.get("instrument", "").strip()
        profile_id = request.args.get("profile_id", "").strip()
        selected = None
        if instrument and profile_id:
            for row in report.get("profiles", []):
                if str(row.get("instrument", "")).strip() == instrument and (
                    str(row.get("profile_id", "")).strip() == profile_id
                ):
                    selected = row
                    break

        return jsonify(success=True, report=report, selected=selected)
    except Exception as exc:
        return (
            jsonify(
                success=False,
                error=f"User DB access health check failed: {exc}",
            ),
            500,
        )


def ariapp_api_database_setup_local_db_list(self):
    """List reusable local database definitions."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.database_setup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    defs = self._load_local_db_definitions()
    rows = []
    for name in sorted(defs.keys()):
        item = defs.get(name, {})
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "name": name,
                "DATABASE_MODE": str(
                    item.get("DATABASE_MODE", "") or ""
                ).strip()
                or "mysql+pymysql",
                "DATABASE_HOST": str(
                    item.get("DATABASE_HOST", "") or ""
                ).strip(),
                "DATABASE_PORT": str(
                    item.get("DATABASE_PORT", "") or ""
                ).strip()
                or "3306",
                "DATABASE_USERNAME": str(
                    item.get("DATABASE_USERNAME", "") or ""
                ).strip(),
                "DATABASE_PASSWORD": str(
                    item.get("DATABASE_PASSWORD", "") or ""
                ),
                "DATABASE_NAME": str(
                    item.get("DATABASE_NAME", "") or ""
                ).strip(),
                "notes": str(item.get("notes", "") or "").strip(),
            }
        )
    return jsonify(success=True, local_databases=rows)


def ariapp_api_user_todo_save(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    item = {
        "id": str(body.get("id", "")).strip(),
        "title": str(body.get("title", "")).strip(),
        "status": str(body.get("status", "")).strip(),
        "size": str(body.get("size", "md")).strip(),
        "priority": body.get("priority", 0),
        "date_added": str(body.get("date_added", "")).strip(),
        "created": str(body.get("created", "")).strip(),
        "projects": body.get("projects", []),
        "tags": body.get("tags", []),
        "comments": str(body.get("comments", "") or ""),
        "link_url": str(body.get("link_url", "") or "").strip(),
        "done": bool(body.get("done", False)),
    }
    if not item["title"]:
        return jsonify(success=False, error="title required"), 400
    saved = ud.save_todo_item(user_info["username"], item)
    return jsonify(success=True, item=saved)


def ariapp_api_admin_sshfs_interactive_start_test(self):
    """Start an interactive SSH test session with PTY."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    from apero_ri.core.sshfs_interactive import start_interactive_test

    body = request.get_json(silent=True) or {}
    result = start_interactive_test(
        connection_mode=body.get("connection_mode", "direct"),
        remote_host=body.get("remote_host", ""),
        remote_user=body.get("remote_user", ""),
        ssh_config_host=body.get("ssh_config_host", ""),
        remote_path=body.get("remote_path", ""),
        ssh_key_name=body.get("ssh_key", ""),
    )
    return jsonify(**result)


def ariapp_build_admin_backup_context(self, perms):
    """Build context for admin backup settings page."""
    import json as _json

    cfg = bb.load_backup_config()
    providers = bb.PROVIDER_DEFAULTS
    current_provider = str(cfg.get("provider", "local_only")).strip()
    if current_provider not in providers:
        current_provider = "local_only"

    local_data_dir = self._resolve_local_data_dir()
    inventory = bb.backup_inventory(
        local_data_dir=local_data_dir,
        cfg=cfg,
        method_id=cfg.get("active_method_id"),
    )

    from flask import request as _req
    _is_https = _req.is_secure or _req.headers.get(
        "X-Forwarded-Proto", ""
    ).lower() == "https"
    _insecure_ok = bool(
        os.environ.get("ARI_ALLOW_INSECURE_OAUTH", "")
    )
    oauth_insecure_warning = (
        not _is_https and not _insecure_ok
    )

    return {
        "backup_cfg": cfg,
        "providers": providers,
        "providers_json": _json.dumps(providers),
        "current_provider": current_provider,
        "can_manage": (
            "manage.admin.backup_setup" in perms
            or "manage.admin.backup" in perms
        ),
        "backup_inventory": inventory,
        "oauth_insecure_warning": oauth_insecure_warning,
    }


def ariapp_api_admin_cache_reset_timings(self):
    """Zero timing stats for a profile without deleting cached data."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.admin" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    instrument = str(body.get("instrument", "")).strip()
    profile_id = str(body.get("profile_id", "")).strip()
    if not instrument or not profile_id:
        return (
            jsonify(
                success=False,
                error="Missing instrument or profile_id",
            ),
            400,
        )

    from apero_ri.core.plot_cache import (
        _profile_dir,
        load_cache_config,
        resolve_cache_root,
        write_timing_reset,
    )

    data_dir = self._resolve_local_data_dir()
    cfg = load_cache_config(data_dir)
    cache_root = resolve_cache_root(data_dir, cfg)
    pdir = _profile_dir(cache_root, instrument, profile_id)
    write_timing_reset(pdir)
    return jsonify(success=True)


def ariapp_api_admin_cache_save(self):
    """Save cache settings (enable/disable, directory)."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.admin" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    from apero_ri.core.plot_cache import (
        load_cache_config,
        save_cache_config,
    )

    data_dir = self._resolve_local_data_dir()
    body = request.get_json(silent=True) or {}
    cfg = load_cache_config(data_dir)
    if "enabled" in body:
        cfg["enabled"] = bool(body["enabled"])
    if "cache_dir" in body:
        cfg["cache_dir"] = str(body["cache_dir"]).strip()
    save_cache_config(cfg, data_dir)
    return jsonify(success=True)


def ariapp_api_admin_health_config_save(self):
    """Persist health-status UI config."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(success=False, error="Forbidden"), 403

    data = request.get_json() or {}
    refresh_frequency = (
        str(data.get("refresh_frequency", "manual")).strip().lower()
    )
    if refresh_frequency not in {"manual", "5m", "15m", "1h"}:
        return jsonify(success=False, error="Invalid refresh_frequency"), 400

    auth.save_admin_health_config({"refresh_frequency": refresh_frequency})
    return jsonify(
        success=True,
        config={"refresh_frequency": refresh_frequency},
    )


def ariapp_api_basket_compile_status(self, job_id):
    """Get the status of a compilation job."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]
    meta = bk.get_job_status(username, job_id)
    if meta is None:
        return jsonify(success=False, error="Job not found"), 404
    # Strip internal file paths from response for security
    safe_meta = {k: v for k, v in meta.items() if k != "chunks"}
    safe_chunks = []
    for chunk in meta.get("chunks", []):
        safe_chunks.append(
            {
                "index": chunk.get("index"),
                "filename": chunk.get("filename"),
                "size_bytes": chunk.get("size_bytes"),
                "file_count": chunk.get("file_count"),
            }
        )
    safe_meta["chunks"] = safe_chunks
    return jsonify(success=True, job=safe_meta)


def ariapp_api_admin_health_update(self):
    """Force-refresh cached admin health and return updated metadata."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(success=False, error="Forbidden"), 403

    health, updated_at, _ = self._get_admin_health(
        user_info=user_info,
        perms=perms,
        force=True,
        allow_async_refresh=False,
    )
    return jsonify(
        success=True,
        updated_at=self._format_utc_datetime(updated_at),
        health=health,
    )


def ariapp_api_admin_audit_log(self):
    """Return recent admin audit log entries (super-admin only)."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms or not auth.user_is_super_admin(
        user_info.get("groups", [])
    ):
        return jsonify(success=False, error="Forbidden"), 403

    data = request.get_json(silent=True) or {}
    limit = max(1, min(1000, int(data.get("limit", 200) or 200)))
    actor = str(data.get("actor", "") or "").strip() or None
    action_prefix = str(data.get("action_prefix", "") or "").strip() or None
    target = str(data.get("target", "") or "").strip() or None

    entries = audit_log.query(
        limit=limit, actor=actor, action_prefix=action_prefix, target=target
    )
    return jsonify(success=True, entries=entries, count=len(entries))


def ariapp_api_admin_health_history(self):
    """Return recent admin-health snapshots/trends (super-admin only)."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms or not auth.user_is_super_admin(
        user_info.get("groups", [])
    ):
        return jsonify(success=False, error="Forbidden"), 403

    data = request.get_json(silent=True) or {}
    limit = max(1, min(1000, int(data.get("limit", 200) or 200)))
    key = str(data.get("key", "") or "").strip() or None

    entries = health_history.query(limit=limit, key=key)
    return jsonify(success=True, entries=entries, count=len(entries))


# Whitelist of individual health keys that page-level checks are
# allowed to patch directly.  Only keys that mirror a page-owned
# check are listed here.
_PATCHABLE_HEALTH_KEYS = frozenset({
    "home.admin_portal.email",
    "home.admin_portal.backup_settings",
    "home.admin_portal.sshfs_management",
})


def ariapp_api_admin_health_patch(self):
    """Patch a single health-cache entry with a page-level result.

    Accepts ``{key, status, message}`` in the JSON body.  Only
    writes to pre-approved keys so pages cannot spoof unrelated
    health entries.
    """
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(success=False, error="Forbidden"), 403
    body = request.get_json() or {}
    key = str(body.get("key", "")).strip()
    status = str(body.get("status", "")).strip()
    message = str(body.get("message", "")).strip()
    if key not in _PATCHABLE_HEALTH_KEYS:
        return jsonify(
            success=False,
            error=f"Key '{key}' is not patchable",
        ), 400
    if status not in ("ok", "warning", "error"):
        return jsonify(
            success=False,
            error="status must be one of: ok, warning, error",
        ), 400
    cache_key = self._admin_health_cache_key(perms)
    with self._admin_health_cache_lock:
        entry = self._admin_health_cache.get(cache_key)
        if entry is None:
            return jsonify(
                success=False, error="No health cache entry found"
            ), 404
        entry["health"][key] = {
            "status": status,
            "message": message,
            "duration_s": 0.0,
        }
    return jsonify(success=True)


def ariapp_load_user_pins(self, username):
    """Load pins from per-user pins.yaml and migrate legacy users.yaml pins."""
    pins_data = ud.load_pins(username)
    file_pins = self._normalize_pinned_pages(pins_data.get("pins", []))

    users = auth.load_users()
    user = users.get(username, {})
    legacy_pins = self._normalize_pinned_pages(user.get("pinned_pages", []))

    pins = file_pins or legacy_pins
    if pins != file_pins:
        ud.save_pins(username, {"pins": pins})

    # Keep legacy field synchronized for backward compatibility.
    if user and legacy_pins != pins:
        user["pinned_pages"] = pins
        users[username] = user
        auth.save_users(users)

    return pins


def ariapp_build_finder_max_payload(
    self, profile, objname, obj_props, preset, band_idx
):
    """Build the plot_payload dict for a finder chart maximize page."""
    from apero_ri.core.object_finder import generate_finder_charts

    result = generate_finder_charts(obj_props, preset)
    if not result.get("success") or not result.get("images"):
        return {
            "has_plot": False,
            "script": "",
            "div": "",
            "message": result.get("error", "Generation failed."),
        }
    idx = max(0, min(band_idx, len(result["images"]) - 1))
    img_b64 = result["images"][idx]
    band_label = result.get("titles", result["bands"])[idx]
    div_html = (
        f'<div style="display:flex;align-items:center;'
        f'justify-content:center;width:100%;height:100%;">'
        f'<img src="data:image/png;base64,{img_b64}" '
        f'alt="Finder Chart – {band_label}" '
        f'style="max-width:100%;max-height:100%;object-fit:contain;">'
        f"</div>"
    )
    return {"has_plot": True, "script": "", "div": div_html, "message": ""}


def ariapp_api_user_account_get(self):
    """Get current user's account profile."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    username = user_info["username"]
    users = auth.load_users()
    user = users.get(username, {})
    return jsonify(
        success=True,
        account={
            "username": username,
            "first_names": user.get("first_names", ""),
            "last_name": user.get("last_name", ""),
            "emails": user.get("emails", []),
            "primary_email": user.get("primary_email", ""),
            "email_verified": bool(user.get("email_verified", False)),
            "institutions": user.get("institutions", []),
            "primary_institution": user.get("primary_institution", ""),
        },
    )


def ariapp_api_profiles_list(self):
    """Return list of accessible profile IDs and basic metadata."""
    user_info = self._get_api_user()
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.data_portal" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    accessible = auth.get_accessible_profiles(user_info, self.ari_groups)
    profiles = []
    for prof in accessible:
        profiles.append(
            {
                "profile_id": prof["profile_id"],
                "instrument": prof.get("instrument", ""),
                "label": prof.get("label", prof["profile_id"]),
            }
        )
    return jsonify(success=True, profiles=profiles)


def ariapp_resolve_profile_db_test_target(
    self,
    mode,
    host,
    port,
    username,
    password,
    db_name,
    use_ssh_tunnel,
    ssh_config_host,
    ssh_local_port,
    ssh_remote_port,
):
    return apero_profiles_api_helpers.resolve_profile_db_test_target(
        self,
        mode=mode,
        host=host,
        port=port,
        username=username,
        password=password,
        db_name=db_name,
        use_ssh_tunnel=use_ssh_tunnel,
        ssh_config_host=ssh_config_host,
        ssh_local_port=ssh_local_port,
        ssh_remote_port=ssh_remote_port,
    )


def ariapp_api_user_calendar_save(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    event = {
        "id": str(body.get("id", "")).strip(),
        "title": str(body.get("title", "")).strip(),
        "date": str(body.get("date", "")).strip(),
        "time": str(body.get("time", "")).strip(),
        "color": str(body.get("color", "#4a90d9")).strip(),
        "category": str(body.get("category", "personal")).strip(),
        "recurrence": str(body.get("recurrence", "none")).strip(),
        "status": str(body.get("status", "confirmed")).strip(),
        "timezone": str(body.get("timezone", "UTC")).strip(),
    }
    if not event["title"] or not event["date"]:
        return jsonify(success=False, error="title and date required"), 400
    saved = ud.save_event(user_info["username"], event)
    return jsonify(success=True, event=saved)


def ariapp_api_admin_backups_sync_from_cloud(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(success=False, error="Insufficient permissions"), 403

    cfg = bb.load_backup_config()
    local_data_dir = self._resolve_local_data_dir()
    body = request.get_json(silent=True) or {}
    method_id = str(body.get("method_id", "") or "").strip() or None
    result = bb.sync_cloud_backups_to_local(
        local_data_dir=local_data_dir, cfg=cfg, method_id=method_id
    )

    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(
        success=result.get("ok", False),
        downloaded=result.get("downloaded", 0),
        error=result.get("error"),
    )


def ariapp_api_admin_sshfs_mounts_test_connection(self):
    """Test SSH authentication/path before saving a mount."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    data = request.get_json() or {}
    result = sb.test_ssh_connection(
        connection_mode=data.get("connection_mode", "direct"),
        remote_host=data.get("remote_host", ""),
        remote_user=data.get("remote_user", ""),
        ssh_config_host=data.get("ssh_config_host", ""),
        remote_path=data.get("remote_path", ""),
        ssh_key_name=data.get("ssh_key", ""),
    )
    return jsonify(**result)


def ariapp_api_admin_sshfs_interactive_send(self):
    """Send input to an interactive SSH/SSHFS session."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    from apero_ri.core.sshfs_interactive import send_input

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    data = str(body.get("data", ""))
    if not token:
        return jsonify(ok=False, error="token required"), 400
    result = send_input(token, data)
    return jsonify(**result)


def ariapp_get_arguments():
    """Parse command-line arguments for the ARI server."""
    parser = argparse.ArgumentParser(description="APERO reduction interface")
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Override data directory (default: ~/.ari)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6666,
        help="Port to run the server on (default: 6666)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="auto",
        help=(
            "Host binding (default: auto; prefers :: for "
            "localhost, falls back to 0.0.0.0)"
        ),
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help=(
            "Serve with the waitress production WSGI server instead of "
            "the Flask development server"
        ),
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=16,
        help=(
            "Worker thread count for the production server "
            "(default: 16; only used with --production)"
        ),
    )
    return parser.parse_args()


def ariapp_build_data_portal_sidebar_tree(
    self,
    accessible_profiles,
    active_page_id,
    user_permissions,
    user_info,
    current_profile_id,
    objname,
    include_children,
):
    """Build data portal sidebar tree from pages.yaml templates."""
    return app_sidebar.build_data_portal_sidebar_tree(
        self,
        accessible_profiles=accessible_profiles,
        active_page_id=active_page_id,
        user_permissions=user_permissions,
        user_info=user_info,
        current_profile_id=current_profile_id,
        objname=objname,
        include_children=include_children,
    )


def ariapp_api_admin_dm_save_settings(self):
    """Save download management settings."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.admin" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json(silent=True) or {}
    updates = {}
    for key in (
        "api_rate_limit_seconds",
        "basket_rate_limit_seconds",
        "basket_max_archive_gb",
    ):
        if key in body:
            updates[key] = float(body[key])
    dt.save_settings(updates)
    return jsonify(success=True)


def ariapp_doc_save_view(self, page_ref):
    """Save edited markdown content for a doc page."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Not logged in"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    clean_ref = str(page_ref or "").strip("/")
    if not doc_views_helpers._doc_edit_allowed(perms, clean_ref):
        return jsonify(success=False, error="No permission"), 403

    data = request.get_json()
    if not data or "content" not in data or "version" not in data:
        return jsonify(success=False, error="Missing data"), 400

    docs.save_doc_content(clean_ref, data["version"], data["content"])
    return jsonify(success=True)


def ariapp_api_database_setup_local_db_delete(self):
    """Delete one reusable local database definition."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.database_setup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "") or "").strip()
    if not name:
        return jsonify(success=False, error="name is required"), 400

    defs = self._load_local_db_definitions()
    if name not in defs:
        return (
            jsonify(success=False, error="Local database definition not found"),
            404,
        )

    del defs[name]
    self._save_local_db_definitions(defs)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_api_admin_links_update(self):
    user_info, perms = self._require_admin_links_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    new_name = str(body.get("new_name", name)).strip()
    url = str(body.get("url", "")).strip()
    if not instrument or not section or not name or not url:
        return (
            jsonify(
                success=False,
                error="instrument, section, name and url required",
            ),
            400,
        )
    links_perm = f"manage.admin.links.{instrument}"
    if links_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    data = ud.update_instrument_link(
        instrument,
        section,
        name,
        new_name,
        url,
        str(body.get("type", "")),
        str(body.get("description", "")),
    )
    return jsonify(success=True, data=data)


def ariapp_api_admin_sshfs_interactive_start_mount(self):
    """Start an interactive SSHFS mount session with PTY."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    from apero_ri.core.sshfs_interactive import start_interactive_mount

    body = request.get_json(silent=True) or {}
    mount_name = str(body.get("mount_name", "")).strip()
    if not mount_name:
        return jsonify(ok=False, error="mount_name required"), 400
    result = start_interactive_mount(mount_name)
    return jsonify(**result)


def ariapp_api_admin_sshfs_interactive_poll(self):
    """Poll output from an interactive SSH/SSHFS session."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    from apero_ri.core.sshfs_interactive import poll_session

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    if not token:
        return jsonify(ok=False, error="token required"), 400
    result = poll_session(token)
    return jsonify(**result)


def ariapp_build_home_sidebar_context(self, perms, user_info):
    """Build sidebar context for the home page using pinned entries."""
    sidebar_tree = permissions_mod.get_pinned_sidebar_items(
        perms,
        self.ari_pages,
        "home",
        logged_in=(user_info is not None),
        username=(user_info or {}).get("username", ""),
    )
    if not sidebar_tree:
        return {}
    return {
        "sidebar_root": "home",
        "sidebar_label": "Home",
        "sidebar_icon": "fa-solid fa-house",
        "sidebar_url": "/",
        "sidebar_tree": sidebar_tree,
    }


def ariapp_api_user_object_sections_reorder(self):
    """Save explicit order for globally pinned object sections."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json() or {}
    ids = body.get("ids", [])
    if not isinstance(ids, list):
        return jsonify(success=False, error="ids must be a list"), 400
    ids = self._normalize_object_section_pins(ids)

    username = user_info["username"]
    self._load_user_object_section_pins(username)
    pinned = ud.reorder_object_section_pins(username, ids)
    pinned = self._normalize_object_section_pins(pinned)
    self._save_user_object_section_pins(username, pinned)
    return jsonify(success=True, object_section={"pinned": pinned})


def ariapp_api_basket_summary(self):
    """Return basket summary: total files, size, missing files."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]
    profile_id = request.args.get("profile_id", "").strip() or None
    accessible_run_ids = self._all_accessible_run_ids(user_info)
    profile_cfgs = self._build_profile_cfgs(user_info)
    bk.cleanup_expired_downloads(username)
    summary = bk.basket_summary(
        username,
        profile_cfgs,
        accessible_run_ids,
        profile_id=profile_id,
    )
    return jsonify(success=True, **summary)


def ariapp_api_basket_add(self):
    """Add file entries to the basket (POST JSON {entries: [...]})."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    new_entries = data.get("entries", [])
    if not isinstance(new_entries, list):
        return jsonify(success=False, error="entries must be a list"), 400

    username = user_info["username"]
    accessible_run_ids = self._all_accessible_run_ids(user_info)
    added = bk.add_to_basket(username, new_entries, accessible_run_ids)
    basket = bk.load_basket(username)
    skipped = len(new_entries) - added
    return jsonify(
        success=True, added=added, skipped=skipped, basket_count=len(basket)
    )


def ariapp_build_safe_select_query(table_access, query_spec, run_ids):
    """Build a safe parameterized SELECT from a structured query spec.

    All table/column identifiers are validated against the whitelist in
    table_access.  Only the operators in ALLOWED_OPS are accepted for
    filters.  WHERE values are always passed as bound parameters.

    :param table_access: dict from _get_user_table_access()
    :param query_spec: structured dict (see _api_query_db_run for schema)
    :param run_ids: set of str run-ids the user may see
    :returns: (sql_str, params_dict)
    :raises ValueError: on any invalid / disallowed input
    """
    return query_helpers.build_safe_select_query(
        table_access=table_access,
        query_spec=query_spec,
        run_ids=run_ids,
    )


def ariapp_build_safe_count_query(table_access, query_spec, run_ids):
    """Build a safe parameterized COUNT(*) query."""
    return query_helpers.build_safe_count_query(
        table_access=table_access,
        query_spec=query_spec,
        run_ids=run_ids,
    )


def ariapp_api_async_tasks_task_log(self):
    """Return current per-task async log content."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    task_id = str(request.args.get("task_id", "") or "").strip()
    if not task_id:
        return jsonify(success=False, error="Missing task_id"), 400

    try:
        lines = int(request.args.get("lines", 400) or 400)
    except (TypeError, ValueError):
        lines = 400
    lines = max(1, min(lines, 2000))

    payload = task_runner.get_task_log(task_id, lines=lines)
    return jsonify(success=True, **payload)


def ariapp_validate_async_task_file_path(self, path):
    """Validate and resolve an async task output file path."""
    if not path:
        return None, (jsonify(success=False, error="No path"), 400)
    if not os.path.isabs(path):
        return None, (
            jsonify(success=False, error="Must be an absolute path"),
            400,
        )

    resolved = Path(path).resolve()
    try:
        resolved.relative_to(Path.home().resolve())
    except ValueError:
        return None, (
            jsonify(success=False, error="Path outside allowed directory"),
            403,
        )

    if not resolved.is_file():
        return None, (jsonify(success=False, error="File not found"), 404)
    return resolved, None


def ariapp_api_admin_links_add(self):
    user_info, perms = self._require_admin_links_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    url = str(body.get("url", "")).strip()
    if not instrument or not section or not name or not url:
        return (
            jsonify(
                success=False,
                error="instrument, section, name and url required",
            ),
            400,
        )
    links_perm = f"manage.admin.links.{instrument}"
    if links_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    data = ud.add_instrument_link(
        instrument,
        section,
        name,
        url,
        str(body.get("type", "")),
        str(body.get("description", "")),
    )
    return jsonify(success=True, data=data)


def ariapp_api_admin_email_send_test(self):
    user_info, perms = self._require_admin_email_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.email_setup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    body = request.get_json() or {}
    to = str(body.get("to", "")).strip()
    if not to:
        return jsonify(success=False, error="Recipient address required."), 400
    err = eb.send_email(
        to,
        "APERO RI — test email",
        (
            "This is a test email from APERO RI.\n\n"
            "If you received this, email delivery is working correctly."
        ),
    )
    if err:
        return jsonify(success=False, error=err)
    return jsonify(success=True)


def ariapp_get_user_accessible_run_ids(self, user_info, instrument):
    """Return set of run_ids the user may see for this instrument.

    Users only see run_ids from science groups where they are listed.
    An empty set means they should see no rows.
    """
    if user_info is None:
        return set()
    username = user_info.get("username", "")
    groups = auth.load_science_groups(instrument)
    accessible = set()
    for group_data in groups.values():
        if username in group_data.get("users", []):
            for rid in group_data.get("run_ids", []):
                if rid:
                    accessible.add(str(rid).strip())
    return accessible


def ariapp_api_admin_dm_reset_user(self):
    """Reset download counters for a user."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.admin" not in perms:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    category = str(body.get("category", "")).strip()
    if not username or category not in ("api", "basket"):
        return jsonify(success=False, error="Invalid parameters"), 400
    dt.reset_user_usage(username, category)
    return jsonify(success=True)


def ariapp_get_api_user():
    """Return user info from Bearer token or session (in that order).

    Checks the ``Authorization: Bearer <token>`` header first.
    Falls back to the normal session-based ``get_effective_user``.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        username = at.validate_token(token)
        if username:
            info = auth.get_user_info(username)
            if info:
                return info
        # Invalid token → do NOT fall back to session
        return None
    return auth.get_effective_user(session)


def ariapp_refresh_admin_health_entry(self, cache_key, user_info, perms):
    """Refresh one admin-health cache entry synchronously."""
    health = self._build_admin_card_health_uncached(user_info, perms)
    with self._admin_health_cache_lock:
        self._admin_health_cache[cache_key] = {
            "health": health,
            "updated_at": datetime.now(timezone.utc),
            "in_progress": False,
            "perms": sorted(perms),
        }
    threading.Thread(
        target=self._save_health_cache_to_disk,
        daemon=True,
        name="admin-health-disk-save",
    ).start()
    try:
        health_history.record_snapshot(health)
    except Exception as exc:
        log.warning("Failed to record health history snapshot: %s", exc)


def ariapp_normalize_object_section_pins(value):
    """Normalize object section ids used for per-user pinned section order."""
    if not isinstance(value, list):
        return []
    normalized = []
    seen = set()
    for item in value:
        sid = str(item).strip()
        if not sid:
            continue
        if not re.match(r"^[a-zA-Z0-9_.\-]+$", sid):
            continue
        if sid in seen:
            continue
        seen.add(sid)
        normalized.append(sid)
    return normalized


def ariapp_save_user_object_section_pins(self, username, pins):
    """Persist object section pin order to file and legacy users.yaml field."""
    pins = self._normalize_object_section_pins(pins)
    ud.save_object_section(username, {"pinned": pins})

    users = auth.load_users()
    user = users.get(username)
    if user is not None:
        section_cfg = user.get("object_section", {})
        if not isinstance(section_cfg, dict):
            section_cfg = {}
        section_cfg["pinned"] = pins
        user["object_section"] = section_cfg
        users[username] = user
        auth.save_users(users)


def ariapp_basket_access_check(self):
    """
    Shared access-check helper for all basket routes.
    Returns (user_info, None) on success, (None, error_response) on failure.
    """
    user_info = self._get_api_user()
    if user_info:
        perms = permissions_mod.resolve_user_permissions(
            user_info["groups"], self.ari_groups
        )
    else:
        perms = auth.get_public_permissions()
    if "view.data_portal" not in perms:
        return None, (jsonify(success=False, error="Unauthorized"), 401)
    if not user_info:
        return None, (jsonify(success=False, error="Login required"), 401)
    return user_info, None


def ariapp_api_basket_jobs_clear(self):
    """Remove all completed/failed compilation jobs for the user."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    username = user_info["username"]
    result = bk.clear_download_jobs(username)
    usage = bk.get_downloads_usage(username)
    limit_bytes = bk.get_downloads_storage_limit_bytes(user_info.get("groups"))
    return jsonify(
        success=True,
        removed=result.get("removed", 0),
        skipped=result.get("skipped", 0),
        download_usage=usage,
        download_limit_bytes=limit_bytes,
        quota_reached=(usage.get("total_bytes", 0) >= limit_bytes),
    )


def ariapp_api_basket_share_token(self):
    """Return (or create) a public share token for a completed job."""
    user_info, err = self._basket_access_check()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id", "") or "").strip()
    if not job_id:
        return jsonify(success=False, error="job_id required"), 400
    username = user_info["username"]
    try:
        token = bk.create_share_token(username, job_id)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    share_url = request.host_url.rstrip("/") + url_for(
        "share_landing", token=token
    )
    return jsonify(success=True, token=token, share_url=share_url)


def ariapp_api_admin_email_save(self):
    user_info, perms = self._require_admin_email_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.admin.email_setup" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    body = request.get_json() or {}
    allowed = {
        "provider",
        "enabled",
        "from_address",
        "smtp_host",
        "smtp_port",
        "smtp_ssl",
        "smtp_tls",
        "smtp_user",
        "smtp_password",
    }
    cfg = {k: v for k, v in body.items() if k in allowed}
    if "smtp_password" not in cfg:
        existing = eb.load_email_config()
        if existing.get("smtp_password_enc"):
            cfg["smtp_password_enc"] = existing["smtp_password_enc"]
    eb.save_email_config(cfg)
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True)


def ariapp_build_admin_email_context(self, perms):
    """Build context for the admin email settings page."""
    import json as _json

    cfg = eb.load_email_config()
    providers = eb.PROVIDER_DEFAULTS
    current_provider = cfg.get("provider", "log")
    # Ensure current is valid
    if current_provider not in providers:
        current_provider = "log"
    return {
        "email_cfg": cfg,
        "providers": providers,
        "providers_json": _json.dumps(providers),
        "current_provider": current_provider,
        "can_manage": "manage.admin.email_setup" in perms,
    }


def ariapp_start_admin_health_refresher(self):
    """Start background hourly refresh; spawn async refresh of any
    entries loaded from the persisted disk cache at startup."""
    with self._admin_health_cache_lock:
        startup_items = [
            (key, set(entry.get("perms", [])))
            for key, entry in self._admin_health_cache.items()
        ]
    for key, perms in startup_items:
        self._spawn_admin_health_refresh(key, None, perms)
    thread = threading.Thread(
        target=self._admin_health_refresher_loop,
        daemon=True,
        name="admin-health-refresher",
    )
    thread.start()
    digest_thread = threading.Thread(
        target=self._admin_health_digest_loop,
        daemon=True,
        name="admin-health-digest",
    )
    digest_thread.start()


def ariapp_editable_groups_for_editor(self, user_info, perms):
    """Return groups this editor may grant DB table access to."""
    all_groups = list(self.ari_groups.keys())
    editor_groups = set(user_info.get("groups", []))
    editor_is_admin = auth.user_has_admin_privileges(list(editor_groups))
    editor_is_super_admin = auth.user_is_super_admin(list(editor_groups))
    if editor_is_super_admin:
        return sorted(all_groups)
    if editor_is_admin:
        return sorted([g for g in all_groups if g != "super_admin"])

    allowed = {g for g in all_groups if f"manage.group.{g}" in perms}
    expanded = set(allowed)
    for g in list(allowed):
        expanded |= set(perms.get_inherited_groups(g, self.ari_groups))
    return sorted(expanded)


def ariapp_validate_profile_database(self, profile_cfg):
    """Validate one profile DB config using the shared runtime path."""
    db_params = self._profile_db_params(profile_cfg)
    return auth.validate_database_connection(
        db_params.get("DATABASE_MODE", ""),
        db_params.get("DATABASE_HOST", ""),
        db_params.get("DATABASE_USERNAME", ""),
        db_params.get("DATABASE_PASSWORD", ""),
        db_params.get("DATABASE_NAME", ""),
        port=db_params.get("DATABASE_PORT", ""),
        use_ssh_tunnel=db_params.get("DATABASE_USE_SSH_TUNNEL", False),
        ssh_config_host=db_params.get("DATABASE_SSH_CONFIG_HOST", ""),
        ssh_local_port=db_params.get("DATABASE_SSH_LOCAL_PORT", ""),
        ssh_remote_port=db_params.get("DATABASE_SSH_REMOTE_PORT", ""),
        local_data_dir=str(self._resolve_local_data_dir()),
    )


def ariapp_profile_db_access_health(self, entry, table_names):
    """Return health status for one profile DB-access config."""
    groups_map = entry.get("groups", {}) if isinstance(entry, dict) else {}
    if not table_names:
        return "warning"
    for table in table_names:
        glist = groups_map.get(table, [])
        if not isinstance(glist, list) or not glist:
            return "warning"
    return "ok"


def ariapp_api_async_tasks_download_file(self):
    """Download an async task output file."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    path = request.args.get("path", "").strip()
    resolved, error_response = self._validate_async_task_file_path(path)
    if error_response is not None:
        return error_response
    if resolved is None:
        return jsonify(success=False, error="Invalid path"), 400

    return send_from_directory(
        str(resolved.parent), resolved.name, as_attachment=True
    )


def ariapp_api_admin_backups_sync(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(success=False, error="Insufficient permissions"), 403

    cfg = bb.load_backup_config()
    local_data_dir = self._resolve_local_data_dir()
    body = request.get_json(silent=True) or {}
    method_id = str(body.get("method_id", "") or "").strip() or None
    result = bb.sync_local_backups_to_cloud(
        local_data_dir=local_data_dir, cfg=cfg, method_id=method_id
    )
    self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True, data=result)


def ariapp_api_admin_sshfs_keys_add(self):
    """Add a new SSH key."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    data = request.get_json() or {}
    key_name = data.get("key_name", "").strip()
    key_content = data.get("key_content", "").strip()

    result = sb.add_ssh_key(key_name, key_content)
    return jsonify(**result)


def ariapp_load_or_create_secret():
    """Load or create a persistent secret key in ARI_DIR/secret."""
    ari_dir = ss.get_ari_dir()
    secret_file = ss.resolve_secret_file(
        "secret.key",
        legacy_paths=[
            ari_dir / "secret.key",
            Path.home() / ".ari" / "secret.key",
        ],
    )
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    if secret_file.exists():
        return secret_file.read_text().strip()
    key = secrets.token_hex(32)
    secret_file.write_text(key, encoding="utf-8")
    ss.protect_path(secret_file, 0o600)
    return key


def ariapp_api_db_ssh_tunnel_status(self):
    """List tunnel status for all saved DB tunnel definitions."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    rows = self._list_db_tunnel_rows()
    active_count = sum(
        1 for row in rows if bool((row.get("status") or {}).get("active"))
    )

    return jsonify(
        success=True,
        tunnels=rows,
        active_count=active_count,
        multi_active_supported=True,
    )


def ariapp_api_user_links_update(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    new_name = str(body.get("new_name", name)).strip()
    url = str(body.get("url", "")).strip()
    if not section or not name or not url:
        return (
            jsonify(success=False, error="section, name and url required"),
            400,
        )
    data = ud.update_link(
        user_info["username"],
        section,
        name,
        new_name,
        url,
        str(body.get("type", "")),
        str(body.get("description", "")),
    )
    return jsonify(success=True, data=data)


def ariapp_api_user_notes_save(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    note = {
        "id": str(body.get("id", "")).strip(),
        "title": str(body.get("title", "Untitled")).strip(),
        "color": str(body.get("color", "#ffd966")).strip(),
        "section": str(body.get("section", "")).strip(),
        "created": str(body.get("created", "")).strip(),
        "content": str(body.get("content", "")),
    }
    saved = ud.save_note(user_info["username"], note)
    return jsonify(success=True, note=saved)


def ariapp_api_admin_links_remove(self):
    user_info, perms = self._require_admin_links_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    if not instrument or not section or not name:
        return (
            jsonify(
                success=False,
                error="instrument, section and name required"
            ),
            400,
        )
    links_perm = f"manage.admin.links.{instrument}"
    if links_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    data = ud.remove_instrument_link(instrument, section, name)
    return jsonify(success=True, data=data)


def ariapp_api_basket_remove(self):
    """Remove entries from the basket (POST JSON {ids: [...]})."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    if not isinstance(ids, list):
        return jsonify(success=False, error="ids must be a list"), 400

    username = user_info["username"]
    removed = bk.remove_from_basket(username, ids)
    return jsonify(success=True, removed=removed)


def ariapp_require_admin_user(self):
    """Check that current user has view.admin permission.

    Returns (user_info, perms) or raises a JSON error response.
    """
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, None
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return None, None
    return user_info, perms


def ariapp_api_apero_profiles_validate(self):
    """Validate a path exists as a directory."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    path = request.args.get("path", "").strip()
    if not path:
        return jsonify(success=False, error="No path"), 400
    if not os.path.isabs(path):
        return jsonify(success=False, error="Must be absolute"), 400

    kind = "file" if request.args.get("kind", "") == "file" else "dir"
    result = auth.validate_path_exists(path, kind=kind)
    return jsonify(success=True, **result)


def ariapp_api_apero_profiles_ssh_tunnel_send(self):
    """Send input to an interactive SSH tunnel session."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    from apero_ri.core.sshfs_interactive import send_input

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    data = str(body.get("data", ""))
    if not token:
        return jsonify(ok=False, error="token required"), 400
    return jsonify(**send_input(token, data))


def ariapp_api_async_tasks_clear_history(self):
    """Clear recent async task history entries."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    result = task_runner.clear_recent_history()
    if result.get("success"):
        return jsonify(success=True, removed=int(result.get("removed", 0) or 0))
    return (
        jsonify(
            success=False, error=result.get("error", "Failed to clear history")
        ),
        500,
    )


def ariapp_api_user_links_add(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    url = str(body.get("url", "")).strip()
    if not section or not name or not url:
        return (
            jsonify(success=False, error="section, name and url required"),
            400,
        )
    data = ud.add_link(
        user_info["username"],
        section,
        name,
        url,
        str(body.get("type", "")),
        str(body.get("description", "")),
    )
    return jsonify(success=True, data=data)


def ariapp_api_admin_links_add_section(self):
    user_info, perms = self._require_admin_links_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    section = str(body.get("section", "")).strip()
    if not instrument or not section:
        return (
            jsonify(
                success=False,
                error="instrument and section required"
            ),
            400,
        )
    links_perm = f"manage.admin.links.{instrument}"
    if links_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    data = ud.add_instrument_link_section(instrument, section)
    return jsonify(success=True, data=data)


def ariapp_api_admin_links_remove_section(self):
    user_info, perms = self._require_admin_links_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    section = str(body.get("section", "")).strip()
    if not instrument or not section:
        return (
            jsonify(
                success=False,
                error="instrument and section required"
            ),
            400,
        )
    links_perm = f"manage.admin.links.{instrument}"
    if links_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    data = ud.remove_instrument_link_section(instrument, section)
    return jsonify(success=True, data=data)


def ariapp_api_admin_backups_list(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "view.admin" not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    cfg = bb.load_backup_config()
    local_data_dir = self._resolve_local_data_dir()
    method_id = str(request.args.get("method_id", "") or "").strip() or None
    inventory = bb.backup_inventory(
        local_data_dir=local_data_dir, cfg=cfg, method_id=method_id
    )
    return jsonify(success=True, data=inventory)


def ariapp_api_admin_sshfs_mounts_delete(self, mount_name):
    """Delete an SSHFS mount."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.delete_mount(mount_name)
    if result["ok"]:
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_mount(self, mount_name):
    """Mount an SSHFS volume."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.mount_sshfs(mount_name)
    if result["ok"]:
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_unmount(self, mount_name):
    """Unmount an SSHFS volume."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.unmount_sshfs(mount_name)
    if result["ok"]:
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_unmount_lazy(self, mount_name):
    """Lazy-unmount an SSHFS volume."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.lazy_unmount_sshfs(mount_name)
    if result["ok"]:
        self._refresh_admin_health_after_change(user_info, perms)
    return jsonify(**result)


def ariapp_resolve_local_data_dir():
    """Resolve configured LOCAL_DATA_DIR, falling back to ARI_DIR."""
    params = perms.load_parameters() or {}
    local_data = params.get("LOCAL_DATA_DIR", "")
    if isinstance(local_data, dict):
        local_data = local_data.get("value", "")
    local_data = str(local_data or "").strip()
    if local_data:
        return Path(local_data).expanduser().resolve()
    return (
        Path(os.environ.get("ARI_DIR", str(Path.home() / ".ari")))
        .expanduser()
        .resolve()
    )


def ariapp_refresh_admin_health_after_change(self, user_info, perms):
    """Refresh admin-health cache after successful admin mutations.

    Best effort only: this must never break the primary API action.
    """
    return admin_health_helpers.refresh_admin_health_after_change(
        self,
        user_info=user_info,
        perms=perms,
        session_obj=session,
    )


def ariapp_cleanup_expired_reset_tokens(self, users):
    """Remove expired password-reset tokens. Returns True if modified."""
    now = datetime.now(timezone.utc)
    changed = False
    for user in users.values():
        reset_data = user.get("password_reset")
        if not isinstance(reset_data, dict):
            continue
        exp = self._parse_iso_datetime(reset_data.get("expires_at", ""))
        if exp is None or now > exp:
            user.pop("password_reset", None)
            changed = True
    return changed


def ariapp_parse_text_presets(text, replace_fn):
    """Parse a ``================`` -delimited preset text file.

    Each preset block has the form::

        ================
        Preset name
        ================
        SELECT ...

    Returns a list of ``{'name': str, 'query': str}`` dicts.
    """
    return query_helpers.parse_text_presets(text, replace_fn)


def ariapp_api_apero_profiles_ssh_tunnel_poll(self):
    """Poll output from an interactive SSH tunnel session."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    from apero_ri.core.sshfs_interactive import poll_session

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    if not token:
        return jsonify(ok=False, error="token required"), 400
    return jsonify(**poll_session(token))


def ariapp_api_apero_profiles_ssh_tunnel_close(self):
    """Close and clean up an interactive SSH tunnel session."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    from apero_ri.core.sshfs_interactive import close_session

    body = request.get_json(silent=True) or {}
    token = str(body.get("token", "")).strip()
    if not token:
        return jsonify(ok=False, error="token required"), 400
    return jsonify(**close_session(token))


def ariapp_api_async_tasks_cancel_task(self):
    """Cancel a single queued or running task by task_id."""
    user_info, perms = self._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    data = request.get_json(silent=True) or {}
    task_id = str(data.get("task_id", "") or "").strip()
    if not task_id:
        return jsonify(success=False, error="task_id is required"), 400
    result = task_runner.cancel_task(task_id)
    if not result.get("success"):
        return jsonify(**result), 404
    return jsonify(**result)


def ariapp_api_user_notes_list(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    notes = ud.load_notes(user_info["username"])
    slim = []
    for note in notes:
        entry = {k: v for k, v in note.items() if k != "content"}
        content = str(note.get("content", ""))
        preview = " ".join(content.split())[:180]
        entry["content_preview"] = preview
        slim.append(entry)
    return jsonify(success=True, notes=slim)


def ariapp_api_admin_calendar_delete(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    event_id = str(body.get("id", "")).strip()
    if not instrument or not event_id:
        return jsonify(success=False, error="instrument and id required"), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403
    ok = ud.delete_instrument_event(instrument, event_id)
    return jsonify(success=True, deleted=ok)


# ---------------------------------------------------------------------------
# ICS feed API — User calendar
# ---------------------------------------------------------------------------

def ariapp_api_user_ics_list(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    feeds = ud.list_ics_feeds(user_info["username"])
    return jsonify(success=True, feeds=feeds)


def ariapp_api_user_ics_add(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    name = str(body.get("name", "")).strip()
    url = str(body.get("url", "")).strip()
    color = str(body.get("color", "#4a90d9")).strip()
    if not name or not url:
        return jsonify(
            success=False, error="name and url are required"
        ), 400
    try:
        username = user_info["username"]
        feed, count = ud.add_ics_feed(
            username, name, url, color
        )
        feeds = ud.list_ics_feeds(username)
        return jsonify(
            success=True, feed=feed,
            imported=count, feeds=feeds,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_user_ics_delete(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    feed_id = str(body.get("feed_id", "")).strip()
    if not feed_id:
        return jsonify(
            success=False, error="feed_id required"
        ), 400
    username = user_info["username"]
    ud.delete_ics_feed(username, feed_id)
    feeds = ud.list_ics_feeds(username)
    return jsonify(success=True, feeds=feeds)


def ariapp_api_user_ics_refresh(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    feed_id = str(body.get("feed_id", "")).strip()
    if not feed_id:
        return jsonify(
            success=False, error="feed_id required"
        ), 400
    try:
        username = user_info["username"]
        feed = ud.refresh_ics_feed(username, feed_id)
        feeds = ud.list_ics_feeds(username)
        return jsonify(success=True, feed=feed, feeds=feeds)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_user_ics_edit(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    feed_id = str(body.get("feed_id", "")).strip()
    name = body.get("name")
    color = body.get("color")
    if not feed_id:
        return jsonify(
            success=False, error="feed_id required"
        ), 400
    if name is not None:
        name = str(name).strip() or None
    if color is not None:
        color = str(color).strip() or None
    try:
        username = user_info["username"]
        feed = ud.update_ics_feed(
            username, feed_id, name=name, color=color
        )
        feeds = ud.list_ics_feeds(username)
        return jsonify(success=True, feed=feed, feeds=feeds)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


# ---------------------------------------------------------------------------
# ICS feed API — Instrument / Admin calendar
# ---------------------------------------------------------------------------

def ariapp_api_admin_ics_list(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    instrument = request.args.get("instrument", "").strip()
    if not instrument:
        return jsonify(
            success=False, error="instrument query param required"
        ), 400
    feeds = ud.list_instrument_ics_feeds(instrument)
    return jsonify(success=True, feeds=feeds)


def ariapp_api_admin_ics_add(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    name = str(body.get("name", "")).strip()
    url = str(body.get("url", "")).strip()
    color = str(body.get("color", "#7b5ea7")).strip()
    if not instrument or not name or not url:
        return jsonify(
            success=False,
            error="instrument, name and url are required",
        ), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403
    try:
        feed, count = ud.add_instrument_ics_feed(
            instrument, name, url, color
        )
        feeds = ud.list_instrument_ics_feeds(instrument)
        return jsonify(
            success=True, feed=feed,
            imported=count, feeds=feeds,
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_admin_ics_delete(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    feed_id = str(body.get("feed_id", "")).strip()
    if not instrument or not feed_id:
        return jsonify(
            success=False,
            error="instrument and feed_id required",
        ), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403
    ud.delete_instrument_ics_feed(instrument, feed_id)
    feeds = ud.list_instrument_ics_feeds(instrument)
    return jsonify(success=True, feeds=feeds)


def ariapp_api_admin_ics_refresh(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    feed_id = str(body.get("feed_id", "")).strip()
    if not instrument or not feed_id:
        return jsonify(
            success=False,
            error="instrument and feed_id required",
        ), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403
    try:
        feed = ud.refresh_instrument_ics_feed(instrument, feed_id)
        feeds = ud.list_instrument_ics_feeds(instrument)
        return jsonify(
            success=True, feed=feed, feeds=feeds
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_admin_ics_edit(self):
    user_info, perms = self._require_admin_calendar_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    instrument = str(body.get("instrument", "")).strip()
    feed_id = str(body.get("feed_id", "")).strip()
    name = body.get("name")
    color = body.get("color")
    if not instrument or not feed_id:
        return jsonify(
            success=False,
            error="instrument and feed_id required",
        ), 400
    cal_perm = f"manage.admin.calendar.{instrument}"
    if cal_perm not in (perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403
    if name is not None:
        name = str(name).strip() or None
    if color is not None:
        color = str(color).strip() or None
    try:
        feed = ud.update_instrument_ics_feed(
            instrument, feed_id, name=name, color=color
        )
        feeds = ud.list_instrument_ics_feeds(instrument)
        return jsonify(
            success=True, feed=feed, feeds=feeds
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 400


def ariapp_api_admin_email_test(self):
    user_info, perms = self._require_admin_email_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    if "view.admin" not in (perms or set()):
        return jsonify(ok=False, error="Insufficient permissions"), 403
    cfg = eb.load_email_config()
    provider = cfg.get("provider", "log")
    if provider == "log" or not cfg.get("enabled", False):
        return jsonify(ok=True, detail="Log mode — no SMTP connection needed.")
    result = eb.test_email_connection(cfg)
    return jsonify(ok=result["ok"], error=result.get("error", ""), detail="")


def ariapp_page_template_meta(self, template_id, **tokens):
    """Resolve label/icon from a dynamic page template in pages.yaml."""
    template = self._page_templates.get(template_id, {})
    label = str(template.get("label", ""))
    for key, value in tokens.items():
        value_str = str(value)
        label = label.replace(f"{{{key}}}", value_str)
        label = label.replace(f'{{{key.replace("_", " ")}}}', value_str)
    return {
        "label": label,
        "icon": template.get("icon", ""),
    }


def ariapp_api_admin_health_config_get(self):
    """Return persisted health-status UI config."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(success=False, error="Forbidden"), 403

    cfg = auth.load_admin_health_config()
    return jsonify(success=True, config=cfg)


def ariapp_get_primary_contact_email(user):
    """Return best email address to use for account notifications."""
    primary = str(user.get("primary_email", "")).strip()
    if primary:
        return primary
    emails = user.get("emails", [])
    if isinstance(emails, list):
        for email in emails:
            val = str(email).strip()
            if val:
                return val
    return ""


def ariapp_find_reset_user(self, token, users):
    """Find username matching a valid reset token."""
    if not token:
        return None
    for username, user in users.items():
        reset_data = user.get("password_reset")
        if not isinstance(reset_data, dict):
            continue
        token_hash = str(reset_data.get("token_hash", "")).strip()
        if token_hash and auth.verify_password(token, token_hash):
            return username
    return None


def ariapp_ri_qc_graphs_max_view(
    self, profile_id, section, metric_key, view_key
):
    return data_portal_view_helpers.ri_qc_graphs_max_view(
        self,
        profile_id=profile_id,
        section=section,
        metric_key=metric_key,
        view_key=view_key,
    )


def ariapp_api_apero_profiles_overview(self):
    """Return all-instruments APERO profile readiness summary."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    overview = self._build_apero_profiles_overview_status()
    return jsonify(
        success=True,
        status=overview.get("status", {}),
        total_profiles=overview.get("total_profiles", 0),
    )


def ariapp_api_user_prefs_save(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    updates = {}
    if "timezone" in body:
        updates["timezone"] = str(body["timezone"]).strip() or "UTC"
    if "theme" in body:
        _theme = str(body["theme"]).strip()
        updates["theme"] = (
            _theme if _theme in ("default", "light", "dark")
            else "default"
        )
    if updates:
        ud.save_user_prefs(user_info["username"], updates)
    prefs = ud.load_user_prefs(user_info["username"])
    return jsonify(success=True, prefs=prefs)


def ariapp_api_user_todo_toggle(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    item_id = str(body.get("id", "")).strip()
    if not item_id:
        return jsonify(success=False, error="id required"), 400
    item = ud.toggle_todo(user_info["username"], item_id)
    if item is None:
        return jsonify(success=False, error="Not found"), 404
    return jsonify(success=True, item=item)


def ariapp_api_admin_backups_test_backup(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    if (
        "manage.admin.backup_setup" not in (perms or set())
        and "manage.admin.backup" not in (perms or set())
    ):
        return jsonify(ok=False, error="Insufficient permissions"), 403

    body = request.get_json(silent=True) or {}
    method_id = str(body.get("method_id", "") or "").strip() or None
    result = bb.test_backup_roundtrip(
        bb.load_backup_config(), method_id=method_id
    )
    return jsonify(result)


def ariapp_api_admin_sshfs_keys_list(self):
    """List available SSH keys."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.list_ssh_keys()
    return jsonify(**result)


def ariapp_api_admin_sshfs_keys_delete(self, key_name):
    """Delete an SSH key."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.delete_ssh_key(key_name)
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_status(self):
    """Get status of all SSHFS mounts."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.get_mounts_status()
    return jsonify(**result)


def ariapp_api_admin_sshfs_mounts_log(self, mount_name):
    """Get the last saved log for a mount."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401

    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "view.admin" not in perms:
        return jsonify(ok=False, error="Forbidden"), 403

    result = sb.get_mount_log(mount_name)
    return jsonify(**result)


def ariapp_resolve_host(host):
    """Resolve 'auto' host to '::' (IPv6) or '0.0.0.0' (IPv4)."""
    if host != "auto":
        return host
    # prefer IPv6 dual-stack if available
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.close()
        return "::"
    except OSError:
        return "0.0.0.0"


def ariapp_admin_health_refresher_loop(self):
    """Refresh all cached admin-health snapshots every hour."""
    while True:
        time.sleep(3600)
        with self._admin_health_cache_lock:
            work_items = [
                (key, set(entry.get("perms", [])))
                for key, entry in self._admin_health_cache.items()
            ]
        for key, perms in work_items:
            self._refresh_admin_health_entry(key, None, perms)


def ariapp_admin_health_digest_loop(self):
    """Send a daily admin-health digest email to super-admins.

    Sleeps in short increments so it can react promptly to the first
    health snapshot, then sends at most one digest per UTC calendar day
    when any check is in 'warning' or 'error' state.
    """
    last_sent_date = None
    while True:
        time.sleep(900)
        try:
            today = datetime.now(timezone.utc).date()
            if last_sent_date == today:
                continue

            with self._admin_health_cache_lock:
                entries = list(self._admin_health_cache.values())
            health: Dict[str, Any] = {}
            for entry in entries:
                health.update(entry.get("health", {}) or {})
            if not health:
                continue

            problems = {
                key: info
                for key, info in health.items()
                if isinstance(info, dict) and info.get("status") in ("warning", "error")
            }
            if not problems:
                last_sent_date = today
                continue

            email_cfg = eb.load_email_config()
            if not email_cfg.get("enabled", False):
                last_sent_date = today
                continue

            recipients = [
                u.get("email", "").strip()
                for u in auth.load_users().values()
                if auth.user_is_super_admin(u.get("groups", [])) and u.get("email", "").strip()
            ]
            if not recipients:
                last_sent_date = today
                continue

            lines = [f"Admin health digest for {today.isoformat()} (UTC)", ""]
            for key in sorted(problems):
                info = problems[key]
                lines.append(f"- [{info.get('status')}] {key}: {info.get('message', '')}")
            body = "\n".join(lines)
            subject = f"APERO RI: {len(problems)} admin health issue(s) - {today.isoformat()}"

            for addr in recipients:
                err = eb.send_email(addr, subject, body, cfg=email_cfg)
                if err:
                    log.warning("Failed to send health digest to %s: %s", addr, err)

            last_sent_date = today
        except Exception as exc:
            log.warning("Admin health digest loop iteration failed: %s", exc)


def ariapp_prune_forgot_pw_rate_limit(self, now_ts):
    """Drop old throttle records to keep in-memory state small."""
    stale_after = 3600.0
    to_delete = []
    for ip, state in self._forgot_pw_rate_limit.items():
        last_seen = float(state.get("last_seen", 0.0) or 0.0)
        blocked_until = float(state.get("blocked_until", 0.0) or 0.0)
        if now_ts > blocked_until and (now_ts - last_seen) > stale_after:
            to_delete.append(ip)
    for ip in to_delete:
        self._forgot_pw_rate_limit.pop(ip, None)


def ariapp_send_verification_email(recipient_email, code, purpose):
    """Send verification code email via configured email backend.

    Returns None on success, error string on failure.
    Configuration is read from {ARI_DIR}/admin/email/email.yaml.
    Falls back to log mode (writes to admin/email/email_log.txt)
    when unconfigured.
    """
    return eb.send_verification_email(recipient_email, code, purpose)


def ariapp_save_user_pins(self, username, pins):
    """Persist pins to per-user pins.yaml and mirror into legacy users.yaml."""
    pins = self._normalize_pinned_pages(pins)
    ud.save_pins(username, {"pins": pins})

    users = auth.load_users()
    user = users.get(username)
    if user is not None:
        user["pinned_pages"] = pins
        users[username] = user
        auth.save_users(users)


def ariapp_all_accessible_run_ids(self, user_info):
    """Return the union of run_ids across all instruments the user can see."""
    accessible = auth.get_accessible_profiles(user_info, self.ari_groups)
    all_run_ids: set = set()
    for prof in accessible:
        instrument = prof.get("instrument", "")
        if instrument:
            all_run_ids |= self._get_user_accessible_run_ids(
                user_info, instrument
            )
    return all_run_ids


def ariapp_api_basket_clear(self):
    """Clear basket (POST JSON {profile_id?: ...})."""
    user_info, err = self._basket_access_check()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    profile_id = data.get("profile_id") or None
    username = user_info["username"]
    removed = bk.clear_basket(username, profile_id)
    return jsonify(success=True, removed=removed)


def ariapp_require_sci_group_perm(self):
    """Check for any manage.sci_group.* permission."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, None
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    has_any = any(
        p.startswith("manage.sci_group.") for p in perms
    )
    if not has_any:
        return None, None
    return user_info, perms


def ariapp_require_apero_profile_perm(self):
    """Check for manage.apero_profile permission."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, None
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.apero_profile" not in perms:
        return None, None
    return user_info, perms


def ariapp_require_user_db_access_perm(self):
    """Check for manage.admin.user_db_access permission."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, None
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.admin.user_db_access" not in perms:
        return None, None
    return user_info, perms


def ariapp_require_async_tasks_perm(self):
    """Check manage.apero_profile permission for async task management."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        return None, None
    perms = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.apero_profile" not in perms:
        return None, None
    return user_info, perms


def _clock_config_path(local_data_dir: Path) -> Path:
    """Return clock configuration path in local admin settings."""
    return (
        Path(local_data_dir).expanduser().resolve()
        / "admin"
        / "general"
        / "clocks.yaml"
    )


def _default_clock_rows() -> list:
    """Return locked default clock rows."""
    return [
        {"name": "UTC", "timezone": "UTC", "locked": True},
        {"name": "Local", "timezone": "LOCAL", "locked": True},
    ]


def _normalise_custom_clock_rows(rows) -> list:
    """Validate and normalize editable custom clock rows."""
    clean = []
    if not isinstance(rows, list):
        return clean
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        timezone_name = str(raw.get("timezone") or "").strip()
        if not name or not timezone_name:
            continue
        if timezone_name in ["UTC", "LOCAL"]:
            continue
        if len(name) > 80:
            name = name[:80].strip()
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            continue
        except Exception:
            continue
        clean.append(
            {
                "name": name,
                "timezone": timezone_name,
                "locked": False,
            }
        )
    return clean


def _load_clock_rows(local_data_dir: Path) -> list:
    """Load clock rows with UTC/local pinned first."""
    defaults = _default_clock_rows()
    path = _clock_config_path(local_data_dir)
    if not path.exists():
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f) or {}
    except Exception:
        return defaults
    custom = _normalise_custom_clock_rows(payload.get("custom", []))
    return defaults + custom


def _save_custom_clock_rows(local_data_dir: Path, custom_rows: list) -> None:
    """Persist custom clock rows atomically."""
    path = _clock_config_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "custom": _normalise_custom_clock_rows(custom_rows),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    os.replace(tmp_path, path)


def ariapp_api_clocks_get(self):
    """Return configured clock rows for nav/user pages."""
    rows = _load_clock_rows(self._resolve_local_data_dir())
    return jsonify(success=True, clocks=rows)


def ariapp_api_admin_clocks(self):
    """Admin API for reading/updating custom clock rows."""
    user_info, perms = self._require_apero_profile_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.apero_profile" not in (perms or set()):
        return jsonify(success=False, error="Forbidden"), 403

    local_data_dir = self._resolve_local_data_dir()
    if request.method == "GET":
        return jsonify(success=True, clocks=_load_clock_rows(local_data_dir))

    body = request.get_json(silent=True) or {}
    rows = body.get("clocks", [])
    if not isinstance(rows, list):
        return jsonify(success=False, error="clocks must be a list"), 400

    # Persist only editable rows; defaults remain immutable.
    custom_rows = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        if idx < 2:
            continue
        name = str(row.get("name") or "").strip()
        timezone_name = str(row.get("timezone") or "").strip()
        row_num = idx + 1
        if not name:
            return (
                jsonify(
                    success=False,
                    error=f"Row {row_num}: name is required",
                ),
                400,
            )
        if not timezone_name:
            return (
                jsonify(
                    success=False,
                    error=f"Row {row_num}: timezone is required",
                ),
                400,
            )
        if timezone_name in ["UTC", "LOCAL"]:
            return (
                jsonify(
                    success=False,
                    error=(
                        f"Row {row_num}: UTC/LOCAL are reserved "
                        "and cannot be edited"
                    ),
                ),
                400,
            )
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            return (
                jsonify(
                    success=False,
                    error=f"Row {row_num}: unknown timezone {timezone_name}",
                ),
                400,
            )
        custom_rows.append(
            {
                "name": name,
                "timezone": timezone_name,
            }
        )

    _save_custom_clock_rows(local_data_dir, custom_rows)
    return jsonify(success=True, clocks=_load_clock_rows(local_data_dir))


def ariapp_api_user_links_remove(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    body = request.get_json() or {}
    section = str(body.get("section", "")).strip()
    name = str(body.get("name", "")).strip()
    if not section or not name:
        return jsonify(success=False, error="section and name required"), 400
    data = ud.remove_link(user_info["username"], section, name)
    return jsonify(success=True, data=data)


def ariapp_api_user_notes_get(self):
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    note_id = request.args.get("id", "").strip()
    if not note_id:
        return jsonify(success=False, error="id required"), 400
    note = ud.get_note(user_info["username"], note_id)
    if note is None:
        return jsonify(success=False, error="Not found"), 404
    return jsonify(success=True, note=note)


def ariapp_api_admin_backups_test(self):
    user_info, perms = self._require_admin_backup_perm()
    if not user_info:
        return jsonify(ok=False, error="Unauthorized"), 401
    if "view.admin" not in (perms or set()):
        return jsonify(ok=False, error="Insufficient permissions"), 403

    method_id = str(request.args.get("method_id", "") or "").strip() or None
    result = bb.test_backup_connection(
        bb.load_backup_config(), method_id=method_id
    )
    return jsonify(result)


# =============================================================================
# Manage Instruments admin page
# =============================================================================

#: Base group levels that get per-instrument variants
_INSTRUMENT_GROUP_LEVELS = ["general", "monitor", "developer", "moderator"]
_INSTRUMENT_YAML_DIR = (
    PACKAGE_DIR / 'resources' / 'aprofile_instruments'
)
_INSTRUMENT_YAML_RE = re.compile(r'^[A-Za-z0-9_.-]+\.ya?ml$')


def _list_instrument_yaml_files() -> List[str]:
    """Return sorted instrument YAML basenames."""
    if not _INSTRUMENT_YAML_DIR.is_dir():
        return []
    names: List[str] = []
    for candidate in _INSTRUMENT_YAML_DIR.glob('*.yaml'):
        if candidate.is_file():
            names.append(candidate.name)
    return sorted(names)


def _resolve_instrument_yaml_path(name: str) -> Path:
    """Resolve one instrument YAML path and guard against traversal."""
    fname = str(name or '').strip()
    if not _INSTRUMENT_YAML_RE.match(fname):
        raise ValueError('Invalid YAML filename')
    path = (_INSTRUMENT_YAML_DIR / fname).resolve()
    base = _INSTRUMENT_YAML_DIR.resolve()
    if not str(path).startswith(str(base) + os.sep):
        raise ValueError('Invalid YAML filename')
    if not path.is_file():
        raise ValueError(f'YAML file not found: {fname}')
    return path


def _write_yaml_atomic(path: Path, payload: Any) -> None:
    """Write YAML payload atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)
    os.replace(tmp_path, path)


def _write_text_atomic(path: Path, text: str) -> None:
    """Write text atomically while preserving formatting/comments."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as handle:
        handle.write(text)
    os.replace(tmp_path, path)


def ariapp_build_admin_manage_instruments_context(self, perms):
    """Build context dict for the Manage Instruments admin page."""
    can_manage = "manage.instrument.super_admin" in (perms or set())
    can_add = "add.instrument" in (perms or set())
    can_edit_instrument_yamls = can_add
    all_groups = permissions_mod.load_groups()
    profiles = auth.load_apero_profiles(hydrate=False)
    profile_instruments = (
        set(profiles.keys()) if isinstance(profiles, dict) else set()
    )
    # Use parameters.yaml as the canonical list; also surface any
    # instruments that exist in profiles but are missing from
    # parameters.yaml so admins can see and clean them up.
    params = permissions_mod.load_parameters()
    params_instruments = set(
        params.get("instruments", {}).get("value", [])
    )
    instruments = sorted(params_instruments | profile_instruments)

    all_users = auth.list_all_users()

    def _users_in_group(group_name):
        return [
            u["username"]
            for u in all_users
            if group_name in (u.get("groups") or [])
        ]

    instruments_data = []
    for instr in instruments:
        groups_info = []
        for level in _INSTRUMENT_GROUP_LEVELS:
            gname = "{}.{}".format(level, instr)
            exists = gname in all_groups
            member_names = _users_in_group(gname) if exists else []
            groups_info.append(
                {
                    "name": gname,
                    "level": level,
                    "exists": exists,
                    "user_count": len(member_names),
                    "users": member_names,
                }
            )
        groups_created = all(g["exists"] for g in groups_info)
        instruments_data.append(
            {
                "name": instr,
                "groups": groups_info,
                "groups_created": groups_created,
            }
        )

    return {
        "instruments_data": instruments_data,
        "instrument_group_levels": _INSTRUMENT_GROUP_LEVELS,
        "instrument_yaml_files": _list_instrument_yaml_files(),
        "can_edit_instrument_yamls": can_edit_instrument_yamls,
        "can_manage": can_manage,
        "can_add": can_add,
    }


def ariapp_api_manage_instruments_yaml_get(self):
    """Return one instrument YAML file as text."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401
    if 'add.instrument' not in (cur_perms or set()):
        return jsonify(
            success=False, error='Insufficient permissions'
        ), 403

    name = str(request.args.get('name', '') or '').strip()
    if not name:
        return jsonify(success=False, error='name is required'), 400
    try:
        path = _resolve_instrument_yaml_path(name)
        with open(path, 'r', encoding='utf-8') as handle:
            text = handle.read()
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(
            success=False,
            error=f'Failed to read YAML: {exc}',
        ), 500

    return jsonify(success=True, name=name, yaml_text=text)


def ariapp_api_manage_instruments_yaml_save(self):
    """Save one or more instrument YAML files from editor text."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401
    if 'add.instrument' not in (cur_perms or set()):
        return jsonify(
            success=False, error='Insufficient permissions'
        ), 403

    body = request.get_json(silent=True) or {}
    files_payload = body.get('files')
    if not isinstance(files_payload, list):
        name = body.get('name')
        yaml_text = body.get('yaml_text')
        files_payload = [dict(name=name, yaml_text=yaml_text)]

    if len(files_payload) == 0:
        return jsonify(success=False, error='No files to save'), 400

    updates: List[Dict[str, Any]] = []
    seen = set()
    for row in files_payload:
        if not isinstance(row, dict):
            return jsonify(
                success=False,
                error='Each files[] entry must be an object',
            ), 400
        name = str(row.get('name', '') or '').strip()
        if not name:
            return jsonify(success=False, error='files[].name required'), 400
        if name in seen:
            return jsonify(
                success=False,
                error=f'Duplicate file in payload: {name}',
            ), 400
        seen.add(name)
        text = row.get('yaml_text')
        if text is None:
            text = ''
        text = str(text)
        try:
            path = _resolve_instrument_yaml_path(name)
            loaded = yaml.safe_load(text)
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400
        except yaml.YAMLError as exc:
            return jsonify(
                success=False,
                error=f'YAML parse error in {name}: {exc}',
            ), 400

        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            return jsonify(
                success=False,
                error=(
                    f'YAML top-level must be a mapping in {name}'
                ),
            ), 400
        normalized_text = text
        if not normalized_text.endswith('\n'):
            normalized_text += '\n'
        updates.append(
            dict(name=name, path=path, text=normalized_text)
        )

    saved = []
    try:
        for item in updates:
            _write_text_atomic(item['path'], item['text'])
            saved.append(item['name'])
    except Exception as exc:
        return jsonify(
            success=False,
            error=f'Failed writing YAML: {exc}',
            saved=saved,
        ), 500

    return jsonify(success=True, saved=saved)


def ariapp_api_manage_instruments_groups_create(self):
    """Create per-instrument groups for a given instrument."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.instrument.super_admin" not in (cur_perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json(silent=True) or {}
    instrument = str(body.get("instrument", "") or "").strip()
    if not instrument:
        return jsonify(success=False, error="instrument is required"), 400

    profiles = auth.load_apero_profiles(hydrate=False)
    if not isinstance(profiles, dict) or instrument not in profiles:
        return jsonify(
            success=False,
            error="Instrument '{}' not found in profiles".format(instrument),
        ), 404

    all_groups = permissions_mod.load_groups()
    created = []
    for level in _INSTRUMENT_GROUP_LEVELS:
        gname = "{}.{}".format(level, instrument)
        if gname not in all_groups:
            all_groups[gname] = {
                "permissions": [],
                "groups": [level],
            }
            created.append(gname)

    if created:
        permissions_mod.save_groups(all_groups)

    return jsonify(success=True, created=created)


def ariapp_api_manage_instruments_groups_delete(self):
    """Delete per-instrument groups for a given instrument."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "manage.instrument.super_admin" not in (cur_perms or set()):
        return jsonify(success=False, error="Insufficient permissions"), 403

    body = request.get_json(silent=True) or {}
    instrument = str(body.get("instrument", "") or "").strip()
    if not instrument:
        return jsonify(success=False, error="instrument is required"), 400

    all_groups = permissions_mod.load_groups()
    deleted = []
    for level in _INSTRUMENT_GROUP_LEVELS:
        gname = "{}.{}".format(level, instrument)
        if gname in all_groups:
            del all_groups[gname]
            deleted.append(gname)

    if deleted:
        permissions_mod.save_groups(all_groups)
        # Remove these group memberships from all users.
        all_users_raw = auth.load_users()
        for uname, udata in all_users_raw.items():
            if not isinstance(udata, dict):
                continue
            user_groups = list(udata.get("groups") or [])
            new_groups = [g for g in user_groups if g not in deleted]
            if new_groups != user_groups:
                all_users_raw[uname]["groups"] = new_groups
        auth.save_users(all_users_raw)

    return jsonify(success=True, deleted=deleted)


def ariapp_api_manage_instruments_add(self):
    """Add a new instrument stub entry to apero_profiles."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "add.instrument" not in (cur_perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    body = request.get_json(silent=True) or {}
    instrument = str(body.get("instrument", "") or "").strip().upper()
    if not instrument:
        return jsonify(
            success=False, error="instrument name is required"
        ), 400
    if not instrument.replace("_", "").replace("-", "").isalnum():
        return jsonify(
            success=False,
            error="Instrument name must be alphanumeric"
            " (underscores/hyphens allowed)",
        ), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    if not isinstance(all_profiles, dict):
        all_profiles = {}
    if instrument in all_profiles:
        return jsonify(
            success=False,
            error="Instrument '{}' already exists".format(instrument),
        ), 409

    all_profiles[instrument] = {}
    auth.save_apero_profiles(all_profiles)

    # Add instrument to parameters.yaml instruments list.
    _params = permissions_mod.load_parameters()
    _instr_block = _params.get("instruments")
    if isinstance(_instr_block, dict):
        _instr_list = _instr_block.get("value")
        if isinstance(_instr_list, list):
            if instrument not in _instr_list:
                _instr_list.append(instrument)
                permissions_mod.save_parameters(_params)

    # Also create the per-instrument groups immediately.
    all_groups = permissions_mod.load_groups()
    created_groups = []
    for level in _INSTRUMENT_GROUP_LEVELS:
        gname = "{}.{}".format(level, instrument)
        if gname not in all_groups:
            all_groups[gname] = {"permissions": [], "groups": [level]}
            created_groups.append(gname)
    if created_groups:
        permissions_mod.save_groups(all_groups)

    return jsonify(
        success=True,
        instrument=instrument,
        created_groups=created_groups,
    )


def ariapp_api_manage_instruments_remove(self):
    """Remove an instrument: deletes its profile entry and all groups."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "add.instrument" not in (cur_perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    body = request.get_json(silent=True) or {}
    instrument = str(body.get("instrument", "") or "").strip()
    if not instrument:
        return jsonify(
            success=False, error="instrument name is required"
        ), 400

    all_profiles = auth.load_apero_profiles(hydrate=False)
    if not isinstance(all_profiles, dict) or instrument not in all_profiles:
        return jsonify(
            success=False,
            error="Instrument '{}' not found".format(instrument),
        ), 404

    del all_profiles[instrument]
    auth.save_apero_profiles(all_profiles)

    # Remove instrument from parameters.yaml instruments list.
    _params = permissions_mod.load_parameters()
    _instr_block = _params.get("instruments")
    if isinstance(_instr_block, dict):
        _instr_list = _instr_block.get("value")
        if isinstance(_instr_list, list) and instrument in _instr_list:
            _instr_block["value"] = [
                i for i in _instr_list if i != instrument
            ]
            permissions_mod.save_parameters(_params)

    # Delete per-instrument groups and remove from users.
    all_groups = permissions_mod.load_groups()
    deleted_groups = []
    for level in _INSTRUMENT_GROUP_LEVELS:
        gname = "{}.{}".format(level, instrument)
        if gname in all_groups:
            del all_groups[gname]
            deleted_groups.append(gname)
    if deleted_groups:
        permissions_mod.save_groups(all_groups)
        all_users_raw = auth.load_users()
        for uname, udata in all_users_raw.items():
            if not isinstance(udata, dict):
                continue
            user_groups = list(udata.get("groups") or [])
            new_groups = [
                g for g in user_groups if g not in deleted_groups
            ]
            if new_groups != user_groups:
                all_users_raw[uname]["groups"] = new_groups
        auth.save_users(all_users_raw)

    return jsonify(
        success=True,
        instrument=instrument,
        deleted_groups=deleted_groups,
    )


def ariapp_api_manage_instruments_rename(self):
    """Rename an instrument across all ARI data stores."""
    user_info, cur_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    if "add.instrument" not in (cur_perms or set()):
        return jsonify(
            success=False, error="Insufficient permissions"
        ), 403

    body = request.get_json(silent=True) or {}
    old_name = str(body.get("old_name", "") or "").strip()
    new_name = (
        str(body.get("new_name", "") or "").strip().upper()
    )
    if not old_name or not new_name:
        return jsonify(
            success=False,
            error="old_name and new_name are required",
        ), 400
    if not new_name.replace("_", "").replace("-", "").isalnum():
        return jsonify(
            success=False,
            error=(
                "Instrument name must be alphanumeric"
                " (underscores/hyphens allowed)"
            ),
        ), 400

    try:
        summary = auth.rename_instrument(old_name, new_name)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(
            success=False,
            error=f"Rename failed: {exc}",
        ), 500

    return jsonify(success=True, summary=summary, new_name=new_name)


# =============================================================================
# Upload management — Admin APIs
# =============================================================================

def ariapp_api_admin_uploads_config_get(self):
    """Return all upload directory configurations."""
    user_info, user_perms = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    all_groups = sorted(self.ari_groups.keys())
    editor_groups = user_info.get("groups", [])
    editor_perms = permissions_mod.resolve_user_permissions(
        editor_groups, self.ari_groups
    )
    can_manage = sorted(
        g for g in all_groups if f"manage.group.{g}" in editor_perms
    )
    if auth.user_has_admin_privileges(editor_groups):
        can_manage = sorted(
            g for g in all_groups if g not in ("super_admin",)
        )
    if auth.user_is_super_admin(editor_groups):
        can_manage = all_groups

    directories = upd.get_all_directories()
    return jsonify(
        success=True,
        directories=directories,
        all_groups=all_groups,
        can_manage_groups=can_manage,
    )


def ariapp_api_admin_uploads_dir_add(self):
    """Add a new upload directory."""
    user_info, _ = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    path = str(body.get("path", "")).strip()
    dir_type = str(body.get("type", "per_user")).strip()
    quota_gb = body.get("quota_gb", 1.0)
    allowed_groups = list(body.get("allowed_groups", []))

    if not name:
        return jsonify(success=False, error="Name is required"), 400
    if not path:
        return jsonify(success=False, error="Path is required"), 400
    if dir_type not in ("per_user", "global"):
        return jsonify(
            success=False, error="type must be per_user or global"
        ), 400
    try:
        quota_gb = float(quota_gb)
        if quota_gb <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(
            success=False, error="quota_gb must be a positive number"
        ), 400

    # Validate allowed_groups against manageable groups
    editor_groups = user_info.get("groups", [])
    all_groups = set(self.ari_groups.keys())
    editor_perms = permissions_mod.resolve_user_permissions(
        editor_groups, self.ari_groups
    )
    if auth.user_is_super_admin(editor_groups):
        can_set = all_groups
    elif auth.user_has_admin_privileges(editor_groups):
        can_set = {g for g in all_groups if g != "super_admin"}
    else:
        can_set = {
            g for g in all_groups
            if f"manage.group.{g}" in editor_perms
        }
    invalid = set(allowed_groups) - can_set
    if invalid:
        return jsonify(
            success=False,
            error=f"Cannot set groups: {sorted(invalid)}",
        ), 403

    entry = upd.add_directory(name, path, dir_type, quota_gb, allowed_groups)
    return jsonify(success=True, entry=entry)


def ariapp_api_admin_uploads_dir_edit(self):
    """Edit an existing upload directory."""
    user_info, _ = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    dir_id = str(body.get("id", "")).strip()
    if not dir_id:
        return jsonify(success=False, error="id is required"), 400

    name = str(body.get("name", "")).strip()
    path = str(body.get("path", "")).strip()
    dir_type = str(body.get("type", "per_user")).strip()
    quota_gb = body.get("quota_gb", 1.0)
    allowed_groups = list(body.get("allowed_groups", []))

    if not name:
        return jsonify(success=False, error="Name is required"), 400
    if not path:
        return jsonify(success=False, error="Path is required"), 400
    if dir_type not in ("per_user", "global"):
        return jsonify(
            success=False, error="type must be per_user or global"
        ), 400
    try:
        quota_gb = float(quota_gb)
        if quota_gb <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(
            success=False, error="quota_gb must be a positive number"
        ), 400

    editor_groups = user_info.get("groups", [])
    all_groups = set(self.ari_groups.keys())
    editor_perms = permissions_mod.resolve_user_permissions(
        editor_groups, self.ari_groups
    )
    if auth.user_is_super_admin(editor_groups):
        can_set = all_groups
    elif auth.user_has_admin_privileges(editor_groups):
        can_set = {g for g in all_groups if g != "super_admin"}
    else:
        can_set = {
            g for g in all_groups
            if f"manage.group.{g}" in editor_perms
        }
    invalid = set(allowed_groups) - can_set
    if invalid:
        return jsonify(
            success=False,
            error=f"Cannot set groups: {sorted(invalid)}",
        ), 403

    updated = upd.edit_directory(
        dir_id, name, path, dir_type, quota_gb, allowed_groups
    )
    if updated is None:
        return jsonify(success=False, error="Directory not found"), 404
    return jsonify(success=True, entry=updated)


def ariapp_api_admin_uploads_dir_delete(self):
    """Delete an upload directory entry."""
    user_info, _ = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    body = request.get_json(silent=True) or {}
    dir_id = str(body.get("id", "")).strip()
    if not dir_id:
        return jsonify(success=False, error="id is required"), 400

    deleted = upd.delete_directory(dir_id)
    if not deleted:
        return jsonify(success=False, error="Directory not found"), 404
    return jsonify(success=True)


def ariapp_api_admin_uploads_quota_get(self):
    """Return quota usage for all configured upload directories."""
    user_info, _ = self._require_admin_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    dirs = upd.get_all_directories()
    result = []
    for d in dirs:
        rows = upd.get_all_users_quota(d)
        result.append({"id": d["id"], "name": d["name"], "rows": rows})
    return jsonify(success=True, quota=result)


# =============================================================================
# Upload management — User APIs
# =============================================================================

def _user_accessible_dirs(user_info):
    """Return directories that the user has access to upload to."""
    user_groups = set(user_info.get("groups", []))
    accessible = []
    for d in upd.get_all_directories():
        allowed = set(d.get("allowed_groups", []))
        if user_groups & allowed:
            accessible.append(d)
    return accessible


def ariapp_api_user_uploads_list(self):
    """List user's uploaded files per accessible directory."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    username = user_info["username"]
    accessible = _user_accessible_dirs(user_info)
    result = []
    for d in accessible:
        files = upd.list_user_files(d, username)
        quota_info = upd.get_quota_info_for_user(d, username)
        # Attach share tokens if they exist
        shares_data = upd._load_shares()
        token_map = {}
        for tok, info in shares_data.items():
            if (
                info.get("dir_id") == d["id"]
                and info.get("username") == username
            ):
                token_map[info["filename"]] = tok
        for f in files:
            f["share_token"] = token_map.get(f["filename"])
        result.append({
            "id": d["id"],
            "name": d["name"],
            "type": d["type"],
            "quota": quota_info,
            "files": files,
        })
    return jsonify(success=True, directories=result)


def ariapp_api_user_uploads_upload(self):
    """Handle a file upload from a user."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    username = user_info["username"]
    dir_id = request.form.get("dir_id", "").strip()
    if not dir_id:
        return jsonify(success=False, error="dir_id is required"), 400

    accessible = {d["id"]: d for d in _user_accessible_dirs(user_info)}
    if dir_id not in accessible:
        return jsonify(
            success=False, error="Access denied to this directory"
        ), 403

    if "file" not in request.files:
        return jsonify(success=False, error="No file part"), 400

    file_obj = request.files["file"]
    if not file_obj or not file_obj.filename:
        return jsonify(success=False, error="No file selected"), 400

    safe_name = secure_filename(file_obj.filename)
    if not safe_name:
        return jsonify(success=False, error="Invalid filename"), 400

    dir_cfg = accessible[dir_id]
    ok, err = upd.store_file(dir_cfg, username, safe_name, file_obj)
    if not ok:
        return jsonify(success=False, error=err), 400

    files = upd.list_user_files(dir_cfg, username)
    quota_info = upd.get_quota_info_for_user(dir_cfg, username)
    return jsonify(
        success=True,
        filename=safe_name,
        files=files,
        quota=quota_info,
    )


def ariapp_api_user_uploads_delete(self):
    """Delete a file from a user's upload directory."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    username = user_info["username"]
    body = request.get_json(silent=True) or {}
    dir_id = str(body.get("dir_id", "")).strip()
    filename = str(body.get("filename", "")).strip()

    if not dir_id or not filename:
        return jsonify(
            success=False, error="dir_id and filename are required"
        ), 400

    accessible = {d["id"]: d for d in _user_accessible_dirs(user_info)}
    if dir_id not in accessible:
        return jsonify(
            success=False, error="Access denied to this directory"
        ), 403

    dir_cfg = accessible[dir_id]
    safe_name = secure_filename(filename)
    if not safe_name or safe_name != filename:
        return jsonify(success=False, error="Invalid filename"), 400

    # Remove any share token for this file
    upd.delete_share_token(dir_id, username, safe_name)

    ok, err = upd.delete_file(dir_cfg, username, safe_name)
    if not ok:
        return jsonify(success=False, error=err), 400

    files = upd.list_user_files(dir_cfg, username)
    quota_info = upd.get_quota_info_for_user(dir_cfg, username)
    return jsonify(success=True, files=files, quota=quota_info)


def ariapp_api_user_uploads_share(self):
    """Create or retrieve a share link for an uploaded file."""
    user_info = self._require_user()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    username = user_info["username"]
    body = request.get_json(silent=True) or {}
    dir_id = str(body.get("dir_id", "")).strip()
    filename = str(body.get("filename", "")).strip()

    if not dir_id or not filename:
        return jsonify(
            success=False, error="dir_id and filename are required"
        ), 400

    accessible = {d["id"]: d for d in _user_accessible_dirs(user_info)}
    if dir_id not in accessible:
        return jsonify(
            success=False, error="Access denied to this directory"
        ), 403

    safe_name = secure_filename(filename)
    if not safe_name or safe_name != filename:
        return jsonify(success=False, error="Invalid filename"), 400

    dir_cfg = accessible[dir_id]
    upload_dir = upd._user_upload_dir(dir_cfg, username)
    target = upd._resolve_safe(upload_dir, safe_name)
    if target is None or not target.is_file():
        return jsonify(success=False, error="File not found"), 404

    token = upd.create_share_token(dir_id, username, safe_name)
    return jsonify(success=True, token=token)


def ariapp_uploads_share_download(self, token):
    """Serve a shared uploaded file by token."""
    result = upd.resolve_share_token(token)
    if result is None:
        return jsonify(error="Invalid or expired link"), 404

    dir_cfg, username, filename = result
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify(error="Invalid file"), 404

    upload_dir = upd._user_upload_dir(dir_cfg, username)
    target = upd._resolve_safe(upload_dir, safe_name)
    if target is None or not target.is_file():
        return jsonify(error="File not found"), 404

    return send_file(
        str(target),
        as_attachment=True,
        download_name=safe_name,
    )


# =============================================================================
# Vault — Admin portal
# =============================================================================
def ariapp_build_admin_vault_context(
    self, resolved_perms: set
) -> dict:
    """Build template context for the Vault admin page."""
    from apero_ri.core import vault_store as vs

    accessible = vs.accessible_levels(resolved_perms)
    manageable = set(vs.manageable_levels(resolved_perms))
    sections = []
    for level in accessible:
        sections.append({
            "level": level,
            "label": vs.VAULT_LEVEL_LABELS[level],
            "icon": vs.VAULT_LEVEL_ICONS[level],
            "can_manage": level in manageable,
        })
    return {
        "vault_sections": sections,
        "can_manage": bool(manageable),
    }


def ariapp_api_vault_list(self):
    """Return vault cards (no information) for user's levels."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.admin.vault" not in resolved:
        return jsonify(success=False, error="Forbidden"), 403

    levels = vs.accessible_levels(resolved)
    entries = vs.filter_by_level(vs.load_entries(), levels)
    safe = [vs.strip_information(e) for e in entries]
    return jsonify(success=True, entries=safe)


def ariapp_api_vault_get(self):
    """Return a single vault entry including information."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.admin.vault" not in resolved:
        return jsonify(success=False, error="Forbidden"), 403

    entry_id = request.args.get("id", "").strip()
    if not entry_id:
        return jsonify(success=False, error="id required"), 400

    entry = vs.get_entry(entry_id)
    if not entry:
        return jsonify(success=False, error="Not found"), 404

    levels = vs.accessible_levels(resolved)
    if entry.get("level", "moderator") not in levels:
        return jsonify(success=False, error="Forbidden"), 403

    return jsonify(success=True, entry=entry)


def ariapp_api_vault_add(self):
    """Create a new vault entry."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    manageable = vs.manageable_levels(resolved)
    if not manageable:
        return jsonify(success=False, error="Forbidden"), 403

    body = request.get_json(silent=True) or {}
    title = str(body.get("title", "") or "").strip()
    information = str(body.get("information", "") or "")
    level = str(
        body.get("level", "moderator") or "moderator"
    ).strip()

    if not title:
        return (
            jsonify(success=False, error="title is required"),
            400,
        )
    if level not in vs.VAULT_LEVELS:
        return jsonify(success=False, error="invalid level"), 400
    if level not in manageable:
        return (
            jsonify(
                success=False,
                error="Forbidden at that level",
            ),
            403,
        )

    entry = vs.save_entry(
        title=title,
        information=information,
        level=level,
        created_by=user_info["username"],
    )
    return jsonify(success=True, entry=vs.strip_information(entry))


def ariapp_api_vault_update(self):
    """Update an existing vault entry."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    manageable = vs.manageable_levels(resolved)
    if not manageable:
        return jsonify(success=False, error="Forbidden"), 403

    body = request.get_json(silent=True) or {}
    entry_id = str(body.get("id", "") or "").strip()
    title = str(body.get("title", "") or "").strip()
    information = str(body.get("information", "") or "")
    level = str(
        body.get("level", "moderator") or "moderator"
    ).strip()

    if not entry_id or not title:
        return (
            jsonify(
                success=False,
                error="id and title are required",
            ),
            400,
        )
    if level not in vs.VAULT_LEVELS:
        return jsonify(success=False, error="invalid level"), 400

    existing = vs.get_entry(entry_id)
    if not existing:
        return jsonify(success=False, error="Not found"), 404

    if existing.get("level", "moderator") not in manageable:
        return jsonify(success=False, error="Forbidden"), 403
    if level not in manageable:
        return (
            jsonify(
                success=False,
                error="Forbidden at that level",
            ),
            403,
        )

    entry = vs.save_entry(
        title=title,
        information=information,
        level=level,
        created_by=existing.get(
            "created_by", user_info["username"]
        ),
        entry_id=entry_id,
    )
    return jsonify(success=True, entry=vs.strip_information(entry))


def ariapp_api_vault_delete(self):
    """Delete a vault entry."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    manageable = vs.manageable_levels(resolved)
    if not manageable:
        return jsonify(success=False, error="Forbidden"), 403

    body = request.get_json(silent=True) or {}
    entry_id = str(body.get("id", "") or "").strip()
    if not entry_id:
        return (
            jsonify(success=False, error="id is required"),
            400,
        )

    existing = vs.get_entry(entry_id)
    if not existing:
        return jsonify(success=False, error="Not found"), 404

    if existing.get("level", "moderator") not in manageable:
        return jsonify(success=False, error="Forbidden"), 403

    vs.delete_entry(entry_id)
    return jsonify(success=True)


def ariapp_api_vault_export(self):
    """Export accessible vault entries as encrypted YAML."""
    import io
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    if "manage.admin.vault" not in resolved:
        return jsonify(success=False, error="Forbidden"), 403

    body = request.get_json(silent=True) or {}
    passphrase = str(
        body.get("passphrase", "") or ""
    ).strip()
    if not passphrase:
        return jsonify(
            success=False, error="passphrase is required"
        ), 400

    levels = vs.accessible_levels(resolved)
    entries = vs.filter_by_level(vs.load_entries(), levels)
    try:
        yaml_bytes = vs.export_vault_yaml(entries, passphrase)
    except Exception as exc:
        return jsonify(
            success=False, error=str(exc)
        ), 500

    buf = io.BytesIO(yaml_bytes)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/x-yaml",
        as_attachment=True,
        download_name="vault_export.yaml",
    )


def ariapp_api_vault_import(self):
    """Import vault entries from an encrypted YAML file."""
    from apero_ri.core import vault_store as vs

    user_info = auth.get_effective_user(session)
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401
    resolved = permissions_mod.resolve_user_permissions(
        user_info["groups"], self.ari_groups
    )
    manageable = vs.manageable_levels(resolved)
    if not manageable:
        return jsonify(success=False, error="Forbidden"), 403

    passphrase = str(
        request.form.get("passphrase", "") or ""
    ).strip()
    if not passphrase:
        return jsonify(
            success=False, error="passphrase is required"
        ), 400

    if "file" not in request.files:
        return jsonify(
            success=False, error="No file provided"
        ), 400
    file_obj = request.files["file"]
    yaml_bytes = file_obj.read()

    try:
        entries = vs.import_vault_yaml(yaml_bytes, passphrase)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(
            success=False,
            error=f"Import failed: {exc}",
        ), 500

    manageable_set = set(manageable)
    existing_ids = {
        e.get("id") for e in vs.load_entries()
    }
    added = 0
    skipped_level = 0
    skipped_duplicate = 0

    for entry in entries:
        if entry.get("level") not in manageable_set:
            skipped_level += 1
            continue
        if entry.get("id") in existing_ids:
            skipped_duplicate += 1
            continue
        vs.save_entry(
            title=entry.get("title", ""),
            information=entry.get("information", ""),
            level=entry.get("level", "moderator"),
            created_by=entry.get(
                "created_by", user_info["username"]
            ),
        )
        added += 1

    return jsonify(
        success=True,
        added=added,
        skipped_duplicate=skipped_duplicate,
        skipped_level=skipped_level,
    )
