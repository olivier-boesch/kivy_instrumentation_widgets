import time

import pytest

from rollingchart import RollingChart
from units import ureg
from theme import ACCENT


def make_chart(**kwargs):
    kwargs.setdefault('x_window', 10)
    chart = RollingChart(y_unit=0 * ureg.watt, x_step=1 * ureg.second, **kwargs)
    chart.size = (300, 200)
    return chart


def test_default_line_color_is_accent():
    chart = make_chart()
    assert chart.line_color == ACCENT


def test_push_appends_to_history():
    chart = make_chart()
    chart.push(5 * ureg.watt)
    chart.push(7 * ureg.watt)

    assert list(chart._history) == [5, 7]


def test_push_rescales_y_range_on_new_extremes():
    chart = make_chart()
    chart.push(10 * ureg.watt)

    assert chart._data_min == pytest.approx(10)
    assert chart._data_max == pytest.approx(10)
    assert chart._y_min < 10 < chart._y_max

    chart.push(20 * ureg.watt)
    assert chart._data_max == pytest.approx(20)
    assert chart._y_max > 20


def test_push_updates_data_line_points():
    chart = make_chart()
    chart.push(1 * ureg.watt)
    chart.push(2 * ureg.watt)

    points = chart._data.points
    assert len(points) == 4  # 2 points x (x, y)
    # les abscisses avancent par pas de _dx
    assert points[2] == pytest.approx(points[0] + chart._dx)


def test_clear_resets_history_and_line():
    chart = make_chart()
    chart.push(1 * ureg.watt)
    chart.push(2 * ureg.watt)

    chart.clear()

    assert len(chart._history) == 0
    assert chart._data.points == []


def test_line_color_property_updates_canvas_color():
    chart = make_chart()
    chart.line_color = [1, 0, 0, 1]
    assert list(chart._lc.rgba) == pytest.approx([1, 0, 0, 1])


def test_unit_conversion_on_push():
    chart = make_chart()
    chart.push((1 * ureg.kilowatt))
    assert chart._history[-1] == pytest.approx(1000)


@pytest.mark.performance
def test_push_performance():
    chart = make_chart(x_window=100)
    iterations = 5000

    start = time.perf_counter()
    for i in range(iterations):
        chart.push((i % 100) * ureg.watt)
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0


@pytest.mark.performance
def test_resize_performance():
    chart = make_chart()
    for i in range(100):
        chart.push((i % 50) * ureg.watt)

    iterations = 500
    start = time.perf_counter()
    for i in range(iterations):
        chart.size = (300 + i % 20, 200 + i % 10)
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0
