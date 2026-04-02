#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI task recipe wrapper for LOCAL_TASK-enabled tasks.

This is a thin recipe front-end over ``apero_ri.tasks.apero_sync``.
It intentionally only allows tasks that declare ``LOCAL_TASK = True``.

Examples
--------
List tasks that can be run via this recipe::

    apero_ri_task --list-local-tasks

Run a task by passing params as inline JSON::

    apero_ri_task APERO_OBJECT_QUERY \
      --params-json '{"LOCAL_DATA_DIR": "/home/user/.ari", "INSTRUMENT": "SPIROU", "APERO_PROFILE_NAMES": ["my_profile"], "APERO_PROFILES": {"my_profile": {...}}, "TASK_CONFIG": {"force_run": true}}'
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from apero_ri.tasks import apero_sync


# =============================================================================
# Define functions
# =============================================================================
def run(task_key: str,
        params: Dict[str, Any],
        *,
        verbose: bool = True,
        log_file: Optional[str] = None) -> Dict[str, Any]:
    """Delegate to apero_sync.run for LOCAL_TASK-enabled tasks."""
    return apero_sync.run(task_key, params, verbose=verbose, log_file=log_file)


def _parse_params_json(params_json: str) -> Dict[str, Any]:
    """Parse a JSON string into the run params dict."""
    try:
        params = json.loads(params_json)
    except Exception as exc:
        raise ValueError(f'Invalid --params-json payload: {exc}')
    if not isinstance(params, dict):
        raise ValueError('--params-json must decode to a JSON object/dict')
    return params


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for local task execution via recipe."""
    parser = argparse.ArgumentParser(
        description='Run a LOCAL_TASK APERO RI task from the recipes entrypoint.',
    )
    parser.add_argument(
        '--list-local-tasks', action='store_true',
        help='List LOCAL_TASK-enabled task keys and exit.',
    )
    parser.add_argument(
        '--params-json', default='',
        help='Inline JSON object passed directly to apero_sync.run(task_key, params).',
    )
    parser.add_argument(
        '--log', default=None,
        help='Optional log file path.',
    )
    parser.add_argument(
        '--quiet', action='store_true',
        help='Suppress stdout progress messages.',
    )
    parser.add_argument(
        'task_key', nargs='?',
        help='LOCAL_TASK task key (for example APERO_OBJECT_QUERY).',
    )
    args = parser.parse_args(argv)

    if args.list_local_tasks:
        keys = apero_sync.local_task_keys()
        if not keys:
            print('No LOCAL_TASK-enabled tasks found.')
        else:
            print('LOCAL_TASK-enabled tasks:')
            for key in keys:
                print(f'- {key}')
        return 0

    if not args.task_key:
        parser.error('task_key is required unless --list-local-tasks is used')
    if not args.params_json:
        parser.error('--params-json is required unless --list-local-tasks is used')

    try:
        params = _parse_params_json(args.params_json)
    except ValueError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    result = run(
        args.task_key,
        params,
        verbose=not args.quiet,
        log_file=args.log,
    )

    if result.get('status') != 'completed':
        print(f"Task failed: {result.get('error', '')}", file=sys.stderr)
        return 1

    print(f"Done. Output files: {len(result.get('output_files', []))}")
    return 0


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    main()

# =============================================================================
# End of code
# =============================================================================
