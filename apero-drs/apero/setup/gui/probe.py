#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO setup gui: helpers run in a sub process

The gui server never imports the instrument definitions itself (that needs
an activated profile - DRS_UCONFIG - and the server works with many
profiles). Instead it runs:

    python -m apero.setup.gui.probe params   (every constant: Docs tab)
    python -m apero.setup.gui.probe report   (state report: Validate tab)

with DRS_UCONFIG set in the environment of the sub process (for "params"
any profile works, the gui uses a throw away one if there is none). The
result is printed as one json line starting with RESULT_PREFIX.

Created on 2026-11-27

@author: cook
"""
import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.setup.gui.probe.py'
# the prefix of the result line
RESULT_PREFIX = 'APERO_SETUP_GUI_RESULT: '
# the instrument constant registries (in get_clists order) -> user yaml
CLIST_FILES = ['user_config.yaml', 'user_constants.yaml',
               'user_keywords.yaml']
# the kind of each registry (Docs tab menu)
CLIST_KINDS = ['config', 'constants', 'keywords']


# =============================================================================
# Define functions
# =============================================================================
def _plain(value: Any) -> Any:
    """
    Convert a constant value to something json friendly

    :param value: Any, the value

    :return: Any, str / int / float / bool / None / list / dict
    """
    # NaN / inf are not valid json (shown as text instead)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): _plain(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_plain(val) for val in value]
    # types, paths, numpy values... as text
    if isinstance(value, type):
        return value.__name__
    return str(value)


def _const_info(const: Any, kind: str, yaml_file: str) -> Dict[str, Any]:
    """
    Describe one constant / keyword (json friendly)

    :param const: Const or Keyword, the definition
    :param kind: str, config / constants / keywords
    :param yaml_file: str, the user yaml the constant can be set in

    :return: dict(description, kind, ctype, dtype, options, minimum,
             maximum, unit, group, user, active, source, author, comment)
    """
    dtype = getattr(const, 'dtype', None)
    dtypei = getattr(const, 'dtypei', None)
    dtype_text = _plain(dtype)
    if dtypei is not None:
        dtype_text = '{0}[{1}]'.format(dtype_text, _plain(dtypei))
    options = getattr(const, 'options', None)
    return dict(description=str(getattr(const, 'description', '') or ''),
                kind=kind, ctype=type(const).__name__,
                dtype=dtype_text,
                options=None if options is None else [
                    str(opt) for opt in options],
                minimum=_plain(getattr(const, 'minimum', None)),
                maximum=_plain(getattr(const, 'maximum', None)),
                unit=_plain(getattr(const, 'unit', None)),
                group=_plain(getattr(const, 'group', None)),
                user=bool(getattr(const, 'user', False)),
                active=bool(getattr(const, 'active', False)),
                source=_plain(getattr(const, 'source', None)),
                author=_plain(getattr(const, 'author', None)),
                comment=_plain(getattr(const, 'comment', None)),
                file=yaml_file if getattr(const, 'user', False) else None)


def probe_params() -> Dict[str, Any]:
    """
    Get the description of every APERO constant, config value and header
    keyword, with its value for every instrument

    :return: dict(params=key -> info (see _const_info) + values
             (instrument -> value), instruments=list of str)
    """
    # imports here: needs DRS_UCONFIG (set by the gui)
    from aperocore.constants import load_functions
    from apero.instruments import select
    params: Dict[str, Dict[str, Any]] = dict()
    instruments: List[str] = []
    for instrument in select.INSTRUMENTS:
        if str(instrument).upper() == 'NONE':
            continue
        instruments.append(str(instrument))
        # the instrument registries (config, constants, keywords)
        inst = load_functions.load_pconfig(select.INSTRUMENTS, instrument)
        clists = inst.get_clists()
        for it, clist in enumerate(clists):
            kind = CLIST_KINDS[min(it, len(CLIST_KINDS) - 1)]
            yaml_file = CLIST_FILES[min(it, len(CLIST_FILES) - 1)]
            for key, const in clist.storage.items():
                if key not in params:
                    params[key] = _const_info(const, kind, yaml_file)
                    params[key]['values'] = dict()
                # keywords: the header card / default / comment
                params[key]['values'][str(instrument)] = _plain(
                    getattr(const, 'value', None))
                # a constant is a user setting if any instrument says so
                if getattr(const, 'user', False):
                    params[key]['user'] = True
                    params[key]['file'] = yaml_file
    return dict(params=params, instruments=instruments,
                files=CLIST_FILES)


def probe_report() -> Dict[str, Any]:
    """
    Collect the state report of the profile in DRS_UCONFIG

    :return: dict(report, text) - see drs_report.collect / to_text
    """
    # imports here: needs DRS_UCONFIG (set by the gui)
    from aperocore.constants import load_functions
    from apero.instruments import select
    from apero.tools.module.setup import drs_report
    # the profile constants (never cached: the gui may have edited them)
    params = load_functions.load_config(select.INSTRUMENTS, cache=False)
    report = drs_report.collect(params)
    return dict(report=report, text=drs_report.to_text(report))


def main(argv: Optional[List[str]] = None) -> int:
    """
    Run one probe and print its json result line

    :param argv: list of str or None, the arguments (default sys.argv)

    :return: int, the exit code
    """
    parser = argparse.ArgumentParser(description='APERO setup gui probes')
    parser.add_argument('kind', choices=['params', 'report'])
    args = parser.parse_args(argv)
    try:
        if args.kind == 'params':
            result = probe_params()
        else:
            result = probe_report()
    except Exception as error:
        result = dict(error='{0}: {1}'.format(type(error).__name__, error))
    sys.stdout.write('\n' + RESULT_PREFIX + json.dumps(result, default=str)
                     + '\n')
    sys.stdout.flush()
    return 0


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    sys.exit(main())

# =============================================================================
# End of code
# =============================================================================
