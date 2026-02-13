"""Tests for CLI functionality."""

import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from gps_time.cli import convert


class TestNowCommand:
    """Test gps-time --now command."""

    def test_now_output_contains_required_fields(self):
        """Test --now output contains all required fields."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--now"])

        assert result.exit_code == 0
        output = result.output

        assert "UTC:" in output
        assert "BJT:" in output
        assert "MJD:" in output
        assert "DOY:" in output
        assert "TOD:" in output
        assert "WEEK:" in output
        assert "DOW:" in output
        assert "TOW:" in output

    def test_now_json_output_valid_json(self):
        """Test --now --json outputs valid JSON."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--now", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)

        assert "utc" in data
        assert "bjt" in data
        assert "mjd" in data
        assert "doy" in data
        assert "tod" in data
        assert "week" in data
        assert "dow" in data
        assert "tow" in data

    def test_now_json_output_types(self):
        """Test --now --json output has correct types."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--now", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)

        assert isinstance(data["utc"], str)
        assert isinstance(data["bjt"], str)
        assert isinstance(data["mjd"], float)
        assert isinstance(data["doy"], int)
        assert isinstance(data["tod"], (int, float))
        assert isinstance(data["week"], int)
        assert isinstance(data["dow"], int)
        assert isinstance(data["tow"], (int, float))

    def test_now_json_utc_format(self):
        """Test UTC time format in JSON output."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--now", "--json"])

        data = json.loads(result.stdout)

        assert " " in data["utc"]
        date_part, time_part = data["utc"].split(" ")
        assert "-" in date_part
        assert ":" in time_part

    def test_now_without_flag_error(self):
        """Test running without --now or --datetime produces error."""
        runner = CliRunner()
        result = runner.invoke(convert, [])

        assert result.exit_code == 1
        assert "Please specify an input time" in result.output


class TestDateTimeCommand:
    """Test gps-time --datetime command."""

    def test_datetime_output_contains_required_fields(self):
        """Test --datetime output contains all required fields."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "2024-01-15 12:30:45"])

        assert result.exit_code == 0
        output = result.output

        assert "UTC:" in output
        assert "BJT:" in output
        assert "MJD:" in output
        assert "DOY:" in output
        assert "TOD:" in output
        assert "WEEK:" in output
        assert "DOW:" in output
        assert "TOW:" in output

    def test_datetime_output_correct_datetime(self):
        """Test --datetime outputs the correct datetime."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "2024-01-15 12:30:45"])

        assert result.exit_code == 0
        assert "UTC:  2024-01-15 12:30:45" in result.output

    def test_datetime_json_output_valid_json(self):
        """Test --datetime --json outputs valid JSON."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "2024-01-15 12:30:45", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)

        assert "utc" in data
        assert "bjt" in data
        assert "mjd" in data
        assert "doy" in data
        assert "tod" in data
        assert "week" in data
        assert "dow" in data
        assert "tow" in data
        assert data["utc"] == "2024-01-15 12:30:45"

    def test_datetime_invalid_format_error(self):
        """Test --datetime with invalid format returns error."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "invalid-date"])

        assert result.exit_code == 1

    def test_datetime_and_now_mutually_exclusive(self):
        """Test --datetime and --now cannot be used together."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--now", "--datetime", "2024-01-15 12:30:45"])

        assert result.exit_code == 1
        assert "Cannot use multiple input options" in result.output


class TestBoundaryConditions:
    def test_date_before_gps_epoch_shows_warning(self):
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "1970-01-01 00:00:00"])

        assert result.exit_code == 0
        assert "Warning: Date is before GPS epoch" in result.stderr

    def test_date_before_gps_epoch_still_produces_output(self):
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "1970-01-01 00:00:00"])

        assert result.exit_code == 0
        assert "UTC:" in result.stdout
        assert "MJD:" in result.stdout

    def test_future_date_uses_latest_leap_second(self):
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "2030-01-01 00:00:00"])

        assert result.exit_code == 0
        assert "Warning: Date is beyond leap second table" in result.stderr
        assert "UTC:" in result.stdout
        assert "WEEK:" in result.stdout

    def test_future_date_json_output(self):
        runner = CliRunner()
        result = runner.invoke(convert, ["--datetime", "2030-01-01 00:00:00", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "week" in data
        assert data["week"] > 0
        assert "Warning: Date is beyond leap second table" in result.stderr

    def test_missing_bsw_file_shows_error(self):
        runner = CliRunner()
        with patch(
            "gps_time.cli.LeapSecondTable",
            side_effect=FileNotFoundError("not found"),
        ):
            result = runner.invoke(convert, ["--datetime", "2024-01-15 12:30:45"])

        assert result.exit_code == 1
        assert "GPSUTC.BSW file not found" in result.output
