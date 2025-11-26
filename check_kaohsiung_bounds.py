#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查高雄市的最北點和最南點，用於設定地圖範圍
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path

# 設定路徑
GEOJSON_FILE = Path("website/static/data/taiwan_township.geojson")

print("=" * 80)
print("檢查高雄市的實際邊界（最北點和最南點）")
print("=" * 80)

# 讀取 GeoJSON
with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
    geo = json.load(f)

print(f"✓ GeoJSON 載入成功，總 features 數量: {len(geo['features'])}")

# 遞迴提取所有座標點
def extract_coordinates(coords, lons, lats):
    """遞迴提取所有座標點"""
    if not isinstance(coords, list) or len(coords) == 0:
        return
    
    # 檢查是否為座標點 [lon, lat]（最內層，兩個數字）
    if len(coords) == 2 and isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
        lon, lat = coords[0], coords[1]
        lons.append(lon)
        lats.append(lat)
        return
    
    # 如果是嵌套陣列，繼續遞迴
    for item in coords:
        if isinstance(item, list):
            extract_coordinates(item, lons, lats)

# 提取高雄市的所有座標點
kaohsiung_lons = []
kaohsiung_lats = []
kaohsiung_features = []

for feature in geo['features']:
    props = feature['properties']
    county_name = props.get('COUNTYNAME', '')
    township_name = props.get('TOWNNAME', '')
    
    # 檢查是否為高雄市（嚴格匹配）
    if county_name == '高雄市':
        kaohsiung_features.append({
            'township': township_name,
            'feature': feature
        })
        geometry = feature.get('geometry')
        if geometry and geometry.get('coordinates'):
            extract_coordinates(geometry['coordinates'], kaohsiung_lons, kaohsiung_lats)

print(f"✓ 找到 {len(kaohsiung_features)} 個高雄市行政區")
print(f"  行政區列表: {[f['township'] for f in kaohsiung_features]}")

print(f"\n✓ 找到 {len(kaohsiung_lons)} 個座標點")

if kaohsiung_lons and kaohsiung_lats:
    min_lon = min(kaohsiung_lons)
    max_lon = max(kaohsiung_lons)
    min_lat = min(kaohsiung_lats)  # 最南點
    max_lat = max(kaohsiung_lats)  # 最北點
    
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat  # 南北距離
    
    print(f"\n高雄市實際邊界:")
    print(f"  最西點（經度）: {min_lon:.6f}°")
    print(f"  最東點（經度）: {max_lon:.6f}°")
    print(f"  最南點（緯度）: {min_lat:.6f}°")
    print(f"  最北點（緯度）: {max_lat:.6f}°")
    print(f"\n中心點:")
    print(f"  經度: {center_lon:.6f}°")
    print(f"  緯度: {center_lat:.6f}°")
    print(f"\n範圍:")
    print(f"  經度範圍: {lon_span:.6f}°")
    print(f"  緯度範圍（南北距離）: {lat_span:.6f}°")
    print(f"\n寬高比:")
    print(f"  經度/緯度: {lon_span/lat_span:.3f}")
    
    # 計算適合網頁容器的範圍（假設容器寬高比約為 1095/600 = 1.825）
    container_aspect = 1095 / 600
    geojson_aspect = lon_span / lat_span
    
    print(f"\n容器寬高比: {container_aspect:.3f}")
    print(f"GeoJSON 寬高比: {geojson_aspect:.3f}")
    
    # 如果容器更寬，需要增加經度範圍
    # 如果容器更高，需要增加緯度範圍
    if container_aspect > geojson_aspect:
        # 容器更寬，需要增加經度範圍
        target_lon_span = lat_span * container_aspect
        lon_padding = (target_lon_span - lon_span) / 2
        final_min_lon = min_lon - lon_padding
        final_max_lon = max_lon + lon_padding
        final_min_lat = min_lat
        final_max_lat = max_lat
    else:
        # 容器更高，需要增加緯度範圍
        target_lat_span = lon_span / container_aspect
        lat_padding = (target_lat_span - lat_span) / 2
        final_min_lon = min_lon
        final_max_lon = max_lon
        final_min_lat = min_lat - lat_padding
        final_max_lat = max_lat + lat_padding
    
    print(f"\n建議的地圖範圍（填滿容器）:")
    print(f"  minLon: {final_min_lon:.6f}")
    print(f"  maxLon: {final_max_lon:.6f}")
    print(f"  minLat: {final_min_lat:.6f}")
    print(f"  maxLat: {final_max_lat:.6f}")
    print(f"\n中心點:")
    print(f"  centerLon: {(final_min_lon + final_max_lon) / 2:.6f}")
    print(f"  centerLat: {(final_min_lat + final_max_lat) / 2:.6f}")
    
    # 添加一些邊距（5%）
    padding = 0.05
    final_lon_span = final_max_lon - final_min_lon
    final_lat_span = final_max_lat - final_min_lat
    
    final_min_lon_with_padding = final_min_lon - final_lon_span * padding
    final_max_lon_with_padding = final_max_lon + final_lon_span * padding
    final_min_lat_with_padding = final_min_lat - final_lat_span * padding
    final_max_lat_with_padding = final_max_lat + final_lat_span * padding
    
    print(f"\n建議的地圖範圍（含 5% 邊距）:")
    print(f"  minLon: {final_min_lon_with_padding:.6f}")
    print(f"  maxLon: {final_max_lon_with_padding:.6f}")
    print(f"  minLat: {final_min_lat_with_padding:.6f}")
    print(f"  maxLat: {final_max_lat_with_padding:.6f}")
    print(f"\n中心點（含邊距）:")
    print(f"  centerLon: {(final_min_lon_with_padding + final_max_lon_with_padding) / 2:.6f}")
    print(f"  centerLat: {(final_min_lat_with_padding + final_max_lat_with_padding) / 2:.6f}")
    
else:
    print("❌ 無法找到高雄市的座標點")

