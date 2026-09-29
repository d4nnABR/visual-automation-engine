# Visual Automation Engine

Motor de automatizacion visual para Windows, modular y **agnostico de la
aplicacion**: maneja cualquier programa de escritorio mediante un archivo de
instrucciones, combinando **anclas de imagen (OpenCV multi-escala)**, **OCR
nativo de Windows**, **deteccion de color** y coordenadas, con control de flujo,
cierres de avisos y verificaciones de seguridad.

> Adaptalo a tu app: graba tus propias anclas y escribe tu propio `.txt`.
> El motor no depende de ninguna aplicacion en particular. Ver `flujos/ejemplos/`.

---

## Caracteristicas

- Click, escritura, teclas y combinaciones.
- Imagenes: `CLICK_WHEN_IMAGE`, `WAIT_FOR_IMAGE`, `CLICK_IF_IMAGE`.
- Anclas multi-escala (tolerantes a cambios de DPI/zoom): `CLICK_ANCHOR`,
  `WAIT_ANCHOR`, `CLICK_IF_ANCHOR`, `VERIFY_ANCHOR`.
- OCR nativo (`winsdk`): `CLICK_TEXT`, `WAIT_TEXT`, `CLICK_IF_TEXT`, `VERIFY_TEXT`.
- Color: `CLICK_RANDOM_YELLOW`, `CLICK_AVAILABLE_COLOR` (con preferencia).
- Apertura de programas/URL/URI sin click inicial: `LAUNCH`.
- Ventanas: `FOCUS_WINDOW` y `MAXIMIZE` determinista por handle (HWND).
- Esperas programadas que cruzan medianoche (`@HH:MM:SS`, `WAIT_UNTIL`) y
  mantienen el PC despierto durante la espera.
- `GUARD` y `AUTO_GUARD`: cierran avisos/banners conocidos antes de cada paso.
- Recuperacion de errores: `ON_FAIL_GOTO`, `LABEL`, `GOTO`, `RETRY`.
- Seguridad: **no envia entrada si la estacion esta bloqueada**.
- Grabador interactivo y comandos de linea `run` / `validate`.

---

## Requisitos

- Windows 10/11 y Python 3.9+.
- Dependencias:

```bash
pip install pyautogui keyboard pillow pyperclip pygetwindow opencv-python winsdk
```

- El OCR usa el motor nativo de Windows: instala el paquete de idioma del OCR
  correspondiente al idioma de tu app (los ejemplos usan espanol `es-ES`/`es-MX`).

---

## Uso rapido

Menu interactivo:

```bash
python main.py
```

Ejecutar un flujo directamente (sin menu):

```bash
python main.py run reserva_csi.txt
python main.py validate mi_flujo.txt
```

Para detener una ejecucion en cualquier momento: **ESC**.

Los flujos se buscan en `flujos/` (o por ruta completa). `run` devuelve codigo de
salida `0` si termino bien (o no tocaba reservar) y `1` si hubo errores.

### Opciones del menu

1. Ejecutar un flujo.
2. **Configurar reserva**: hora de inicio, modo de fecha (anticipacion o dia de
   semana), semanas alternas (y cual semana toca) y prioridad de parqueos.
   Se guarda en `config_usuario.json`.
3. Ver ultimo log (resumen: fecha elegida, parqueo, errores).
4. Limpiar debug (borra logs y capturas de mas de N dias, con confirmacion).
5. Grabar flujo nuevo · 6. Continuar grabacion.
7. Validar un flujo · 8. Ver imagenes · 9. Directorio base · 0. Salir.

---

## Formato del archivo de instrucciones

```
ACCION,X,Y,RETRASO,CARGA
```

Las lineas que empiezan con `#` se ignoran. Hay flujos completos en
`flujos/ejemplos/`.

Variables: `{HORA_INICIO}`, `{PRIORIDAD}` y `{DIAS_ANTICIPACION}` se reemplazan
al cargar el flujo con lo configurado en el menu (opcion 2). Una variable
desconocida invalida la linea.

| Accion | Descripcion |
|---|---|
| `CLICK` | Click en coordenadas |
| `TYPE` | Click y escribir texto |
| `TYPE_RAW` | Escribir sin click previo |
| `PRESS` | Presionar una tecla |
| `HOTKEY` | Combinacion de teclas |
| `KEYEVENTS` | Reproducir una secuencia de teclas grabada |
| `CLICK_WHEN_IMAGE` | Click cuando aparezca una imagen |
| `WAIT_FOR_IMAGE` | Esperar a que aparezca una imagen (retraso = timeout) |
| `CLICK_IF_IMAGE` | Click solo si la imagen esta presente |
| `CLICK_NEXT_DATE` | Click en la siguiente fecha disponible del calendario |
| `CLICK_RANDOM_YELLOW` | Click en un cuadro amarillo aleatorio de una region |
| `CLICK_AVAILABLE_COLOR` | Click en un cuadro disponible (amarillo) con preferencia |
| `LAUNCH` | Abrir app/proceso/URL/URI |
| `FOCUS_WINDOW` | Traer al frente la ventana que coincida con un titulo |
| `MAXIMIZE` | Maximizar la ventana objetivo (por HWND) |
| `PASTE` | Copiar al portapapeles y `Ctrl+V` (soporta acentos) |
| `WAIT_UNTIL` | Esperar a la proxima ocurrencia de `HH:MM:SS` |
| `CLICK_ANCHOR` | Click en un ancla encontrada en pantalla |
| `CLICK_IF_ANCHOR` | Click solo si el ancla esta presente |
| `WAIT_ANCHOR` | Esperar a que aparezca un ancla (retraso = timeout) |
| `VERIFY_ANCHOR` | Fallar si el ancla no esta (no hace click) |
| `CLICK_TEXT` | Click en un texto leido por OCR |
| `CLICK_IF_TEXT` | Click en el texto solo si esta presente |
| `WAIT_TEXT` | Esperar a que aparezca un texto (retraso = timeout) |
| `VERIFY_TEXT` | Fallar si el texto no esta (no hace click) |
| `DROPDOWN` | `x,y` = campo; `CARGA` = opcion a elegir (por OCR) |
| `SELECCIONAR_DIA` | Elegir un dia del calendario por posicion de celda (`auto`, numero o `AAAA-MM-DD`); verifica la seleccion y, si falla, detiene el flujo |
| `MARCAR_1DIA` | Marcar el checkbox "1 dia" (calibracion de ejemplo) |
| `SELECCIONAR_PARQUEO` | Buscar un recurso por numero y marcar su checkbox |
| `VERIFICAR_SEMANA` | Si hay semanas alternas y la fecha a reservar cae en semana libre, termina el flujo sin error |
| `GUARD` | Cerrar avisos/banners conocidos |
| `LABEL` / `GOTO` / `RETRY` / `ON_FAIL_GOTO` | Control de flujo |

Banderas de `CLICK_TEXT`: `|exacto`, `|doble`, `|boton` (solo botones de
contenido, no la barra inferior de navegacion). Se pueden combinar, por ejemplo
`CLICK_TEXT,0,0,1,Confirmar|exacto|boton`.

### Esperas programadas

El campo `RETRASO` acepta `@HH:MM:SS` para esperar hasta la **proxima
ocurrencia** de esa hora, cruzando medianoche. Si la hora ya paso y la proxima
ocurrencia queda a mas de 12 h, no espera (evita quedarse 24 h). Durante la
espera el equipo se mantiene despierto.

```
WAIT_FOR_IMAGE,0,0,120@00:02:05,bienvenido.png
WAIT_UNTIL,0,0,0,00:02:05
```

### Formatos de LAUNCH

```
LAUNCH,0,0,1,path:C:\ruta\app.exe
LAUNCH,0,0,1,proc:notepad
LAUNCH,0,0,1,aumid:Vendor.App_xxxxx!App
LAUNCH,0,0,1,https://ejemplo.com
LAUNCH,0,0,1,mi-esquema://parametro
```

Modo "sin click al iniciar": comenzar el flujo con `LAUNCH` + `WAIT_FOR_IMAGE`.

### Anclas, OCR, color y guard

- Anclas: coloca recortes `.png` en `automation_images/anchors/`. El motor los
  busca en toda la pantalla a varias escalas. Las anclas **nunca clickean a
  ciegas**: `CLICK_ANCHOR` falla si no la encuentra y `CLICK_IF_ANCHOR` continua.
- OCR: lee texto real de la pantalla (fechas, temporizadores, mensajes).
- Color: `CLICK_AVAILABLE_COLOR,500,180,2,1380|760|derecha` hace click en un
  elemento disponible (amarillo) de la region, con preferencia
  `derecha|izquierda|arriba|abajo|aleatorio`.
- Guard: coloca recortes del boton de cierre en
  `automation_images/obstrucciones/`. Con `AUTO_GUARD = True` se cierran antes de
  cada paso; `GUARD` lo fuerza.

### Seguridad ante bloqueo

Si la estacion de trabajo esta bloqueada, el motor **no envia ninguna tecla ni
click** y espera al desbloqueo (evita escribir en la pantalla de bloqueo). La
automatizacion requiere una sesion desbloqueada.

---

## Adaptarlo a tu aplicacion

1. Graba tus imagenes de referencia con el grabador (`g` = ancla, `e` = ancla de
   espera, `o` = obstruccion, `m` = maximizar).
2. Escribe tu `.txt` con el catalogo de acciones de arriba.
3. Calibra las coordenadas en `visualpilot/ajustes.py` para tu ventana **maximizada** a una
   resolucion/zoom fijos.
4. Ejecuta `python main.py run mi_flujo.txt`.

Los modulos del motor son genericos; solo son especificos de una app los flujos,
las imagenes y `visualpilot/ajustes.py`. `visualpilot/reserva.py` es la logica de
fecha y "semanas alternas" del ejemplo; puedes ignorarla.

---

## Estructura del proyecto

```
VisualPilot/
├── main.py              # Punto de entrada (menu + CLI)
├── auto.bat             # Lanzador para el Programador de tareas
├── visualpilot/
│   ├── menu.py          # Menu, configuracion de reserva, logs, limpieza, CLI
│   ├── core.py          # Orquestacion, control de flujo, variables, guard de bloqueo
│   ├── acciones.py      # Ejecucion de acciones
│   ├── vision.py        # Utilidades de imagen/color (acciones legacy)
│   ├── vision_ui.py     # Anclas (OpenCV), maximizar, guard, color
│   ├── ocr.py           # OCR nativo de Windows
│   ├── reserva.py       # Fecha a reservar y semanas alternas
│   ├── ajustes.py       # Calibracion por app y valores por defecto de reserva
│   ├── config.py        # Configuracion del motor y config_usuario.json
│   ├── utils.py         # Tiempo, deteccion de bloqueo, keep-awake
│   └── logger.py        # Logs y capturas de error
├── flujos/              # Flujos .txt (personales ignorados) y ejemplos/
├── docs/                # Como ejecutar, inicio automatico, pendientes
├── herramientas/        # Utilidades (generar anclas desde capturas)
└── automation_images/   # anchors/ · obstrucciones/ · debug/
```

---

## Notas

- Todo lo que hay en `automation_images/` (imagenes, logs, capturas) y
  `config_usuario.json` (rutas locales y configuracion de reserva) **no se versiona**.
- Los flujos personales (`reserva_csi.txt`, `onlypark.txt`) estan ignorados por git.
- Pendiente: modo PC bloqueado / keep-awake (ver `docs/TAREAS.md`).

---

## Licencia

MIT. Ver `LICENSE`.

## Autor

[d4nnABR](https://github.com/d4nnABR)
