# Pendientes — VisualPilot

El historial de lo hecho está en git y en el handoff de Obsidian
(`Proyectos\Claude Memory\VisualPilot`). Aquí solo lo que falta.

## Reserva

- [ ] Estrategia ante **"0 disponibles"** o ninguno de la prioridad libre
      (hoy el flujo registra error y termina).
- [ ] Reintento del **flujo completo** si falla la reserva (no solo por acción).
- [ ] Verificar en vivo el keep-awake durante una espera larga real
      (p. ej. 23:58 → 00:02).

## PC bloqueado

`pyautogui` no puede enviar clicks con la estación bloqueada.

- [ ] Confirmar si el bloqueo nocturno es por inactividad o por política de TI.
- [ ] Si es por política: pedir excepción de TI o correr en un equipo siempre
      desbloqueado.
- [ ] Nunca teclear credenciales ni tocar el escritorio seguro (descartado).

## Robustez

- [ ] Conciencia de DPI/escalado: hoy las coordenadas asumen 1920x1080 al 100 %.
- [ ] Calendario: si Power Apps cambia el diseño, recalibrar `CALENDARIO` en
      `visualpilot\ajustes.py`.
- [ ] Rotar `automation_images\debug\reserva_bat.log` (crece sin límite; la
      opción "Limpiar debug" no lo toca).

## Opcional

- [ ] Prototipo web (Playwright) solo para fijar tamaño de ventana; el canvas de
      Power Apps no expone DOM, los clics seguirían siendo por imagen/OCR.
