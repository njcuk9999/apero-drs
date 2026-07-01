#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for low-level queue helpers in `apero.io.drs_lock`."""

import os

from apero.io import drs_lock


def _params(tmp_path):
    """Build minimal lock params dictionary with a log path."""
    logdir = tmp_path / 'log'
    logdir.mkdir()
    return {'PATH.LOG': str(logdir)}


def test_clean_name_replaces_bad_characters(tmp_path) -> None:
    """Private cleaner should replace slash, backslash, dot, and comma."""
    lock = drs_lock.Lock(_params(tmp_path), 'my.lock')
    clean = lock._Lock__clean_name('a/b.c,d\\e')
    assert clean == 'a_b_c_d_e'


def test_enqueue_creates_lock_file_and_dequeue_removes_it(tmp_path) -> None:
    """Queue operations should create and then remove the item lock file."""
    lock = drs_lock.Lock(_params(tmp_path), 'queue')
    lock.enqueue('item.one')
    clean = lock._Lock__clean_name('item.one')
    abspath = os.path.join(lock.path, clean + '.lock')
    assert os.path.exists(abspath)
    lock.dequeue('item.one')
    assert not os.path.exists(abspath)


def test_myturn_true_when_first_matches_item(tmp_path, monkeypatch) -> None:
    """myturn should return True if computed first lock is this item."""
    lock = drs_lock.Lock(_params(tmp_path), 'queue2')
    clean = lock._Lock__clean_name('abc')
    monkeypatch.setattr(lock, '_Lock__getfirst', lambda name: clean + '.lock')
    ok, err = lock.myturn('abc')
    assert ok and err is None


def test_myturn_false_when_first_is_other(tmp_path, monkeypatch) -> None:
    """myturn should return False when another lock file is first."""
    lock = drs_lock.Lock(_params(tmp_path), 'queue3')
    monkeypatch.setattr(lock, '_Lock__getfirst',
                        lambda name: 'someone_else.lock')
    ok, err = lock.myturn('abc')
    assert not ok and err is None

