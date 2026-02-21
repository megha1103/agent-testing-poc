@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt -q 2>nul
if errorlevel 1 (
    py -m pip install -r requirements.txt -q 2>nul
)
echo.
echo Running Agent-Based Testing POC demo...
echo.
python main.py 2>nul
if errorlevel 1 py main.py
echo.
if exist reports (
    echo Reports saved in: %CD%\reports
    explorer reports
) else (
    echo No reports folder yet. Run: python main.py
)
pause
