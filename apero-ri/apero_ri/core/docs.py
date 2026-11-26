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
import hashlib
import json
import logging
import os
import posixpath
import re
import threading
import time
from html import unescape
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlsplit, urlunsplit

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
# Doc ref (post-normalize_doc_ref) whose body is generated from
# GLOSSARY_REL_PATH at request time, rather than read from disk, so the
# page and the inline-tooltip term list can never drift apart.
GLOSSARY_DOC_REF = 'home/docs/glossary'
GLOSSARY_REL_PATH = 'home/docs/glossary.yaml'

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
        "use_pygments": True,
    },
    "toc": {
        "permalink": True,
    },
}

_DOC_CACHE_LOCK = threading.Lock()
_DOC_CACHE_TTL_S = 30.0
_DOC_VERSIONS_CACHE: dict = dict()
# Child/sidebar caches are invalidated by directory signature rather than
# a blind TTL: docs only change when someone edits/saves a page or the
# apero_documentation tool rebuilds the tree, so a correctness-based
# cache can be kept indefinitely between those events instead of
# re-scanning + re-parsing front matter every 30s.
_DOC_CHILDREN_CACHE: dict = dict()
# Bumped per-version every time _get_doc_children actually recomputes
# (cache miss), so get_doc_sidebar_tree can tell whether any directory
# it walked has changed since its own result was cached.
_DOC_CHILDREN_GENERATION: dict = dict()
_DOC_SIDEBAR_CACHE: dict = dict()
_DOC_SEARCH_CACHE: dict = dict()
# Rendered-HTML cache keyed by the source file's mtime, so the
# markdown -> HTML conversion (codehilite/toc/mermaid regex pass) only
# re-runs when the page content actually changes, not on every request.
_DOC_RENDER_CACHE: dict = dict()

# Prebuilt per-version snapshots (rendered pages, children, search index)
# persisted under <data_dir>/docs_cache so requests never build docs.
_SNAPSHOT_SCHEMA = 1
_SNAPSHOT_DIR_NAME = 'docs_cache'
_SNAPSHOT_RELOAD_CHECK_S = 5.0
_SNAPSHOT_LOCK = threading.Lock()
_SNAPSHOT_REFRESH_LOCK = threading.Lock()
_SNAPSHOT_STATE: Dict[str, Any] = dict(dir=None, thread=None)
_SNAPSHOTS: Dict[str, dict] = dict()
_SNAPSHOT_CHECKED: Dict[str, float] = dict()
_SNAPSHOT_FILE_MTIME: Dict[str, int] = dict()
_SNAPSHOT_PENDING = threading.Event()
# Builder thread sets ``bypass`` so it renders from source, not itself.
_SNAPSHOT_LOCAL = threading.local()
LOGGER = logging.getLogger(__NAME__)


def _cache_get(cache: Dict[Any, Any], key: Any) -> Any:
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


def _cache_set(cache: Dict[Any, Any], key: Any, value: Any) -> None:
    """Set cached value for key with shared TTL."""
    now = time.monotonic()
    with _DOC_CACHE_LOCK:
        if len(cache) > 512:
            cache.clear()
        cache[key] = {
            'expires': now + _DOC_CACHE_TTL_S,
            'value': value,
        }


def _dir_signature(path: Path) -> Tuple[Tuple[str, int], ...]:
    """Return a cheap (name, mtime_ns) signature for a directory's entries.

    Only stats the listing (no file reads), so it can be checked on
    every request to detect added/removed/edited entries without
    paying the cost of re-parsing front matter for unchanged ones.

    :param path: Path, directory to fingerprint

    :return: tuple of (name, mtime_ns) pairs, sorted by name; empty
        tuple when the directory does not exist
    """
    try:
        entries = sorted(
            (entry.name, entry.stat().st_mtime_ns)
            for entry in os.scandir(path)
            if not entry.name.startswith('.')
        )
    except OSError:
        return ()
    return tuple(entries)


def _clone_list_of_dict(
    rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
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


def _split_front_matter(
    text: str,
) -> Tuple[Dict[str, Any], str]:
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


def _card_meta_from_markdown(path: Path) -> Dict[str, Any]:
    """Read optional card metadata from a markdown file."""
    if not path.exists() or not path.is_file():
        return dict()
    text = path.read_text(encoding='utf-8')
    meta, _body = _split_front_matter(text)
    return meta


def _merge_doc_child_item(
    existing: Dict[str, Any], incoming: Dict[str, Any]
) -> Dict[str, Any]:
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
    snapshot = _active_snapshot(version)
    if snapshot is not None and rel_dir in snapshot['children']:
        return _clone_list_of_dict(snapshot['children'][rel_dir])
    version_key = str(version or '')
    cache_key = (version_key, rel_dir)
    scan_dirs = [
        (DOC_ROOT / 'all' / rel_dir, True),
        (DOC_ROOT / version / rel_dir, False),
    ]
    # Cheap listing fingerprint; reuse the (expensive) parsed result
    # below for as long as neither scan dir's contents have changed.
    signature = tuple(_dir_signature(base_dir) for base_dir, _ in scan_dirs)
    with _DOC_CACHE_LOCK:
        entry = _DOC_CHILDREN_CACHE.get(cache_key)
    if entry is not None and entry.get('sig') == signature:
        return _clone_list_of_dict(entry['value'])

    items_map: Dict[str, dict] = dict()

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

    with _DOC_CACHE_LOCK:
        if len(_DOC_CHILDREN_CACHE) > 512:
            _DOC_CHILDREN_CACHE.clear()
        _DOC_CHILDREN_CACHE[cache_key] = dict(
            sig=signature,
            value=_clone_list_of_dict(children),
        )
        # Tell any sidebar-tree cache keyed on this version that this
        # directory's content changed, so it knows to rebuild too.
        _DOC_CHILDREN_GENERATION[version_key] = (
            _DOC_CHILDREN_GENERATION.get(version_key, 0) + 1
        )
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
    version_key = str(version or '')
    # A swapped-in snapshot changes the children without bumping the
    # generation counter, so key the tree on its fingerprint too.
    snapshot = _active_snapshot(version)
    snap_fp = snapshot['fingerprint'] if snapshot is not None else ''
    cache_key = (version_key, current_ref, snap_fp)
    # Reuse the cached tree as long as no directory it was built from
    # has changed (tracked via _DOC_CHILDREN_GENERATION), rather than a
    # blind TTL that still re-walks all 190+ files every 30s.
    generation = _DOC_CHILDREN_GENERATION.get(version_key, 0)
    with _DOC_CACHE_LOCK:
        entry = _DOC_SIDEBAR_CACHE.get(cache_key)
    if entry is not None and entry.get('gen') == generation:
        return _clone_list_of_dict(entry['value'])

    tree: List[dict] = []

    def walk(rel_doc_dir: str, depth: int) -> None:
        """Append the directory's children and recursively visit subdirs."""
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
                    rel_path=rel_path,
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

    # The walk above may have triggered _get_doc_children cache misses
    # (bumping the generation counter); store the tree keyed to the
    # generation actually observed while building it, not the one read
    # before the walk started.
    generation = _DOC_CHILDREN_GENERATION.get(version_key, 0)
    with _DOC_CACHE_LOCK:
        if len(_DOC_SIDEBAR_CACHE) > 512:
            _DOC_SIDEBAR_CACHE.clear()
        _DOC_SIDEBAR_CACHE[cache_key] = dict(
            gen=generation,
            value=_clone_list_of_dict(tree),
        )
    return tree


def get_search_index(version: Optional[str] = None) -> List[dict]:
    """Return a flat, searchable index of every doc page for one version.

    Piggybacks on the cached sidebar tree and caches extracted page text by
    its generation. The first index request reads page bodies once; later
    requests only reuse the cached list. This lets autocomplete find science
    terms and recipe descriptions without putting disk reads in the
    per-keystroke path.

    :param version: str or None, documentation version

    :return: list of dict, each ``{label, url, keywords}`` where
        ``keywords`` is a lowercased, space-joined string of the label
        and its URL path segments for simple client-side filtering
    """
    if not version:
        version = get_default_version()
    if not version:
        return []

    snapshot = _active_snapshot(version)
    if snapshot is not None:
        return _clone_list_of_dict(snapshot['search_index'])

    tree = get_doc_sidebar_tree('home/docs', version)
    version_key = str(version)
    generation = _DOC_CHILDREN_GENERATION.get(version_key, 0)
    cache_key = (version_key, generation)
    with _DOC_CACHE_LOCK:
        cached = _DOC_SEARCH_CACHE.get(cache_key)
    if cached is not None:
        return _clone_list_of_dict(cached)

    index: List[dict] = []
    for item in tree:
        label = str(item.get('label') or '').strip()
        url = str(item.get('url') or '').strip()
        if not label or not url:
            continue
        slug_tokens = [tok for tok in re.split(r'[/_\-]+', url) if tok]
        doc_ref = str(item.get('rel_path') or '')
        if doc_ref.endswith('/index'):
            content_ref = doc_ref
        elif item.get('kind') == 'dir':
            content_ref = doc_ref + '/index'
        else:
            content_ref = doc_ref
        md_file, _ = _resolve_markdown_path(content_ref, version)
        body_text = ''
        if normalize_doc_ref(content_ref) == GLOSSARY_DOC_REF:
            body_text = _build_glossary_markdown(version)
        elif md_file is not None:
            source = md_file.read_text(encoding='utf-8')
            _meta, body_text = _split_front_matter(source)
            body_text = re.sub(r'```.*?```', ' ', body_text,
                               flags=re.DOTALL)
            body_text = re.sub(r'`[^`]*`', ' ', body_text)
            body_text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', body_text)
            body_text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1',
                               body_text)
            body_text = re.sub(r'[#>*_|~`]', ' ', body_text)
            body_text = unescape(body_text)
        keywords = ' '.join([label] + slug_tokens + [body_text]).lower()
        index.append(dict(label=label, url=url, keywords=keywords))
    with _DOC_CACHE_LOCK:
        if len(_DOC_SEARCH_CACHE) > 32:
            _DOC_SEARCH_CACHE.clear()
        _DOC_SEARCH_CACHE[cache_key] = _clone_list_of_dict(index)
    return index


def normalize_doc_ref(doc_ref: str) -> str:
    """Normalize external doc refs to ``home/docs/...`` style paths."""
    ref = str(doc_ref or '').strip().strip('/')
    if ref.lower().endswith('.md'):
        ref = ref[:-3]
    if ref.lower().endswith('/index'):
        ref = ref[:-len('/index')]
    elif ref.lower() == 'index':
        ref = ''
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
        (DOC_ROOT / version / rel_doc_path / 'index.md', version),
        (DOC_ROOT / 'all' / f'{rel_doc_path}.md', version),
        (DOC_ROOT / 'all' / rel_doc_path / 'index.md', version),
    ]
    for md_file, ver in candidates:
        if md_file.exists() and md_file.is_file():
            return md_file, ver
    return None, version


def doc_exists(doc_ref: str, version: Optional[str] = None) -> bool:
    """Return True when documentation markdown exists for this ref."""
    if _snapshot_page(doc_ref, version) is not None:
        return True
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


def _resolve_glossary_path(version: Optional[str]) -> Optional[Path]:
    """Resolve ``glossary.yaml`` using version then ``all`` fallback."""
    if not version:
        version = get_default_version()
    if not version:
        return None
    for base_dir in (DOC_ROOT / version, DOC_ROOT / 'all'):
        path = base_dir / GLOSSARY_REL_PATH
        if path.exists() and path.is_file():
            return path
    return None


def get_glossary_terms(version: Optional[str] = None) -> List[dict]:
    """Return glossary terms sorted alphabetically by term.

    :param version: str or None, documentation version

    :return: list of dict, each ``{term, definition}``
    """
    path = _resolve_glossary_path(version)
    if path is None:
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return []
    terms = [
        dict(term=str(term), definition=str(definition or '').strip())
        for term, definition in data.items()
    ]
    terms.sort(key=lambda item: item['term'].lower())
    return terms


def _build_glossary_markdown(version: Optional[str]) -> str:
    """Render the glossary page body from ``glossary.yaml``."""
    terms = get_glossary_terms(version)
    if not terms:
        return '# Glossary\n\nNo glossary terms are defined yet.\n'

    lines = [
        '# Glossary',
        '',
        'APERO and science terms used throughout this documentation.',
        '',
    ]
    for item in terms:
        lines.append('### {0}'.format(item['term']))
        lines.append('')
        lines.append(item['definition'])
        lines.append('')
    return '\n'.join(lines)


# Glossary substitutions apply only to plain HTML text, never markup or attrs.
_HTML_TAG_RE = re.compile(r'(<[^>]+>)')
_HTML_TAG_NAME_RE = re.compile(r'^<(\/?)\s*([A-Za-z][\w:-]*)\b')
_GLOSSARY_PROTECTED_TAGS = {'a', 'pre', 'code', 'h1', 'h2', 'h3',
                            'h4', 'h5', 'h6'}
_HTML_VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                   'input', 'link', 'meta', 'param', 'source', 'track',
                   'wbr'}


def _wrap_glossary_terms(html: str, terms: List[dict]) -> str:
    """Wrap the first mention of each glossary term on a page.

    Each match becomes a link to the glossary page with the
    definition in its ``title`` attribute (a native browser tooltip
    on hover/focus - no extra JS needed). Only the first occurrence of
    a term per page is wrapped, so a page that says e.g. "recipe"
    forty times isn't cluttered with forty links.

    :param html: str, already-rendered page HTML
    :param terms: list of dict, each ``{term, definition}``

    :return: str, HTML with glossary links inserted
    """
    if not terms or not html:
        return html

    patterns = []
    sorted_terms = sorted(
        terms, key=lambda item: len(str(item.get('term') or '')), reverse=True
    )
    for item in sorted_terms:
        term = str(item.get('term') or '').strip()
        if not term:
            continue
        pattern = re.compile(
            r'(?<![\w-])(' + re.escape(term) + r')(?![\w-])',
            re.IGNORECASE,
        )
        safe_def = (
            str(item.get('definition') or '')
            .replace('&', '&amp;')
            .replace('"', '&quot;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )
        patterns.append((pattern, safe_def))

    protected_stack: List[str] = []
    output_parts: List[str] = []
    wrapped_terms = set()
    for part in _HTML_TAG_RE.split(html):
        if not part:
            continue
        if part.startswith('<'):
            tag_match = _HTML_TAG_NAME_RE.match(part)
            if tag_match is not None:
                closing, tag_name = tag_match.groups()
                tag_name = tag_name.lower()
                if closing:
                    if tag_name in protected_stack:
                        reverse_index = protected_stack[::-1].index(tag_name)
                        stack_index = len(protected_stack) - 1 - reverse_index
                        del protected_stack[stack_index:]
                elif tag_name in _GLOSSARY_PROTECTED_TAGS:
                    if not part.rstrip().endswith('/>'):
                        protected_stack.append(tag_name)
                elif (protected_stack
                      and tag_name not in _HTML_VOID_TAGS
                      and not part.rstrip().endswith('/>')):
                    protected_stack.append(tag_name)
            output_parts.append(part)
            continue
        if protected_stack:
            output_parts.append(part)
            continue

        candidates = []
        for pattern, safe_def in patterns:
            match = pattern.search(part)
            if match is None:
                continue
            term_key = match.group(1).lower()
            if term_key not in wrapped_terms:
                candidates.append((match.start(), match.end(), term_key,
                                   safe_def, match.group(1)))
        candidates.sort(key=lambda candidate: (
            candidate[0], -(candidate[1] - candidate[0])
        ))
        cursor = 0
        text_parts = []
        for start, end, term_key, safe_def, label in candidates:
            if start < cursor or term_key in wrapped_terms:
                continue
            text_parts.append(part[cursor:start])
            text_parts.append(
                '<a class="ari-glossary-term" href="/docs/glossary" '
                'title="{0}">{1}</a>'.format(safe_def, label)
            )
            cursor = end
            wrapped_terms.add(term_key)
        text_parts.append(part[cursor:])
        output_parts.append(''.join(text_parts))
    return ''.join(output_parts)


_MARKDOWN_LINK_RE = re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')
_FENCED_CODE_RE = re.compile(r'^```.*?^```\s*$', re.MULTILINE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r'`([^`\n]+)`')


def _normalize_relative_doc_links(text: str, doc_ref: str,
                                  md_file: Path,
                                  version: Optional[str]) -> str:
    """Resolve relative Markdown page links into canonical ARI doc URLs.

    Markdown files are stored as ordinary files, while ARI routes use
    extensionless page refs and do not require a trailing slash. Browsers
    therefore resolve a link such as ``recipes/bad`` incorrectly when it
    appears on ``/docs/apero/instruments/spirou/recipes``. Resolve relative
    targets using the source file's directory, then rewrite only targets
    that correspond to an actual documentation page.

    :param text: str, Markdown body text
    :param doc_ref: str, normalized source page ref
    :param md_file: Path, resolved source Markdown file
    :param version: str or None, documentation version

    :return: str, Markdown with resolved local documentation links
    """
    normalized_ref = normalize_doc_ref(doc_ref)
    if md_file.name == 'index.md':
        base_ref = normalized_ref
    else:
        base_ref = posixpath.dirname(normalized_ref)

    def replace_link(match: re.Match) -> str:
        """Rewrite a local Markdown link when its target page exists."""
        label = match.group(1)
        raw_target = match.group(2).strip()
        target_part = raw_target.split(maxsplit=1)[0]
        if target_part.startswith('<') and target_part.endswith('>'):
            target_part = target_part[1:-1]
        parsed = urlsplit(target_part)
        if (parsed.scheme or parsed.netloc or not parsed.path
                or parsed.path.startswith('/')):
            return match.group(0)

        target_path = parsed.path
        suffix = Path(target_path).suffix.lower()
        if suffix in ['.md', '.html']:
            target_path = target_path[:-len(suffix)]
        target_ref = None
        search_base = base_ref
        while search_base == 'home/docs' or search_base.startswith(
            'home/docs/'
        ):
            candidate = posixpath.normpath(
                posixpath.join(search_base, target_path)
            ).strip('/')
            in_docs = (candidate == 'home/docs'
                       or candidate.startswith('home/docs/'))
            if in_docs and doc_exists(candidate, version):
                target_ref = candidate
                break
            if search_base == 'home/docs':
                break
            search_base = posixpath.dirname(search_base)
        if target_ref is None:
            return match.group(0)

        short_ref = target_ref[len('home/docs'):].strip('/')
        route = '/docs' if not short_ref else '/docs/' + short_ref
        route = urlunsplit(('', '', route, parsed.query, parsed.fragment))
        return '[{0}]({1})'.format(label, route)

    return _MARKDOWN_LINK_RE.sub(replace_link, text)


def _linkify_apero_commands(text: str, version: Optional[str]) -> str:
    """Link known APERO recipe/tool names to their generated detail pages.

    Only command-like labels beginning with ``apero_`` are linked. Existing
    Markdown links and fenced code are left intact; inline-code command names
    become normal links so they remain clickable in rendered prose and tables.

    :param text: str, Markdown body text
    :param version: str or None, documentation version

    :return: str, body with known APERO command names linked
    """
    commands = {}
    for item in get_search_index(version):
        label = str(item.get('label') or '').strip()
        url = str(item.get('url') or '').strip()
        if label.lower().startswith('apero_') and url.startswith('/docs/'):
            commands[label.lower()] = (label, url)
    if not commands:
        return text

    placeholders = []

    def protect(value: str) -> str:
        """Replace protected Markdown with a reversible placeholder."""
        placeholders.append(value)
        return '\x00APERO_LINK_BLOCK_{0}\x00'.format(
            len(placeholders) - 1)

    body = _FENCED_CODE_RE.sub(lambda match: protect(match.group(0)), text)

    def link_inline_code(match: re.Match) -> str:
        """Link inline code when it names a known APERO command."""
        token = match.group(1).strip()
        command = commands.get(token.lower())
        if command is None:
            return match.group(0)
        label, url = command
        return '[{0}]({1})'.format(label, url)

    body = _INLINE_CODE_RE.sub(link_inline_code, body)
    body = _MARKDOWN_LINK_RE.sub(lambda match: protect(match.group(0)), body)
    for name, (label, url) in sorted(
        commands.items(), key=lambda item: len(item[0]), reverse=True
    ):
        pattern = re.compile(r'(?<![A-Za-z0-9_]){0}(?![A-Za-z0-9_])'
                             .format(re.escape(name)), re.IGNORECASE)
        body = pattern.sub('[{0}]({1})'.format(label, url), body)
    for index, original in enumerate(placeholders):
        marker = '\x00APERO_LINK_BLOCK_{0}\x00'.format(index)
        body = body.replace(marker, original)
    return body


def get_doc_content(
    doc_ref: str, version: Optional[str] = None
) -> Tuple[str, str, Optional[str], dict]:
    """
    Get markdown content for a doc page.

    Layout: documentation/ari/{version}/{page_id}.md

    If version is None, uses the default (first) version.

    :param doc_ref: str, slash path under home/docs/ matching the markdown
    :param version: str or None, documentation version to look up

    :return: tuple of (raw_markdown, rendered_html, version_id, meta),
        where meta is the page's parsed YAML front matter (e.g. its
        ``related:`` topics list), or an empty dict if there is none
    :rtype: tuple
    """
    if not version:
        version = get_default_version()
    if not version:
        return "", "<p>No documentation versions configured.</p>", None, {}

    rel_doc_path = normalize_doc_ref(doc_ref)
    page = _snapshot_page(rel_doc_path, version)
    if page is not None:
        return page['raw'], page['html'], page['version'], dict(page['meta'])

    md_file, version = _resolve_markdown_path(rel_doc_path, version)
    if md_file is None:
        return (
            '',
            '<p>No documentation available for this version.</p>',
            version,
            {},
        )

    # The markdown parse (codehilite/toc/mermaid extraction) is the
    # expensive part of serving a page; skip it whenever the file's
    # mtime matches the last render, instead of redoing it on every
    # click as before.
    mtime_ns = _content_mtime(md_file, version)
    is_glossary = rel_doc_path == GLOSSARY_DOC_REF

    cache_key = (str(version or ''), rel_doc_path)
    with _DOC_CACHE_LOCK:
        entry = _DOC_RENDER_CACHE.get(cache_key)
    if entry is not None and entry.get('mtime') == mtime_ns:
        raw, html, meta = entry['value']
        return raw, html, version, meta

    raw = md_file.read_text(encoding='utf-8')
    meta, body = _split_front_matter(raw)
    if is_glossary:
        body = _build_glossary_markdown(version)
    body = _linkify_apero_commands(body, version)
    body = _normalize_relative_doc_links(body, rel_doc_path, md_file,
                                         version)
    html = render_markdown(body)
    if not is_glossary:
        # Skip tagging the glossary page itself, or every term's own
        # heading would immediately self-wrap.
        html = _wrap_glossary_terms(html, get_glossary_terms(version))

    with _DOC_CACHE_LOCK:
        if len(_DOC_RENDER_CACHE) > 512:
            _DOC_RENDER_CACHE.clear()
        _DOC_RENDER_CACHE[cache_key] = dict(
            mtime=mtime_ns,
            value=(raw, html, meta),
        )
    return raw, html, version, meta


def get_doc_dir_meta(rel_doc_dir: str, version: Optional[str] = None) -> dict:
    """Return front matter for a docs directory's own ``index.md``.

    Directory listing pages (card grids) can declare ``related:``
    topics in their own ``index.md`` front matter, same as leaf pages;
    this is not covered by ``get_doc_cards``, which only reads the
    *children's* front matter for card labels/icons.

    :param rel_doc_dir: str, doc ref for the directory (e.g. ``apero``)
    :param version: str or None, documentation version

    :return: dict, parsed front matter, or empty dict if no index.md
    """
    rel_dir = normalize_doc_ref(rel_doc_dir)
    md_file, _ = _resolve_markdown_path(rel_dir + '/index', version)
    if md_file is None:
        return dict()
    return _card_meta_from_markdown(md_file)


def build_related_topics(meta: dict, version: Optional[str]) -> List[dict]:
    """Build related-topics links from a page's ``related:`` front matter.

    Accepts either plain doc refs (label auto-derived from the target
    page's own card metadata) or ``{ref, label}`` dicts for a custom
    label, e.g.::

        related:
          - developer
          - {ref: reference, label: Reference guides}

    :param meta: dict, the page's parsed front matter
    :param version: str or None, documentation version to resolve
        target labels against

    :return: list of dict, each ``{label, url}``
    """
    raw_items = meta.get('related') if isinstance(meta, dict) else None
    if not isinstance(raw_items, list):
        return []

    topics = []
    for raw_item in raw_items:
        if isinstance(raw_item, dict):
            ref = str(raw_item.get('ref') or '').strip()
            label = str(raw_item.get('label') or '').strip()
        else:
            ref = str(raw_item or '').strip()
            label = ''
        if not ref:
            continue

        normalized = normalize_doc_ref(ref)
        short_ref = (
            normalized[len('home/docs/'):]
            if normalized != 'home/docs' else ''
        )
        if not label:
            target_page = _snapshot_page(ref, version)
            if target_page is not None:
                target_meta = target_page['meta']
            else:
                md_file, _ = _resolve_markdown_path(ref, version)
                target_meta = (
                    _card_meta_from_markdown(md_file) if md_file else {}
                )
            fallback_name = short_ref.split('/')[-1] if short_ref else 'home'
            label = str(
                target_meta.get('card_label')
                or target_meta.get('title')
                or _slug_to_label(fallback_name)
            ).strip()

        url = '/docs' if not short_ref else '/docs/' + short_ref
        topics.append(dict(label=label, url=url))
    return topics


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


def _extract_mermaid(text: str) -> Tuple[str, List[str]]:
    """Replace ```mermaid fences with placeholders markdown will not touch.

    The fenced-code/codehilite extensions would otherwise syntax-highlight
    the diagram source and destroy the language marker, so mermaid.js could
    never find it. We pull the blocks out first and re-insert them as
    ``<div class="mermaid">`` after rendering.

    :param text: str, the raw markdown body

    :return: tuple, 1. the markdown with placeholders, 2. the diagram sources
    """
    blocks: List[str] = []

    def _replace(match: 're.Match') -> str:
        """Store one diagram and return its placeholder."""
        blocks.append(match.group(1))
        # Placeholder must survive markdown as its own paragraph.
        return '\n\nAPEROMERMAIDBLOCK{0}\n\n'.format(len(blocks) - 1)

    pattern = r'^[ \t]*```+[ \t]*mermaid[ \t]*\r?\n(.*?)\r?\n[ \t]*```+[ \t]*$'
    out = re.sub(pattern, _replace, text, flags=re.DOTALL | re.MULTILINE)
    return out, blocks


def _restore_mermaid(html: str, blocks: List[str]) -> str:
    """Swap mermaid placeholders in rendered HTML for mermaid containers.

    :param html: str, the rendered HTML containing placeholders
    :param blocks: list of str, the diagram sources in placeholder order

    :return: str, the HTML with ``<div class="mermaid">`` containers
    """
    for index, source in enumerate(blocks):
        # Escape so the diagram source cannot inject markup.
        safe = (
            source.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )
        container = '<div class="mermaid">\n{0}\n</div>'.format(safe)
        # markdown may have wrapped the bare placeholder in a paragraph.
        for candidate in (
            '<p>APEROMERMAIDBLOCK{0}</p>'.format(index),
            'APEROMERMAIDBLOCK{0}'.format(index),
        ):
            html = html.replace(candidate, container)
    return html


def render_markdown(text: str) -> str:
    """Render markdown text to HTML without allowing raw HTML injection."""
    # Pull mermaid diagrams out before the code extensions mangle them.
    body, mermaid_blocks = _extract_mermaid(str(text or ''))
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
        output_format="html5",
    )
    md.stripTopLevelTags = False
    try:
        md.enable_attributes = False
    except Exception:
        pass
    html = md.convert(body)
    # Put the diagrams back as mermaid.js containers.
    return _restore_mermaid(html, mermaid_blocks)


def save_doc_content(doc_ref: str, version: str, content: str) -> None:
    """Save markdown content for a doc page version."""
    rel_doc_path = normalize_doc_ref(doc_ref)
    current_file, _ = _resolve_markdown_path(rel_doc_path, version)
    if current_file is not None and current_file.name == 'index.md':
        md_file = current_file
    else:
        ver_dir = DOC_ROOT / version
        md_file = ver_dir / f'{rel_doc_path}.md'
    md_file.parent.mkdir(parents=True, exist_ok=True)
    md_file.write_text(content, encoding='utf-8')
    # The edited page is served live (mtime mismatch) until the
    # background rebuild also refreshes sidebars and the search index.
    request_snapshot_refresh()


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
# Prebuilt documentation snapshots
# =============================================================================
def _content_mtime(md_file: Path, version: Optional[str]) -> int:
    """Return the render-relevant mtime of a page.

    Every page's HTML may include glossary tooltip spans, so editing
    ``glossary.yaml`` must invalidate every page, not just the glossary.

    :param md_file: Path, markdown source of the page
    :param version: str or None, documentation version

    :return: int, the newest mtime (ns) of the page and the glossary
    """
    mtime_ns = md_file.stat().st_mtime_ns
    glossary_path = _resolve_glossary_path(version)
    if glossary_path is not None:
        mtime_ns = max(mtime_ns, glossary_path.stat().st_mtime_ns)
    return mtime_ns


def set_snapshot_dir(data_dir: Union[str, Path]) -> Path:
    """Set where prebuilt snapshots are persisted.

    :param data_dir: str or Path, the ARI data directory (e.g. ``~/.ari``)

    :return: Path, the snapshot directory (``<data_dir>/docs_cache``)
    """
    path = Path(data_dir).expanduser() / _SNAPSHOT_DIR_NAME
    with _SNAPSHOT_LOCK:
        _SNAPSHOT_STATE['dir'] = path
    return path


def _snapshot_path(version: str) -> Optional[Path]:
    """Return the on-disk snapshot file for a version, if configured."""
    base_dir = _SNAPSHOT_STATE.get('dir')
    if base_dir is None:
        return None
    safe = re.sub(r'[^\w.\-]', '_', str(version))
    return Path(base_dir) / '{0}.json'.format(safe)


def _install_snapshot(snapshot: dict, file_mtime: Optional[int]) -> None:
    """Make a snapshot the one served to requests for its version."""
    version = str(snapshot['version'])
    with _SNAPSHOT_LOCK:
        _SNAPSHOTS[version] = snapshot
        if file_mtime is not None:
            _SNAPSHOT_FILE_MTIME[version] = file_mtime


def load_snapshot(version: str) -> Optional[dict]:
    """Load (and install) a persisted snapshot for one version.

    :param version: str, documentation version id

    :return: dict snapshot, or None if missing, unreadable, or written
        by an incompatible schema
    """
    path = _snapshot_path(version)
    if path is None or not path.is_file():
        return None
    try:
        file_mtime = path.stat().st_mtime_ns
        with open(path, 'r', encoding='utf-8') as fio:
            snapshot = json.load(fio)
    except (OSError, ValueError) as exc:
        LOGGER.warning('Ignoring unreadable docs snapshot %s: %s',
                       path, exc)
        return None
    if not isinstance(snapshot, dict):
        return None
    if snapshot.get('schema') != _SNAPSHOT_SCHEMA:
        return None
    if str(snapshot.get('version')) != str(version):
        return None
    _install_snapshot(snapshot, file_mtime)
    return snapshot


def _active_snapshot(version: Optional[str]) -> Optional[dict]:
    """Return the in-memory snapshot to serve for a version.

    At most every few seconds the persisted file is stat'ed so a
    snapshot rebuilt by another process (or a standalone task run) is
    picked up without restarting the server.

    :param version: str or None, documentation version id

    :return: dict snapshot, or None when none is available (callers
        then fall back to building from source)
    """
    if not version or getattr(_SNAPSHOT_LOCAL, 'bypass', False):
        return None
    key = str(version)
    now = time.monotonic()
    with _SNAPSHOT_LOCK:
        snapshot = _SNAPSHOTS.get(key)
        last_check = _SNAPSHOT_CHECKED.get(key, 0.0)
        due = now - last_check >= _SNAPSHOT_RELOAD_CHECK_S
        if due:
            _SNAPSHOT_CHECKED[key] = now
    if not due:
        return snapshot
    path = _snapshot_path(key)
    try:
        file_mtime = path.stat().st_mtime_ns if path is not None else None
    except OSError:
        file_mtime = None
    known_mtime = _SNAPSHOT_FILE_MTIME.get(key)
    if file_mtime is not None and file_mtime != known_mtime:
        loaded = load_snapshot(key)
        if loaded is not None:
            snapshot = loaded
    return snapshot


def _snapshot_page(doc_ref: str, version: Optional[str]) -> Optional[dict]:
    """Return a prebuilt page if its source has not changed since.

    The single stat keeps edits (in the ARI editor or on disk) visible
    immediately; a stale page falls back to the live render.

    :param doc_ref: str, doc ref (any accepted form)
    :param version: str or None, documentation version id

    :return: dict page entry, or None when not prebuilt or stale
    """
    if not version:
        version = get_default_version()
    snapshot = _active_snapshot(version)
    if snapshot is None:
        return None
    page = snapshot['pages'].get(normalize_doc_ref(doc_ref))
    if page is None:
        return None
    try:
        mtime_ns = _content_mtime(Path(page['path']), page['version'])
    except OSError:
        return None
    if mtime_ns != page['mtime']:
        return None
    return page


def compute_fingerprint(version: str) -> str:
    """Fingerprint every source a version's snapshot is built from.

    Covers all files under ``all/`` and ``{version}/``, ``versions.yaml``
    and this renderer module, using (path, mtime, size) only, so it is
    cheap enough to run on a schedule.

    :param version: str, documentation version id

    :return: str, hex digest
    """
    digest = hashlib.sha1()
    digest.update('schema={0}\n'.format(_SNAPSHOT_SCHEMA).encode())
    sources = [VERSIONS_FILE, Path(__file__)]
    for root in (DOC_ROOT / 'all', DOC_ROOT / version):
        for dirpath, dirnames, filenames in os.walk(root):
            # Sort in place so os.walk visits directories deterministically.
            dirnames[:] = sorted(
                name for name in dirnames if not name.startswith('.'))
            for name in sorted(filenames):
                if not name.startswith('.'):
                    sources.append(Path(dirpath) / name)
    for path in sources:
        try:
            stat = path.stat()
        except OSError:
            continue
        line = '{0}|{1}|{2}\n'.format(path, stat.st_mtime_ns, stat.st_size)
        digest.update(line.encode('utf-8'))
    return digest.hexdigest()


def build_snapshot(version: str) -> dict:
    """Render every page, child listing and the search index for a version.

    Runs entirely from source (the active snapshot is bypassed for the
    calling thread), so it is safe to call while requests are being
    served from the previous snapshot.

    :param version: str, documentation version id

    :return: dict snapshot ready for ``_install_snapshot``
    """
    _SNAPSHOT_LOCAL.bypass = True
    try:
        fingerprint = compute_fingerprint(version)
        tree = get_doc_sidebar_tree('home/docs', version)
        root_children = _get_doc_children('home/docs', version)
        children = {'home/docs': root_children}
        refs = ['home/docs']
        for item in tree:
            ref = normalize_doc_ref(item.get('rel_path') or '')
            refs.append(ref)
            if item.get('kind') == 'dir':
                children[ref] = _get_doc_children(ref, version)
        pages = dict()
        for ref in refs:
            md_file, page_version = _resolve_markdown_path(ref, version)
            if md_file is None or ref in pages:
                continue
            raw, html, _, meta = get_doc_content(ref, version)
            pages[ref] = dict(
                path=str(md_file),
                version=page_version,
                mtime=_content_mtime(md_file, page_version),
                raw=raw,
                html=html,
                meta=meta,
            )
        search_index = get_search_index(version)
    finally:
        _SNAPSHOT_LOCAL.bypass = False
    snapshot = dict(
        schema=_SNAPSHOT_SCHEMA,
        version=version,
        fingerprint=fingerprint,
        built_at=datetime.now(timezone.utc).isoformat(),
        pages=pages,
        children=children,
        search_index=search_index,
    )
    # Round-trip through JSON so served and persisted copies match
    # (e.g. YAML dates in front matter become strings either way).
    return json.loads(json.dumps(snapshot, default=str))


def _write_snapshot(snapshot: dict) -> Optional[int]:
    """Persist a snapshot atomically.

    :param snapshot: dict, snapshot from ``build_snapshot``

    :return: int or None, mtime of the snapshot file now on disk (the
        old one if writing failed, so it is not re-loaded over the new
        in-memory snapshot), or None when there is no file
    """
    path = _snapshot_path(snapshot['version'])
    if path is None:
        return None
    tmp_path = path.with_name(path.name + '.tmp')
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as fio:
            json.dump(snapshot, fio)
        os.replace(tmp_path, path)
    except OSError as exc:
        LOGGER.warning('Could not persist docs snapshot %s: %s', path, exc)
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


def refresh_snapshots(force: bool = False,
                      logger: Any = None) -> Dict[str, str]:
    """Rebuild any version snapshot whose sources changed.

    :param force: bool, rebuild even when the fingerprint matches
    :param logger: callable or None, receives one progress line per
        version

    :return: dict mapping version id to a short status string
    """
    statuses = dict()
    # Serialise builds: the startup thread, the async task and editor
    # saves may all ask for a refresh at once.
    with _SNAPSHOT_REFRESH_LOCK:
        for item in get_versions():
            version = str(item.get('id') or '')
            if not version:
                continue
            current = _SNAPSHOTS.get(version) or load_snapshot(version)
            fingerprint = compute_fingerprint(version)
            if (not force and current is not None
                    and current.get('fingerprint') == fingerprint):
                statuses[version] = 'up to date'
            else:
                start = time.monotonic()
                snapshot = build_snapshot(version)
                file_mtime = _write_snapshot(snapshot)
                _install_snapshot(snapshot, file_mtime)
                statuses[version] = 'rebuilt {0} pages in {1:.1f}s'.format(
                    len(snapshot['pages']), time.monotonic() - start)
            if callable(logger):
                logger('docs {0}: {1}'.format(version, statuses[version]))
    return statuses


def _snapshot_worker() -> None:
    """Run refreshes until no further refresh has been requested."""
    while _SNAPSHOT_PENDING.is_set():
        _SNAPSHOT_PENDING.clear()
        try:
            refresh_snapshots()
        except Exception:  # noqa: BLE001
            LOGGER.exception('Documentation snapshot refresh failed')


def request_snapshot_refresh() -> None:
    """Refresh snapshots in a daemon thread without blocking the caller."""
    _SNAPSHOT_PENDING.set()
    with _SNAPSHOT_LOCK:
        worker = _SNAPSHOT_STATE.get('thread')
        if worker is not None and worker.is_alive():
            return
        worker = threading.Thread(target=_snapshot_worker,
                                  name='ari-docs-snapshot', daemon=True)
        _SNAPSHOT_STATE['thread'] = worker
    worker.start()


def start_snapshot_service(data_dir: Union[str, Path]) -> None:
    """Load persisted snapshots and rebuild stale ones in the background.

    :param data_dir: str or Path, the ARI data directory

    :return: None
    """
    set_snapshot_dir(data_dir)
    request_snapshot_refresh()


def get_search_index_json(version: Optional[str] = None) -> Tuple[str, str]:
    """Return the search index as serialised JSON plus an ETag.

    With a snapshot the serialisation is done once per snapshot, so the
    (large) index is served without re-encoding on every request.

    :param version: str or None, documentation version id

    :return: tuple, 1. JSON text ``{"items": [...]}``, 2. ETag string
    """
    if not version:
        version = get_default_version()
    snapshot = _active_snapshot(version)
    if snapshot is not None:
        cached = snapshot.get('_search_json')
        if cached is None:
            text = json.dumps(dict(items=snapshot['search_index']))
            cached = (text, snapshot['fingerprint'][:20])
            snapshot['_search_json'] = cached
        return cached
    text = json.dumps(dict(items=get_search_index(version)))
    return text, hashlib.sha1(text.encode('utf-8')).hexdigest()[:20]


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
