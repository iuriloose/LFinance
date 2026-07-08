@echo off
cd /d %~dp0
python -m pip install --upgrade pyinstaller PySide6 python-dateutil
pyinstaller --clean --noconfirm LFinance.spec
pause
