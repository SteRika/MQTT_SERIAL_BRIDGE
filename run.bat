@echo off
:start
echo %date% %time%: Starting PLC-MQTT Bridge...
python main.py

if %errorlevel% equ 0 (
    echo %date% %time%: Normal exit, stopping completely
    pause
    exit /b 0
) else (
    echo %date% %time%: Unexpected exit, restarting in 5 seconds...
    timeout /t 5 /nobreak
    goto start
)