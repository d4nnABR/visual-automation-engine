import os
import json

# Ruta del archivo donde se guarda la configuración persistente
_RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_usuario.json")

# Directorio base por defecto (escritorio del usuario actual)
_DIRECTORIO_BASE_DEFAULT = os.path.join(os.path.expanduser("~"), "Desktop")

CAPTURAR_SCREENSHOTS_ERROR = False


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
]