#!/usr/bin/env python3
"""Verify TOW calculation for the user's test cases."""

from datetime import datetime, timedelta

# GPS epoch
GPS_EPOCH = datetime(1980, 1, 6)
GPS_EPOCH_MJD = 44244
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800
LEAP_SECONDS = 18


def ymd_to_mjd(year, month, day, hour=0, minute=0, second=0):
    """Convert YMD to MJD using simplified algorithm."""
    day_frac = day + hour / 24.0 + minute / 1440.0 + second / 86400.0

    if month <= 2:
        y = year - 1
        m = month + 12
    else:
        y = year
        m = month

    mjd = int(365.25 * y) + int(30.6001 * (m + 1)) + day_frac - 679019
    return mjd


def calculate_tow(year, month, day, hour, minute, second):
    """Calculate GPS TOW manually."""
    mjd = ymd_to_mjd(year, month, day, hour, minute, second)
    diff_days = mjd - GPS_EPOCH_MJD

    week = int(diff_days // 7)
    tow = (diff_days - week * 7) * SECONDS_PER_DAY
    tow += LEAP_SECONDS

    if tow >= SECONDS_PER_WEEK:
        tow -= SECONDS_PER_WEEK
        week += 1

    dow = int(tow // SECONDS_PER_DAY)

    return {
        "mjd": mjd,
        "diff_days": diff_days,
        "week": week,
        "tow": tow,
        "dow": dow,
        "time_of_day": hour * 3600 + minute * 60 + second,
    }


# Test cases from user
print("=" * 60)
print("TOW Calculation Verification")
print("=" * 60)

test_cases = [
    (2026, 2, 13, 12, 0, 1, "User case 1: 2026-02-13 12:00:01"),
    (2026, 2, 13, 0, 0, 1, "User case 2: 2026-02-13 00:00:01"),
]

results = []
for year, month, day, hour, minute, second, desc in test_cases:
    result = calculate_tow(year, month, day, hour, minute, second)
    results.append(result)

    print(f"\n{desc}")
    print(f"  MJD: {result['mjd']:.6f}")
    print(f"  Days since epoch: {result['diff_days']:.6f}")
    print(f"  Week: {result['week']}")
    print(f"  DOW: {result['dow']}")
    print(f"  Time of day: {result['time_of_day']} seconds")
    print(f"  TOW: {result['tow']:.6f}")

# Compare
print("\n" + "=" * 60)
print("Comparison")
print("=" * 60)
tow_diff = results[0]["tow"] - results[1]["tow"]
time_diff = results[0]["time_of_day"] - results[1]["time_of_day"]

print(f"\nTOW difference: {tow_diff:.6f} seconds")
print(f"Time difference: {time_diff} seconds")
print(f"Expected difference (12 hours): 43200 seconds")
print(f"\nMatch: {'✓ YES' if abs(tow_diff - 43200) < 0.001 else '✗ NO'}")

# Calculate what TOW should be
print("\n" + "=" * 60)
print("Manual TOW verification")
print("=" * 60)
for i, (year, month, day, hour, minute, second, desc) in enumerate(test_cases):
    r = results[i]
    # TOW should be: DOW * 86400 + time_of_day + leap_seconds
    expected_tow = r["dow"] * SECONDS_PER_DAY + r["time_of_day"] + LEAP_SECONDS
    # Handle overflow
    if expected_tow >= SECONDS_PER_WEEK:
        expected_tow -= SECONDS_PER_WEEK

    print(f"\n{desc}")
    print(f"  DOW * 86400: {r['dow']} * 86400 = {r['dow'] * SECONDS_PER_DAY}")
    print(f"  Time of day: {r['time_of_day']}")
    print(f"  Leap seconds: {LEAP_SECONDS}")
    print(f"  Expected TOW: {expected_tow}")
    print(f"  Calculated TOW: {r['tow']:.6f}")
    print(f"  Match: {'✓' if abs(r['tow'] - expected_tow) < 0.001 else '✗'}")
