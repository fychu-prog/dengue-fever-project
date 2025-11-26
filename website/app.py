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


def generate_complete_township_data(county_name, existing_township_data):
    """生成完整的行政區列表（包含所有行政區，即使病例數為 0）"""
    try:
        # 從 GeoJSON 中讀取該縣市的所有行政區
        geojson_file = STATIC_DATA_DIR / "taiwan_township.geojson"
        if not geojson_file.exists():
            print(f"警告: GeoJSON 檔案不存在，使用現有資料")
            return existing_township_data
        
        with open(geojson_file, 'r', encoding='utf-8') as f:
            geo = json.load(f)
        
        # 提取該縣市的所有行政區名稱
        all_townships = set()
        county_variants = [
            county_name,
            county_name.replace('台', '臺'),
            county_name.replace('臺', '台')
        ]
        
        for feature in geo['features']:
            props = feature['properties']
            feature_county = props.get('COUNTYNAME', '')
            feature_township = props.get('TOWNNAME', '')
            
            if feature_township and any(variant in feature_county for variant in county_variants):
                all_townships.add(feature_township)
        
        print(f"從 GeoJSON 中找到 {county_name} 的 {len(all_townships)} 個行政區")
        
        # 建立現有資料的病例數對應表
        existing_cases = {}
        for item in existing_township_data:
            township = item.get('居住鄉鎮', '')
            if township:
                existing_cases[township] = item.get('病例數', 0)
        
        # 如果原始資料存在，從中讀取更完整的病例數
        if RAW_DATA.exists():
            df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
            
            # 找出匹配的縣市名稱
            matching_county = None
            for variant in county_variants:
                matching = df[df['居住縣市'] == variant]
                if len(matching) > 0:
                    matching_county = variant
                    break
            
            if matching_county:
                county_df = df[df['居住縣市'] == matching_county].copy()
                township_counts = county_df.groupby('居住鄉鎮').size().reset_index(name='病例數')
                
                for _, row in township_counts.iterrows():
                    township = row['居住鄉鎮']
                    cases = int(row['病例數'])
                    if pd.notna(township) and township != '未知' and township != '其他':
                        existing_cases[township] = cases
        
        # 生成完整列表
        complete_list = []
        for township in sorted(all_townships):
            complete_list.append({
                '居住縣市': county_name,
                '居住鄉鎮': township,
                '病例數': existing_cases.get(township, 0)
            })
        
        # 按病例數排序（降序）
        complete_list.sort(key=lambda x: x['病例數'], reverse=True)
        
        return complete_list
    except Exception as e:
        print(f"生成完整行政區列表時發生錯誤: {e}")
        # 發生錯誤時，返回現有資料
        return existing_township_data


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
        
        # 生成完整的行政區列表（包含所有行政區，即使病例數為 0）
        # 這對於地圖顯示很重要，因為地圖需要顯示所有行政區
        complete_township_data = generate_complete_township_data(matching_county_name, township_data)
        filtered['location']['township'] = complete_township_data
        filtered['location']['township_top30'] = township_data  # 保留 top30 用於其他用途
        print(f"過濾鄉鎮資料: 找到 {len(township_data)} 筆 top30 記錄，完整列表 {len(complete_township_data)} 筆")
        
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
            # 年齡層先不 fillna，讓 normalize_age_group 處理
            
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
            
            actual_county_name = None
            if matching_names:
                print(f"找到匹配的縣市名稱: {matching_names}")
                # 使用第一個匹配的名稱
                actual_county_name = matching_names[0]
            else:
                # 如果完全匹配失敗，嘗試部分匹配
                print(f"警告: 無法找到完全匹配的縣市名稱，嘗試部分匹配...")
                for name in possible_names:
                    matching = df[df['居住縣市'].str.contains(name, na=False, regex=False)]
                    if len(matching) > 0:
                        actual_county_name = matching['居住縣市'].iloc[0]
                        print(f"部分匹配成功，找到 {len(matching)} 筆記錄，實際縣市名稱: {actual_county_name}")
                        break
                
                if not actual_county_name:
                    print(f"錯誤: 無法找到 {county_name} 的資料")
                    print(f"資料中可用的縣市: {sorted([c for c in unique_counties if pd.notna(c)])[:20]}")
            
            if actual_county_name:
                county_df = df[df['居住縣市'] == actual_county_name].copy()
                print(f"過濾 {actual_county_name} 的資料，找到 {len(county_df)} 筆記錄")
                
                if len(county_df) > 0:
                    # 驗證資料：顯示性別分布
                    gender_check = county_df.groupby('性別').size()
                    print(f"{actual_county_name} 性別分布: {gender_check.to_dict()}")
                    
                    # 計算該縣市的性別分布
                    gender = county_df.groupby('性別').size().reset_index(name='病例數')
                    gender['百分比'] = (gender['病例數'] / gender['病例數'].sum() * 100).round(2)
                    filtered['person']['gender'] = gender.to_dict('records')
                    print(f"{actual_county_name} 性別資料: {filtered['person']['gender']}")
                    
                    # 計算該縣市的年齡層分布（與 analyze_dengue.py 保持一致）
                    # 先處理特殊情況：將單獨的數字（0, 1, 2, 3, 4）合併到 '0-4'
                    county_df_age = county_df.copy()
                    # 確保年齡層欄位是字串類型，並處理 NaN
                    county_df_age['年齡層'] = county_df_age['年齡層'].fillna('未知').astype(str)
                    # 將 'nan', 'NaN', 'None', '' 轉換為 '未知'
                    county_df_age.loc[county_df_age['年齡層'].isin(['nan', 'NaN', 'None', '']), '年齡層'] = '未知'
                    # 將單獨的數字年齡（0-4）合併到 '0-4' 年齡層
                    single_digit_ages = ['0', '1', '2', '3', '4']
                    for single_age in single_digit_ages:
                        county_df_age.loc[county_df_age['年齡層'] == single_age, '年齡層'] = '0-4'
                    
                    # 將所有 70 歲以上的年齡層轉換為 '70+'
                    # 處理 '70+', '70-74', '75-79', '80-84', '85+' 等格式
                    def normalize_age_group(age_str):
                        if pd.isna(age_str) or str(age_str).strip() in ['未知', 'nan', 'NaN', 'None', '']:
                            return '未知'
                        age_str = str(age_str).strip()
                        # 如果已經是 '70+'，直接返回
                        if age_str == '70+':
                            return '70+'
                        # 如果以 '70' 開頭（如 '70-74'），轉換為 '70+'
                        if age_str.startswith('70'):
                            return '70+'
                        # 如果包含 '-'，檢查起始年齡
                        if '-' in age_str:
                            try:
                                start_age = int(age_str.split('-')[0])
                                if start_age >= 70:
                                    return '70+'
                            except:
                                pass
                        # 如果以數字開頭且 >= 70（如 '75', '80' 等），轉換為 '70+'
                        try:
                            if age_str.isdigit() and int(age_str) >= 70:
                                return '70+'
                        except:
                            pass
                        return age_str
                    
                    county_df_age['年齡層'] = county_df_age['年齡層'].apply(normalize_age_group)
                    
                    age = county_df_age.groupby('年齡層').size().reset_index(name='病例數')
                    age['百分比'] = (age['病例數'] / age['病例數'].sum() * 100).round(2)
                    
                    # 定義年齡層的固定排序順序（與 analyze_dengue.py 保持一致）
                    age_order = [
                        '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', 
                        '30-34', '35-39', '40-44', '45-49', '50-54', '55-59',
                        '60-64', '65-69', '70+',  # 原始資料使用 '70+' 表示所有70歲以上
                        '未知'
                    ]
                    
                    # 建立排序映射（與 analyze_dengue.py 保持一致）
                    def get_age_order(age_str):
                        if pd.isna(age_str) or str(age_str).strip() in ['未知', 'nan', 'NaN', 'None', '']:
                            return len(age_order)
                        age_str = str(age_str).strip()
                        # 先嘗試完全匹配
                        if age_str in age_order:
                            return age_order.index(age_str)
                        # 如果不在列表中，放在最後
                        return len(age_order)
                    
                    age['排序'] = age['年齡層'].apply(get_age_order)
                    age = age.sort_values('排序')
                    age = age.drop('排序', axis=1)
                    filtered['person']['age'] = age.to_dict('records')
                    print(f"{actual_county_name} 年齡層資料筆數: {len(filtered['person']['age'])}")
                    print(f"{actual_county_name} 年齡層: {[item['年齡層'] for item in filtered['person']['age'][:5]]}")
                    # 特別檢查 70+ 的資料
                    age_70 = [item for item in filtered['person']['age'] if item['年齡層'] == '70+']
                    if age_70:
                        print(f"{actual_county_name} 70+ 病例數: {age_70[0]['病例數']}, 百分比: {age_70[0]['百分比']}%")
                    else:
                        print(f"警告: {actual_county_name} 沒有找到 70+ 的資料！")
                        print(f"所有年齡層: {[item['年齡層'] for item in filtered['person']['age']]}")
                else:
                    # 如果沒有找到該縣市的資料，使用空資料
                    print(f"警告: {actual_county_name} 沒有資料")
                    filtered['person']['gender'] = []
                    filtered['person']['age'] = []
            else:
                # 如果無法匹配縣市名稱，使用空資料
                print(f"錯誤: 無法匹配縣市名稱 {county_name}，使用空資料")
                filtered['person']['gender'] = []
                filtered['person']['age'] = []
        else:
            # 如果原始資料不存在，使用空資料（不應該使用整體資料）
            print(f"警告: 原始資料檔案不存在，無法計算縣市特定的人群分析資料")
            filtered['person']['gender'] = []
            filtered['person']['age'] = []
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
