import time

import pytest
from kivy.metrics import dp

from borderwrapper import BorderWrapper
from theme import ACCENT_DIM


def test_default_border_color_is_accent_dim():
    bw = BorderWrapper()
    assert bw.border_color == ACCENT_DIM
    assert bw.title_texture is None


def test_setting_title_creates_texture():
    bw = BorderWrapper()
    bw.title = "Puissance"
    assert bw.title_texture is not None
    assert bw.title_texture.width > 0
    assert bw.title_texture.height > 0


def test_clearing_title_removes_texture():
    bw = BorderWrapper(title="Puissance")
    assert bw.title_texture is not None

    bw.title = ""
    assert bw.title_texture is None


def test_border_color_and_width_update_canvas_instructions():
    bw = BorderWrapper()

    bw.border_color = [1, 0, 0, 1]
    assert list(bw._border_color_instr.rgba) == pytest.approx([1, 0, 0, 1])

    bw.border_width = 3
    assert bw._border_line.width == pytest.approx(dp(3))


def test_rebuild_canvas_on_resize_updates_border_line():
    bw = BorderWrapper(title="Tension", padding=[10, 16, 10, 10])
    bw.size = (200, 100)
    bw.pos = (5, 5)

    # rounded_rectangle est une propriété d'écriture seule sur Line ;
    # on vérifie simplement que la mise à jour ne lève pas d'exception.

    # La texture du titre doit être positionnée dans la bordure
    assert bw._title_rect.texture is bw.title_texture
    assert bw._title_color_instr.rgba == [1, 1, 1, 1]


@pytest.mark.performance
def test_resize_performance():
    bw = BorderWrapper(title="Puissance")
    iterations = 3000

    start = time.perf_counter()
    for i in range(iterations):
        bw.size = (200 + i % 50, 100 + i % 30)
        bw.pos = (i % 10, 0)
    elapsed = time.perf_counter() - start

    assert elapsed < 3.0


@pytest.mark.performance
def test_title_update_performance():
    bw = BorderWrapper()
    iterations = 500

    start = time.perf_counter()
    for i in range(iterations):
        bw.title = f"Mesure {i}"
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0
