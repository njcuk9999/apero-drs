#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tripwire test for ``apero_ri/static/js/target_info_render.js``.

A legacy plain-text renderer keeps getting re-appended to the
end of this file by something (editor, AI agent, merge, stash
pop). When that happens the second IIFE silently overwrites
``window.AperoTargetInfo`` and users see ugly white text instead
of the rich yellow/orange card UI.

This test asserts a set of structural invariants on the file so
any regression fails CI immediately and names the file.

If you legitimately need to grow the file past the size ceiling,
bump ``MAX_BYTES`` here in the same commit.

See /memories/repo/target-info-render-no-duplicate.md.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
JS_PATH = (HERE.parent / "apero_ri" / "static" / "js"
           / "target_info_render.js")

# Hard ceiling: the legitimate file is ~33 KB. Any append puts
# it well over 60 KB. Bump deliberately if growth is intended.
MAX_BYTES = 60_000

SENTINEL = "// === END OF FILE === apero_ri target_info_render.js"

FORBIDDEN_TOKENS = (
    # The legacy plain-grid renderer's CSS class. Must not exist
    # anywhere in this file. The active renderer uses
    # ``ari-tinfo-row`` instead.
    "ari-tinfo-grid",
)


class TargetInfoRenderInvariants(unittest.TestCase):
    """Structural invariants for target_info_render.js."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.assertTrue_path_exists = JS_PATH.exists()
        cls.text = JS_PATH.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        self.assertTrue(
            JS_PATH.exists(),
            "Missing file: {0}".format(JS_PATH),
        )

    def test_size_under_ceiling(self) -> None:
        size = JS_PATH.stat().st_size
        self.assertLessEqual(
            size, MAX_BYTES,
            "target_info_render.js is {0} B, over the {1} B "
            "ceiling. The legacy plain-text renderer has "
            "probably been re-appended. See "
            "/memories/repo/target-info-render-no-duplicate.md."
            .format(size, MAX_BYTES),
        )

    def test_exactly_one_iife(self) -> None:
        # An IIFE here always opens with ``(function ()`` at the
        # start of a line. There must be exactly one.
        opens = re.findall(
            r"(?m)^\(function \(\)", self.text)
        self.assertEqual(
            len(opens), 1,
            "Expected exactly 1 top-level IIFE in "
            "target_info_render.js, found {0}. The legacy "
            "renderer has been duplicated -- truncate the file "
            "back to a single IIFE."
            .format(len(opens)),
        )

    def test_exactly_one_iife_close(self) -> None:
        # The single IIFE must close with ``}());`` on its own
        # line. More than one means the file has been duplicated.
        closes = re.findall(r"(?m)^}\(\)\);\s*$", self.text)
        self.assertEqual(
            len(closes), 1,
            "Expected exactly 1 IIFE close on its own line in "
            "target_info_render.js, found %d." % len(closes),
        )

    def test_no_forbidden_tokens(self) -> None:
        for token in FORBIDDEN_TOKENS:
            self.assertNotIn(
                token, self.text,
                "Forbidden token {0!r} found in "
                "target_info_render.js. The legacy plain-grid "
                "renderer has come back."
                .format(token),
            )

    def test_sentinel_present(self) -> None:
        self.assertIn(
            SENTINEL, self.text,
            "End-of-file sentinel missing from "
            "target_info_render.js. Either the file was "
            "truncated too aggressively, or content was "
            "appended after the sentinel.",
        )

    def test_sentinel_near_end(self) -> None:
        # Sentinel must appear in the last 600 bytes of the
        # file. If anything is appended after it, this fails.
        tail = self.text[-600:]
        self.assertIn(
            SENTINEL, tail,
            "Sentinel is not near the end of the file -- "
            "something has been appended after it.",
        )

    def test_anti_revert_guard_present(self) -> None:
        self.assertIn(
            "__AperoTargetInfoLoaded", self.text,
            "Anti-revert guard '__AperoTargetInfoLoaded' is "
            "missing. Restore it at the top of the IIFE.",
        )

    def test_api_is_frozen(self) -> None:
        # The runtime backstop: AperoTargetInfo must be
        # installed via Object.defineProperty so a duplicate
        # IIFE cannot overwrite it.
        self.assertIn(
            'Object.defineProperty(window, "AperoTargetInfo"',
            self.text,
            "AperoTargetInfo must be installed via "
            "Object.defineProperty (writable:false) so a "
            "duplicate IIFE cannot reassign it.",
        )


if __name__ == "__main__":
    unittest.main()
