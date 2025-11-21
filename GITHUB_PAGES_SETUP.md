# GitHub Pages 設定指南

## 重要說明

本專案是 **Flask 應用程式**，需要後端 API 來提供資料。GitHub Pages 只能託管**靜態網站**，無法運行 Flask 後端。

## 解決方案

### 方案一：使用靜態資料檔案（推薦）

將資料檔案轉換為靜態 JSON，讓前端直接讀取：

1. **確保資料檔案存在**
   ```bash
   # 如果還沒有資料，先執行分析
   python src/analyze_dengue.py
   ```

2. **複製資料檔案到靜態目錄**
   ```bash
   # 建立 docs 目錄（GitHub Pages 使用）
   mkdir -p docs/static/data
   
   # 複製資料檔案
   cp data/processed/dengue_analysis.json docs/static/data/
   
   # 複製網站檔案
   cp -r website/static docs/
   cp website/templates/*.html docs/
   ```

3. **修改 HTML 檔案中的 API 路徑**
   - 將 `/api/data` 改為 `static/data/dengue_analysis.json`
   - 將 `/api/data/kaohsiung` 改為使用 JavaScript 過濾資料

4. **在 GitHub 設定 Pages**
   - 前往儲存庫的 Settings > Pages
   - Source 選擇 "Deploy from a branch"
   - Branch 選擇 `main`，資料夾選擇 `/docs`
   - 點擊 Save

5. **訪問網站**
   - 網址格式：`https://YOUR_USERNAME.github.io/REPO_NAME/`
   - 例如：`https://username.github.io/dengue-fever-project/`

### 方案二：使用 GitHub Actions 自動部署

已建立 `.github/workflows/deploy-pages.yml`，會自動：
- 在每次推送到 main 分支時建立靜態版本
- 部署到 GitHub Pages

**啟用步驟：**
1. 確保 `.github/workflows/deploy-pages.yml` 已提交
2. 前往儲存庫的 Settings > Pages
3. Source 選擇 "GitHub Actions"
4. 下次推送時會自動部署

### 方案三：使用其他託管平台（完整功能）

如果需要完整的 Flask 功能，建議使用：

- **Render**: https://render.com
- **Heroku**: https://heroku.com
- **Vercel**: https://vercel.com
- **Railway**: https://railway.app

這些平台可以運行 Flask 應用程式。

## 當前狀態檢查

執行以下指令檢查是否已準備好：

```bash
# 檢查資料檔案
ls -la data/processed/dengue_analysis.json

# 檢查 docs 目錄
ls -la docs/

# 檢查 GitHub Actions
ls -la .github/workflows/
```

## 快速設定指令

```bash
# 1. 建立 docs 目錄結構
mkdir -p docs/static/{css,js,data}

# 2. 複製靜態資源
cp -r website/static/* docs/static/

# 3. 複製資料檔案（如果存在）
if [ -f "data/processed/dengue_analysis.json" ]; then
    cp data/processed/dengue_analysis.json docs/static/data/
fi

# 4. 複製 HTML 檔案
cp website/templates/*.html docs/

# 5. 提交變更
git add docs/
git commit -m "Add static site for GitHub Pages"
git push
```

## 訪問網站

設定完成後，您的網站網址為：
```
https://YOUR_USERNAME.github.io/REPO_NAME/
```

**注意**：首次部署可能需要幾分鐘才會生效。

