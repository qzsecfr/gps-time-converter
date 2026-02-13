"""Command-line interface for GPS Time Converter.

This module provides the CLI interface for converting between various
time formats including UTC, GPS, MJD, BJT, DOY, and TOD.
"""

import click
from datetime import datetime, date as dt_date
import json

from gps_time.converter import (
    ymd_to_mjd,
    mjd_to_ymd,
    day_of_year,
    time_of_day,
    utc_to_bjt_datetime,
    bjt_to_utc_datetime,
    utc_to_gps_datetime,
    gps_to_utc_datetime,
    ymd_to_doy_with_fraction,
    doy_to_ymd_with_fraction,
)
from gps_time.leap_second_table import LeapSecondTable

GPS_EPOCH = dt_date(1980, 1, 6)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """GPS Time Converter - Convert between UTC and GPS time formats."""
    pass


@click.command()
@click.option("--now", is_flag=True, help="Show current time in all formats")
@click.option(
    "--datetime",
    "datetime_str",
    type=str,
    help="Convert specific datetime (format: YYYY-MM-DD HH:MM:SS)",
)
@click.option(
    "--year-doy",
    "year_doy",
    type=str,
    help="Convert from Year and Day of Year (format: YYYY,DOY where DOY can be fractional)",
)
@click.option(
    "--mjd",
    "mjd_input",
    type=float,
    help="Convert from Modified Julian Date",
)
@click.option(
    "--bjt",
    "bjt_str",
    type=str,
    help="Convert from Beijing Time (format: YYYY-MM-DD HH:MM:SS)",
)
@click.option(
    "--gps-week-dow",
    "gps_week_dow",
    type=str,
    help="Convert from GPS Week and Day of Week (format: WEEK,DOW)",
)
@click.option(
    "--gps-week-tow",
    "gps_week_tow",
    type=str,
    help="Convert from GPS Week and Time of Week (format: WEEK,TOW where TOW can be fractional)",
)
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.option(
    "--leap-second-file",
    "leap_file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to GPSUTC.BSW leap second file (default: use system config or bundled)",
)
def convert(
    now: bool,
    datetime_str: str,
    year_doy: str,
    mjd_input: float,
    bjt_str: str,
    gps_week_dow: str,
    gps_week_tow: str,
    json_output: bool,
    leap_file: str,
):
    """Show time in various GPS time formats.

    Displays the input time in multiple formats: UTC, BJT, MJD, DOY, TOD,
    GPS Week, DOW, and TOW.
    """
    year = month = day = hour = minute = second = 0

    # Count input options
    input_options = [
        now,
        datetime_str is not None,
        year_doy is not None,
        mjd_input is not None,
        bjt_str is not None,
        gps_week_dow is not None,
        gps_week_tow is not None,
    ]

    if sum(input_options) == 0:
        raise click.ClickException(
            "Please specify an input time: --now, --datetime, --year-doy, --mjd, --bjt, --gps-week-dow, or --gps-week-tow"
        )

    if sum(input_options) > 1:
        raise click.ClickException(
            "Cannot use multiple input options at the same time. Please specify only one."
        )

    # Determine the UTC time to convert
    if now:
        now_utc = datetime.utcnow()
        year = now_utc.year
        month = now_utc.month
        day = now_utc.day
        hour = now_utc.hour
        minute = now_utc.minute
        second = now_utc.second + now_utc.microsecond / 1_000_000.0
    elif datetime_str:
        # Parse datetime string
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            year = dt.year
            month = dt.month
            day = dt.day
            hour = dt.hour
            minute = dt.minute
            second = dt.second + dt.microsecond / 1_000_000.0
        except ValueError:
            raise click.ClickException(
                f"Invalid datetime format: {datetime_str}. Expected format: YYYY-MM-DD HH:MM:SS"
            )
    elif year_doy:
        # Parse Year,DOY format
        try:
            parts = year_doy.split(",")
            if len(parts) != 2:
                raise ValueError()
            year = int(parts[0])
            doy = float(parts[1])
            year, month, day, hour, minute, second = doy_to_ymd_with_fraction(year, doy)
        except ValueError:
            raise click.ClickException(
                f"Invalid format: {year_doy}. Expected format: YYYY,DOY (e.g., 2024,15.5)"
            )
    elif mjd_input is not None:
        # Convert from MJD
        try:
            year, month, day, hour, minute, second = mjd_to_ymd(mjd_input)
        except (ValueError, TypeError) as e:
            raise click.ClickException(f"Invalid MJD: {mjd_input}. Error: {e}")
    elif bjt_str:
        # Parse BJT datetime and convert to UTC
        try:
            dt = datetime.strptime(bjt_str, "%Y-%m-%d %H:%M:%S")
            year, month, day, hour, minute, second = bjt_to_utc_datetime(
                dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
            )
        except ValueError:
            raise click.ClickException(
                f"Invalid datetime format: {bjt_str}. Expected format: YYYY-MM-DD HH:MM:SS"
            )
    elif gps_week_tow:
        # Parse WEEK,TOW format
        try:
            parts = gps_week_tow.split(",")
            if len(parts) != 2:
                raise ValueError()
            week = int(parts[0])
            tow = float(parts[1])
            # Get leap seconds (need to determine date first for leap second lookup)
            # First convert without leap seconds to get approximate date
            year, month, day, hour, minute, second = gps_to_utc_datetime(
                week, tow, leap_seconds=0
            )
            # Now get actual leap seconds for that date
            leap_table = LeapSecondTable(leap_file)
            leap_seconds = leap_table.get_leap_second(year, month, day)
            # Convert again with correct leap seconds
            year, month, day, hour, minute, second = gps_to_utc_datetime(
                week, tow, leap_seconds
            )
        except ValueError as e:
            raise click.ClickException(
                f"Invalid format: {gps_week_tow}. Expected format: WEEK,TOW (e.g., 2405,475219.5). Error: {e}"
            )
    elif gps_week_dow:
        # Parse WEEK,DOW format
        try:
            parts = gps_week_dow.split(",")
            if len(parts) != 2:
                raise ValueError()
            week = int(parts[0])
            dow = int(parts[1])
            # Calculate TOW from DOW (DOW * 86400 seconds)
            tow = dow * 86400.0
            # Get leap seconds
            year, month, day, hour, minute, second = gps_to_utc_datetime(
                week, tow, leap_seconds=0
            )
            leap_table = LeapSecondTable(leap_file)
            leap_seconds = leap_table.get_leap_second(year, month, day)
            year, month, day, hour, minute, second = gps_to_utc_datetime(
                week, tow, leap_seconds
            )
        except ValueError as e:
            raise click.ClickException(
                f"Invalid format: {gps_week_dow}. Expected format: WEEK,DOW (e.g., 2405,5). Error: {e}"
            )

    # Check GPS epoch boundary
    input_date = dt_date(year, month, day)
    if input_date < GPS_EPOCH:
        click.echo("Warning: Date is before GPS epoch (1980-01-06)", err=True)

    # Get leap seconds for current date
    try:
        leap_table = LeapSecondTable(leap_file)
    except FileNotFoundError:
        raise click.ClickException(
            f"GPSUTC.BSW file not found: {leap_file or 'default locations'}"
        )

    if leap_table.leap_seconds and input_date > leap_table.leap_seconds[-1][0]:
        click.echo(
            "Warning: Date is beyond leap second table, using latest value",
            err=True,
        )

    leap_seconds = leap_table.get_leap_second(year, month, day)

    # Calculate all formats
    mjd = ymd_to_mjd(year, month, day, hour, minute, second)
    doy = day_of_year(year, month, day)
    tod = time_of_day(hour, minute, second)
    bjt = utc_to_bjt_datetime(year, month, day, hour, minute, second)
    week, tow, dow = utc_to_gps_datetime(
        year, month, day, hour, minute, second, leap_seconds
    )

    # Format output
    utc_str = (
        f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{int(second):02d}"
    )
    bjt_str = f"{bjt[0]:04d}-{bjt[1]:02d}-{bjt[2]:02d} {bjt[3]:02d}:{bjt[4]:02d}:{int(bjt[5]):02d}"

    if json_output:
        result = {
            "utc": utc_str,
            "bjt": bjt_str,
            "mjd": mjd,
            "doy": doy,
            "tod": tod,
            "week": week,
            "dow": dow,
            "tow": tow,
        }
        click.echo(json.dumps(result, indent=2))
    else:
        # Human-readable table format
        lines = [
            f"UTC:  {utc_str}",
            f"BJT:  {bjt_str}",
            f"MJD:  {mjd}",
            f"DOY:  {doy}",
            f"TOD:  {tod}",
            f"WEEK: {week}",
            f"DOW:  {dow}",
            f"TOW:  {tow}",
        ]
        for line in lines:
            click.echo(line)


# Register the convert command
cli.add_command(convert)


def main():
    cli()


if __name__ == "__main__":
    main()
