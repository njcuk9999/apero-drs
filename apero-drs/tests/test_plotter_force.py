#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for forced APERO plotter overrides."""

from apero.plotting import plotter as plotter_module


class _FakePlt:
    """Minimal pyplot stub that records display operations."""

    def __init__(self):
        """Initialize the pyplot call counters."""
        self.show_calls = []
        self.close_calls = 0

    def show(self, block: bool = True) -> None:
        """Record a show call."""
        self.show_calls.append(block)

    def close(self, *args, **kwargs) -> None:
        """Record a close call."""
        _ = args, kwargs
        self.close_calls += 1

    def ion(self) -> None:
        """Provide the interactive-on API used by the plotter."""

    def ioff(self) -> None:
        """Provide the interactive-off API used by the plotter."""

    def isinteractive(self) -> bool:
        """Report a non-interactive pyplot state for tests."""
        return False


class _FakeGraph:
    """Minimal graph object used to exercise Plotter.__call__."""

    def __init__(self, func, kind: str = 'debug',
                 name: str = 'THERMAL_BACKGROUND'):
        """Store the graph metadata used by the plotter."""
        self.func = func
        self.kind = kind
        self.name = name
        self.filename = 'fake-graph'
        self.dpi = 100
        self.description = 'fake graph'

    def copy(self):
        """Return a shallow copy that keeps the plotting callback."""
        new_graph = _FakeGraph(self.func, kind=self.kind, name=self.name)
        new_graph.filename = self.filename
        new_graph.dpi = self.dpi
        new_graph.description = self.description
        return new_graph

    def set_filename(self, params, location, fiber=None, suffix=None) -> None:
        """Accept the filename update used during plot execution."""
        _ = params, location, fiber
        if suffix is not None:
            self.filename = suffix


# =============================================================================
# Define functions
# =============================================================================
def _patch_plotter_backend(monkeypatch, plotter_obj, fake_plt,
                           backend_calls) -> None:
    """Patch backend helpers so tests never open a real matplotlib GUI.

    :param monkeypatch: pytest monkeypatch fixture
    :param plotter_obj: Plotter instance under test
    :param fake_plt: fake pyplot object to attach to the plotter
    :param backend_calls: list used to record force flags

    :return: None
    """
    def _fake_get_plot_switches() -> None:
        """Provide a deterministic plot switch table for the fake plot."""
        plotter_obj.plot_switches['THERMAL_BACKGROUND'] = False

    def _fake_get_matplotlib(force: bool = False) -> None:
        """Attach the fake pyplot backend to the plotter."""
        backend_calls.append(force)
        plotter_obj.plt = fake_plt
        plotter_obj.matplotlib = object()
        plotter_obj.axes_grid1 = object()
        plotter_obj.backend = 'Qt5Agg'

    monkeypatch.setattr(plotter_obj, '_get_plot_switches',
                        _fake_get_plot_switches)
    monkeypatch.setattr(plotter_obj, '_get_matplotlib',
                        _fake_get_matplotlib)
    monkeypatch.setattr(plotter_obj, '_backend_can_show', lambda: True)


def test_plotter_returns_zero_in_mode_zero_without_force(
        spirou_params, monkeypatch) -> None:
    """Mode zero should still suppress plots when no force override is set."""
    plotter_obj = plotter_module.Plotter(spirou_params, None, mode=0)
    fake_plt = _FakePlt()
    backend_calls = []
    get_func_called = dict(value=False)

    def _unexpected_get_func(name: str):
        """Record an unexpected graph lookup during suppressed plotting."""
        _ = name
        get_func_called['value'] = True
        return None

    _patch_plotter_backend(monkeypatch, plotter_obj, fake_plt,
                           backend_calls)
    monkeypatch.setattr(plotter_obj, '_get_func', _unexpected_get_func)

    result = plotter_obj('THERMAL_BACKGROUND')

    assert result == 0
    assert backend_calls == [False]
    assert get_func_called['value'] is False


def test_force_plot_overrides_mode_zero_for_debug_plot(
        spirou_params, monkeypatch) -> None:
    """Forced debug plots should execute and display even in plot mode zero."""
    plotter_obj = plotter_module.Plotter(spirou_params, None, mode=0)
    fake_plt = _FakePlt()
    backend_calls = []
    state = dict(plot_started=False, force_seen=False)

    def _fake_plot(local_plotter, graph, kwargs) -> None:
        """Exercise the real plotstart/plotend methods under force mode."""
        _ = kwargs
        state['plot_started'] = local_plotter.plotstart(graph)
        state['force_seen'] = local_plotter.force_plot_active
        local_plotter.plotend(graph)

    _patch_plotter_backend(monkeypatch, plotter_obj, fake_plt,
                           backend_calls)
    monkeypatch.setattr(plotter_obj, '_get_func',
                        lambda name: _FakeGraph(_fake_plot, name=name))

    result = plotter_obj('THERMAL_BACKGROUND', force_plot=True)

    assert result == 1
    assert state['plot_started'] is True
    assert state['force_seen'] is True
    assert backend_calls == [True, True]
    assert fake_plt.show_calls == [True]
    assert fake_plt.close_calls == 1
    assert plotter_obj.force_plot_active is False

