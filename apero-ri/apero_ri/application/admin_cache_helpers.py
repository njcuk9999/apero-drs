"""Admin cache context helper functions for ARIApp."""

import json
from datetime import datetime
from pathlib import Path

from apero_ri.core.plot_cache import (
    CACHE_SECTIONS,
    cache_inventory,
    get_timing_reset_ts,
    load_cache_config,
)


def build_admin_cache_context(app, perms):
    """Build context for admin plot-cache settings page."""
    data_dir = app._resolve_local_data_dir()
    cfg = load_cache_config(data_dir)
    inv = cache_inventory(data_dir)

    # Aggregate per-plot timing stats from cached object_plots payloads.
    # Each cache file stores payload.server_timings_ms from API generation.
    cache_root = Path(inv.get("cache_dir", "") or "")
    for prof in inv.get("profiles", []):
        instrument = str(prof.get("instrument", "") or "").strip()
        profile_id = str(prof.get("profile_id", "") or "").strip()
        timing_rows = {}
        if instrument and profile_id and cache_root:
            pdir = cache_root / instrument / profile_id
            reset_ts = get_timing_reset_ts(pdir)

            def _after_reset(entry):
                """Return False if entry was cached before the reset point."""
                if reset_ts is None:
                    return True
                cached_at = (entry or {}).get("cached_at", "")
                if not cached_at:
                    return True
                try:
                    return (
                        datetime.fromisoformat(cached_at).timestamp()
                        >= reset_ts
                    )
                except Exception:
                    return True

            # object_plots / debug_plots: per-plot breakdown ----------------
            # Both sections store payload.server_timings_ms (ms per plot).
            _per_plot_sections = ["object_plots", "debug_plots"]
            for sec in _per_plot_sections:
                section_dir = pdir / sec
                if not section_dir.exists():
                    continue
                for cfile in section_dir.glob("*.json"):
                    try:
                        with open(cfile, "r", encoding="utf-8") as fh:
                            entry = json.load(fh)
                        if not _after_reset(entry):
                            continue
                        payload = (entry or {}).get("payload", {})
                        timings = payload.get(
                            "server_timings_ms", {}
                        )
                        if not isinstance(timings, dict):
                            continue
                        for plot_name, value in timings.items():
                            try:
                                ms = float(value)
                            except Exception:
                                continue
                            timing_rows.setdefault(
                                str(plot_name), []
                            ).append(ms)
                    except Exception:
                        continue

            # lbl_plots / qc_graphs: total generation time ------------------
            _sec_labels = [
                ("lbl_plots", "lbl (total)"),
                ("qc_graphs", "qc (total)"),
            ]
            for sec, label in _sec_labels:
                sec_dir = pdir / sec
                if not sec_dir.exists():
                    continue
                for cfile in sec_dir.glob("*.json"):
                    try:
                        with open(cfile, "r", encoding="utf-8") as fh:
                            entry = json.load(fh)
                        if not _after_reset(entry):
                            continue
                        gen_s = float(
                            (entry or {}).get("generation_time_s", 0) or 0
                        )
                        if gen_s <= 0:
                            continue
                        timing_rows.setdefault(label, []).append(
                            gen_s * 1000.0
                        )
                    except Exception:
                        continue

        prof["timing_stats"] = []
        for plot_name in sorted(timing_rows.keys()):
            values = timing_rows.get(plot_name, [])
            if not values:
                continue
            count = len(values)
            vmin = min(values)
            vmax = max(values)
            vmean = sum(values) / count
            prof["timing_stats"].append(
                {
                    "plot": plot_name,
                    "count": count,
                    "min_ms": round(vmin, 2),
                    "mean_ms": round(vmean, 2),
                    "max_ms": round(vmax, 2),
                }
            )

    return {
        "can_manage": "view.admin" in perms,
        "cache_cfg": cfg,
        "cache_inventory": inv,
        "cache_sections": CACHE_SECTIONS,
    }
