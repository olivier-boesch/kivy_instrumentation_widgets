import time

import pytest

from jauge import CircularGauge
from units import ureg


def make_gauge(**kwargs):
    kwargs.setdefault('window_size_n', 5)
    gauge = CircularGauge(min_value=0 * ureg.watt, max_value=50 * ureg.watt, **kwargs)
    gauge.size = (200, 200)
    return gauge


def test_initial_state():
    gauge = make_gauge()
    assert gauge.current_value == 0 * ureg.watt
    assert gauge.value_text == "0.00"
    assert gauge.unit_text == "W"


def test_set_value_updates_current_and_text():
    gauge = make_gauge()
    gauge.set_value(25 * ureg.watt)

    assert gauge.current_value == 25 * ureg.watt
    assert gauge.value_text == "25.00"


def test_set_value_clamps_to_bounds():
    gauge = make_gauge()

    gauge.set_value(1000 * ureg.watt)
    assert gauge.current_value == gauge.max_value

    gauge.set_value(-50 * ureg.watt)
    assert gauge.current_value == gauge.min_value


def test_set_value_accepts_plain_numbers():
    gauge = make_gauge()
    gauge.set_value(10)
    assert gauge.current_value.magnitude == pytest.approx(10)


def test_mean_value_tracks_moving_window():
    gauge = make_gauge(window_size_n=2)

    # La fenêtre est initialisée avec min_value (0 W) -> deque([0, 0])
    gauge.set_value(10 * ureg.watt)
    assert gauge.mean_value.magnitude == pytest.approx(5.0)  # (0 + 10) / 2

    gauge.set_value(20 * ureg.watt)
    assert gauge.mean_value.magnitude == pytest.approx(15.0)  # (10 + 20) / 2


def test_rebuild_geometry_computes_arc_radius():
    gauge = make_gauge()
    assert gauge._radius > 0
    assert gauge._r_inner < gauge._radius


def test_update_display_moves_arc_with_display_value():
    gauge = make_gauge()

    gauge.display_value = 25
    gauge._update_display()  # ne doit pas lever d'exception

    gauge.display_mean_value = 0
    gauge._update_display()
    points_at_zero = list(gauge._triangle_instr.points)

    gauge.display_mean_value = 50
    gauge._update_display()
    points_at_max = list(gauge._triangle_instr.points)

    assert points_at_zero != points_at_max


@pytest.mark.performance
def test_set_value_performance():
    gauge = make_gauge(window_size_n=20)
    iterations = 2000

    start = time.perf_counter()
    for i in range(iterations):
        gauge.set_value((i % 50) * ureg.watt)
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0


@pytest.mark.performance
def test_update_display_hot_path_performance():
    gauge = make_gauge()
    iterations = 20000

    start = time.perf_counter()
    for i in range(iterations):
        gauge.display_value = i % 50
        gauge.display_mean_value = (i * 2) % 50
        gauge._update_display()
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0
