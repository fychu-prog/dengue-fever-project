@echo off
chcp 65001 >nul
echo ========================================
echo 登革熱監測系統 - 完整啟動流程
echo ========================================
echo.

echo [步驟 1/3] 下載最新資料...
echo.
python src/download_dengue_data.py --auto
if %errorlevel% neq 0 (
    echo.
    echo [警告] 自動下載失敗，請檢查網路連線或手動下載資料
    echo 手動下載網址: https://data.gov.tw/datasets/search?qs=登革熱
    echo.
    set /p CONTINUE="是否要繼續使用現有資料？(Y/N): "
    if /i not "%CONTINUE%"=="Y" (
        echo 已取消
        pause
        exit /b 1
    )
)
echo.

echo [步驟 2/3] 分析資料...
echo.
python src/analyze_dengue.py
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 資料分析失敗
    echo 請確認 data/raw/Dengue_Daily.csv 檔案存在
    pause
    exit /b 1
)
echo.

echo [步驟 3/3] 啟動網站伺服器...
echo.
echo 網站將在以下網址開啟:
echo   http://localhost:8080
echo   http://127.0.0.1:8080
echo.
echo 按 Ctrl+C 可停止伺服器
echo ========================================
echo.

cd website
python app.py

pause