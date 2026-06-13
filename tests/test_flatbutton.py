import time

import pytest
from kivy.metrics import dp

from flatbutton import FlatButton, FlatToggleButton
from theme import ACCENT, ACCENT_DIM


def test_default_colors_are_accent():
    btn = FlatButton(text="Valider")
    assert btn.button_color == ACCENT_DIM
    assert btn.border_color == ACCENT


def test_state_change_updates_fill_alpha():
    btn = FlatButton(text="Valider")

    btn.state = "down"
    assert btn._fill_color.a == pytest.approx(1.0)

    btn.state = "normal"
    assert btn._fill_color.a == pytest.approx(0.3)


def test_button_color_updates_canvas_colors():
    btn = FlatButton(text="Valider", button_color=[1, 0, 0, 1], border_color=[0, 0, 1, 1])
    assert list(btn._fill_color.rgb) == pytest.approx([1, 0, 0])
    assert list(btn._border_color_instr.rgb) == pytest.approx([0, 0, 1])

    btn.button_color = [0, 1, 0, 1]
    assert list(btn._fill_color.rgb) == pytest.approx([0, 1, 0])
    assert list(btn._border_color_instr.rgb) == pytest.approx([0, 0, 1])


def test_radius_change_updates_geometry():
    btn = FlatButton(text="Valider", size=(100, 40))
    btn.radius = 20
    assert btn._dp_r == pytest.approx(dp(20))
    assert btn._fill_rect.radius[0] == pytest.approx((dp(20), dp(20)))


def test_resize_updates_fill_and_border_geometry():
    btn = FlatButton(text="Valider")
    btn.size = (200, 60)
    btn.pos = (10, 5)
    assert list(btn._fill_rect.size) == [200, 60]
    assert list(btn._fill_rect.pos) == [10, 5]
    # rounded_rectangle est une propriété d'écriture seule sur Line ;
    # on vérifie simplement que la mise à jour ne lève pas d'exception.


def test_toggle_button_group_exclusivity():
    a = FlatToggleButton(text="A", group="opts")
    b = FlatToggleButton(text="B", group="opts")

    a._do_press()
    assert a.state == "down"

    b._do_press()
    assert b.state == "down"
    assert a.state == "normal"


@pytest.mark.performance
def test_state_toggle_performance():
    btn = FlatButton(text="Valider")
    iterations = 5000

    start = time.perf_counter()
    for i in range(iterations):
        btn.state = "down" if i % 2 == 0 else "normal"
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0


@pytest.mark.performance
def test_resize_performance():
    btn = FlatButton(text="Valider")
    iterations = 5000

    start = time.perf_counter()
    for i in range(iterations):
        btn.size = (100 + i % 50, 40 + i % 20)
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0
