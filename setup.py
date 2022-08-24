import os
from pathlib import Path

from setuptools import setup

INSTRUMENTS = ["spirou", "nirps_ha", "nirps_he"]

PACKAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def get_relative_path(path):
    return PACKAGE_DIR.joinpath(path)


binpath = get_relative_path("apero/recipes")
tools_path = get_relative_path("apero/tools/recipes")

# %%
paths = []
for path in binpath.iterdir():
    if path.is_dir() and path.name in INSTRUMENTS:
        paths.append(path)
for path in tools_path.iterdir():
    if path.is_dir():
        paths.append(path)

# %%
scripts = []
for path in paths:
    for f in path.iterdir():
        if f.is_file() and os.access(f, os.X_OK) and f.name != "__init__.py":
            scripts.append(os.path.relpath(str(f)))

# %%
setup(scripts=scripts)
