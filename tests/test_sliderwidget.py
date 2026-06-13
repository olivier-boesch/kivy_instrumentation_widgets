import pytest

from sliderwidget import SliderWidget
from units import ureg


class FakeTouch:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.is_double_tap = False
        self.button = None
        self.ud = {}
        self.grab_current = None

    def grab(self, widget):
        self.grab_current = widget

    def ungrab(self, widget):
        self.grab_current = None


class FakeKeycode:
    def __init__(self, key_str):
        self.value = (None, key_str)

    def __getitem__(self, index):
        return self.value[index]


def make_slider(**kwargs):
    slider = SliderWidget(unit='W', min_value=0, max_value=100, **kwargs)
    slider.size = (200, 60)
    slider.pos = (0, 0)
    slider._deferred_init(0)
    return slider


def test_deferred_init_sets_initial_value():
    slider = make_slider()

    assert slider.value == 0 * ureg.watt
    assert slider.value_text == "0.00"
    assert slider.unit_text == "W"


def test_geometry_rebuilds_on_resize():
    slider = make_slider()
    track = slider.ids.track

    assert slider._x_min == pytest.approx(track.x + slider._handle_r)
    assert slider._x_max == pytest.approx(track.right - slider._handle_r)


def test_touch_at_track_start_sets_min_value():
    slider = make_slider()
    touch = FakeTouch(slider._x_min, slider._track_y)

    slider.on_touch_down(touch)

    assert slider.value.magnitude == pytest.approx(0)


def test_touch_at_track_end_sets_max_value():
    slider = make_slider()
    touch = FakeTouch(slider._x_max, slider._track_y)

    slider.on_touch_down(touch)

    assert slider.value.magnitude == pytest.approx(100)


def test_touch_at_middle_sets_midpoint():
    slider = make_slider()
    mid_x = (slider._x_min + slider._x_max) / 2
    touch = FakeTouch(mid_x, slider._track_y)

    slider.on_touch_down(touch)

    assert slider.value.magnitude == pytest.approx(50)


def test_touch_grabs_focus():
    slider = make_slider()
    touch = FakeTouch(slider._x_min, slider._track_y)

    slider.on_touch_down(touch)

    assert slider.focus is True
    assert touch.grab_current is slider


def test_touch_outside_track_is_ignored():
    slider = make_slider()
    slider.on_touch_down(FakeTouch(-50, -50))

    assert slider.value.magnitude == 0
    assert slider.focus is False


def test_drag_updates_value_continuously():
    slider = make_slider()

    touch = FakeTouch(slider._x_min, slider._track_y)
    slider.on_touch_down(touch)
    assert slider.value.magnitude == pytest.approx(0)

    touch.x = slider._x_max
    touch.pos = (touch.x, touch.y)
    slider.on_touch_move(touch)
    assert slider.value.magnitude == pytest.approx(100)

    slider.on_touch_up(touch)
    assert touch.grab_current is None


def test_touch_move_ignored_without_grab():
    slider = make_slider()
    touch = FakeTouch(slider._x_max, slider._track_y)

    slider.on_touch_move(touch)

    assert slider.value.magnitude == 0


def test_keyboard_arrows_change_value_by_granularity():
    slider = make_slider(granularity=2)

    slider.keyboard_on_key_down(None, FakeKeycode('right'), '', [])
    assert slider.value.magnitude == pytest.approx(2)

    slider.keyboard_on_key_down(None, FakeKeycode('left'), '', [])
    assert slider.value.magnitude == pytest.approx(0)


def test_keyboard_page_keys_change_value_by_ten_granularities():
    slider = make_slider(granularity=1)

    slider.keyboard_on_key_down(None, FakeKeycode('pageup'), '', [])
    assert slider.value.magnitude == pytest.approx(10)

    slider.keyboard_on_key_down(None, FakeKeycode('pagedown'), '', [])
    assert slider.value.magnitude == pytest.approx(0)


def test_keyboard_home_end_set_bounds():
    slider = make_slider()

    slider.keyboard_on_key_down(None, FakeKeycode('end'), '', [])
    assert slider.value.magnitude == pytest.approx(100)

    slider.keyboard_on_key_down(None, FakeKeycode('home'), '', [])
    assert slider.value.magnitude == pytest.approx(0)


def test_keyboard_clamps_to_bounds():
    slider = make_slider()

    slider.set_value(slider.max_value)
    slider.keyboard_on_key_down(None, FakeKeycode('right'), '', [])
    assert slider.value.magnitude == pytest.approx(100)

    slider.set_value(slider.min_value)
    slider.keyboard_on_key_down(None, FakeKeycode('left'), '', [])
    assert slider.value.magnitude == pytest.approx(0)


def test_value_text_updates_with_granularity():
    slider = make_slider(granularity=0.1)
    touch = FakeTouch((slider._x_min + slider._x_max) / 2, slider._track_y)

    slider.on_touch_down(touch)

    assert slider.value_text == "50.0"


def test_unit_change_updates_internal_unit():
    slider = make_slider()
    slider.unit = 'A'

    assert slider._unit == ureg('A')


def test_set_value_clamps_and_rounds():
    slider = make_slider(granularity=0.1)

    slider.set_value(150)
    assert slider.value.magnitude == pytest.approx(100)

    slider.set_value(-10)
    assert slider.value.magnitude == pytest.approx(0)

    slider.set_value(33.333)
    assert slider.value.magnitude == pytest.approx(33.3)


def test_label_press_event_dispatches():
    slider = make_slider()
    events = []
    slider.bind(on_label_press=lambda *a: events.append(a))

    slider.dispatch('on_label_press')

    assert len(events) == 1


def test_focus_changes_handle_color():
    slider = make_slider()
    assert slider._handle_color.rgba == list(slider.graphics_color)

    slider.focus = True
    assert slider._handle_color.rgba == [1, 0.5, 0, 1]

    slider.focus = False
    assert slider._handle_color.rgba == list(slider.graphics_color)
