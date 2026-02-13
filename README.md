# GPS Time Converter

> 🕒 多种时间格式互转工具 - UTC、GPS、MJD、BJT 等

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)]()

## 项目简介

**GPS Time Converter** 是一个用于多种时间格式互转的 Python 工具。支持 UTC、GPS 时间、MJD（简化儒略日）、BJT（北京时间）、DOY（年积日）等格式之间的转换，适用于天文观测、卫星导航、时间同步等场景。

## 功能特性

- 🔄 **多种时间格式互转**: UTC ↔ GPS ↔ MJD ↔ BJT
- 📅 **年积日计算**: Day of Year (DOY)
- ⏱️ **日内秒计算**: Time of Day (TOD)
- 📊 **GPS 时间解析**: GPS Week、DOW、TOW
- ⏰ **闰秒自动处理**: 自动获取闰秒信息
- 💻 **命令行工具**: 简洁易用的 CLI 界面
- 🐍 **Python API**: 灵活的编程接口

## 安装说明

### 从源代码安装

```bash
# 克隆仓库
git clone <repository-url>
cd gps_time

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -e .
```

### 开发模式安装

```bash
pip install -e ".[dev]"
```

### 依赖要求

- Python >= 3.8
- Click >= 8.0
- PyYAML >= 6.0

## 支持的格式说明

| 格式 | 说明 | 示例 |
|------|------|------|
| **UTC** | 协调世界时 | `2024-01-01 12:00:00` |
| **BJT** | 北京时间 (UTC+8) | `2024-01-01 20:00:00` |
| **MJD** | 简化儒略日 | `60309.5` |
| **DOY** | 年积日 (Day of Year) | `1` (1月1日) |
| **TOD** | 日内秒 (Time of Day) | `43200.0` (12:00:00) |
| **WEEK** | GPS 周数 | `2298` |
| **DOW** | 周内日 (Day of Week) | `1` (周一) |
| **TOW** | 周内秒 (Time of Week) | `518400.0` |

### GPS 时间系统

- **GPS 起始纪元**: 1980-01-06 00:00:00 UTC (MJD 44244)
- **GPS 周数**: 从起始纪元开始计算的周数
- **TOW (Time of Week)**: 周内秒数 (0 - 604799)
- **DOW (Day of Week)**: 周内日 (0=周日, 1=周一, ..., 6=周六)

## CLI 使用示例

### 显示当前时间

显示当前时间的所有格式：

```bash
gps-time convert --now
```

输出示例：
```
UTC:  2024-01-01 12:00:00
BJT:  2024-01-01 20:00:00
MJD:  60309.5
DOY:  1
TOD:  43200.0
WEEK: 2298
DOW:  1
TOW:  518400.0
```

### 转换指定时间

将指定 UTC 时间转换为所有格式：

```bash
gps-time convert --datetime "2024-01-01 12:00:00"
```

### 从其他时间格式转换

支持从多种时间格式作为输入：

```bash
# 从 MJD 转换
gps-time convert --mjd 60309.5

# 从年积日（DOY）转换 - 支持小数表示天内时间
gps-time convert --year-doy "2024,15.5"

# 从北京时间（BJT）转换
gps-time convert --bjt "2024-01-01 20:00:00"

# 从 GPS 周和周内天转换
gps-time convert --gps-week-dow "2298,1"

# 从 GPS 周和周内秒转换
gps-time convert --gps-week-tow "2298,518400"
```

> 💡 **提示**: 所有输入选项（--now, --datetime, --year-doy, --mjd, --bjt, --gps-week-dow, --gps-week-tow）互斥，同一时间只能使用一种输入格式。

### JSON 输出

```bash
gps-time convert --now --json
```

输出示例：
```json
{
  "utc": "2024-01-01 12:00:00",
  "bjt": "2024-01-01 20:00:00",
  "mjd": 60309.5,
  "doy": 1,
  "tod": 43200.0,
  "week": 2298,
  "dow": 1,
  "tow": 518400.0
}
```

### 查看帮助

```bash
gps-time --help
gps-time convert --help
```

## Python API 使用示例

### 基础转换

```python
from gps_time.converter import (
    ymd_to_mjd, 
    mjd_to_ymd, 
    day_of_year, 
    time_of_day,
    utc_to_bjt_datetime,
    utc_to_gps_datetime, 
    gps_to_utc_datetime
)

# UTC YMD 转 MJD
mjd = ymd_to_mjd(2024, 1, 1, 12, 0, 0)
print(f"MJD: {mjd}")  # 60309.5

# MJD 转 UTC YMD
year, month, day, hour, minute, second = mjd_to_ymd(60309.5)
print(f"UTC: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:05.2f}")

# 计算年积日 DOY
doy = day_of_year(2024, 3, 15)
print(f"DOY: {doy}")  # 75

# 计算日内秒 TOD
tod = time_of_day(12, 30, 45)
print(f"TOD: {tod}")  # 45045.0

# UTC 转北京时间 BJT
bjt = utc_to_bjt_datetime(2024, 1, 1, 12, 0, 0)
print(f"BJT: {bjt}")  # (2024, 1, 1, 20, 0, 0.0)
```

### GPS 时间转换

```python
from gps_time.converter import utc_to_gps_datetime, gps_to_utc_datetime

# UTC 转 GPS 时间
week, tow, dow = utc_to_gps_datetime(2024, 1, 1, 12, 0, 0, leap_seconds=18)
print(f"GPS Week: {week}, TOW: {tow}, DOW: {dow}")
# 输出: GPS Week: 2298, TOW: 518418.0, DOW: 1

# GPS 时间转 UTC
year, month, day, hour, minute, second = gps_to_utc_datetime(2298, 518418.0, leap_seconds=18)
print(f"UTC: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:05.2f}")
# 输出: UTC: 2024-01-01 12:00:00.00
```

### 闰秒表使用

```python
from gps_time.leap_second_table import LeapSecondTable

# 加载闰秒表（自动查找 GPSUTC.BSW 文件）
lst = LeapSecondTable()

# 查询指定日期的闰秒数
leap = lst.get_leap_second(2024, 1, 1)
print(f"Leap seconds: {leap}")  # 18

# 或使用 date 对象
from datetime import date
leap = lst.get_leap_second(date=date(2024, 1, 1))
print(f"Leap seconds: {leap}")

# 指定自定义闰秒表文件路径
lst = LeapSecondTable("/path/to/GPSUTC.BSW")
```

## 闰秒表管理

本项目使用 **GPSUTC.BSW** 文件作为闰秒数据源。支持多种方式指定闰秒表文件位置：

### 闰秒文件查找优先级

程序按以下优先级查找闰秒表文件：

1. **CLI 参数指定**（最高优先级）
   ```bash
   gps-time convert --now --leap-second-file /path/to/GPSUTC.BSW
   ```

2. **环境变量指定**
   ```bash
   # Windows
   set GPS_LEAP_SECOND_FILE=D:\path\to\GPSUTC.BSW
   gps-time convert --now
   
   # Linux/macOS
   export GPS_LEAP_SECOND_FILE=/path/to/GPSUTC.BSW
   gps-time convert --now
   ```

3. **系统配置目录**（推荐，自动管理）
   - **Windows**: `%APPDATA%\gps_time\GPSUTC.BSW`
   - **Linux/macOS**: `~/.config/gps_time/GPSUTC.BSW`
   
   首次运行时会自动复制内置闰秒表到该目录，之后直接更新此文件即可。

4. **包安装目录**（内置备份）
   作为最后 fallback，使用安装时自带的闰秒表文件。

### 更新闰秒表

1. 从 [AIUB FTP](ftp://ftp.aiub.unibe.ch/BSWUSER52/GEN/) 下载最新的 GPSUTC.BSW 文件
2. 选择以下任一方式更新：
   - **方式 A**: 覆盖系统配置目录中的文件（推荐）
     - Windows: `C:\Users\<用户名>\AppData\Roaming\gps_time\GPSUTC.BSW`
     - Linux/macOS: `~/.config/gps_time/GPSUTC.BSW`
   - **方式 B**: 使用 `--leap-second-file` 参数指定新文件路径
   - **方式 C**: 设置 `GPS_LEAP_SECOND_FILE` 环境变量指向新文件

### 闰秒表格式

文件格式说明：
```
DIFFERENCE GPS-UTC VALID SINCE (SEC)
------------------------------------
    18 2017  1  1  0  0  0.0000000
    19 2025  1  1  0  0  0.0000000  (预计)
```

> ⚠️ **注意**: GPS 时间计算依赖于准确的闰秒数据，建议定期检查并更新闰秒表文件。

### Python API 中的闰秒表管理

```python
from gps_time.leap_second_table import LeapSecondTable

# 自动查找（按优先级）
lst = LeapSecondTable()

# 指定文件路径
lst = LeapSecondTable("/path/to/GPSUTC.BSW")

# 查询闰秒
leap = lst.get_leap_second(2024, 1, 1)  # 返回: 18
```

## 项目结构

```
gps_time/
├── gps_time/              # 主包目录
│   ├── __init__.py
│   ├── cli.py             # 命令行接口
│   ├── converter.py       # 核心转换函数
│   └── leap_second_table.py  # 闰秒表处理
├── tests/                 # 测试目录
│   ├── test_cli.py
│   ├── test_converter.py
│   └── ...
├── GPSUTC.BSW             # 闰秒数据文件
├── pyproject.toml         # 项目配置
└── README.md              # 本文件
```

## 开发

### 运行测试

```bash
pytest
```

### 代码风格

本项目遵循 PEP 8 代码规范。

## 版本历史

### v0.2.0
- ✨ 新增多种输入格式支持：MJD、年积日、BJT、GPS Week+DOW/TOW
- 🔧 支持多种闰秒表管理方式：CLI参数、环境变量、系统配置目录
- ✅ 完整测试覆盖，66个测试用例全部通过

### v0.1.0
- 🎉 初始版本
- 支持 UTC/GPS/MJD/BJT/DOY/TOD 等格式互转
- 提供 CLI 和 Python API 接口
- 支持闰秒自动处理

## 许可证

GNU General Public License v3.0 (GPL-3.0)

本程序是自由软件：你可以在遵守自由软件基金会发布的 GNU 通用公共许可证第三版或（按你的选择）任何后续版本的条件下，重新发布和/或修改本程序。

本程序是希望它能有用而发布的，但没有任何担保；甚至没有适销性或适用于特定目的的隐含担保。详情请参阅 GNU 通用公共许可证。

## 致谢

- 闰秒数据源：[Bernese GNSS Software](https://www.bernese.unibe.ch/)
- 算法参考：天文算法（Hoffman 算法）

---

> 📧 如有问题或建议，欢迎提交 Issue 或 PR
