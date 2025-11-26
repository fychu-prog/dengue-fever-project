# 地圖資料說明

## 台灣鄉鎮市區界線 GeoJSON

本專案使用**政府開放資料**的台灣鄉鎮市區界線資料（共 368 個行政區）。

### 推薦資料來源

**政府資料開放平台**（最推薦）：
- 網址：https://data.gov.tw/dataset/7442
- 檔案：`TOWN_MOI_1090415.json`（鄉鎮市區界線）
- 格式：GeoJSON
- 包含：全台 368 個鄉鎮市區的行政區界線

### 下載方式

#### 方式一：使用 Python 腳本自動下載（推薦）

```bash
python download_geojson.py
```

腳本會自動嘗試從多個來源下載 GeoJSON 檔案。

#### 方式二：手動下載

1. 前往 https://data.gov.tw/dataset/7442
2. 下載「TOWN_MOI_1090415.json」檔案
3. 將檔案放置於此目錄：`website/static/data/TOWN_MOI_1090415.json`

### 檔案命名

- **全台鄉鎮市區**：`TOWN_MOI_1090415.json`
- **縣市專用**（可選）：`kaohsiung_districts.geojson`、`tainan_districts.geojson`

### 自動載入

系統會自動嘗試從以下來源載入地圖（按優先順序）：
1. 政府開放資料（GitHub 備份）
2. GitHub 其他來源
3. 本地檔案（`./static/data/TOWN_MOI_1090415.json`）

如果所有來源都無法載入，會顯示提示訊息。
