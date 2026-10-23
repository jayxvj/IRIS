@echo off
setlocal

REM Directory where this BAT is located
set DIR=%~dp0

start "" python "%DIR%setup.py" %*

exit
