# GitHub 上傳指南

## 步驟 1: 初始化 Git 儲存庫

在專案根目錄執行：

```bash
git init
```

## 步驟 2: 添加所有檔案

```bash
git add .
```

這會根據 `.gitignore` 自動排除不需要的檔案（如資料檔案、測試檔案等）。

## 步驟 3: 建立初始提交

```bash
git commit -m "Initial commit: Taiwan Dengue Fever Epidemiology Surveillance System"
```

## 步驟 4: 在 GitHub 建立新儲存庫

1. 前往 https://github.com/new
2. 填寫儲存庫資訊：
   - **Repository name**: `dengue-fever-project` (或您喜歡的名稱)
   - **Description**: `台灣登革熱流行病學監測系統 - Taiwan Dengue Fever Epidemiology Surveillance System`
   - **Visibility**: 選擇 Public 或 Private
   - **不要**勾選 "Initialize this repository with a README"（因為我們已經有 README.md）
3. 點擊 "Create repository"

## 步驟 5: 連接本地儲存庫到 GitHub

GitHub 會顯示連接指令，類似這樣：

```bash
git remote add origin https://github.com/YOUR_USERNAME/dengue-fever-project.git
git branch -M main
git push -u origin main
```

將 `YOUR_USERNAME` 替換為您的 GitHub 使用者名稱。

## 步驟 6: 推送檔案到 GitHub

```bash
git push -u origin main
```

如果這是第一次使用，可能需要輸入 GitHub 的使用者名稱和密碼（或 Personal Access Token）。

## 完整指令序列

```bash
# 1. 初始化 Git
git init

# 2. 添加檔案
git add .

# 3. 建立提交
git commit -m "Initial commit: Taiwan Dengue Fever Epidemiology Surveillance System"

# 4. 連接 GitHub（替換 YOUR_USERNAME 和 REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 5. 設定主分支
git branch -M main

# 6. 推送檔案
git push -u origin main
```

## 注意事項

1. **資料檔案不會上傳**：`.gitignore` 已設定排除 `data/` 目錄中的檔案
2. **測試檔案不會上傳**：測試檔案已在 `.gitignore` 中排除
3. **首次推送可能需要認證**：如果遇到認證問題，請使用 Personal Access Token

## 後續更新

之後如果有修改，使用以下指令更新：

```bash
git add .
git commit -m "描述您的修改"
git push
```

## 疑難排解

### 如果遇到認證問題

GitHub 已不再支援密碼認證，請使用 Personal Access Token：

1. 前往 https://github.com/settings/tokens
2. 點擊 "Generate new token (classic)"
3. 選擇適當的權限（至少需要 `repo` 權限）
4. 複製 token
5. 推送時使用 token 作為密碼

### 如果遇到 "remote origin already exists" 錯誤

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### 如果遇到 "refusing to merge unrelated histories" 錯誤

```bash
git pull origin main --allow-unrelated-histories
```

