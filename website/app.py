"""
登革熱流行病學分析網頁應用程式
參考 WHO 網站設計風格
"""

import sys
import io

# 設定 Windows 終端機 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, jsonify, send_from_directory
import json
import pandas as pd
from pathlib import Path

# 取得當前檔案所在目錄
BASE_DIR = Path(__file__).parent

app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'),
            static_url_path='/static')

# 設定 CORS（如果需要）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 設定資料路徑
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA = DATA_DIR / "raw" / "Dengue_Daily.csv"
ANALYSIS_FILE = DATA_DIR / "processed" / "dengue_analysis.json"
STATIC_DATA_DIR = Path(__file__).parent / "static" / "data"
STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


@app.route('/test')
def test():
    """測試頁面"""
    return render_template('test.html')


@app.route('/kaohsiung')
def kaohsiung():
    """高雄市專頁"""
    return render_template('kaohsiung.html')


@app.route('/tainan')
def tainan():
    """台南市專頁"""
    return render_template('tainan.html')


@app.route('/api/data')
def get_data():
    """取得分析資料 API"""
    try:
        if not ANALYSIS_FILE.exists():
            return jsonify({'error': '分析資料不存在，請先執行分析腳本'}), 404
        
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 檢查資料結構
        if not isinstance(data, dict):
            return jsonify({'error': '資料格式錯誤'}), 500
        
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': '分析資料不存在，請先執行分析腳本'}), 404
    except json.JSONDecodeError as e:
        return jsonify({'error': f'JSON 解析錯誤: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary')
def get_summary():
    """取得摘要統計 API"""
    try:
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data.get('summary', {}))
    except FileNotFoundError:
        return jsonify({'error': '分析資料不存在'}), 404


@app.route('/api/data/<county>')
def get_county_data(county):
    """取得特定縣市的資料 API"""
    try:
        if not ANALYSIS_FILE.exists():
            return jsonify({'error': '分析資料不存在，請先執行分析腳本'}), 404
        
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 縣市名稱對應（處理可能的命名差異）
        county_mapping = {
            'kaohsiung': '高雄市',
            'tainan': '台南市',
            '臺南市': '台南市',
            '臺北市': '台北市'
        }
        
        county_name = county_mapping.get(county, county)
        
        # 確保使用正確的縣市名稱（處理「臺」vs「台」的差異）
        # 先嘗試原始名稱，如果找不到再嘗試變體
        print(f"請求的縣市: {county} -> 對應名稱: {county_name}")
        
        # 過濾該縣市的資料
        filtered_data = filter_data_by_county(data, county_name)
        
        return jsonify(filtered_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def filter_data_by_county(data, county_name):
    """過濾特定縣市的資料"""
    filtered = {
        'summary': {},
        'time': {},
        'location': {},
        'person': {},
        'last_updated': data.get('last_updated', '')
    }
    
    # 過濾縣市相關資料
    county_data = []
    township_data = []
    matching_county_name = county_name  # 預設使用原始名稱
    
    if 'location' in data:
        # 嘗試多種可能的縣市名稱匹配（處理「臺」vs「台」的差異）
        possible_county_names = [
            county_name,
            county_name.replace('台', '臺'),
            county_name.replace('臺', '台')
        ]
        
        # 找出資料中實際存在的匹配名稱
        all_counties = [item.get('居住縣市') for item in data['location'].get('county', [])]
        matching_county_name = None
        for name in possible_county_names:
            if name in all_counties:
                matching_county_name = name
                print(f"找到匹配的縣市名稱: {name} (原始請求: {county_name})")
                break
        
        if not matching_county_name:
            print(f"警告: 無法找到完全匹配的縣市名稱，使用原始名稱: {county_name}")
            print(f"資料中可用的縣市: {sorted(set(all_counties))[:10]}")
            matching_county_name = county_name
        
        # 縣市統計（只保留該縣市）
        county_data = [item for item in data['location'].get('county', []) 
                      if item.get('居住縣市') == matching_county_name]
        filtered['location']['county'] = county_data
        print(f"過濾縣市資料: 找到 {len(county_data)} 筆縣市記錄")
        
        # 鄉鎮統計（只保留該縣市的鄉鎮）
        township_data = [item for item in data['location'].get('township_top30', [])
                        if item.get('居住縣市') == matching_county_name]
        filtered['location']['township'] = township_data
        filtered['location']['township_top30'] = township_data
        print(f"過濾鄉鎮資料: 找到 {len(township_data)} 筆鄉鎮記錄")
        
        # 縣市年度趨勢（只保留該縣市）
        county_yearly = [item for item in data['location'].get('county_yearly', [])
                        if item.get('居住縣市') == matching_county_name]
        filtered['location']['county_yearly'] = county_yearly
        print(f"過濾年度趨勢資料: 找到 {len(county_yearly)} 筆年度記錄")
    
    # 時間資料保持不變（因為是整體趨勢）
    if 'time' in data:
        filtered['time'] = data['time']
    
    # 從原始資料計算該縣市的性別和年齡分布
    try:
        if RAW_DATA.exists():
            df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
            
            # 清理資料
            df['居住縣市'] = df['居住縣市'].fillna('未知')
            df['性別'] = df['性別'].fillna('未知')
            df['年齡層'] = df['年齡層'].fillna('未知')
            
            # 處理縣市名稱差異（臺 vs 台）
            # 檢查資料中實際使用的縣市名稱
            unique_counties = df['居住縣市'].unique()
            print(f"資料中所有縣市名稱: {sorted([c for c in unique_counties if pd.notna(c)])[:20]}")
            
            # 嘗試多種可能的縣市名稱匹配
            possible_names = [
                county_name,
                county_name.replace('台', '臺'),
                county_name.replace('臺', '台')
            ]
            
            # 找出資料中實際存在的匹配名稱
            matching_names = [name for name in possible_names if name in unique_counties]
            
            if matching_names:
                print(f"找到匹配的縣市名稱: {matching_names}")
                # 使用第一個匹配的名稱
                actual_county_name = matching_names[0]
                county_df = df[df['居住縣市'] == actual_county_name]
                print(f"過濾 {actual_county_name} 的資料，找到 {len(county_df)} 筆記錄")
                
                # 驗證資料：顯示性別分布
                if len(county_df) > 0:
                    gender_check = county_df.groupby('性別').size()
                    print(f"{actual_county_name} 性別分布: {gender_check.to_dict()}")
            else:
                # 如果完全匹配失敗，嘗試部分匹配
                print(f"警告: 無法找到完全匹配的縣市名稱，嘗試部分匹配...")
                county_df = df[df['居住縣市'].str.contains(county_name.replace('台', '臺').replace('臺', '台'), na=False)]
                if len(county_df) > 0:
                    print(f"部分匹配成功，找到 {len(county_df)} 筆記錄")
                    print(f"實際縣市名稱: {county_df['居住縣市'].unique()[:5]}")
                else:
                    print(f"錯誤: 無法找到 {county_name} 的資料")
                    county_df = pd.DataFrame()  # 空資料框
            
            if len(county_df) > 0:
                # 計算該縣市的性別分布
                gender = county_df.groupby('性別').size().reset_index(name='病例數')
                gender['百分比'] = (gender['病例數'] / gender['病例數'].sum() * 100).round(2)
                filtered['person']['gender'] = gender.to_dict('records')
                
                # 計算該縣市的年齡層分布
                age = county_df.groupby('年齡層').size().reset_index(name='病例數')
                age['百分比'] = (age['病例數'] / age['病例數'].sum() * 100).round(2)
                
                # 定義年齡層的固定排序順序
                age_order = [
                    '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', 
                    '30-34', '35-39', '40-44', '45-49', '50-54', '55-59',
                    '60-64', '65-69', '70-74', '75-79', '80-84', '85+', '未知'
                ]
                
                # 建立排序映射
                def get_age_order(age_str):
                    if pd.isna(age_str) or age_str == '未知':
                        return len(age_order)
                    for i, age_range in enumerate(age_order):
                        if str(age_str) == age_range or str(age_str).startswith(age_range.split('-')[0]):
                            return i
                    return len(age_order)
                
                age['排序'] = age['年齡層'].apply(get_age_order)
                age = age.sort_values('排序')
                age = age.drop('排序', axis=1)
                filtered['person']['age'] = age.to_dict('records')
            else:
                # 如果沒有找到該縣市的資料，使用空資料
                filtered['person']['gender'] = []
                filtered['person']['age'] = []
        else:
            # 如果原始資料不存在，使用整體資料
            if 'person' in data:
                filtered['person'] = data['person']
    except Exception as e:
        print(f"計算縣市性別年齡分布時發生錯誤: {e}")
        # 發生錯誤時，使用整體資料
        if 'person' in data:
            filtered['person'] = data['person']
    
    # 計算該縣市的摘要統計
    # 使用匹配到的縣市名稱
    final_county_name = matching_county_name
    
    if county_data:
        total_cases = sum(item.get('病例數', 0) for item in county_data)
        filtered['summary'] = {
            '總病例數': total_cases,
            '縣市': final_county_name,
            '鄉鎮數': len(township_data) if township_data else 0
        }
        print(f"摘要統計: {final_county_name}, 總病例數: {total_cases}, 鄉鎮數: {len(township_data) if township_data else 0}")
    elif township_data:
        # 如果沒有找到縣市數據，嘗試從鄉鎮數據計算
        total_cases = sum(item.get('病例數', 0) for item in township_data)
        filtered['summary'] = {
            '總病例數': total_cases,
            '縣市': final_county_name,
            '鄉鎮數': len(township_data)
        }
        print(f"摘要統計（從鄉鎮計算）: {final_county_name}, 總病例數: {total_cases}, 鄉鎮數: {len(township_data)}")
    else:
        # 如果完全沒有資料，設置空摘要
        filtered['summary'] = {
            '總病例數': 0,
            '縣市': final_county_name,
            '鄉鎮數': 0
        }
        print(f"警告: 無法找到 {final_county_name} 的任何資料")
    
    return filtered


@app.route('/static/data/<path:filename>')
def serve_static_data(filename):
    """提供靜態資料檔案（如 GeoJSON）"""
    return send_from_directory(STATIC_DATA_DIR, filename)


@app.route('/favicon.ico')
def favicon():
    """處理 favicon 請求，避免 404 錯誤"""
    return '', 204  # No Content


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
