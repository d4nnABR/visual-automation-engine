import os
import time
import pyautogui
from datetime import datetime
from utils import obtener_marca_tiempo
from config import CAPTURAR_SCREENSHOTS_ERROR



class Logger:
    def __init__(self, directorio_debug):
        self.directorio_debug = directorio_debug
        self._archivo_log = None
        self._hora_inicio = None
        self._advertencia_opencv_mostrada = False

    def abrir(self, nombre_archivo):
        self._hora_inicio = time.time()
        ruta_log = os.path.join(self.directorio_debug, nombre_archivo)
        self._archivo_log = open(ruta_log, "w", encoding="utf-8")
        return ruta_log

    def cerrar(self):
        if self._archivo_log:
            self._archivo_log.close()
            self._archivo_log = None

    def registrar(self, mensaje, nivel="INFO"):
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca_tiempo}] [{nivel}] {mensaje}"
        if self._archivo_log:
            self._archivo_log.write(linea + "\n")
            self._archivo_log.flush()
        print(linea)

    def capturar_pantallazo_error(self, numero_paso, accion, mensaje_error):
        if not CAPTURAR_SCREENSHOTS_ERROR:
            self.registrar(f"Screenshot deshabilitado — error en paso {numero_paso} ({accion})", "ERROR")
            return None

        nombre_archivo = f"ERROR_Paso{numero_paso}_{accion}_{obtener_marca_tiempo()}.png"
        ruta_archivo = os.path.join(self.directorio_debug, nombre_archivo)
        try:
            pyautogui.screenshot().save(ruta_archivo)
            self.registrar(f"Screenshot de error guardado: {nombre_archivo}", "ERROR")
            return ruta_archivo
        except Exception as e:
            self.registrar(f"No se pudo guardar screenshot: {e}", "ERROR")
            return None

    @property
    def tiempo_transcurrido(self):
        return time.time() - self._hora_inicio if self._hora_inicio else 0.0

    @property
    def advertencia_opencv_mostrada(self):
        return self._advertencia_opencv_mostrada

    @advertencia_opencv_mostrada.setter
    def advertencia_opencv_mostrada(self, valor):
        self._advertencia_opencv_mostrada = valor
