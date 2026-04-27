#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ARI Bokeh theme helper.

Apply the active ARI theme (default / light / dark) to a Bokeh
figure. Server-side endpoints that build Bokeh figures should accept
a ``theme`` parameter and call :func:`apply_bokeh_theme` on every
figure before serialising. The theme palette mirrors the CSS custom
properties in ``static/css/style.css`` so plots blend with the rest
of the page chrome.

See ``.github/instructions/ari-new-page.instructions.md`` §3 for the
contract.
"""

from typing import Optional
import threading

# Thread-local request-scoped theme. API endpoints set this from
# ``request.args.get('theme')`` before invoking any ``build_*`` plot
# helper; ``plot_to_components`` / ``plot_to_json_item`` consult it
# at serialisation time so individual builders need not change their
# signatures.
_THEME_TLS = threading.local()


def set_request_theme(theme: Optional[str]) -> None:
    """Store the active theme for this request/thread."""
    _THEME_TLS.theme = normalise_theme(theme)


def get_request_theme() -> str:
    """Return the active theme for this thread, defaulting to
    'default'.
    """
    return getattr(_THEME_TLS, "theme", "default")


def clear_request_theme() -> None:
    """Reset the active theme for this thread."""
    if hasattr(_THEME_TLS, "theme"):
        delattr(_THEME_TLS, "theme")

# Palette matches :root / [data-theme="dark"] in style.css /
# mobile_overrides.css. Keep these in sync if either file changes.
THEMES = {
    "default": {
        "bg": "#FFFFFF",
        "border": "#FFFFFF",
        "text": "#1a1a1a",
        "muted": "#666666",
        "grid": "#dee2e6",
        "axis": "#1a1a1a",
    },
    "light": {
        "bg": "#FFFFFF",
        "border": "#FFFFFF",
        "text": "#1a1a1a",
        "muted": "#666666",
        "grid": "#dee2e6",
        "axis": "#1a1a1a",
    },
    "dark": {
        "bg": "#161b22",
        "border": "#161b22",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "grid": "#30363d",
        "axis": "#e6edf3",
    },
}


def normalise_theme(theme: Optional[str]) -> str:
    """Coerce an arbitrary string to one of THEMES keys."""
    t = (theme or "default").strip().lower()
    if t not in THEMES:
        return "default"
    return t


def apply_bokeh_theme(fig, theme: Optional[str] = "default") -> None:
    """Apply ARI theme colors to a Bokeh figure in-place.

    Safe to call with any object: missing attributes are ignored so
    callers can pass figures, layouts, or even None without raising.
    """
    if fig is None:
        return
    palette = THEMES[normalise_theme(theme)]

    # Plot canvas
    for attr in ("background_fill_color", "border_fill_color",
                 "outline_line_color"):
        try:
            setattr(fig, attr, palette[
                "bg" if attr != "outline_line_color" else "grid"])
        except Exception:  # noqa: BLE001
            pass

    # Title
    try:
        if fig.title is not None:
            fig.title.text_color = palette["text"]
    except Exception:  # noqa: BLE001
        pass

    # Axes
    for ax_attr in ("xaxis", "yaxis"):
        try:
            ax = getattr(fig, ax_attr, None)
        except Exception:  # noqa: BLE001
            ax = None
        if ax is None:
            continue
        try:
            ax.axis_label_text_color = palette["text"]
            ax.major_label_text_color = palette["text"]
            ax.major_tick_line_color = palette["axis"]
            ax.minor_tick_line_color = palette["axis"]
            ax.axis_line_color = palette["axis"]
        except Exception:  # noqa: BLE001
            pass

    # Grid
    for grid_attr in ("xgrid", "ygrid"):
        try:
            g = getattr(fig, grid_attr, None)
        except Exception:  # noqa: BLE001
            g = None
        if g is None:
            continue
        try:
            g.grid_line_color = palette["grid"]
            g.minor_grid_line_color = palette["grid"]
            g.minor_grid_line_alpha = 0.25
        except Exception:  # noqa: BLE001
            pass

    # Legend(s)
    try:
        legends = list(getattr(fig, "legend", []) or [])
    except Exception:  # noqa: BLE001
        legends = []
    for lg in legends:
        try:
            lg.label_text_color = palette["text"]
            lg.background_fill_color = palette["bg"]
            lg.background_fill_alpha = 0.85
            lg.border_line_color = palette["grid"]
        except Exception:  # noqa: BLE001
            pass


def theme_palette(theme: Optional[str]) -> dict:
    """Return a copy of the palette dict for templating purposes."""
    return dict(THEMES[normalise_theme(theme)])


def fg_glyph_color(theme: Optional[str] = None) -> str:
    """Return the high-contrast foreground glyph colour for *theme*.

    Plot builders that previously hardcoded ``color="black"`` for an
    "overall" or "primary" series (which becomes invisible on the
    dark theme's near-black background) should call this helper
    instead. Defaults to the active request-thread theme if none is
    given. Returns black on light/default and white on dark.
    """
    t = normalise_theme(theme if theme is not None else get_request_theme())
    return "#FFFFFF" if t == "dark" else "#000000"


def apply_theme_to_layout(obj, theme: Optional[str] = "default") -> None:
    """Walk a Bokeh model tree and apply ``apply_bokeh_theme`` to every
    Plot/Figure encountered. Safe to pass any Bokeh model, layout, or
    None.
    """
    if obj is None:
        return
    try:
        from bokeh.models import Plot
    except Exception:  # noqa: BLE001
        # Bokeh not available — caller will already have failed
        return
    # If the root itself is a Plot, theme it
    try:
        if isinstance(obj, Plot):
            apply_bokeh_theme(obj, theme)
    except Exception:  # noqa: BLE001
        pass
    # Walk children via .select if available
    try:
        for plot in obj.select({"type": Plot}):
            apply_bokeh_theme(plot, theme)
    except Exception:  # noqa: BLE001
        pass
