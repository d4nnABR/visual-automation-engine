@echo off
rem Lanzador de la reserva para el Programador de tareas.
rem El flujo abre la app y espera hasta la hora de inicio configurada en el
rem menu (opcion 2). El flujo se busca en flujos\ (o en la raiz, por compatibilidad).
rem Solo da OK si ve "Se ha reservado!" con el check verde; si no, cierra
rem Power Apps y reintenta (maximo 5 intentos). Historial por intento en
rem automation_images\debug\historial_reservas.log
rem Codigo de salida: 0 = reserva confirmada o semana libre, 1 = no se logro.
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist "automation_images\debug" mkdir "automation_images\debug"
python -u main.py reservar reserva_csi.txt >> "automation_images\debug\reserva_bat.log" 2>&1
set CODIGO=%ERRORLEVEL%
endlocal & exit /b %CODIGO%
