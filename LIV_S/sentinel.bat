@echo off
setlocal

REM Directory where this BAT is located
set DIR=%~dp0

REM First run → setup
if not exist "%DIR%protected_files.dat" (
    start "" python "%DIR%setup.py"
) else (
    REM Ghost mode (no UI, no console)
    start "" pythonw "%DIR%godmod.py"
)

exit