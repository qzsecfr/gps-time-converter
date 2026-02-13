"""Tests for Beijing Time (BJT) conversion."""

import pytest
from gps_time.converter import utc_to_bjt_datetime


class TestUtcToBjtDatetime:
    """Test UTC to BJT conversion."""

    def test_utc_to_bjt_same_day(self):
        """UTC 10:00 → BJT 18:00 (same day)."""
        result = utc_to_bjt_datetime(2024, 1, 15, 10, 0, 0)
        assert result == (2024, 1, 15, 18, 0, 0)

    def test_utc_to_bjt_next_day(self):
        """UTC 23:00 → BJT 07:00+1 day (cross day boundary)."""
        result = utc_to_bjt_datetime(2024, 1, 15, 23, 0, 0)
        assert result == (2024, 1, 16, 7, 0, 0)

    def test_utc_to_bjt_midnight(self):
        """UTC 00:00 → BJT 08:00."""
        result = utc_to_bjt_datetime(2024, 1, 15, 0, 0, 0)
        assert result == (2024, 1, 15, 8, 0, 0)

    def test_bjt_year_boundary(self):
        """UTC 2023-12-31 20:00 → BJT 2024-01-01 04:00."""
        result = utc_to_bjt_datetime(2023, 12, 31, 20, 0, 0)
        assert result == (2024, 1, 1, 4, 0, 0)
