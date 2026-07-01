#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Documentation content management.

Reads and writes markdown files from the version-first layout::

    documentation/ari/
    ├── versions.yaml
    ├── {version}/home/docs/.../*.md
    └── static/images/

Version applies globally to all doc pages (like ReadTheDocs).
"""

# =============================================================================
# Imports
# =============================================================================
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import markdown
import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.docs"
# The documentation root: documentation/ari/ in the repo
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOC_ROOT = REPO_ROOT / "documentation" / "ari"
DOC_STATIC = DOC_ROOT / "static"
DOC_IMAGES = DOC_STATIC / "images"
VERSIONS_FILE = DOC_ROOT / "versions.yaml"

# Markdown extensions for rendering
MD_EXTENSIONS = [
    "extra",
    "admonition",
    "codehilite",
    "toc",
    "tables",
    "fenced_code",
    "sane_lists",
]

MD_EXTENSION_CONFIGS = {
    "codehilite": {
        "css_class": "highlight",
        "guess_lang": False,
    },
    "toc": {
        "permalink": True,
    },
}

_DOC_CACHE_LOCK = threading.Lock()
_DOC_CACHE_TTL_S = 30.0
_DOC_VERSIONS_CACHE: dict = dict()
_DOC_CHILDREN_CACHE: dict = dict()
_DOC_SIDEBAR_CACHE: dict = dict()


def _cache_get(cache: dict, key):
    """Return cached value for key if not expired."""
    now = time.monotonic()
    with _DOC_CACHE_LOCK:
        entry = cache.get(key)
        if entry is None:
            return None
        if float(entry.get('expires', 0.0) or 0.0) <= now:
            cache.pop(key, None)
            return None
        return entry.get('value')


def _cache_set(cache: dict, key, value):
    """Set cached value for key with shared TTL."""
    now = time.monotonic()
    with _DOC_CACHE_LOCK:
        if len(cache) > 512:
            cache.clear()
        cache[key] = {
            'expires': now + _DOC_CACHE_TTL_S,
            'value': value,
        }


def _clone_list_of_dict(rows: List[dict]) -> List[dict]:
    """Return shallow-cloned list of dict rows."""
    out = []
    for row in list(rows or []):
        out.append(dict(row))
    return out


def _slug_to_label(name: str) -> str:
    """Convert a slug-like token into a display label."""
    clean = str(name or '').replace('_', ' ').replace('-', ' ').strip()
    if not clean:
        return ''
    return ' '.join(tok.capitalize() for tok in clean.split())


def _split_front_matter(text: str) -> Tuple[dict, str]:
    """Split YAML front matter from markdown body.

    Front matter must be at the very top of the file and bounded by
    `---` lines.
    """
    content = str(text or '')
    if not content.startswith('---'):
        return dict(), content

    # Match a leading YAML front-matter block.
    match = re.match(
        r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?',
        content,
        flags=re.DOTALL,
    )
    if match is None:
        return dict(), content

    raw_meta = match.group(1)
    meta_obj = yaml.safe_load(raw_meta)
    if not isinstance(meta_obj, dict):
        meta_obj = dict()
    body = content[match.end():]
    return meta_obj, body


def _card_meta_from_markdown(path: Path) -> dict:
    """Read optional card metadata from a markdown file."""
    if not path.exists() or not path.is_file():
        return dict()
    text = path.read_text(encoding='utf-8')
    meta, _body = _split_front_matter(text)
    return meta


def _merge_doc_child_item(existing: dict, incoming: dict) -> dict:
    """Merge one docs child item, preferring file metadata when present."""
    merged = dict(existing)
    merged['dir_present'] = bool(existing.get('dir_present')) or bool(
        incoming.get('dir_present')
    )
    merged['file_present'] = bool(existing.get('file_present')) or bool(
        incoming.get('file_present')
    )

    if incoming.get('file_present'):
        merged['label'] = str(
            incoming.get('label') or merged.get('label') or ''
        ).strip()
        merged['icon'] = str(
            incoming.get('icon') or merged.get('icon') or ''
        ).strip()
    elif not merged.get('file_present'):
        if incoming.get('label'):
            merged['label'] = str(incoming.get('label') or '').strip()
        if incoming.get('icon'):
            merged['icon'] = str(incoming.get('icon') or '').strip()

    merged['kind'] = 'dir' if merged['dir_present'] else 'file'
    merged['has_children'] = bool(merged['dir_present'])
    return merged


def _get_doc_children(
    rel_doc_dir: str,
    version: Optional[str],
) -> List[dict]:
    """Return merged immediate children for a docs directory."""
    if not version:
        version = get_default_version()
    if not version:
        return []

    rel_dir = normalize_doc_ref(rel_doc_dir)
    cache_key = (str(version or ''), rel_dir)
    cached = _cache_get(_DOC_CHILDREN_CACHE, cache_key)
    if isinstance(cached, list):
        return _clone_list_of_dict(cached)

    items_map: Dict[str, dict] = dict()
    scan_dirs = [
        (DOC_ROOT / 'all' / rel_dir, True),
        (DOC_ROOT / version / rel_dir, False),
    ]

    for base_dir, is_all_dir in scan_dirs:
        if not base_dir.exists() or not base_dir.is_dir():
            continue

        for child in sorted(base_dir.iterdir()):
            name = child.name
            if name.startswith('.'):
                continue

            if child.is_dir():
                child_ref = normalize_doc_ref(rel_dir + '/' + name)
                dir_meta = _card_meta_from_markdown(child / 'index.md')
                item = dict(
                    key=child_ref,
                    kind='dir',
                    name=name,
                    label=str(
                        dir_meta.get('card_label')
                        or dir_meta.get('title')
                        or _slug_to_label(name)
                    ).strip(),
                    icon=str(
                        dir_meta.get('card_icon')
                        or dir_meta.get('icon')
                        or ''
                    ).strip(),
                    rel_path=child_ref,
                    dir_present=True,
                    file_present=False,
                )
            elif child.is_file() and child.suffix.lower() == '.md':
                stem = child.stem
                if stem.lower() == 'index':
                    continue
                child_ref = normalize_doc_ref(rel_dir + '/' + stem)
                file_meta = _card_meta_from_markdown(child)
                item = dict(
                    key=child_ref,
                    kind='file',
                    name=stem,
                    label=str(
                        file_meta.get('card_label')
                        or file_meta.get('title')
                        or _slug_to_label(stem)
                    ).strip(),
                    icon=str(
                        file_meta.get('card_icon')
                        or file_meta.get('icon')
                        or ''
                    ).strip(),
                    rel_path=child_ref,
                    dir_present=False,
                    file_present=True,
                )
            else:
                continue

            existing = items_map.get(item['key'])
            if existing is None:
                items_map[item['key']] = item
            else:
                items_map[item['key']] = _merge_doc_child_item(
                    existing,
                    item,
                )

    children = []
    for key in sorted(items_map.keys()):
        children.append(items_map[key])
    _cache_set(_DOC_CHILDREN_CACHE, cache_key, _clone_list_of_dict(children))
    return children


def get_doc_sidebar_tree(
    doc_ref: str,
    version: Optional[str] = None,
) -> List[dict]:
    """Build a docs navigation tree rooted at ``home/docs``."""
    if not version:
        version = get_default_version()
    if not version:
        return []

    current_ref = normalize_doc_ref(doc_ref)
    cache_key = (str(version or ''), current_ref)
    cached = _cache_get(_DOC_SIDEBAR_CACHE, cache_key)
    if isinstance(cached, list):
        return _clone_list_of_dict(cached)

    tree: List[dict] = []

    def walk(rel_doc_dir: str, depth: int) -> None:
        children = _get_doc_children(rel_doc_dir, version)
        for child in children:
            rel_path = child['rel_path']
            suffix = ''
            if rel_path.startswith('home/docs/'):
                suffix = rel_path[len('home/docs/'):]
            elif rel_path == 'home/docs':
                suffix = ''

            url = '/docs' if not suffix else '/docs/' + suffix
            icon = child.get('icon', '')
            if not icon:
                if child['kind'] == 'dir':
                    icon = 'fa-solid fa-folder'
                else:
                    icon = 'fa-solid fa-file-lines'

            item_id = 'home.docs'
            if suffix:
                item_id = 'home.docs.' + suffix.replace('/', '.')

            tree.append(
                dict(
                    id=item_id,
                    label=child.get('label') or child.get('name') or suffix,
                    icon=icon,
                    url=url,
                    depth=depth,
                    kind=child.get('kind', 'file'),
                    has_children=bool(child.get('has_children')),
                    pinned=False,
                    disabled=False,
                    active=(rel_path == current_ref),
                )
            )

            if child['kind'] == 'dir':
                walk(rel_path, depth + 1)

    walk('home/docs', 0)
    for idx, item in enumerate(tree):
        next_idx = idx + 1
        if next_idx >= len(tree):
            continue
        if tree[next_idx].get('depth', 0) > item.get('depth', 0):
            tree[idx]['has_children'] = True
    _cache_set(_DOC_SIDEBAR_CACHE, cache_key, _clone_list_of_dict(tree))
    return tree


def normalize_doc_ref(doc_ref: str) -> str:
    """Normalize external doc refs to ``home/docs/...`` style paths."""
    ref = str(doc_ref or '').strip().strip('/')
    if not ref:
        return 'home/docs'
    if ref.startswith('home/docs'):
        tail = ref[9:].strip('/')
        if tail:
            return f'home/docs/{tail}'
        return 'home/docs'

    if ref.startswith('docs/'):
        tail = ref[5:].strip('/')
        if tail:
            return f'home/docs/{tail}'
        return 'home/docs'

    return f'home/docs/{ref}'


def _resolve_markdown_path(
    rel_doc_path: str,
    version: Optional[str],
) -> Tuple[Optional[Path], Optional[str]]:
    """Resolve markdown file path using version then ``all`` fallback."""
    if not version:
        version = get_default_version()
    if not version:
        return None, None

    rel_doc_path = normalize_doc_ref(rel_doc_path)

    candidates = [
        (DOC_ROOT / version / f'{rel_doc_path}.md', version),
        (DOC_ROOT / 'all' / f'{rel_doc_path}.md', version),
    ]
    for md_file, ver in candidates:
        if md_file.exists() and md_file.is_file():
            return md_file, ver
    return None, version


def doc_exists(doc_ref: str, version: Optional[str] = None) -> bool:
    """Return True when documentation markdown exists for this ref."""
    md_file, _ = _resolve_markdown_path(doc_ref, version)
    return md_file is not None


def get_doc_cards(
    doc_ref: str,
    version: Optional[str] = None,
) -> Tuple[List[dict], Optional[str], str]:
    """Return immediate child cards for a doc directory page."""
    if not version:
        version = get_default_version()
    if not version:
        return [], None, normalize_doc_ref(doc_ref)

    rel_doc_dir = normalize_doc_ref(doc_ref)
    children = _get_doc_children(rel_doc_dir, version)

    cards: List[dict] = []
    for item in children:
        rel = item['rel_path']
        suffix = ''
        if rel.startswith('home/docs/'):
            suffix = rel[len('home/docs/'):]
        url = '/docs' if not suffix else '/docs/' + suffix
        cards.append(
            dict(
                label=item['label'] or item['name'],
                icon=item.get('icon')
                or (
                    'fa-solid fa-folder' if item['kind'] == 'dir'
                    else 'fa-solid fa-file-lines'
                ),
                url=url,
            )
        )
    return cards, version, rel_doc_dir


# =============================================================================
# Define functions
# =============================================================================
def get_versions() -> List[dict]:
    """Get all doc versions from versions.yaml.

    Returns list of dicts: {id, name}  (first is default/latest).
    """
    cache_key = str(VERSIONS_FILE)
    cached = _cache_get(_DOC_VERSIONS_CACHE, cache_key)
    if isinstance(cached, list):
        return [dict(item) for item in cached if isinstance(item, dict)]

    if not VERSIONS_FILE.exists():
        return []
    with open(VERSIONS_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    versions = data.get('versions', [])
    if not isinstance(versions, list):
        versions = []
    clean = [dict(item) for item in versions if isinstance(item, dict)]
    _cache_set(_DOC_VERSIONS_CACHE, cache_key, clean)
    return [dict(item) for item in clean]


def get_default_version() -> Optional[str]:
    """Return the default (first) version id, or None."""
    versions = get_versions()
    return versions[0]["id"] if versions else None


def get_doc_content(
    doc_ref: str, version: Optional[str] = None
) -> Tuple[str, str, Optional[str]]:
    """
    Get markdown content for a doc page.

    Layout: documentation/ari/{version}/{page_id}.md

    If version is None, uses the default (first) version.

    :param doc_ref: str, slash path under home/docs/ matching the markdown
    :param version: str or None, documentation version to look up

    :return: tuple of (raw_markdown, rendered_html, version_id)
    :rtype: tuple
    """
    if not version:
        version = get_default_version()
    if not version:
        return "", "<p>No documentation versions configured.</p>", None

    rel_doc_path = normalize_doc_ref(doc_ref)
    md_file, version = _resolve_markdown_path(rel_doc_path, version)
    if md_file is None:
        return (
            '',
            '<p>No documentation available for this version.</p>',
            version,
        )

    raw = md_file.read_text(encoding='utf-8')
    _meta, body = _split_front_matter(raw)
    html = render_markdown(body)
    return raw, html, version


def get_doc_last_modified(
    doc_ref: str,
    version: Optional[str] = None,
) -> str:
    """Return last-modified timestamp text from the markdown file."""
    rel_doc_path = normalize_doc_ref(doc_ref)
    md_file, _ = _resolve_markdown_path(rel_doc_path, version)
    if md_file is None:
        return ''
    try:
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
    except Exception:
        return ''
    return mtime.strftime('%Y-%m-%d %H:%M:%S')


def render_markdown(text: str) -> str:
    """Render markdown text to HTML."""
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    return md.convert(text)


def save_doc_content(doc_ref: str, version: str, content: str) -> None:
    """Save markdown content for a doc page version."""
    rel_doc_path = normalize_doc_ref(doc_ref)
    ver_dir = DOC_ROOT / version
    ver_dir.mkdir(parents=True, exist_ok=True)
    md_file = ver_dir / f'{rel_doc_path}.md'
    md_file.parent.mkdir(parents=True, exist_ok=True)
    md_file.write_text(content, encoding='utf-8')


def save_uploaded_image(page_ref: str, filename: str, data: bytes) -> str:
    """Save an uploaded image to documentation/ari/static/images/.

    Returns the filename for use in markdown.
    """
    DOC_IMAGES.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = re.sub(r"[^\w\-.]", "_", filename)
    # Add date tag and page reference
    date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem, ext = os.path.splitext(safe_name)
    if not ext:
        ext = ".png"
    final_name = f"{page_ref}_{date_tag}_{stem}{ext}"

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
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
