"""
Excel 解析服务 - Web API
========================
基于 Flask，提供 HTTP 调用接口。

Author: Tristan (技术架构官)
"""

import os
import json
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify

from parser import parse_to_json, TEMPLATES, parse_excel

# ----------------------------------------------------------------
#  配置
# ----------------------------------------------------------------
HOST = os.getenv("EXCEL_TOOL_HOST", "127.0.0.1")
PORT = int(os.getenv("EXCEL_TOOL_PORT", 5100))
DEBUG = os.getenv("EXCEL_TOOL_DEBUG", "false").lower() == "true"
SHARED_DIR = os.getenv("EXCEL_SHARED_DIR", "/home/agentuser/shared")

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("excel-api")

app = Flask(__name__)


# ----------------------------------------------------------------
#  API
# ----------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "excel-tool",
        "templates": list(TEMPLATES.keys()),
        "shared_dir": SHARED_DIR,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    })


@app.route("/api/v1/templates", methods=["GET"])
def list_templates():
    """列出可用模板"""
    info = {}
    for name, tpl in TEMPLATES.items():
        info[name] = {
            "columns": list(tpl["columns"].values()),
            "description": tpl["description"],
        }
    return jsonify({"code": 0, "data": info})


@app.route("/api/v1/parse/upload", methods=["POST"])
def parse_upload():
    """
    上传 Excel 文件并解析
    ---
    Multipart:
        file: Excel 文件（必填）
        template: 模板名（可选，默认 zwf20）
        output_json: 是否输出 JSON（可选，默认 true）

    返回: 解析结果 JSON
    """
    if "file" not in request.files:
        return jsonify({"code": 2002, "message": "缺少 file 字段"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"code": 2002, "message": "文件名为空"}), 400

    template = request.form.get("template", "zwf20")
    output_json = request.form.get("output_json", "true").lower() == "true"

    # 保存到临时目录
    suffix = Path(f.filename).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        f.save(tmp.name)
        logger.info("收到文件: %s → %s", f.filename, tmp.name)

        result = parse_to_json(tmp.name, template,
                               output_dir=SHARED_DIR if output_json else None)

        return jsonify({"code": 0, "message": "ok", "data": result})
    except Exception as e:
        logger.exception("解析失败")
        return jsonify({"code": 5000, "message": str(e)}), 500
    finally:
        os.unlink(tmp.name)


@app.route("/api/v1/parse/file", methods=["POST"])
def parse_file():
    """
    解析服务端已有文件
    ---
    Body:
        file_path: str  文件绝对路径
        template:  str  模板名（默认 zwf20）
    """
    data = request.get_json(silent=True) or {}
    file_path = data.get("file_path", "")
    template = data.get("template", "zwf20")

    if not file_path:
        return jsonify({"code": 2002, "message": "缺少 file_path"}), 400
    if not os.path.isfile(file_path):
        return jsonify({"code": 2004, "message": f"文件不存在: {file_path}"}), 404

    result = parse_to_json(file_path, template, output_dir=SHARED_DIR)
    return jsonify({"code": 0, "message": "ok", "data": result})


if __name__ == "__main__":
    os.makedirs(SHARED_DIR, exist_ok=True)
    logger.info("启动 Excel 解析服务: %s:%d", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
