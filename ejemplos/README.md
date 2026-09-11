# Ejemplos

Flujos de ejemplo del motor. Son genéricos: **no dependen de ninguna app en
particular**. Sustituye textos y coordenadas por los de tu aplicación.

- `ejemplo_simple.txt` — muestra todas las acciones básicas (click, escribir,
  hotkeys, anclas, OCR, flujo de error con `LABEL`/`GOTO`).
- `ejemplo_reserva.txt` — flujo tipo "reservar un recurso": elegir día, tipo,
  ubicación, buscar por número y confirmar.

## Cómo adaptarlo a tu app

1. **Crea tus imágenes de referencia** en `automation_images/anchors/` (recórtalas
   con el grabador del menú, tecla `g`) y las de cierre de avisos en
   `automation_images/obstrucciones/` (tecla `o`).
2. **Escribe tu `.txt`** usando el catálogo de acciones del `README` principal.
3. **Calibra** las coordenadas que uses (`config`/`ajustes.py`) a tu ventana
   MAXIMIZADA con la resolución/zoom fijos.
4. Ejecuta: `python main.py run mi_flujo.txt` (detén con **ESC**).

## Anonimización

Los ejemplos usan marcadores genéricos (`MiApp`, `PAIS`, `UNIDAD`, `UBICACION`,
`TIPO_RECURSO`, `Se ha reservado`). Reemplázalos por los textos reales de tu app.
