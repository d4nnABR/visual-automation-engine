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
python main.py reservar reserva_csi.txt
```

`reservar` solo da la reserva por hecha si ve **"Se ha reservado!" con el check
verde** (deja la captura `CONFIRMACION_OK_*.png` / `CONFIRMACION_FALTA_*.png` en
`automation_images\debug`). Si no la ve, **cierra Power Apps y repite el flujo
completo**, hasta **5 intentos** (lo que pase primero). Cada intento queda en
`automation_images\debug\historial_reservas.log`. Semana libre o ESC no se
reintentan. (`run` ejecuta el flujo una sola vez, sin verificar.)

Si lo inicias cuando la hora de inicio ya pasó y faltan más de 12 h para la
siguiente, **no espera** y ejecuta de inmediato (sirve para recuperar una noche
perdida: la fecha habilitada ese día sigue disponible).

## Opción 2: lanzador `auto.bat`

`C:\Users\gary.abrigo\Downloads\Projects\VisualPilot\auto.bat` hace `cd` a la carpeta
del proyecto, ejecuta `main.py reservar reserva_csi.txt` (con confirmación y
reintentos) y agrega la salida a `automation_images\debug\reserva_bat.log`.
Devuelve `0` si la reserva quedó confirmada (o semana libre) y `1` si no se logró
en 5 intentos, así el Programador de tareas muestra el resultado.

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

### Una sola ejecución a la vez

Se puede lanzar `auto.bat` desde varios lados (la tarea de las 23:58, un acceso
al encender el PC, a mano): `run` y `reservar` toman un mutex de Windows
(`Local\VisualPilot_ejecucion`). Si ya hay una ejecución en curso, la nueva
**no se inicia**: escribe "Ya hay otra ejecución de VisualPilot en curso" en
`reserva_bat.log` y sale con 0. El mutex se libera solo al terminar el proceso
(aunque se cierre de golpe), así que nunca queda bloqueado. El menú abierto sin
ejecutar nada no bloquea la tarea.

### Por qué la tarea "no se lanza" (evento 332)

Con "Ejecutar solo cuando el usuario haya iniciado sesión", si a las 23:58 **no
hay sesión abierta** la tarea no corre: el Historial muestra el evento **332**
("el usuario no tenía una sesión iniciada"). Pasa si se usa **Inicio → Apagar** o
**Cerrar sesión**: el equipo despierta a la hora (por "Activar el equipo"), pero
sin sesión no hay escritorio donde clickear. Para la noche: **no apagar ni cerrar
sesión**; dejar la sesión abierta o, mejor, iniciar `auto.bat` a mano antes de
irse: mientras espera la hora mantiene el equipo despierto y evita que se
bloquee la pantalla.

"Ejecutar tanto si el usuario inició sesión como si no" **no sirve**: corre en
segundo plano sin escritorio y los clicks/OCR no funcionan.
