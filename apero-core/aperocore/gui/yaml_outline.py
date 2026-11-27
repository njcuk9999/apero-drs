#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comment preserving yaml outlines for browser gui editors

Parses yaml text line by line (no yaml library round trip) into an
outline of its keys - with the comment block written above each key, the
section banners ("# ==== / # Title / # ====") and the key's nesting path -
so a gui can show a form of the parameters. Edits are applied back onto
the original text by replacing only the value text of the edited lines,
so every comment, blank line and the key order are kept exactly.

Supported (editable) values:

    - scalars on the key line:      KEY: value  # comment
    - block lists below a key:      KEY:\\n  - item1\\n  - item2

A whole key can also be rewritten as a mapping of scalars / block lists
(e.g. switching "FILE: name.fits" to "FILE:\n  filelist: ...\n  source:
mast\n  ...") - see apply_edits. Anything else (block scalars) is shown
but edited in the raw text instead.

Created on 2026-11-26

@author: cook
"""
import re
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.yaml_outline.py'
# a mapping key line: indent, key, rest of the line
KEY_RE = re.compile(r'^(\s*)([^\s#][^:#]*?|"[^"]*"|\'[^\']*\'):(?:\s+|$)(.*)$')
# a block list item line: indent, item text
ITEM_RE = re.compile(r'^(\s*)-(?:\s+(.*))?$')
# a section separator comment line (# ===== or # -----)
SEPARATOR_RE = re.compile(r'^#\s*[-=]{5,}\s*$')
# a decoration-only comment line (e.g. # ########)
DECORATION_RE = re.compile(r'^#[\s#*~]*$')


# =============================================================================
# Define functions
# =============================================================================
def split_comment(rest: str) -> Tuple[str, str]:
    """
    Split the value text and the inline comment of a line (a "#" inside
    quotes is not a comment)

    :param rest: str, the text after "KEY:"

    :return: tuple, (value text, comment text without the "#")
    """
    quote = None
    for index, char in enumerate(rest):
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in ['"', "'"]:
            quote = char
        elif char == '#' and (index == 0 or rest[index - 1] in ' \t'):
            return rest[:index].rstrip(), rest[index + 1:].strip()
    return rest.rstrip(), ''


def _scalar_type(text: str) -> str:
    """
    Classify a yaml scalar (for the editor widget)

    :param text: str, the raw value text

    :return: str, one of bool, null, int, float, str, flow
    """
    if text.startswith('[') or text.startswith('{'):
        return 'flow'
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError:
        return 'str'
    if isinstance(value, bool):
        return 'bool'
    if value is None:
        return 'null'
    if isinstance(value, int):
        return 'int'
    if isinstance(value, float):
        return 'float'
    return 'str'


def outline(text: str) -> Dict[str, Any]:
    """
    Build the outline of yaml text

    :param text: str, the yaml text

    :return: dict(nodes, error, header) - nodes is a list (file order) of
             dict(line, indent, depth, key, path, kind, value, vtype,
             inline, comment, section, items, end) where line is 0-based,
             kind is scalar/list/map/block, items the list item texts and
             end the last line (0-based) that belongs to the node; error is
             the yaml parse error (or None); header holds the comment lines
             at the top of the file
    """
    lines = text.splitlines()
    # check the text is valid yaml at all
    error = None
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as yaml_error:
        error = str(yaml_error)
    nodes: List[Dict[str, Any]] = []
    # the stack of (indent, key) of open parent keys
    stack: List[Tuple[int, str]] = []
    comments: List[str] = []
    section: Optional[str] = None
    in_banner = False
    header: List[str] = []
    seen_key = False
    current: Optional[Dict[str, Any]] = None
    for lno, line in enumerate(lines):
        stripped = line.strip()
        # ---------------------------------------------------------------------
        # comment lines: banners name sections, others describe the next key
        if stripped.startswith('#'):
            if SEPARATOR_RE.match(stripped):
                in_banner = not in_banner
                if in_banner:
                    section = None
                comments = []
                continue
            # decoration lines (# #######) carry no text
            if DECORATION_RE.match(stripped):
                continue
            body = stripped.lstrip('#').strip()
            if not seen_key and not in_banner:
                header.append(body)
            if in_banner:
                # the first banner line is the section title
                if body and section is None:
                    section = body
                continue
            if body:
                comments.append(body)
            continue
        # blank lines may sit inside a banner (keep its state)
        if stripped == '':
            continue
        in_banner = False
        # ---------------------------------------------------------------------
        # block list items belong to the previous key
        item = ITEM_RE.match(line)
        if item is not None and current is not None:
            if current['kind'] in ['map', 'list'] and not current['value']:
                current['kind'] = 'list'
                current['vtype'] = 'list'
                current['items'].append((item.group(2) or '').rstrip())
                current['item_lines'].append(lno)
                current['item_indent'] = len(item.group(1))
                current['end'] = lno
            continue
        # ---------------------------------------------------------------------
        match = KEY_RE.match(line)
        if match is None:
            # continuation of a block scalar or something unsupported
            if current is not None:
                current['end'] = lno
                if current['kind'] == 'map' and not current['value']:
                    current['kind'] = 'block'
            continue
        seen_key = True
        indent = len(match.group(1))
        key = match.group(2).strip().strip('"\'')
        value, inline = split_comment(match.group(3))
        # close parents at the same or deeper indent
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = [entry[1] for entry in stack] + [key]
        # a key without a value opens a map (or a block list)
        if value == '':
            kind = 'map'
        elif value[:1] in ['|', '>']:
            kind = 'block'
        else:
            kind = 'scalar'
        node = dict(line=lno, indent=indent, depth=len(stack), key=key,
                    path=path, kind=kind, value=value,
                    vtype=_scalar_type(value) if kind == 'scalar' else kind,
                    inline=inline, comment=' '.join(comments),
                    section=section, items=[], item_lines=[],
                    item_indent=None, end=lno)
        # the section only labels the first key after its banner
        section = None
        comments = []
        nodes.append(node)
        current = node
        if kind == 'map':
            stack.append((indent, key))
    # maps that got no children are empty values
    for node in nodes:
        if node['kind'] == 'map':
            has_child = any(other['depth'] > node['depth']
                            and other['line'] > node['line']
                            and other['path'][:len(node['path'])]
                            == node['path'] for other in nodes)
            if not has_child:
                node['kind'] = 'scalar'
                node['vtype'] = 'null'
    return dict(nodes=nodes, error=error, header=header)


def _format_line(line: str, new_value: str) -> str:
    """
    Replace the value of a "KEY: value  # comment" line

    :param line: str, the original line
    :param new_value: str, the new raw value text

    :return: str, the new line (indent, key and inline comment kept)
    """
    match = KEY_RE.match(line)
    if match is None:
        return line
    _, inline = split_comment(match.group(3))
    head = line[:match.start(3)].rstrip()
    new_line = '{0} {1}'.format(head, new_value) if new_value != '' else head
    if inline:
        new_line += '  # ' + inline
    return new_line


def _subtree_end(nodes: List[Dict[str, Any]], node: Dict[str, Any]) -> int:
    """
    Get the last line of a node including all of its child keys

    :param nodes: list of dict, the outline nodes
    :param node: dict, the node

    :return: int, the last line (0-based)
    """
    end = node['end']
    size = len(node['path'])
    for other in nodes:
        if (other['line'] > node['line'] and len(other['path']) > size
                and other['path'][:size] == node['path']):
            end = max(end, other['end'])
    return end


def _mapping_lines(nodes: List[Dict[str, Any]], node: Dict[str, Any],
                   key_line: str, mapping: List[Dict[str, Any]]
                   ) -> List[str]:
    """
    Write a key as a mapping (the key line keeps its inline comment)

    :param nodes: list of dict, the outline nodes
    :param node: dict, the node being rewritten
    :param key_line: str, the original key line
    :param mapping: list of dict(key, value=raw text) or dict(key,
                    items=list of raw item texts) in output order

    :return: list of str, the new lines
    """
    # keep the child indent of an existing mapping (else two more spaces)
    indent = node['indent'] + 2
    for other in nodes:
        if (other['line'] > node['line']
                and other['path'][:-1] == node['path']):
            indent = other['indent']
            break
    pad = ' ' * indent
    new_lines = [_format_line(key_line, '')]
    for entry in mapping:
        sub_key = str(entry.get('key', '')).strip()
        if not sub_key:
            continue
        if entry.get('items') is not None:
            items = [str(item) for item in entry['items']]
            if len(items) == 0:
                new_lines.append('{0}{1}:'.format(pad, sub_key))
                continue
            new_lines.append('{0}{1}:'.format(pad, sub_key))
            new_lines += ['{0}- {1}'.format(pad, item) for item in items]
            continue
        value = str(entry.get('value', '') or '').strip()
        new_lines.append(('{0}{1}: {2}' if value else '{0}{1}:').format(
            pad, sub_key, value))
    return new_lines


def apply_edits(text: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply value edits to yaml text (comments and layout preserved)

    :param text: str, the original yaml text
    :param edits: list of dict(line, key, value) for scalars,
                  dict(line, key, items=list of str) for block lists or
                  dict(line, key, mapping=list of dict(key, value | items))
                  to rewrite the key (and all its child keys) as a mapping;
                  line is the 0-based key line from outline() and key is
                  checked against that line (stale edits are refused).
                  Edits must not overlap (e.g. a mapping edit and an edit
                  of one of its children).

    :return: dict(text, errors, applied) - text is the new yaml text,
             errors lists refused edits / a yaml parse error of the result
    """
    lines = text.splitlines()
    trailing = text.endswith('\n')
    nodes = outline(text)['nodes']
    info = {node['line']: node for node in nodes}
    errors: List[str] = []
    # apply from the bottom up so list edits do not shift earlier lines
    replacements: List[Tuple[int, int, List[str]]] = []
    for edit in edits:
        try:
            lno = int(edit.get('line'))
        except (TypeError, ValueError):
            errors.append('invalid edit: {0}'.format(edit))
            continue
        node = info.get(lno)
        if node is None or node['key'] != str(edit.get('key')):
            errors.append('line {0} is no longer key {1} - reload'.format(
                lno + 1, edit.get('key')))
            continue
        if isinstance(edit.get('mapping'), list):
            if node['kind'] == 'block':
                errors.append('{0} cannot be edited here (use the raw '
                              'view)'.format(node['key']))
                continue
            replacements.append((lno, _subtree_end(nodes, node),
                                 _mapping_lines(nodes, node, lines[lno],
                                                edit['mapping'])))
            continue
        if 'items' in edit and edit['items'] is not None:
            items = [str(item) for item in edit['items']]
            if node['kind'] != 'list' and not (node['kind'] == 'scalar'
                                               and node['vtype'] == 'null'):
                errors.append('{0} is not a list'.format(node['key']))
                continue
            indent = node['item_indent']
            if indent is None:
                indent = node['indent']
            new_lines = [_format_line(lines[lno], '')]
            new_lines += ['{0}- {1}'.format(' ' * indent, item)
                          for item in items]
            # an empty list is written as a flow list
            if len(items) == 0:
                new_lines = [_format_line(lines[lno], '[]')]
            replacements.append((lno, node['end'], new_lines))
            continue
        if node['kind'] != 'scalar':
            errors.append('{0} cannot be edited here (use the raw '
                          'view)'.format(node['key']))
            continue
        value = str(edit.get('value', '')).strip()
        replacements.append((lno, lno, [_format_line(lines[lno], value)]))
    for start, end, new_lines in sorted(replacements, reverse=True):
        lines[start:end + 1] = new_lines
    new_text = '\n'.join(lines) + ('\n' if trailing else '')
    try:
        yaml.safe_load(new_text)
    except yaml.YAMLError as yaml_error:
        errors.append('the edited yaml does not parse: {0}'.format(
            yaml_error))
    return dict(text=new_text, errors=errors,
                applied=len(replacements))


# =============================================================================
# End of code
# =============================================================================
