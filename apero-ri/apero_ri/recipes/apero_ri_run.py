#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the APERO reduction interface
"""

import argparse
import os
import sys

from apero_ri.setup.bootstrap import can_start_main_app, resolve_local_data_dir

# =============================================================================
# Define variables
# =============================================================================


# =============================================================================
# Define functions
# =============================================================================
def _get_arguments() -> argparse.Namespace:
    """Parse enough arguments to resolve the data directory before startup."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data-dir", type=str)
    args, _ = parser.parse_known_args()
    return args


def main():
    """Entry point for apero_ri_run."""
    args = _get_arguments()
    data_dir = resolve_local_data_dir(args.data_dir)
    os.environ["ARI_DIR"] = str(data_dir)
    if not can_start_main_app(data_dir):
        print(
            "APERO RI setup has not been completed for this installation.",
            file=sys.stderr,
        )
        print(f"Local data directory: {data_dir}", file=sys.stderr)
        print(
            "Run `apero_ri_setup` first, then start the app again.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    from apero_ri.application import application

    app = application.ARIApp()
    # Ctrl+C is handled inside app.run() via a SIGINT handler that arms a
    # 5-second watchdog.  If the server exits cleanly, shutdown() runs in
    # the finally block of run().  If block_on_close hangs, the watchdog
    # calls os._exit(130) so the port is always released.
    app.run()


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
