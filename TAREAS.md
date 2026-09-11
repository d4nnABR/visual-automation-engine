# TAREAS — VisualPilot (Reservas CMI CSI-Corporativo)

Bitácora de pendientes. Fase 1 y Fase 2 completadas. Lo de abajo es lo que falta.

## Hecho (Fase 1 + Fase 2)

- [x] `esperar_hasta_hora` con próxima ocurrencia y cruce de medianoche (ventana máx. 12 h).
- [x] PC se mantiene despierto durante esperas (`SetThreadExecutionState`).
- [x] `WAIT_FOR_IMAGE` sin código muerto; `retraso` = timeout; `@HH:MM:SS` = espera posterior.
- [x] Comentarios `#` ignorados en validación y ejecución.
- [x] Screenshots de error activados (`CAPTURAR_SCREENSHOTS_ERROR = True`).
- [x] Nuevas acciones: `LAUNCH`, `FOCUS_WINDOW`, `PASTE`, `WAIT_UNTIL`, `CLICK_IF_IMAGE`.
- [x] `ESC` cancela también dentro de `esperar_imagen`.
- [x] README actualizado (menú real, acciones nuevas, `@HH:MM:SS`, `LAUNCH`).
- [x] Motor de **anclas por imagen** (`vision_ui.py`, OpenCV multi-escala) probado: `nueva_reference.png` con confianza 0.838.
- [x] `MAXIMIZE` determinista por HWND (`ShowWindow`), no por teclado.
- [x] Acciones de ancla: `CLICK_ANCHOR`, `CLICK_IF_ANCHOR`, `WAIT_ANCHOR`, `VERIFY_ANCHOR`.
- [x] `GUARD` + `AUTO_GUARD`: cierra obstrucciones conocidas antes de cada paso.
- [x] Carpetas `automation_images/anchors` y `.../obstrucciones`; grabación con teclas `g`/`e`/`m`/`o`.
- [x] `winsdk` instalado; OCR español (`es-ES`/`es-MX`) probado leyendo `septiembre 2026`, días, `SALA`, `Continuar`, `Regresar`.
- [x] Acciones OCR: `CLICK_TEXT`, `CLICK_IF_TEXT`, `WAIT_TEXT`, `VERIFY_TEXT` (probadas: presente=EXITO, ausente=FALLO).
- [x] Flujo completo `reserva_csi.txt` (19 pasos) con anclas + OCR + color, validado.
- [x] `CLICK_AVAILABLE_COLOR`: detecta cajones amarillos y clickea con preferencia (derecha por defecto).
- [x] Anclas/obstrucciones generadas con `herramientas/preparar_anclas.py`: `check_seleccion.png` (match 1.0) y `cerrar_aviso_semana.png` (match 1.0 en banner / 0.76 sin él).
- [x] `SELECCIONAR_DIA`: espera a que el calendario muestre el día y hace doble click (o `auto` por semanas).
- [x] `DROPDOWN,x,y,RETRASO,opcion`: abre el campo y elige la opción por OCR (tipo de lugar, país, unidad, ubicación).
- [x] `SELECCIONAR_PARQUEO`: escribe el número, pulsa la lupa, verifica que aparezca el **checkbox naranja**; si no, borra y prueba el siguiente; marca, Continuar y exige la pantalla `¿Está todo bien?` para confirmar éxito.
- [x] Bucle **validado en vivo**: probó 41→40→39 y reservó el 39; otra corrida 39→…→35 y reservó el 35.
- [x] `Confirmar|exacto|boton`: distingue el botón del contenido del del nav (evita caer en el QR).
- [x] Flujo **`reserva_csi.txt` validado de punta a punta**: última corrida **20/20 pasos, 0 errores, 86 s** (39✗ → 38✗ → 37✓ → Continuar → Confirmar → "Se ha reservado!").
- [x] El bucle `SELECCIONAR_PARQUEO` solo pasa al siguiente número si el parqueo **no aparece o el checkbox no queda marcado**; al marcarse, sigue a Continuar/Confirmar.
- [x] `MARCAR_1DIA` (checkbox "1 Día") y `hay_marca_oscura` para verificar el check.
- [x] `MARCAR_1DIA` y `DROPDOWN` usan coordenadas del layout maximizado; `MAXIMIZE` garantiza que sean estables.
- [x] Detector de bloqueo (`esta_bloqueado`) fiable + guard que **no envía entrada** si la estación está bloqueada.
- [x] Motor separado de la calibración: `config.py` genérico + `ajustes.py` (por app).
- [x] `LICENSE` (MIT), `ejemplos/` (genéricos y anonimizados), README reescrito, `COMO_EJECUTAR.md` y CLI `run`/`validate`.
- [x] Directorio base apuntando al propio proyecto; capturas `Config` copiadas a `automation_images/Config` (no versionadas).

## Hallazgos técnicos (importante)

- **UI Automation no sirve aquí:** el canvas de Power Apps no expone árbol
  accesible (solo 14 nodos del shell). Se convalidó con `uia_dump.ps1`.
  Por eso la vía robusta es **visión por computadora**.
- OCR nativo de Windows vía `winsdk` (instalado). Idiomas `es-ES`/`es-MX`.
- `pyautogui` no inyecta clicks en el escritorio seguro: la estación debe estar
  **desbloqueada** para que la reserva funcione.
- El canvas escala con el tamaño de la ventana → **siempre `MAXIMIZE` antes de
  buscar anclas** para tener un layout estable y comparable.
- `pyautogui.screenshot()` captura solo el monitor primario (la app vive en 1920x1080).

> Estado de testeo: PC **desbloqueado** y con resolución/zoom **fijos**. El modo
> bloqueado queda pendiente (ver abajo).

## Flujo de reserva (completo)

Capturas en `automation_images\Config` (`paso1..paso13`, `ERROR_...`, `menu*.png`):

1. **Agendar** (nav inferior `+`).
2. **Calendario** → doble clic en el día. Semana equivocada = banner rojo (se cierra con `GUARD`).
3. **Tipo de lugar** = `PARQUEO` (dropdown; por defecto `SALA`).
4. **Duración** = `1 Día` (checkbox) + `Continuar` (horario 8:00–17:00).
5. **Seleccione un parqueo** (dropdowns Guatemala/CSI/CSI, temporizador, "N disponibles", recargar ↻).
6. **Mapa lateral**: clic en el sector (cuadro rojo).
7. **Mapa PARQUEO PRADERA**: `CLICK_AVAILABLE_COLOR` sobre amarillos (leyenda: amarillo=disponible, verde=seleccionado, azul=no disponible, rojo=reservado).
8. **Check superior derecho** (`check_seleccion.png`).
9. **¿Está todo bien?** → `Confirmar`.
10. **"Reservando Día / Por favor espere..."**.
11. **"Registro Exitoso / Se ha reservado!"** (espera final).

Pendiente de ajuste en vivo (flujo `reserva_csi.txt`):

- [ ] Número de **día** a reservar (variable; hoy `11|exacto|doble`).
- [ ] Confirmar que `CLICK_TEXT "1 Día"` alterna el checkbox (si no, crear ancla del checkbox).
- [ ] **Coordenadas del mapa lateral** (paso 6): hoy `CLICK,970,240`; calibrar en vivo.
- [ ] Verificar región de `CLICK_AVAILABLE_COLOR` según el layout maximizado.
- [ ] Estrategia cuando **"0 disponibles"** o "no se encontró disponibilidad" (probablemente pasar a otra fecha).
- [ ] Comportamiento ante banner rojo: ¿cerrar y reintentar otra semana?

## Fase 3 — Programación y modo bloqueado

- [ ] **Modo PC BLOQUEADO (investigar y decidir).**
      `pyautogui` no inyecta clicks en el escritorio seguro de Windows; con la
      estación bloqueada los pasos de imagen/click no llegan a la app. Opciones a
      evaluar:
        - [ ] Dejar la sesión desbloqueada con política local de "no bloquear" (requiere permiso de TI).
        - [ ] Desbloqueo automático: **descartado** (requiere credenciales).
        - [ ] Tarea programada con "ejecutar solo cuando el usuario haya iniciado sesión".
        - [ ] Confirmar si la app/ventana realmente queda accesible con la pantalla apagada vs. bloqueada.
- [ ] **Disparador sin auto-arranque por política.**
      La PC no puede iniciar el script sola. Alternativas:
        - [ ] Dejar el proceso corriendo desde temprano con `WAIT_UNTIL` (opción más simple, sin admin).
        - [ ] Task Scheduler a nivel usuario (validar si la política lo permite; pedir confirmación).
        - [ ] Disparo externo (Flipper Zero) como respaldo.
- [ ] **`--wait-until HH:MM`** en `main.py`: arrancar el script y no hacer nada hasta la hora.
- [ ] **`ReservarParqueo.bat`** para lanzar el flujo con doble clic / dejar en espera.
- [ ] Verificar wake lock en una espera larga real (p. ej. de 23:00 a 00:02).
- [ ] Reintento del **flujo completo** (no solo por acción) si falla la reserva.

## Fase 4 — Web (opcional)

- [ ] Prototipo Playwright: abrir la URL del canvas app y fijar tamaño/posición de ventana.
      Nota: un canvas de Power Apps **no expone DOM estándar**; los clics seguirían
      siendo por imagen/coordenadas. Solo ayuda a estandarizar la ventana.
- [ ] Comparar estabilidad web vs. app de escritorio y decidir.

## Robustez / mejoras

- [ ] `CLICK_NEXT_DATE`: color de "disponible" configurable y soporte de tema oscuro/zoom.
- [ ] Conciencia de DPI/escalado (evitar desalineación si cambia la resolución).
- [ ] Grabar `LAUNCH` / `FOCUS_WINDOW` / `PASTE` desde el recorder (teclas nuevas en el menú de grabación).
- [ ] Rotación/limpieza automática de `automation_images/debug` (hay muchos logs y PNG acumulados).
- [ ] Revisar `onlypark.txt` línea final (`shutdown /s /t 0`): decidir si se conserva.

## PC bloqueado / keep-awake (pendiente)

- [ ] Confirmar si el bloqueo nocturno es por inactividad o por política de TI.
- [ ] Probar **keep-awake** (micro-movimiento de ratón cada ~45 s) si es por inactividad.
- [ ] Si la política fuerza el bloqueo: pedir **excepción de TI** o correr en un equipo siempre desbloqueado.
- [ ] Nunca teclear credenciales ni tocar el escritorio seguro.

## Decisiones registradas

- Preferencia: si la vía web resulta más estable, migrar; mientras, pulir escritorio.
- La espera debe seguir siendo genérica: "tras este paso, esperar N segundos **o** hasta cierta hora".
- El modo "sin click al iniciar" = empezar con `LAUNCH` + `WAIT_FOR_IMAGE`.
