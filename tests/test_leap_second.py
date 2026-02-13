"""Test for leap second table parser."""

import pytest
from datetime import date
from gps_time.leap_second_table import LeapSecondTable


class TestLeapSecondTable:
    """Test cases for LeapSecondTable class."""

    @pytest.fixture
    def table(self):
        """Create LeapSecondTable instance."""
        return LeapSecondTable()

    def test_get_leap_second_1972_01_01(self, table):
        """Test leap second value for 1972-01-01."""
        result = table.get_leap_second(1972, 1, 1)
        assert result == -9

    def test_get_leap_second_1980_01_06(self, table):
        """Test leap second value for 1980-01-06 (GPS epoch)."""
        result = table.get_leap_second(1980, 1, 6)
        assert result == 0

    def test_get_leap_second_2017_01_01(self, table):
        """Test leap second value for 2017-01-01."""
        result = table.get_leap_second(2017, 1, 1)
        assert result == 18

    def test_get_leap_second_2024_01_01(self, table):
        """Test leap second value for 2024-01-01."""
        result = table.get_leap_second(2024, 1, 1)
        assert result == 18

    def test_get_leap_second_with_date_object(self, table):
        """Test get_leap_second with date object."""
        result = table.get_leap_second(date=date(2017, 1, 1))
        assert result == 18

    def test_get_leap_second_before_first_record(self, table):
        """Test leap second before first record returns first value."""
        result = table.get_leap_second(1970, 1, 1)
        assert result == -9

    def test_get_leap_second_between_records(self, table):
        """Test leap second between two records returns earlier value."""
        # 1981-01-01 is between 1980-01-01 (0) and 1981-07-01 (1)
        result = table.get_leap_second(1981, 1, 1)
        assert result == 0
