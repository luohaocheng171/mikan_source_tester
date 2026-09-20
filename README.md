[README.md](https://github.com/user-attachments/files/32429522/README.md)
# Mikan 直播源检测工具

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://www.qt.io/qt-for-python)

> M3U 直播源检测与筛选工具 — 支持暴力截停、搜索过滤、IP国家查询

Mikan 直播源检测工具是一款基于 Python 和 PySide6 开发的 M3U 直播源检测桌面应用程序，提供图形化界面来导入 m3u 文件、并发检测直播源可用性、查询 IP 归属国家，并将可用源导出为标准 m3u 格式。旨在为直播源管理提供一个免费、开源、功能全面的检测工具。

---

## 功能特性

### M3U 导入与解析
- 导入 .m3u / .m3u8 文件
- 自动解析 EXTINF 格式的频道名称和播放地址
- 支持标准 M3U playlist 格式

### 直播源检测
- 可调式检测参数（超时时间、重试次数、重试间隔均可配置）
- 多线程并发检测（支持 1~30 个并发线程，可配置）
- 支持随机顺序检测（打乱检测顺序避免目标服务器限流）
- 暴力截停：一键立即终止所有检测任务（关闭 HTTP Session、取消所有 Future）
- 检测指标：HTTP 状态码、响应延迟(ms)、尝试次数、IP 地址、归属国家

### IP 国家查询（三种模式）
- 自动模式：优先使用离线数据库查询，失败后自动切换在线查询
- 离线模式：使用 GeoLite2-City.mmdb 本地数据库查询，无需联网
- 在线模式：通过 ip-api.com / ipinfo.io 在线接口查询
- 支持用户自行导入 GeoLite2 数据库文件
- IP 查询结果缓存机制（线程安全，避免重复查询）

### 结果管理与导出
- 实时进度条显示检测进度
- 结果表格展示（状态、频道名、状态码、尝试次数、延迟、IP、国家、URL）
- 搜索过滤：按频道名称实时筛选结果
- 复选框选中：手动勾选需要打包的频道
- 全选 / 取消全选快捷操作
- 打包所有可用源（一键导出全部可用频道）
- 打包选中频道（按需导出指定频道）
- 自动导出：检测完成后可自动导出可用源
- 导出为标准 M3U 格式，兼容 VLC、PotPlayer 等播放器

### 设置与配置
- 检测参数设置（超时、重试、间隔、并发线程数）
- 主题切换（浅色主题 / 深色主题）
- IP 查询模式切换（自动 / 离线 / 在线）
- GeoLite2 数据库导入与管理
- 自动导出开关与导出路径设置
- JSON 文件持久化配置，重启后自动加载

### UI 特性
- 扁平化粉色系浅色主题
- 暗蓝色调深色主题
- 状态颜色标识（可用-绿色、不可用-红色、超时-橙色、已停止-橙色）
- 表格交替行颜色
- 列排序功能

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| GUI 框架 | PySide6 (Qt for Python) |
| HTTP 请求 | requests |
| IP 查询 | geoip2（离线）+ 在线 API |
| 并发模型 | concurrent.futures + ThreadPoolExecutor + QThread |
| 配置存储 | JSON 文件 |
| UI 样式 | 自定义 QSS（浅色/深色两套主题） |

---

## 安装与运行

### 环境要求

- Windows / macOS / Linux
- Python 3.8 或更高版本

### 安装依赖

```
pip install PySide6 requests geoip2
```

### 下载 GeoLite2 数据库（可选）

如需使用离线 IP 国家查询功能，请从 [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) 下载 GeoLite2-City.mmdb 文件，放置于程序同目录下，或在程序设置中手动导入。

### 运行程序

```
python mikan_source_tester_v3.py
```

首次运行时，程序会自动检测缺失依赖并提示安装。

---

## 项目结构

```
mikan_source_tester_v3.py    # 主程序入口（单文件应用）
├── tester_config.json        # 用户配置（自动生成）
└── GeoLite2-City.mmdb        # IP 地理数据库（可选）
```

> 注：本项目采用单文件架构，所有模块、面板、对话框和工具类均集成在 `mikan_source_tester_v3.py` 中，便于分发和部署。

---

## 模块说明

| 模块 | 说明 |
|------|------|
| `ConfigManager` | 配置管理（JSON 持久化加载与保存） |
| `ThemeManager` | 主题管理（浅色/深色 QSS 样式切换） |
| `IPCountryLookup` | IP 国家查询（三种模式、缓存、线程安全） |
| `M3UParser` | M3U 解析器（文件解析与导出） |
| `SourceTester` | 检测器（QThread + 线程池、暴力截停机制） |
| `SettingsDialog` | 设置对话框（参数配置与主题切换） |
| `MainWindow` | 主窗口（UI 逻辑与事件绑定） |

---

## 注意事项

1. **网络连接**：直播源检测需要稳定的网络连接；在线 IP 查询模式也需要联网。
2. **依赖安装**：首次运行程序会自动检测缺失依赖并提示安装，也可手动执行 `pip install PySide6 requests geoip2` 预先安装。
3. **性能调优**：可根据网络状况调整并发线程数和超时时间。并发数过高可能导致目标服务器限流或本地网络拥塞。
4. **GeoLite2 数据库**：离线 IP 查询功能需要 GeoLite2-City.mmdb 文件。可从 MaxMind 官网免费下载，放置于程序同目录下即可自动加载。
5. **杀毒软件**：程序涉及网络请求和进程操作，可能被杀毒软件误报，请将程序加入白名单。
6. **数据导出**：导出的 m3u 文件为标准格式，可直接导入 VLC、PotPlayer、IPTV 播放器使用。

---

## 开发

### 代码风格

- 遵循 PEP 8 编码规范
- 使用类型注解（typing）
- 异步操作通过 QThread + ThreadPoolExecutor 实现
- UI 样式统一使用 QSS 管理

### 添加新功能

1. 在对应面板类或主窗口中实现 UI 逻辑
2. 在专用工具类中封装功能逻辑
3. 通过 SourceTester 的线程池机制执行耗时操作
4. 在 SettingsDialog 中添加新的配置项

---

## 许可证

本项目采用 **GNU General Public License v3.0** 许可。你可以自由地复制、修改和再分发本软件，但必须保留版权声明和许可声明。衍生作品也必须以相同的许可证开源。

详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python 绑定
- [requests](https://docs.python-requests.org/) - HTTP 请求库
- [geoip2](https://geoip2.readthedocs.io/) - MaxMind GeoLite2 Python 客户端
- [MaxMind GeoLite2](https://www.maxmind.com/en/geoip2-databases) - 地理定位数据库
- [DeepSeek](https://www.deepseek.com/) - AI 辅助开发

---

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

*Made with care by Mikan Team · AI assisted by DeepSeek*
