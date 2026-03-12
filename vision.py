import time
import random
import pyautogui
import keyboard
from utils import antirrebote


def seleccionar_region():
    print("Mueve el mouse a la esquina superior izquierda y presiona Enter.")
    keyboard.wait("enter")
    inicio_x, inicio_y = pyautogui.position()
    antirrebote("enter")
    print(f"Punto inicial: ({inicio_x}, {inicio_y})")

    print("Mueve el mouse a la esquina inferior derecha y presiona Enter.")
    keyboard.wait("enter")
    fin_x, fin_y = pyautogui.position()
    antirrebote("enter")
    print(f"Punto final: ({fin_x}, {fin_y})")

    ancho = abs(fin_x - inicio_x)
    alto = abs(fin_y - inicio_y)
    return (min(inicio_x, fin_x), min(inicio_y, fin_y), ancho, alto)


def capturar_imagen_referencia(nombre_paso, directorio_imagenes):
    print(f"Posiciona la pantalla para capturar la imagen de referencia para: {nombre_paso}")
    print("Presiona Enter para capturar la pantalla completa o r para seleccionar región...")
    import os

    while True:
        if keyboard.is_pressed("enter"):
            antirrebote("enter")
            captura = pyautogui.screenshot()
            ruta = os.path.join(directorio_imagenes, f"{nombre_paso}_reference.png")
            captura.save(ruta)
            print(f"Imagen de referencia guardada: {ruta}")
            return ruta

        if keyboard.is_pressed("r"):
            antirrebote("r")
            region = seleccionar_region()
            if region:
                captura = pyautogui.screenshot(region=region)
                ruta = os.path.join(directorio_imagenes, f"{nombre_paso}_reference.png")
                captura.save(ruta)
                print(f"Imagen de referencia guardada: {ruta}")
                return ruta

        time.sleep(0.1)


def esperar_imagen(ruta_imagen, tiempo_limite=30, confianza=0.8, logger=None):
    import os
    print(f"Esperando imagen: {os.path.basename(ruta_imagen)}")
    hora_inicio = time.time()

    while time.time() - hora_inicio < tiempo_limite:
        try:
            ubicacion = pyautogui.locateOnScreen(ruta_imagen, confidence=confianza)
            if ubicacion:
                print(f"Imagen encontrada en: {ubicacion}")
                return ubicacion
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            if logger and not logger.advertencia_opencv_mostrada:
                print(f"Advertencia (solo se muestra una vez): {e}")
                logger.advertencia_opencv_mostrada = True
        time.sleep(0.5)

    print(f"Timeout: No se encontró la imagen después de {tiempo_limite} segundos")
    return None


def encontrar_y_clickear_proxima_fecha(region_calendario, retraso, logger=None):
    """Encuentra la fecha más próxima habilitada y hace doble click."""
    if logger:
        logger.registrar(f"Buscando fecha disponible en región: {region_calendario}")

    captura = pyautogui.screenshot(region=region_calendario)
    img = captura.convert("RGB")
    pixeles = img.load()
    ancho, alto = img.size

    ancho_celda = ancho / 7
    alto_celda = alto / 6

    dias_disponibles = []
    colores_encontrados = []

    for fila in range(6):
        for columna in range(7):
            cx = int(columna * ancho_celda + ancho_celda / 2)
            cy = int(fila * alto_celda + alto_celda / 2)
            if 0 <= cx < ancho and 0 <= cy < alto:
                r, g, b = pixeles[cx, cy]
                colores_encontrados.append((r, g, b))
                es_gris = (
                    150 < r < 240 and 150 < g < 240 and 150 < b < 240
                    and abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20
                )
                if not es_gris:
                    abs_x = region_calendario[0] + cx
                    abs_y = region_calendario[1] + cy
                    dias_disponibles.append((abs_x, abs_y))
                    if logger:
                        logger.registrar(f"Fecha encontrada fila {fila}, col {columna}: RGB({r},{g},{b})")

    if logger:
        logger.registrar(f"Muestra de colores (primeros 5): {colores_encontrados[:5]}")
        logger.registrar(f"Total fechas disponibles: {len(dias_disponibles)}")

    if not dias_disponibles:
        if logger:
            logger.registrar("No se encontraron fechas habilitadas", "WARNING")
            logger.registrar(f"Todos los colores: {colores_encontrados}", "WARNING")
        return False

    ultimo_dia = dias_disponibles[-1]
    pyautogui.moveTo(ultimo_dia[0], ultimo_dia[1], duration=0.3)
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(retraso)
    if logger:
        logger.registrar(f"Doble click en fecha próxima: ({ultimo_dia[0]}, {ultimo_dia[1]})")
    return True


def encontrar_y_clickear_amarillo_aleatorio(region, retraso, logger=None):
    """Encuentra todos los cuadros amarillos y clickea uno al azar."""
    if logger:
        logger.registrar(f"Buscando cuadros amarillos en región: {region}")

    captura = pyautogui.screenshot(region=region)
    img = captura.convert("RGB")
    pixeles = img.load()
    ancho, alto = img.size

    pixeles_amarillos = [
        (x, y)
        for x in range(0, ancho, 5)
        for y in range(0, alto, 5)
        if pixeles[x, y][0] > 200 and pixeles[x, y][1] > 200 and pixeles[x, y][2] < 100
    ]

    if not pixeles_amarillos:
        if logger:
            logger.registrar("No se encontraron cuadros amarillos", "WARNING")
        return False

    bloques_amarillos = []
    usados = set()

    for px, py in pixeles_amarillos:
        if (px, py) in usados:
            continue
        bloque = []
        pila = [(px, py)]
        while pila and len(bloque) < 500:
            x, y = pila.pop()
            if (x, y) in usados or not (0 <= x < ancho and 0 <= y < alto):
                continue
            r, g, b = pixeles[x, y]
            if r > 200 and g > 200 and b < 100:
                usados.add((x, y))
                bloque.append((x, y))
                pila.extend([(x + 5, y), (x - 5, y), (x, y + 5), (x, y - 5)])

        if len(bloque) > 50:
            promedio_x = sum(p[0] for p in bloque) // len(bloque)
            promedio_y = sum(p[1] for p in bloque) // len(bloque)
            bloques_amarillos.append((promedio_x, promedio_y))

    if not bloques_amarillos:
        if logger:
            logger.registrar("No se encontraron bloques amarillos grandes", "WARNING")
        return False

    seleccionado = random.choice(bloques_amarillos)
    abs_x = region[0] + seleccionado[0]
    abs_y = region[1] + seleccionado[1]
    pyautogui.moveTo(abs_x, abs_y, duration=0.3)
    pyautogui.click()
    time.sleep(retraso)
    if logger:
        logger.registrar(f"Click en cuadro amarillo: ({abs_x}, {abs_y}). Total encontrados: {len(bloques_amarillos)}")
    return True
