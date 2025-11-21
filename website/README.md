# 台灣登革熱流行病學監測系統

## 功能說明

本系統提供台灣登革熱病例的基礎流行病學分析，包含：

1. **時間分析**：年度趨勢、月度分布、季節性模式
2. **地理分析**：縣市分布、鄉鎮分布、地理趨勢
3. **人群分析**：性別分布、年齡層分布、境外移入分析

## 使用步驟

### 1. 執行資料分析

首先需要執行分析腳本產生資料：

```bash
python src/analyze_dengue.py
```

這會產生 `data/processed/dengue_analysis.json` 檔案。

### 2. 啟動網頁伺服器

```bash
cd website
python app.py
```

或從專案根目錄：

```bash
python website/app.py
```

### 3. 開啟瀏覽器

在瀏覽器中開啟：http://localhost:8080

## 系統需求

- Python 3.7+
- Flask
- pandas
- Chart.js (透過 CDN 載入)

## 安裝依賴

```bash
pip install flask pandas
```

## 資料來源

- 疾病管制署登革熱病例資料
- 資料時間範圍：1998-2025

## 技術架構

- **後端**：Flask (Python)
- **前端**：HTML5, CSS3, JavaScript
- **圖表**：Chart.js
- **資料格式**：JSON

## 參考設計

本系統參考 WHO (世界衛生組織) 的疾病監測網站設計風格，提供：
- 清晰的資料視覺化
- 專業的流行病學分析
- 易於使用的介面

