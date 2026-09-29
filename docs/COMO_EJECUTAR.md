# Cómo ejecutar VisualPilot

## Requisitos (una sola vez)

```bat
pip install pyautogui keyboard pillow pyperclip pygetwindow opencv-python winsdk
```

- Power Apps debe quedar **maximizado** (el flujo lo hace con `MAXIMIZE`) y la
  **sesión desbloqueada**.
- El OCR (`winsdk`) necesita el idioma español instalado.

## 1) Menú

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py
```

| Opción | Qué hace |
|---|---|
| 1 | Ejecutar un flujo (se busca en `flujos\`) |
| 2 | Configurar reserva: hora de inicio, modo de fecha, semanas alternas, prioridad de parqueos |
| 3 | Ver el último log (resumen) |
| 4 | Limpiar `automation_images\debug` (archivos de más de N días) |
| 5 / 6 | Grabar un flujo nuevo / continuar una grabación |
| 7 | Validar un flujo sin ejecutarlo |
| 8 / 9 | Ver imágenes / cambiar directorio base |

Lo configurado en la opción 2 se guarda en `config_usuario.json` y el flujo lo usa
mediante variables (`{HORA_INICIO}`, `{PRIORIDAD}`).

## 2) Ejecutar un flujo directamente

```bat
python main.py run reserva_csi.txt
python main.py validate reserva_csi.txt
```

- Si solo das el nombre, se busca en `flujos\` y, por compatibilidad, en la raíz.
- También acepta ruta completa.
- Detener en cualquier momento: **ESC**.
- Código de salida de `run`: `0` terminó bien (o semana libre), `1` hubo errores.

## 3) Lanzador `auto.bat`

Doble clic (o Programador de tareas): ejecuta `reserva_csi.txt` y agrega la salida a
`automation_images\debug\reserva_bat.log`. Detalle en `INICIO_AUTOMATICO.md`.

## Directorio base

Es donde se buscan `flujos\` e `automation_images\`. Por defecto es la carpeta del
proyecto; se cambia con la opción 9.

```
<directorio_base>\
├── flujos\                 (reserva_csi.txt y otros flujos)
└── automation_images\
    ├── anchors\            (anclas: CLICK_ANCHOR/WAIT_ANCHOR)
    ├── obstrucciones\      (avisos que cierra GUARD)
    └── debug\              (logs y capturas de error)
```

## Notas

- Coordenadas calibradas a ventana maximizada 1920x1080 al 100 %
  (`visualpilot\ajustes.py`). Si cambia resolución o zoom, recalibrar.
- Si la estación está bloqueada, el flujo **no envía entrada** y espera.
