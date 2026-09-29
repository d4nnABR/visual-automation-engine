"""
Ajustes de la APLICACIÓN DE EJEMPLO (calibración de pantalla y reglas propias).

Este archivo es lo único que depende del caso concreto. Si adaptas el motor a
otra app, cambia aquí los valores o crea tu propio `ajustes.py`.

Notas:
- Las coordenadas están calibradas a la ventana MAXIMIZADA en 1920x1080 al 100%.
  Si cambias resolución, zoom o tamaño de ventana, hay que recalibrarlas.
- `BUSCAR_PARQUEO` describe el campo de búsqueda de la pantalla de ejemplo.
- `RESERVA` son los VALORES POR DEFECTO de la reserva. Lo que se cambia desde
  el menú (opción "Configurar reserva") se guarda en `config_usuario.json` y
  tiene prioridad sobre esto.
"""

# --- Reserva (valores por defecto; editables desde el menú) ---
# hora_inicio: hora en que la app habilita la fecha; el flujo la usa como
#   {HORA_INICIO} en WAIT_UNTIL.
# modo "anticipacion": fecha a reservar = hoy + dias_anticipacion
#   (14/09 -> 22/09, 15/09 -> 23/09, ...).
# modo "dia_semana": el próximo `dia_semana_objetivo` (0=lunes..6=domingo).
# semanas_alternas: si es True, solo se reserva cuando la fecha cae en una
#   semana "sí" (lunes a domingo). `fecha_ancla_semana_on` es un lunes de semana
#   "sí"; desde ahí se alternan sí / no / sí...
# prioridad: números de parqueo en orden; el flujo la usa como {PRIORIDAD}.
RESERVA = {
    "hora_inicio": "00:02:00",
    "modo": "anticipacion",
    "dias_anticipacion": 8,
    "dia_semana_objetivo": 1,
    "semanas_alternas": False,
    "fecha_ancla_semana_on": "2026-09-07",
    "prioridad": "39,38,37,36,35,34,33,32,31,105,106,104",
}

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# --- Calibración de la pantalla de búsqueda de la app de ejemplo ---
BUSCAR_PARQUEO = {
    "campo_busqueda": "Buscar",
    "campo_x": 920,
    "campo_y": 388,
    "lupa_x": 1083,
    "lupa_y": 388,
    "checkbox_x": 1168,
    "checkbox_offset_y": 21,
    "espera_resultado": 2.0,
}

# Checkbox "1 Día" de la pantalla de ejemplo (layout maximizado)
DURACION_1DIA = (1050, 742)

# --- Calendario "Seleccione una fecha" (layout maximizado) ---
# Cuadrícula de 6 semanas x 7 días que empieza en domingo. El día se elige por
# posición de celda, no por OCR del número: los dígitos sueltos fallan en OCR y
# el mismo número aparece dos veces (p. ej. 7/sep en gris y 7/oct).
# `encabezado_y` es la Y del texto "septiembre 2026"; si el OCR lo encuentra a
# otra altura, toda la cuadrícula se desplaza lo mismo.
CALENDARIO = {
    "encabezado_y": 150,
    "col_x": [746, 818, 890, 961, 1033, 1105, 1176],
    "fila_y": [268, 324, 380, 437, 493, 549],
    "flecha_siguiente": (1185, 145),
    "medio_celda": 22,  # semilado de la zona donde se comprueba el naranja
}
