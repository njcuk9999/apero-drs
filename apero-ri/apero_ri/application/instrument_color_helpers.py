"""Instrument color helpers shared across application modules."""

from apero_ri.core import permissions as perms

INSTRUMENT_PALETTE = [
    {"bg": "#e3f2fd", "text": "#1565c0", "border": "#90caf9"},
    {"bg": "#e8f5e9", "text": "#2e7d32", "border": "#a5d6a7"},
    {"bg": "#fff3e0", "text": "#e65100", "border": "#ffcc80"},
    {"bg": "#f3e5f5", "text": "#6a1b9a", "border": "#ce93d8"},
    {"bg": "#ffebee", "text": "#c62828", "border": "#ef9a9a"},
    {"bg": "#e0f2f1", "text": "#00695c", "border": "#80cbc4"},
    {"bg": "#fff8e1", "text": "#f57f17", "border": "#ffe082"},
    {"bg": "#e8eaf6", "text": "#283593", "border": "#9fa8da"},
]

DEFAULT_INSTRUMENT_COLOR = INSTRUMENT_PALETTE[0]


def instrument_colors() -> dict:
    """Map each instrument to a stable palette entry."""
    params = perms.load_parameters()
    all_instr = params.get("instruments", {}).get("value", [])
    palette = INSTRUMENT_PALETTE
    return {
        inst: palette[idx % len(palette)] for idx, inst in enumerate(all_instr)
    }
