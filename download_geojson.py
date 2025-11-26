#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
下載台灣鄉鎮市區界線 GeoJSON 檔案（政府開放資料）
來源：https://data.gov.tw/dataset/7442
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
from pathlib import Path

# 設定路徑
BASE_DIR = Path(__file__).parent
STATIC_DATA_DIR = BASE_DIR / "website" / "static" / "data"
STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 政府開放資料的 URL（可能需要根據實際情況調整）
GEOJSON_URLS = [
    # 政府開放資料平台（可能需要直接下載連結）
    'https://data.gov.tw/dataset/7442/resource/1a1c4e4b-1b0a-4e0a-9e0a-1b0a4e0a9e0a',
    # GitHub 備用來源
    'https://raw.githubusercontent.com/kiang/taiwan.idv.tw/master/data/town/TOWN_MOI_1090415.json',
    # 其他可能的來源
    'https://raw.githubusercontent.com/g0v/twgeojson/master/json/town/TOWN_MOI_1090415.json',
]

def download_geojson():
    """下載台灣鄉鎮市區界線 GeoJSON 檔案"""
    output_file = STATIC_DATA_DIR / "TOWN_MOI_1090415.json"
    
    print("正在下載台灣鄉鎮市區界線 GeoJSON 檔案...")
    print(f"目標檔案: {output_file}")
    
    for url in GEOJSON_URLS:
        try:
            print(f"\n嘗試從以下網址下載: {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # 檢查是否為有效的 JSON
                try:
                    data = response.json()
                    if 'features' in data or 'type' in data:
                        # 儲存檔案
                        output_file.write_text(response.text, encoding='utf-8')
                        print(f"✅ 下載成功！")
                        print(f"檔案已儲存至: {output_file}")
                        print(f"檔案大小: {len(response.content) / 1024 / 1024:.2f} MB")
                        
                        # 顯示一些統計資訊
                        if 'features' in data:
                            print(f"包含 {len(data['features'])} 個行政區")
                            if len(data['features']) > 0:
                                print(f"第一個行政區的屬性: {list(data['features'][0].get('properties', {}).keys())}")
                        
                        return True
                    else:
                        print("⚠️  回應不是有效的 GeoJSON 格式")
                except ValueError as e:
                    print(f"⚠️  JSON 解析失敗: {e}")
            else:
                print(f"⚠️  HTTP 狀態碼: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  下載失敗: {e}")
            continue
    
    print("\n❌ 所有下載來源都失敗了")
    print("\n請手動下載：")
    print("1. 前往 https://data.gov.tw/dataset/7442")
    print("2. 下載「TOWN_MOI_1090415.json」檔案")
    print(f"3. 將檔案放置於: {STATIC_DATA_DIR}")
    return False

if __name__ == "__main__":
    success = download_geojson()
    sys.exit(0 if success else 1)

