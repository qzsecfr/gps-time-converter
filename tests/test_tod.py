"""Tests for Time of Day (TOD) calculation."""

import pytest

from gps_time.converter import time_of_day


def test_tod_midnight():
    """Test TOD at midnight: 00:00:00 should be 0 seconds."""
    result = time_of_day(0, 0, 0)
    assert result == 0


def test_tod_noon():
    """Test TOD at noon: 12:00:00 should be 43200 seconds."""
    result = time_of_day(12, 0, 0)
    assert result == 43200  # 12 * 3600


def test_tod_specific():
    """Test TOD at specific time: 15:30:45 should be 55845 seconds."""
    result = time_of_day(15, 30, 45)
    assert result == 55845  # 15*3600 + 30*60 + 45


def test_tod_day_boundary():
    """Test TOD at end of day: 23:59:59 should be 86399 seconds."""
    result = time_of_day(23, 59, 59)
    assert result == 86399  # 23*3600 + 59*60 + 59


def test_tod_invalid_time():
    """Test TOD with invalid time inputs raises ValueError."""
    # Invalid hour
    with pytest.raises(ValueError):
        time_of_day(24, 0, 0)

    with pytest.raises(ValueError):
        time_of_day(-1, 0, 0)

    # Invalid minute
    with pytest.raises(ValueError):
        time_of_day(0, 60, 0)

    with pytest.raises(ValueError):
        time_of_day(0, -1, 0)

    # Invalid second
    with pytest.raises(ValueError):
        time_of_day(0, 0, 60)

    with pytest.raises(ValueError):
        time_of_day(0, 0, -1)
