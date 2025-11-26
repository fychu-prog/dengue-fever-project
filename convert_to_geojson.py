#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
將 GML 或 SHP 格式轉換為 GeoJSON
用於台灣鄉鎮市區界線資料
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("警告: 未安裝 geopandas，無法轉換 SHP/GML 格式")
    print("請執行: pip install geopandas")

# 設定路徑
BASE_DIR = Path(__file__).parent
STATIC_DATA_DIR = BASE_DIR / "website" / "static" / "data"
STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

def convert_shp_to_geojson(shp_path, output_path):
    """將 SHP 格式轉換為 GeoJSON"""
    if not HAS_GEOPANDAS:
        print("❌ 需要安裝 geopandas 才能轉換 SHP 格式")
        print("請執行: pip install geopandas")
        return False
    
    try:
        print(f"正在讀取 SHP 檔案: {shp_path}")
        # 讀取 SHP 檔案（需要完整的 .shp 檔案路徑，但 geopandas 會自動找到相關檔案）
        gdf = gpd.read_file(shp_path, encoding='utf-8')
        
        print(f"找到 {len(gdf)} 個行政區")
        print(f"屬性欄位: {list(gdf.columns)}")
        
        # 轉換為 GeoJSON
        print(f"正在轉換為 GeoJSON: {output_path}")
        gdf.to_file(output_path, driver='GeoJSON', encoding='utf-8')
        
        print(f"✅ 轉換成功！")
        print(f"輸出檔案: {output_path}")
        print(f"檔案大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        return False

def convert_gml_to_geojson(gml_path, output_path):
    """將 GML 格式轉換為 GeoJSON"""
    if not HAS_GEOPANDAS:
        print("❌ 需要安裝 geopandas 才能轉換 GML 格式")
        print("請執行: pip install geopandas")
        return False
    
    try:
        print(f"正在讀取 GML 檔案: {gml_path}")
        # 讀取 GML 檔案
        gdf = gpd.read_file(gml_path, encoding='utf-8')
        
        print(f"找到 {len(gdf)} 個行政區")
        print(f"屬性欄位: {list(gdf.columns)}")
        
        # 轉換為 GeoJSON
        print(f"正在轉換為 GeoJSON: {output_path}")
        gdf.to_file(output_path, driver='GeoJSON', encoding='utf-8')
        
        print(f"✅ 轉換成功！")
        print(f"輸出檔案: {output_path}")
        print(f"檔案大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("台灣鄉鎮市區界線資料格式轉換工具")
    print("=" * 60)
    print()
    
    # 檢查是否有輸入檔案
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python convert_to_geojson.py <輸入檔案路徑>")
        print()
        print("支援的格式:")
        print("  - SHP (Shapefile): .shp")
        print("  - GML: .gml")
        print()
        print("範例:")
        print("  python convert_to_geojson.py TOWN_MOI_1090415.shp")
        print("  python convert_to_geojson.py TOWN_MOI_1090415.gml")
        print()
        print("輸出檔案會自動儲存至: website/static/data/TOWN_MOI_1090415.json")
        return
    
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ 找不到檔案: {input_path}")
        return
    
    output_path = STATIC_DATA_DIR / "TOWN_MOI_1090415.json"
    
    # 根據副檔名選擇轉換函數
    suffix = input_path.suffix.lower()
    
    if suffix == '.shp':
        success = convert_shp_to_geojson(input_path, output_path)
    elif suffix == '.gml':
        success = convert_gml_to_geojson(input_path, output_path)
    elif suffix == '.json' or suffix == '.geojson':
        # 如果已經是 GeoJSON，直接複製
        print(f"檔案已經是 GeoJSON 格式，直接複製...")
        import shutil
        shutil.copy(input_path, output_path)
        print(f"✅ 複製成功！")
        print(f"輸出檔案: {output_path}")
        success = True
    else:
        print(f"❌ 不支援的檔案格式: {suffix}")
        print("支援的格式: .shp, .gml, .json, .geojson")
        success = False
    
    if success:
        print()
        print("=" * 60)
        print("✅ 轉換完成！")
        print("=" * 60)
        print(f"檔案已儲存至: {output_path}")
        print("請重新整理網頁以查看地圖")
    else:
        print()
        print("=" * 60)
        print("❌ 轉換失敗")
        print("=" * 60)

if __name__ == "__main__":
    main()

