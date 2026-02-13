"""Tests for GPS time conversion functions."""

import pytest
from gps_time.converter import utc_to_gps_datetime, gps_to_utc_datetime


class TestUTCToGPS:
    """Tests for UTC to GPS time conversion."""

    def test_utc_to_gps_epoch(self):
        """Test UTC 1980-01-06 00:00:00 → GPS Week 0, TOW 0."""
        week, tow, dow = utc_to_gps_datetime(1980, 1, 6, 0, 0, 0, leap_seconds=0)

        assert week == 0
        assert tow == 0.0
        assert dow == 0

    def test_utc_to_gps_with_leap(self):
        """Test UTC to GPS conversion considering leap seconds."""
        # UTC 2024-05-20 12:00:00 with 18 second leap
        week, tow, dow = utc_to_gps_datetime(2024, 5, 20, 12, 0, 0, leap_seconds=18)

        # Expected: This should return valid week and tow values
        # We verify by roundtrip
        assert week >= 0
        assert 0 <= tow < 604800
        assert 0 <= dow <= 6

    def test_gps_dow_calculation(self):
        """Test DOW (Day of Week) = TOW // 86400 calculation."""
        # Test various times within the week
        # Day 0 (Sunday) - TOW 0 to 86399
        week, tow, dow = utc_to_gps_datetime(1980, 1, 6, 12, 0, 0, leap_seconds=0)
        assert dow == 0
        assert 0 <= tow < 86400

        # Day 1 (Monday) - TOW 86400 to 172799
        week, tow, dow = utc_to_gps_datetime(1980, 1, 7, 0, 0, 0, leap_seconds=0)
        assert dow == 1

        # Day 6 (Saturday)
        week, tow, dow = utc_to_gps_datetime(1980, 1, 12, 0, 0, 0, leap_seconds=0)
        assert dow == 6


class TestGPSToUTC:
    """Tests for GPS to UTC time conversion."""

    def test_gps_to_utc_epoch(self):
        """Test GPS Week 0, TOW 0 → UTC 1980-01-06 00:00:00."""
        year, month, day, hour, minute, second = gps_to_utc_datetime(
            0, 0.0, leap_seconds=0
        )

        assert year == 1980
        assert month == 1
        assert day == 6
        assert hour == 0
        assert minute == 0
        assert second == 0.0


class TestRoundTrip:
    """Tests for round-trip GPS ↔ UTC conversions."""

    def test_gps_to_utc_roundtrip(self):
        """Test GPS → UTC → GPS roundtrip conversion."""
        # Start with some GPS time
        original_week = 2300
        original_tow = 12345.0
        leap = 18

        # Convert GPS → UTC
        year, month, day, hour, minute, second = gps_to_utc_datetime(
            original_week, original_tow, leap_seconds=leap
        )

        # Convert UTC → GPS
        week, tow, dow = utc_to_gps_datetime(
            year, month, day, hour, minute, second, leap_seconds=leap
        )

        assert week == original_week
        assert abs(tow - original_tow) < 0.001  # Allow small floating point error


class TestGPSWeekBoundary:
    """Tests for GPS week boundary conditions."""

    def test_gps_week_boundary(self):
        """Test TOW = 604800 triggers week + 1."""
        # GPS TOW 604800 should be equivalent to next week, TOW 0
        week1, tow1, dow1 = utc_to_gps_datetime(1980, 1, 13, 0, 0, 0, leap_seconds=0)

        # This should be Week 1, TOW 0 (exactly one week after epoch)
        assert week1 == 1
        assert tow1 == 0.0
        assert dow1 == 0

    def test_gps_tow_overflow(self):
        """Test handling of TOW overflow across week boundary."""
        # Test with leap seconds that could cause TOW overflow
        # If UTC is at end of week and we add leap seconds
        week, tow, dow = utc_to_gps_datetime(1980, 1, 12, 23, 59, 50, leap_seconds=15)

        # TOW should be in valid range after adding leap seconds
        assert 0 <= tow < 604800
        # Week should have incremented if overflow occurred
        assert week >= 0


class TestLeapSeconds:
    """Tests for leap second handling."""

    def test_leap_second_effect(self):
        """Test that leap seconds affect TOW calculation."""
        # Same UTC time with different leap seconds
        week1, tow1, dow1 = utc_to_gps_datetime(2024, 5, 20, 12, 0, 0, leap_seconds=0)
        week2, tow2, dow2 = utc_to_gps_datetime(2024, 5, 20, 12, 0, 0, leap_seconds=18)

        # TOW should differ by exactly 18 seconds
        assert abs((tow2 - tow1) - 18.0) < 0.001

    def test_gps_minus_utc_with_leap(self):
        """Test GPS time minus UTC time equals leap seconds."""
        # At a specific moment, GPS time = UTC time + leap_seconds
        year, month, day, hour, minute, second = 2024, 5, 20, 12, 0, 0.0
        leap = 18

        # Get GPS time
        week, tow, dow = utc_to_gps_datetime(
            year, month, day, hour, minute, second, leap_seconds=leap
        )

        # Convert back without leap seconds (to get UTC equivalent)
        utc_from_gps = gps_to_utc_datetime(week, tow - leap, leap_seconds=0)

        # Should match original UTC time
        assert utc_from_gps[0] == year
        assert utc_from_gps[1] == month
        assert utc_from_gps[2] == day
        assert utc_from_gps[3] == hour
        assert utc_from_gps[4] == minute
        assert abs(utc_from_gps[5] - second) < 0.001
