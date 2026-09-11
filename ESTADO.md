# Estado del proyecto (retomar rapido)

Ultima actualizacion: 2026-09-11.
Rama de trabajo: `tests_new_features` (equivalente a `main`, que ya esta actualizado).
Ultimo commit relevante: `381c043` (merge) / `c68bfbf` (trabajo).

---

## Que es

Motor de automatizacion visual para Windows, **agnostico de la aplicacion**.
Maneja cualquier programa por pantalla con un archivo `.txt` de instrucciones,
combinando anclas de imagen (OpenCV multi-escala), OCR nativo de Windows,
deteccion de color y coordenadas.

---

## Estado actual (validado en vivo)

- Flujo real de reserva **`reserva_csi.txt`** probado end-to-end: **20/20 pasos,
  0 errores** (reserva completada, "Se ha reservado!").
- El bucle de seleccion de recurso funciona: recorre la prioridad y **solo pasa
  al siguiente si el checkbox no aparece o no se marca**; al marcarse sigue a
  Continuar y Confirmar.
- Guard de seguridad: si la estacion esta **bloqueada**, no envia entrada y espera.

### Acciones implementadas

Coordenadas: `CLICK`, `TYPE`, `TYPE_RAW`, `PRESS`, `HOTKEY`, `KEYEVENTS`.
Imagen: `CLICK_WHEN_IMAGE`, `WAIT_FOR_IMAGE`, `CLICK_IF_IMAGE`.
Anclas: `CLICK_ANCHOR`, `CLICK_IF_ANCHOR`, `WAIT_ANCHOR`, `VERIFY_ANCHOR`.
OCR: `CLICK_TEXT`, `CLICK_IF_TEXT`, `WAIT_TEXT`, `VERIFY_TEXT`.
Ventanas/app: `LAUNCH`, `FOCUS_WINDOW`, `MAXIMIZE`, `PASTE`, `WAIT_UNTIL`, `GUARD`.
Especificas del ejemplo: `DROPDOWN`, `SELECCIONAR_DIA`, `MARCAR_1DIA`,
`SELECCIONAR_PARQUEO`, `CLICK_AVAILABLE_COLOR`, `CLICK_NEXT_DATE`,
`CLICK_RANDOM_YELLOW`.
Control de flujo: `LABEL`, `GOTO`, `RETRY`, `ON_FAIL_GOTO`.

---

## Como ejecutar (resumen)

```bat
cd /d "C:\Users\gary.abrigo\Downloads\Projects\VisualPilot"
pip install pyautogui keyboard pillow pyperclip pygetwindow opencv-python winsdk
python main.py run reserva_csi.txt
```

- Detener con **ESC**.
- El **directorio base** apunta a esta misma carpeta (todo queda dentro del proyecto).
- Detalle completo: `COMO_EJECUTAR.md`.

---

## Archivos clave

| Archivo | Rol |
|---|---|
| `main.py` | Menu + comandos `run` / `validate` |
| `core.py` | Orquestacion, control de flujo, guard de bloqueo |
| `acciones.py` | Implementacion de las acciones |
| `vision_ui.py` | Anclas (OpenCV), maximizar, guard, color |
| `ocr.py` | OCR nativo de Windows |
| `utils.py` | Tiempo, `esta_bloqueado()`, keep-awake, espera por hora |
| `config.py` | Configuracion generica del motor |
| `ajustes.py` | Calibracion especifica de la app de ejemplo (editar aqui) |
| `reserva.py` | Ejemplo: logica de semanas alternas |
| `reserva_csi.txt` | Flujo real (personal, ignorado por git) |
| `TAREAS.md` | Pendientes |
| `ejemplos/` | Flujos genericos y anonimizados |

---

## El flujo real `reserva_csi.txt`

1. `MAXIMIZE` de la app.
2. `GUARD` (cierra avisos; p. ej. banner rojo de semana no asignada).
3. `Agendar` -> `SELECCIONAR_DIA` (dia fijo, o `auto` por semanas).
4. `DROPDOWN` tipo de recurso = PARQUEO -> `MARCAR_1DIA` -> `Continuar`.
5. Ubicacion (3 `DROPDOWN`): pais / unidad / ubicacion.
6. `SELECCIONAR_PARQUEO` con prioridad: `39,38,37,36,35,34,33,32,31,105,106,104`.
7. `Continuar` -> `WAIT_TEXT "todo bien"` -> `Confirmar|exacto|boton` ->
   `WAIT_TEXT "Se ha reservado"`.

---

## Puntos importantes (gotchas)

- Siempre `MAXIMIZE` antes de buscar anclas o usar coordenadas calibradas.
- Coordenadas de `ajustes.py` calibradas a ventana maximizada, 1920x1080 al 100%.
  Si cambia resolucion/zoom, recalibrar.
- OCR requiere idioma instalado (espanol). El campo de busqueda se localiza solo
  con la palabra `Buscar` (tolera cambios de texto).
- La app de reserva tiene un **temporizador (~5 min)**; el flujo debe ser rapido.
- El banner rojo puede aparecer de forma transitoria; `GUARD` lo cierra.
- `onlypark.txt` es un flujo antiguo; ya no se usa.

---

## Pendientes

- **PC bloqueado / keep-awake** (ver `TAREAS.md`): confirmar si el bloqueo es por
  politica o inactividad; probar keep-awake; o excepcion de TI / equipo aparte.
- Manejo de **"0 disponibles"** y de banner rojo (probar otra fecha/semana).
- Activar `SELECCIONAR_DIA auto` (semanas alternas) cuando corresponda.
- Rotar/limpiar `automation_images/debug` (logs y capturas acumuladas).

---

## Git

- Remoto: `https://github.com/d4nnABR/visual-automation-engine` (donde `main` ya
  tiene todo lo trabajado).
- No hay `gh` instalado; los PR se abren por web.
- `config_usuario.json`, `reserva_csi.txt`, `onlypark.txt` y
  `automation_images/**` estan ignorados por git (no se publican).
