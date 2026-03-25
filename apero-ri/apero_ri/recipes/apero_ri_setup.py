#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup the APERO reduction interface
"""

import argparse
import os
import webbrowser
from pathlib import Path

from apero_ri.core import auth
from apero_ri.core import user_data as ud
from apero_ri.setup.bootstrap import ensure_directory_layout
from apero_ri.setup.bootstrap import is_setup_complete
from apero_ri.setup.bootstrap import resolve_local_data_dir
from apero_ri.setup.bootstrap import save_bootstrap_config
from apero_ri.setup.setup_app import create_setup_app


# =============================================================================
# Define variables
# =============================================================================



# =============================================================================
# Define functions
# =============================================================================
def _get_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the setup wizard."""
    parser = argparse.ArgumentParser(description='APERO RI first-run setup')
    parser.add_argument(
        '--data-dir', type=str,
        help='Local data directory to initialize (default: ~/.ari or bootstrap config)',
    )
    parser.add_argument(
        '--host', type=str, default='127.0.0.1',
        help='Host binding for the temporary setup app (default: 127.0.0.1)',
    )
    parser.add_argument(
        '--port', type=int, default=6670,
        help='Port for the temporary setup app (default: 6670)',
    )
    parser.add_argument(
        '--no-browser', action='store_true',
        help='Do not try to open the setup URL in a browser automatically',
    )
    parser.add_argument(
        '--force', action='store_true',
        help='Run setup even if setup_state.yaml already marks the install complete',
    )
    return parser.parse_args()


def _prompt_for_data_dir(default_dir: Path) -> Path:
    """Prompt for the local data directory unless already supplied."""
    prompt = f'Local APERO RI data directory [{default_dir}]: '
    try:
        entered = input(prompt).strip()
    except EOFError:
        return default_dir
    if not entered:
        return default_dir
    return Path(entered).expanduser()


def main():
    """Entry point for apero_ri_setup."""
    args = _get_arguments()
    default_dir = resolve_local_data_dir(args.data_dir)
    local_data_dir = Path(args.data_dir).expanduser() if args.data_dir else _prompt_for_data_dir(default_dir)

    ensure_directory_layout(local_data_dir)
    save_bootstrap_config(str(local_data_dir))
    os.environ['ARI_DIR'] = str(local_data_dir)
    ud.set_ari_dir(str(local_data_dir))
    auth.set_ari_dir(str(local_data_dir))

    if is_setup_complete(local_data_dir) and not args.force:
        print(f'Setup already completed for {local_data_dir}.')
        print('Run `apero_ri_run` to start the application, or re-run with --force.')
        return

    app = create_setup_app(local_data_dir)
    setup_url = f'http://{args.host}:{args.port}/'
    print('APERO RI setup initialized.')
    print(f'Local data directory: {local_data_dir}')
    print(f'Open {setup_url} to continue setup.')
    if not args.no_browser:
        try:
            webbrowser.open(setup_url)
        except Exception:
            pass
    app.run(host=args.host, port=args.port)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    main()

# =============================================================================
# End of code
# =============================================================================
