#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查並修復台南和高雄地圖無法顯示的問題
問題：資料中只有 township_top30，但地圖需要所有行政區的資料
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# 設定路徑
GEOJSON_FILE = Path("website/static/data/taiwan_township.geojson")
DATA_FILE = Path("data/processed/dengue_analysis.json")
RAW_DATA = Path("data/raw/Dengue_Daily.csv")
ANALYSIS_FILE = Path("data/processed/dengue_analysis.json")

print("=" * 80)
print("檢查並修復台南和高雄地圖無法顯示的問題")
print("=" * 80)

# 1. 讀取 GeoJSON 檔案
print("\n【步驟 1】讀取 GeoJSON 檔案...")
with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
    geo = json.load(f)

print(f"✓ GeoJSON 載入成功，總 features 數量: {len(geo['features'])}")

# 2. 從 GeoJSON 中提取台南和高雄的所有行政區
print("\n【步驟 2】從 GeoJSON 中提取台南和高雄的所有行政區...")

geojson_townships = {
    '台南市': {},
    '臺南市': {},
    '高雄市': {}
}

for feature in geo['features']:
    props = feature['properties']
    county_name = props.get('COUNTYNAME', '')
    township_name = props.get('TOWNNAME', '')
    
    if not township_name:
        continue
    
    # 處理「台」vs「臺」的差異
    if '臺南' in county_name or '台南' in county_name:
        geojson_townships['台南市'][township_name] = 0  # 預設病例數為 0
        geojson_townships['臺南市'][township_name] = 0
    elif '高雄' in county_name:
        geojson_townships['高雄市'][township_name] = 0

print(f"✓ GeoJSON 中台南市行政區數量: {len(geojson_townships['台南市'])}")
print(f"✓ GeoJSON 中高雄市行政區數量: {len(geojson_townships['高雄市'])}")

# 3. 從原始資料中讀取所有行政區的病例數
print("\n【步驟 3】從原始資料中讀取所有行政區的病例數...")

if RAW_DATA.exists():
    df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
    print(f"✓ 原始資料載入成功，總筆數: {len(df)}")
    
    # 處理台南市
    for county_variant in ['台南市', '臺南市']:
        tainan_df = df[df['居住縣市'] == county_variant].copy()
        if len(tainan_df) > 0:
            print(f"✓ 找到 {county_variant} 資料: {len(tainan_df)} 筆")
            township_counts = tainan_df.groupby('居住鄉鎮').size().reset_index(name='病例數')
            for _, row in township_counts.iterrows():
                township = row['居住鄉鎮']
                cases = row['病例數']
                if pd.notna(township) and township != '未知' and township != '其他':
                    # 更新到 geojson_townships
                    if township in geojson_townships['台南市']:
                        geojson_townships['台南市'][township] = int(cases)
                    if township in geojson_townships['臺南市']:
                        geojson_townships['臺南市'][township] = int(cases)
            break
    
    # 處理高雄市
    kaohsiung_df = df[df['居住縣市'] == '高雄市'].copy()
    if len(kaohsiung_df) > 0:
        print(f"✓ 找到高雄市資料: {len(kaohsiung_df)} 筆")
        township_counts = kaohsiung_df.groupby('居住鄉鎮').size().reset_index(name='病例數')
        for _, row in township_counts.iterrows():
            township = row['居住鄉鎮']
            cases = row['病例數']
            if pd.notna(township) and township != '未知' and township != '其他':
                if township in geojson_townships['高雄市']:
                    geojson_townships['高雄市'][township] = int(cases)
else:
    print("⚠ 原始資料檔案不存在，無法讀取完整行政區資料")

# 4. 生成完整的行政區資料
print("\n【步驟 4】生成完整的行政區資料...")

complete_township_data = {
    '台南市': [],
    '高雄市': []
}

for county_name in ['台南市', '高雄市']:
    for township, cases in geojson_townships[county_name].items():
        complete_township_data[county_name].append({
            '居住縣市': county_name,
            '居住鄉鎮': township,
            '病例數': cases
        })
    
    # 按病例數排序（降序）
    complete_township_data[county_name].sort(key=lambda x: x['病例數'], reverse=True)
    print(f"✓ {county_name} 完整行政區資料: {len(complete_township_data[county_name])} 個")

# 5. 檢查匹配情況
print("\n【步驟 5】檢查匹配情況...")

for county_name in ['台南市', '高雄市']:
    print(f"\n{county_name}:")
    matched = sum(1 for item in complete_township_data[county_name] if item['病例數'] > 0)
    total = len(complete_township_data[county_name])
    print(f"  - 總行政區數: {total}")
    print(f"  - 有病例數的行政區: {matched}")
    print(f"  - 無病例數的行政區: {total - matched}")
    print(f"  - 前 5 名行政區:")
    for i, item in enumerate(complete_township_data[county_name][:5], 1):
        print(f"    {i}. {item['居住鄉鎮']}: {item['病例數']} 例")

# 6. 更新分析資料檔案（可選）
print("\n【步驟 6】建議的解決方案...")
print("\n問題診斷:")
print("1. 資料中只有 township_top30（前 30 名行政區）")
print("2. 地圖需要顯示所有行政區，即使病例數為 0")
print("3. 目前 JavaScript 只使用 township_top30，導致地圖無法顯示所有行政區")
print("\n解決方案:")
print("方案 A: 修改 app.py，在 filter_data_by_county 函數中生成完整的行政區列表")
print("方案 B: 修改 county.js，讓地圖能夠處理只有部分行政區有資料的情況")
print("方案 C: 在分析階段生成完整的 township 資料（包含所有行政區）")
print("\n建議採用方案 A + B 的組合：")
print("- 在 app.py 中從原始資料生成完整的行政區列表")
print("- 在 county.js 中確保地圖能夠正確處理所有行政區（包括病例數為 0 的）")

# 7. 生成修復建議的程式碼片段
print("\n【步驟 7】生成修復建議...")
print("\n建議在 app.py 的 filter_data_by_county 函數中添加以下邏輯：")
print("""
# 生成完整的行政區列表（包含所有行政區，即使病例數為 0）
if RAW_DATA.exists():
    df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
    county_df = df[df['居住縣市'] == matching_county_name].copy()
    
    # 從 GeoJSON 中獲取該縣市的所有行政區名稱
    all_townships = set()
    # ... 從 GeoJSON 讀取所有行政區 ...
    
    # 計算每個行政區的病例數
    township_counts = county_df.groupby('居住鄉鎮').size().reset_index(name='病例數')
    township_dict = dict(zip(township_counts['居住鄉鎮'], township_counts['病例數']))
    
    # 生成完整列表（包含所有行政區）
    complete_township_list = []
    for township in all_townships:
        complete_township_list.append({
            '居住縣市': matching_county_name,
            '居住鄉鎮': township,
            '病例數': township_dict.get(township, 0)
        })
    
    filtered['location']['township'] = complete_township_list
""")

print("\n檢查完成！")

