# Inicio automatico del script

El script **no se inicia solo** a una hora: hay que dejarlo corriendo o
programarlo. Requisito: la PC debe estar **encendida y desbloqueada** a las 00:02
(si esta bloqueada no puede clickear; ver `TAREAS.md`).

El flujo `reserva_csi.txt` ya abre la app (`LAUNCH`), la maximiza (`MAXIMIZE`) y
**espera a las 00:02** con `WAIT_UNTIL,0,0,0,00:02:00`.

## Opcion 1 (recomendada): dejarlo esperando la hora

Inicia el script **antes de dormir** (despues del mediodia y antes de medianoche):

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py run reserva_csi.txt
```

Dejalo abierto. A las 00:02 selecciona el dia correcto y reserva. Detener con ESC.

Nota: si lo inicias por la manana, como las 00:02 ya pasaron y faltan mas de 12 h,
no espera y se ejecuta de inmediato (por eso debes iniciarlo por la noche).

## Opcion 2: lanzador .bat

Crea `Reservar.bat`:

```bat
@echo off
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py run reserva_csi.txt
pause
```

Doble clic por la noche.

## Opcion 3: Programador de tareas (Task Scheduler)

- Desencadenador: diario a las 00:01.
- Accion: iniciar `python.exe` con argumentos `main.py run reserva_csi.txt`
  y "Iniciar en" = carpeta del proyecto.
- Marcar "Ejecutar solo cuando el usuario haya iniciado sesion" (interactivo).

Puede estar **bloqueado por politica de TI**. Ademas, si la sesion esta bloqueada,
la automatizacion no puede clickear.
