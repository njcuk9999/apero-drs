#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic step progress markers (for gui status pages)

Code marks where it is with nested, named steps. A program that wants a
record (e.g. pogos_run for the pogos_gui Status tab) installs a writer
with set_writer(); without a writer every call does nothing, so library
code (e.g. sossisse) can always mark its steps.

Two ways to mark steps:

    with progress.step('Linear reconstruction'):   # a block
        ...

    progress.mark('Flat field')     # sequential sections of a function:
    ...                             #   each mark ends the previous one
    progress.mark('Background')     #   (and the enclosing step ends any
    ...                             #   mark left open)

Loops whose length is only known at run time are a step with its items,
and one child step per item:

    with progress.step('Detector', items=['nrs1', 'nrs2']):
        for det in ['nrs1', 'nrs2']:
            with progress.step(det):
                ...

A plan (the steps a program will go through, declared up front so a gui
can show them as pending) is a list of nodes built with node():

    PLAN = [node('Linear reconstruction', node('Detector', loop=True,
                 children=[node('Load data'), node('Flat field')]))]

A loop node is a template: its children are repeated for every item the
code announces (step(..., items=[...])). named_node() builds a node from
module constants KEY / KEY_FUNC / KEY_DESC (the step name, the function
doing the work and its description) so a gui can show the code and the
documentation of every step.

Events written (each with the step path = list of names from the root):

    step_start   path, total, items, src_file, src_line (where the code
                 marked the step)
    step_items   path, items          (items announced after the start)
    step_end     path, status (complete / failed), error
    step_advance path, done, total, detail

Only the standard library is used and nothing here ever raises.

Created on 2026-11-26

@author: cook
"""
import ast
import contextlib
import functools
import inspect
import os
import sys
import textwrap
import threading
import time
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.progress.py'
# seconds between rate limited step_advance events
ADVANCE_INTERVAL = 2.0
# the event writer: writer(event, **fields) (None = recording is off)
_WRITER: Optional[Callable[..., None]] = None
# the open steps (outermost first): dict(name, mark, last_advance)
_STACK: List[Dict[str, Any]] = []
# guards the writer and the stack
_LOCK = threading.RLock()


# =============================================================================
# Define plan functions
# =============================================================================
def node(name: str, *children: Dict[str, Any], loop: bool = False,
         desc: Optional[str] = None, func: Optional[str] = None
         ) -> Dict[str, Any]:
    """
    Build one plan node (json friendly)

    :param name: str, the step name (must match the name the code marks)
    :param children: dict, the child nodes (in order)
    :param loop: bool, True: a template repeated for every item the code
                 announces (e.g. one per detector)
    :param desc: str or None, a description of the step (None: a gui may
                 show the docstring of func)
    :param func: str or None, the dotted path of the function doing the
                 work (e.g. pkg.module.Class.method) - a gui can show its
                 current source

    :return: dict(name, children, loop, desc, func)
    """
    return dict(name=str(name), children=list(children), loop=bool(loop),
                desc=desc, func=func)


def named_node(namespace: Dict[str, Any], key: str,
               *children: Dict[str, Any], loop: bool = False
               ) -> Dict[str, Any]:
    """
    Build a plan node from module constants named after a key:

        KEY       the step name
        KEY_FUNC  (optional) the dotted path of the function doing it
        KEY_DESC  (optional) its description (None: the gui shows the
                  docstring of KEY_FUNC)

    :param namespace: dict, the module globals holding the constants
    :param key: str, the constant name (e.g. LR_WRITE)
    :param children: dict, the child nodes (in order)
    :param loop: bool, True for a loop template

    :return: dict, the plan node
    """
    return node(namespace[key], *children, loop=loop,
                desc=namespace.get(key + '_DESC'),
                func=namespace.get(key + '_FUNC'))


def nodes(*names: str) -> List[Dict[str, Any]]:
    """
    Build plain (leaf) plan nodes from names

    :param names: str, the step names (in order)

    :return: list of dict, the nodes
    """
    return [node(name) for name in names]


# the attribute a step_method wrapper carries (its plan information)
STEP_ATTR = '_progress_step'
# the deepest nesting plan_from_calls follows
MAX_PLAN_DEPTH = 6


def step_method(namespace: Dict[str, Any], key: str,
                label_arg: Optional[int] = None) -> Callable[[Any], Any]:
    """
    Decorate a method (or function) so every call is recorded as a step
    named by module constants (see named_node): KEY is the step name,
    KEY_DESC its description and KEY_FUNC the function shown as its code
    (default: the decorated function itself)

    Steps called inside the decorated function nest below it. The plan of
    a method calling decorated methods can be read from its source with
    plan_from_calls().

    :param namespace: dict, the module globals holding the constants
    :param key: str, the constant name (e.g. TS_LINEARITY)
    :param label_arg: int or None, the position of a call argument (after
                      self) added to the name when it is a string, e.g.
                      save_outputs('_rateints.fits') ->
                      "Save outputs (_rateints.fits)" - for steps called
                      several times

    :return: the decorator
    """
    name = str(namespace[key])

    def _decorator(func: Any) -> Any:
        dotted = namespace.get(key + '_FUNC') or '{0}.{1}'.format(
            func.__module__, func.__qualname__)
        info = dict(name=name, desc=namespace.get(key + '_DESC'),
                    func=dotted, label_arg=label_arg)

        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            if _WRITER is None:
                return func(*args, **kwargs)
            # args[0] is self for methods
            label = step_label(name, label_arg, list(args[1:]))
            with step(label):
                return func(*args, **kwargs)

        setattr(_wrapper, STEP_ATTR, info)
        return _wrapper

    return _decorator


def step_label(name: str, label_arg: Optional[int],
               args: List[Any]) -> str:
    """
    Get the step name of one call of a step_method

    :param name: str, the step name
    :param label_arg: int or None, the argument added to the name
    :param args: list, the call arguments (without self)

    :return: str, the step name
    """
    if label_arg is None or label_arg >= len(args):
        return name
    if not isinstance(args[label_arg], str):
        return name
    return '{0} ({1})'.format(name, args[label_arg])


def plan_from_calls(cls: Any, method: str, depth: int = 0
                    ) -> List[Dict[str, Any]]:
    """
    Build a plan from the source of a method: every call of a step_method
    on self (self.x(...)), in source order - calls inside those methods
    become their children. Commented out calls are not code, so they never
    appear.

    :param cls: class, the class whose method is read (its overrides are
                used for the called methods)
    :param method: str, the method name (e.g. process)
    :param depth: int, the current nesting (internal)

    :return: list of dict, plan nodes (named_node format)
    """
    func = inspect.unwrap(getattr(cls, method, None))
    if func is None or depth > MAX_PLAN_DEPTH:
        return []
    try:
        source = textwrap.dedent(inspect.getsource(func))
        tree = ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return []
    calls = []
    for item in ast.walk(tree):
        if (isinstance(item, ast.Call)
                and isinstance(item.func, ast.Attribute)
                and isinstance(item.func.value, ast.Name)
                and item.func.value.id == 'self'):
            calls.append(item)
    # source order (ast.walk is breadth first)
    calls.sort(key=lambda call: (call.lineno, call.col_offset))
    plan = []
    for call in calls:
        target = getattr(cls, call.func.attr, None)
        info = getattr(target, STEP_ATTR, None)
        if info is None:
            continue
        # the label argument when it is written as a constant
        args = [arg.value if isinstance(arg, ast.Constant) else None
                for arg in call.args]
        label = step_label(info['name'], info['label_arg'], args)
        children = plan_from_calls(cls, call.func.attr, depth + 1)
        plan.append(node(label, *children, desc=info['desc'],
                         func=info['func']))
    return plan


# =============================================================================
# Define recording functions
# =============================================================================
def set_writer(writer: Optional[Callable[..., None]]) -> None:
    """
    Install (or remove with None) the event writer and forget open steps

    :param writer: callable(event, **fields) or None

    :return: None
    """
    global _WRITER
    with _LOCK:
        _WRITER = writer
        del _STACK[:]


def active() -> bool:
    """
    Whether steps are being recorded

    :return: bool, True when a writer is installed
    """
    return _WRITER is not None


def current_path() -> List[str]:
    """
    Get the path of the innermost open step

    :return: list of str, the step names from the root
    """
    with _LOCK:
        return [frame['name'] for frame in _STACK]


def _write(event: str, **fields: Any) -> None:
    """
    Write one event (never raises)

    :param event: str, the event name
    :param fields: the event values

    :return: None
    """
    writer = _WRITER
    if writer is None:
        return
    try:
        writer(event, **fields)
    except Exception:
        return


def _push(name: str, mark: bool, total: Optional[int],
          items: Optional[List[Any]]) -> None:
    """
    Open a step (write step_start)

    :param name: str, the step name
    :param mark: bool, True for a mark (ended by the next mark)
    :param total: int or None, the number of things it will process
    :param items: list or None, the loop items (child step names)

    :return: None
    """
    _STACK.append(dict(name=str(name), mark=mark, last_advance=0.0))
    src_file, src_line = _caller()
    _write('step_start', path=current_path(), total=total,
           items=None if items is None else [str(i) for i in items],
           src_file=src_file, src_line=src_line)


def _caller() -> Tuple[Optional[str], Optional[int]]:
    """
    Get where the code marked a step (the first frame outside this module
    and contextlib)

    :return: tuple (file, line) or (None, None)
    """
    skip = [os.path.realpath(__file__), os.path.realpath(contextlib.__file__)]
    try:
        frame = sys._getframe(1)
    except ValueError:
        return None, None
    while frame is not None:
        filename = frame.f_code.co_filename
        if os.path.realpath(filename) not in skip:
            return filename, frame.f_lineno
        frame = frame.f_back
    return None, None


def _pop(status: str, error: Optional[str] = None) -> None:
    """
    Close the innermost step (write step_end)

    :param status: str, complete or failed
    :param error: str or None, the error of a failed step

    :return: None
    """
    if not _STACK:
        return
    path = current_path()
    _STACK.pop()
    _write('step_end', path=path, status=status, error=error)


def _close_marks(status: str) -> None:
    """
    Close the marks left open above the innermost real step

    :param status: str, complete or failed

    :return: None
    """
    while _STACK and _STACK[-1]['mark']:
        _pop(status)


def start(name: str, total: Optional[int] = None,
          items: Optional[List[Any]] = None) -> None:
    """
    Open a step without a context manager (close it with end())

    :param name: str, the step name
    :param total: int or None, the number of things it will process
    :param items: list or None, loop items (one child step each)

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        _close_marks('complete')
        _push(name, False, total, items)


def end(status: str = 'complete', error: Optional[str] = None) -> None:
    """
    Close the innermost step opened with start() (and its open marks)

    :param status: str, complete or failed
    :param error: str or None, the error of a failed step

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        _close_marks(status)
        _pop(status, error)


@contextlib.contextmanager
def step(name: str, total: Optional[int] = None,
         items: Optional[List[Any]] = None) -> Iterator[None]:
    """
    Record a block as a step (failed if it raises)

    :param name: str, the step name
    :param total: int or None, the number of things it will process
    :param items: list or None, loop items (one child step each)

    :return: None (context manager)
    """
    if _WRITER is None:
        yield
        return
    with _LOCK:
        _close_marks('complete')
        _push(name, False, total, items)
        depth = len(_STACK)
    try:
        yield
    except BaseException as error:
        with _LOCK:
            # close everything opened inside this step, then the step
            while len(_STACK) > depth:
                _pop('failed')
            _pop('failed', '{0}: {1}'.format(type(error).__name__, error))
        raise
    with _LOCK:
        while len(_STACK) > depth:
            _pop('complete')
        _pop('complete')


def mark(name: str, total: Optional[int] = None,
         items: Optional[List[Any]] = None) -> None:
    """
    Start a sequential section: ends the previous mark of the same step
    and opens a new one (the enclosing step closes the last mark)

    :param name: str, the section name
    :param total: int or None, the number of things it will process
    :param items: list or None, loop items (one child step each)

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        _close_marks('complete')
        _push(name, True, total, items)


def items(names: List[Any]) -> None:
    """
    Announce the loop items of the innermost step (if they were not known
    when it started)

    :param names: list, the items (one child step each)

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        _write('step_items', path=current_path(),
               items=[str(name) for name in names])


def advance(done: Optional[int] = None, total: Optional[int] = None,
            detail: Optional[str] = None, force: bool = False) -> None:
    """
    Record progress through the innermost step (rate limited)

    :param done: int or None, the number of things done
    :param total: int or None, the number of things
    :param detail: str or None, what is being processed now
    :param force: bool, write even if the last event is very recent

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        if not _STACK:
            return
        frame = _STACK[-1]
        now = time.time()
        if not force and now - frame['last_advance'] < ADVANCE_INTERVAL:
            return
        frame['last_advance'] = now
        _write('step_advance', path=current_path(), done=done, total=total,
               detail=detail)


def close_all(status: str, error: Optional[str] = None) -> None:
    """
    Close every open step (e.g. when the owner's stage ends or fails)

    :param status: str, complete or failed
    :param error: str or None, the error (given to the outermost step)

    :return: None
    """
    if _WRITER is None:
        return
    with _LOCK:
        while len(_STACK) > 1:
            _pop(status)
        _pop(status, error)


# =============================================================================
# End of code
# =============================================================================
