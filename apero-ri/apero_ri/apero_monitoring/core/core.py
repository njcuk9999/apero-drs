#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller class for apero checks

Created on 2026-05-15 at 13:36:01

@author: cook
"""

import copy
import getpass
import inspect
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import yaml

from apero_ri.apero_monitoring.core import contacts

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
        self.contact_list = dict()
        # optional declarative helper for simple checks
        self.simple_check = None
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


class SimpleCheck:
    """Declarative runner for simple engineering checks."""

    def __init__(
        self,
        check: AperoCheck,
        test_key: str,
        config_section: str = 'eng_test',
    ):
        self.check = check
        self.test_key = str(test_key or '').strip()
        self.config_section = str(config_section or 'eng_test').strip()
        self.data: Dict[str, Any] = dict()
        self.calc: Dict[str, Callable[..., Any]] = dict()
        self.func: Optional[Callable[..., Any]] = None
        self.pmsg: Any = ''
        self.fmsg: Any = ''
        self.desc: Any = ''
        self.filters: Dict[str, dict] = dict()
        self.check.simple_check = self

    @staticmethod
    def _display_name(names: Any) -> str:
        """Return the primary display name for one config alias set."""
        if isinstance(names, (list, tuple)):
            for name in names:
                text = str(name or '').strip()
                if text != '':
                    return text
            return ''
        return str(names or '').strip()

    @staticmethod
    def _safe_format(text: Any, values: dict) -> str:
        """Format text with placeholder values while preserving misses."""

        class _Missing(dict):
            def __missing__(self, key):
                return '{' + str(key) + '}'

        return str(text or '').format_map(_Missing(values))

    @staticmethod
    def _callable_source(func: Any) -> str:
        """Return a readable source string for one callable when possible."""
        if not callable(func):
            return ''
        try:
            source = str(inspect.getsource(func) or '').strip()
        except Exception:
            return getattr(func, '__name__', str(func))
        if source == '':
            return getattr(func, '__name__', str(func))
        if '=' in source and 'lambda' in source:
            parts = source.split('=', 1)
            source = str(parts[1] or '').strip()
        return source

    @staticmethod
    def _spec_kind(spec: Any) -> str:
        """Return the logical kind for one data specification."""
        if not isinstance(spec, dict):
            return 'const'
        kind = str(spec.get('kind', '') or '').strip().lower()
        if kind != '':
            return kind
        if 'cast' in spec or 'default' in spec:
            return 'config'
        return 'header'

    def _spec_key(self, name: str, spec: Any) -> Any:
        """Return the config-key alias for one data/filter specification."""
        if not isinstance(spec, dict):
            return name
        if 'key' in spec:
            return spec.get('key', name)
        if 'config' in spec:
            return spec.get('config', name)
        return name

    def _spec_summary(self, name: str, spec: Any) -> str:
        """Return a concise human-readable summary for one data spec."""
        kind = self._spec_kind(spec)
        if kind == 'const':
            return f'const = {spec}'
        key_name = self._display_name(self._spec_key(name, spec))
        if kind == 'config':
            cast = str((spec or {}).get('cast', 'raw') or 'raw')
            default = (spec or {}).get('default', None)
            summary = f'config {key_name}'
            summary += f' cast={cast}'
            if 'default' in dict(spec or {}):
                summary += f' default={default}'
            return summary
        dtype = str((spec or {}).get('dtype', 'str') or 'str')
        summary = f'header {key_name} dtype={dtype}'
        logical_key = str((spec or {}).get('logical_key', '') or '').strip()
        if logical_key != '':
            summary += f' logical_key={logical_key}'
        normalize = str((spec or {}).get('normalize', '') or '').strip()
        if normalize != '':
            summary += f' normalize={normalize}'
        return summary

    def _filter_summary(self, name: str, spec: dict) -> str:
        """Return a concise summary for one row-filter specification."""
        logical_key = str(spec.get('logical_key', '') or '').strip()
        key_name = self._display_name(self._spec_key(name, spec))
        dtype = str(spec.get('dtype', 'str') or 'str')
        return (
            f'logical_key={logical_key} values={key_name} dtype={dtype}'
        )

    def _display_cfg(self) -> dict:
        """Build placeholder values for docs and admin views."""
        values = dict()
        values['test_key'] = self.test_key
        values['config_section'] = self.config_section
        values['enabled'] = True

        for name, spec in self.data.items():
            kind = self._spec_kind(spec)
            key_name = self._display_name(self._spec_key(name, spec))
            if kind == 'const':
                values[name] = spec
            elif kind == 'config':
                cast = str((spec or {}).get('cast', 'raw') or 'raw')
                if cast == 'list':
                    values[name] = [key_name]
                else:
                    values[name] = key_name
            else:
                values[name] = key_name

        for name in self.calc:
            values[name] = name

        for name, spec in self.filters.items():
            key_name = self._display_name(self._spec_key(name, spec))
            values[name] = [key_name]

        return values

    def _render_desc(self, values: dict) -> str:
        """Render the logic description text for a values mapping."""
        if callable(self.desc):
            try:
                return str(self.desc(**values) or '').strip()
            except TypeError:
                return str(self.desc(values) or '').strip()
        return self._safe_format(self.desc, values).strip()

    @staticmethod
    def _group_signature(values: dict, logic_markdown: str) -> str:
        """Return a stable signature for one resolved logic payload."""
        payload = dict()
        payload['values'] = dict(values or {})
        payload['logic_markdown'] = str(logic_markdown or '')
        try:
            text = yaml.safe_dump(payload, sort_keys=True)
        except Exception:
            text = str(payload)
        return str(text or '').strip()

    def _logic_label(self, name: str, spec: Any = None) -> str:
        """Return a readable label for one logic row."""
        label = ''
        if spec is not None:
            label = self._display_name(self._spec_key(name, spec))
        if str(label or '').strip() == '':
            label = str(name or '').strip()
        return str(label or '').upper()

    def _logic_rows(self, values: dict) -> List[dict]:
        """Return ordered key/value rows for one logic-values mapping."""
        rows = []
        rows.append(dict(label='TEST_KEY', value=self.test_key))
        rows.append(dict(label='ENABLED', value=values.get('enabled', True)))

        for name, spec in self.data.items():
            rows.append(dict(
                label=self._logic_label(name, spec),
                value=values.get(name, ''),
            ))

        for name in self.calc:
            rows.append(dict(
                label=str(name or '').upper(),
                value=values.get(name, ''),
            ))

        for name, spec in self.filters.items():
            rows.append(dict(
                label=self._logic_label(name, spec),
                value=values.get(name, list()),
            ))
        return rows

    def get_generic_logic_group(self) -> dict:
        """Return one generic logic section using placeholder names."""
        values = self._display_cfg()
        logic_markdown = self.get_logic_markdown(values)
        if logic_markdown == '':
            logic_markdown = self.get_logic_markdown()
        return dict(
            kind='generic',
            title='generic',
            profiles=[],
            values=dict(values),
            rows=self._logic_rows(values),
            logic_markdown=logic_markdown,
        )

    def get_profile_logic_groups(
        self,
        profiles_data: Optional[dict] = None,
    ) -> List[dict]:
        """Return grouped per-profile logic payloads for docs/admin tabs."""
        from apero_ri.apero_monitoring.core import raw_common
        from apero_ri.core.auth import load_apero_profiles

        if profiles_data is None:
            profiles_data = load_apero_profiles(hydrate=True)
        if not isinstance(profiles_data, dict):
            return []

        grouped = dict()
        order = []

        check_instruments_upper = {
            str(i or '').strip().upper()
            for i in list(self.check.instruments or [])
            if str(i or '').strip() != ''
        }

        for instrument in sorted(profiles_data):
            inst_key = str(instrument or '').strip()
            if inst_key == '':
                continue

            inst_profiles = profiles_data.get(instrument, {})
            if not isinstance(inst_profiles, dict):
                continue

            for profile_id, profile_data in inst_profiles.items():
                pid = str(profile_id or '').strip()
                if pid == '' or not isinstance(profile_data, dict):
                    continue

                # Use the per-profile instrument name (e.g. 'NIRPS_HA')
                # rather than the top-level group key (e.g. 'NIRPS').
                gen = profile_data.get('general', {}) or {}
                profile_instrument = str(
                    gen.get('instrument', '')
                    or gen.get('INSTRUMENT', '')
                    or inst_key
                ).strip().upper()
                if profile_instrument not in check_instruments_upper:
                    continue

                yaml_name = pid
                if not yaml_name.endswith('.yaml'):
                    yaml_name = yaml_name + '.yaml'
                label = 'aprofile_instrument/' + yaml_name
                cfg = raw_common.get_check_value(
                    profile_data,
                    self.config_section,
                    ['tests', self.test_key],
                    dict(),
                )
                if not isinstance(cfg, dict):
                    cfg = dict()

                values = self._display_cfg()
                values['enabled'] = raw_common.to_bool(
                    cfg.get('enabled', True),
                    default=True,
                )
                values.update(
                    self._runtime_logic_values(cfg, profile_data)
                )

                logic_markdown = self.get_logic_markdown(values)
                if logic_markdown == '':
                    logic_markdown = self.get_logic_markdown()

                signature = self._group_signature(values, logic_markdown)
                if signature not in grouped:
                    grouped[signature] = dict(
                        kind='profile_group',
                        title='',
                        profiles=[],
                        values=dict(values),
                        rows=self._logic_rows(values),
                        logic_markdown=logic_markdown,
                    )
                    order.append(signature)
                grouped[signature]['profiles'].append(label)

        out = []
        for signature in order:
            item = dict(grouped.get(signature, {}))
            profiles = list(item.get('profiles', []) or [])
            item['title'] = ', '.join(profiles)
            out.append(item)
        return out

    def get_logic_tab_groups(
        self,
        profiles_data: Optional[dict] = None,
    ) -> List[dict]:
        """Return generic + grouped per-profile logic tabs."""
        out = [self.get_generic_logic_group()]
        out.extend(self.get_profile_logic_groups(profiles_data=profiles_data))
        return out

    def get_logic_markdown(self, values: Optional[dict] = None) -> str:
        """Return markdown describing this SimpleCheck logic."""
        logic = self._render_desc(values or self._display_cfg())
        if logic == '' and callable(self.func):
            logic = self._callable_source(self.func)
        if logic == '':
            return ''
        if '```' in logic:
            return logic
        out = 'Performs the following test\n\n'
        out += '```python\n'
        out += logic + '\n'
        out += '```'
        return out

    def get_admin_sections(self) -> List[dict]:
        """Return structured parameter sections for admin views."""
        sections = []

        rows = []
        rows.append(dict(label='TEST_KEY', value=self.test_key))
        rows.append(dict(label='CONFIG_SECTION', value=self.config_section))
        sections.append(dict(title='SimpleCheck Core', rows=rows))

        if len(self.data) > 0:
            rows = []
            for name, spec in self.data.items():
                rows.append(dict(
                    label=str(name or '').upper(),
                    value=self._spec_summary(name, spec),
                ))
            sections.append(dict(title='Data', rows=rows))

        if len(self.filters) > 0:
            rows = []
            for name, spec in self.filters.items():
                rows.append(dict(
                    label=str(name or '').upper(),
                    value=self._filter_summary(name, spec),
                ))
            sections.append(dict(title='Filters', rows=rows))

        if len(self.calc) > 0:
            rows = []
            for name, func in self.calc.items():
                rows.append(dict(
                    label=str(name or '').upper(),
                    value=self._callable_source(func),
                ))
            sections.append(dict(title='Calculated', rows=rows))

        rows = []
        if callable(self.func):
            rows.append(dict(
                label='FUNC',
                value=self._callable_source(self.func),
            ))
        if str(self.pmsg or '').strip() != '':
            rows.append(dict(label='PASS_MESSAGE', value=self.pmsg))
        if str(self.fmsg or '').strip() != '':
            rows.append(dict(label='FAIL_MESSAGE', value=self.fmsg))
        if str(self.desc or '').strip() != '':
            rows.append(dict(label='DESC', value=self.desc))
        if len(rows) > 0:
            sections.append(dict(title='Logic', rows=rows))

        return sections

    def run(
        self,
        instrument: str,
        obs_dir: str,
        aparams: dict,
        dbparams: dict,
    ) -> Tuple[bool, str]:
        """Execute this simple check against one observation night."""
        from apero_ri.apero_monitoring.core import raw_common

        _ = instrument, dbparams
        cfg = raw_common.get_check_value(
            aparams,
            self.config_section,
            ['tests', self.test_key],
            dict(),
        )
        if not isinstance(cfg, dict) or len(cfg) == 0:
            return True, f'Skipped {self.test_key}: not configured.'
        logic_values = self._display_cfg()
        runtime_logic = self._runtime_logic_values(cfg, aparams)
        logic_values.update(runtime_logic)
        self.check.description = self.get_logic_markdown(logic_values)
        if not raw_common.to_bool(cfg.get('enabled', True), default=True):
            return True, f'Skipped {self.test_key}: disabled.'

        runtime = self._build_runtime(cfg, aparams)
        error = str(runtime.get('error', '') or '').strip()
        if error != '':
            return False, error
        skip = str(runtime.get('skip', '') or '').strip()
        if skip != '':
            return True, skip

        obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
        if len(files) == 0:
            return False, f'No FITS files found in {obs_dir}.'

        table, masks = raw_common.load_header_table(files, runtime['defs'])
        use = self._build_use_mask(table, masks, runtime)
        if np.sum(use) == 0:
            return True, f'Skipped {self.test_key}: no valid rows.'

        variables = self._build_variables(table, use, runtime)
        ok, reason, pass_message, fail_mask = self._evaluate(
            table,
            use,
            variables,
        )
        if ok:
            return True, pass_message

        fail_files = raw_common.files_from_mask(table, fail_mask)
        message = raw_common.format_failed_file_message(
            self.test_key,
            reason,
            obs_path,
            fail_files,
        )
        return False, message

    def _cfg_value(
        self,
        cfg: dict,
        names: Any,
        default: Any = None,
    ) -> Any:
        """Return the first present config value from one or more names."""
        if isinstance(names, (list, tuple)):
            for name in names:
                key = str(name or '').strip()
                if key != '' and key in cfg:
                    value = cfg.get(key)
                    if value is not None:
                        return value
            return default
        key = str(names or '').strip()
        if key == '':
            return default
        value = cfg.get(key, default)
        return default if value is None else value

    def _runtime_logic_values(self, cfg: dict, aparams: dict) -> dict:
        """Return display values resolved from config for logic text."""
        from apero_ri.apero_monitoring.core import raw_common

        values = dict()
        values['test_key'] = self.test_key
        for name, spec in self.data.items():
            kind = self._spec_kind(spec)
            if kind == 'const':
                values[name] = spec
                continue
            if kind == 'config':
                raw_value = self._cfg_value(
                    cfg,
                    self._spec_key(name, spec),
                    dict(spec or {}).get('default', None),
                )
                values[name] = raw_value
                continue
            logical_key = str((spec or {}).get('logical_key', '') or '').strip()
            if logical_key != '':
                values[name] = raw_common.get_header_key(aparams, logical_key)
            else:
                values[name] = self._cfg_value(
                    cfg,
                    self._spec_key(name, spec),
                    '',
                )
        for name in self.calc:
            values[name] = name
        for name, spec in self.filters.items():
            default = dict(spec or {}).get('default', list())
            values[name] = self._cfg_value(
                cfg,
                self._spec_key(name, spec),
                default,
            )
        return values

    def _cast_value(
        self,
        value: Any,
        cast: str,
        default: Any,
    ) -> Any:
        """Cast one config value to the requested type."""
        cast_name = str(cast or 'raw').strip().lower()
        if cast_name == 'bool':
            from apero_ri.apero_monitoring.core import raw_common
            return raw_common.to_bool(value, default=bool(default))
        if cast_name == 'float':
            try:
                return float(value)
            except Exception:
                return default
        if cast_name == 'list':
            if isinstance(value, list):
                return list(value)
            return default
        if cast_name == 'str':
            if value is None:
                return default
            return str(value)
        return value if value is not None else default

    def _build_runtime(self, cfg: dict, aparams: dict) -> dict:
        """Resolve config-backed runtime values for one check."""
        from apero_ri.apero_monitoring.core import raw_common

        runtime = dict()
        runtime['defs'] = dict()
        runtime['header_data'] = dict()
        runtime['fixed_data'] = dict()
        runtime['filters'] = dict()

        for name, spec in self.data.items():
            kind = self._spec_kind(spec)
            if kind == 'const':
                runtime['fixed_data'][name] = spec
                continue
            if kind == 'config':
                default = dict(spec or {}).get('default', None)
                cast = str((spec or {}).get('cast', 'raw') or 'raw')
                raw_value = self._cfg_value(
                    cfg,
                    self._spec_key(name, spec),
                    default,
                )
                runtime['fixed_data'][name] = self._cast_value(
                    raw_value,
                    cast,
                    default,
                )
                continue
            logical_key = str((spec or {}).get('logical_key', '') or '').strip()
            if logical_key != '':
                header_key = raw_common.get_header_key(aparams, logical_key)
                config_name = logical_key
            else:
                config_name = self._spec_key(name, spec)
                header_key = str(
                    self._cfg_value(cfg, config_name, '') or ''
                ).strip()
            if header_key == '':
                runtime['error'] = (
                    f'{self.test_key} missing '
                    f'{self._first_name(config_name)}.'
                )
                return runtime
            runtime['defs'][name] = dict(
                key=header_key,
                dtype=str((spec or {}).get('dtype', 'str') or 'str'),
            )
            runtime['header_data'][name] = dict(spec or {})

        for name, spec in self.filters.items():
            logical_key = str(spec.get('logical_key', '') or '').strip()
            header_key = raw_common.get_header_key(aparams, logical_key)
            if header_key == '':
                runtime['error'] = (
                    f'{self.test_key} requires {logical_key} header key.'
                )
                return runtime
            default = dict(spec or {}).get('default', list())
            values = self._cfg_value(
                cfg,
                self._spec_key(name, spec),
                default,
            )
            if not isinstance(values, list) or len(values) == 0:
                runtime['skip'] = (
                    f'Skipped {self.test_key}: '
                    f'no {self._first_name(self._spec_key(name, spec))} '
                    'configured.'
                )
                return runtime
            runtime['defs'][name] = dict(
                key=header_key,
                dtype=str(spec.get('dtype', 'str') or 'str'),
            )
            runtime['filters'][name] = dict(
                spec=dict(spec),
                values=list(values),
            )
        return runtime

    @staticmethod
    def _first_name(names: Any) -> str:
        """Return the first config name from a string/list definition."""
        if isinstance(names, (list, tuple)) and len(names) > 0:
            return str(names[0] or '').strip()
        return str(names or '').strip()

    def _build_use_mask(self, table: dict, masks: dict, runtime: dict):
        """Return the combined row mask for fields and configured filters."""
        use = np.ones(len(table.get('filename', [])), dtype=bool)
        for name in runtime['header_data']:
            use &= np.array(masks[name]).astype(bool)
        for name, item in runtime['filters'].items():
            use &= np.array(masks[name]).astype(bool)
            values = np.array(table[name]).astype(str)
            use &= np.isin(values, item['values'])
        return use

    def _normalize_series(self, raw_values: Any, spec: dict) -> np.ndarray:
        """Convert one loaded header column to the requested runtime form."""
        values = np.array(raw_values)
        normalize = str(spec.get('normalize', '') or '').strip()
        if normalize == 'float':
            return np.array(values, dtype=float)
        if normalize == 'bool':
            return np.array(values, dtype=bool)
        if normalize == 'strip':
            return np.char.strip(np.array(values).astype(str))
        if normalize == 'upper_strip':
            text = np.array(values).astype(str)
            return np.char.upper(np.char.strip(text))
        return values

    def _build_variables(
        self,
        table: dict,
        use: np.ndarray,
        runtime: dict,
    ) -> dict:
        """Build the runtime variable mapping from loaded table data."""
        variables = dict(runtime['fixed_data'])
        variables['test_key'] = self.test_key

        for name, spec in runtime['header_data'].items():
            series = self._normalize_series(table[name], spec)
            variables[name] = series[use]

        for name, func in self.calc.items():
            variables[name] = func(**variables)

        return variables

    def _render_message(self, template: Any, values: dict) -> str:
        """Render one pass/fail message from a template or callable."""
        if callable(template):
            try:
                return str(template(**values) or '').strip()
            except TypeError:
                return str(template(values) or '').strip()
        return self._safe_format(template, values).strip()

    def _evaluate(
        self,
        table: dict,
        use: np.ndarray,
        variables: dict,
    ) -> Tuple[bool, str, str, np.ndarray]:
        """Evaluate this declarative SimpleCheck instance."""
        if not callable(self.func):
            raise ValueError(
                f'SimpleCheck {self.test_key} has no func defined.'
            )

        logic = self.func(**variables)
        if isinstance(logic, (bool, np.bool_)):
            ok = bool(logic)
            reason = self._render_message(self.fmsg, variables)
            message = self._render_message(self.pmsg, variables)
            return ok, reason, message, use.copy()

        logic_array = np.array(logic, dtype=bool)
        ok = bool(np.all(logic_array))
        reason = self._render_message(self.fmsg, variables)
        message = self._render_message(self.pmsg, variables)
        fail_mask = np.zeros(len(table.get('filename', [])), dtype=bool)
        fail_mask[use] = ~logic_array
        return ok, reason, message, fail_mask
        
        

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
    payload['passes'] = dict()
    payload['failures'] = dict()
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
                      history_entry: Optional[dict] = None) -> Path:
    """Write one APERO-check YAML file atomically."""
    # Create the root directory before writing the file.
    root_dir = Path(root_dir)
    root_dir.mkdir(parents=True, exist_ok=True)
    # Append a history entry when one is supplied for this run.
    if history_entry is not None:
        payload['history'] = append_history_entry(payload, history_entry)
    # Build the final output path for this obsdir.
    filename = make_obsdir_filename(root_dir, obs_dir)
    # Write to a temporary file first so updates stay atomic.
    tmpname = filename.with_suffix(filename.suffix + '.tmp')
    with open(tmpname, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(payload, handle, sort_keys=False,
                       allow_unicode=False)
    # Promote the temporary file to the final YAML path.
    tmpname.replace(filename)
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
