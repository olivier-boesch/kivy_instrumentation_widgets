import time
from datetime import timedelta

import pytest

from timer import CircularTimer


def test_initial_state():
    timer = CircularTimer()
    assert timer.angle == 360
    assert timer.time_text == "00:00"
    assert timer.total_seconds == 0.0
    assert timer.seconds_left == 0.0


def test_start_sets_duration_and_updates_ui():
    timer = CircularTimer()
    timer.start(timedelta(seconds=30))

    assert timer.total_seconds == 30.0
    assert timer.seconds_left == 30.0
    assert timer.time_text == "00:30"
    assert timer.angle == pytest.approx(360)
    assert timer._clock_event is not None

    timer.stop()


def test_tick_decreases_remaining_time():
    timer = CircularTimer()
    timer.start(timedelta(seconds=10))

    timer._tick(2.0)

    assert timer.seconds_left == pytest.approx(8.0)
    assert timer.time_text == "00:08"
    assert timer.angle == pytest.approx(360 * 8 / 10)

    timer.stop()


def test_tick_stops_at_zero():
    timer = CircularTimer()
    timer.start(timedelta(seconds=1))

    timer._tick(2.0)

    assert timer.seconds_left == 0.0
    assert timer.time_text == "00:00"
    assert timer.angle == 0
    assert timer._clock_event is None


def test_pause_cancels_event_without_resetting_time():
    timer = CircularTimer()
    timer.start(timedelta(seconds=10))
    timer._tick(1.0)

    timer.pause()

    assert timer._clock_event is None
    assert timer.seconds_left == pytest.approx(9.0)


def test_resume_continues_from_paused_time():
    timer = CircularTimer()
    timer.start(timedelta(seconds=10))
    timer._tick(4.0)
    timer.pause()

    timer.start()  # sans durée -> reprend

    assert timer.total_seconds == 10.0
    assert timer.seconds_left == pytest.approx(6.0)
    assert timer._clock_event is not None

    timer.stop()


def test_stop_resets_everything():
    timer = CircularTimer()
    timer.start(timedelta(seconds=10))

    timer.stop()

    assert timer.seconds_left == 0.0
    assert timer.total_seconds == 0.0
    assert timer.time_text == "00:00"
    assert timer.angle == 0
    assert timer._clock_event is None


@pytest.mark.performance
def test_tick_performance():
    timer = CircularTimer()
    timer.start(timedelta(hours=10))
    iterations = 20000

    start = time.perf_counter()
    for _ in range(iterations):
        timer._tick(0.05)
    elapsed = time.perf_counter() - start

    timer.stop()
    assert elapsed < 3.0
