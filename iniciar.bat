@echo off
rem Abre la pagina del proyecto sin usar la terminal a mano
cd /d "%~dp0"
python -c "import flask, matplotlib" 2>nul
if errorlevel 1 (
    echo Instalando lo que falta...
    pip install -r requirements.txt
)
python servidor.py
pause
