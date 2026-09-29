# Inicio automático del script

El script **no se inicia solo**: hay que dejarlo corriendo o programarlo.
Requisito: la PC debe estar **encendida y desbloqueada** a la hora de inicio
(si está bloqueada no puede clickear; ver `TAREAS.md`).

El flujo `flujos\reserva_csi.txt` abre la app (`LAUNCH`), la maximiza, **espera la
hora de inicio** (`WAIT_UNTIL,0,0,0,{HORA_INICIO}`, por defecto 00:02) y luego
`VERIFICAR_SEMANA`: si usas semanas alternas y la fecha a reservar cae en semana
libre, termina **sin error** y sin reservar.

La hora, los días de anticipación, las semanas alternas y la prioridad se cambian
en el menú: `python main.py` → opción **2**.

## Opción 1: dejarlo esperando la hora

Inicia el script **por la noche** (entre el mediodía y la hora de inicio):

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py run reserva_csi.txt
```

Si lo inicias cuando la hora de inicio ya pasó y faltan más de 12 h para la
siguiente, **no espera** y ejecuta de inmediato (sirve para recuperar una noche
perdida: la fecha habilitada ese día sigue disponible).

## Opción 2: lanzador `auto.bat`

`C:\Users\gary.abrigo\Downloads\Projects\VisualPilot\auto.bat` hace `cd` a la carpeta
del proyecto, ejecuta el flujo y agrega la salida a
`automation_images\debug\reserva_bat.log`. Devuelve `0` si terminó bien (o semana
libre) y `1` si hubo errores, así el Programador de tareas muestra el resultado.

## Opción 3: Programador de tareas

Programa el `.bat` **unos minutos antes de la hora de inicio** (p. ej. 23:58 para
00:02), así el proceso ya está vivo y esperando.

- Desencadenador: **Diario, 23:58**.
- Acción: iniciar un programa → `C:\Users\gary.abrigo\Downloads\Projects\VisualPilot\auto.bat`
  ("Agregar argumentos" e "Iniciar en" pueden quedar vacíos).
- Marcar **"Ejecutar solo cuando el usuario haya iniciado sesión"** (la
  automatización necesita la sesión desbloqueada).
- Marcar **"Ejecutar la tarea lo antes posible tras un inicio programado omitido"**.

Con semanas alternas no hace falta tocar la tarea: en la semana libre el flujo
termina solo. Si también quieres que corra al iniciar sesión, agrega un segundo
desencadenador "Al iniciar sesión".

Puede estar **bloqueado por política de TI**.
