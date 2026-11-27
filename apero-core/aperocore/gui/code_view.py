#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Show python source code in a browser gui (read only)

Two lookups:

    find_function('pkg.module.func')         a function / class / method
    find_function('pkg.module.Class.method')   (source + docstring)
    read_block('/path/file.py', 120)         the code starting at a line
                                             (e.g. where a progress step
                                             is marked or called)

Functions are found by parsing the file (ast) - nothing is imported, so
the code shown is always the current code on disk and looking it up has no
side effects. Only .py files below a directory of the python path
(sys.path) or inside an importable package (e.g. an editable install) are
read.

Created on 2026-11-26

@author: cook
"""
import ast
import importlib.util
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.code_view.py'
# the most lines returned for one block / function
MAX_LINES = 400
# lines of comments shown above the start of a block
CONTEXT_ABOVE = 4
# a line that starts the next marked step (ends a marked block)
NEXT_MARK_RE = re.compile(r'progress\.(mark|end|start)\(')
# the most parent directories checked for an importable package
MAX_PACKAGE_DEPTH = 8
# a valid dotted python path
DOTTED_RE = re.compile(r'^[A-Za-z_][\w]*(\.[A-Za-z_][\w]*)*$')


# =============================================================================
# Define functions
# =============================================================================
def _python_roots() -> List[str]:
    """
    Get the directories of the python path (the only places code is read)

    :return: list of str, real directory paths
    """
    roots = []
    # the working directory is on the path of "python -m" programs - it is
    #   not code (an importable package inside it is still found below)
    cwd = os.path.realpath(os.getcwd())
    for entry in sys.path:
        if not entry or not os.path.isdir(entry):
            continue
        real = os.path.realpath(entry)
        # never allow the whole file system (or the working directory)
        if real not in [os.path.sep, cwd] and real not in roots:
            roots.append(real)
    return roots


def _in_package(real: str) -> bool:
    """
    Whether a file belongs to an importable package (e.g. an editable
    install found through an import hook rather than sys.path): one of its
    parent directories must be where python imports a top level package
    of that name from (sub packages may be namespace packages without an
    __init__.py)

    :param real: str, the real file path

    :return: bool, True if it is part of an importable package
    """
    directory = os.path.dirname(real)
    for _ in range(MAX_PACKAGE_DEPTH):
        name = os.path.basename(directory)
        if not name.isidentifier():
            return False
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            spec = None
        if spec is not None:
            locations = [os.path.realpath(location) for location in
                         (spec.submodule_search_locations or [])]
            if directory in locations:
                return True
        parent = os.path.dirname(directory)
        if parent == directory:
            return False
        directory = parent
    return False


def allowed_file(path: str) -> bool:
    """
    Whether a file may be shown: a .py file below the python path or
    part of an importable package

    :param path: str, the file path

    :return: bool, True if it may be read
    """
    real = os.path.realpath(str(path))
    if not real.endswith('.py') or not os.path.isfile(real):
        return False
    if any(real.startswith(root + os.path.sep)
           for root in _python_roots()):
        return True
    return _in_package(real)


def _module_file(parts: List[str]) -> Optional[str]:
    """
    Find the file of a module without importing it (or its parents)

    :param parts: list of str, the dotted module path split on dots

    :return: str or None, the .py file
    """
    try:
        spec = importlib.util.find_spec(parts[0])
    except (ImportError, ValueError):
        return None
    if spec is None:
        return None
    # a plain top level module
    if len(parts) == 1:
        if spec.origin and spec.origin.endswith('.py'):
            return spec.origin
        return None
    # walk the package directories for the sub modules
    dirs = list(spec.submodule_search_locations or [])
    for it, part in enumerate(parts[1:], start=1):
        last = it == len(parts) - 1
        found = None
        for directory in dirs:
            package = os.path.join(directory, part)
            if last and os.path.isfile(package + '.py'):
                return package + '.py'
            # a package (a directory without __init__.py is a namespace
            #   package)
            if os.path.isdir(package):
                found = package
                break
        if found is None:
            return None
        if last:
            init = os.path.join(found, '__init__.py')
            return init if os.path.isfile(init) else None
        dirs = [found]
    return None


def _split_dotted(dotted: str) -> Optional[Tuple[str, List[str]]]:
    """
    Split a dotted path into its module file and the attribute path inside
    it (the longest module prefix wins)

    :param dotted: str, e.g. pkg.module.Class.method

    :return: tuple (file, attribute names) or None
    """
    parts = dotted.split('.')
    for cut in range(len(parts), 0, -1):
        path = _module_file(parts[:cut])
        if path is not None:
            return path, parts[cut:]
    return None


def _find_def(tree: ast.AST, names: List[str]) -> Optional[ast.AST]:
    """
    Find a (nested) function / class definition in a module tree

    :param tree: ast.Module, the parsed module
    :param names: list of str, e.g. ['Class', 'method']

    :return: the definition node or None
    """
    current: Any = tree
    for name in names:
        found = None
        for child in getattr(current, 'body', []):
            if (isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef))
                    and child.name == name):
                found = child
        if found is None:
            return None
        current = found
    return current


def _numbered(lines: List[str], start: int, end: int
              ) -> List[List[Any]]:
    """
    Get numbered lines (1-based, inclusive range, capped at MAX_LINES)

    :param lines: list of str, the file lines
    :param start: int, the first line (1-based)
    :param end: int, the last line (1-based)

    :return: list of [line number, text]
    """
    end = min(end, start + MAX_LINES - 1, len(lines))
    return [[number, lines[number - 1].rstrip('\n')]
            for number in range(max(start, 1), end + 1)]


def find_function(dotted: str) -> Dict[str, Any]:
    """
    Find the source and docstring of a function / class / method / module

    :param dotted: str, the dotted path (e.g. sossisse.core.io.load_fits)

    :return: dict(name, file, line, end, lines, doc, error)
    """
    out: Dict[str, Any] = dict(name=dotted, file=None, line=None, end=None,
                               lines=[], doc=None, error=None)
    if not DOTTED_RE.match(str(dotted or '')):
        out['error'] = 'not a dotted python path: {0}'.format(dotted)
        return out
    split = _split_dotted(dotted)
    if split is None:
        out['error'] = 'module not found for {0}'.format(dotted)
        return out
    path, names = split
    if not allowed_file(path):
        out['error'] = 'file is outside the python path: {0}'.format(path)
        return out
    with open(path, 'r', errors='replace') as pfile:
        text = pfile.read()
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        out['error'] = 'cannot parse {0}: {1}'.format(path, error)
        return out
    lines = text.splitlines()
    out['file'] = path
    # the whole module
    if not names:
        out.update(line=1, end=len(lines), doc=ast.get_docstring(tree),
                   lines=_numbered(lines, 1, len(lines)))
        return out
    node = _find_def(tree, names)
    if node is None:
        out['error'] = '{0} not found in {1}'.format('.'.join(names), path)
        return out
    # start at the first decorator
    start = min([node.lineno] + [dec.lineno for dec in
                                 getattr(node, 'decorator_list', [])])
    end = getattr(node, 'end_lineno', None) or node.lineno
    out.update(line=node.lineno, end=end, doc=ast.get_docstring(node),
               lines=_numbered(lines, start, end))
    return out


def _block_end(lines: List[str], line: int) -> int:
    """
    Find the last line of the code starting at a line:

        a progress mark / start   up to the next mark at the same indent
        a block opener (...:)     to the end of the indented block
        any other statement       the statement (continuation lines too)

    :param lines: list of str, the file lines
    :param line: int, the first line (1-based)

    :return: int, the last line (1-based)
    """
    first = lines[line - 1]
    stripped = first.strip()
    indent = len(first) - len(first.lstrip())
    code = stripped.split('#')[0].rstrip()
    mark = bool(NEXT_MARK_RE.search(stripped))
    opener = code.endswith(':')
    if not mark and not opener:
        # one statement: until its brackets close
        depth = 0
        for number in range(line, len(lines) + 1):
            text = lines[number - 1].split('#')[0]
            depth += sum(text.count(c) for c in '([{')
            depth -= sum(text.count(c) for c in ')]}')
            if depth <= 0:
                return number
        return line
    end = line
    for number in range(line + 1, len(lines) + 1):
        text = lines[number - 1]
        stripped = text.strip()
        if not stripped:
            continue
        this_indent = len(text) - len(text.lstrip())
        # the enclosing block ended (or this block, for an opener)
        if this_indent < indent or (opener and this_indent <= indent):
            break
        # the next marked step starts here
        if (mark and this_indent == indent
                and NEXT_MARK_RE.search(stripped)):
            break
        # trailing comments belong to the next block
        if not stripped.startswith('#'):
            end = number
    return end


def read_block(path: str, line: int) -> Dict[str, Any]:
    """
    Read the code starting at a line (see _block_end), with the comment
    lines just above it

    :param path: str, the .py file
    :param line: int, the first line (1-based)

    :return: dict(file, line, end, lines, error)
    """
    out: Dict[str, Any] = dict(file=path, line=line, end=None, lines=[],
                               error=None)
    if not allowed_file(path):
        out['error'] = 'file is outside the python path: {0}'.format(path)
        return out
    with open(path, 'r', errors='replace') as pfile:
        lines = pfile.read().splitlines()
    if line < 1 or line > len(lines):
        out['error'] = 'line {0} is not in {1}'.format(line, path)
        return out
    end = _block_end(lines, line)
    # include the comment lines just above the start
    start = line
    while (start > 1 and line - start < CONTEXT_ABOVE
           and lines[start - 2].strip().startswith('#')):
        start -= 1
    out.update(end=end, lines=_numbered(lines, start, end))
    return out


# =============================================================================
# End of code
# =============================================================================
