import os
import time
import json
import subprocess
import webbrowser
import pyautogui
import keyboard
import pyperclip
import pygetwindow as gw
from config import (
    CLICK_IF_IMAGE_TIMEOUT, UMBRAL_ANCHOR, MAX_Y_BOTON,
    get_directorio_anchors, get_directorio_obstrucciones,
)
from ajustes import BUSCAR_PARQUEO, DURACION_1DIA
from utils import antirrebote, esperar_hasta_hora
from vision import (
    esperar_imagen,
    encontrar_y_clickear_proxima_fecha,
    encontrar_y_clickear_amarillo_aleatorio,
)
from vision_ui import (
    encontrar_plantilla, click_plantilla, esperar_plantilla,
    maximizar_ventana, cerrar_obstrucciones, click_amarillo,
    hay_color_naranja, hay_marca_oscura, TITULO_VENTANA_DEFECTO,
)
from ocr import click_texto, esperar_texto, buscar_texto, leer_texto

# Resultado especial para señalar fallo sin lanzar excepción
FALLO = "FALLO"
EXITO = "EXITO"


def _esperar_retraso(hora_siguiente, retraso, logger):
    if hora_siguiente:
        esperar_hasta_hora(hora_siguiente, logger=logger)
    else:
        time.sleep(retraso or 0)


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

        # `retraso` es el TIMEOUT de búsqueda de la imagen.
        ubicacion = esperar_imagen(ruta_imagen, tiempo_limite=retraso, logger=logger)

        if not ubicacion:
            logger.registrar(f"Imagen '{nombre_imagen}' no apareció en {retraso}s", "WARNING")
            return FALLO

        logger.registrar(f"Imagen encontrada: {nombre_imagen}")

        # `@HH:MM:SS` en el campo retraso: esperar hasta esa hora antes del
        # siguiente paso (permite alinear la reserva a las 00:02, etc.).
        if hora_siguiente:
            esperar_hasta_hora(hora_siguiente, logger=logger)
            logger.registrar(f"Hora alcanzada: {hora_siguiente}")

    elif accion == "CLICK_IF_IMAGE":
        nombre_imagen = carga_util.strip()
        ruta_imagen = os.path.join(directorio_imagenes, nombre_imagen)
        if not os.path.exists(ruta_imagen):
            raise FileNotFoundError(f"Imagen no encontrada: {ruta_imagen}")

        ubicacion = esperar_imagen(
            ruta_imagen, tiempo_limite=CLICK_IF_IMAGE_TIMEOUT, logger=logger
        )
        if ubicacion:
            pyautogui.moveTo(x, y, duration=0.3)
            pyautogui.click()
            logger.registrar(f"Imagen presente — click en ({x}, {y}): {nombre_imagen}")
        else:
            logger.registrar(f"Imagen ausente — se continúa sin click: {nombre_imagen}")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "WAIT_UNTIL":
        hora_objetivo = carga_util.strip()
        if not hora_objetivo:
            raise ValueError("WAIT_UNTIL requiere una hora HH:MM:SS como carga útil")
        esperar_hasta_hora(hora_objetivo, logger=logger)
        logger.registrar(f"WAIT_UNTIL alcanzado: {hora_objetivo}")
        _esperar_retraso(None, retraso, logger)

    elif accion == "LAUNCH":
        _lanzar_aplicacion(carga_util, logger)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "FOCUS_WINDOW":
        _enfocar_ventana(carga_util, logger)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "PASTE":
        pyperclip.copy(carga_util)
        pyautogui.hotkey("ctrl", "v")
        logger.registrar(f"Texto pegado (clipboard): {carga_util[:40]}")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "MAXIMIZE":
        titulo = carga_util.strip() or TITULO_VENTANA_DEFECTO
        maximizar_ventana(titulo, logger)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "GUARD":
        subdir = carga_util.strip() or get_directorio_obstrucciones(directorio_imagenes)
        cerrar_obstrucciones(subdir, escalas=[1.0], logger=logger)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion in ("CLICK_ANCHOR", "CLICK_IF_ANCHOR"):
        ruta, conf = _resolver_anchor(carga_util, directorio_imagenes)
        click_plantilla(
            ruta, confianza=conf, logger=logger,
            obligatorio=(accion == "CLICK_ANCHOR"),
        )
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "WAIT_ANCHOR":
        ruta, conf = _resolver_anchor(carga_util, directorio_imagenes)
        if not esperar_plantilla(ruta, confianza=conf, tiempo_limite=retraso, logger=logger):
            logger.registrar(f"Ancla '{os.path.basename(ruta)}' no apareció en {retraso}s", "WARNING")
            return FALLO
        logger.registrar(f"Ancla encontrada: {os.path.basename(ruta)}")
        if hora_siguiente:
            esperar_hasta_hora(hora_siguiente, logger=logger)

    elif accion == "VERIFY_ANCHOR":
        ruta, conf = _resolver_anchor(carga_util, directorio_imagenes)
        if not encontrar_plantilla(ruta, confianza=conf):
            logger.registrar(f"Verificación fallida, no está: {os.path.basename(ruta)}", "WARNING")
            return FALLO
        logger.registrar(f"Verificado: {os.path.basename(ruta)}")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion in ("CLICK_TEXT", "CLICK_IF_TEXT"):
        texto, exacto, doble, boton = _parse_texto_payload(carga_util)
        click_texto(
            texto, exacto=exacto, doble=doble, logger=logger,
            obligatorio=(accion == "CLICK_TEXT"),
            max_y=(MAX_Y_BOTON if boton else None),
        )
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "WAIT_TEXT":
        texto, exacto, _, _ = _parse_texto_payload(carga_util)
        if not esperar_texto(texto, exacto=exacto, tiempo_limite=retraso, logger=logger):
            logger.registrar(f"Texto '{texto}' no apareció en {retraso}s", "WARNING")
            return FALLO
        logger.registrar(f"Texto encontrado: '{texto}'")
        if hora_siguiente:
            esperar_hasta_hora(hora_siguiente, logger=logger)

    elif accion == "VERIFY_TEXT":
        texto, exacto, _, _ = _parse_texto_payload(carga_util)
        if not buscar_texto(texto, exacto=exacto):
            logger.registrar(f"Verificación fallida, no está el texto: '{texto}'", "WARNING")
            return FALLO
        logger.registrar(f"Texto verificado: '{texto}'")
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "CLICK_AVAILABLE_COLOR":
        partes = (carga_util or "").split("|")
        if len(partes) < 2:
            raise ValueError("CLICK_AVAILABLE_COLOR requiere ancho|alto[|preferencia]")
        ancho, alto = int(partes[0]), int(partes[1])
        preferencia = partes[2].strip() if len(partes) > 2 and partes[2].strip() else "derecha"
        if click_amarillo((x, y, ancho, alto), preferencia=preferencia,
                          logger=logger, obligatorio=False) is None:
            return FALLO
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "DROPDOWN":
        opcion = (carga_util or "").strip()
        if not opcion:
            raise ValueError("DROPDOWN requiere el texto de la opción")
        pyautogui.click(x, y)
        time.sleep(0.7)
        if not click_texto(opcion, logger=logger, obligatorio=False):
            pyautogui.click(x, y)
            time.sleep(0.7)
            click_texto(opcion, logger=logger)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "MARCAR_1DIA":
        x1, y1 = DURACION_1DIA
        pyautogui.click(x1, y1)
        logger.registrar(f"Checkbox '1 Día' marcado en ({x1}, {y1})")
        time.sleep(0.8)
        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "SELECCIONAR_DIA":
        from ajustes import MESES
        dia = (carga_util or "").strip()
        if not dia or dia.lower() == "auto":
            from reserva import calcular_fecha_objetivo
            dia = str(calcular_fecha_objetivo().day)

        esperar_texto("Seleccione una fecha", tiempo_limite=15, logger=logger)
        for _ in range(20):
            if any(m in (l["texto"].lower()) for l in leer_texto() for m in MESES):
                break
            time.sleep(0.5)

        linea = None
        for _ in range(4):
            linea = buscar_texto(dia, exacto=True)
            if linea:
                break
            time.sleep(1.0)

        if not linea:
            logger.registrar(f"Día '{dia}' no apareció en el calendario", "WARNING")
            return FALLO

        pyautogui.moveTo(linea["x"], linea["y"], duration=0.3)
        pyautogui.click()
        time.sleep(0.15)
        pyautogui.click()
        logger.registrar(f"Día {dia} seleccionado (doble click en {linea['x']}, {linea['y']})")
        time.sleep(1.2)

        if not esperar_texto("tipo de lugar", tiempo_limite=8, logger=logger):
            logger.registrar("El día no quedó seleccionado (no avanzó)", "WARNING")
            return FALLO

        _esperar_retraso(hora_siguiente, retraso, logger)

    elif accion == "SELECCIONAR_PARQUEO":
        prioridad = [n.strip() for n in (carga_util or "").split(",") if n.strip()]
        if not prioridad:
            raise ValueError("SELECCIONAR_PARQUEO requiere una lista de números")
        if not _seleccionar_parqueo(prioridad, logger):
            logger.registrar("Ningún parqueo de la prioridad está disponible", "WARNING")
            return FALLO
        _esperar_retraso(hora_siguiente, retraso, logger)

    else:
        raise ValueError(f"Acción no soportada: {accion}")

    return EXITO


def _enfocar_busqueda(logger):
    if not click_texto(BUSCAR_PARQUEO["campo_busqueda"], logger=logger, obligatorio=False):
        pyautogui.click(BUSCAR_PARQUEO["campo_x"], BUSCAR_PARQUEO["campo_y"])
    time.sleep(0.4)


def _escribir_busqueda(numero):
    pyautogui.click(BUSCAR_PARQUEO["campo_x"], BUSCAR_PARQUEO["campo_y"])
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    time.sleep(0.2)
    pyautogui.write(str(numero), interval=0.12)
    time.sleep(0.3)
    pyautogui.click(BUSCAR_PARQUEO["lupa_x"], BUSCAR_PARQUEO["lupa_y"])
    time.sleep(0.4)


def _buscar_resultado(numero, intentos=3):
    objetivo = f"No. {numero}"
    for _ in range(intentos):
        time.sleep(BUSCAR_PARQUEO["espera_resultado"])
        for l in leer_texto():
            if objetivo in l["texto"] and l["palabras"]:
                return l
    return None


def _seleccionar_parqueo(prioridad, logger):
    """
    Recorre la prioridad: busca el número, marca su checkbox y pulsa Continuar.
    Si llega a la pantalla de confirmación ('¿Está todo bien?') termina; si no,
    vuelve con Regresar y prueba el siguiente número. Así no se queda pegado si
    un parqueo aparece en la lista pero no se puede reservar.
    """
    _enfocar_busqueda(logger)

    for numero in prioridad:
        _escribir_busqueda(numero)
        linea = _buscar_resultado(numero)
        if not linea:
            logger.registrar(f"Parqueo {numero} no disponible, probando el siguiente...", "WARNING")
            _enfocar_busqueda(logger)
            continue

        palabra = linea["palabras"][0]
        row_y = palabra["y"] + palabra["h"] // 2
        x = BUSCAR_PARQUEO["checkbox_x"]
        y = row_y + BUSCAR_PARQUEO["checkbox_offset_y"]

        region_checkbox = (x - 22, row_y - 8, 46, 46)
        if not hay_color_naranja(region_checkbox):
            logger.registrar(f"Parqueo {numero} sin checkbox; probando el siguiente...", "WARNING")
            continue

        pyautogui.click(x, y)
        time.sleep(0.6)

        if not hay_marca_oscura((x - 13, y - 13, 26, 26)):
            logger.registrar(f"Parqueo {numero} no se marcó; probando el siguiente...", "WARNING")
            _enfocar_busqueda(logger)
            continue

        logger.registrar(f"Parqueo {numero} SELECCIONADO (checkbox marcado)")
        return True

    return False


def _parse_texto_payload(carga_util):
    partes = (carga_util or "").split("|")
    texto = partes[0].strip()
    banderas = [p.strip().lower() for p in partes[1:]]
    exacto = any(b in ("exacto", "exact", "1", "true") for b in banderas)
    doble = any(b in ("doble", "2", "double") for b in banderas)
    boton = any(b in ("boton", "button", "arriba", "top") for b in banderas)
    return texto, exacto, doble, boton


def _resolver_anchor(carga_util, directorio_imagenes):
    partes = carga_util.strip().split("|")
    nombre = partes[0].strip()
    conf = float(partes[1]) if len(partes) > 1 and partes[1].strip() else UMBRAL_ANCHOR
    if os.path.isabs(nombre) or ("/" in nombre) or ("\\" in nombre):
        ruta = nombre
    else:
        ruta = os.path.join(get_directorio_anchors(directorio_imagenes), nombre)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Ancla no encontrada: {ruta}")
    return ruta, conf


def _lanzar_aplicacion(carga_util, logger):
    """
    Abre una app/proceso/URL de forma genérica. Formatos aceptados en la carga útil:
      path:C:\\ruta\\app.exe          -> ejecuta una ruta local
      proc:PowerApps                   -> ejecuta un proceso del PATH
      aumid:Microsoft.PowerApps...!App -> app de Microsoft Store (AUMID)
      shell:AppsFolder\\...            -> shell de Windows
      https://...  o  ms-powerapps://  -> URL / URI registrada
      C:\\ruta\\archivo                -> os.startfile (ruta o documento)
    """
    destino = (carga_util or "").strip()
    if not destino:
        raise ValueError("LAUNCH requiere un destino como carga útil")

    prefijo, _, resto = destino.partition(":")
    prefijo = prefijo.lower()

    if destino.startswith(("http://", "https://")):
        webbrowser.open(destino)
        logger.registrar(f"LAUNCH (URL): {destino}")

    elif destino.startswith("ms-") or resto.startswith("//"):
        # URI registrada, ej: ms-powerapps://...
        os.startfile(destino)
        logger.registrar(f"LAUNCH (URI): {destino}")

    elif prefijo == "path":
        os.startfile(resto.lstrip("\\/"))
        logger.registrar(f"LAUNCH (ruta): {resto}")

    elif prefijo == "proc":
        subprocess.Popen(resto.strip(), shell=True)
        logger.registrar(f"LAUNCH (proceso): {resto.strip()}")

    elif prefijo in ("aumid", "shell"):
        objetivo = resto.lstrip("\\/")
        if prefijo == "aumid":
            objetivo = f"shell:AppsFolder\\{objetivo}"
        subprocess.Popen(["explorer.exe", objetivo])
        logger.registrar(f"LAUNCH ({prefijo}): {objetivo}")

    else:
        os.startfile(destino)
        logger.registrar(f"LAUNCH (ruta/documento): {destino}")


def _enfocar_ventana(titulo, logger):
    """Trae al primer plano la primera ventana cuyo título contenga `titulo`."""
    fragmento = (titulo or "").strip()
    if not fragmento:
        raise ValueError("FOCUS_WINDOW requiere parte del título de la ventana")

    coincidencias = [v for v in gw.getAllWindows() if fragmento.lower() in v.title.lower()]
    if not coincidencias:
        raise RuntimeError(f"No se encontró ventana que contenga '{fragmento}'")

    ventana = coincidencias[0]
    try:
        if ventana.isMinimized:
            ventana.restore()
    except Exception:
        pass
    ventana.activate()
    time.sleep(0.3)
    logger.registrar(f"Ventana enfocada: '{ventana.title}'")
       


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
