#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查原始資料中台南市的鄉鎮市區
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
print("檢查台南市鄉鎮市區")
print("=" * 60)

# 讀取資料
print(f"\n正在讀取資料: {RAW_DATA}")
df = pd.read_csv(RAW_DATA, encoding='utf-8-sig', low_memory=False)

print(f"總資料筆數: {len(df)}")

# 過濾台南市資料（處理「台」vs「臺」）
tainan = df[df['居住縣市'].str.contains('台南|臺南', na=False, regex=True)]
print(f"\n台南市資料筆數: {len(tainan)}")

# 取得所有鄉鎮市區
townships = tainan['居住鄉鎮'].dropna().unique()
townships = sorted([str(t) for t in townships if pd.notna(t) and str(t).strip() != ''])

print(f"\n台南市共有 {len(townships)} 個鄉鎮市區：")
print("-" * 60)

for i, township in enumerate(townships, 1):
    # 計算該鄉鎮的病例數
    count = len(tainan[tainan['居住鄉鎮'] == township])
    print(f"{i:2d}. {township:15s} (病例數: {count:,})")

print("-" * 60)
print(f"總計: {len(townships)} 個鄉鎮市區")

# 檢查是否有「未知」或其他特殊值
unknown = tainan[tainan['居住鄉鎮'].isna() | (tainan['居住鄉鎮'].astype(str).str.strip() == '')]
if len(unknown) > 0:
    print(f"\n注意: 有 {len(unknown)} 筆資料的鄉鎮欄位為空值或未知")


