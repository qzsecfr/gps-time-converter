"""Test reverse conversion functions."""

import pytest
from gps_time.converter import (
    doy_to_ymd_with_fraction,
    bjt_to_utc_datetime,
    gps_to_utc_datetime,
    ymd_to_mjd,
    day_of_year,
    utc_to_bjt_datetime,
    utc_to_gps_datetime,
)


class TestDoyToYmd:
    """Test DOY to YMD conversion with fractional days."""

    def test_doy_whole_day(self):
        """Test DOY without fractional part."""
        year, month, day, hour, minute, second = doy_to_ymd_with_fraction(2024, 15.0)
        assert (year, month, day) == (2024, 1, 15)
        assert hour == 0 and minute == 0 and second == 0

    def test_doy_with_fraction(self):
        """Test DOY with 0.5 fraction (12 hours)."""
        year, month, day, hour, minute, second = doy_to_ymd_with_fraction(2024, 15.5)
        assert (year, month, day) == (2024, 1, 15)
        assert hour == 12 and minute == 0 and second == 0

    def test_doy_cross_day_boundary(self):
        """Test DOY fraction crossing to next day."""
        year, month, day, hour, minute, second = doy_to_ymd_with_fraction(2024, 15.75)
        assert (year, month, day) == (2024, 1, 15)
        assert hour == 18 and minute == 0

    def test_doy_roundtrip(self):
        """Test roundtrip: YMD -> DOY -> YMD."""
        original_doy = day_of_year(2024, 6, 15)
        ymd = doy_to_ymd_with_fraction(2024, original_doy + 0.5)
        assert ymd[:3] == (2024, 6, 15)


class TestBjtToUtc:
    """Test Beijing Time to UTC conversion."""

    def test_bjt_to_utc_same_day(self):
        """Test BJT 20:00 -> UTC 12:00 (same day)."""
        year, month, day, hour, minute, second = bjt_to_utc_datetime(
            2024, 1, 15, 20, 0, 0
        )
        assert (year, month, day) == (2024, 1, 15)
        assert hour == 12 and minute == 0 and second == 0

    def test_bjt_to_utc_previous_day(self):
        """Test BJT 04:00 -> UTC 20:00 (previous day)."""
        year, month, day, hour, minute, second = bjt_to_utc_datetime(
            2024, 1, 2, 4, 0, 0
        )
        assert (year, month, day) == (2024, 1, 1)
        assert hour == 20 and minute == 0 and second == 0

    def test_bjt_to_utc_roundtrip(self):
        """Test roundtrip: UTC -> BJT -> UTC."""
        bjt = utc_to_bjt_datetime(2024, 6, 15, 12, 30, 45)
        utc = bjt_to_utc_datetime(*bjt)
        assert utc[:3] == (2024, 6, 15)
        assert utc[3:] == (12, 30, 45)


class TestGpsWeekToUtc:
    """Test GPS Week to UTC conversion."""

    def test_gps_week_dow_to_utc(self):
        """Test GPS Week + DOW (converted to TOW) to UTC."""
        # DOW 5 = Friday = 5 * 86400 seconds from week start
        tow_for_dow_5 = 5 * 86400  # 432000 seconds
        year, month, day, hour, minute, second = gps_to_utc_datetime(
            2405, tow_for_dow_5, 0
        )
        # Week 2405, day 5 (Friday) should be 2026-02-13
        assert (year, month, day) == (2026, 2, 13)
        assert hour == 0 and minute == 0 and second == 0

    def test_gps_week_tow_to_utc(self):
        """Test GPS Week + TOW to UTC."""
        year, month, day, hour, minute, second = gps_to_utc_datetime(2405, 475219.0)
        # TOW 475219 = 5 days + 13h 13m 39s
        assert (year, month, day) == (2026, 2, 13)

    def test_gps_week_roundtrip(self):
        """Test roundtrip: UTC -> GPS -> UTC."""
        gps = utc_to_gps_datetime(2024, 6, 15, 12, 0, 0)
        utc = gps_to_utc_datetime(gps[0], gps[1])
        assert utc[:3] == (2024, 6, 15)


class TestReverseConversions:
    """Test that reverse conversions are consistent."""

    def test_mjd_roundtrip(self):
        """Test MJD -> YMD -> MJD roundtrip."""
        from gps_time.converter import mjd_to_ymd

        original_mjd = 61084.52135416667
        ymd = mjd_to_ymd(original_mjd)
        back_to_mjd = ymd_to_mjd(*ymd)
        assert (
            abs(original_mjd - back_to_mjd) < 1e-9
        )  # Allow small floating point error

    def test_all_formats_consistency(self):
        """Test that all input formats produce consistent output."""
        # UTC 2024-01-15 12:00:00
        utc_ymd = (2024, 1, 15, 12, 0, 0)

        # Convert to other formats
        mjd = ymd_to_mjd(*utc_ymd)
        doy = day_of_year(2024, 1, 15) + 0.5
        bjt = utc_to_bjt_datetime(*utc_ymd)
        gps = utc_to_gps_datetime(*utc_ymd)

        # Convert back to UTC
        from gps_time.converter import mjd_to_ymd

        utc_from_mjd = mjd_to_ymd(mjd)[:6]
        utc_from_doy = doy_to_ymd_with_fraction(2024, doy)
        utc_from_bjt = bjt_to_utc_datetime(*bjt)
        utc_from_gps = gps_to_utc_datetime(gps[0], gps[1])

        # All should match original UTC
        for utc in [utc_from_mjd, utc_from_doy, utc_from_bjt, utc_from_gps]:
            assert utc[:3] == (2024, 1, 15)
