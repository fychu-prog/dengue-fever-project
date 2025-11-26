#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查 GeoJSON 檔案中台南市的行政區
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path

# 設定路徑
GEOJSON_FILE = Path(__file__).parent / "website" / "static" / "data" / "taiwan_township.geojson"

print("=" * 60)
print("檢查 GeoJSON 檔案中台南市的行政區")
print("=" * 60)

# 讀取 GeoJSON
print(f"\n正在讀取 GeoJSON: {GEOJSON_FILE}")
with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
    geo = json.load(f)

print(f"總 features 數量: {len(geo['features'])}")

# 過濾台南市（處理「台」vs「臺」）
tainan_features = [
    f for f in geo['features'] 
    if '臺南市' in f['properties'].get('COUNTYNAME', '') or 
       '台南市' in f['properties'].get('COUNTYNAME', '')
]

print(f"\n台南市 features 數量: {len(tainan_features)}")

# 取得所有行政區名稱
townships = sorted([f['properties']['TOWNNAME'] for f in tainan_features])

print(f"\nGeoJSON 中台南市共有 {len(townships)} 個行政區：")
print("-" * 60)

for i, township in enumerate(townships, 1):
    print(f"{i:2d}. {township}")

print("-" * 60)
print(f"總計: {len(townships)} 個行政區")


