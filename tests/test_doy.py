"""Tests for Day of Year (DOY) calculation."""

import pytest


class TestDayOfYearCalculation:
    """Test Day of Year (DOY) calculation."""

    def test_doy_normal_year(self):
        """平年 DOY 计算（2024-01-01 = 1）."""
        from gps_time.converter import day_of_year

        # 平年、闰年 1月1日都是 DOY = 1
        assert day_of_year(2024, 1, 1) == 1
        assert day_of_year(2023, 1, 1) == 1

    def test_doy_leap_year(self):
        """闰年 DOY 计算（2024-03-01 = 61）."""
        from gps_time.converter import day_of_year

        # 2024 是闰年，3月1日应该是第61天
        assert day_of_year(2024, 3, 1) == 61
        # 2024 是闰年，2月29日应该是第60天
        assert day_of_year(2024, 2, 29) == 60

    def test_doy_non_leap_year(self):
        """非闰年 DOY 计算（2023-03-01 = 60）."""
        from gps_time.converter import day_of_year

        # 2023 不是闰年，3月1日应该是第60天
        assert day_of_year(2023, 3, 1) == 60

    def test_doy_year_boundary(self):
        """年末测试（2024-12-31 = 366）."""
        from gps_time.converter import day_of_year

        # 闰年最后一天
        assert day_of_year(2024, 12, 31) == 366
        # 非闰年最后一天
        assert day_of_year(2023, 12, 31) == 365

    def test_doy_invalid_date(self):
        """无效日期检查."""
        from gps_time.converter import day_of_year

        # 无效月份
        with pytest.raises(ValueError):
            day_of_year(2024, 13, 1)

        with pytest.raises(ValueError):
            day_of_year(2024, 0, 1)

        # 无效日期（闰年2月29日有效，非闰年无效）
        with pytest.raises(ValueError):
            day_of_year(2023, 2, 29)

        # 无效日期（超过当月天数）
        with pytest.raises(ValueError):
            day_of_year(2024, 1, 32)

        with pytest.raises(ValueError):
            day_of_year(2024, 1, 0)

        with pytest.raises(ValueError):
            day_of_year(2024, 4, 31)  # 4月只有30天
