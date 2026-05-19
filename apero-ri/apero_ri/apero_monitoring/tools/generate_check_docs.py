#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate markdown documentation pages for APERO checks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

from apero_ri.apero_monitoring import CHECKS


DEFAULT_DOCS_DIR = (
    Path(__file__).resolve().parents[4]
    / 'documentation'
    / 'ari'
    / 'all'
    / 'home'
    / 'docs'
    / 'monitor'
    / 'checks'
)


def _doc_filename(check_key: str) -> str:
    """Return the markdown filename for one check key."""
    return f'{str(check_key).strip().lower()}.md'


def _contact_anchor(contact_key: str) -> str:
    """Return a markdown anchor id for one contact section key."""
    text = str(contact_key).strip().lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return f'contact-list-{text}'


def _replace_contact_refs(text: str, contact_keys: List[str]) -> str:
    """Replace <CONTACT:KEY> tags with links to contact sections."""
    out = str(text or '')
    for key in contact_keys:
        token = f'<CONTACT:{key}>'
        label = f'Contact list {key}'
        anchor = _contact_anchor(key)
        out = out.replace(token, f'[{label}](#{anchor})')
    return out


def _requirements_lines(check_key: str,
                        dependencies: List[str],
                        key_to_file: Dict[str, str]) -> List[str]:
    """Build markdown lines for the Requirements section."""
    lines = ['## Requirements', '']
    deps = [str(dep).strip() for dep in dependencies if str(dep).strip()]
    if len(deps) == 0:
        lines.append('No dependencies.')
        lines.append('')
        return lines

    for dep in deps:
        dep_file = key_to_file.get(dep, _doc_filename(dep))
        dep_link = f'checks/{dep_file}'
        lines.append(f'- [{dep}]({dep_link})')
    lines.append('')
    return lines


def _contact_lines(contact_list: Dict[object, object]) -> List[str]:
    """Build markdown lines for contact sections and tables."""
    lines = ['## Contact', '']
    if not isinstance(contact_list, dict) or len(contact_list) == 0:
        lines.append('No contacts.')
        lines.append('')
        return lines

    emitted = 0
    for key, clist in contact_list.items():
        names = list(getattr(clist, 'contact_names', []) or [])
        emails = list(getattr(clist, 'contact_emails', []) or [])
        starred = set(getattr(clist, 'starred', []) or [])
        if len(names) == 0:
            continue

        if key is not None:
            key_text = str(key).strip()
            anchor = _contact_anchor(key_text)
            lines.append(f'### Contact list {key_text}')
            lines.append(f'<a id="{anchor}"></a>')
            lines.append('')

        lines.append('| Name | Email |')
        lines.append('| --- | --- |')
        for idx, name in enumerate(names):
            email = emails[idx] if idx < len(emails) else ''
            marker = ' *' if str(name) in starred else ''
            lines.append(f'| {name}{marker} | {email} |')
        lines.append('')
        emitted += 1

    if emitted == 0:
        lines.append('No contacts.')
        lines.append('')
    return lines


def _check_page(check_key: str,
                check_obj: object,
                key_to_file: Dict[str, str]) -> str:
    """Build markdown content for one check."""
    check_type = str(getattr(check_obj, 'check_type', '') or '')
    human = str(getattr(check_obj, 'string_name', check_key) or check_key)
    description = str(getattr(check_obj, 'description', '') or '').strip()
    what_to_do = str(getattr(check_obj, 'what_to_do', '') or '').strip()
    dependencies = list(getattr(check_obj, 'dependencies', []) or [])
    contact_list = dict(getattr(check_obj, 'contact_list', {}) or {})

    contact_keys = []
    for key in contact_list:
        if key is None:
            continue
        contact_keys.append(str(key).strip())

    description = _replace_contact_refs(description, contact_keys)
    what_to_do = _replace_contact_refs(what_to_do, contact_keys)

    lines = []
    lines.append(f'# {check_type}: {human}')
    lines.append('')
    lines.append('## Overview')
    lines.append('')
    lines.append(description if description else 'No overview available.')
    lines.append('')
    lines.extend(_requirements_lines(check_key, dependencies, key_to_file))
    lines.append('## What to do')
    lines.append('')
    lines.append(what_to_do if what_to_do else 'No instructions provided.')
    lines.append('')
    lines.extend(_contact_lines(contact_list))
    return '\n'.join(lines).rstrip() + '\n'


def generate_check_docs(output_dir: Path) -> Tuple[int, List[Path]]:
    """Generate one markdown file per check in output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    key_to_file = dict()
    for check_key in CHECKS:
        key_to_file[str(check_key)] = _doc_filename(str(check_key))

    written = []
    for check_key, check_obj in CHECKS.items():
        filename = _doc_filename(str(check_key))
        content = _check_page(str(check_key), check_obj, key_to_file)
        out_path = output_dir / filename
        out_path.write_text(content, encoding='utf-8')
        written.append(out_path)

    return len(written), written


def main() -> None:
    """Run the checks-doc generator CLI."""
    parser = argparse.ArgumentParser(
        description='Generate markdown docs for APERO checks.',
    )
    parser.add_argument(
        '--output-dir',
        default=str(DEFAULT_DOCS_DIR),
        help='Output directory for generated markdown files.',
    )
    args = parser.parse_args()

    output_dir = Path(str(args.output_dir)).expanduser().resolve()
    count, files = generate_check_docs(output_dir)
    print(
        f'Generated {count} check docs in {output_dir} '
        f'(first={files[0] if files else "none"}).'
    )


if __name__ == '__main__':
    main()