"""
快速啟動登革熱監測系統網頁
"""

import sys
import io
import os
from pathlib import Path

# 設定 Windows 終端機 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 檢查分析資料是否存在
analysis_file = Path(__file__).parent / "data" / "processed" / "dengue_analysis.json"

if not analysis_file.exists():
    print("=" * 50)
    print("警告：分析資料不存在！")
    print("=" * 50)
    print("請先執行資料分析：")
    print("  python src/analyze_dengue.py")
    print("=" * 50)
    sys.exit(1)

# 切換到 website 目錄並啟動 Flask
os.chdir(Path(__file__).parent / "website")

print("=" * 50)
print("台灣登革熱流行病學監測系統")
print("=" * 50)
print("正在啟動網頁伺服器...")
print("請在瀏覽器中開啟：http://localhost:8080")
print("按 Ctrl+C 停止伺服器")
print("=" * 50)

from app import app
app.run(debug=True, host='127.0.0.1', port=8080)

