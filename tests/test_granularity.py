import pytest

from granularity import snap_value, decimals_for, format_value


@pytest.mark.parametrize("granularity, expected", [
    (0.5, 1),
    (0.2, 1),
    (0.25, 2),
    (2, 0),
    (10, 0),
    (1, 0),
    (None, 2),
])
def test_decimals_for(granularity, expected):
    assert decimals_for(granularity) == expected


@pytest.mark.parametrize("magnitude, granularity, expected", [
    (2.6, 0.5, 2.5),
    (2.9, 0.5, 3.0),
    (2.3, 0.2, 2.2),
    (2.5, 0.2, 2.4),
    (2.7, 0.2, 2.8),
    (4.9, 2, 4),
    (6.1, 2, 6),
    (7.9, 2, 8),
    (33.333, None, 33.333),
    (33.333, 0, 33.333),
])
def test_snap_value(magnitude, granularity, expected):
    assert snap_value(magnitude, granularity) == pytest.approx(expected)


@pytest.mark.parametrize("magnitude, granularity, expected", [
    (2.5, 0.5, "2.5"),
    (3.0, 0.5, "3.0"),
    (2.2, 0.2, "2.2"),
    (4, 2, "4"),
    (33.333, None, "33.33"),
])
def test_format_value(magnitude, granularity, expected):
    assert format_value(magnitude, granularity) == expected
