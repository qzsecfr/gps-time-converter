"""Test fixtures for GPS time package."""

import pytest

from datetime import datetime, timezone


@pytest.fixture
def gps_epoch():
    """GPS epoch: 1980-01-06 00:00:00 UTC."""
    return datetime(1980, 1, 6, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_datetime():
    """A sample datetime for testing."""
    return datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)


@pytest.fixture
def leap_second_table():
    """Sample leap second table for testing."""
    return {
        datetime(1980, 1, 6, tzinfo=timezone.utc): 0,
        datetime(1981, 7, 1, tzinfo=timezone.utc): 1,
        datetime(1982, 7, 1, tzinfo=timezone.utc): 2,
        datetime(1983, 7, 1, tzinfo=timezone.utc): 3,
        datetime(1985, 7, 1, tzinfo=timezone.utc): 4,
        datetime(1988, 1, 1, tzinfo=timezone.utc): 5,
        datetime(1990, 1, 1, tzinfo=timezone.utc): 6,
        datetime(1991, 1, 1, tzinfo=timezone.utc): 7,
        datetime(1992, 7, 1, tzinfo=timezone.utc): 8,
        datetime(1993, 7, 1, tzinfo=timezone.utc): 9,
        datetime(1994, 7, 1, tzinfo=timezone.utc): 10,
        datetime(1996, 1, 1, tzinfo=timezone.utc): 11,
        datetime(1997, 7, 1, tzinfo=timezone.utc): 12,
        datetime(1999, 1, 1, tzinfo=timezone.utc): 13,
        datetime(2006, 1, 1, tzinfo=timezone.utc): 14,
        datetime(2009, 1, 1, tzinfo=timezone.utc): 15,
        datetime(2012, 7, 1, tzinfo=timezone.utc): 16,
        datetime(2015, 7, 1, tzinfo=timezone.utc): 17,
        datetime(2017, 1, 1, tzinfo=timezone.utc): 18,
    }
