# GitHub 发布指南

本指南帮助你快速将代码推送到 GitHub 并发布 Release。

## 📋 前置要求

- Git 已安装
- GitHub 账号
- 代码已完成并测试通过 ✅

## 🚀 快速步骤

### 1. 创建 GitHub 仓库

访问 https://github.com/new 创建新仓库：

- **Repository name**: `gps-time-converter`（或其他你喜欢的名字）
- **Description**: GPS时间转换工具 - 支持UTC/GPS/MJD/BJT等多种时间格式转换
- **Visibility**: Public（推荐）或 Private
- **不要勾选** "Initialize this repository with a README"（本地已有）
- **不要勾选** "Add .gitignore"（本地已有）
- **不要勾选** "Choose a license"（本地已有）

点击 **Create repository**

### 2. 推送代码到 GitHub

在本地项目目录执行：

```bash
# 添加远程仓库地址（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/gps-time-converter.git

# 推送代码
git push -u origin main

# 或者如果是 master 分支
git push -u origin master
```

### 3. 验证推送成功

访问 `https://github.com/YOUR_USERNAME/gps-time-converter`

应该能看到所有文件已上传。

### 4. 创建 Release（发布可执行文件）

#### 方式一：Web 界面（推荐）

1. 在 GitHub 仓库页面，点击右侧的 **"Create a new release"** 或访问 `https://github.com/YOUR_USERNAME/gps-time-converter/releases`

2. 点击 **"Draft a new release"**

3. 填写发布信息：
   - **Choose a tag**: 输入 `v0.2.0`，点击 "Create new tag"
   - **Release title**: `v0.2.0 - GPS Time Converter Release`
   - **Description**: 
     ```markdown
     ## 🎉 GPS Time Converter v0.2.0

     ### ✨ 主要功能
     - 支持 UTC/GPS/MJD/BJT/DOY/TOD 等多种时间格式转换
     - 支持从任意格式输入转换为所有格式
     - 闰秒表灵活管理（CLI参数/环境变量/配置目录）
     - 命令行和 Python API 双接口

     ### 📦 分发方式
     1. **可执行文件**：下载下方的 `gps-time.exe`（Windows）
     2. **源代码安装**：`pip install git+https://github.com/YOUR_USERNAME/gps-time-converter.git`

     ### 📖 使用示例
     ```bash
     # 查看当前时间
     gps-time convert --now

     # 从 MJD 转换
     gps-time convert --mjd 60309.5

     # 从年积日转换
     gps-time convert --year-doy "2024,15.5"
     ```
     ```

4. **上传可执行文件**：
   - 在 "Attach binaries by dropping them here or selecting them" 区域
   - 上传 `dist/gps-time.exe`
   - 同时上传 `GPSUTC.BSW`（闰秒表数据）

5. 勾选 **"Set as the latest release"**

6. 点击 **"Publish release"**

#### 方式二：命令行（可选）

```bash
# 安装 GitHub CLI（如未安装）
# https://cli.github.com/

# 创建 release 并上传文件
gh release create v0.2.0 \
  --title "v0.2.0 - GPS Time Converter" \
  --notes-file release-notes.md \
  dist/gps-time.exe \
  GPSUTC.BSW
```

## 📁 本地文件清单

发布前请确保以下文件已准备：

- [ ] `dist/gps-time.exe` - Windows 可执行文件
- [ ] `GPSUTC.BSW` - 闰秒表数据文件
- [ ] `README.md` - 项目说明
- [ ] `LICENSE` - GPL-3.0 许可证

## 🔗 发布后分享链接

用户可通过以下方式获取：

1. **直接下载可执行文件**：
   ```
   https://github.com/YOUR_USERNAME/gps-time-converter/releases/latest/download/gps-time.exe
   ```

2. **源代码安装**：
   ```bash
   pip install git+https://github.com/YOUR_USERNAME/gps-time-converter.git
   ```

3. **克隆仓库**：
   ```bash
   git clone https://github.com/YOUR_USERNAME/gps-time-converter.git
   cd gps-time-converter
   pip install -e .
   ```

## 🐛 常见问题

### Q: 推送时提示权限错误？
**A**: 使用 HTTPS 需要密码，或使用 SSH 密钥：
```bash
# 方法1: 使用 HTTPS + Personal Access Token
# 访问 https://github.com/settings/tokens 生成 Token

# 方法2: 使用 SSH
git remote set-url origin git@github.com:YOUR_USERNAME/gps-time-converter.git
# 确保已配置 SSH 密钥: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### Q: 可执行文件太大？
**A**: 这是正常的，PyInstaller 会打包 Python 解释器和所有依赖。约 7-15MB 是合理范围。

### Q: 可执行文件被杀毒软件误报？
**A**: PyInstaller 打包的可执行文件有时会被误报。建议：
- 在 Release 说明中注明可能的误报情况
- 提供源代码安装作为备选方案
- 代码完全开源，用户可以自行审计

---

✅ 完成以上步骤后，其他人就可以通过 GitHub 使用你的工具了！
