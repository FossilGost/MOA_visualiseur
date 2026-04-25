@echo off
cd /d "%~dp0"
call MOAenv\Scripts\activate
python main.py
pause