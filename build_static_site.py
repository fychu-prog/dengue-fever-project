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
# 使用相對路徑，從當前頁面位置開始（適用於 GitHub Pages）
main_js = main_js.replace("'/api/data'", "'./static/data/dengue_analysis.json'")
# 確保所有 fetch 都使用正確的路徑
main_js = main_js.replace("fetch('static/data/", "fetch('./static/data/")
main_js = main_js.replace('fetch("static/data/', 'fetch("./static/data/')
(DOCS_DIR / "static" / "js" / "main.js").write_text(main_js, encoding='utf-8')

# 修改 county.js
county_js = (DOCS_DIR / "static" / "js" / "county.js").read_text(encoding='utf-8')
# 將 API 路徑改為靜態檔案路徑
county_js = county_js.replace("`/api/data/${countyCode}`", "`./static/data/dengue_analysis.json`")
county_js = county_js.replace("fetch(`static/data/", "fetch(`./static/data/")
county_js = county_js.replace('fetch("static/data/', 'fetch("./static/data/')
county_js = county_js.replace("fetch('static/data/", "fetch('./static/data/")

# 添加完整的前端資料過濾邏輯
filter_function = """
// 前端過濾縣市資料的函數
function filterDataByCounty(data, countyName) {
    const filtered = {
        summary: {},
        time: data.time || {},
        location: {},
        person: {},
        last_updated: data.last_updated || ''
    };
    
    // 縣市名稱對應（處理「臺」vs「台」的差異）
    const possibleNames = [
        countyName,
        countyName.replace(/台/g, '臺'),
        countyName.replace(/臺/g, '台')
    ];
    
    // 找出匹配的縣市名稱
    const allCounties = (data.location?.county || []).map(item => item.居住縣市);
    let matchingName = null;
    for (const name of possibleNames) {
        if (allCounties.includes(name)) {
            matchingName = name;
            break;
        }
    }
    
    if (!matchingName) {
        console.warn('無法找到匹配的縣市名稱:', countyName);
        matchingName = countyName;
    }
    
    // 過濾縣市資料
    filtered.location.county = (data.location?.county || []).filter(
        item => item.居住縣市 === matchingName
    );
    
    // 過濾鄉鎮資料
    filtered.location.township = (data.location?.township_top30 || []).filter(
        item => item.居住縣市 === matchingName
    );
    filtered.location.township_top30 = filtered.location.township;
    
    // 過濾縣市年度趨勢
    filtered.location.county_yearly = (data.location?.county_yearly || []).filter(
        item => item.居住縣市 === matchingName
    );
    
    // 過濾性別和年齡資料（使用該縣市的資料）
    if (data.person) {
        // 性別資料：從原始資料中過濾（如果有縣市欄位）
        filtered.person.gender = data.person.gender || [];
        filtered.person.age = data.person.age || [];
        // 注意：如果原始資料沒有縣市欄位，這裡會使用整體資料
        // 這是一個限制，因為靜態網站無法訪問原始 CSV
    }
    
    // 計算摘要統計
    const countyData = filtered.location.county;
    const townshipData = filtered.location.township;
    
    if (countyData.length > 0) {
        const totalCases = countyData.reduce((sum, item) => sum + (item.病例數 || 0), 0);
        filtered.summary = {
            總病例數: totalCases,
            縣市: matchingName,
            鄉鎮數: townshipData.length
        };
    } else if (townshipData.length > 0) {
        const totalCases = townshipData.reduce((sum, item) => sum + (item.病例數 || 0), 0);
        filtered.summary = {
            總病例數: totalCases,
            縣市: matchingName,
            鄉鎮數: townshipData.length
        };
    } else {
        filtered.summary = {
            總病例數: 0,
            縣市: matchingName,
            鄉鎮數: 0
        };
    }
    
    return filtered;
}
"""

# 在 loadData 函數中添加過濾邏輯
county_js = county_js.replace(
    "// 縣市專頁 JavaScript（高雄/台南）",
    "// 縣市專頁 JavaScript（高雄/台南）\n" + filter_function
)

county_js = county_js.replace(
    "analysisData = await response.json();",
    """const allData = await response.json();
                // 如果是縣市專頁，過濾資料
                if (countyCode && countyCode !== 'main' && countyName) {
                    analysisData = filterDataByCounty(allData, countyName);
                    console.log('已過濾縣市資料:', countyName, analysisData.summary);
                } else {
                    analysisData = allData;
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

