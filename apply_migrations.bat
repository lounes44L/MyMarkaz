@echo off
echo Applying pending migrations...
python manage.py migrate
echo Migration completed!
pause
