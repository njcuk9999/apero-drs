#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller class for apero checks

Created on 2026-05-15 at 13:36:01

@author: cook
"""

import copy
import getpass
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from apero_checks.core import contacts

# =============================================================================
# Define variables
# =============================================================================
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# =============================================================================
# Define classes
# =============================================================================
class AperoCheck:
    """Class to represent an APERO check."""

    def __init__(self, name: str, string_name: str,
                 check_type: str, instruments: List[str]):
        # the name of this test which should be used in the check_dict
        self.name = name
        # the string name of this test (for internal use)
        self.string_name = string_name
        # the type of check (e.g. 'raw', 'red')
        self.check_type = check_type
        # this instruments this test is valid for
        self.instruments = instruments
        # the message to display for this check
        self.message = ''
        # whether this test is skipped (due to wrong instrument)
        self.wrong_instrument = False
        # whether this test passed or failed
        self.passed = False
        # dependencies for this check (e.g. other checks that must pass 
        # before this one can be run)
        self.dependencies = []
        # define the description for the check (for documentation)
        self.description = ''
        # define the what to do text for this check
        self.what_to_do = ''
        # define contact information for this check
        self.contactlist = contacts.AperoCheckContactList()
        # function to run for this check
        # must return a tuple of (passed: bool, message: str)
        self.func = no_function

    def clone(self):
        """Return a per-run copy of this check instance."""
        # Copy the instance so runtime state is not shared between runs.
        return copy.deepcopy(self)
        
    def __call__(self, instrument, obs_dir: str, aparams: dict,
                 dbparams: dict, check_dict: Dict[str, bool]):
        """Run the check."""
        # Reset runtime state before every execution.
        self.message = ''
        self.wrong_instrument = False
        self.passed = False
        # ---------------------------------------------------------------------
        # deal with check not in instrument
        if instrument not in self.instruments:
            self.wrong_instrument = True
            self.message = f"Check not valid for instrument {instrument}"
            return
        # ---------------------------------------------------------------------
        # deal with dependencies
        # if a dependency is False (or not present) we fail this check
        if len(self.dependencies) > 0:
            for dep in self.dependencies:
                if dep not in check_dict or not check_dict[dep]:
                    self.message = (
                        f'Check failed due to failed dependency: {dep}'
                    )
                    return
        # ---------------------------------------------------------------------
        # run the check function
        if self.func is not None:
            self.passed, self.message = self.func(
                instrument=instrument,
                obs_dir=obs_dir,
                aparams=aparams,
                dbparams=dbparams,
            )
        else:
            self.message = "No function defined for this check"
    
    def create_yaml_entry(self):
        """Create the YAML bucket name and entry for this check."""
        # Skip checks that are not valid for this instrument.
        if self.wrong_instrument:
            return None
        # Create the ordered entry used in the output YAML file.
        entry = dict()
        entry['name'] = str(self.string_name)
        entry['type'] = str(self.check_type)
        # Only persist messages when they are non-empty.
        if str(self.message or '').strip():
            entry['message'] = str(self.message)
        # Route the entry to the correct YAML section.
        bucket = 'passes' if self.passed else 'failures'
        # Return the bucket, key, and payload for the writer.
        return bucket, str(self.name), entry
        
    def report(self):
        """Create a report for this check."""
        status = "PASSED" if self.passed else "FAILED"
        if self.wrong_instrument:
            status = "SKIPPED (wrong instrument)"
        return f"{self.string_name}: {status} - {self.message}"
        
        

def no_function(instrument: str, obs_dir: str,
                aparams: dict, dbparams: dict) -> (bool, str):
    """Default function for checks that have no function defined."""
    
    _ = instrument, obs_dir, aparams, dbparams
    
    return False, "No function defined for this check"


def get_runtime_user() -> str:
    """Return a platform-independent username for check history."""
    # Fall back to a safe placeholder if the OS user cannot be resolved.
    return str(getpass.getuser() or 'unknown')


def get_runtime_source() -> str:
    """Return a platform-independent host name for check history."""
    # Fall back to a safe placeholder if the host name cannot be resolved.
    return str(socket.gethostname() or 'unknown')


def now_str() -> str:
    """Return the current UTC time in the APERO-check YAML format."""
    # Use a stable UTC timestamp without timezone text to match samples.
    return datetime.now(timezone.utc).strftime(TIME_FORMAT)


def format_time_string(value: Any) -> str:
    """Normalise a time-like value to the YAML storage format."""
    # Return an empty string for null-like values.
    if value in [None, 'None', '']:
        return ''
    # Convert non-strings to strings before parsing.
    text = str(value).strip()
    # Return early for empty text.
    if text == '':
        return ''
    # Try a small set of common timestamp parsers.
    for parser in (_parse_iso_datetime, _parse_plain_datetime):
        dtime = parser(text)
        if dtime is not None:
            return dtime.strftime(TIME_FORMAT)
    # If parsing fails keep the original text.
    return text


def load_yaml_file(filename: Path) -> dict:
    """Load an existing APERO-check YAML file if it exists."""
    # Return an empty payload when the file does not exist.
    if not filename.exists() or not filename.is_file():
        return dict()
    # Read the YAML file with safe loading.
    with open(filename, 'r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle) or dict()
    # Only dict payloads are supported by the monitor portal.
    if isinstance(data, dict):
        return data
    return dict()


def resolve_output_root(local_data_dir: str, aparams: dict) -> Path:
    """Resolve the output root from LOCAL_DATA_DIR and profile paths."""
    # Import lazily to avoid a module cycle at import time.
    from apero_ri.core import apero_checks as checks_core

    # Resolve the checks root using the same helper as the monitor portal.
    return checks_core.resolve_checks_root(Path(local_data_dir), aparams)


def make_obsdir_filename(root_dir: Path, obs_dir: str) -> Path:
    """Return the canonical YAML filename for one obsdir."""
    # Name files only by obsdir so monitor lookups stay simple.
    return Path(root_dir) / f'{obs_dir}.yaml'


def build_history_entry(user: Optional[str] = None,
                        source: Optional[str] = None,
                        date_str: Optional[str] = None) -> dict:
    """Create one history entry for a check run."""
    # Build the ordered event mapping used in the YAML output.
    entry = dict()
    entry['date'] = str(date_str or now_str())
    entry['user'] = str(user or get_runtime_user())
    entry['source'] = str(source or get_runtime_source())
    return entry


def append_history_entry(data: dict, history_entry: dict) -> dict:
    """Append a history entry and return the updated history mapping."""
    # Copy the existing history so callers do not mutate shared state.
    history = dict(data.get('history', {}) or {})
    # Work out the next zero-padded entry number.
    next_index = len(history) + 1
    next_key = f'entry{next_index:05d}'
    # Append the new history entry.
    history[next_key] = dict(history_entry)
    return history


def build_obsdir_payload(obs_dir: str,
                         instrument: str,
                         profile: str,
                         first_file: Any,
                         last_file: Any,
                         existing_data: Optional[dict] = None) -> dict:
    """Create the base YAML payload for one obsdir."""
    # Start from any existing data so history can be preserved.
    current = dict(existing_data or {})
    # Build the ordered payload expected by the monitor portal.
    payload = dict()
    payload['obsdir'] = str(obs_dir)
    payload['first file'] = format_time_string(first_file)
    payload['last file'] = format_time_string(last_file)
    payload['instrument'] = str(instrument)
    payload['profile'] = str(profile)
    payload['history'] = dict(current.get('history', {}) or {})
    payload['passes'] = dict(current.get('passes', {}) or {})
    payload['failures'] = dict(current.get('failures', {}) or {})
    return payload


def add_check_entry(payload: dict,
                    check_entry: Optional[Tuple[str, str, dict]],
                    existing_data: Optional[dict] = None) -> None:
    """Add one check entry to the in-memory YAML payload."""
    # Ignore empty or skipped check entries.
    if check_entry is None:
        return
    # Unpack the bucket name, check key, and YAML entry.
    bucket, check_name, entry = check_entry
    # Remove stale copies from both buckets before re-adding.
    payload['passes'].pop(check_name, None)
    payload['failures'].pop(check_name, None)
    # Copy the entry so later callers cannot mutate stored data.
    value = dict(entry)
    # Preserve override/monitor annotations for persistent failures.
    if bucket == 'failures' and isinstance(existing_data, dict):
        previous = dict(existing_data.get('failures', {}) or {})
        if check_name in previous and isinstance(previous[check_name], dict):
            if 'override' in previous[check_name]:
                value['override'] = dict(previous[check_name]['override'])
            if 'monitor' in previous[check_name]:
                value['monitor'] = dict(previous[check_name]['monitor'])
    # Store the entry in the target bucket.
    payload[bucket][check_name] = value


def write_obsdir_yaml(root_dir: Path,
                      obs_dir: str,
                      payload: dict,
                      history_entry: Optional[dict] = None,
                      profile_id: Optional[str] = None) -> Path:
    """Write one APERO-check YAML file atomically.

    :param root_dir: Root directory for check YAML files.
    :param obs_dir: Observation directory identifier (becomes filename stem).
    :param payload: Check payload dict to serialise.
    :param history_entry: Optional history record to append before writing.
    :param profile_id: When supplied, the checks index is updated for this
                       profile after the write so the next policy scan can
                       skip the re-read.
    """
    # Create the root directory before writing the file.
    root_dir = Path(root_dir)
    root_dir.mkdir(parents=True, exist_ok=True)
    # Append a history entry when one is supplied for this run.
    if history_entry is not None:
        payload['history'] = append_history_entry(payload, history_entry)
    # Build the final output path for this obsdir.
    filename = make_obsdir_filename(root_dir, obs_dir)
    # Ensure nested obsdir paths can be written safely.
    filename.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temporary file first so updates stay atomic.
    tmpname = filename.with_suffix(filename.suffix + '.tmp')
    with open(tmpname, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(payload, handle, sort_keys=False,
                       allow_unicode=False)
    # Promote the temporary file to the final YAML path.
    tmpname.replace(filename)
    # Update the checks index so the next policy scan skips this file.
    if profile_id:
        try:
            from apero_ri.core import checks_index as _ci
            from apero_ri.core import apero_checks as _ac
            from apero_ri.apero_monitoring.checks import CHECKS as _MC
            loaded = _ac.load_check_file(filename)
            _ac.propagate_dependency_states(loaded, _MC)
            _ci.update_obsdir(str(profile_id), str(obs_dir), filename, loaded)
        except Exception:
            pass  # index update is best-effort
    return filename


def _parse_iso_datetime(text: str) -> Optional[datetime]:
    """Parse an ISO-like datetime string."""
    # Normalise a trailing Z to an explicit UTC offset.
    value = text.replace('Z', '+00:00')
    try:
        dtime = datetime.fromisoformat(value)
    except ValueError:
        return None
    # Convert timezone-aware values to UTC before formatting.
    if dtime.tzinfo is not None:
        dtime = dtime.astimezone(timezone.utc).replace(tzinfo=None)
    return dtime


def _parse_plain_datetime(text: str) -> Optional[datetime]:
    """Parse a plain APERO-check datetime string."""
    try:
        return datetime.strptime(text, TIME_FORMAT)
    except ValueError:
        return None


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print('Hello World!')


# =============================================================================
# End of code
# =============================================================================
