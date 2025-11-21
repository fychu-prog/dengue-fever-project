#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""建立 GitHub Pages 靜態網站版本"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import shutil
from pathlib import Path

# 設定路徑
BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
WEBSITE_DIR = BASE_DIR / "website"
DATA_DIR = BASE_DIR / "data" / "processed"

# 建立 docs 目錄結構
print("建立目錄結構...")
(DOCS_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
(DOCS_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
(DOCS_DIR / "static" / "data").mkdir(parents=True, exist_ok=True)

# 複製 CSS
print("複製 CSS 檔案...")
shutil.copy(WEBSITE_DIR / "static" / "css" / "style.css", DOCS_DIR / "static" / "css" / "style.css")

# 複製 JS 檔案
print("複製 JavaScript 檔案...")
shutil.copy(WEBSITE_DIR / "static" / "js" / "main.js", DOCS_DIR / "static" / "js" / "main.js")
shutil.copy(WEBSITE_DIR / "static" / "js" / "county.js", DOCS_DIR / "static" / "js" / "county.js")

# 複製資料檔案
if (DATA_DIR / "dengue_analysis.json").exists():
    print("複製資料檔案...")
    shutil.copy(DATA_DIR / "dengue_analysis.json", DOCS_DIR / "static" / "data" / "dengue_analysis.json")
    print("[OK] 資料檔案已複製")
else:
    print("[WARNING] 找不到資料檔案，請先執行 python src/analyze_dengue.py")

# 讀取並修改 HTML 檔案
print("建立 HTML 檔案...")

# 讀取原始 HTML
index_html = (WEBSITE_DIR / "templates" / "index.html").read_text(encoding='utf-8')
kaohsiung_html = (WEBSITE_DIR / "templates" / "kaohsiung.html").read_text(encoding='utf-8')
tainan_html = (WEBSITE_DIR / "templates" / "tainan.html").read_text(encoding='utf-8')

# 替換 Flask 的 url_for 為相對路徑
def replace_flask_paths(html_content):
    html_content = html_content.replace(
        '{{ url_for(\'static\', filename=\'css/style.css\') }}',
        'static/css/style.css'
    )
    html_content = html_content.replace(
        '{{ url_for(\'static\', filename=\'js/main.js\') }}',
        'static/js/main.js'
    )
    html_content = html_content.replace(
        '{{ url_for(\'static\', filename=\'js/county.js\') }}',
        'static/js/county.js'
    )
    # 替換導航連結
    html_content = html_content.replace('href="/"', 'href="index.html"')
    html_content = html_content.replace('href="/kaohsiung"', 'href="kaohsiung.html"')
    html_content = html_content.replace('href="/tainan"', 'href="tainan.html"')
    return html_content

# 寫入修改後的 HTML
(DOCS_DIR / "index.html").write_text(replace_flask_paths(index_html), encoding='utf-8')
(DOCS_DIR / "kaohsiung.html").write_text(replace_flask_paths(kaohsiung_html), encoding='utf-8')
(DOCS_DIR / "tainan.html").write_text(replace_flask_paths(tainan_html), encoding='utf-8')

print("[OK] HTML 檔案已建立")

# 修改 main.js 讓它讀取靜態 JSON
print("修改 JavaScript 以讀取靜態資料...")
main_js = (DOCS_DIR / "static" / "js" / "main.js").read_text(encoding='utf-8')
# 將 API 路徑改為靜態檔案路徑
main_js = main_js.replace("'/api/data'", "'static/data/dengue_analysis.json'")
(DOCS_DIR / "static" / "js" / "main.js").write_text(main_js, encoding='utf-8')

# 修改 county.js
county_js = (DOCS_DIR / "static" / "js" / "county.js").read_text(encoding='utf-8')
# 將 API 路徑改為靜態檔案路徑（需要特殊處理，因為是動態路徑）
county_js = county_js.replace("`/api/data/${countyCode}`", "`static/data/dengue_analysis.json`")
# 添加資料過濾邏輯（在載入後過濾）
county_js = county_js.replace(
    "analysisData = await response.json();",
    """analysisData = await response.json();
                // 如果是縣市專頁，需要過濾資料
                if (countyCode && countyCode !== 'main') {
                    // 這裡需要在前端過濾資料，或使用預先處理的 JSON
                    console.log('縣市專頁需要過濾資料:', countyCode);
                }"""
)
(DOCS_DIR / "static" / "js" / "county.js").write_text(county_js, encoding='utf-8')

print("[OK] JavaScript 已修改")

print("\n" + "="*60)
print("靜態網站已建立完成！")
print("="*60)
print(f"檔案位置: {DOCS_DIR}")
print("\n下一步:")
print("1. 檢查 docs/ 目錄中的檔案")
print("2. 提交到 Git: git add docs/ && git commit -m 'Add static site for GitHub Pages'")
print("3. 推送到 GitHub: git push")
print("4. 在 GitHub 設定 Pages: Settings > Pages > Source: /docs")
print("="*60)

