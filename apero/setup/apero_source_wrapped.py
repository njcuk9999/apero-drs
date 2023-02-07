import argparse
import os
from typing import List

from apero.base import base, drs_base
from apero.tools.module.setup import drs_installation as install

# from apero.setup import setup_lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_source.py"
__INSTRUMENT__ = "None"
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
DRS_PATH = "apero"
# start the language dictionary
lang = drs_base.lang_db_proxy()


def get_args(available_profiles: List[str]) -> argparse.Namespace:
    """
    Define the command line arguments (via argparse) for this recipe
    :return:
    """
    # get parser
    description = lang["SOURCE_DESCRIPTION"]
    parser = argparse.ArgumentParser(description=description.format(DRS_PATH))
    # add arguments
    parser.add_argument(
        "name",
        action="store",
        help=lang["SOURCE_NAME_HELP"],
        choices=available_profiles,
    )
    parser.add_argument(
        "--shell", action="store", dest="shell", help=lang["SOURCE_SHELL_HELP"]
    )
    # parse arguments
    args = parser.parse_args()
    return args


def get_current_shell():

    if os.name == "nt":
        shell = "win"
    else:
        shell = os.path.split(os.environ.get("SHELL", "bash"))[-1]

    return shell


def main():

    profiles = install.read_home_profiles()
    available_profiles_name = list(profiles.keys())

    args = get_args(available_profiles_name)

    # TODO: Discuss this alternative name handling in PR
    # if args.name is None:
    #     print(
    #         "Please pass one of the following profiles as argument: "
    #         f"{list(profiles.keys())}"
    #     )
    #     return

    profile_config_dir = profiles[args.name]

    if args.shell in ["None", None, ""]:
        shell = get_current_shell()
    else:
        shell = args.shell

    source_file_name = f"{args.name}.{shell}.setup"
    profile_config_file = os.path.join(profile_config_dir, source_file_name)

    # if os.name == "nt":
    #     os.system(f"call {profile_config_file}")
    # else:
    #     os.system(f"source {profile_config_file}")
    print(profile_config_file)


if __name__ == "__main__":
    main()
