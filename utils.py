import os
import time
import pyautogui
import keyboard
from datetime import datetime


def obtener_marca_tiempo():
    """Retorna timestamp en formato: AAAAMMDD_HHMMSS"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def antirrebote(tecla, tiempo_espera=0.05):
    while keyboard.is_pressed(tecla):
        time.sleep(tiempo_espera)


def parse_retraso_y_hora_siguiente(retraso_s):
    """
    Acepta:
    - "1.5"
    - "1.5@14:23:10" (esperar por reloj hasta HH:MM:SS antes del siguiente paso)
    """
    if retraso_s is None:
        return 1.0, None

    txt = str(retraso_s).strip()
    if not txt:
        return 1.0, None

    if "@" not in txt:
        return float(txt), None

    retraso_parte, hora_parte = txt.split("@", 1)
    retraso_parte = retraso_parte.strip()
    hora_parte = hora_parte.strip()

    retraso = float(retraso_parte) if retraso_parte else 0.0
    if not hora_parte:
        return retraso, None

    try:
        hora_norm = datetime.strptime(hora_parte, "%H:%M:%S").strftime("%H:%M:%S")
    except ValueError:
        raise ValueError(f"Hora inválida '{hora_parte}'. Usa formato HH:MM:SS (ej: 14:23:10)")

    return retraso, hora_norm


def esperar_hasta_hora(hora_objetivo_hhmmss):
    """
    Espera hasta la hora local indicada (HH:MM:SS).
    Si la hora ya pasó, NO espera. Permite cancelar con ESC.
    """
    ahora = datetime.now()
    objetivo_hoy = datetime.strptime(hora_objetivo_hhmmss, "%H:%M:%S").replace(
        year=ahora.year, month=ahora.month, day=ahora.day
    )
    if objetivo_hoy <= ahora:
        return
    objetivo = objetivo_hoy

    while True:
        if keyboard.is_pressed("esc"):
            antirrebote("esc")
            raise KeyboardInterrupt("Cancelado por usuario")
        restante = (objetivo - datetime.now()).total_seconds()
        if restante <= 0:
            return
        time.sleep(min(0.25, restante))


def crear_directorios(directorio_imagenes, directorio_debug):
    if not os.path.exists(directorio_imagenes):
        os.makedirs(directorio_imagenes)
        print(f"Directorio de imágenes creado: {directorio_imagenes}")
    if not os.path.exists(directorio_debug):
        os.makedirs(directorio_debug)
        print(f"Directorio de debug creado: {directorio_debug}")
