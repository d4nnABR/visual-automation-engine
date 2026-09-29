@echo off
rem Lanzador de la reserva para el Programador de tareas.
rem El flujo abre la app y espera hasta la hora de inicio configurada en el
rem menu (opcion 2). El flujo se busca en flujos\ (o en la raiz, por compatibilidad).
rem Codigo de salida: 0 = OK o semana libre, 1 = hubo errores.
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist "automation_images\debug" mkdir "automation_images\debug"
python -u main.py run reserva_csi.txt >> "automation_images\debug\reserva_bat.log" 2>&1
set CODIGO=%ERRORLEVEL%
endlocal & exit /b %CODIGO%
