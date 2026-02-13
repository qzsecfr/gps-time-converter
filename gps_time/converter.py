"""MJD ↔ YMD conversion utilities and Time of Day calculations."""

from typing import Tuple

# GPS epoch: 1980-01-06 00:00:00 UTC (MJD 44244)
GPS_EPOCH_MJD = 44244.0
# Seconds in a week
SECONDS_PER_WEEK = 604800.0
# Seconds in a day
SECONDS_PER_DAY = 86400.0

# Type aliases
Year = int
Month = int
Day = int
Hour = int
Minute = int
Second = float
GPSWeek = int
TOW = float
DOW = int


def ymd_to_mjd(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0
) -> float:
    """Convert year-month-day to Modified Julian Date.

    Uses Hoffman algorithm for YMD → MJD conversion.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59.999..., can have fractional part)

    Returns:
        Modified Julian Date as float

    Raises:
        ValueError: If any input is out of valid range
    """
    # Validate inputs
    _validate_ymd_datetime(year, month, day, hour, minute, second)

    # Calculate fractional day
    day_frac = day + hour / 24.0 + minute / 1440.0 + second / 86400.0

    # Adjust for January and February
    if month <= 2:
        y = year - 1
        m = month + 12
    else:
        y = year
        m = month

    year_frac = 365.25 * y
    frac = year_frac - int(year_frac)
    a = int(year_frac + 0.5) if frac == 0.5 else int(year_frac)
    b = int(30.6001 * (m + 1))
    mjd = a + b + day_frac - 679019

    return mjd


def mjd_to_ymd(mjd: float) -> Tuple[int, int, int, int, int, float]:
    """Convert Modified Julian Date to year-month-day.

    Uses astronomical algorithm for MJD → YMD conversion.

    Args:
        mjd: Modified Julian Date as float

    Returns:
        Tuple of (year, month, day, hour, minute, second)
    """
    jd = mjd + 2400000.5

    # Julian day number and fraction
    j = int(jd + 0.5)
    f = jd + 0.5 - j

    # Gregorian calendar correction
    if j >= 2299161:
        a = int((j - 1867216.25) / 36524.25)
        j = j + 1 + a - int(a / 4)

    # Calculate year, month, day
    b = j + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)

    day = b - d - int(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    # Calculate time from fraction
    total_seconds = f * 86400
    hour = int(total_seconds // 3600)
    remaining = total_seconds % 3600
    minute = int(remaining // 60)
    second = remaining % 60

    return year, month, day, hour, minute, second


def _validate_ymd_datetime(
    year: int, month: int, day: int, hour: int, minute: int, second: float
) -> None:
    """Validate YMD datetime components.

    Args:
        year: Year to validate
        month: Month to validate (1-12)
        day: Day to validate (1-31, depends on month/year)
        hour: Hour to validate (0-23)
        minute: Minute to validate (0-59)
        second: Second to validate (0-60 for leap second)

    Raises:
        ValueError: If any component is out of valid range
    """
    if not (1 <= month <= 12):
        raise ValueError(f"Month must be between 1 and 12, got {month}")

    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be between 0 and 23, got {hour}")

    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be between 0 and 59, got {minute}")

    if not (0 <= second < 60):
        raise ValueError(f"Second must be between 0 and 60, got {second}")

    # Validate day based on month and year
    max_days = _days_in_month(year, month)
    if not (1 <= day <= max_days):
        raise ValueError(
            f"Day must be between 1 and {max_days} for {year}-{month}, got {day}"
        )


def day_of_year(year: int, month: int, day: int) -> int:
    """Calculate the day of year (DOY) for a given date.

    DOY (Day of Year) is the day number from the start of the year,
    where January 1st is day 1.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day of month (1-31, depends on month/year)

    Returns:
        Day of year (1-366)

    Raises:
        ValueError: If date is invalid
    """
    # Validate the date
    _validate_ymd_datetime(year, month, day, 0, 0, 0)

    # Days in each month (index 0 is unused)
    month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Calculate DOY
    doy = day
    for m in range(1, month):
        doy += month_days[m]

    # Add leap day for leap years if after February
    if month > 2 and _is_leap_year(year):
        doy += 1

    return doy


def _is_leap_year(year: int) -> bool:
    """Check if a year is a leap year.

    Args:
        year: Year to check

    Returns:
        True if leap year, False otherwise
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _days_in_month(year: int, month: int) -> int:
    """Get the number of days in a month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Number of days in the month
    """
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month in (4, 6, 9, 11):
        return 30
    elif month == 2:
        return 29 if _is_leap_year(year) else 28
    return 30  # Should not reach here due to month validation


def time_of_day(hour: int, minute: int, second: float) -> float:
    """Calculate Time of Day (TOD) in seconds from hour, minute, second.

    TOD (Time of Day) represents the number of seconds elapsed
    since midnight of the current day.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59.999..., can have fractional part)

    Returns:
        Time of Day in seconds (0.0 to 86399.999...)

    Raises:
        ValueError: If any time component is out of valid range
    """
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be between 0 and 23, got {hour}")

    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be between 0 and 59, got {minute}")

    if not (0 <= second < 60):
        raise ValueError(f"Second must be between 0 and 60, got {second}")

    return hour * 3600 + minute * 60 + second


def utc_to_bjt_datetime(
    year: int, month: int, day: int, hour: int, minute: int, second: float
) -> Tuple[int, int, int, int, int, float]:
    """Convert UTC datetime to Beijing Time (BJT, UTC+8).

    BJT (Beijing Time) is UTC+8 hours. This function handles day overflow
    when the UTC time is late in the day.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour in UTC (0-23)
        minute: Minute (0-59)
        second: Second (0-59.999...)

    Returns:
        Tuple of (year, month, day, hour, minute, second) in BJT
    """
    # Convert UTC time to total seconds since midnight, add 8 hours offset
    total_seconds = hour * 3600 + minute * 60 + second + 8 * 3600

    # Calculate day offset and time of day
    day_offset = int(total_seconds // 86400)
    tod = total_seconds % 86400

    # Convert TOD back to hour, minute, second
    new_hour = int(tod // 3600)
    remaining = tod % 3600
    new_minute = int(remaining // 60)
    new_second = remaining % 60

    # Apply day offset using MJD conversion
    mjd = ymd_to_mjd(year, month, day, 0, 0, 0)
    new_year, new_month, new_day, *_ = mjd_to_ymd(mjd + day_offset)

    return new_year, new_month, new_day, new_hour, new_minute, new_second


def utc_to_gps_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: float,
    leap_seconds: int = 18,
) -> Tuple[int, float, int]:
    """Convert UTC datetime to GPS time (week, TOW, DOW).

    GPS time starts at 1980-01-06 00:00:00 UTC (MJD 44244).
    GPS Week: weeks since GPS epoch
    TOW (Time of Week): seconds within the week (0-604799)
    DOW (Day of Week): day within the week (0-6)

    GPS time = UTC time + leap_seconds

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour in UTC (0-23)
        minute: Minute (0-59)
        second: Second (0-59.999...)
        leap_seconds: Leap seconds offset (default 18)

    Returns:
        Tuple of (week, tow, dow) where:
        - week: GPS week number (integer)
        - tow: Time of week in seconds (float, 0.0 to 604799.999...)
        - dow: Day of week (0-6, where 0=Sunday)
    """
    mjd = ymd_to_mjd(year, month, day, hour, minute, second)
    diff_days = mjd - GPS_EPOCH_MJD

    week = int(diff_days // 7)
    tow = (diff_days - week * 7) * SECONDS_PER_DAY
    tow += leap_seconds

    if tow >= SECONDS_PER_WEEK:
        tow -= SECONDS_PER_WEEK
        week += 1

    dow = int(tow // SECONDS_PER_DAY)

    return week, tow, dow


def gps_to_utc_datetime(
    week: int, tow: float, leap_seconds: int = 18
) -> Tuple[int, int, int, int, int, float]:
    """Convert GPS time (week, tow) to UTC datetime.

    Args:
        week: GPS week number
        tow: Time of week in seconds (0 to 604799)
        leap_seconds: Current leap second difference (GPS - UTC)

    Returns:
        Tuple of (year, month, day, hour, minute, second) in UTC
    """
    # Subtract leap seconds to get UTC time of week
    utc_tow = tow - leap_seconds

    # Handle underflow (previous week)
    utc_week = week
    if utc_tow < 0:
        utc_tow += 604800
        utc_week -= 1

    # Calculate total days from GPS epoch
    total_days = utc_week * 7 + utc_tow / 86400.0
    mjd = 44244 + total_days

    # Convert MJD back to YMD
    return mjd_to_ymd(mjd)


def ymd_to_doy_with_fraction(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0
) -> float:
    """Convert YMD to DOY with fractional day.

    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23), default 0
        minute: Minute (0-59), default 0
        second: Second (0-59), default 0

    Returns:
        Day of year as float (e.g., 45.5 for noon on day 45)
    """
    doy = day_of_year(year, month, day)
    fraction = (hour * 3600 + minute * 60 + second) / 86400.0
    return doy + fraction


def doy_to_ymd_with_fraction(
    year: int, doy_fraction: float
) -> Tuple[int, int, int, int, int, float]:
    """Convert DOY with fractional day to YMD.

    Args:
        year: Year
        doy_fraction: Day of year as float (e.g., 45.5 for noon on day 45)

    Returns:
        Tuple of (year, month, day, hour, minute, second)
    """
    doy = int(doy_fraction)
    fraction = doy_fraction - doy

    # Convert DOY to month and day
    month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if _is_leap_year(year):
        month_days[2] = 29

    remaining_doy = doy
    month = 1
    for m in range(1, 13):
        days_in_m = month_days[m]
        if remaining_doy <= days_in_m:
            month = m
            day = remaining_doy
            break
        remaining_doy -= days_in_m
    else:
        month = 12
        day = remaining_doy

    # Convert fraction to time
    total_seconds = fraction * 86400
    hour = int(total_seconds // 3600)
    remaining = total_seconds % 3600
    minute = int(remaining // 60)
    second = remaining % 60

    return year, month, day, hour, minute, second


def bjt_to_utc_datetime(
    year: int, month: int, day: int, hour: int, minute: int, second: float
) -> Tuple[int, int, int, int, int, float]:
    """Convert Beijing Time (UTC+8) to UTC datetime.

    Args:
        year: Year in BJT
        month: Month in BJT (1-12)
        day: Day in BJT (1-31)
        hour: Hour in BJT (0-23)
        minute: Minute in BJT (0-59)
        second: Second in BJT (0-59)

    Returns:
        Tuple of (year, month, day, hour, minute, second) in UTC
    """
    # Convert BJT to total seconds
    bjt_total_seconds = hour * 3600 + minute * 60 + second
    utc_total_seconds = bjt_total_seconds - 8 * 3600

    # Calculate day offset
    day_offset = utc_total_seconds // 86400
    utc_seconds_of_day = utc_total_seconds % 86400

    if utc_seconds_of_day < 0:
        utc_seconds_of_day += 86400
        day_offset -= 1

    # Convert seconds to HMS
    utc_hour = int(utc_seconds_of_day // 3600)
    utc_minute = int((utc_seconds_of_day % 3600) // 60)
    utc_second = utc_seconds_of_day % 60

    # Adjust date using MJD
    bjt_mjd = ymd_to_mjd(year, month, day, 0, 0, 0)
    utc_mjd = bjt_mjd + day_offset
    utc_year, utc_month, utc_day, _, _, _ = mjd_to_ymd(utc_mjd)

    return utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second
