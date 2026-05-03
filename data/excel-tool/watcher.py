"""
文件监听服务 - Watchdog
========================
监控 /home/agentuser/shared/ 目录。
自动解析新放入的 .xlsx/.xls/.csv 文件并输出 JSON。

Author: Tristan (技术架构官)
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 导入同级 parser 模块
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parser import parse_to_json

# ----------------------------------------------------------------
#  配置
# ----------------------------------------------------------------
WATCH_DIR = os.getenv("EXCEL_WATCH_DIR", "/home/agentuser/shared")
TEMPLATE = os.getenv("EXCEL_WATCH_TEMPLATE", "zwf20")
POLL_INTERVAL = float(os.getenv("EXCEL_WATCH_INTERVAL", 1.0))
SLEEP_BEFORE_PARSE = 1.5  # 秒，等待文件写入完成

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] watcher: %(message)s",
)
logger = logging.getLogger("file-watcher")


# ----------------------------------------------------------------
#  事件处理器
# ----------------------------------------------------------------
SUPPORTED_EXTS = {".xlsx", ".xls", ".csv"}


class ExcelHandler(FileSystemEventHandler):
    """监控新文件的创建/移动事件"""

    def on_created(self, event):
        self._process(event)

    def on_moved(self, event):
        # 文件移入目标目录（完成写入）
        if event.dest_path.startswith(WATCH_DIR):
            self._process_event(event.dest_path)

    def _process(self, event):
        if event.is_directory:
            return
        path = event.src_path
        ext = Path(path).suffix.lower()
        if ext not in SUPPORTED_EXTS:
            return
        # 等待文件写入完成
        time.sleep(SLEEP_BEFORE_PARSE)
        self._process_file(path)

    @staticmethod
    def _process_event(path: str):
        ext = Path(path).suffix.lower()
        if ext not in SUPPORTED_EXTS:
            return
        time.sleep(SLEEP_BEFORE_PARSE)
        ExcelHandler._process_file(path)

    @staticmethod
    def _process_file(path: str):
        if not os.path.isfile(path):
            logger.warning("文件已消失: %s", path)
            return
        try:
            logger.info("检测到新文件: %s", path)
            result = parse_to_json(path, TEMPLATE, output_dir=WATCH_DIR)
            n = result.get("total", 0)
            out = result.get("_json_output", f"{Path(path).stem}.json")
            logger.info("✅ 解析完成: %s → %d 条记录 (JSON: %s)",
                        Path(path).name, n, out)
        except Exception as e:
            logger.error("❌ 解析失败: %s — %s", path, e)


# ----------------------------------------------------------------
#  启动
# ----------------------------------------------------------------

def start_watcher():
    os.makedirs(WATCH_DIR, exist_ok=True)
    logger.info("文件监听服务启动 | 目录: %s | 模板: %s", WATCH_DIR, TEMPLATE)

    event_handler = ExcelHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("文件监听服务已停止")
    observer.join()


if __name__ == "__main__":
    start_watcher()
