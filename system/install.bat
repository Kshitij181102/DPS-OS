@echo off
REM DPS-OS Windows Installation Script

echo Installing DPS-OS for Windows development...

REM Create installation directory
if not exist "C:\dps-os" mkdir "C:\dps-os"
xcopy /E /I daemon "C:\dps-os\daemon\"
xcopy /E /I agents "C:\dps-os\agents\"
xcopy /E /I watchers "C:\dps-os\watchers\"
xcopy /E /I schema "C:\dps-os\schema\"

REM Install Python dependencies
pip install pyudev watchdog jsonschema psutil flask

echo DPS-OS installed successfully!
echo Note: This is a development setup. Linux is recommended for production.
echo Start daemon with: python C:\dps-os\daemon\daemon.py
pause