# GPS Time Converter Tool - 执行计划

> **任务目标**: 使用 TDD 开发一个支持多种时间格式互转的 GPS 时间转换工具

---

## TL;DR

**交付物**: Python 库 + CLI 工具，支持 UTC/GPS/MJD/DOY/TOW 等 9 种时间格式互转
**技术栈**: Python 3.8+, pytest, click
**闰秒管理**: 直接读取 BSW 格式文件（项目根目录 GPSUTC.BSW）
**测试策略**: TDD (Red-Green-Refactor) + pytest
**执行路径**: 项目初始化 → 核心算法 → 闰秒解析 → CLI → 集成测试

---

## 需求确认

### 核心功能
- ✅ 支持 UTC ↔ GPS 双向转换
- ✅ 支持 9 种时间类型：UTC, BJT, MJD, YEAR, DOY, TOD, GPS WEEK, DOW, TOW
- ✅ 支持输入时间或系统当前时间
- ✅ 输出所有格式（Human-readable + JSON）

### 技术决策（已确认）
- **语言**: Python 3.8+
- **架构**: Library + CLI，CLI 包装 Library
- **闰秒管理**: 直接从 `GPSUTC.BSW` 文件读取（BIPM 标准格式）
- **输出**: 默认人类可读，--json 参数输出 JSON

### 闰秒表格式（GPSUTC.BSW）
```
DIFFERENCE OF GPS-TIME MINUS UTC-TIME
-------------------------------------
GPS-UTC     VALID SINCE
 (SEC)      YYYY MM DD HH MM SS.SS

  -9.       1972 01 01 00 00 00.00
  -8.       1972 07 01 00 00 00.00
  ...
  18.       2017 01 01 00 00 00.00
```

---

## 项目结构

```
gps_time/
├── gps_time/                    # 核心包
│   ├── __init__.py              # 包导出
│   ├── converter.py             # 核心转换类（TDD主战场）
│   ├── leap_seconds.py          # 闰秒表解析
│   └── cli.py                   # 命令行接口
├── tests/
│   ├── test_converter.py        # 转换器单元测试
│   ├── test_leap_seconds.py     # 闰秒表测试
│   └── test_cli.py              # CLI集成测试
├── GPSUTC.BSW                   # 闰秒表（用户提供）
├── pyproject.toml               # 项目配置
├── setup.py                     # 安装脚本
└── README.md                    # 使用说明
```

---

## 任务清单 (TODOs)

### Phase 1: 项目初始化

- [x] 1.1 创建项目结构和配置文件
  - 创建目录：`gps_time/`, `tests/`
  - 创建 `pyproject.toml` (依赖: pytest, click)
  - 创建 `setup.py`
  - 创建 `.gitignore`
  - **TDD**: 运行 `python -m pytest` 确保环境正常
  - **Acceptance**: `pytest --version` 显示版本号

- [x] 1.2 设置测试基础设施
  - 安装开发依赖
  - 创建 `tests/__init__.py`
  - 创建 `tests/conftest.py` (fixtures)
  - **TDD**: 写一个空测试验证 pytest 运行
  - **Acceptance**: `pytest tests/` 运行 0 个测试，0 失败

### Phase 2: 核心转换算法（TDD）

- [x] 2.1 实现 MJD ↔ YMD 转换
  - **Test**: `test_mjd_to_ymd_basic()` - MJD 0 对应 1858-11-17
  - **Implement**: `ymd_to_mjd()` 使用 Hoffman 算法
  - **Test**: `test_ymd_to_mjd_basic()` - 2024-01-01 → 60310
  - **Implement**: `mjd_to_ymd()` 使用天文算法
  - **Test**: `test_roundtrip()` - YMD→MJD→YMD 精度验证
  - **Commit**: "feat: implement MJD ↔ YMD conversion"

- [x] 2.2 实现 DOY 计算
  - **Test**: `test_doy_basic()` - 2024-01-01 → DOY=1
  - **Test**: `test_doy_leap_year()` - 2024-03-01 → DOY=61
  - **Test**: `test_doy_common_year()` - 2023-03-01 → DOY=60
  - **Implement**: `ymd_to_doy()` 闰年感知计算
  - **Commit**: "feat: implement Day of Year calculation"

- [x] 2.3 实现 TOD 计算
  - **Test**: `test_tod_midnight()` - 00:00:00 → TOD=0
  - **Test**: `test_tod_noon()` - 12:00:00 → TOD=43200
  - **Implement**: `time_to_tod()` 时/分/秒转秒内
  - **Commit**: "feat: implement Time of Day calculation"

- [x] 2.4 实现 BJT 计算
  - **Test**: `test_utc_to_bjt()` - 2024-01-01 00:00:00 UTC → 2024-01-01 08:00:00 BJT
  - **Test**: `test_bjt_date_rollover()` - 2024-01-01 20:00:00 UTC → 2024-01-02 04:00:00 BJT
  - **Implement**: `utc_to_bjt()` UTC+8 转换
  - **Commit**: "feat: implement Beijing Time conversion"

- [x] 2.5 实现 GPS 时间转换（核心！）
  - **Test**: `test_utc_to_gps_epoch()` - 1980-01-06 00:00:00 → Week=0, TOW=0
  - **Test**: `test_utc_to_gps_with_leap()` - 2017-01-01 00:00:00 → Week=..., TOW=18
  - **Test**: `test_gps_to_utc_roundtrip()` - UTC→GPS→UTC 一致性
  - **Test**: `test_gps_week_boundary()` - 闰秒导致周边界处理
  - **Implement**: `utc_to_gps()` MJD 差值 + 闰秒
  - **Implement**: `gps_to_utc()` 减去闰秒
  - **Commit**: "feat: implement UTC ↔ GPS conversion with leap seconds"

### Phase 3: 闰秒表管理

- [x] 3.1 实现 BSW 文件解析
  - **Test**: `test_parse_bsw_file()` - 正确解析 GPSUTC.BSW
  - **Test**: `test_leap_second_lookup()` - 2017-01-01 查询返回 18
  - **Test**: `test_leap_second_before_first()` - 1971-12-31 返回 -10（或使用第一个值）
  - **Test**: `test_leap_second_after_last()` - 2025-01-01 使用最新值 18
  - **Implement**: `LeapSecondTable` 类，解析 BSW 格式
  - **Implement**: `get_leap_seconds(date)` 查询方法
  - **Commit**: "feat: implement BSW leap second table parser"

### Phase 4: CLI 开发

- [x] 4.1 实现基础 CLI 框架
  - **Test**: `test_cli_version()` - `gps-time --version` 显示版本
  - **Test**: `test_cli_help()` - `gps-time --help` 显示帮助
  - **Implement**: `cli.py` 使用 click，定义命令结构
  - **Commit**: "feat: implement CLI framework"

- [x] 4.2 实现 --now 功能
  - **Test**: `test_cli_now()` - `gps-time --now` 显示当前时间所有格式
  - **Test**: `test_cli_now_json()` - `gps-time --now --json` 输出 JSON
  - **Implement**: `--now` 标志，读取系统时间
  - **Implement**: 格式化输出（表格/JSON）
  - **Acceptance**: 
    ```bash
    gps-time --now
    # 显示：UTC, BJT, MJD, YEAR/DOY/TOD, WEEK/DOW/TOW
    ```
  - **Commit**: "feat: implement --now flag for current time"

- [x] 4.3 实现 --datetime 功能
  - **Test**: `test_cli_datetime()` - `gps-time --datetime "2024-01-01 12:00:00"` 
  - **Test**: `test_cli_datetime_invalid()` - 无效日期返回非零退出码
  - **Test**: `test_cli_datetime_json()` - JSON 输出验证
  - **Implement**: `--datetime` 参数解析
  - **Implement**: ISO 8601 格式支持 "YYYY-MM-DD HH:MM:SS"
  - **Acceptance**:
    ```bash
    gps-time --datetime "2024-01-01 12:00:00"
    # 输出包含所有 9 种格式
    ```
  - **Commit**: "feat: implement --datetime flag for specific time"

- [x] 4.4 实现错误处理和边界检查
  - **Test**: `test_cli_pre_gps_epoch()` - 1970-01-01 显示警告或错误
  - **Test**: `test_cli_future_date()` - 2030-01-01 使用最新闰秒
  - **Test**: `test_cli_missing_bsw()` - 无 GPSUTC.BSW 时友好错误
  - **Implement**: 边界情况处理
  - **Commit**: "feat: add error handling for edge cases"

### Phase 5: 集成与文档

- [x] 5.1 编写 README
  - 安装说明 (`pip install -e .`)
  - 使用示例（CLI + Library）
  - 闰秒表更新说明
  - **Acceptance**: README 包含完整使用说明
  - **Commit**: "docs: add README with usage examples"

- [x] 5.2 最终集成测试
  - **Test**: 端到端测试，完整工作流
  - **Test**: 所有格式互转验证
  - **Acceptance**: `pytest tests/` 全部通过
  - **Commit**: "test: add comprehensive integration tests"

- [x] 5.3 代码清理和优化
  - 类型注解检查
  - 代码格式化 (black)
  - 文档字符串完善
  - **Commit**: "chore: code cleanup and documentation"

---

## TDD 执行指南

### 每个任务的 TDD 流程

```
1. RED: 写测试（预期失败）
   → python -m pytest tests/test_module.py::test_name -v
   → Expected: FAILED

2. GREEN: 最小实现
   → 编写刚好让测试通过的代码
   → python -m pytest tests/test_module.py::test_name -v
   → Expected: PASSED

3. REFACTOR: 优化（可选）
   → 保持测试通过的前提下改进代码
   → python -m pytest tests/test_module.py::test_name -v
   → Expected: PASSED

4. COMMIT
   → git add tests/ gps_time/
   → git commit -m "type(scope): description"
```

### 测试设计原则

- **单一职责**: 每个测试只验证一个行为
- **描述性命名**: `test_<function>_<scenario>_<expected>`
- **独立性**: 测试之间不依赖顺序
- **确定性**: 相同输入总是产生相同结果
- **边界覆盖**: 正常值、边界值、异常值

---

## 关键算法参考

### Hoffman 算法 (YMD → MJD)

```python
def ymd_to_mjd(year, month, day, hour=0, min=0, sec=0):
    day_frac = day + hour/24.0 + min/1440.0 + sec/86400.0
    
    if month <= 2:
        y = year - 1
        m = month + 12
    else:
        y = year
        m = month
        
    mjd = int(365.25 * y) + int(30.6001 * (m + 1)) + day_frac - 679019
    return mjd
```

### GPS 时间计算

```python
MJD_GPS_EPOCH = 44244  # 1980-01-06

def utc_to_gps(year, month, day, hour, minute, second, leap_seconds):
    mjd = ymd_to_mjd(year, month, day, hour, minute, second)
    diff_days = mjd - MJD_GPS_EPOCH
    week = int(diff_days // 7)
    raw_seconds = (diff_days - week * 7) * 86400
    gps_seconds = raw_seconds + leap_seconds
    
    if gps_seconds >= 604800:  # 跨周处理
        gps_seconds -= 604800
        week += 1
        
    return week, gps_seconds
```

---

## 验证策略

### 单元测试验证

```bash
# 运行所有测试
python -m pytest tests/ -v

# 预期输出：
# ===================== test session starts ======================
# tests/test_converter.py::test_mjd_to_ymd_basic PASSED
# tests/test_converter.py::test_utc_to_gps_epoch PASSED
# ...
# ================== X passed in Y seconds =====================
```

### CLI 验证

```bash
# 测试当前时间
gps-time --now

# 测试指定时间
gps-time --datetime "2024-01-01 12:00:00"

# 测试 JSON 输出
gps-time --now --json | python -m json.tool

# 测试无效输入
gps-time --datetime "invalid"  # 应该返回非零退出码
```

### 边界情况验证

```bash
# GPS 纪元
gps-time --datetime "1980-01-06 00:00:00"
# 预期：Week=0, TOW=0

# 闰秒边界
gps-time --datetime "2017-01-01 00:00:00"
# 预期：TOW 包含 +18 秒偏移

# 跨日 BJT
gps-time --datetime "2024-01-01 20:00:00"
# 预期：BJT 显示 2024-01-02 04:00:00
```

---

## Agent 执行建议

### 推荐 Agent 配置

```python
# 每个任务使用以下配置
task(
    category="quick",  # 轻量级任务
    load_skills=[
        "test-driven-development",  # 强制 TDD 流程
        "root-cause-tracing",       # 调试问题
    ]
)
```

### 并行执行策略

- **可并行**: Phase 2 的各个子任务（2.1-2.5 互相独立）
- **必须串行**: 
  - Phase 1 必须在 Phase 2 之前
  - Phase 3 必须在 Phase 2 之后（需要转换函数）
  - Phase 4 必须在 Phase 2 和 3 之后
  - Phase 5 最后执行

### 失败回滚策略

- 每个 Commit 都是可工作的状态
- 如果测试失败，查看上一次成功的 Commit
- 使用 `git bisect` 定位问题引入点

---

## 成功标准

### 功能完成
- [x] 所有 9 种时间类型正确转换
- [x] CLI --now 和 --datetime 正常工作
- [x] JSON 输出格式正确
- [x] BSW 闰秒表正确解析

### 测试通过
- [x] pytest 全部通过（覆盖率 >80%）
- [x] 边界情况处理正确
- [x] 错误信息清晰有用

### 代码质量
- [x] 所有函数有文档字符串
- [x] 类型注解完整
- [x] 代码通过 black 格式化
- [x] 无警告（pylance/pyright）

### 文档完整
- [x] README 包含安装和使用说明
- [x] 使用示例代码可运行
- [x] 闰秒表更新方法说明

---

**计划生成完成！**

保存路径: `.sisyphus/plans/gps-time-converter.md`

**下一步**: 运行 `/start-work` 开始执行计划

**建议**: 使用 `task(category="quick", load_skills=["test-driven-development"])` 开始第一个任务
