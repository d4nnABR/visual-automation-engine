import os
import json

# Ruta del archivo donde se guarda la configuración persistente
_RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_usuario.json")

# Directorio base por defecto (escritorio del usuario actual)
_DIRECTORIO_BASE_DEFAULT = os.path.join(os.path.expanduser("~"), "Desktop")

CAPTURAR_SCREENSHOTS_ERROR = True


def cargar_directorio_base() -> str:
    if os.path.exists(_RUTA_CONFIG):
        try:
            with open(_RUTA_CONFIG, "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos.get("directorio_base", _DIRECTORIO_BASE_DEFAULT)
        except (json.JSONDecodeError, KeyError):
            pass
    return _DIRECTORIO_BASE_DEFAULT


def guardar_directorio_base(ruta: str):
    with open(_RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"directorio_base": ruta}, f, ensure_ascii=False, indent=2)


def get_directorio_imagenes(directorio_base: str) -> str:
    return os.path.join(directorio_base, "automation_images")


def get_directorio_debug(directorio_base: str) -> str:
    return os.path.join(directorio_base, "automation_images", "debug")


ACCIONES_VALIDAS = [
    "CLICK", "TYPE", "TYPE_RAW", "PRESS", "HOTKEY",
    "KEYEVENTS", "CLICK_WHEN_IMAGE", "WAIT_FOR_IMAGE",
    "CLICK_NEXT_DATE", "CLICK_RANDOM_YELLOW",
    # Fase 2: automatización "global" (Power Apps / cualquier app)
    "LAUNCH", "FOCUS_WINDOW", "PASTE", "WAIT_UNTIL", "CLICK_IF_IMAGE",
    # Fase 3: visión por anclas (sin depender de coordenadas fijas)
    "MAXIMIZE", "CLICK_ANCHOR", "WAIT_ANCHOR", "CLICK_IF_ANCHOR",
    "VERIFY_ANCHOR", "GUARD",
    # Fase 4: OCR (leer/decidir por texto en pantalla)
    "CLICK_TEXT", "CLICK_IF_TEXT", "WAIT_TEXT", "VERIFY_TEXT",
    # Selección de cajón disponible (amarillo) con preferencia
    "CLICK_AVAILABLE_COLOR",
    # Buscar parqueo por número con prioridad (39,38,...,105,106,104)
    "SELECCIONAR_PARQUEO",
    # Abrir un desplegable y elegir una opción por texto
    "DROPDOWN",
    # Seleccionar día del calendario con espera (o "auto" según semanas)
    "SELECCIONAR_DIA",
    # Marcar el checkbox "1 Día"
    "MARCAR_1DIA",
]

# Tiempo máximo (segundos) que CLICK_IF_IMAGE busca la imagen antes de continuar.
CLICK_IF_IMAGE_TIMEOUT = 2.0

# Si True, WAIT_FOR_IMAGE/CLICK_WHEN_IMAGE registran la hora exacta al encontrar.
LOG_IMAGENES_DETALLE = True

# Subcarpetas dentro de automation_images
SUBDIR_ANCHORS = "anchors"
SUBDIR_OBSTRUCCIONES = "obstrucciones"

# Si True, antes de cada acción se intenta cerrar cualquier obstrucción conocida
# (avisos/notificaciones) usando las imágenes de la carpeta `obstrucciones`.
AUTO_GUARD = True

# Confianza por defecto para el motor de anclas (OpenCV matchTemplate).
UMBRAL_ANCHOR = 0.8

# Por debajo de esta Y se considera un botón de contenido (no la barra inferior
# de navegación). Útil para distinguir "Confirmar" del botón vs el del nav.
MAX_Y_BOTON = 900


def get_directorio_anchors(directorio_imagenes: str) -> str:
    return os.path.join(directorio_imagenes, SUBDIR_ANCHORS)


def get_directorio_obstrucciones(directorio_imagenes: str) -> str:
    return os.path.join(directorio_imagenes, SUBDIR_OBSTRUCCIONES)