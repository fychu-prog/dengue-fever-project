#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
詳細檢查原始資料中台南市的鄉鎮市區（排除「其他」）
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from pathlib import Path

# 設定路徑
DATA_DIR = Path(__file__).parent / "data"
RAW_DATA = DATA_DIR / "raw" / "Dengue_Daily.csv"

print("=" * 60)
print("檢查原始資料中台南市的鄉鎮市區（詳細）")
print("=" * 60)

# 讀取資料
print(f"\n正在讀取資料: {RAW_DATA}")
df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)

print(f"總資料筆數: {len(df)}")

# 過濾台南市資料（處理「台」vs「臺」）
tainan = df[df['居住縣市'].str.contains('台南|臺南', na=False, regex=True)]
print(f"台南市資料筆數: {len(tainan)}")

# 取得所有鄉鎮市區（排除空值和「其他」）
townships = tainan['居住鄉鎮'].dropna()
townships = townships[townships.astype(str).str.strip() != '']
townships = townships[townships.astype(str) != '其他']

unique_townships = sorted(townships.unique())

print(f"\n台南市共有 {len(unique_townships)} 個實際行政區（排除「其他」）：")
print("-" * 60)

for i, township in enumerate(unique_townships, 1):
    # 計算該鄉鎮的病例數
    count = len(tainan[tainan['居住鄉鎮'] == township])
    print(f"{i:2d}. {township:15s} (病例數: {count:,})")

print("-" * 60)
print(f"實際行政區總計: {len(unique_townships)} 個")

# 檢查「其他」類別
other_count = len(tainan[tainan['居住鄉鎮'].astype(str) == '其他'])
if other_count > 0:
    print(f"\n「其他」類別: {other_count} 例")

# 檢查空值
empty_count = len(tainan[tainan['居住鄉鎮'].isna() | (tainan['居住鄉鎮'].astype(str).str.strip() == '')])
if empty_count > 0:
    print(f"空值或未知: {empty_count} 例")

print(f"\n總計（包含「其他」和空值）: {len(tainan)} 例")


