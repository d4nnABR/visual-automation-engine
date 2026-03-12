import os
import time
import pyautogui
import keyboard
from datetime import datetime, timedelta

from config import (
    cargar_directorio_base, guardar_directorio_base,
    get_directorio_imagenes, get_directorio_debug,
    ACCIONES_VALIDAS,
)
from utils import obtener_marca_tiempo, antirrebote, parse_retraso_y_hora_siguiente, crear_directorios
from logger import Logger
from vision import seleccionar_region, capturar_imagen_referencia
from acciones import ejecutar_accion, grabar_eventos_teclas_hasta_f12, FALLO, EXITO

ACCIONES_FLUJO = {"LABEL", "GOTO", "RETRY", "ON_FAIL_GOTO"}


class AutomatizacionVisual:
    def __init__(self):
        self.directorio_base     = cargar_directorio_base()
        self.directorio_imagenes = get_directorio_imagenes(self.directorio_base)
        self.directorio_debug    = get_directorio_debug(self.directorio_base)
        crear_directorios(self.directorio_imagenes, self.directorio_debug)
        self.logger = Logger(self.directorio_debug)

    # ──────────────────────────────────────────────
    # DIRECTORIO BASE DINÁMICO
    # ──────────────────────────────────────────────

    def establecer_directorio_base(self):
        print(f"\nDirectorio base actual: {self.directorio_base}")
        nueva_ruta = input("Introduce la nueva ruta (o Enter para conservar la actual): ").strip()

        if not nueva_ruta:
            print("Sin cambios.")
            return

        if not os.path.exists(nueva_ruta):
            crear = input("La ruta no existe. ¿Crearla? (s/n): ").strip().lower()
            if crear == "s":
                os.makedirs(nueva_ruta)
                print(f"Directorio creado: {nueva_ruta}")
            else:
                print("Operación cancelada.")
                return

        self.directorio_base     = nueva_ruta
        self.directorio_imagenes = get_directorio_imagenes(nueva_ruta)
        self.directorio_debug    = get_directorio_debug(nueva_ruta)
        guardar_directorio_base(nueva_ruta)
        crear_directorios(self.directorio_imagenes, self.directorio_debug)
        self.logger = Logger(self.directorio_debug)
        print(f"Directorio base actualizado y guardado: {nueva_ruta}")

    # ──────────────────────────────────────────────
    # GRABACIÓN DE COORDENADAS
    # ──────────────────────────────────────────────

    def registrar_coordenadas_visuales(self, modo="w"):
        nombre_archivo = input("Introduce el nombre del archivo para guardar las coordenadas (incluye .txt): ")
        ruta_archivo = os.path.join(self.directorio_base, nombre_archivo)

        if modo == "a" and not os.path.exists(ruta_archivo):
            print(f"El archivo {ruta_archivo} no existe. Usa la opción 1 para crearlo.")
            return

        print(f"'{'Continuando' if modo == 'a' else 'Guardando nuevas'}' coordenadas visuales en {ruta_archivo}.")
        self._mostrar_comandos_grabacion()

        try:
            with open(ruta_archivo, modo, encoding="utf-8") as archivo:
                contador_pasos = 1
                while True:
                    if keyboard.is_pressed("q"):
                        antirrebote("q")
                        print("Saliendo de la grabación...")
                        break

                    if keyboard.is_pressed("enter"):
                        antirrebote("enter")
                        x, y = pyautogui.position()
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"CLICK,{x},{y},{retraso}\n")
                        print(f"Coordenadas capturadas: ({x}, {y}) con espera {retraso}s")

                    elif keyboard.is_pressed("t"):
                        antirrebote("t")
                        x, y = pyautogui.position()
                        texto = input("Introduce el texto: ")
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"TYPE,{x},{y},{retraso},{texto}\n")
                        print(f"TYPE guardado en ({x}, {y}) con espera {retraso}s")

                    elif keyboard.is_pressed("i"):
                        antirrebote("i")
                        nombre_paso = input(f"Nombre para este paso (default: step_{contador_pasos}): ") or f"step_{contador_pasos}"
                        ruta_img = capturar_imagen_referencia(nombre_paso, self.directorio_imagenes)
                        x, y = pyautogui.position()
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"CLICK_WHEN_IMAGE,{x},{y},{retraso},{os.path.basename(ruta_img)}\n")
                        print(f"CLICK_WHEN_IMAGE guardado: {os.path.basename(ruta_img)}")
                        contador_pasos += 1

                    elif keyboard.is_pressed("w"):
                        antirrebote("w")
                        nombre_paso = input(f"Nombre para imagen de espera (default: wait_{contador_pasos}): ") or f"wait_{contador_pasos}"
                        ruta_img = capturar_imagen_referencia(nombre_paso, self.directorio_imagenes)
                        tiempo_limite = input("Timeout en segundos (default: 30): ") or "30"
                        archivo.write(f"WAIT_FOR_IMAGE,0,0,{tiempo_limite},{os.path.basename(ruta_img)}\n")
                        print(f"WAIT_FOR_IMAGE guardado: {os.path.basename(ruta_img)}")
                        contador_pasos += 1

                    elif keyboard.is_pressed("h"):
                        antirrebote("h")
                        atajo = input("Introduce el hotkey (ejemplo: ctrl+v o win+r): ").strip()
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"HOTKEY,0,0,{retraso},{atajo}\n")
                        print("HOTKEY guardado.")

                    elif keyboard.is_pressed("k"):
                        antirrebote("k")
                        retraso = input("Introduce el tiempo de espera después de enviar la secuencia (segundos): ")
                        eventos_json = grabar_eventos_teclas_hasta_f12()
                        archivo.write(f"KEYEVENTS,0,0,{retraso},{eventos_json}\n")
                        print("KEYEVENTS guardado.")

                    elif keyboard.is_pressed("p"):
                        antirrebote("p")
                        nombre_tecla = input("Introduce la tecla para PRESS (ejemplo: enter, tab, esc): ").strip()
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"PRESS,0,0,{retraso},{nombre_tecla}\n")
                        print("PRESS guardado.")

                    elif keyboard.is_pressed("r"):
                        antirrebote("r")
                        texto = input("Introduce el texto para TYPE_RAW: ")
                        retraso = input("Introduce el tiempo de espera (en segundos): ")
                        archivo.write(f"TYPE_RAW,0,0,{retraso},{texto}\n")
                        print("TYPE_RAW guardado.")

                    elif keyboard.is_pressed("d"):
                        antirrebote("d")
                        print("Define la región del calendario completo (solo la grilla de días)")
                        region = seleccionar_region()
                        if region:
                            retraso = input("Introduce el tiempo de espera (en segundos): ")
                            archivo.write(f"CLICK_NEXT_DATE,{region[0]},{region[1]},{retraso},{region[2]}|{region[3]}\n")
                            print(f"CLICK_NEXT_DATE guardado con región: {region}")

                    elif keyboard.is_pressed("a"):
                        antirrebote("a")
                        print("Define la región completa donde buscar cuadros amarillos")
                        region = seleccionar_region()
                        if region:
                            retraso = input("Introduce el tiempo de espera (en segundos): ")
                            archivo.write(f"CLICK_RANDOM_YELLOW,{region[0]},{region[1]},{retraso},{region[2]}|{region[3]}\n")
                            print(f"CLICK_RANDOM_YELLOW guardado con región: {region}")

                    time.sleep(0.05)

        except KeyboardInterrupt:
            print("Captura terminada.")

        print(f"Coordenadas visuales almacenadas en {ruta_archivo}")

    def _mostrar_comandos_grabacion(self):
        comandos = [
            ("Enter", "Capturar coordenadas normales"),
            ("t",     "Capturar coordenadas con texto"),
            ("i",     "Capturar imagen de referencia y coordenadas"),
            ("w",     "Capturar imagen de espera"),
            ("h",     "Guardar un hotkey (ejemplo: ctrl+v o win+r)"),
            ("k",     "Grabar secuencia real de teclas (termina con F12)"),
            ("p",     "Guardar una tecla simple para PRESS (ejemplo: enter, tab, esc)"),
            ("r",     "Guardar TYPE_RAW (escribe sin hacer click)"),
            ("d",     "Capturar región del calendario para fecha automática"),
            ("a",     "Click aleatorio en cuadro AMARILLO"),
            ("q",     "Salir"),
        ]
        print("\nComandos disponibles:")
        for tecla, desc in comandos:
            print(f"  - {tecla}: {desc}")

    # ──────────────────────────────────────────────
    # EJECUCIÓN DE COORDENADAS (con flujo de control)
    # ──────────────────────────────────────────────

    def _construir_indice_etiquetas(self, lineas):
        etiquetas = {}
        for i, linea in enumerate(lineas):
            partes = linea.strip().split(",", 4)
            if partes and partes[0].strip() == "LABEL" and len(partes) > 4:
                nombre = partes[4].strip()  # ✅ posición 4
                etiquetas[nombre] = i
        return etiquetas

    def aplicar_coordenadas_visuales(self):
        nombre_archivo = input("Introduce el nombre del archivo con las coordenadas: ")
        ruta_archivo = os.path.join(self.directorio_base, nombre_archivo)

        if not os.path.exists(ruta_archivo):
            print(f"No se encontró el archivo: {ruta_archivo}")
            return

        lineas = self.validar_y_limpiar_archivo(ruta_archivo)  # ✅ ya es lista
        if not lineas:
            return

        marca_tiempo = obtener_marca_tiempo()
        ruta_log = self.logger.abrir(f"registro_ejecucion_{marca_tiempo}.txt")
        self.logger.registrar("=" * 60)
        self.logger.registrar("INICIO DE EJECUCIÓN DE AUTOMATIZACIÓN")
        self.logger.registrar(f"Archivo: {nombre_archivo}")
        self.logger.registrar("=" * 60)

        ruta_txt_con_horas = os.path.join(
            self.directorio_debug,
            f"coordenadas_con_hora_siguiente_{obtener_marca_tiempo()}.txt",
        )
        salida_con_horas = open(ruta_txt_con_horas, "w", encoding="utf-8")

        contador_exitos = 0
        contador_errores = 0
        total_pasos = len(lineas)

        print("Aplicando coordenadas visuales...")
        print("Presiona ESC en cualquier momento para detener la ejecución")

        try:
            etiquetas = self._construir_indice_etiquetas(lineas)  # ✅ usa lista directamente

            reintentos_activos = {}
            on_fail_goto_activo = None

            i = 0
            while i < total_pasos:
                if keyboard.is_pressed("esc"):
                    antirrebote("esc")
                    self.logger.registrar("Ejecución detenida por el usuario", "WARNING")
                    break

                linea = lineas[i].strip()
                if not linea:
                    i += 1
                    continue

                partes = linea.split(",", 4)
                accion = partes[0].strip()

                # ── Directivas de flujo ───────────────────────────
                if accion == "LABEL":
                    nombre = partes[4].strip() if len(partes) > 4 else "?"  # ✅
                    self.logger.registrar(f"[LABEL] {nombre}")
                    i += 1
                    continue

                if accion == "GOTO":
                    destino = partes[4].strip() if len(partes) > 4 else ""  # ✅
                    if destino in etiquetas:
                        self.logger.registrar(f"[GOTO] Saltando a etiqueta: {destino}")
                        i = etiquetas[destino]
                    else:
                        self.logger.registrar(f"[GOTO] Etiqueta no encontrada: {destino}", "ERROR")
                        i += 1
                    continue

                if accion == "RETRY":
                    n = int(partes[4].strip()) if len(partes) > 4 else 3  # ✅ ya estaba bien
                    reintentos_activos[i + 1] = n
                    self.logger.registrar(f"[RETRY] Próxima acción tendrá hasta {n} reintentos")
                    i += 1
                    continue

                if accion == "ON_FAIL_GOTO":
                    etiqueta = partes[4].strip() if len(partes) > 4 else ""  # ✅
                    on_fail_goto_activo = etiqueta
                    self.logger.registrar(f"[ON_FAIL_GOTO] Si falla la próxima acción → {etiqueta}")
                    i += 1
                    continue

                # ── Acción real ───────────────────────────────────
                analizado = self._analizar_linea(linea)
                if not analizado:
                    self.logger.registrar(f"Línea {i+1} inválida (se omite): {linea}", "WARNING")
                    i += 1
                    continue

                accion, x, y, retraso, carga_util, hora_siguiente = analizado
                self.logger.registrar(f"--- Paso {i+1}/{total_pasos}: {accion} ---")

                max_intentos = reintentos_activos.pop(i, 0) + 1
                on_fail = on_fail_goto_activo
                on_fail_goto_activo = None

                resultado = FALLO
                for intento in range(1, max_intentos + 1):
                    try:
                        resultado = ejecutar_accion(
                            accion, x, y, retraso, carga_util, hora_siguiente,
                            self.directorio_imagenes, self.logger,
                        )
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        self.logger.registrar(f"Intento {intento}/{max_intentos} falló: {e}", "ERROR")
                        resultado = FALLO

                    if resultado == EXITO:
                        break

                    if intento < max_intentos:
                        self.logger.registrar(f"Reintentando ({intento}/{max_intentos - 1})...", "WARNING")
                        time.sleep(1)

                if resultado == EXITO:
                    contador_exitos += 1
                    self._escribir_linea_con_hora(salida_con_horas, accion, x, y, retraso, hora_siguiente, carga_util)
                    i += 1
                else:
                    contador_errores += 1
                    self.logger.registrar(f"FALLO en paso {i+1} ({accion})", "ERROR")
                    self.logger.capturar_pantallazo_error(i + 1, accion, "Acción falló")

                    if on_fail and on_fail in etiquetas:
                        self.logger.registrar(f"ON_FAIL_GOTO → saltando a: {on_fail}", "WARNING")
                        i = etiquetas[on_fail]
                    else:
                        i += 1

        except KeyboardInterrupt:
            self.logger.registrar("Ejecución interrumpida por el usuario", "WARNING")
        except Exception as e:
            self.logger.registrar(f"Error crítico en ejecución: {e}", "CRITICAL")
            self.logger.capturar_pantallazo_error(0, "CRITICAL", str(e))
        finally:
            self.logger.registrar("=" * 60)
            self.logger.registrar("RESUMEN DE EJECUCIÓN")
            self.logger.registrar(f"Exitosos: {contador_exitos}")
            self.logger.registrar(f"Errores: {contador_errores}")
            self.logger.registrar(f"Tiempo total: {self.logger.tiempo_transcurrido:.2f} segundos")
            self.logger.registrar("=" * 60)
            self.logger.cerrar()
            print(f"\nLog guardado en: {ruta_log}")
            try:
                salida_con_horas.close()
            except Exception:
                pass

        print("Aplicación completada.")

    def _escribir_linea_con_hora(self, archivo_salida, accion, x, y, retraso, hora_siguiente, carga_util):
        ACCIONES_CON_RETRASO = {
            "CLICK", "TYPE", "TYPE_RAW", "PRESS", "HOTKEY",
            "KEYEVENTS", "CLICK_WHEN_IMAGE", "CLICK_NEXT_DATE", "CLICK_RANDOM_YELLOW",
        }
        if hora_siguiente:
            hora_out = hora_siguiente
        else:
            delay = float(retraso) if accion in ACCIONES_CON_RETRASO else 0.0
            hora_out = (datetime.now() + timedelta(seconds=delay)).strftime("%H:%M:%S")

        retraso_txt = f"{float(retraso)}@{hora_out}"
        linea = f"{accion},{x},{y},{retraso_txt}"
        if carga_util:
            linea += f",{carga_util}"
        archivo_salida.write(linea + "\n")
        archivo_salida.flush()

    # ──────────────────────────────────────────────
    # VALIDACIÓN EN MEMORIA (sin .backup)
    # ──────────────────────────────────────────────

    def _analizar_linea(self, linea):
        partes = linea.rstrip("\n").split(",", 4)
        if len(partes) < 4:
            return None
        try:
            accion = partes[0].strip()
            x = int(partes[1].strip())
            y = int(partes[2].strip())
            retraso, hora_siguiente = parse_retraso_y_hora_siguiente(partes[3].strip())
            carga_util = partes[4] if len(partes) > 4 else ""
            return accion, x, y, retraso, carga_util, hora_siguiente
        except (ValueError, IndexError):
            return None

    def validar_y_limpiar_archivo(self, ruta_archivo):
        print("Validando archivo de coordenadas...")
        lineas_validas = []

        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, 1):
                linea = linea.rstrip("\n")
                if not linea.strip():
                    continue

                partes = linea.split(",", 4)
                accion = partes[0].strip()

                if accion in ACCIONES_FLUJO:
                    lineas_validas.append(linea)
                    continue

                if len(partes) < 4:
                    print(f"Línea {numero_linea} incompleta (se omite): {linea}")
                    continue

                x_s, y_s, retraso_s = partes[1].strip(), partes[2].strip(), partes[3].strip()
                carga_util = partes[4] if len(partes) > 4 else ""

                if accion not in ACCIONES_VALIDAS:
                    print(f"Línea {numero_linea} acción inválida (se omite): {linea}")
                    continue

                try:
                    x, y = int(x_s), int(y_s)
                except ValueError:
                    print(f"Línea {numero_linea} coordenadas inválidas (se omite): {linea}")
                    continue

                try:
                    retraso, hora_siguiente = parse_retraso_y_hora_siguiente(retraso_s or "1.0")
                except ValueError:
                    retraso, hora_siguiente = 1.0, None

                retraso_txt = f"{float(retraso)}@{hora_siguiente}" if hora_siguiente else str(float(retraso))
                limpia = f"{accion},{x},{y},{retraso_txt}"
                if carga_util:
                    limpia += f",{carga_util}"
                lineas_validas.append(limpia)

        if not lineas_validas:
            print("No se encontraron líneas válidas en el archivo")
            return None

        print(f"Archivo validado: {len(lineas_validas)} líneas listas.")
        return lineas_validas  # ✅ lista en memoria, sin .backup

    def menu_validar_archivo(self):
        nombre_archivo = input("Introduce el nombre del archivo a validar: ")
        ruta_archivo = os.path.join(self.directorio_base, nombre_archivo)

        if not os.path.exists(ruta_archivo):
            print(f"No se encontró el archivo: {ruta_archivo}")
            return

        lineas = self.validar_y_limpiar_archivo(ruta_archivo)
        if lineas:
            print(f"Archivo válido con {len(lineas)} líneas. No se generó ningún archivo extra.")

    # ──────────────────────────────────────────────
    # UTILIDADES DE MENÚ
    # ──────────────────────────────────────────────

    def mostrar_imagenes_almacenadas(self):
        if not os.path.exists(self.directorio_imagenes):
            print("No hay directorio de imágenes.")
            return
        imagenes = [f for f in os.listdir(self.directorio_imagenes) if f.endswith(".png")]
        if not imagenes:
            print("No hay imágenes almacenadas.")
            return
        print("Imágenes almacenadas:")
        for i, img in enumerate(imagenes, 1):
            print(f"  {i}. {img}")
