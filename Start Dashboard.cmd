@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo The Python environment is missing. Follow step 1 in SETUP.md first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Streamlit is not installed. Run this command in the project folder:
    echo .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo Keep this window open while using the dashboard.
echo Once the server is ready, open http://localhost:8501 in your browser.
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
if errorlevel 1 pause
