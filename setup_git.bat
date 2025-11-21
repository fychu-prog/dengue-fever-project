@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 上傳設定腳本
echo ========================================
echo.

echo [步驟 1/6] 初始化 Git 儲存庫...
git init
if %errorlevel% neq 0 (
    echo 錯誤: Git 未安裝或無法執行
    echo 請先安裝 Git: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo 完成！
echo.

echo [步驟 2/6] 檢查 .gitignore 檔案...
if not exist .gitignore (
    echo 警告: 找不到 .gitignore 檔案
) else (
    echo .gitignore 檔案存在
)
echo.

echo [步驟 3/6] 添加檔案到 Git...
git add .
echo 完成！
echo.

echo [步驟 4/6] 建立初始提交...
git commit -m "Initial commit: Taiwan Dengue Fever Epidemiology Surveillance System"
if %errorlevel% neq 0 (
    echo 警告: 提交失敗，可能是因為沒有變更或已存在提交
)
echo.

echo ========================================
echo 本地 Git 儲存庫已設定完成！
echo ========================================
echo.
echo 接下來請：
echo 1. 前往 https://github.com/new 建立新儲存庫
echo 2. 複製儲存庫的 URL（例如：https://github.com/YOUR_USERNAME/REPO_NAME.git）
echo 3. 執行以下指令連接 GitHub：
echo.
echo    git remote add origin YOUR_REPO_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 或執行 setup_git_push.bat 並輸入您的儲存庫 URL
echo.
pause

