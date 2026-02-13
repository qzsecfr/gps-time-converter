ulw 我需要一个GPS时间转换的小工具，方便调用，我的设想是这样的：

小工具需要实现的功能如下：

1. 小工具需要能进行UTC时间、GPS时间之间的互相转换；
2. 小工具需要根据用户的输入参数直接输出所有的时间类型/格式；
3. 小工具具备根据系统当前时间显式所有时间类型/格式的能力。

首先在此对各种所需的时间类型进行说明：

所有项目所需的时间类型包括：

1. UTC时间（UTC）、北京时间（BJT）
2. 简化儒略日（MJD）
3. 年（YEAR）、年积日（DOY）、天内秒（TOD）
4. GPS周（WEEK）、周内天（DOW）、周内秒（TOW）

以UTC时间的`2026/02/13 11:48:00`为例：

1. UTC时间即为格林尼治的地方时，也是全球标准的世界时（时区为0，简写为`UTC+0`），其格式形如：`2026/02/13 11:48:00`；对应的北京时间（时区为东8区，简写为`UTC+8`）为在UTC的时间上再加8小时，即`2026/02/13 19:48:00`。UTC不连续，使用闰秒机制进行调整，需要有一个闰秒调整的表作为先验信息，由用户维护。
2. 简化儒略日是一个连续的时间计数，单位为“日”，其小数部分代表不足一天的时间，起算点为1858年11月17日的子夜时刻。
3. 年、年积日和天内秒选取UTC为计算基准，年即为UTC的年，年积日为从UTC当年的1月1日为第1天（DOY=1），一直推算到UTC时间所在的天数，天内秒即为当前时刻在一天内的秒数。
4. GPS周和周内天及周内秒是GPS系统使用的连续的时间系统，起算点为UTC+0的1980年1月6日0时0分0秒，其计数是连续的，没有闰秒机制。

为了简化工具的逻辑，建议采用“公历日期+MJD”作为核心枢纽，所有格式先转换为MJD/公历日期，再转换为目标格式。

1. 首先将公历日期（Year，Month，Day）转换为年积日（DOY），需要考虑闰年的判断。使用`$$\text{IsLeap} = (Year \% 4 == 0 \land Year \% 100 \neq 0) \lor (Year \% 400 == 0)$$`，然后累加当前月之前所有月份的天数，再补加当天的日期Day。（如果是闰年且`Month > 2`时，DOY还需要再 +1）。
2. 然后使用简化版的Hoffman算法，将UTC时间（Year，Month，Day）转化为MJD：在此处，Day包含小数部分的天内秒，例如正午（12:00:00）对应的Day的小数部分为0.5（$Day$ 如果包含时间，则 $Day = \text{Day} + \text{Hour}/24.0 + \text{Minute}/1440.0 + \text{Second}/86400.0$。）。如果`Month <= 2`，`y = Year - 1, m = Month + 12`，否则，`y = Year, m = Month`；MJD的计算为$$MJD = \lfloor 365.25 \times y \rfloor + \lfloor 30.6001 \times (m + 1) \rfloor + D - 679019$$，其中$\lfloor x \rfloor$ 表示取整（floor）。
3. 将MJD转换为YMD的算法比较复杂，建议直接使用编程语言的时间库（如 Python 的 astropy 或 gnsscal），或参考标准天文算法。
4. 接下来从MJD计算GPS时间。由于GPS 起算点（1980-01-06）对应的 MJD 为 44244，首先计算自 GPS 起算点经过的总天数：$$\Delta Days = MJD - 44244$$，然后计算 GPS Week：$$\text{GPS\_Week} = \lfloor \frac{\Delta Days}{7} \rfloor$$，再计算周内秒 (TOW)：$$\text{TOW} = (\Delta Days - \text{GPS\_Week} \times 7) \times 86400 + \text{Seconds\_of\_Day}$$。注意：这里的 MJD 通常带小数部分，TOW 也是浮点数。最后计算 Day of Week：$$\text{DOW} = \lfloor \frac{\text{TOW}}{86400} \rfloor$$。
5. 最后是将UTC转换为GPS时，数学转换上它们只差闰秒，但逻辑上必须处理这个跳变：$$GPS = UTC + \Delta t_{LS}$$。如果输入是 UTC 时间，先将其转换为 MJD，然后计算出 GPS 时间。但是，这样计算出的 GPS 时间实际上是“UTC 时的 GPS 表示”，因此必须在最终的秒数上加上当前的闰秒值，才能得到真实的 GPS 系统时间。该表由用户维护更新。

核心算法和逻辑可以参考下面的Python实现：
```python
import math
from datetime import datetime, timedelta

class TimeConverter:
    def __init__(self):
        # GPS 起始时间的 MJD (1980-01-06)
        self.MJD_GPS_EPOCH = 44244
        # 当前闰秒 (GPS - UTC)，实际应用中应维护一个查找表
        self.LEAP_SECONDS = 18 

    def ymd_to_mjd(self, year, month, day, hour=0, min=0, sec=0):
        """公历转 MJD"""
        # 将时间转换为日的小数部分
        day_frac = day + hour/24.0 + min/1440.0 + sec/86400.0
        
        if month <= 2:
            y = year - 1
            m = month + 12
        else:
            y = year
            m = month
            
        # Hoffman 算法
        mjd = int(365.25 * y) + int(30.6001 * (m + 1)) + day_frac - 679019
        return mjd

    def mjd_to_ymd(self, mjd):
        """MJD 转公历 (返回 datetime 对象)"""
        jd = mjd + 2400000.5
        j = int(jd + 0.5)
        f = jd + 0.5 - j
        
        if j >= 2299161:
            a = int((j - 1867216.25) / 36524.25)
            j += 1 + a - int(a / 4)
            
        b = j + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        
        day_int = b - d - int(30.6001 * e)
        
        if e < 14:
            month = e - 1
        else:
            month = e - 13
            
        if month > 2:
            year = c - 4716
        else:
            year = c - 4715
            
        # 处理小数天转时分秒
        total_seconds = f * 86400
        hour = int(total_seconds // 3600)
        minute = int((total_seconds % 3600) // 60)
        second = total_seconds % 60
        
        # 注意：这里返回的是 UTC 时间尺度下的 YMD
        return datetime(year, month, day_int, hour, minute, int(second)), second - int(second)

    def utc_to_gps(self, year, month, day, hour, minute, second):
        """UTC 时间转 GPS (Week, Seconds)"""
        # 1. 先转 MJD
        mjd = self.ymd_to_mjd(year, month, day, hour, minute, second)
        
        # 2. 计算自 GPS epoch 经过的天数
        diff_days = mjd - self.MJD_GPS_EPOCH
        
        # 3. 计算周和秒
        week = int(diff_days // 7)
        # 此时的 seconds 是基于 UTC 刻度的
        raw_seconds = (diff_days - week * 7) * 86400
        
        # 4. 加上闰秒差异
        gps_seconds = raw_seconds + self.LEAP_SECONDS
        
        # 处理秒数溢出（比如加上18秒后跨周了）
        if gps_seconds >= 604800:
            gps_seconds -= 604800
            week += 1
            
        return week, gps_seconds

    def gps_to_utc(self, week, seconds):
        """GPS (Week, Seconds) 转 UTC 时间"""
        # 1. 减去闰秒回到 UTC 刻度
        utc_seconds_in_week = seconds - self.LEAP_SECONDS
        
        # 处理下溢（比如减去18秒后变成上一周了）
        if utc_seconds_in_week < 0:
            utc_seconds_in_week += 604800
            week -= 1
            
        # 2. 计算 MJD
        total_days = week * 7 + utc_seconds_in_week / 86400.0
        mjd = self.MJD_GPS_EPOCH + total_days
        
        # 3. MJD 转 YMD
        dt, frac_sec = self.mjd_to_ymd(mjd)
        return dt

    def ymd_to_doy(self, year, month, day):
        """年+月+日 转 年积日 (DOY)"""
        dt = datetime(year, month, day)
        new_year = datetime(year, 1, 1)
        return (dt - new_year).days + 1

# --- 测试用例 ---
if __name__ == "__main__":
    tool = TimeConverter()
    
    # 设定一个测试时间: 2024-05-20 12:00:00 UTC
    y, m, d, h, mn, s = 2024, 5, 20, 12, 0, 0
    
    print(f"输入 UTC: {y}-{m}-{d} {h}:{mn}:{s}")
    
    # 1. 验证 UTC -> MJD
    mjd = tool.ymd_to_mjd(y, m, d, h, mn, s)
    print(f"MJD: {mjd}")
    
    # 2. 验证 UTC -> GPS
    gps_week, gps_sec = tool.utc_to_gps(y, m, d, h, mn, s)
    print(f"GPS Week: {gps_week}, GPS Sec: {gps_sec}")
    
    # 3. 验证 YMD -> DOY
    doy = tool.ymd_to_doy(y, m, d)
    print(f"DOY: {doy}")
    
    # 4. 反向验证 GPS -> UTC
    restored_date = tool.gps_to_utc(gps_week, gps_sec)
    print(f"GPS还原回 UTC: {restored_date}")
```

以上是基本的需求，请使用superpowers的相关技能。请首先使用brainstrom技能评估该需求，澄清不清晰的需求，然后使用plan-writing技能写一个详细的执行计划，再交给负责审查的子Agent或相关技能评估计划，再使用TDD（测试驱动开发）的技能等相关的技能，执行开发过程。


