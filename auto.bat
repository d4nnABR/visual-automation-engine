@echo off
rem Lanzador de la reserva para el Programador de tareas.
rem El flujo abre la app y espera hasta las 00:02 (WAIT_UNTIL).
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist "automation_images\debug" mkdir "automation_images\debug"
python -u main.py run reserva_csi.txt >> "automation_images\debug\reserva_bat.log" 2>&1
endlocal
