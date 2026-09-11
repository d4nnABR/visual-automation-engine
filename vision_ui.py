import os
import time
import ctypes
import random
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import keyboard
from utils import antirrebote

ESCALAS_DEFECTO = [1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15, 0.8, 1.2, 0.75, 1.25]

TITULO_VENTANA_DEFECTO = "Power Apps"

_SW_RESTORE = 9
_SW_MAXIMIZE = 3


def _capturar(region=None):
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def encontrar_plantilla(ruta_plantilla, region=None, confianza=0.8, escalas=None):
    """
    Busca una imagen de referencia en la pantalla a varias escalas (robusto a
    cambios de DPI/zoom). Devuelve dict con x, y (centro absoluto), confianza,
    escala y tamaño; o None si no se encuentra.
    """
    if not os.path.exists(ruta_plantilla):
        raise FileNotFoundError(f"Plantilla no encontrada: {ruta_plantilla}")

    pantalla = _capturar(region)
    plantilla = cv2.imread(ruta_plantilla, cv2.IMREAD_COLOR)
    if plantilla is None or pantalla is None:
        return None

    alto_p, ancho_p = pantalla.shape[:2]
    mejor = None

    for escala in (escalas or ESCALAS_DEFECTO):
        ancho = int(plantilla.shape[1] * escala)
        alto = int(plantilla.shape[0] * escala)
        if ancho < 5 or alto < 5 or ancho > ancho_p or alto > alto_p:
            continue

        interpolacion = cv2.INTER_AREA if escala < 1 else cv2.INTER_LINEAR
        plantilla_esc = cv2.resize(plantilla, (ancho, alto), interpolation=interpolacion)

        resultado = cv2.matchTemplate(pantalla, plantilla_esc, cv2.TM_CCOEFF_NORMED)
        _, max_valor, _, max_loc = cv2.minMaxLoc(resultado)

        if max_valor >= confianza and (mejor is None or max_valor > mejor["confianza"]):
            cx = max_loc[0] + ancho // 2
            cy = max_loc[1] + alto // 2
            if region:
                cx += region[0]
                cy += region[1]
            mejor = {
                "confianza": float(max_valor),
                "x": int(cx),
                "y": int(cy),
                "escala": float(escala),
                "w": int(ancho),
                "h": int(alto),
                "region": (max_loc[0], max_loc[1], ancho, alto),
            }

    return mejor


def existe_plantilla(ruta_plantilla, region=None, confianza=0.8, escalas=None):
    return encontrar_plantilla(ruta_plantilla, region, confianza, escalas) is not None


def esperar_plantilla(ruta_plantilla, region=None, confianza=0.8, escalas=None,
                      tiempo_limite=30, intervalo=0.4, logger=None):
    inicio = time.time()
    while time.time() - inicio < tiempo_limite:
        if keyboard.is_pressed("esc"):
            antirrebote("esc")
            raise KeyboardInterrupt("Cancelado por usuario")
        hallado = encontrar_plantilla(ruta_plantilla, region, confianza, escalas)
        if hallado:
            return hallado
        time.sleep(intervalo)
    return None


def click_plantilla(ruta_plantilla, region=None, confianza=0.8, escalas=None,
                    doble=False, offset=(0, 0), logger=None, obligatorio=True):
    hallado = encontrar_plantilla(ruta_plantilla, region, confianza, escalas)
    if not hallado:
        if logger:
            logger.registrar(f"Ancla no encontrada: {os.path.basename(ruta_plantilla)}", "WARNING")
        if obligatorio:
            raise RuntimeError(f"Ancla no encontrada: {ruta_plantilla}")
        return None

    x = hallado["x"] + offset[0]
    y = hallado["y"] + offset[1]
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()
    if doble:
        time.sleep(0.15)
        pyautogui.click()

    if logger:
        logger.registrar(
            f"Click en ancla '{os.path.basename(ruta_plantilla)}' "
            f"({x}, {y}) conf={hallado['confianza']:.2f} escala={hallado['escala']}"
        )
    return hallado


def hay_marca_oscura(region, minimo=8, umbral=130):
    imagen = _capturar(region)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    return int((gris < umbral).sum()) >= minimo


def hay_color_naranja(region, minimo=15):
    imagen = _capturar(region)
    b, g, r = cv2.split(imagen)
    mascara = (
        (r.astype(int) > 200) & (g.astype(int) > 100)
        & (g.astype(int) < 215) & (b.astype(int) < 95)
    )
    return int(mascara.sum()) >= minimo


def encontrar_bloques_amarillos(region, area_min=300, area_max=4000):
    imagen = _capturar(region)
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, (20, 120, 180), (35, 255, 255))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    n, _, stats, centros = cv2.connectedComponentsWithStats(mascara, 8)
    off_x = region[0] if region else 0
    off_y = region[1] if region else 0

    bloques = []
    for i in range(1, n):
        ancho, alto, area = stats[i, 2], stats[i, 3], stats[i, 4]
        if area_min <= area <= area_max:
            bloques.append({
                "x": int(centros[i][0]) + off_x,
                "y": int(centros[i][1]) + off_y,
                "w": int(ancho),
                "h": int(alto),
                "area": int(area),
            })
    return bloques


def click_amarillo(region, preferencia="derecha", area_min=300, area_max=4000,
                   logger=None, obligatorio=True):
    """
    Clickea un cajón DISPONIBLE (amarillo) dentro de `region`.
    preferencia: derecha | izquierda | arriba | abajo | aleatorio.
    `derecha` prioriza los números altos del mapa (p. ej. 39, 38, ...).
    """
    bloques = encontrar_bloques_amarillos(region, area_min, area_max)
    if not bloques:
        if logger:
            logger.registrar(f"No hay cajones amarillos en region {region}", "WARNING")
        if obligatorio:
            raise RuntimeError("No hay cajones amarillos disponibles")
        return None

    if preferencia == "izquierda":
        bloques.sort(key=lambda b: b["x"])
    elif preferencia == "arriba":
        bloques.sort(key=lambda b: b["y"])
    elif preferencia == "abajo":
        bloques.sort(key=lambda b: -b["y"])
    elif preferencia == "aleatorio":
        random.shuffle(bloques)
    else:
        bloques.sort(key=lambda b: -b["x"])

    elegido = bloques[0]
    pyautogui.moveTo(elegido["x"], elegido["y"], duration=0.3)
    pyautogui.click()
    if logger:
        logger.registrar(
            f"Click en cajón disponible ({elegido['x']}, {elegido['y']}) "
            f"preferencia={preferencia} total={len(bloques)}"
        )
    return elegido


def _hwnd_ventana(titulo):
    coincidencias = [v for v in gw.getAllWindows() if titulo.lower() in (v.title or "").lower()]
    if not coincidencias:
        return None, None
    ventana = coincidencias[0]
    hwnd = getattr(ventana, "_hWnd", None)
    return ventana, hwnd


def maximizar_ventana(titulo=TITULO_VENTANA_DEFECTO, logger=None):
    """
    Maximiza la ventana indicada manipulando su handle (HWND). Determinista:
    no depende de qué ventana tenga el foco (evita enganches a media pantalla).
    """
    ventana, hwnd = _hwnd_ventana(titulo)
    if not hwnd:
        if logger:
            logger.registrar(f"No se encontró ventana '{titulo}' para maximizar", "WARNING")
        return False

    try:
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, _SW_RESTORE)
        time.sleep(0.2)
        user32.ShowWindow(hwnd, _SW_MAXIMIZE)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    except Exception as e:
        if logger:
            logger.registrar(f"No se pudo maximizar '{titulo}': {e}", "WARNING")
        return False

    if logger:
        logger.registrar(f"Ventana maximizada (HWND {hwnd}): '{ventana.title}'")
    return True


def cerrar_obstrucciones(directorio_obstrucciones, confianza=0.85, escalas=None, logger=None):
    """
    Escanea imágenes en `directorio_obstrucciones`. Cada plantilla representa un
    botón de cierre (X) o un aviso; al encontrarlo hace click en su centro.
    Devuelve la lista de archivos cerrados.
    """
    if not os.path.isdir(directorio_obstrucciones):
        return []

    cerrados = []
    for nombre in sorted(os.listdir(directorio_obstrucciones)):
        if not nombre.lower().endswith(".png"):
            continue
        ruta = os.path.join(directorio_obstrucciones, nombre)
        hallado = encontrar_plantilla(ruta, confianza=confianza, escalas=escalas)
        if hallado:
            pyautogui.moveTo(hallado["x"], hallado["y"], duration=0.2)
            pyautogui.click()
            time.sleep(0.3)
            cerrados.append(nombre)
            if logger:
                logger.registrar(
                    f"Obstrucción cerrada: {nombre} ({hallado['x']}, {hallado['y']})"
                )
    return cerrados
