#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free tests for setup replay scripts."""

import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

import pytest

from apero.dev import get_base_params
from apero.setup.bin import apero_setup
from apero.setup.core import drs_setup
from apero.setup.core import setup_constants


def _setup_params(tmp_path: Path) -> drs_setup.ParamDict:
    """Build deterministic setup choices without accessing a profile.

    :param tmp_path: Temporary directory for all configured paths.
    :return: Complete setup parameters with non-default replay choices.
    """
    get_base_params('SPIROU')
    params = drs_setup.ParamDict()
    for key, arg in setup_constants.SARGS.items():
        params[key] = arg.default_value
        if arg.dtype == 'path':
            params[key] = str(tmp_path / key)
            Path(params[key]).mkdir()
    params['NAME'] = 'test_profile'
    params['CONFIG_PATH'] = tmp_path / 'test_profile'
    params['CONFIG_PATH'].mkdir()
    params['INSTRUMENT'] = 'SPIROU'
    params['DATADIR'] = str(tmp_path / 'umbrella')
    params['EDIT_DBTABLES'] = True
    params['CALIB_DBTABLE'] = 'custom_calib'
    params['CLEAN_START'] = False
    params['CLEAN_PROMPT'] = False
    params['DATABASE_PASS'] = 'test quote \' " $HOME; $(echo nope)'
    params['EXTERNAL_RAW'] = str(tmp_path / 'external raw')
    Path(params['EXTERNAL_RAW']).mkdir()
    params['USE_EXTERNAL_RAW'] = True
    params['EXTERNAL_RAW_TYPE'] = 'hardlink'
    for key, arg in setup_constants.SARGS.items():
        if arg.apero_name is not None:
            params[arg.apero_name] = params[key]
    return params


def test_install_script_replays_choices_from_any_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Execute the generated shell command and round-trip its setup options."""
    params = _setup_params(tmp_path)
    params['UPDATE'] = True
    params['INSTALL_SH'] = True
    original = dict(params)
    original_sources = dict(params.sources)
    # Replace only the target setup program, not the generated shell command.
    source = tmp_path / 'source with spaces'
    setup_script = source / 'setup' / 'bin' / 'apero_setup.py'
    setup_script.parent.mkdir(parents=True)
    setup_script.write_text('import json, sys\n'
                            'print(json.dumps(sys.argv[1:]))\n')
    monkeypatch.setattr(drs_setup, '__PATH__', source)
    drs_setup.create_install_script(params, setup_constants.SARGS)
    script = params['CONFIG_PATH'] / 'install_script.sh'
    assert script.stat().st_mode & 0o777 == 0o700
    assert dict(params) == original
    assert dict(params.sources) == original_sources
    assert not (tmp_path / 'install_script.sh').exists()

    result = subprocess.run([str(script)], cwd=tmp_path, check=True,
                            capture_output=True, text=True)
    options = json.loads(result.stdout)
    monkeypatch.setattr(sys, 'argv', ['apero_setup.py', *options])
    replay = drs_setup.command_line_args(setup_constants.SARGS)
    assert replay['CONFIG_PATH'] == params['CONFIG_PATH']
    assert replay['DATABASE_PASS'] == params['DATABASE_PASS']
    assert replay['CLEAN_START'] is False
    assert replay['FORCE_DIR_CREATE'] is False
    assert replay['CALIB_DBTABLE'] == 'custom_calib'
    assert replay['RAWDIR'] == params['RAWDIR']
    assert replay['UPDATE'] is False
    assert replay['INSTALL_SH'] is False

    def unexpected_prompt(*values: Any, **options: Any) -> None:
        """Fail if replay tries to ask for a recorded setup choice."""
        pytest.fail('Replay unexpectedly requested input')

    monkeypatch.setattr(drs_setup, 'user_input', unexpected_prompt)
    drs_setup.ask_user(replay, setup_constants.SARGS)
    # Appended CLI arguments can override the recorded choices.
    result = subprocess.run([str(script), '--clean=True'], cwd=tmp_path,
                            check=True, capture_output=True, text=True)
    options = json.loads(result.stdout)
    monkeypatch.setattr(sys, 'argv', ['apero_setup.py', *options])
    replay = drs_setup.command_line_args(setup_constants.SARGS)
    assert replay['CLEAN_START'] is True


@pytest.mark.parametrize('explicit_profile', [False, True])
def test_install_sh_only_regenerates_current_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    explicit_profile: bool,
) -> None:
    """Recover persisted choices without entering any installation phase."""
    params = _setup_params(tmp_path)
    config_path = params['CONFIG_PATH']
    drs_setup.create_yamls(params)
    drs_setup.create_user_configs(params, setup_constants.SARGS)
    yaml_before = {
        path.name: path.read_bytes() for path in config_path.glob('*.yaml')
    }

    def unexpected_install(*values: Any, **options: Any) -> None:
        """Fail if script-only mode runs installation or asks questions."""
        pytest.fail('Script-only mode entered installation')

    monkeypatch.setattr(drs_setup, 'run_setup', unexpected_install)
    monkeypatch.setattr(drs_setup, 'ask_user', unexpected_install)
    monkeypatch.setattr(apero_setup.drs_demo, 'start_from_demo',
                        unexpected_install)
    argv = ['apero_setup.py', '--install_sh']
    if explicit_profile:
        monkeypatch.setenv(drs_setup.base.USER_ENV, str(tmp_path / 'other'))
        argv += ['--name=test_profile', f'--config={tmp_path}']
    else:
        monkeypatch.setenv(drs_setup.base.USER_ENV, str(config_path))
    monkeypatch.setattr(sys, 'argv', argv)
    # Overwriting an existing script must also restore owner-only permissions.
    script = config_path / 'install_script.sh'
    script.write_text('old script')
    script.chmod(0o755)
    result = apero_setup.main()
    tokens = shlex.split(script.read_text().replace('\\\n', ''))
    assert '--name=test_profile' in tokens
    assert '--instrument=SPIROU' in tokens
    assert f'--config={config_path}' in tokens
    assert '--calibtable=custom_calib' in tokens
    assert f"--RAWDIR={params['RAWDIR']}" in tokens
    assert '--external-raw-type=hardlink' in tokens
    assert '--use-external-raw=True' in tokens
    assert '--clean=False' in tokens
    assert '--clean-prompt=False' in tokens
    assert '--install_sh=True' not in tokens
    assert result['CONFIG_PATH'] == config_path
    assert script.stat().st_mode & 0o777 == 0o700
    assert yaml_before == {
        path.name: path.read_bytes() for path in config_path.glob('*.yaml')
    }
    assert not (tmp_path / 'other').exists()


def test_install_sh_without_profile_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Require a profile instead of prompting or creating a new config."""
    monkeypatch.delenv(drs_setup.base.USER_ENV, raising=False)
    monkeypatch.setattr(sys, 'argv', ['apero_setup.py', '--install_sh'])
    params = drs_setup.command_line_args(setup_constants.SARGS)
    assert params['INSTALL_SH'] is True
    with pytest.raises(drs_setup.AperoCodedException):
        drs_setup.update_setup(params, setup_constants.SARGS)
