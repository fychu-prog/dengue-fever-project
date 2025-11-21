"""
登革熱病例基礎流行病學分析
分析人、時、地三個維度
"""

import sys
import io

# 設定 Windows 終端機 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

# 設定路徑
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA = DATA_DIR / "raw" / "Dengue_Daily.csv"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_and_clean_data():
    """載入並清理資料"""
    print("正在載入資料...")
    
    # 讀取資料
    df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)
    
    print(f"原始資料筆數: {len(df)}")
    
    # 清理日期欄位
    df['發病日期'] = pd.to_datetime(df['發病日'], errors='coerce')
    df = df.dropna(subset=['發病日期'])
    
    # 提取時間資訊
    df['發病年'] = df['發病日期'].dt.year
    df['發病月'] = df['發病日期'].dt.month
    df['發病年月'] = df['發病日期'].dt.to_period('M')
    
    # 清理性別資料
    df['性別'] = df['性別'].fillna('未知')
    
    # 清理年齡層資料
    df['年齡層'] = df['年齡層'].fillna('未知')
    
    # 清理地區資料
    df['居住縣市'] = df['居住縣市'].fillna('未知')
    df['居住鄉鎮'] = df['居住鄉鎮'].fillna('未知')
    
    # 清理境外移入資料
    df['是否境外移入'] = df['是否境外移入'].fillna('否')
    
    print(f"清理後資料筆數: {len(df)}")
    print(f"資料時間範圍: {df['發病日期'].min()} 至 {df['發病日期'].max()}")
    
    return df


def analyze_time_trend(df):
    """時間分析：年度、月度趨勢"""
    print("\n=== 時間分析 ===")
    
    # 年度趨勢
    yearly = df.groupby('發病年').size().reset_index(name='病例數')
    yearly['年份'] = yearly['發病年'].astype(str)
    
    # 月度趨勢（所有年份）
    monthly = df.groupby('發病月').size().reset_index(name='病例數')
    monthly['月份'] = monthly['發病月'].astype(str) + '月'
    
    # 年度月度趨勢（熱力圖用）
    yearly_monthly = df.groupby(['發病年', '發病月']).size().reset_index(name='病例數')
    yearly_monthly['年月'] = yearly_monthly['發病年'].astype(str) + '-' + yearly_monthly['發病月'].astype(str).str.zfill(2)
    
    # 最近5年趨勢
    recent_years = df[df['發病年'] >= df['發病年'].max() - 4]
    recent_yearly_monthly = recent_years.groupby(['發病年', '發病月']).size().reset_index(name='病例數')
    recent_yearly_monthly['年月'] = recent_yearly_monthly['發病年'].astype(str) + '-' + recent_yearly_monthly['發病月'].astype(str).str.zfill(2)
    
    return {
        'yearly': yearly.to_dict('records'),
        'monthly': monthly.to_dict('records'),
        'yearly_monthly': yearly_monthly.to_dict('records'),
        'recent_yearly_monthly': recent_yearly_monthly.to_dict('records')
    }


def analyze_location(df):
    """地理分析：縣市、鄉鎮分布"""
    print("\n=== 地理分析 ===")
    
    # 縣市分布
    county = df.groupby('居住縣市').size().reset_index(name='病例數')
    county = county.sort_values('病例數', ascending=False)
    county_top20 = county.head(20)
    
    # 鄉鎮分布（Top 30）
    township = df.groupby(['居住縣市', '居住鄉鎮']).size().reset_index(name='病例數')
    township = township.sort_values('病例數', ascending=False)
    township_top30 = township.head(30)
    
    # 縣市年度趨勢（Top 10 縣市）
    top_counties = county.head(10)['居住縣市'].tolist()
    county_yearly = df[df['居住縣市'].isin(top_counties)].groupby(['居住縣市', '發病年']).size().reset_index(name='病例數')
    
    return {
        'county': county.to_dict('records'),
        'county_top20': county_top20.to_dict('records'),
        'township_top30': township_top30.to_dict('records'),
        'county_yearly': county_yearly.to_dict('records')
    }


def analyze_person(df):
    """人群分析：性別、年齡分布"""
    print("\n=== 人群分析 ===")
    
    # 性別分布
    gender = df.groupby('性別').size().reset_index(name='病例數')
    gender['百分比'] = (gender['病例數'] / gender['病例數'].sum() * 100).round(2)
    
    # 年齡層分布 - 使用固定排序（從小到大）
    age = df.groupby('年齡層').size().reset_index(name='病例數')
    
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
            if age_str == age_range or age_str.startswith(age_range.split('-')[0]):
                return i
        return len(age_order)
    
    age['排序'] = age['年齡層'].apply(get_age_order)
    age = age.sort_values('排序')
    age = age.drop('排序', axis=1)
    age['百分比'] = (age['病例數'] / age['病例數'].sum() * 100).round(2)
    
    # 性別年度趨勢
    gender_yearly = df.groupby(['發病年', '性別']).size().reset_index(name='病例數')
    
    # 年齡層年度趨勢（Top 10 年齡層）
    top_ages = age.head(10)['年齡層'].tolist()
    age_yearly = df[df['年齡層'].isin(top_ages)].groupby(['發病年', '年齡層']).size().reset_index(name='病例數')
    
    # 境外移入分析
    import_status = df.groupby('是否境外移入').size().reset_index(name='病例數')
    import_status['百分比'] = (import_status['病例數'] / import_status['病例數'].sum() * 100).round(2)
    
    # 境外移入年度趨勢
    import_yearly = df.groupby(['發病年', '是否境外移入']).size().reset_index(name='病例數')
    
    return {
        'gender': gender.to_dict('records'),
        'age': age.to_dict('records'),
        'gender_yearly': gender_yearly.to_dict('records'),
        'age_yearly': age_yearly.to_dict('records'),
        'import_status': import_status.to_dict('records'),
        'import_yearly': import_yearly.to_dict('records')
    }


def generate_summary_stats(df):
    """產生摘要統計"""
    print("\n=== 摘要統計 ===")
    
    total_cases = len(df)
    date_range = f"{df['發病日期'].min().strftime('%Y-%m-%d')} 至 {df['發病日期'].max().strftime('%Y-%m-%d')}"
    years_covered = df['發病年'].max() - df['發病年'].min() + 1
    
    top_county = df.groupby('居住縣市').size().idxmax()
    top_county_cases = df.groupby('居住縣市').size().max()
    
    peak_year = df.groupby('發病年').size().idxmax()
    peak_year_cases = df.groupby('發病年').size().max()
    
    local_cases = len(df[df['是否境外移入'] == '否'])
    imported_cases = len(df[df['是否境外移入'] == '是'])
    
    return {
        'total_cases': int(total_cases),
        'date_range': date_range,
        'years_covered': int(years_covered),
        'top_county': top_county,
        'top_county_cases': int(top_county_cases),
        'peak_year': int(peak_year),
        'peak_year_cases': int(peak_year_cases),
        'local_cases': int(local_cases),
        'imported_cases': int(imported_cases),
        'local_percentage': round(local_cases / total_cases * 100, 2),
        'imported_percentage': round(imported_cases / total_cases * 100, 2)
    }


def main():
    """主函數"""
    print("=" * 50)
    print("登革熱病例基礎流行病學分析")
    print("=" * 50)
    
    # 載入資料
    df = load_and_clean_data()
    
    # 執行分析
    time_analysis = analyze_time_trend(df)
    location_analysis = analyze_location(df)
    person_analysis = analyze_person(df)
    summary = generate_summary_stats(df)
    
    # 組合所有分析結果
    results = {
        'summary': summary,
        'time': time_analysis,
        'location': location_analysis,
        'person': person_analysis,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 儲存為 JSON
    output_file = PROCESSED_DIR / "dengue_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析完成！結果已儲存至: {output_file}")
    
    # 顯示摘要
    print("\n" + "=" * 50)
    print("分析摘要")
    print("=" * 50)
    print(f"總病例數: {summary['total_cases']:,}")
    print(f"時間範圍: {summary['date_range']}")
    print(f"涵蓋年數: {summary['years_covered']} 年")
    print(f"最多病例縣市: {summary['top_county']} ({summary['top_county_cases']:,} 例)")
    print(f"疫情高峰年: {summary['peak_year']} 年 ({summary['peak_year_cases']:,} 例)")
    print(f"本土病例: {summary['local_cases']:,} ({summary['local_percentage']}%)")
    print(f"境外移入: {summary['imported_cases']:,} ({summary['imported_percentage']}%)")
    
    return results


if __name__ == "__main__":
    main()

