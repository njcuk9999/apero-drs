#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Developer plotting helpers for lightweight debug plotting."""

import platform
from typing import Optional, Sequence, Tuple, Any


# =============================================================================
# Define functions
# =============================================================================
def import_plotting(
    backend: Optional[str] = 'TkAgg',
    fallback_backends: Optional[Sequence[str]] = None,
    set_imshow_defaults: bool = True,
) -> Any:
    """
    Import matplotlib pyplot with APERO-style backend fallback.

    :param backend: str or None, preferred backend tried first
    :param fallback_backends: list-like or None, backends tried after backend
    :param set_imshow_defaults: bool, if True set defaults for plt.imshow

    :return: matplotlib.pyplot module

    :raises ImportError: if matplotlib cannot be imported with any backend
    """
    import matplotlib

    if fallback_backends is None:
        fallback_backends = ['Qt5Agg', 'GTKAgg', 'TKAgg', 'WXAgg', 'Agg']

    # Build an ordered backend list without duplicates.
    backend_order = []
    if isinstance(backend, str) and backend != '':
        backend_order.append(backend)
    for candidate in fallback_backends:
        if candidate not in backend_order:
            backend_order.append(candidate)

    # Avoid the macOS backend used in APERO plotting guards.
    if platform.system().lower() == 'darwin':
        backend_order = [name for name in backend_order if name != 'MacOSX']

    for candidate in backend_order:
        try:
            matplotlib.use(candidate, force=True)
            import matplotlib.pyplot as plt
            if set_imshow_defaults:
                _set_imshow_defaults(plt)
            return plt
        except Exception:
            continue

    emsg = 'Unable to import matplotlib.pyplot with backends: {0}'
    raise ImportError(emsg.format(', '.join(backend_order)))


def pyplot(
    backend: Optional[str] = 'TkAgg',
    fallback_backends: Optional[Sequence[str]] = None,
    set_imshow_defaults: bool = True,
) -> Any:
    """
    Convenience wrapper around import_plotting for debugger use.

    :param backend: str or None, preferred backend tried first
    :param fallback_backends: list-like or None, backends tried after backend
    :param set_imshow_defaults: bool, if True set defaults for plt.imshow

    :return: matplotlib.pyplot module
    """
    return import_plotting(
        backend=backend,
        fallback_backends=fallback_backends,
        set_imshow_defaults=set_imshow_defaults,
    )


# =============================================================================
# Define worker functions
# =============================================================================
def _set_imshow_defaults(plt: Any) -> None:
    """Patch plt.imshow so default origin/aspect match APERO debug usage."""
    marker_name = '_apero_default_imshow'
    # Avoid patching multiple times in the same Python session.
    if getattr(plt.imshow, marker_name, False):
        return

    old_imshow = plt.imshow

    def _imshow(*args: Tuple[Any, ...], **kwargs: Any):
        kwargs.setdefault('aspect', 'auto')
        kwargs.setdefault('origin', 'lower')
        return old_imshow(*args, **kwargs)

    setattr(_imshow, marker_name, True)
    plt.imshow = _imshow


# =============================================================================
# End of code
# =============================================================================

