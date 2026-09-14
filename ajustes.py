"""
Ajustes de la APLICACIÓN DE EJEMPLO (calibración de pantalla y reglas propias).

Este archivo es lo único que depende del caso concreto. Si adaptas el motor a
otra app, cambia aquí los valores o crea tu propio `ajustes.py`.

Notas:
- Las coordenadas están calibradas a la ventana MAXIMIZADA en 1920x1080 al 100%.
  Si cambias resolución, zoom o tamaño de ventana, hay que recalibrarlas.
- `BUSCAR_PARQUEO` describe el campo de búsqueda de la pantalla de ejemplo.
- `RESERVA` es la regla de "semanas alternas" del ejemplo (opcional): puedes
  ignorarla si tu app no la usa.
"""

# --- Regla de fecha a reservar ---
# modo "anticipacion": la fecha que la app habilita hoy = hoy + dias_anticipacion
#   (14/09 -> 22/09, 15/09 -> 23/09, ...).
# modo "dia_semana": el primer `dia_semana_objetivo` (0=lunes..6=domingo) en
#   semana habilitada; usa `fecha_ancla_semana_on` (un lunes de semana on).
RESERVA = {
    "modo": "anticipacion",
    "dias_anticipacion": 8,
    "fecha_ancla_semana_on": "2026-09-07",
    "dia_semana_objetivo": 1,
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
