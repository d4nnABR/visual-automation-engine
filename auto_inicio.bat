@echo off
rem Lanzador para el ARRANQUE del PC (o "Al iniciar sesion").
rem Si ya hay un log exitoso (Resultado: OK) para la fecha que toca reservar,
rem no se lanza. Si no, reserva igual que auto.bat (confirmacion + 5 intentos).
rem Si ya hay otra ejecucion en curso (p. ej. la tarea de las 23:58), tampoco.
rem Codigo de salida: 0 = ya estaba, confirmada o semana libre, 1 = no se logro.
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist "automation_images\debug" mkdir "automation_images\debug"
python -u main.py reservar_si_falta reserva_csi.txt >> "automation_images\debug\reserva_bat.log" 2>&1
set CODIGO=%ERRORLEVEL%
endlocal & exit /b %CODIGO%
