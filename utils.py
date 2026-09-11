import os
import time
import ctypes
import pyautogui
import keyboard
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
# EVITAR QUE EL PC SE DUERMA DURANTE UNA ESPERA
# ──────────────────────────────────────────────

_ES_CONTINUOUS = 0x80000000
_ES_SYSTEM_REQUIRED = 0x00000001
_ES_DISPLAY_REQUIRED = 0x00000002


def mantener_pc_despierto(activar=True):
    """
    Impide que Windows suspenda el sistema o apague la pantalla mientras
    se espera una hora concreta. Devuelve True si se pudo aplicar.
    """
    try:
        if activar:
            flags = _ES_CONTINUOUS | _ES_SYSTEM_REQUIRED | _ES_DISPLAY_REQUIRED
        else:
            flags = _ES_CONTINUOUS
        ctypes.windll.kernel32.SetThreadExecutionState(flags)
        return True
    except Exception:
        return False


def _logonui_activo():
    import subprocess
    try:
        salida = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq LogonUI.exe"],
            capture_output=True, text=True, creationflags=0x08000000,
        )
        return "LogonUI.exe" in salida.stdout
    except Exception:
        return False


def esta_bloqueado():
    """
    True si la estación está bloqueada. Señales en este equipo:
    escritorio de entrada no accesible, foreground = lock screen
    (Windows.UI.Core.CoreWindow) o LogonUI activo.
    """
    try:
        user32 = ctypes.windll.user32
        escritorio = user32.OpenInputDesktop(0, False, 0x0100)
        if not escritorio:
            return True
        try:
            buf = ctypes.create_unicode_buffer(256)
            need = ctypes.c_ulong(0)
            user32.GetUserObjectInformationW(escritorio, 2, buf, 512, ctypes.byref(need))
            if buf.value and buf.value.lower() not in ("default", "input"):
                return True
        finally:
            user32.CloseDesktop(escritorio)

        hwnd = user32.GetForegroundWindow()
        if hwnd:
            clase = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, clase, 256)
            if clase.value.lower() == "windows.ui.core.corewindow":
                return True
        elif _logonui_activo():
            return True

        return _logonui_activo()
    except Exception:
        return None


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


def esperar_hasta_hora(hora_objetivo_hhmmss, ventana_max_horas=12, logger=None):
    """
    Espera hasta la hora local indicada (HH:MM:SS), calculando la PRÓXIMA
    ocurrencia. Esto permite cruzar medianoche: si son las 23:58 y el objetivo
    es 00:02:05, espera los minutos que faltan (no los asume como "ya pasó").

    Si la hora ya pasó hoy y la próxima ocurrencia queda a más de
    `ventana_max_horas`, se considera que el objetivo quedó atrás (ej. el
    script corrió a las 00:10 con objetivo 00:02) y NO se espera 24 horas.

    Permite cancelar con ESC y mantiene el PC despierto durante la espera.
    """
    ahora = datetime.now()
    objetivo = datetime.strptime(hora_objetivo_hhmmss, "%H:%M:%S").replace(
        year=ahora.year, month=ahora.month, day=ahora.day
    )
    if objetivo <= ahora:
        objetivo += timedelta(days=1)

    restante = (objetivo - ahora).total_seconds()
    if restante > ventana_max_horas * 3600:
        if logger:
            logger.registrar(
                f"Hora objetivo {hora_objetivo_hhmmss} ya pasó hoy y la próxima "
                f"ocurre en {restante/3600:.1f}h (> {ventana_max_horas}h). No se espera.",
                "WARNING",
            )
        return

    if logger:
        logger.registrar(
            f"Esperando hasta {objetivo.strftime('%Y-%m-%d %H:%M:%S')} "
            f"({restante:.0f}s en el futuro)"
        )

    mantener_pc_despierto(True)
    try:
        while True:
            if keyboard.is_pressed("esc"):
                antirrebote("esc")
                raise KeyboardInterrupt("Cancelado por usuario")
            restante = (objetivo - datetime.now()).total_seconds()
            if restante <= 0:
                return
            time.sleep(min(0.25, restante))
    finally:
        mantener_pc_despierto(False)


def crear_directorios(directorio_imagenes, directorio_debug):
    if not os.path.exists(directorio_imagenes):
        os.makedirs(directorio_imagenes)
        print(f"Directorio de imágenes creado: {directorio_imagenes}")
    if not os.path.exists(directorio_debug):
        os.makedirs(directorio_debug)
        print(f"Directorio de debug creado: {directorio_debug}")
