@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1 && goto run_python
where py >nul 2>&1 && goto run_py
echo Python nao encontrado. Instale em https://www.python.org/downloads/ e marque tcl/tk.
exit /b 1

:run_python
python teleprompter.py %*
exit /b %ERRORLEVEL%

:run_py
py -3 teleprompter.py %*
exit /b %ERRORLEVEL%
