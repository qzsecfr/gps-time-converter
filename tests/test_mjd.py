"""Tests for MJD ↔ YMD conversion."""

import pytest


class TestMjdYmdConversion:
    """Test MJD ↔ YMD bidirectional conversion."""

    def test_mjd_ymd_roundtrip(self):
        """MJD 0 ↔ 1858-11-17 双向转换."""
        from gps_time.converter import mjd_to_ymd, ymd_to_mjd

        # MJD 0 = 1858-11-17 00:00:00
        mjd_in = 0.0
        year, month, day, hour, minute, second = mjd_to_ymd(mjd_in)
        assert year == 1858
        assert month == 11
        assert day == 17
        assert hour == 0
        assert minute == 0
        assert second == pytest.approx(0.0, abs=1e-9)

        # 反向转换
        mjd_out = ymd_to_mjd(year, month, day, hour, minute, second)
        assert mjd_out == pytest.approx(mjd_in, abs=1e-9)

    def test_mjd_to_ymd(self):
        """MJD 44244 → 1980-01-06 (GPS纪元)."""
        from gps_time.converter import mjd_to_ymd

        year, month, day, hour, minute, second = mjd_to_ymd(44244.0)
        assert year == 1980
        assert month == 1
        assert day == 6
        assert hour == 0
        assert minute == 0
        assert second == pytest.approx(0.0, abs=1e-9)

    def test_ymd_to_mjd(self):
        """2024-01-01 → MJD 60310."""
        from gps_time.converter import ymd_to_mjd

        mjd = ymd_to_mjd(2024, 1, 1, 0, 0, 0)
        assert mjd == pytest.approx(60310.0, abs=1e-9)

    def test_mjd_fractional_day(self):
        """测试小数天处理."""
        from gps_time.converter import mjd_to_ymd, ymd_to_mjd

        # MJD 44244.5 = 1980-01-06 12:00:00
        year, month, day, hour, minute, second = mjd_to_ymd(44244.5)
        assert year == 1980
        assert month == 1
        assert day == 6
        assert hour == 12
        assert minute == 0
        assert second == pytest.approx(0.0, abs=1e-9)

        # 反向转换
        mjd = ymd_to_mjd(1980, 1, 6, 12, 0, 0)
        assert mjd == pytest.approx(44244.5, abs=1e-9)

        # 测试带秒的小数
        mjd2 = ymd_to_mjd(1980, 1, 6, 12, 30, 45.5)
        expected = 44244.0 + 12 / 24 + 30 / 1440 + 45.5 / 86400
        assert mjd2 == pytest.approx(expected, abs=1e-9)

    def test_invalid_date(self):
        """边界检查 - 无效日期."""
        from gps_time.converter import ymd_to_mjd

        # 无效月份
        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 13, 1)

        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 0, 1)

        # 无效日期
        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 1, 32)

        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 1, 0)

        # 无效时间
        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 1, 1, 25, 0, 0)

        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 1, 1, 0, 60, 0)

        with pytest.raises(ValueError):
            ymd_to_mjd(2024, 1, 1, 0, 0, 60)

    def test_mjd_0_roundtrip_exact(self):
        """MJD 0 精确往返测试."""
        from gps_time.converter import mjd_to_ymd, ymd_to_mjd

        # MJD 0 精确值
        year, month, day, hour, minute, second = mjd_to_ymd(0.0)
        mjd_back = ymd_to_mjd(year, month, day, hour, minute, second)
        assert mjd_back == pytest.approx(0.0, abs=1e-9)

    def test_gps_epoch_roundtrip(self):
        """GPS纪元精确往返测试."""
        from gps_time.converter import mjd_to_ymd, ymd_to_mjd

        # GPS纪元: MJD 44244 = 1980-01-06
        year, month, day, hour, minute, second = mjd_to_ymd(44244.0)
        mjd_back = ymd_to_mjd(year, month, day, hour, minute, second)
        assert mjd_back == pytest.approx(44244.0, abs=1e-9)

    def test_ymd_with_fractional_seconds(self):
        """测试带小数秒的转换."""
        from gps_time.converter import mjd_to_ymd, ymd_to_mjd

        # 测试小数秒
        mjd_in = ymd_to_mjd(2024, 6, 15, 10, 30, 45.123456)
        year, month, day, hour, minute, second = mjd_to_ymd(mjd_in)

        assert year == 2024
        assert month == 6
        assert day == 15
        assert hour == 10
        assert minute == 30
        assert second == pytest.approx(45.123456, abs=1e-4)
