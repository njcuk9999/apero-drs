"""Admin cache context helper functions for ARIApp."""

import json
from pathlib import Path

from apero_ri.core.plot_cache import (
    CACHE_SECTIONS,
    cache_inventory,
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
            section_dir = cache_root / instrument / profile_id / "object_plots"
            if section_dir.exists():
                for cfile in section_dir.glob("*.json"):
                    try:
                        with open(cfile, "r", encoding="utf-8") as fh:
                            entry = json.load(fh)
                        payload = (entry or {}).get("payload", {})
                        timings = payload.get("server_timings_ms", {})
                        if not isinstance(timings, dict):
                            continue
                        for plot_name, value in timings.items():
                            try:
                                ms = float(value)
                            except Exception:
                                continue
                            timing_rows.setdefault(str(plot_name), []).append(
                                ms
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
