import os
import time
import asyncio
import tempfile
import pyautogui
import keyboard
from utils import antirrebote

try:
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.storage import StorageFile, FileAccessMode
    _OCR_DISPONIBLE = True
except Exception:
    _OCR_DISPONIBLE = False

IDIOMAS_PREFERIDOS = ["es-ES", "es-MX"]
_ENGINE = None


def _engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE
    for tag in IDIOMAS_PREFERIDOS:
        try:
            if OcrEngine.is_language_supported(Language(tag)):
                eng = OcrEngine.try_create_from_language(Language(tag))
                if eng:
                    _ENGINE = eng
                    return _ENGINE
        except Exception:
            pass
    _ENGINE = OcrEngine.try_create_from_user_profile_languages()
    return _ENGINE


async def _reconocer_archivo(ruta, engine):
    archivo = await StorageFile.get_file_from_path_async(ruta)
    stream = await archivo.open_async(FileAccessMode.READ)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    return await engine.recognize_async(bitmap)


def leer_texto(region=None):
    """Devuelve las líneas OCR con sus palabras y cajas (coords absolutas)."""
    if not _OCR_DISPONIBLE:
        raise RuntimeError("OCR no disponible: instala 'winsdk' (pip install winsdk)")

    imagen = pyautogui.screenshot(region=region)
    fd, ruta = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    imagen.save(ruta)

    try:
        engine = _engine()
        if engine is None:
            raise RuntimeError("No hay motor OCR para los idiomas del sistema")
        resultado = asyncio.new_event_loop().run_until_complete(
            _reconocer_archivo(ruta, engine)
        )
    finally:
        try:
            os.remove(ruta)
        except Exception:
            pass

    off_x = region[0] if region else 0
    off_y = region[1] if region else 0

    lineas = []
    for linea in resultado.lines:
        palabras = []
        for p in linea.words:
            caja = p.bounding_rect
            palabras.append({
                "texto": p.text,
                "x": int(caja.x) + off_x,
                "y": int(caja.y) + off_y,
                "w": int(caja.width),
                "h": int(caja.height),
            })
        lineas.append({"texto": linea.text, "palabras": palabras})
    return lineas


def _normalizar(s):
    return "".join(s.split()).lower()


def buscar_texto(texto, region=None, exacto=False, ignorar_mayus=True, max_y=None):
    objetivo = texto.lower() if ignorar_mayus else texto
    for linea in leer_texto(region):
        contenido = linea["texto"].lower() if ignorar_mayus else linea["texto"]
        if exacto:
            coincide = _normalizar(contenido) == _normalizar(objetivo)
        else:
            coincide = objetivo in contenido
        if coincide and linea["palabras"]:
            palabras = linea["palabras"]
            cy = sum(p["y"] + p["h"] // 2 for p in palabras) // len(palabras)
            if max_y is not None and cy > max_y:
                continue
            cx = sum(p["x"] + p["w"] // 2 for p in palabras) // len(palabras)
            return {"texto": linea["texto"], "x": cx, "y": cy, "palabras": palabras}
    return None


def click_texto(texto, region=None, exacto=False, doble=False, logger=None,
                obligatorio=True, max_y=None):
    hallado = buscar_texto(texto, region, exacto, max_y=max_y)
    if not hallado:
        if logger:
            logger.registrar(f"Texto no encontrado: '{texto}'", "WARNING")
        if obligatorio:
            raise RuntimeError(f"Texto no encontrado: '{texto}'")
        return None

    pyautogui.moveTo(hallado["x"], hallado["y"], duration=0.3)
    pyautogui.click()
    if doble:
        time.sleep(0.15)
        pyautogui.click()
    if logger:
        logger.registrar(f"Click en texto '{hallado['texto']}' ({hallado['x']}, {hallado['y']})")
    return hallado


def esperar_texto(texto, region=None, exacto=False, tiempo_limite=30, intervalo=0.5,
                  logger=None, max_y=None):
    inicio = time.time()
    while time.time() - inicio < tiempo_limite:
        if keyboard.is_pressed("esc"):
            antirrebote("esc")
            raise KeyboardInterrupt("Cancelado por usuario")
        hallado = buscar_texto(texto, region, exacto, max_y=max_y)
        if hallado:
            return hallado
        time.sleep(intervalo)
    return None
