@echo off
rem Executa o autoclicker usando o ambiente virtual local (.venv)
"%~dp0.venv\Scripts\python.exe" "%~dp0src\main.py" %*
