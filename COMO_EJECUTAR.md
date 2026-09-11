# Cómo ejecutar VisualPilot desde CMD

## Requisitos (una sola vez)

```bat
pip install pyautogui keyboard pillow pyperclip pygetwindow opencv-python winsdk
```

- Power Apps debe estar **maximizado** y la **sesión desbloqueada**.
- El OCR (`winsdk`) debe tener idioma español instalado.

## 1) Menú interactivo

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py
```

Opciones del menú: 1 grabar · 2 ejecutar · 3 continuar grabación · 4 ver imágenes ·
5 validar · 6 directorio base · 7 salir.

## 2) Ejecutar un flujo directamente (sin menú)

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py run reserva_csi.txt
```

También acepta ruta absoluta:

```bat
python main.py run "C:\ruta\a\mi_flujo.txt"
```

En el repo hay ejemplos genéricos:

```bat
python main.py run ejemplos\ejemplo_reserva.txt
```

- Si el nombre no incluye ruta, se busca en el **directorio base** configurado.
- Para detener la ejecución en cualquier momento: **ESC**.

## 3) Validar un archivo (sin ejecutarlo)

```bat
python main.py validate ejemplos\ejemplo_reserva.txt
```

## 4) Lanzador con doble clic (.bat)

Crea `ReservarParqueo.bat` con:

```bat
@echo off
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
python main.py run reserva_csi.txt
pause
```

(Sustituye `reserva_csi.txt` por tu propio flujo.)

## Directorio base

Es donde se buscan los `.txt`, las imágenes y las anclas. Se guarda en
`config_usuario.json` y se cambia con la opción **6** del menú. Estructura:

```
<directorio_base>\
├── reserva_csi.txt            (flujos)
└── automation_images\
    ├── anchors\               (anclas: CLICK_ANCHOR/WAIT_ANCHOR)
    ├── obstrucciones\         (avisos que cierra GUARD)
    └── debug\                 (logs y capturas de error)
```

## Notas

- El flujo empieza con `MAXIMIZE` para fijar el layout (las coordenadas de
  `BUSCAR_PARQUEO` y `DURACION_1DIA` en `config.py` están calibradas a pantalla
  maximizada).
- Si la estación está bloqueada, el flujo **no envía entrada** y espera
  (evita teclear en la pantalla de bloqueo).
- El modo PC bloqueado / keep-awake está pendiente: ver `TAREAS.md`.
