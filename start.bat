@echo off
REM Change to the directory where the BAT file is located
cd /d %~dp0

REM Change to the source directory to run manage.py and daphne
cd source

REM Ensure migrations are run
python manage.py makemigrations api
python manage.py makemigrations
python manage.py migrate

REM Now run the server with Daphne for ASGI support
REM The path to asgi application should be relative to the directory where daphne is run (source/)
daphne -p 8000 django_layer.character_net.asgi:application
pause

