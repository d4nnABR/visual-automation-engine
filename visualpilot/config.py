import os
import json

# Raíz del proyecto (carpeta que contiene main.py y el paquete visualpilot/)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuración persistente del usuario (ignorada por git). Secciones:
#   "directorio_base": dónde están flujos, imágenes y debug
#   "reserva": valores editables desde el menú (ver ajustes.RESERVA)
_RUTA_CONFIG = os.path.join(RAIZ_PROYECTO, "config_usuario.json")

CAPTURAR_SCREENSHOTS_ERROR = True


def _leer_config_usuario() -> dict:
    if not os.path.exists(_RUTA_CONFIG):
        return {}
    try:
        with open(_RUTA_CONFIG, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _guardar_config_usuario(cambios: dict):
    """Fusiona `cambios` con lo que ya hay en el archivo (no borra otras secciones)."""
    datos = _leer_config_usuario()
    datos.update(cambios)
    with open(_RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_directorio_base() -> str:
    return _leer_config_usuario().get("directorio_base", RAIZ_PROYECTO)


def guardar_directorio_base(ruta: str):
    _guardar_config_usuario({"directorio_base": ruta})


def cargar_reserva() -> dict:
    """Valores de reserva: defaults de ajustes.RESERVA + lo guardado por el usuario."""
    from .ajustes import RESERVA
    cfg = dict(RESERVA)
    cfg.update(_leer_config_usuario().get("reserva", {}))
    return cfg


def guardar_reserva(cfg: dict):
    _guardar_config_usuario({"reserva": cfg})


def variables_flujo() -> dict:
    """Variables que un flujo .txt puede usar como {NOMBRE}."""
    cfg = cargar_reserva()
    return {
        "HORA_INICIO": cfg["hora_inicio"],
        "PRIORIDAD": cfg["prioridad"],
        "DIAS_ANTICIPACION": str(cfg["dias_anticipacion"]),
    }


def resolver_flujo(archivo: str, directorio_base: str) -> str:
    """Ruta de un flujo: tal cual si existe; si no, en <base>/flujos/ o en <base>/."""
    for ruta in (
        archivo,
        os.path.join(directorio_base, "flujos", archivo),
        os.path.join(directorio_base, archivo),
    ):
        if os.path.exists(ruta):
            return ruta
    return os.path.join(directorio_base, "flujos", archivo)


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
    # Termina el flujo sin error si la fecha a reservar cae en semana libre
    "VERIFICAR_SEMANA",
]

# Si una de estas acciones falla (y no hay ON_FAIL_GOTO), se detiene el flujo.
# Ej.: si no se pudo elegir el día, la app deja el de hoy preseleccionado y se
# reservaría la fecha equivocada.
ACCIONES_CRITICAS = {"SELECCIONAR_DIA"}

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