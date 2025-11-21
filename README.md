# 台灣登革熱流行病學監測系統

Taiwan Dengue Fever Epidemiology Surveillance System

## 專案簡介

本專案是一個基於台灣政府開放資料的登革熱流行病學分析與視覺化系統，提供人、時、地三個維度的流行病學分析，並以網頁形式呈現分析結果。

## 資料來源

本專案使用的資料均來自**台灣政府公開的開放資料**，不包含任何個人隱私資訊：

1. **政府資料開放平台 (data.gov.tw)**
   - 網址: https://data.gov.tw/datasets/search?qs=登革熱
   - 提供登革熱病例統計資料

2. **疾病管制署傳染病統計系統**
   - 網址: https://nidss.cdc.gov.tw/nndss/
   - 提供登革熱病例的詳細統計資料

### 資料隱私說明

- ✅ 所有資料均為**已去識別化**的統計資料
- ✅ 資料僅包含：發病日期、性別、年齡層、居住縣市/鄉鎮、是否境外移入等統計資訊
- ✅ **不包含**任何個人識別資訊（如姓名、身分證字號、地址等）
- ✅ 資料來源為政府公開資料，符合開放資料使用規範

## 專案結構

```
dengue_fever_project/
├── data/                    # 資料目錄（不包含在 Git 中）
│   ├── raw/                # 原始資料（需自行下載）
│   └── processed/          # 處理後的資料
├── src/                    # 原始碼
│   ├── download_dengue_data.py    # 資料下載腳本
│   └── analyze_dengue.py          # 資料分析腳本
├── website/                # 網頁應用程式
│   ├── app.py             # Flask 後端
│   ├── templates/         # HTML 模板
│   └── static/            # 靜態資源（CSS, JS）
├── docs/                   # 文件
└── README.md              # 本檔案
```

## 安裝與使用

### 1. 環境需求

- Python 3.7+
- 所需套件：
  ```bash
  pip install flask pandas requests
  ```

### 2. 下載資料

資料檔案（`data/raw/Dengue_Daily.csv`）需要自行下載，因為檔案較大，不包含在 Git 儲存庫中。

**方法一：使用腳本下載**
```bash
python src/download_dengue_data.py
```

**方法二：手動下載**
1. 前往 [政府資料開放平台](https://data.gov.tw/datasets/search?qs=登革熱)
2. 下載登革熱病例資料
3. 將檔案放置到 `data/raw/Dengue_Daily.csv`

詳細說明請參考 `docs/登革熱資料下載說明.md`

### 3. 執行資料分析

```bash
python src/analyze_dengue.py
```

這會產生 `data/processed/dengue_analysis.json` 檔案。

### 4. 啟動網頁應用程式

```bash
python start_website.py
```

或

```bash
cd website
python app.py
```

然後在瀏覽器中開啟 `http://localhost:8080`

## 功能特色

### 時間分析
- 年度趨勢圖
- 季節性模式分析
- 月度分布（按年度）
- 近期趨勢

### 地理分析
- 台灣縣市地圖（Choropleth Map）
- 縣市病例統計表
- 鄉鎮病例統計
- 縣市年度趨勢

### 人群分析
- 性別分布
- 年齡層分布
- 性別年度趨勢
- 境外移入 vs 本土病例分析

### 縣市專頁
- 高雄市專頁
- 台南市專頁

## 技術架構

- **後端**: Flask (Python)
- **前端**: HTML, CSS, JavaScript
- **視覺化**: 
  - Chart.js (統計圖表)
  - Plotly.js (地圖和折線圖)
- **資料處理**: Pandas (Python)

## 授權

本專案使用 MIT 授權。資料來源為台灣政府開放資料，使用時請遵守相關使用規範。

## 免責聲明

1. 本專案僅供學術研究和教育用途
2. 資料來源為政府公開資料，本專案不對資料的準確性負責
3. 分析結果僅供參考，不應作為醫療或公共衛生決策的唯一依據
4. 使用者應自行驗證資料和分析結果

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 聯絡資訊

如有問題或建議，請透過 GitHub Issues 聯繫。

