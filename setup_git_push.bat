@echo off
chcp 65001 >nul
echo ========================================
echo 推送檔案到 GitHub
echo ========================================
echo.

set /p REPO_URL="請輸入您的 GitHub 儲存庫 URL (例如: https://github.com/USERNAME/REPO.git): "

if "%REPO_URL%"=="" (
    echo 錯誤: 未輸入儲存庫 URL
    pause
    exit /b 1
)

echo.
echo [步驟 1/3] 連接 GitHub 儲存庫...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
if %errorlevel% neq 0 (
    echo 錯誤: 無法連接儲存庫
    pause
    exit /b 1
)
echo 完成！
echo.

echo [步驟 2/3] 設定主分支...
git branch -M main
echo 完成！
echo.

echo [步驟 3/3] 推送檔案到 GitHub...
echo 注意: 如果這是第一次推送，可能需要輸入 GitHub 使用者名稱和 Personal Access Token
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 成功！檔案已上傳到 GitHub
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 推送失敗
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 認證失敗 - 請使用 Personal Access Token 而非密碼
    echo 2. 儲存庫 URL 錯誤
    echo 3. 網路連線問題
    echo.
    echo 如何取得 Personal Access Token:
    echo 1. 前往 https://github.com/settings/tokens
    echo 2. 點擊 "Generate new token (classic)"
    echo 3. 選擇 "repo" 權限
    echo 4. 複製 token 並在推送時使用
    echo.
)

pause

