#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Documentation content management.

Reads and writes markdown files from the version-first layout::

    documentation/ari/
    ├── versions.yaml
    ├── {version}/{page_id}.md  (e.g. home.docs.install.md)
    └── static/images/

Version applies globally to all doc pages (like ReadTheDocs).
Filenames match the page_id from pages.yaml.
"""

# =============================================================================
# Imports
# =============================================================================
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import markdown
import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.docs'
# The documentation root: documentation/ari/ in the repo
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOC_ROOT = REPO_ROOT / 'documentation' / 'ari'
DOC_STATIC = DOC_ROOT / 'static'
DOC_IMAGES = DOC_STATIC / 'images'
VERSIONS_FILE = DOC_ROOT / 'versions.yaml'

# Markdown extensions for rendering
MD_EXTENSIONS = [
    'extra',
    'codehilite',
    'toc',
    'tables',
    'fenced_code',
    'sane_lists',
]

MD_EXTENSION_CONFIGS = {
    'codehilite': {
        'css_class': 'highlight',
        'guess_lang': False,
    },
    'toc': {
        'permalink': True,
    },
}

# =============================================================================
# Define functions
# =============================================================================
def get_versions() -> List[dict]:
    """Get all doc versions from versions.yaml.

    Returns list of dicts: {id, name}  (first is default/latest).
    """
    if not VERSIONS_FILE.exists():
        return []
    with open(VERSIONS_FILE, 'r') as f:
        data = yaml.safe_load(f) or {}
    return data.get('versions', [])


def get_default_version() -> Optional[str]:
    """Return the default (first) version id, or None."""
    versions = get_versions()
    return versions[0]['id'] if versions else None


def get_doc_content(page_id: str,
                    version: Optional[str] = None
                    ) -> Tuple[str, str, Optional[str]]:
    """
    Get markdown content for a doc page.

    Layout: documentation/ari/{version}/{page_id}.md

    If version is None, uses the default (first) version.

    :param page_id: str, page identifier matching the markdown filename
    :param version: str or None, documentation version to look up

    :return: tuple of (raw_markdown, rendered_html, version_id)
    :rtype: tuple
    """
    if not version:
        version = get_default_version()
    if not version:
        return '', '<p>No documentation versions configured.</p>', None

    md_file = DOC_ROOT / version / f'{page_id}.md'
    if not md_file.exists():
        # Fall back to the 'all' directory for version-agnostic pages
        md_file = DOC_ROOT / 'all' / f'{page_id}.md'
    if not md_file.exists():
        return '', '<p>No documentation available for this version.</p>', version

    raw = md_file.read_text(encoding='utf-8')
    html = render_markdown(raw)
    return raw, html, version


def render_markdown(text: str) -> str:
    """Render markdown text to HTML."""
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    return md.convert(text)


def save_doc_content(page_id: str, version: str, content: str) -> None:
    """Save markdown content for a doc page version."""
    ver_dir = DOC_ROOT / version
    ver_dir.mkdir(parents=True, exist_ok=True)
    md_file = ver_dir / f'{page_id}.md'
    md_file.write_text(content, encoding='utf-8')


def save_uploaded_image(page_ref: str, filename: str,
                        data: bytes) -> str:
    """Save an uploaded image to documentation/ari/static/images/.

    Returns the filename for use in markdown.
    """
    DOC_IMAGES.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = re.sub(r'[^\w\-.]', '_', filename)
    # Add date tag and page reference
    date_tag = datetime.now().strftime('%Y%m%d_%H%M%S')
    stem, ext = os.path.splitext(safe_name)
    if not ext:
        ext = '.png'
    final_name = f'{page_ref}_{date_tag}_{stem}{ext}'

    dest = DOC_IMAGES / final_name
    dest.write_bytes(data)

    return final_name


def ensure_doc_dir(page_ref: str) -> None:
    """
    Ensure a documentation directory exists for a page reference.

    :param page_ref: str, page reference string used as directory name

    :return: None
    """
    page_dir = DOC_ROOT / page_ref
    page_dir.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
