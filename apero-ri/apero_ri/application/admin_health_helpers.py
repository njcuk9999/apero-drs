"""Admin health helper functions for ARIApp."""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from apero_ri.core import backup_backend as bb
from apero_ri.core import email_backend as eb
from apero_ri.core import sshfs_backend as sb
from apero_ri.core import task_runner
from apero_ri.core.auth import (
    get_effective_user,
    get_users_for_instrument,
    load_async_tasks,
    load_science_groups,
    load_users,
)
from apero_ri.core.log import get_logger
from apero_ri.core.permissions import (
    get_children,
    load_parameters,
    page_id_to_url,
    resolve_user_permissions,
)

log = get_logger(__name__)


def get_admin_health(
    app, user_info, perms, force: bool = False, allow_async_refresh: bool = True
):
    """Return cached admin-health with optional async/sync refresh."""
    cache_key = app._admin_health_cache_key(perms)
    now = datetime.now(timezone.utc)

    with app._admin_health_cache_lock:
        entry = app._admin_health_cache.get(cache_key)

    if force:
        app._refresh_admin_health_entry(cache_key, user_info, perms)
        with app._admin_health_cache_lock:
            refreshed = app._admin_health_cache.get(cache_key, {})
        return (
            refreshed.get("health", {}),
            refreshed.get("updated_at"),
            refreshed.get("in_progress", False),
        )

    if entry:
        updated_at = entry.get("updated_at")
        fresh = (
            updated_at is not None
            and (now - updated_at) <= app._admin_health_cache_ttl
        )
        if fresh:
            return (
                entry.get("health", {}),
                updated_at,
                entry.get("in_progress", False),
            )

        if allow_async_refresh:
            app._spawn_admin_health_refresh(cache_key, user_info, perms)
            with app._admin_health_cache_lock:
                stale = app._admin_health_cache.get(cache_key, {})
            return (
                stale.get("health", {}),
                stale.get("updated_at"),
                stale.get("in_progress", False),
            )

        app._refresh_admin_health_entry(cache_key, user_info, perms)
        with app._admin_health_cache_lock:
            refreshed = app._admin_health_cache.get(cache_key, {})
        return (
            refreshed.get("health", {}),
            refreshed.get("updated_at"),
            refreshed.get("in_progress", False),
        )

    if allow_async_refresh:
        with app._admin_health_cache_lock:
            app._admin_health_cache[cache_key] = {
                "health": {},
                "updated_at": None,
                "in_progress": False,
                "perms": sorted(perms),
            }
        app._spawn_admin_health_refresh(cache_key, user_info, perms)
        with app._admin_health_cache_lock:
            pending = app._admin_health_cache.get(cache_key, {})
        return (
            pending.get("health", {}),
            pending.get("updated_at"),
            pending.get("in_progress", False),
        )

    app._refresh_admin_health_entry(cache_key, user_info, perms)
    with app._admin_health_cache_lock:
        refreshed = app._admin_health_cache.get(cache_key, {})
    return (
        refreshed.get("health", {}),
        refreshed.get("updated_at"),
        refreshed.get("in_progress", False),
    )


def refresh_admin_health_after_change(
    app, user_info=None, perms=None, session_obj=None
) -> None:
    """Refresh admin-health cache after successful admin mutations."""
    try:
        if user_info is None:
            user_info = get_effective_user(session_obj)
        if not user_info:
            return

        if perms is None:
            perms = resolve_user_permissions(
                user_info.get("groups", []),
                app.ari_groups,
            )
        perms = perms or set()
        if "view.admin" not in perms:
            return

        app._get_admin_health(
            user_info=user_info,
            perms=perms,
            force=True,
            allow_async_refresh=True,
        )
    except Exception as exc:
        log.warning("Failed to trigger background health refresh: %s", exc)
        return


def build_admin_card_health_uncached(app, user_info, perms) -> Dict[str, Any]:
    """Build uncached health payload for admin cards."""
    health: Dict[str, Any] = {}

    _t0 = time.monotonic()
    if "view.admin" in perms:
        try:
            all_users = load_users()
            unreviewed = sum(
                1
                for _u, ud_data in all_users.items()
                if set(ud_data.get("groups", [])) <= {"public"}
            )
            if unreviewed:
                health["home.admin_portal.users"] = {
                    "status": "warning",
                    "message": (
                        f'{unreviewed} user(s) with only "public" '
                        "access - may need group assignment."
                    ),
                }
            else:
                health["home.admin_portal.users"] = {
                    "status": "ok",
                    "message": "",
                }
        except Exception as exc:
            log.warning("admin health: users check failed: %s", exc)
    if "home.admin_portal.users" in health:
        health["home.admin_portal.users"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "view.admin" in perms:
        try:
            email_cfg = eb.load_email_config()
            if not email_cfg.get("enabled", False):
                health["home.admin_portal.email"] = {
                    "status": "warning",
                    "message": "Email delivery is not"
                    "enabled. Verification codes go to log file.",

                }
            else:
                test = eb.test_email_connection(email_cfg, quick_test=True)
                if test["ok"]:
                    health["home.admin_portal.email"] = {
                        "status": "ok",
                        "message": "",
                    }
                else:
                    health["home.admin_portal.email"] = {
                        "status": "error",
                        "message": f'SMTP connection failed: {test["error"]}',
                    }
        except Exception as exc:
            log.warning("admin health: email check failed: %s", exc)
    if "home.admin_portal.email" in health:
        health["home.admin_portal.email"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "view.admin" in perms:
        try:
            backup_cfg = bb.load_backup_config()
            methods = bb.get_backup_methods(backup_cfg, enabled_only=False)
            active_id = str(
                backup_cfg.get("active_method_id", "") or ""
            ).strip()
            active_method = None
            for method in methods:
                if str(method.get("id", "")) == active_id:
                    active_method = method
                    break
            if active_method is None and methods:
                active_method = methods[0]

            active_enabled = bool(active_method.get("enabled", False))
            active_provider = str(
                active_method.get("provider", "local_only") or "local_only"
            ).strip()
            cloud_providers = {"gdrive_oauth", "s3", "ssh_rsync", "local_copy"}
            if (
                not active_enabled
                or active_provider not in cloud_providers
            ):
                msg = "Cloud backup mirror is not enabled (local backups only)."
                method_name = str(
                    active_method.get("name", "")
                    or active_method.get("id", "active method")
                ).strip()
                if not active_enabled:
                    msg = (
                        "Cloud backup mirror is not enabled (local backups "
                        f"only). Active method '{method_name}' is disabled."
                    )
                elif active_provider == "local_only":
                    msg = (
                        "Cloud backup mirror is not enabled (local backups "
                        "only). Active method is configured as local-only."
                    )
                health["home.admin_portal.backup_settings"] = {
                    "status": "warning",
                    "message": msg,

                }
            else:
                test = bb.test_backup_connection(backup_cfg)
                if test.get("ok", False):
                    health["home.admin_portal.backup_settings"] = {
                        "status": "ok",
                        "message": "",
                    }
                else:
                    health["home.admin_portal.backup_settings"] = {
                        "status": "error",
                        "message": f'Cloud backup test failed: {
                            test.get(
                                "error",
                                "unknown error")}',
                    }
        except Exception as exc:
            log.warning("admin health: backup check failed: %s", exc)
    if "home.admin_portal.backup_settings" in health:
        health["home.admin_portal.backup_settings"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "view.admin" in perms:
        try:
            health_check = sb.health_check()
            health["home.admin_portal.sshfs_management"] = health_check
        except Exception as exc:
            log.warning("admin health: sshfs check failed: %s", exc)
    if "home.admin_portal.sshfs_management" in health:
        health["home.admin_portal.sshfs_management"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "manage.apero_profile" in perms:
        try:
            overview = app._build_apero_profiles_overview_status()
            profile_errors = overview.get("issues", [])
            if profile_errors:
                health["home.admin_portal.apero_profiles"] = {
                    "status": "error",
                    "message": (
                        f"Some APERO profiles need attention. "
                        f'{"; ".join(profile_errors[:3])}'
                        f'{"; ..." if len(profile_errors) > 3 else ""}'
                    ),
                }
            else:
                health["home.admin_portal.apero_profiles"] = {
                    "status": "ok",
                    "message": "",
                }
        except Exception as exc:
            log.warning("admin health: apero profiles check failed: %s", exc)
    if "home.admin_portal.apero_profiles" in health:
        health["home.admin_portal.apero_profiles"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "manage.apero_profile" in perms:
        try:
            all_tasks = load_async_tasks()
            failed_tasks = []

            for instrument, task_list in all_tasks.items():
                if not isinstance(task_list, list):
                    continue
                for task_cfg in task_list:
                    if not isinstance(task_cfg, dict):
                        continue
                    if task_cfg.get("active", True) is False:
                        continue

                    task_id = str(task_cfg.get("id", "") or "").strip()
                    runtime = (
                        task_runner.get_task_status(task_id)
                        if task_id
                        else {"found": False}
                    )

                    if runtime.get("found"):
                        status = str(runtime.get("status", "") or "")
                        error = str(runtime.get("error", "") or "").strip()
                    else:
                        status = str(task_cfg.get("last_status", "") or "")
                        persisted = task_runner.get_persisted_task_info_error(
                            task_id
                        )
                        error = str(
                            persisted.get("error", "")
                            or task_cfg.get("error", "")
                            or ""
                        ).strip()

                    if status == "failed" or error:
                        label = str(
                            task_cfg.get("task_key", task_id) or task_id
                        )
                        failed_tasks.append(f"{instrument}:{label}")

            if failed_tasks:
                health["home.admin_portal.async_tasks"] = {
                    "status": "error",
                    "message": (
                        f"{len(failed_tasks)} active task(s) in error: "
                        f'{", ".join(failed_tasks[:3])}'
                        f'{" ..." if len(failed_tasks) > 3 else ""}'
                    ),
                }
            else:
                health["home.admin_portal.async_tasks"] = {
                    "status": "ok",
                    "message": "",
                }
        except Exception as exc:
            log.warning("admin health: async tasks check failed: %s", exc)
    if "home.admin_portal.async_tasks" in health:
        health["home.admin_portal.async_tasks"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    has_sci_group = any(
        p.startswith("manage.sci_group.") for p in perms
    )
    if has_sci_group:
        try:
            params = load_parameters()
            all_instr = params.get("instruments", {}).get("value", [])
            instruments = [
                i for i in all_instr
                if f"manage.sci_group.{i}" in perms
            ]

            total_users = set()
            assigned_users = set()
            total_run_ids = set()
            assigned_run_ids = set()
            groups_without_users = []
            groups_without_run_ids = []
            run_id_pi_map = {}
            for inst in instruments:
                inst_users = set(get_users_for_instrument(inst))
                total_users |= inst_users
                inst_run_ids = {
                    str(rid).strip()
                    for rid in app._get_instrument_run_ids(inst)
                    if str(rid).strip()
                }
                total_run_ids |= inst_run_ids
                run_id_pi_map.update(
                    app._get_instrument_run_id_pi_names(inst)
                )

                groups = load_science_groups(inst)
                groups, _ = app._sync_all_science_group(
                    inst,
                    groups=groups,
                    run_ids=sorted(inst_run_ids),
                    persist=True,
                )

                for gname, entry in groups.items():
                    if not isinstance(entry, dict):
                        continue
                    is_all_group = app._is_all_science_group(gname)

                    group_users = []
                    for username in entry.get("users", []):
                        uname = str(username).strip()
                        if uname:
                            group_users.append(uname)
                            assigned_users.add(uname)

                    group_run_ids = []
                    for run_id in entry.get("run_ids", []):
                        rid = str(run_id).strip()
                        if rid:
                            group_run_ids.append(rid)
                            if not is_all_group:
                                assigned_run_ids.add(rid)

                    if not group_users and not is_all_group:
                        groups_without_users.append(f"{inst}:{gname}")
                    if not group_run_ids and not is_all_group:
                        groups_without_run_ids.append(f"{inst}:{gname}")

            unassigned_users = sorted(total_users - assigned_users)
            unassigned_run_ids = sorted(total_run_ids - assigned_run_ids)

            issue_parts = []
            details = []

            if unassigned_users:
                issue_parts.append(
                    f"{len(unassigned_users)} user(s) not assigned "
                    "to any science group"
                )
                details.extend([f"user: {u}" for u in unassigned_users])

            if groups_without_users:
                issue_parts.append(
                    f"{len(groups_without_users)} science group(s) "
                    "without users"
                )
                details.extend(
                    [
                        f"group-without-users: {name}"
                        for name in groups_without_users
                    ]
                )

            if groups_without_run_ids:
                issue_parts.append(
                    f"{len(groups_without_run_ids)} science group(s) "
                    "without run IDs"
                )
                details.extend(
                    [
                        f"group-without-run-ids: {name}"
                        for name in groups_without_run_ids
                    ]
                )

            if unassigned_run_ids:
                issue_parts.append(
                    f"{len(unassigned_run_ids)} run ID(s) not "
                    "assigned to any science group"
                )
                for rid in unassigned_run_ids:
                    pi = run_id_pi_map.get(rid, '')
                    if pi:
                        details.append(f"run_id: {rid} [{pi}]")
                    else:
                        details.append(f"run_id: {rid}")

            if issue_parts:
                health["home.admin_portal.science_groups"] = {
                    "status": "warning",
                    "message": "; ".join(issue_parts) + ".",
                    "details": details,
                }
            else:
                if not total_users:
                    health["home.admin_portal.science_groups"] = {
                        "status": "warning",
                        "message": "No users are currently assigned "
                        "to managed instruments.",
                    }
                else:
                    health["home.admin_portal.science_groups"] = {
                        "status": "ok",
                        "message": (
                            f"All {len(total_users)} users and "
                            f"{len(total_run_ids)} run ID(s) are "
                            "assigned to at least one "
                            "science group, and all groups have users/run IDs."
                        ),
                    }
        except Exception as exc:
            health["home.admin_portal.science_groups"] = {
                "status": "error",
                "message": f"Science group health check failed: {exc}",
            }
    if "home.admin_portal.science_groups" in health:
        health["home.admin_portal.science_groups"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "manage.admin.user_db_access" in perms:
        try:
            report = app._build_user_db_access_health_report(user_info)
            health["home.admin_portal.user_db_access"] = {
                "status": report.get("status", "warning"),
                "message": str(report.get("message", "")).strip(),
            }
        except Exception as exc:
            health["home.admin_portal.user_db_access"] = {
                "status": "error",
                "message": f"User DB access health check failed: {exc}",
            }
    if "home.admin_portal.user_db_access" in health:
        health["home.admin_portal.user_db_access"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    _t0 = time.monotonic()
    if "manage.apero_profile" in perms:
        try:
            from apero_ri.application.page_view_helpers import (
                _build_apero_policy_payload,
                _build_checks_policy_health,
            )
            from apero_ri.core import apero_checks as checks_core
            local_data_dir = app._resolve_local_data_dir()
            chk_cfg = checks_core.load_config(local_data_dir)
            ignored = checks_core.load_ignored_checks(local_data_dir)
            override = checks_core.load_override_allowed(local_data_dir)
            payload = _build_apero_policy_payload(
                local_data_dir, chk_cfg, ignored, override,
            )
            chk_health = _build_checks_policy_health(
                payload.get('checks_catalog', []),
                ignored,
            )
            health["home.admin_portal.apero_checks_policy"] = {
                "status": chk_health["status"],
                "message": chk_health["message"],
                "details": chk_health.get("details", []),
            }
        except Exception as exc:
            log.warning("admin health: apero checks policy check failed: %s", exc)
    if "home.admin_portal.apero_checks_policy" in health:
        health["home.admin_portal.apero_checks_policy"]["duration_s"] = round(
            time.monotonic() - _t0, 2
        )

    return health


def build_admin_health_rows(app, health: dict) -> list:
    """Build ordered health rows for the Admin Portal health panel."""
    checks = {
        "home.admin_portal.users": {
            "ok": "All users have at least one non-public group assignment.",
            "warning": "Some users still only have public access"
            "and should be reviewed.",

            "error": "User assignment checks failed.",
        },
        "home.admin_portal.science_groups": {
            "ok": "All users are assigned to at least one science group.",
            "warning": "At least one user is not assigned to any"
            "science group.",

            "error": "Science-group assignment checks failed.",
        },
        "home.admin_portal.email": {
            "ok": "Email delivery is enabled and SMTP connectivity"
            "check succeeds.",

            "warning": "Email delivery is disabled or running in"
            "non-email mode.",

            "error": "SMTP connectivity failed.",
        },
        "home.admin_portal.apero_profiles": {
            "ok": "All APERO profiles pass database and path checks.",
            "warning": "Some APERO profile checks need attention.",
            "error": "One or more APERO profiles failed validation checks.",
        },
        "home.admin_portal.apero_checks_policy": {
            "ok": (
                "All active checks are passing with complete "
                "documentation."
            ),
            "warning": (
                "Some checks have incomplete documentation metadata."
            ),
            "error": (
                "One or more active checks have more failures "
                "than passes."
            ),
        },
        "home.admin_portal.user_db_access": {
            "ok": "All APERO profiles have complete DB table access rules.",
            "warning": "At least one APERO profile has incomplete"
            "DB table access rules.",

            "error": "DB-access health checks failed.",
        },
        "home.admin_portal.async_tasks": {
            "ok": "No active async tasks are in failed/error state.",
            "warning": "Some async task checks are inconclusive.",
            "error": "One or more active async tasks are in"
            "failed/error state.",

        },
        "home.admin_portal.backup_settings": {
            "ok": "Cloud backup is properly configured and"
            "connection check succeeds.",

            "warning": "Cloud backup mirror is not enabled "
            "(local backups only).",

            "error": "Cloud backup test failed.",
        },
        "home.admin_portal.sshfs_management": {
            "ok": "All configured SSHFS mounts are mounted.",
            "warning": "Some SSHFS mounts are not currently"
            "mounted, or no mounts are configured.",

            "error": "One or more SSHFS mounts have connection issues.",
        },
    }

    rows = []
    for pid in get_children("home.admin_portal", app.ari_pages):
        status_data = health.get(pid)
        if not isinstance(status_data, dict):
            continue
        status = str(status_data.get("status", "warning")).strip() or "warning"
        if status not in {"ok", "warning", "error"}:
            status = "warning"
        msg = str(status_data.get("message", "")).strip()
        details = status_data.get("details", [])
        if not isinstance(details, list):
            details = []
        details = [str(item).strip() for item in details if str(item).strip()]

        rules = checks.get(pid, {})
        rule_msg = str(rules.get(status, "")).strip()
        page_def = app.ari_pages.get(pid, {})
        page_label = str(page_def.get("label", pid)).strip()

        duration_s = status_data.get("duration_s")
        rows.append(
            {
                "page_id": pid,
                "label": page_label,
                "url": page_id_to_url(pid),
                "status": status,
                "message": msg or rule_msg,
                "rule_message": rule_msg,
                "details": details,
                "duration_s": duration_s,
            }
        )

    return rows
