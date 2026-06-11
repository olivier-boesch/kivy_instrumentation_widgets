import time

import pytest

from validationwidget import ValidationWidget, SwipeArea, ActionCircle


class FakeTouch:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.ud = {}


def test_check_progress_marks_validated_above_threshold():
    widget = ValidationWidget()

    widget.check_progress(0.5)
    assert widget.is_validated is False

    widget.check_progress(0.99)
    assert widget.is_validated is True


def test_swipe_area_drag_updates_progress():
    area = SwipeArea(text="Arm >", thumb_width=50)
    area.size = (200, 60)
    area.pos = (0, 0)

    down = FakeTouch(x=25, y=30)  # à l'intérieur du thumb (0..50)
    assert area.on_touch_down(down) is True
    assert area._is_dragging is True

    move = FakeTouch(x=175, y=30)
    area.on_touch_move(move)
    assert area.progress == pytest.approx(1.0)

    up = FakeTouch(x=175, y=30)
    area.on_touch_up(up)
    assert area._is_dragging is False


def test_swipe_area_ignores_touch_outside_thumb():
    area = SwipeArea(text="Arm >", thumb_width=50)
    area.size = (200, 60)
    area.pos = (0, 0)

    down = FakeTouch(x=150, y=30)  # hors du thumb initial (0..50)
    result = area.on_touch_down(down)

    assert area._is_dragging is False
    # Widget.on_touch_down renvoie False si aucun enfant ne capte le touché
    assert not result


def test_action_circle_dispatches_event_when_active():
    received = []
    circle = ActionCircle(text="OK", is_active=True)
    circle.size = (80, 80)
    circle.pos = (0, 0)
    circle.bind(on_button_pressed=lambda *_: received.append(True))

    touch = FakeTouch(x=40, y=40)
    assert circle.on_touch_down(touch) is True
    assert received == [True]


def test_action_circle_ignores_touch_when_inactive():
    received = []
    circle = ActionCircle(text="OK", is_active=False)
    circle.size = (80, 80)
    circle.pos = (0, 0)
    circle.bind(on_button_pressed=lambda *_: received.append(True))

    touch = FakeTouch(x=40, y=40)
    circle.on_touch_down(touch)

    assert received == []


@pytest.mark.performance
def test_swipe_drag_performance():
    area = SwipeArea(text="Arm >", thumb_width=50)
    area.size = (200, 60)
    area.pos = (0, 0)
    area.on_touch_down(FakeTouch(x=25, y=30))

    iterations = 5000
    start = time.perf_counter()
    for i in range(iterations):
        area.on_touch_move(FakeTouch(x=25 + (i % 150), y=30))
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0
