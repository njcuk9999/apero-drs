#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Side by side diffs for browser guis

Builds the rows of a two pane (left/right) diff view, similar to the diff
viewers of IDEs: equal lines sit side by side, changed lines are paired
up (with the changed characters marked), deleted lines only have a left
side and inserted lines only have a right side. Long runs of equal lines
can be folded down to a few context lines around each change.

Only the standard library (difflib) is used.

Created on 2026-11-26

@author: cook
"""
import difflib
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.diff.py'
# changed line pairs less similar than this are shown as delete + insert
#    (no character highlights)
PAIR_RATIO = 0.3
# maximum line length for character level highlighting (speed)
INTRALINE_MAX = 2000


# =============================================================================
# Define functions
# =============================================================================
def _char_spans(left: str, right: str
                ) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Find the changed character ranges between two lines

    :param left: str, the left line
    :param right: str, the right line

    :return: tuple, (left spans, right spans) - each span is [start, end]
    """
    if len(left) > INTRALINE_MAX or len(right) > INTRALINE_MAX:
        return [[0, len(left)]], [[0, len(right)]]
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    lspans, rspans = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        if i2 > i1:
            lspans.append([i1, i2])
        if j2 > j1:
            rspans.append([j1, j2])
    return lspans, rspans


def _row(tag: str, lno: Optional[int], ltext: Optional[str],
         rno: Optional[int], rtext: Optional[str]) -> Dict[str, Any]:
    """
    Build one diff row

    :param tag: str, equal / replace / delete / insert
    :param lno: int or None, the 1-based left line number
    :param ltext: str or None, the left text
    :param rno: int or None, the 1-based right line number
    :param rtext: str or None, the right text

    :return: dict, the row
    """
    return dict(tag=tag, lno=lno, ltext=ltext, rno=rno, rtext=rtext,
                lspans=[], rspans=[])


def side_by_side(left_text: str, right_text: str,
                 context: Optional[int] = None) -> Dict[str, Any]:
    """
    Compute a side by side diff of two texts

    :param left_text: str, the left (old) text
    :param right_text: str, the right (new) text
    :param context: int or None, fold equal runs down to this many lines
                    around each change (None = no folding)

    :return: dict(rows, changes, stats, identical) where rows is a list of
             row dicts (tag, lno, ltext, rno, rtext, lspans, rspans) or
             fold rows (tag='fold', count, lstart, rstart); changes holds
             the row index where each change block starts; stats counts
             added/removed/changed lines
    """
    left = left_text.splitlines()
    right = right_text.splitlines()
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    rows: List[Dict[str, Any]] = []
    stats = dict(added=0, removed=0, changed=0)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for offset in range(i2 - i1):
                rows.append(_row('equal', i1 + offset + 1, left[i1 + offset],
                                 j1 + offset + 1, right[j1 + offset]))
            continue
        if tag == 'delete':
            for it in range(i1, i2):
                rows.append(_row('delete', it + 1, left[it], None, None))
            stats['removed'] += i2 - i1
            continue
        if tag == 'insert':
            for jt in range(j1, j2):
                rows.append(_row('insert', None, None, jt + 1, right[jt]))
            stats['added'] += j2 - j1
            continue
        # replace: pair up lines (similar pairs get character highlights)
        npairs = max(i2 - i1, j2 - j1)
        for offset in range(npairs):
            it, jt = i1 + offset, j1 + offset
            ltext = left[it] if it < i2 else None
            rtext = right[jt] if jt < j2 else None
            if ltext is None:
                rows.append(_row('insert', None, None, jt + 1, rtext))
                stats['added'] += 1
                continue
            if rtext is None:
                rows.append(_row('delete', it + 1, ltext, None, None))
                stats['removed'] += 1
                continue
            ratio = difflib.SequenceMatcher(None, ltext, rtext).ratio()
            row = _row('replace', it + 1, ltext, jt + 1, rtext)
            if ratio >= PAIR_RATIO:
                row['lspans'], row['rspans'] = _char_spans(ltext, rtext)
            else:
                row['lspans'] = [[0, len(ltext)]]
                row['rspans'] = [[0, len(rtext)]]
            rows.append(row)
            stats['changed'] += 1
    # fold long runs of equal lines
    if context is not None:
        rows = _fold(rows, max(0, int(context)))
    # the row index where each change block starts (for next/prev)
    changes = []
    for index, row in enumerate(rows):
        if row['tag'] in ['equal', 'fold']:
            continue
        if index == 0 or rows[index - 1]['tag'] in ['equal', 'fold']:
            changes.append(index)
    identical = stats['added'] + stats['removed'] + stats['changed'] == 0
    return dict(rows=rows, changes=changes, stats=stats,
                identical=identical, nleft=len(left), nright=len(right))


def _fold(rows: List[Dict[str, Any]], context: int) -> List[Dict[str, Any]]:
    """
    Replace long runs of equal rows by a fold row (keeping context rows
    next to every change)

    :param rows: list of dict, the diff rows
    :param context: int, the number of equal rows kept around changes

    :return: list of dict, the folded rows
    """
    out: List[Dict[str, Any]] = []
    index = 0
    while index < len(rows):
        if rows[index]['tag'] != 'equal':
            out.append(rows[index])
            index += 1
            continue
        # find the run of equal rows
        end = index
        while end < len(rows) and rows[end]['tag'] == 'equal':
            end += 1
        run = rows[index:end]
        # how many rows to keep at the start / end of the run
        keep_start = 0 if index == 0 else context
        keep_end = 0 if end == len(rows) else context
        if len(run) <= keep_start + keep_end + 1:
            out.extend(run)
        else:
            out.extend(run[:keep_start])
            hidden = run[keep_start:len(run) - keep_end]
            out.append(dict(tag='fold', count=len(hidden),
                            lstart=hidden[0]['lno'], rstart=hidden[0]['rno'],
                            rows=hidden))
            out.extend(run[len(run) - keep_end:])
        index = end
    return out


# =============================================================================
# End of code
# =============================================================================
