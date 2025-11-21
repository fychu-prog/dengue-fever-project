"""
台灣登革熱病例開放資料下載工具
從政府資料開放平台和疾病管制署下載登革熱病例資料
"""

import sys
import io

# 設定 Windows 終端機 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time

# 設定資料儲存路徑
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_from_data_gov_tw():
    """
    從政府資料開放平台 (data.gov.tw) 下載登革熱資料
    """
    print("正在從政府資料開放平台搜尋登革熱資料...")
    
    # 嘗試多種 API 端點
    api_endpoints = [
        "https://data.gov.tw/api/front/dataset/list",
        "https://data.gov.tw/api/v1/rest/dataset",
    ]
    
    datasets = []
    
    for search_url in api_endpoints:
        try:
            params = {
                "q": "登革熱",
                "page": 1,
                "pageSize": 20
            }
            
            response = requests.get(search_url, params=params, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        datasets = data.get('data', [])
                    elif isinstance(data, list):
                        datasets = data
                    
                    if datasets:
                        print(f"[成功] 找到 {len(datasets)} 個相關資料集")
                        break
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            continue
    
    if not datasets:
        print("[警告] API 搜尋失敗，請使用網頁介面手動下載")
        print("   網址: https://data.gov.tw/datasets/search?qs=登革熱")
        return []
    
    # 顯示找到的資料集
    for i, dataset in enumerate(datasets[:10], 1):  # 只顯示前10個
        print(f"\n{i}. {dataset.get('title', 'N/A')}")
        if 'description' in dataset:
            desc = str(dataset.get('description', ''))[:100]
            print(f"   描述: {desc}...")
        if 'id' in dataset:
            print(f"   資料集ID: {dataset.get('id')}")
        
        # 嘗試下載資料
        if 'resources' in dataset:
            for resource in dataset['resources']:
                if resource.get('format') in ['CSV', 'JSON', 'XLS', 'XLSX']:
                    print(f"   資源: {resource.get('name', 'N/A')} ({resource.get('format')})")
                    download_url = resource.get('downloadUrl') or resource.get('url')
                    if download_url:
                        print(f"   下載連結: {download_url}")
    
    return datasets


def download_from_cdc_api():
    """
    從疾病管制署 API 下載登革熱資料
    注意：需要確認實際的 API 端點
    """
    print("\n正在嘗試從疾病管制署下載資料...")
    
    # 疾病管制署傳染病統計資料查詢系統
    # 注意：實際的 API 端點可能需要進一步確認
    cdc_urls = [
        "https://nidss.cdc.gov.tw/nndss/DiseaseMap?id=061",  # 登革熱疾病代碼
    ]
    
    print("提示：疾病管制署的資料可能需要透過網頁介面下載")
    print("網址: https://nidss.cdc.gov.tw/nndss/DiseaseMap?id=061")
    
    return None


def download_from_url(url, filename=None):
    """
    從指定 URL 下載檔案
    """
    try:
        print(f"正在下載: {url}")
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # 判斷檔案格式
        if filename is None:
            # 從 URL 或 Content-Type 判斷
            if 'csv' in url.lower() or response.headers.get('Content-Type', '').startswith('text/csv'):
                filename = f"dengue_data_{datetime.now().strftime('%Y%m%d')}.csv"
            elif 'xls' in url.lower() or 'excel' in response.headers.get('Content-Type', '').lower():
                filename = f"dengue_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
            elif 'json' in url.lower() or response.headers.get('Content-Type', '').startswith('application/json'):
                filename = f"dengue_data_{datetime.now().strftime('%Y%m%d')}.json"
            else:
                filename = f"dengue_data_{datetime.now().strftime('%Y%m%d')}.csv"
        
        filepath = DATA_DIR / filename
        
        # 儲存檔案
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"[成功] 已儲存至: {filepath}")
        
        # 如果是 CSV，嘗試讀取並顯示資訊
        if filepath.suffix.lower() == '.csv':
            try:
                df = pd.read_csv(filepath, encoding='utf-8-sig')
                print(f"[成功] 資料筆數: {len(df)}")
                print(f"[成功] 欄位數: {len(df.columns)}")
                print(f"[成功] 前5個欄位: {', '.join(df.columns.tolist()[:5])}")
            except Exception as e:
                print(f"[警告] 無法讀取 CSV 檔案: {e}")
        
        return filepath
    
    except Exception as e:
        print(f"[錯誤] 下載失敗: {e}")
        return None


def download_dengue_daily_data():
    """
    下載登革熱每日病例資料
    從政府資料開放平台下載最新的登革熱病例資料
    """
    print("\n=== 台灣登革熱病例資料下載工具 ===\n")
    
    # 方法1: 從政府資料開放平台搜尋
    datasets = download_from_data_gov_tw()
    
    if datasets:
        print("\n請選擇要下載的資料集編號（或按 Enter 跳過）:")
        try:
            choice = input().strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(datasets):
                dataset = datasets[int(choice) - 1]
                print(f"\n正在下載: {dataset.get('title')}")
                
                # 嘗試下載資源
                if 'resources' in dataset:
                    for resource in dataset['resources']:
                        download_url = resource.get('downloadUrl') or resource.get('url')
                        if download_url:
                            download_from_url(download_url)
        except EOFError:
            print("\n非互動模式，跳過選擇步驟")
    
    # 方法2: 提供手動下載指引
    print("\n=== 手動下載指引 ===")
    print("1. 政府資料開放平台: https://data.gov.tw/datasets/search?qs=登革熱")
    print("2. 疾病管制署傳染病統計: https://nidss.cdc.gov.tw/nndss/DiseaseMap?id=061")
    print("3. 傳染病統計資料查詢系統: https://nidss.cdc.gov.tw/nndss/")
    print("\n提示：您也可以直接提供下載連結，使用 download_from_url() 函數下載")
    
    return None


def get_dengue_data_info():
    """
    取得登革熱資料的相關資訊和連結
    """
    info = {
        "政府資料開放平台": {
            "網址": "https://data.gov.tw/datasets/search?qs=登革熱",
            "說明": "可搜尋和下載登革熱相關的開放資料集"
        },
        "疾病管制署傳染病統計": {
            "網址": "https://nidss.cdc.gov.tw/nndss/DiseaseMap?id=061",
            "說明": "提供登革熱的流行趨勢圖、統計報表和地理分布"
        },
        "傳染病統計資料查詢系統": {
            "網址": "https://nidss.cdc.gov.tw/nndss/",
            "說明": "可查詢和下載多種傳染病的統計資料，包括登革熱"
        }
    }
    
    print("\n=== 台灣登革熱開放資料來源 ===\n")
    for source, details in info.items():
        print(f"{source}:")
        print(f"  網址: {details['網址']}")
        print(f"  說明: {details['說明']}\n")
    
    return info


if __name__ == "__main__":
    import sys
    
    # 顯示資料來源資訊
    get_dengue_data_info()
    
    # 檢查是否有命令列參數
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自動模式：直接嘗試下載
        print("\n自動模式：正在搜尋和下載資料...")
        download_dengue_daily_data()
    else:
        # 互動模式
        try:
            print("\n是否要嘗試自動下載資料？(y/n): ", end="")
            choice = input().strip().lower()
            
            if choice == 'y':
                download_dengue_daily_data()
            else:
                print("\n您可以使用上述連結手動下載資料。")
                print("提示：使用 'python src/download_dengue_data.py --auto' 可跳過互動")
        except EOFError:
            print("\n非互動模式：使用 'python src/download_dengue_data.py --auto' 可自動下載")
            print("或直接使用上述連結手動下載資料。")

