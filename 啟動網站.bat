@echo off
chcp 65001 >nul
echo ========================================
echo 啟動登革熱監測系統網站
echo ========================================
echo.
echo 正在啟動 Flask 伺服器...
echo.
cd website
python app.py
pause

