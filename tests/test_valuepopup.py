import time

import pytest

from valuepopup import UnitNumberPopup
from units import ureg


def test_press_key_digits_and_decimal():
    popup = UnitNumberPopup()

    popup.press_key('1')
    popup.press_key('2')
    popup.press_key('.')
    popup.press_key('5')

    assert popup.input_numeric_str == '12.5'


def test_press_key_decimal_only_once():
    popup = UnitNumberPopup()

    popup.press_key('.')
    popup.press_key('.')

    assert popup.input_numeric_str == '0.'


def test_press_key_backspace_and_delete():
    popup = UnitNumberPopup()
    popup.input_numeric_str = '123'

    popup.press_key('⌫')
    assert popup.input_numeric_str == '12'

    popup.press_key('Del')
    assert popup.input_numeric_str == ''


def test_press_key_toggle_sign():
    popup = UnitNumberPopup()
    popup.input_numeric_str = '12'

    popup.press_key('-')
    assert popup.input_numeric_str == '-12'

    popup.press_key('-')
    assert popup.input_numeric_str == '12'


def test_update_display_formats_text():
    popup = UnitNumberPopup()
    popup.input_numeric_str = '12.5'
    popup.selected_prefix_str = 'k'
    popup.selected_unit_str = 'W'

    popup.update_display()

    assert popup.display_text == '12.5 kW'


def test_update_display_defaults_to_zero():
    popup = UnitNumberPopup()
    popup.selected_prefix_str = ''
    popup.selected_unit_str = 'W'

    popup.update_display()

    assert popup.display_text == '0 W'


@pytest.mark.parametrize("unit_name, expected_prefix, expected_root", [
    ('kilogram', 'k', 'gram'),
    ('milliwatt', 'm', 'watt'),
    ('watt', '', 'watt'),
])
def test_extract_prefix_and_root(unit_name, expected_prefix, expected_root):
    popup = UnitNumberPopup()
    unit_obj = ureg.Unit(unit_name)

    prefix, root = popup.extract_prefix_and_root(unit_obj)

    assert prefix == expected_prefix
    assert root == ureg.Unit(expected_root)


def test_validate_parses_value_and_invokes_callback():
    popup = UnitNumberPopup()
    popup.input_numeric_str = '5'
    popup.selected_prefix_str = 'k'
    popup.selected_unit_str = 'W'

    results = []
    popup.callback = results.append
    popup.initial_value = 0 * ureg.watt

    popup.validate()

    assert len(results) == 1
    quantity = results[0].to(ureg.watt)
    assert quantity.magnitude == pytest.approx(5000)


def test_validate_falls_back_to_initial_value_on_error():
    popup = UnitNumberPopup()
    popup.input_numeric_str = '5'
    popup.selected_prefix_str = 'bogus'
    popup.selected_unit_str = 'notaunit'

    results = []
    popup.callback = results.append
    popup.initial_value = 2 * ureg.hertz

    popup.validate()

    assert results == [2 * ureg.hertz]


@pytest.mark.performance
def test_press_key_performance():
    popup = UnitNumberPopup()
    iterations = 5000

    start = time.perf_counter()
    for i in range(iterations):
        popup.press_key(str(i % 10))
        if len(popup.input_numeric_str) > 20:
            popup.press_key('Del')
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0
