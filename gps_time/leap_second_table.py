"""Leap second table handling for GPS time conversions."""

import os
import platform
import shutil
from datetime import date as dt_date
from pathlib import Path
from typing import Optional, List, Tuple


def _get_config_dir() -> Path:
    """Get the system configuration directory for gps_time.

    Returns:
        Path to the configuration directory.
    """
    if platform.system() == "Windows":
        config_dir = Path(os.environ.get("APPDATA", Path.home())) / "gps_time"
    else:
        config_dir = Path.home() / ".config" / "gps_time"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _get_default_bsw_path() -> str:
    """Get the default BSW file path.

    Checks in order:
    1. Environment variable GPS_LEAP_SECOND_FILE
    2. System config directory (APP_DATA/gps_time/GPSUTC.BSW or ~/.config/gps_time/GPSUTC.BSW)
    3. Package directory (fallback)

    If the config directory doesn't have the file but package directory does,
    copy it to config directory for future updates.

    Returns:
        Absolute path to the GPSUTC.BSW file.
    """
    # 1. Check environment variable
    env_path = os.environ.get("GPS_LEAP_SECOND_FILE")
    if env_path and os.path.exists(env_path):
        return os.path.abspath(env_path)

    # 2. Check system config directory
    config_dir = _get_config_dir()
    config_bsw = config_dir / "GPSUTC.BSW"

    # 3. Package directory (built-in fallback)
    package_bsw = Path(__file__).parent.parent / "GPSUTC.BSW"

    # If config doesn't exist but package does, copy it
    if not config_bsw.exists() and package_bsw.exists():
        shutil.copy2(str(package_bsw), str(config_bsw))

    # Use config if it exists, otherwise package
    if config_bsw.exists():
        return str(config_bsw.absolute())
    elif package_bsw.exists():
        return str(package_bsw.absolute())
    else:
        # Return config path anyway (will fail with FileNotFoundError later)
        return str(config_bsw.absolute())


class LeapSecondTable:
    """A class for managing GPS leap second data from BSW files.

    This class parses GPSUTC.BSW files and provides methods to query
    the leap second value for any given date.
    """

    def __init__(self, bsw_path: Optional[str] = None):
        """Initialize the LeapSecondTable.

        Args:
            bsw_path: Path to GPSUTC.BSW file. If None, uses default location:
                      - Environment variable GPS_LEAP_SECOND_FILE, or
                      - System config directory (APPDATA/gps_time/ or ~/.config/gps_time/), or
                      - Package directory (fallback)
        """
        if bsw_path is None:
            bsw_path = _get_default_bsw_path()
        self.bsw_path = os.path.abspath(bsw_path)
        self.leap_seconds: List[Tuple[dt_date, int]] = []
        self._parse()

    def _parse(self) -> None:
        """Parse the BSW file and populate leap seconds data."""
        with open(self.bsw_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("DIFFERENCE") or line.startswith("-----"):
                continue
            if "GPS-UTC" in line or "VALID SINCE" in line or "(SEC)" in line:
                continue

            parts = line.split()
            if len(parts) >= 7:
                leap_second = int(float(parts[0]))
                year = int(parts[1])
                month = int(parts[2])
                day = int(parts[3])
                valid_since = dt_date(year, month, day)
                self.leap_seconds.append((valid_since, leap_second))

    def get_leap_second(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        date: Optional[dt_date] = None,
    ) -> int:
        """Get the leap second value for a given date.

        Args:
            year: Year component of the query date.
            month: Month component of the query date (1-12).
            day: Day component of the query date.
            date: Alternative to year/month/day, a date object.

        Returns:
            The leap second value (seconds) valid at the query date.

        Raises:
            ValueError: If neither date nor year/month/day is provided.
        """
        if date is not None:
            query_date = date
        elif year is not None and month is not None and day is not None:
            query_date = dt_date(year, month, day)
        else:
            raise ValueError("Either date or year/month/day must be provided")

        result = self.leap_seconds[0][1]
        for valid_since, leap_second in self.leap_seconds:
            if query_date >= valid_since:
                result = leap_second

        return result
