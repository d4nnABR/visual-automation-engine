import os
import time
import json
import pyautogui
import keyboard
from utils import antirrebote, esperar_hasta_hora
from vision import (
    esperar_imagen,
    encontrar_y_clickear_proxima_fecha,
    encontrar_y_clickear_amarillo_aleatorio,
)

# Resultado especial para señalar fallo sin lanzar excepción
FALLO = "FALLO"
EXITO = "EXITO"


def _esperar_retraso(hora_siguiente, retraso, logger):
    if hora_siguiente:
        logger.registrar(f"Esperando hasta hora para siguiente paso: {hora_siguiente}")
        esperar_hasta_hora(hora_siguiente)
    else:
        time.sleep(retraso)


def ejecutar_accion(accion, x, y, retraso, carga_util, hora_siguiente, directorio_imagenes, logger):
    """
    Ejecuta una acción individual.
    Retorna EXITO, FALLO, o lanza excepción crítica / KeyboardInterrupt.
    """
    if accion == "CLICK":
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click()
        logger.registrar(f"Click en ({x}, {y})")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "TYPE":
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.write(carga_util)
        logger.registrar(f"Texto escrito en ({x}, {y}): {carga_util[:20]}...")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "TYPE_RAW":
        pyautogui.write(carga_util)
        logger.registrar(f"Texto escrito (sin click): {carga_util[:20]}...")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "PRESS":
        nombre_tecla = carga_util.strip()
        if nombre_tecla:
            pyautogui.press(nombre_tecla)
            logger.registrar(f"Tecla presionada: {nombre_tecla}")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "HOTKEY":
        teclas = [k.strip() for k in carga_util.strip().split("+") if k.strip()]
        if teclas:
            pyautogui.hotkey(*teclas)
            logger.registrar(f"Hotkey ejecutado: {carga_util.strip()}")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "KEYEVENTS":
        _reproducir_eventos_teclas_json(carga_util or "[]")
        logger.registrar("Secuencia de teclas reproducida")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "CLICK_NEXT_DATE":
        partes = carga_util.split("|")
        if len(partes) != 2:
            raise ValueError("Formato inválido para CLICK_NEXT_DATE")
        region = (x, y, int(partes[0]), int(partes[1]))
        if not encontrar_y_clickear_proxima_fecha(region, retraso, logger):
            return FALLO

    elif accion == "CLICK_RANDOM_YELLOW":
        partes = carga_util.split("|")
        if len(partes) != 2:
            raise ValueError("Formato inválido para CLICK_RANDOM_YELLOW")
        region = (x, y, int(partes[0]), int(partes[1]))
        if not encontrar_y_clickear_amarillo_aleatorio(region, retraso, logger):
            return FALLO

    elif accion == "CLICK_WHEN_IMAGE":
        nombre_imagen = carga_util.strip()
        ruta_imagen = os.path.join(directorio_imagenes, nombre_imagen)
        if not os.path.exists(ruta_imagen):
            raise FileNotFoundError(f"Imagen no encontrada: {ruta_imagen}")

        logger.registrar(f"Esperando imagen: {nombre_imagen}")
        encontrado = False
        inicio_espera = time.time()

        while time.time() - inicio_espera < 60:
            if keyboard.is_pressed("esc"):
                antirrebote("esc")
                raise KeyboardInterrupt("Cancelado por usuario")
            try:
                if pyautogui.locateOnScreen(ruta_imagen, confidence=0.8):
                    encontrado = True
                    break
            except pyautogui.ImageNotFoundException:
                pass
            except Exception as e:
                if not logger.advertencia_opencv_mostrada:
                    logger.registrar(f"Advertencia OpenCV: {e}", "WARNING")
                    logger.advertencia_opencv_mostrada = True
            time.sleep(0.5)

        if not encontrado:
            return FALLO

        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click()
        logger.registrar(f"Imagen encontrada y click realizado: {nombre_imagen}")
        _esperar_retraso(hora_siguiente, retraso, logger)
      
    elif accion == "WAIT_FOR_IMAGE":
        nombre_imagen = carga_util.strip()
        ruta_imagen = os.path.join(directorio_imagenes, nombre_imagen)
        if not os.path.exists(ruta_imagen):
            raise FileNotFoundError(f"Imagen no encontrada: {ruta_imagen}")

        # Espera la imagen — respeta el timeout completo
        ubicacion = esperar_imagen(ruta_imagen, tiempo_limite=retraso, logger=logger)

        if not ubicacion:
            logger.registrar(f"Imagen '{nombre_imagen}' no apareció en {retraso}s", "WARNING")
            return FALLO

        logger.registrar(f"Imagen encontrada: {nombre_imagen}")

        if hora_siguiente:
            logger.registrar(f"Imagen encontrada — esperando hora: {hora_siguiente}")
            esperar_hasta_hora(hora_siguiente)
        elif accion == "WAIT_FOR_IMAGE":
            nombre_imagen = carga_util.strip()
            ruta_imagen = os.path.join(directorio_imagenes, nombre_imagen)
            if not os.path.exists(ruta_imagen):
                raise FileNotFoundError(f"Imagen no encontrada: {ruta_imagen}")

            ubicacion = esperar_imagen(ruta_imagen, tiempo_limite=retraso, logger=logger)
            if not ubicacion:
                logger.registrar(f"Imagen '{nombre_imagen}' no apareció en {retraso}s", "WARNING")
                return FALLO
            logger.registrar(f"Imagen encontrada: {nombre_imagen}")
            if hora_siguiente:
                logger.registrar(f"Imagen encontrada — esperando hora: {hora_siguiente}")
                esperar_hasta_hora(hora_siguiente)

    else:
        raise ValueError(f"Acción no soportada: {accion}")

    return EXITO  
       


def _reproducir_eventos_teclas_json(eventos_json):
    import keyboard as kb
    datos = json.loads(eventos_json)
    eventos = [
        kb.KeyboardEvent(
            event_type=d["event_type"],
            scan_code=d["scan_code"],
            name=d["name"],
            time=d["time"],
            device=d.get("device"),
            is_keypad=d.get("is_keypad"),
        )
        for d in datos
    ]
    kb.play(eventos)


def grabar_eventos_teclas_hasta_f12():
    print("Grabación de teclado iniciada.")
    print("Presiona la secuencia de teclas que quieres grabar.")
    print("Para terminar y guardar, presiona F12.")
    grabacion = keyboard.record(until="f12")
    eventos = [
        {
            "event_type": e.event_type,
            "scan_code": e.scan_code,
            "name": e.name,
            "time": e.time,
            "device": getattr(e, "device", None),
            "is_keypad": getattr(e, "is_keypad", None),
        }
        for e in grabacion
        if getattr(e, "name", None) != "f12"
    ]
    print("Grabación finalizada.")
    return json.dumps(eventos, ensure_ascii=False)
