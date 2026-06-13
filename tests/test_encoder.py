import time

import pytest

from encoder import RotaryEncoderWidget
from theme import EDIT, TEXT
from units import ureg


class FakeTouch:
    def __init__(self, x, y, is_double_tap=False, button=None):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.is_double_tap = is_double_tap
        self.button = button
        self.ud = {}
        self.grab_current = None

    def grab(self, widget):
        self.grab_current = widget

    def ungrab(self, widget):
        self.grab_current = None


def make_encoder(**kwargs):
    enc = RotaryEncoderWidget(unit='W', min_value=0, max_value=100, **kwargs)
    enc.size = (200, 200)
    enc.pos = (0, 0)
    enc._deferred_init(0)
    return enc


def test_deferred_init_sets_initial_value():
    enc = make_encoder()

    assert enc.value == 0 * ureg.watt
    assert enc.value_text == "0.00"
    assert enc.unit_text == "W"


def test_geometry_rebuilds_on_resize():
    enc = make_encoder()
    assert enc._r_outer == pytest.approx(80)
    assert enc._r_fine == pytest.approx(40)


def test_double_tap_toggles_editing_mode():
    enc = make_encoder()

    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))
    assert enc.state == 'editing'

    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))
    assert enc.state == 'idle'


def test_editing_mode_recolors_ring_with_edit_color():
    enc = make_encoder()

    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))
    assert enc._color_instr.rgba == EDIT
    assert enc.text_color == EDIT

    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))
    assert enc._color_instr.rgba == list(enc.graphics_color)
    assert enc.text_color == list(TEXT)


def test_drag_outside_fine_zone_changes_value():
    enc = make_encoder()
    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))  # éditer
    assert enc.state == 'editing'

    touch = FakeTouch(100, 175)  # à 90° (hors zone fine, r=75 > r_fine=40)
    enc.on_touch_down(touch)
    assert touch.grab_current is enc

    # Le même touché se déplace vers 0° -> delta = -90°
    touch.x, touch.y, touch.pos = 175, 100, (175, 100)
    enc.on_touch_move(touch)

    step_max = enc._step() * enc.step_max_multiplier
    assert enc.value.magnitude == pytest.approx(step_max * 90, rel=1e-2)


def test_scroll_in_editing_mode_steps_value():
    enc = make_encoder(granularity=0.5)
    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))  # éditer

    enc.on_touch_down(FakeTouch(175, 100, button='scrollup'))
    assert enc.value.magnitude == pytest.approx(0.5)

    enc.on_touch_down(FakeTouch(175, 100, button='scrolldown'))
    assert enc.value.magnitude == pytest.approx(0.0)


def test_long_press_cancel_restores_backup_value():
    enc = make_encoder()
    enc.on_touch_down(FakeTouch(175, 100, is_double_tap=True))  # éditer

    backup = enc.value
    enc.value = 42 * ureg.watt

    touch = FakeTouch(175, 100)
    enc._trigger_cancel(touch)

    assert enc.value == backup
    assert enc.state == 'idle'
    assert enc.fine_mode is False


def test_touch_outside_widget_is_ignored():
    enc = make_encoder()
    far_touch = FakeTouch(1000, 1000)

    result = enc.on_touch_down(far_touch)

    assert not result
    assert enc.state == 'idle'


@pytest.mark.performance
def test_update_text_performance():
    enc = make_encoder()
    iterations = 20000

    start = time.perf_counter()
    for i in range(iterations):
        enc.value = (i % 100) * ureg.watt
        enc.update_text()
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0


@pytest.mark.performance
def test_rebuild_geometry_performance():
    enc = make_encoder()
    iterations = 2000

    start = time.perf_counter()
    for i in range(iterations):
        enc.size = (200 + i % 30, 200 + i % 20)
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0
