@echo off
:loop
cd C:\Users\DARCKBLACK\Desktop\performance_monitor
"C:\Users\DARCKBLACK\AppData\Local\Programs\Python\Python313\python.exe" app.py
if %errorlevel% neq 0 (
    echo Script crashed, restarting...
    timeout /t 5 /nobreak >nul
)
goto loop
pause