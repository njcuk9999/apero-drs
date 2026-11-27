#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetch read-only remote diagnostics for a local coding/chat session."""

import argparse
import getpass
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Callable

from aperocore import drs_lang
from apero_ri.ari_api import diagnostics
from apero_ri.base import base
from apero_ri.core import log as ri_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.recipes.apero_ri_debug'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
# progress goes to stderr so stdout stays the list of saved files
LOG = ri_log.get_logger(__NAME__)
# log a "still collecting" line every N server heartbeats (10 s each)
HEARTBEATS_PER_UPDATE = 3

# =============================================================================
# Define functions
# =============================================================================
def _progress_logger(label: str,
                     started: float) -> Callable[[dict], None]:
    """Build a stream callback that logs stages and periodic waits.

    :param label: ``INSTRUMENT / profile`` shown on every line.
    :param started: ``time.time()`` when this profile's request began.
    :return: Callback accepting one server stream event.
    """
    state = dict(stage='runtime', beats=0)

    def on_event(event: dict) -> None:
        """Log one progress or heartbeat event from the server.

        :param event: Decoded stream event.
        :return: None.
        """
        if event.get('type') == 'progress':
            total = event.get('total') or 1
            percent = int(100 * event.get('completed', 0) / total)
            state['stage'] = str(event.get('stage', ''))
            state['beats'] = 0
            LOG.info(str(drs_lang.textentry(
                'ARI_DIAGNOSTICS_CLI_PROGRESS',
                args=[label, percent, state['stage']])))
        elif event.get('type') == 'heartbeat':
            state['beats'] += 1
            # a slow stage sends only heartbeats; report it periodically
            if state['beats'] % HEARTBEATS_PER_UPDATE == 0:
                elapsed = int(time.time() - started)
                LOG.info(str(drs_lang.textentry(
                    'ARI_DIAGNOSTICS_CLI_WAITING',
                    args=[label, elapsed, state['stage']])))

    return on_event


def main(argv: list[str] | None = None) -> int:
    """Download reports for the profiles explicitly authorized by a grant.

    :param argv: Optional CLI arguments for deterministic testing.
    :return: Exit status, zero when all requested reports were downloaded.
    """
    description = drs_lang.textentry('ARI_DIAGNOSTICS_CLI_DESCRIPTION')
    parser = argparse.ArgumentParser(description=str(description))
    parser.add_argument('--host', required=True, metavar='URL')
    parser.add_argument('--key', nargs='?', const='', default='',
                        metavar='EXPIRING_KEY')
    parser.add_argument('--profile', action='append', default=[])
    parser.add_argument('--object', default='')
    parser.add_argument('--pid', default='')
    parser.add_argument('--logs', action='store_true')
    parser.add_argument('--no-database', action='store_true')
    parser.add_argument('--output', type=Path,
                        default=Path('apero-diagnostics'))
    args = parser.parse_args(argv)
    key = args.key or os.environ.get('APERO_RI_DEBUG_KEY', '')
    if not key:
        prompt = drs_lang.textentry('ARI_DIAGNOSTICS_KEY_PROMPT')
        key = getpass.getpass(str(prompt))
    if not key:
        parser.error(str(drs_lang.textentry('ARI_DIAGNOSTICS_ERROR',
                                           args=['missing_key'])))
    # timestamped progress lines on stderr
    ri_log.configure_logging(fmt='[%(asctime)s] %(message)s')
    try:
        LOG.info(str(drs_lang.textentry('ARI_DIAGNOSTICS_CLI_CONNECT',
                                        args=[args.host])))
        listing = diagnostics.request_report(args.host, key)
        profiles = listing['profiles']
        available = {row['profile_id'] for row in profiles}
        if set(args.profile) - available:
            raise ValueError('profile_not_authorized')
        if args.profile:
            profiles = [row for row in profiles
                        if row['profile_id'] in args.profile]
        if not profiles:
            raise ValueError('no_authorized_profiles')
        names = ', '.join(row['instrument'] + '/' + row['profile_id']
                          for row in profiles)
        LOG.info(str(drs_lang.textentry('ARI_DIAGNOSTICS_CLI_PROFILES',
                                        args=[len(profiles), names])))
        args.output.mkdir(parents=True, exist_ok=True, mode=0o700)
        output = args.output.resolve()
        downloaded = []
        for index, profile in enumerate(profiles, start=1):
            instrument, name = profile['instrument'], profile['profile_id']
            if not all(value and all(char.isalnum() or char in '_-'
                                      for char in value)
                       for value in (instrument, name)):
                raise ValueError('invalid_profile_identifier')
            filters = dict(profile_id=name, instrument=instrument,
                           objname=args.object, pid=args.pid,
                           logs='1' if args.logs else '0',
                           database='0' if args.no_database else '1')
            label = instrument + ' / ' + name
            LOG.info(str(drs_lang.textentry(
                'ARI_DIAGNOSTICS_CLI_COLLECT',
                args=[index, len(profiles), label])))
            started = time.time()
            # stream so stages and heartbeats arrive while the server works
            stream_kwargs = dict(on_event=_progress_logger(label, started))
            report = diagnostics.request_report(args.host, key, 'stream',
                                                 filters, **stream_kwargs)
            path = output / f'{instrument}-{name}.json'
            with tempfile.NamedTemporaryFile(mode='w', dir=output,
                                             delete=False) as temporary:
                temporary_path = Path(temporary.name)
                try:
                    json.dump(report, temporary, indent=2, allow_nan=False)
                    temporary.flush()
                    os.fsync(temporary.fileno())
                    temporary_path.replace(path)
                finally:
                    temporary_path.unlink(missing_ok=True)
            downloaded.append(str(path))
            size = round(path.stat().st_size / 1024 ** 2, 1)
            LOG.info(str(drs_lang.textentry(
                'ARI_DIAGNOSTICS_CLI_SAVED',
                args=[label, path, size, int(time.time() - started)])))
        message = drs_lang.textentry('ARI_DIAGNOSTICS_DOWNLOADED',
                                     args=['\n'.join(downloaded)])
        print(str(message))
        return 0
    except Exception as error:
        from aperocore.core.diagnostics import redact

        safe_error = redact(str(error), [key])
        message = drs_lang.textentry('ARI_DIAGNOSTICS_ERROR', args=[safe_error])
        LOG.error(str(message))
        return 1


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    raise SystemExit(main())

# =============================================================================
# End of code
# =============================================================================