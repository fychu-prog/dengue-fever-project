#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查台灣縣市合併後的命名對應問題
2010年縣市合併：
- 臺中縣 + 臺中市 → 臺中市
- 臺南縣 + 臺南市 → 臺南市
- 高雄縣 + 高雄市 → 高雄市
- 臺北縣 → 新北市
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

# 設定路徑
GEOJSON_FILE = Path("website/static/data/taiwan_township.geojson")
DATA_FILE = Path("data/processed/dengue_analysis.json")
RAW_DATA = Path("data/raw/Dengue_Daily.csv")

print("=" * 80)
print("檢查台灣縣市合併後的命名對應問題")
print("=" * 80)

# 縣市合併對應表（2010年合併前 → 合併後）
COUNTY_MERGER_MAP = {
    '臺中縣': '臺中市',
    '台中縣': '臺中市',
    '臺南縣': '臺南市',
    '台南縣': '臺南市',
    '高雄縣': '高雄市',
    '臺北縣': '新北市',
    '台北縣': '新北市',
    # 合併後的標準名稱
    '臺中市': '臺中市',
    '台中市': '臺中市',
    '臺南市': '臺南市',
    '台南市': '臺南市',
    '高雄市': '高雄市',
    '新北市': '新北市',
}

# 縣市合併規則（合併前 → 合併後）
MERGER_RULES = {
    '臺中縣': '臺中市',
    '台中縣': '臺中市',
    '臺南縣': '臺南市',
    '台南縣': '臺南市',
    '高雄縣': '高雄市',
    '臺北縣': '新北市',
    '台北縣': '新北市',
}

print("\n【縣市合併規則（2010年）】")
print("-" * 80)
for old_name, new_name in MERGER_RULES.items():
    print(f"  {old_name} → {new_name}")

# 1. 檢查 GeoJSON 中的縣市名稱
print("\n【步驟 1】檢查 GeoJSON 中的縣市名稱...")
if GEOJSON_FILE.exists():
    with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    geojson_counties = Counter()
    geojson_county_townships = defaultdict(set)
    
    for feature in geo['features']:
        props = feature['properties']
        county_name = props.get('COUNTYNAME', '')
        township_name = props.get('TOWNNAME', '')
        
        if county_name:
            geojson_counties[county_name] += 1
            geojson_county_townships[county_name].add(township_name)
    
    print(f"✓ GeoJSON 中發現 {len(geojson_counties)} 個縣市")
    print("\nGeoJSON 中的縣市列表（按數量排序）：")
    for county, count in geojson_counties.most_common():
        print(f"  {county:15s}: {count:3d} 個行政區")
    
    # 檢查是否有舊縣市名稱
    old_counties_in_geojson = [c for c in geojson_counties.keys() if c in MERGER_RULES]
    if old_counties_in_geojson:
        print(f"\n⚠ 警告: GeoJSON 中包含合併前的舊縣市名稱:")
        for old_county in old_counties_in_geojson:
            print(f"  - {old_county} (應改為 {MERGER_RULES[old_county]})")
    else:
        print("\n✓ GeoJSON 中沒有合併前的舊縣市名稱（已更新）")
else:
    print("❌ GeoJSON 檔案不存在")
    geojson_counties = Counter()
    geojson_county_townships = defaultdict(set)

# 2. 檢查病例資料中的縣市名稱
print("\n【步驟 2】檢查病例資料中的縣市名稱...")

# 2.1 檢查處理過的資料
if DATA_FILE.exists():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    processed_counties = Counter()
    if 'location' in data and 'county' in data['location']:
        for item in data['location']['county']:
            county = item.get('居住縣市', '')
            if county:
                processed_counties[county] += item.get('病例數', 0)
    
    print(f"✓ 處理過的資料中發現 {len(processed_counties)} 個縣市")
    print("\n處理過的資料中的縣市列表（按病例數排序）：")
    for county, cases in sorted(processed_counties.items(), key=lambda x: x[1], reverse=True):
        print(f"  {county:15s}: {cases:>8,} 例")
    
    # 檢查是否有舊縣市名稱
    old_counties_in_processed = [c for c in processed_counties.keys() if c in MERGER_RULES]
    if old_counties_in_processed:
        print(f"\n⚠ 警告: 處理過的資料中包含合併前的舊縣市名稱:")
        for old_county in old_counties_in_processed:
            print(f"  - {old_county} (應改為 {MERGER_RULES[old_county]})")
    else:
        print("\n✓ 處理過的資料中沒有合併前的舊縣市名稱（已更新）")
else:
    print("❌ 處理過的資料檔案不存在")
    processed_counties = Counter()

# 2.2 檢查原始資料
print("\n【步驟 3】檢查原始資料中的縣市名稱...")
if RAW_DATA.exists():
    df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
    print(f"✓ 原始資料載入成功，總筆數: {len(df):,}")
    
    # 統計縣市名稱
    raw_counties = df['居住縣市'].value_counts()
    print(f"\n原始資料中發現 {len(raw_counties)} 個不同的縣市名稱")
    print("\n原始資料中的縣市列表（按病例數排序）：")
    for county, count in raw_counties.head(20).items():
        if pd.notna(county):
            print(f"  {county:15s}: {count:>8,} 例")
    
    # 檢查是否有舊縣市名稱
    old_counties_in_raw = [c for c in raw_counties.index if pd.notna(c) and c in MERGER_RULES]
    if old_counties_in_raw:
        print(f"\n⚠ 警告: 原始資料中包含合併前的舊縣市名稱:")
        total_old_cases = 0
        for old_county in old_counties_in_raw:
            cases = raw_counties[old_county]
            new_name = MERGER_RULES[old_county]
            print(f"  - {old_county:15s}: {cases:>8,} 例 (應合併到 {new_name})")
            total_old_cases += cases
        
        print(f"\n  總計舊縣市病例數: {total_old_cases:,} 例")
        print("  建議: 在資料處理時將這些舊縣市名稱統一為新名稱")
    else:
        print("\n✓ 原始資料中沒有合併前的舊縣市名稱（已更新）")
    
    # 檢查「台」vs「臺」的差異
    print("\n【步驟 4】檢查「台」vs「臺」的命名差異...")
    tai_variants = {}
    for county in raw_counties.index:
        if pd.notna(county):
            if '台' in county or '臺' in county:
                normalized = county.replace('台', '臺')
                if normalized not in tai_variants:
                    tai_variants[normalized] = []
                tai_variants[normalized].append((county, raw_counties[county]))
    
    if tai_variants:
        print("發現「台」vs「臺」的命名差異:")
        for normalized, variants in tai_variants.items():
            if len(variants) > 1:
                print(f"\n  {normalized} 的變體:")
                total_cases = 0
                for variant, cases in variants:
                    print(f"    - {variant:15s}: {cases:>8,} 例")
                    total_cases += cases
                print(f"    總計: {total_cases:>8,} 例")
    
    # 統計主要縣市的資料
    print("\n【步驟 5】主要縣市資料統計...")
    major_counties = ['臺南市', '台南市', '臺南縣', '台南縣', 
                     '高雄市', '高雄縣',
                     '臺中市', '台中市', '臺中縣', '台中縣',
                     '新北市', '臺北縣', '台北縣']
    
    print("\n主要縣市（含變體）的病例數統計:")
    for county in major_counties:
        if county in raw_counties.index:
            cases = raw_counties[county]
            new_name = MERGER_RULES.get(county, county)
            print(f"  {county:15s} → {new_name:15s}: {cases:>8,} 例")
    
    # 合併統計（將舊縣市合併到新縣市）
    print("\n【步驟 6】合併後的縣市統計（統一命名）...")
    merged_counties = Counter()
    for county, cases in raw_counties.items():
        if pd.notna(county):
            # 統一為「臺」
            normalized = county.replace('台', '臺')
            # 應用合併規則
            final_name = MERGER_RULES.get(normalized, normalized)
            merged_counties[final_name] += cases
    
    print("\n合併後的縣市列表（按病例數排序，Top 10）:")
    for county, cases in merged_counties.most_common(10):
        print(f"  {county:15s}: {cases:>8,} 例")
    
    # 對比 GeoJSON 和病例資料
    print("\n【步驟 7】對比 GeoJSON 和病例資料的縣市名稱...")
    geojson_county_set = set(geojson_counties.keys())
    merged_county_set = set(merged_counties.keys())
    
    only_in_geojson = geojson_county_set - merged_county_set
    only_in_data = merged_county_set - geojson_county_set
    in_both = geojson_county_set & merged_county_set
    
    print(f"\n✓ 兩者都有的縣市: {len(in_both)} 個")
    if in_both:
        print("  範例:", list(in_both)[:5])
    
    if only_in_geojson:
        print(f"\n⚠ 只在 GeoJSON 中的縣市: {len(only_in_geojson)} 個")
        print("  列表:", list(only_in_geojson))
    
    if only_in_data:
        print(f"\n⚠ 只在病例資料中的縣市: {len(only_in_data)} 個")
        print("  列表:", list(only_in_data))
    
    # 檢查台南和高雄的詳細情況
    print("\n【步驟 8】檢查台南和高雄的詳細情況...")
    for target_county in ['臺南市', '高雄市']:
        print(f"\n{target_county}:")
        
        # GeoJSON 中的行政區
        geojson_townships = geojson_county_townships.get(target_county, set())
        print(f"  GeoJSON 行政區數: {len(geojson_townships)}")
        
        # 病例資料中的行政區（從原始資料統計）
        data_townships = set()
        county_variants = [target_county, target_county.replace('臺', '台')]
        for variant in county_variants:
            county_df = df[df['居住縣市'] == variant]
            if len(county_df) > 0:
                townships = county_df['居住鄉鎮'].dropna().unique()
                data_townships.update([t for t in townships if pd.notna(t) and t != '未知' and t != '其他'])
        
        print(f"  病例資料行政區數: {len(data_townships)}")
        
        # 匹配情況
        matched = geojson_townships & data_townships
        only_in_geojson_town = geojson_townships - data_townships
        only_in_data_town = data_townships - geojson_townships
        
        print(f"  完全匹配: {len(matched)} 個")
        if only_in_geojson_town:
            print(f"  ⚠ 只在 GeoJSON 中: {len(only_in_geojson_town)} 個")
            print(f"    範例: {list(only_in_geojson_town)[:5]}")
        if only_in_data_town:
            print(f"  ⚠ 只在病例資料中: {len(only_in_data_town)} 個")
            print(f"    範例: {list(only_in_data_town)[:5]}")
else:
    print("❌ 原始資料檔案不存在")

# 總結
print("\n" + "=" * 80)
print("【總結與建議】")
print("=" * 80)

print("\n1. 縣市合併對應規則:")
for old, new in MERGER_RULES.items():
    print(f"   {old} → {new}")

print("\n2. 建議的資料處理步驟:")
print("   a. 統一「台」vs「臺」的命名（建議統一使用「臺」）")
print("   b. 將合併前的舊縣市名稱統一為新名稱")
print("   c. 在資料分析時應用合併規則")

print("\n3. 需要檢查的檔案:")
print("   - 原始資料 (Dengue_Daily.csv): 檢查是否有舊縣市名稱")
print("   - 處理過的資料 (dengue_analysis.json): 確認已應用合併規則")
print("   - GeoJSON 檔案: 確認使用合併後的縣市名稱")

print("\n檢查完成！")


