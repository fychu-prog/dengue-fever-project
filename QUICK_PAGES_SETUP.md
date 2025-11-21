# GitHub Pages 快速設定

## 訪問您的網站

GitHub Pages 的網址格式為：
```
https://YOUR_USERNAME.github.io/REPO_NAME/
```

例如，如果您的：
- GitHub 使用者名稱是：`username`
- 儲存庫名稱是：`dengue-fever-project`

那麼網址就是：
```
https://username.github.io/dengue-fever-project/
```

## 重要：這是 Flask 應用，需要轉換為靜態版本

GitHub Pages 只能託管靜態網站，無法運行 Flask 後端。需要將資料轉換為靜態 JSON 檔案。

## 快速設定步驟

### 方法一：手動設定（最簡單）

1. **建立 docs 目錄並複製檔案**
   ```bash
   # 建立目錄
   mkdir -p docs/static/{css,js,data}
   
   # 複製靜態資源
   xcopy /E /I website\static\css docs\static\css
   xcopy /E /I website\static\js docs\static\js
   
   # 複製資料檔案（如果存在）
   if exist data\processed\dengue_analysis.json (
       copy data\processed\dengue_analysis.json docs\static\data\
   )
   
   # 複製 HTML 檔案
   copy website\templates\*.html docs\
   ```

2. **在 GitHub 設定 Pages**
   - 前往您的儲存庫
   - 點擊 Settings（設定）
   - 左側選單選擇 Pages
   - Source 選擇 "Deploy from a branch"
   - Branch 選擇 `main`，資料夾選擇 `/docs`
   - 點擊 Save

3. **等待部署完成**
   - 通常需要 1-2 分鐘
   - 重新整理頁面，會看到 "Your site is live at..."

4. **訪問網站**
   - 使用上面提到的網址格式

### 方法二：使用 GitHub Actions（自動化）

已建立 `.github/workflows/deploy-pages.yml`，會自動部署。

1. **確保檔案已提交**
   ```bash
   git add .github/workflows/deploy-pages.yml
   git commit -m "Add GitHub Pages deployment"
   git push
   ```

2. **在 GitHub 設定 Pages**
   - Settings > Pages
   - Source 選擇 "GitHub Actions"

3. **等待自動部署**

## 檢查部署狀態

1. 前往儲存庫的 **Actions** 標籤
2. 查看 "Deploy to GitHub Pages" 工作流程
3. 如果顯示綠色 ✓，表示部署成功

## 常見問題

### Q: 網站顯示 404？
A: 檢查：
- Settings > Pages 是否已啟用
- 是否選擇了正確的資料夾（/docs）
- 等待幾分鐘讓部署完成

### Q: 資料無法載入？
A: 確保 `docs/static/data/dengue_analysis.json` 檔案存在

### Q: 想要完整 Flask 功能？
A: 考慮使用 Render、Heroku 或 Vercel 等平台

