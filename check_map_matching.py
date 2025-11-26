#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查台南和高雄地圖無法顯示的問題
比較 GeoJSON 檔案中的行政區名稱與病例資料中的行政區名稱是否匹配
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path
from collections import defaultdict

# 設定路徑
GEOJSON_FILE = Path("website/static/data/taiwan_township.geojson")
DATA_FILE = Path("data/processed/dengue_analysis.json")

print("=" * 80)
print("檢查台南和高雄地圖無法顯示的問題")
print("=" * 80)

# 1. 讀取 GeoJSON 檔案
print("\n【步驟 1】讀取 GeoJSON 檔案...")
if not GEOJSON_FILE.exists():
    print(f"❌ GeoJSON 檔案不存在: {GEOJSON_FILE}")
    sys.exit(1)

with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
    geo = json.load(f)

print(f"✓ GeoJSON 載入成功，總 features 數量: {len(geo['features'])}")

# 檢查第一個 feature 的屬性
if geo['features']:
    first_props = geo['features'][0]['properties']
    print(f"✓ GeoJSON 屬性鍵: {list(first_props.keys())}")
    print(f"✓ 第一個 feature 範例: {first_props}")

# 2. 讀取病例資料
print("\n【步驟 2】讀取病例資料...")
if not DATA_FILE.exists():
    print(f"❌ 資料檔案不存在: {DATA_FILE}")
    sys.exit(1)

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("✓ 病例資料載入成功")

# 3. 提取台南和高雄的行政區資料
print("\n【步驟 3】提取台南和高雄的行政區資料...")

# 從病例資料中提取行政區名稱
county_township_data = defaultdict(dict)

# 檢查資料結構（使用 township_top30）
if 'location' in data:
    township_list = data['location'].get('township_top30', []) or data['location'].get('township', [])
    print(f"✓ 找到 {len(township_list)} 筆行政區資料")
    
    for item in township_list:
        county = item.get('居住縣市', '')
        township = item.get('居住鄉鎮', '') or item.get('鄉鎮', '') or item.get('行政區', '')
        cases = item.get('病例數', 0)
        
        if county and township and township != '未知':
            if county not in county_township_data:
                county_township_data[county] = {}
            county_township_data[county][township] = cases
else:
    print("⚠ 找不到 location 資料")

# 4. 從 GeoJSON 中提取台南和高雄的行政區
print("\n【步驟 4】從 GeoJSON 中提取台南和高雄的行政區...")

# 找出 GeoJSON 中使用的屬性鍵
district_key = None
county_key = None

if geo['features']:
    first_props = geo['features'][0]['properties']
    
    # 尋找行政區名稱屬性
    possible_district_keys = ['TOWNNAME', 'TOWN', 'name', '鄉鎮', '行政區', 'NAME_2014', 'TOWNNAME_2014', 'TOWNNAME_109']
    for key in possible_district_keys:
        if key in first_props:
            district_key = key
            break
    
    # 尋找縣市名稱屬性
    possible_county_keys = ['COUNTYNAME', 'COUNTY', '縣市', 'COUNTY_2014', 'COUNTYNAME_109']
    for key in possible_county_keys:
        if key in first_props:
            county_key = key
            break

print(f"✓ 找到的屬性鍵: district_key={district_key}, county_key={county_key}")

if not district_key:
    print("❌ 無法找到行政區名稱屬性！")
    sys.exit(1)

# 提取台南和高雄的行政區
geojson_townships = {
    '台南市': [],
    '臺南市': [],
    '高雄市': []
}

for feature in geo['features']:
    props = feature['properties']
    county_name = props.get(county_key, '') if county_key else ''
    township_name = props.get(district_key, '')
    
    if not township_name:
        continue
    
    # 處理「台」vs「臺」的差異
    if '臺南' in county_name or '台南' in county_name:
        geojson_townships['台南市'].append(township_name)
        geojson_townships['臺南市'].append(township_name)
    elif '高雄' in county_name:
        geojson_townships['高雄市'].append(township_name)

print(f"✓ GeoJSON 中台南市行政區數量: {len(geojson_townships['台南市'])}")
print(f"✓ GeoJSON 中高雄市行政區數量: {len(geojson_townships['高雄市'])}")

# 5. 比較匹配情況
print("\n" + "=" * 80)
print("【步驟 5】比較匹配情況")
print("=" * 80)

for county_name in ['台南市', '高雄市']:
    print(f"\n{'='*80}")
    print(f"檢查: {county_name}")
    print(f"{'='*80}")
    
    # 取得病例資料中的行政區
    data_townships = set()
    for county_key_data in county_township_data.keys():
        # 處理「台」vs「臺」的差異
        if county_name == '台南市':
            if '台南' in county_key_data or '臺南' in county_key_data:
                data_townships.update(county_township_data[county_key_data].keys())
        elif county_name == '高雄市':
            if '高雄' in county_key_data:
                data_townships.update(county_township_data[county_key_data].keys())
    
    # 取得 GeoJSON 中的行政區
    geojson_set = set(geojson_townships[county_name])
    
    print(f"\n病例資料中的行政區數量: {len(data_townships)}")
    print(f"GeoJSON 中的行政區數量: {len(geojson_set)}")
    
    # 找出匹配的行政區
    matched = data_townships & geojson_set
    print(f"✓ 完全匹配的行政區數量: {len(matched)}")
    
    # 找出只在病例資料中的行政區
    only_in_data = data_townships - geojson_set
    if only_in_data:
        print(f"\n⚠ 只在病例資料中的行政區 ({len(only_in_data)} 個):")
        for name in sorted(only_in_data):
            cases = 0
            for county_key_data in county_township_data.keys():
                if county_name == '台南市' and ('台南' in county_key_data or '臺南' in county_key_data):
                    cases = county_township_data[county_key_data].get(name, 0)
                    break
                elif county_name == '高雄市' and '高雄' in county_key_data:
                    cases = county_township_data[county_key_data].get(name, 0)
                    break
            print(f"  - {name} (病例數: {cases})")
    
    # 找出只在 GeoJSON 中的行政區
    only_in_geojson = geojson_set - data_townships
    if only_in_geojson:
        print(f"\n⚠ 只在 GeoJSON 中的行政區 ({len(only_in_geojson)} 個):")
        for name in sorted(only_in_geojson):
            print(f"  - {name}")
    
    # 檢查可能的模糊匹配（移除後綴）
    print(f"\n【模糊匹配檢查】")
    unmatched_in_data = []
    for data_name in only_in_data:
        data_clean = data_name.replace('區', '').replace('鄉', '').replace('鎮', '').replace('市', '')
        found_match = False
        for geojson_name in only_in_geojson:
            geojson_clean = geojson_name.replace('區', '').replace('鄉', '').replace('鎮', '').replace('市', '')
            if data_clean == geojson_clean:
                print(f"  ✓ 可能匹配: '{data_name}' (資料) <-> '{geojson_name}' (GeoJSON)")
                found_match = True
                break
        if not found_match:
            unmatched_in_data.append(data_name)
    
    if unmatched_in_data:
        print(f"\n  ⚠ 無法匹配的行政區 ({len(unmatched_in_data)} 個):")
        for name in sorted(unmatched_in_data):
            print(f"    - {name}")
    
    # 顯示匹配的行政區範例
    if matched:
        print(f"\n✓ 匹配成功的行政區範例 (前 10 個):")
        for name in sorted(list(matched))[:10]:
            cases = 0
            for county_key_data in county_township_data.keys():
                if county_name == '台南市' and ('台南' in county_key_data or '臺南' in county_key_data):
                    cases = county_township_data[county_key_data].get(name, 0)
                    break
                elif county_name == '高雄市' and '高雄' in county_key_data:
                    cases = county_township_data[county_key_data].get(name, 0)
                    break
            print(f"  - {name}: {cases} 例")

# 6. 總結
print("\n" + "=" * 80)
print("【總結】")
print("=" * 80)

print("\n可能的原因：")
print("1. 行政區名稱不完全匹配（例如：'東區' vs '東區區'）")
print("2. 縣市名稱不一致（例如：'台南市' vs '臺南市'）")
print("3. GeoJSON 檔案中缺少某些行政區")
print("4. 病例資料中缺少某些行政區")
print("\n建議：")
print("- 檢查 JavaScript 中的匹配邏輯（county.js 的 renderCountyMap 函數）")
print("- 確認模糊匹配是否正確處理了名稱差異")
print("- 檢查瀏覽器控制台的錯誤訊息")

