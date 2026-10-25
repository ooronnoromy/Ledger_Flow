@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (py -3 -m venv .venv) else (python -m venv .venv)
if errorlevel 1 (echo Python 3.11+ must be installed first. & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (echo Cannot install dependencies. Check your internet connection. & pause & exit /b 1)
if not exist .env copy .env.example .env
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 (echo Migration failed. & pause & exit /b 1)
echo Setup complete. Open http://127.0.0.1:8000/register/ after running start_windows.bat
pause
