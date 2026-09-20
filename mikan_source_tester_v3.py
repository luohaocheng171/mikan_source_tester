#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌸 Mikan 直播源检测工具 v6.4
功能：导入 m3u · 可调式检测 · 导出可用源 · IP 国家查询
新增：暴力截停 · 搜索过滤 · 复选框选中打包
"""

import os
import sys
import re
import time
import json
import random
import socket
import threading
import subprocess
import shutil
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from datetime import datetime

# ============================================================
# 自动安装依赖
# ============================================================

def install_dependencies():
    missing = []
    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import geoip2
    except ImportError:
        missing.append("geoip2")

    if missing:
        print(f"📦 正在安装依赖: {', '.join(missing)}")
        for pkg in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("✅ 依赖安装完成，请重新运行")
        sys.exit(0)

install_dependencies()

# ============================================================
# 导入
# ============================================================

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import requests
import geoip2.database

# ============================================================
# 配置
# ============================================================

APP_NAME = "🌸 Mikan 直播源检测工具 v6.4"
APP_VERSION = "6.4"

CONFIG_FILE = Path(__file__).parent / "tester_config.json"

DEFAULT_CONFIG = {
    "timeout": 10,
    "retries": 3,
    "retry_interval": 0.5,
    "max_workers": 10,
    "random_order": False,
    "auto_export": False,
    "export_path": str(Path.home() / "good_sources.m3u"),
    "ip_mode": "auto",
    "theme": "light",
}

class ConfigManager:
    @staticmethod
    def load() -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_CONFIG.copy()

    @staticmethod
    def save(data: dict):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# 主题管理
# ============================================================

class ThemeManager:
    LIGHT_STYLE = """
        QMainWindow, QDialog { background: #FDF6F0; }
        QWidget { background: #FDF6F0; color: #444; font-family: "Microsoft YaHei"; }
        QPushButton {
            background: #FFD1D6;
            color: #444;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background: #FFB3BA; }
        QPushButton:pressed { background: #FF8A9C; }
        QPushButton:disabled { background: #E8E0D8; color: #A0A0A0; }
        QPushButton:checked { background: #A8E6CF; }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
            background: white;
            border: 2px solid #FFD1D6;
            border-radius: 10px;
            padding: 6px 12px;
            color: #444;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border-color: #FFB3BA;
        }
        QComboBox QAbstractItemView {
            background: white;
            border: 2px solid #FFD1D6;
            border-radius: 10px;
            selection-background-color: #FFB3BA;
        }
        QTableWidget {
            background: #FDF6F0;
            border: 2px solid #FFD1D6;
            border-radius: 10px;
            gridline-color: #FFE6E8;
            color: #444;
        }
        QTableWidget::item { padding: 6px 8px; }
        QTableWidget::item:selected { background: #FFB3BA; color: white; }
        QHeaderView::section {
            background: #FFF0F0;
            padding: 6px 8px;
            border: none;
            font-weight: bold;
            color: #444;
        }
        QCheckBox { color: #444; spacing: 6px; }
        QCheckBox::indicator {
            width: 18px; height: 18px; border-radius: 6px;
            border: 2px solid #FFB3BA; background: white;
        }
        QCheckBox::indicator:checked { background: #FFB3BA; border-color: #FF8A9C; }
        QScrollBar:vertical {
            background: #FDF6F0; width: 10px; border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #FFD1D6; border-radius: 5px; min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #FFB3BA; }
        QProgressBar {
            height: 20px; border-radius: 10px;
            background: #F5EDE8;
        }
        QProgressBar::chunk {
            background: #A8E6CF; border-radius: 10px;
        }
        QLabel { color: #444; }
        QStatusBar { color: #888; font-size: 10px; }
        QStatusBar::item { border: none; }
    """

    DARK_STYLE = """
        QMainWindow, QDialog { background: #1a1a2e; }
        QWidget { background: #1a1a2e; color: #e0e0e0; font-family: "Microsoft YaHei"; }
        QPushButton {
            background: #2a2a4a;
            color: #e0e0e0;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background: #3a3a5e; }
        QPushButton:pressed { background: #4a4a6e; }
        QPushButton:disabled { background: #2a2a3a; color: #666; }
        QPushButton:checked { background: #4a6a5a; }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
            background: #0d0d1a;
            border: 2px solid #3a3a5e;
            border-radius: 10px;
            padding: 6px 12px;
            color: #e0e0e0;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border-color: #6a4a8a;
        }
        QTableWidget {
            background: #1a1a2e;
            border: 2px solid #3a3a5e;
            border-radius: 10px;
            gridline-color: #2a2a4a;
            color: #e0e0e0;
        }
        QTableWidget::item:selected { background: #4a3a6a; color: white; }
        QHeaderView::section {
            background: #2a2a4a;
            padding: 6px 8px;
            border: none;
            font-weight: bold;
            color: #a0a0c0;
        }
        QCheckBox { color: #e0e0e0; spacing: 6px; }
        QCheckBox::indicator {
            width: 18px; height: 18px; border-radius: 6px;
            border: 2px solid #4a4a6e; background: #0d0d1a;
        }
        QCheckBox::indicator:checked { background: #4a6a8a; border-color: #6a4a8a; }
        QScrollBar:vertical {
            background: #1a1a2e; width: 10px; border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #3a3a5e; border-radius: 5px; min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #4a4a6e; }
        QProgressBar {
            height: 20px; border-radius: 10px;
            background: #2a2a4a;
        }
        QProgressBar::chunk {
            background: #4a8a6a; border-radius: 10px;
        }
        QLabel { color: #e0e0e0; }
        QStatusBar { color: #888; font-size: 10px; }
        QStatusBar::item { border: none; }
    """

    @classmethod
    def apply_theme(cls, app, theme: str):
        app.setStyleSheet(cls.DARK_STYLE if theme == "dark" else cls.LIGHT_STYLE)

# ============================================================
# IP 国家查询（三种模式独立）
# ============================================================

class IPCountryLookup:
    _cache = {}
    _lock = threading.Lock()
    _reader = None
    _db_path = None
    _mode = "auto"
    _db_ready = False

    COUNTRY_MAP = {
        "US": "美国", "CN": "中国", "JP": "日本", "KR": "韩国",
        "DE": "德国", "FR": "法国", "GB": "英国", "IT": "意大利",
        "ES": "西班牙", "RU": "俄罗斯", "IN": "印度", "BR": "巴西",
        "CA": "加拿大", "AU": "澳大利亚", "NL": "荷兰", "SE": "瑞典",
        "CH": "瑞士", "BE": "比利时", "AT": "奥地利", "DK": "丹麦",
        "NO": "挪威", "FI": "芬兰", "PL": "波兰", "UA": "乌克兰",
        "SG": "新加坡", "HK": "香港", "TW": "台湾", "MO": "澳门",
        "MY": "马来西亚", "TH": "泰国", "VN": "越南", "PH": "菲律宾",
        "ID": "印尼", "NZ": "新西兰", "ZA": "南非", "EG": "埃及",
        "SA": "沙特", "AE": "阿联酋", "IL": "以色列", "TR": "土耳其",
        "GR": "希腊", "PT": "葡萄牙", "IE": "爱尔兰", "CZ": "捷克",
        "HU": "匈牙利", "RO": "罗马尼亚", "BG": "保加利亚", "HR": "克罗地亚",
        "RS": "塞尔维亚", "SK": "斯洛伐克", "SI": "斯洛文尼亚",
        "MX": "墨西哥", "AR": "阿根廷", "CL": "智利", "CO": "哥伦比亚",
        "PE": "秘鲁", "VE": "委内瑞拉", "NG": "尼日利亚",
        "PK": "巴基斯坦", "BD": "孟加拉",
    }

    @classmethod
    def init(cls, mode: str = "auto", db_path: str = None):
        cls._mode = mode
        cls._db_path = Path(db_path) if db_path else Path(__file__).parent / "GeoLite2-City.mmdb"
        cls._load_db()

    @classmethod
    def _load_db(cls):
        if not cls._db_path or not cls._db_path.exists():
            cls._db_ready = False
            return
        try:
            cls._reader = geoip2.database.Reader(str(cls._db_path))
            cls._db_ready = True
        except:
            cls._db_ready = False

    @classmethod
    def get_country(cls, ip: str) -> str:
        if not ip:
            return "未知"
        
        with cls._lock:
            if ip in cls._cache:
                return cls._cache[ip]

        country = "未知"

        # ===== 离线模式 / auto 模式优先离线 =====
        if cls._mode in ["offline", "auto"] and cls._db_ready and cls._reader:
            try:
                resp = cls._reader.country(ip)
                if resp.country.name:
                    with cls._lock:
                        cls._cache[ip] = resp.country.name
                    return resp.country.name
                if resp.country.iso_code:
                    country = cls.COUNTRY_MAP.get(resp.country.iso_code, resp.country.iso_code)
                    with cls._lock:
                        cls._cache[ip] = country
                    return country
            except:
                # 离线失败，如果是离线模式则直接返回未知
                if cls._mode == "offline":
                    with cls._lock:
                        cls._cache[ip] = "未知"
                    return "未知"

        # ===== 在线模式 / auto 模式离线失败后走在线 =====
        if cls._mode in ["online", "auto"]:
            for api in [
                ("http://ip-api.com/json/{ip}?fields=countryCode,country", lambda d: d.get("country")),
                ("https://ipinfo.io/{ip}/json", lambda d: d.get("country")),
            ]:
                try:
                    resp = requests.get(api[0].format(ip=ip), timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        result = api[1](data)
                        if result:
                            if len(result) == 2:
                                result = cls.COUNTRY_MAP.get(result, result)
                            with cls._lock:
                                cls._cache[ip] = result
                            return result
                except:
                    continue

        with cls._lock:
            cls._cache[ip] = "未知"
        return "未知"

    @classmethod
    def extract_ip(cls, url: str) -> str:
        try:
            host = urlparse(url).hostname
            if not host:
                return ""
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
                return host
            return socket.gethostbyname(host)
        except:
            return ""

    @classmethod
    def clear_cache(cls):
        with cls._lock:
            cls._cache.clear()

    @classmethod
    def is_db_ready(cls) -> bool:
        return cls._db_ready

    @classmethod
    def get_db_path(cls) -> str:
        return str(cls._db_path) if cls._db_path else ""

    @classmethod
    def set_mode(cls, mode: str):
        if mode in ["auto", "offline", "online"]:
            cls._mode = mode

# ============================================================
# M3U 解析器
# ============================================================

class M3UParser:
    @staticmethod
    def parse(content: str) -> List[Dict]:
        channels = []
        lines = content.splitlines()
        current = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#EXTINF:"):
                match = re.search(r',(.+)$', line)
                if match:
                    current = {"name": match.group(1).strip(), "raw": line}
            elif line.startswith("http://") or line.startswith("https://"):
                if current:
                    current["url"] = line
                    channels.append(current.copy())
                    current = {}

        return channels

    @staticmethod
    def export(channels: List[Dict], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for ch in channels:
                f.write(f"{ch.get('raw', '#EXTINF:-1,')}\n")
                f.write(f"{ch.get('url', '')}\n")

# ============================================================
# 检测器（暴力截停版）
# ============================================================

class SourceTester(QThread):
    progress = Signal(int, int, str)
    result = Signal(dict)
    finished = Signal()

    def __init__(self, channels: List[Dict], config: dict):
        super().__init__()
        self.channels = channels
        self.config = config
        self.running = True
        self.results = []
        self._lock = threading.Lock()
        self._executor = None
        self._futures = []
        self._session = requests.Session()

    def stop(self):
        """暴力截停 - 立即终止所有检测"""
        self.running = False
        
        # 关闭 session 强制中断所有请求
        try:
            self._session.close()
        except:
            pass
        
        # 取消所有未完成的 Future
        if self._executor:
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except:
                pass
        
        # 取消所有 Future
        for f in self._futures:
            try:
                f.cancel()
            except:
                pass

    def test_single(self, channel: Dict) -> Dict:
        url = channel.get("url")
        name = channel.get("name", "未知")
        timeout = self.config.get("timeout", 10)
        retries = self.config.get("retries", 3)
        retry_interval = self.config.get("retry_interval", 0.5)

        ip = IPCountryLookup.extract_ip(url)
        country = IPCountryLookup.get_country(ip) if ip else "未知"

        for attempt in range(1, retries + 1):
            if not self.running:
                return {**channel, "status": "⏹ 已停止", "code": None, "attempts": attempt, "latency": -1, "ip": ip, "country": country}

            try:
                start = time.time()
                resp = self._session.get(
                    url,
                    stream=True,
                    timeout=timeout,
                    allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                latency = int((time.time() - start) * 1000)

                if resp.status_code < 400:
                    try:
                        if next(resp.iter_content(1024), b""):
                            return {**channel, "status": "✅ 可用", "code": resp.status_code, "attempts": attempt, "latency": latency, "ip": ip, "country": country}
                    except:
                        return {**channel, "status": "✅ 可用（无数据）", "code": resp.status_code, "attempts": attempt, "latency": latency, "ip": ip, "country": country}

                if attempt < retries and self.running:
                    time.sleep(retry_interval)
                else:
                    return {**channel, "status": f"❌ 不可用 ({resp.status_code})", "code": resp.status_code, "attempts": attempt, "latency": latency, "ip": ip, "country": country}

            except (requests.Timeout, requests.ConnectionError):
                if attempt < retries and self.running:
                    time.sleep(retry_interval)
                else:
                    return {**channel, "status": "⏰ 超时", "code": None, "attempts": attempt, "latency": -1, "ip": ip, "country": country}

            except Exception as e:
                if attempt < retries and self.running:
                    time.sleep(retry_interval)
                else:
                    return {**channel, "status": f"❌ 错误: {str(e)[:30]}", "code": None, "attempts": attempt, "latency": -1, "ip": ip, "country": country}

        return {**channel, "status": "❌ 不可用", "code": None, "attempts": retries, "latency": -1, "ip": ip, "country": country}

    def run(self):
        total = len(self.channels)
        self.results = []
        max_workers = self.config.get("max_workers", 10)
        channels = self.channels.copy()
        if self.config.get("random_order"):
            random.shuffle(channels)

        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures = []
        self._session = requests.Session()

        # 提交所有任务
        for ch in channels:
            if not self.running:
                break
            future = self._executor.submit(self.test_single, ch)
            self._futures.append(future)

        # 使用 as_completed 逐个获取结果（可中断）
        completed = 0
        for future in concurrent.futures.as_completed(self._futures):
            if not self.running:
                # 取消剩余任务
                for f in self._futures:
                    f.cancel()
                break
            
            try:
                result = future.result()
                with self._lock:
                    self.results.append(result)
                    completed += 1
                    self.progress.emit(completed, total, result.get("name", "未知"))
                    self.result.emit(result)
            except concurrent.futures.CancelledError:
                continue
            except Exception:
                continue

        # 清理
        try:
            self._session.close()
        except:
            pass
        
        try:
            self._executor.shutdown(wait=False, cancel_futures=True)
        except:
            pass
        
        self.finished.emit()

# ============================================================
# 设置对话框
# ============================================================

class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.parent_window = parent
        self.setWindowTitle("⚙️ 设置")
        self.setMinimumSize(400, 500)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("⚙️ 检测设置")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FF8A9C;")
        layout.addWidget(title)

        # 主题
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("🎨 主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["☀️ 浅色", "🌙 深色"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        # 超时
        row = QHBoxLayout()
        row.addWidget(QLabel("⏱️ 超时:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setSuffix(" 秒")
        row.addWidget(self.timeout_spin)
        row.addStretch()
        layout.addLayout(row)

        # 重试
        row = QHBoxLayout()
        row.addWidget(QLabel("🔄 重试:"))
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 10)
        self.retries_spin.setSuffix(" 次")
        row.addWidget(self.retries_spin)
        row.addStretch()
        layout.addLayout(row)

        # 间隔
        row = QHBoxLayout()
        row.addWidget(QLabel("⏳ 间隔:"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 5)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setSuffix(" 秒")
        row.addWidget(self.interval_spin)
        row.addStretch()
        layout.addLayout(row)

        # 并发
        row = QHBoxLayout()
        row.addWidget(QLabel("🚀 并发:"))
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 30)
        self.workers_spin.setSuffix(" 个")
        row.addWidget(self.workers_spin)
        row.addStretch()
        layout.addLayout(row)

        # 随机顺序
        self.random_check = QCheckBox("🎲 随机顺序")
        layout.addWidget(self.random_check)

        # IP 模式
        row = QHBoxLayout()
        row.addWidget(QLabel("🌍 IP 模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["自动", "离线", "在线"])
        row.addWidget(self.mode_combo)
        row.addStretch()
        layout.addLayout(row)

        # 数据库状态
        self.db_status = QLabel("📦 数据库: 检测中...")
        self.db_status.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.db_status)

        # 导入数据库
        import_btn = QPushButton("📂 导入数据库")
        import_btn.clicked.connect(self.import_db)
        layout.addWidget(import_btn)

        # 自动导出
        self.auto_export_check = QCheckBox("📤 自动导出可用源")
        layout.addWidget(self.auto_export_check)

        # 导出路径
        row = QHBoxLayout()
        row.addWidget(QLabel("📁 导出路径:"))
        self.export_path = QLineEdit()
        self.export_path.setReadOnly(True)
        row.addWidget(self.export_path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_export)
        row.addWidget(browse_btn)
        layout.addLayout(row)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("💾 保存")
        save_btn.setStyleSheet("background: #A8E6CF; color: white; font-weight: bold; padding: 8px 24px; border-radius: 10px;")
        save_btn.clicked.connect(self.save)
        btn_row.addWidget(save_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def load_config(self):
        self.timeout_spin.setValue(self.config.get("timeout", 10))
        self.retries_spin.setValue(self.config.get("retries", 3))
        self.interval_spin.setValue(self.config.get("retry_interval", 0.5))
        self.workers_spin.setValue(self.config.get("max_workers", 10))
        self.random_check.setChecked(self.config.get("random_order", False))
        self.auto_export_check.setChecked(self.config.get("auto_export", False))
        self.export_path.setText(self.config.get("export_path", str(Path.home() / "good_sources.m3u")))

        mode_map = {"auto": 0, "offline": 1, "online": 2}
        self.mode_combo.setCurrentIndex(mode_map.get(self.config.get("ip_mode", "auto"), 0))
        self.theme_combo.setCurrentIndex(0 if self.config.get("theme", "light") == "light" else 1)
        self.update_db_status()

    def update_db_status(self):
        if IPCountryLookup.is_db_ready():
            self.db_status.setText(f"✅ 数据库已就绪")
            self.db_status.setStyleSheet("color: #2e7d32; font-size: 10px;")
        else:
            self.db_status.setText("💡 未找到数据库，请导入")
            self.db_status.setStyleSheet("color: #888; font-size: 10px;")

    def browse_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择导出路径", self.export_path.text(), "M3U 文件 (*.m3u)")
        if path:
            self.export_path.setText(path)

    def import_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 GeoLite2-City.mmdb", str(Path.home()), "MMDB 文件 (*.mmdb)")
        if path:
            target = Path(__file__).parent / "GeoLite2-City.mmdb"
            shutil.copy2(path, target)
            IPCountryLookup._db_path = target
            IPCountryLookup._load_db()
            self.update_db_status()
            QMessageBox.information(self, "成功", f"数据库已导入:\n{target}")

    def save(self):
        self.config["timeout"] = self.timeout_spin.value()
        self.config["retries"] = self.retries_spin.value()
        self.config["retry_interval"] = self.interval_spin.value()
        self.config["max_workers"] = self.workers_spin.value()
        self.config["random_order"] = self.random_check.isChecked()
        self.config["auto_export"] = self.auto_export_check.isChecked()
        self.config["export_path"] = self.export_path.text()
        mode_map = {0: "auto", 1: "offline", 2: "online"}
        self.config["ip_mode"] = mode_map.get(self.mode_combo.currentIndex(), "auto")
        self.config["theme"] = "dark" if self.theme_combo.currentIndex() == 1 else "light"

        IPCountryLookup.set_mode(self.config["ip_mode"])
        ConfigManager.save(self.config)

        if self.parent_window:
            ThemeManager.apply_theme(QApplication.instance(), self.config["theme"])

        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()

# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load()
        IPCountryLookup.init(self.config.get("ip_mode", "auto"))

        self.channels = []
        self.results = []
        self.tester = None
        self.testing = False
        self.search_keyword = ""

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1100, 750)
        self.resize(1150, 800)

        self.setup_ui()
        ThemeManager.apply_theme(QApplication.instance(), self.config.get("theme", "light"))
        self.update_status()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)

        # 标题
        title = QLabel("🌸 Mikan 直播源检测工具 v6.4")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #FF8A9C;")
        layout.addWidget(title)

        subtitle = QLabel("暴力截停 · 搜索过滤 · 复选框打包 · 三种IP模式独立")
        subtitle.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(subtitle)

        # 工具栏
        toolbar = QHBoxLayout()
        self.import_btn = QPushButton("📂 导入 m3u")
        self.import_btn.clicked.connect(self.import_m3u)
        toolbar.addWidget(self.import_btn)

        self.test_btn = QPushButton("🔍 开始检测")
        self.test_btn.setEnabled(False)
        self.test_btn.clicked.connect(self.start_test)
        self.test_btn.setStyleSheet("background: #A8E6CF; color: white; font-weight: bold;")
        toolbar.addWidget(self.test_btn)

        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setStyleSheet("background: #FF8A9C; color: white; font-weight: bold;")
        toolbar.addWidget(self.stop_btn)

        toolbar.addStretch()

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索频道名...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setMaximumWidth(200)
        toolbar.addWidget(self.search_input)

        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("background: #E8E0D8;")
        toolbar.addWidget(self.settings_btn)

        layout.addLayout(toolbar)

        # 信息栏
        info = QHBoxLayout()
        self.file_label = QLabel("📁 未导入文件")
        self.file_label.setStyleSheet("color: #888;")
        info.addWidget(self.file_label)
        info.addStretch()
        self.config_summary = QLabel("")
        self.config_summary.setStyleSheet("color: #aaa; font-size: 10px;")
        info.addWidget(self.config_summary)
        layout.addLayout(info)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态
        status = QHBoxLayout()
        self.status_label = QLabel("💡 请导入 m3u 文件")
        self.status_label.setStyleSheet("color: #888;")
        status.addWidget(self.status_label)
        status.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #888;")
        status.addWidget(self.count_label)
        layout.addLayout(status)

        # 打包按钮
        pack_layout = QHBoxLayout()
        self.pack_all_btn = QPushButton("📦 打包所有可用源")
        self.pack_all_btn.setEnabled(False)
        self.pack_all_btn.clicked.connect(self.pack_all)
        self.pack_all_btn.setStyleSheet("background: #FFD1D6;")
        pack_layout.addWidget(self.pack_all_btn)

        self.pack_selected_btn = QPushButton("📦 打包选中频道")
        self.pack_selected_btn.setEnabled(False)
        self.pack_selected_btn.clicked.connect(self.pack_selected)
        self.pack_selected_btn.setStyleSheet("background: #A8E6CF;")
        pack_layout.addWidget(self.pack_selected_btn)

        self.select_all_btn = QPushButton("☑️ 全选")
        self.select_all_btn.setEnabled(False)
        self.select_all_btn.clicked.connect(self.select_all)
        pack_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("☐ 取消全选")
        self.deselect_all_btn.setEnabled(False)
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        pack_layout.addWidget(self.deselect_all_btn)

        pack_layout.addStretch()
        layout.addLayout(pack_layout)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(9)
        self.result_table.setHorizontalHeaderLabels(
            ["", "状态", "频道名", "状态码", "尝试", "延迟(ms)", "IP", "国家", "URL"]
        )
        self.result_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)
        self.result_table.setStyleSheet("""
            QTableWidget {
                background: #FDF6F0;
                border: 2px solid #FFD1D6;
                border-radius: 10px;
                gridline-color: #FFE6E8;
            }
            QTableWidget::item { padding: 4px 6px; }
            QTableWidget::item:selected { background: #FFB3BA; color: white; }
            QHeaderView::section {
                background: #FFF0F0;
                padding: 4px 6px;
                border: none;
                font-weight: bold;
                color: #444;
            }
        """)
        layout.addWidget(self.result_table, 1)

    def update_status(self):
        self.config_summary.setText(
            f"超时{self.config.get('timeout',10)}s · "
            f"重试{self.config.get('retries',3)}次 · "
            f"并发{self.config.get('max_workers',10)}"
        )

    def import_m3u(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 m3u 文件", str(Path.home()), "M3U 文件 (*.m3u *.m3u8)")
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.channels = M3UParser.parse(content)
            if not self.channels:
                QMessageBox.warning(self, "提示", "未解析到任何频道")
                return

            self.file_label.setText(f"📁 {Path(path).name} — {len(self.channels)} 个频道")
            self.test_btn.setEnabled(True)
            self.result_table.setRowCount(0)
            self.results = []
            self.status_label.setText(f"✅ 已导入 {len(self.channels)} 个频道")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def start_test(self):
        if not self.channels:
            return

        self.testing = True
        self.test_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pack_all_btn.setEnabled(False)
        self.pack_selected_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.channels))
        self.progress_bar.setValue(0)
        self.result_table.setRowCount(0)
        self.results = []
        self.status_label.setText("🔍 检测中...")

        self.tester = SourceTester(self.channels, self.config)
        self.tester.progress.connect(self.on_progress)
        self.tester.result.connect(self.on_result)
        self.tester.finished.connect(self.on_finished)
        self.tester.start()

    def stop_test(self):
        """暴力停止 - 立即终止"""
        if self.tester:
            self.tester.stop()
            self.stop_btn.setEnabled(False)
            self.status_label.setText("⏹ 正在停止...")
            QApplication.processEvents()
            QTimer.singleShot(500, self.on_stop_done)

    def on_stop_done(self):
        self.status_label.setText("⏹ 已停止")
        self.stop_btn.setEnabled(False)

    def on_progress(self, current, total, name):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"🔍 {current}/{total} — {name[:40]}")

    def on_result(self, result):
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)

        # 复选框
        cb = QCheckBox()
        cb.setChecked(False)
        self.result_table.setCellWidget(row, 0, cb)

        status = result.get("status", "未知")
        name = result.get("name", "未知")
        code = str(result.get("code", "")) if result.get("code") else "-"
        attempts = str(result.get("attempts", 0))
        latency = str(result.get("latency", -1)) if result.get("latency", -1) >= 0 else "-"
        ip = result.get("ip", "-")
        country = result.get("country", "-")
        url = result.get("url", "")

        status_item = QTableWidgetItem(status)
        if "✅" in status:
            status_item.setForeground(QColor("#2e7d32"))
        elif "❌" in status or "错误" in status:
            status_item.setForeground(QColor("#c62828"))
        elif "⏰" in status:
            status_item.setForeground(QColor("#f57c00"))
        elif "⏹" in status:
            status_item.setForeground(QColor("#f57c00"))
        elif "🔌" in status:
            status_item.setForeground(QColor("#6a1b9a"))

        self.result_table.setItem(row, 1, status_item)
        self.result_table.setItem(row, 2, QTableWidgetItem(name[:60]))
        self.result_table.setItem(row, 3, QTableWidgetItem(code))
        self.result_table.setItem(row, 4, QTableWidgetItem(attempts))
        self.result_table.setItem(row, 5, QTableWidgetItem(latency))
        self.result_table.setItem(row, 6, QTableWidgetItem(ip[:20]))
        self.result_table.setItem(row, 7, QTableWidgetItem(country))
        self.result_table.setItem(row, 8, QTableWidgetItem(url))

        self.results.append(result)
        self.apply_search_filter()

    def on_finished(self):
        self.testing = False
        self.test_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        good = [r for r in self.results if "✅" in r.get("status", "")]
        if self.results:
            self.status_label.setText(f"✅ 检测完成！可用: {len(good)}/{len(self.results)}")
        else:
            self.status_label.setText("⏹ 已停止")

        if good:
            self.pack_all_btn.setEnabled(True)
            self.select_all_btn.setEnabled(True)
            self.deselect_all_btn.setEnabled(True)
            self.pack_selected_btn.setEnabled(True)
            if self.config.get("auto_export"):
                self.pack_all()

    def on_search(self, text):
        self.search_keyword = text.strip().lower()
        self.apply_search_filter()

    def apply_search_filter(self):
        keyword = self.search_keyword
        for row in range(self.result_table.rowCount()):
            name_item = self.result_table.item(row, 2)
            if name_item:
                visible = keyword in name_item.text().lower() if keyword else True
                self.result_table.setRowHidden(row, not visible)

    def get_selected_rows(self) -> List[int]:
        rows = []
        for row in range(self.result_table.rowCount()):
            if self.result_table.isRowHidden(row):
                continue
            cb = self.result_table.cellWidget(row, 0)
            if cb and cb.isChecked():
                rows.append(row)
        return rows

    def get_selected_count(self) -> int:
        return len(self.get_selected_rows())

    def select_all(self):
        for row in range(self.result_table.rowCount()):
            if not self.result_table.isRowHidden(row):
                cb = self.result_table.cellWidget(row, 0)
                if cb:
                    cb.setChecked(True)
        self.update_selected_count()

    def deselect_all(self):
        for row in range(self.result_table.rowCount()):
            cb = self.result_table.cellWidget(row, 0)
            if cb:
                cb.setChecked(False)
        self.update_selected_count()

    def update_selected_count(self):
        count = self.get_selected_count()
        self.pack_selected_btn.setText(f"📦 打包选中 ({count}个)" if count > 0 else "📦 打包选中")
        self.pack_selected_btn.setEnabled(count > 0)

    def pack_all(self):
        good = [r for r in self.results if "✅" in r.get("status", "")]
        if not good:
            QMessageBox.warning(self, "提示", "没有可用的源")
            return
        self.export_channels(good, "所有可用源")

    def pack_selected(self):
        rows = self.get_selected_rows()
        if not rows:
            QMessageBox.warning(self, "提示", "请先勾选要打包的频道")
            return

        channels = []
        for row in rows:
            url_item = self.result_table.item(row, 8)
            raw = f"#EXTINF:-1,{self.result_table.item(row, 2).text()}" if self.result_table.item(row, 2) else "#EXTINF:-1,"
            if url_item:
                channels.append({
                    "name": self.result_table.item(row, 2).text() if self.result_table.item(row, 2) else "未知",
                    "url": url_item.text(),
                    "raw": raw,
                })
        self.export_channels(channels, f"选中{len(channels)}个")

    def export_channels(self, channels: List[Dict], label: str):
        path, _ = QFileDialog.getSaveFileName(
            self, f"导出 {label}", self.config.get("export_path", str(Path.home() / "selected.m3u")),
            "M3U 文件 (*.m3u)"
        )
        if not path:
            return

        try:
            M3UParser.export(channels, path)
            QMessageBox.information(self, "成功", f"已导出 {len(channels)} 个频道到:\n{path}")
            self.status_label.setText(f"✅ 已导出 {len(channels)} 个频道")
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            self.update_status()

# ============================================================
# 启动
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()