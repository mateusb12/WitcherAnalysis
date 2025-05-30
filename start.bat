@echo off
REM Change to the directory where the BAT file is located
cd /d %~dp0

REM Now run the manage.py script from the relative path
python source\manage.py runserver
pause