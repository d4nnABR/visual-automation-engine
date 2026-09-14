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

## Opcion 2: lanzador .bat (ya incluido)

El archivo ya existe en la raiz del proyecto:

```
C:\Users\gary.abrigo\Downloads\Projects\VisualPilot\ReservarParqueo.bat
```

Hace `cd` a la carpeta del proyecto y ejecuta el flujo, guardando el log en
`automation_images\debug\reserva_bat.log`. Doble clic por la noche.

## Opcion 3: Programador de tareas (Task Scheduler)

Programa el `.bat` **a las 23:58** (4 min antes de las 00:02), asi el proceso ya
esta vivo y esperando la hora.

- Desencadenador: **Diario, 23:58**.
- Accion: iniciar un programa -> `C:\Users\gary.abrigo\Downloads\Projects\VisualPilot\ReservarParqueo.bat`
  (o `cmd.exe` con argumentos `/c "...\ReservarParqueo.bat"`).
- "Iniciar en": `C:\Users\gary.abrigo\Downloads\Projects\VisualPilot`.
- Marcar **"Ejecutar solo cuando el usuario haya iniciado sesion"** (interactivo:
  la automatizacion necesita la sesion desbloqueada).
- Marcar **"Ejecutar la tarea lo antes posible tras una inicio programado
  omitido"** por si la PC estaba apagada a las 23:58.

Si quieres que tambien corra **al iniciar la PC**, agrega un segundo desencadenador
"Al iniciar sesion".

Puede estar **bloqueado por politica de TI**. Ademas, si la sesion esta bloqueada,
la automatizacion no puede clickear (no envia entrada).
