"""
Genera anclas y plantillas de obstrucción a partir de las capturas del flujo
(automation_images/Config) y las copia al directorio de trabajo de la app.

Uso:
    python herramientas/preparar_anclas.py
    python herramientas/preparar_anclas.py --destino "C:\\ruta\\automation_images"
"""

import os
import sys
import shutil
import argparse

import cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)

CONFIG_POR_DEFECTO = os.path.join(REPO, "automation_images", "Config")
DESTINO_POR_DEFECTO = os.path.join(REPO, "automation_images")

ANCLAS = {
    "check_seleccion.png": "paso11_CLICK_EN EL CHECK2 despues de confirmar parqueo amarillo .png",
}

OBSTRUCCIONES = {
    "cerrar_aviso_semana.png": ("ERROR_si selecciona semana erronea.png", (1875, 44, 40, 30)),
}


def main():
    parser = argparse.ArgumentParser(description="Prepara anclas desde las capturas del flujo")
    parser.add_argument("--config", default=CONFIG_POR_DEFECTO, help="Carpeta con las capturas")
    parser.add_argument("--destino", default=DESTINO_POR_DEFECTO, help="Carpeta automation_images destino")
    args = parser.parse_args()

    if not os.path.isdir(args.config):
        print(f"No existe la carpeta de capturas: {args.config}")
        return 1

    dir_anclas = os.path.join(args.destino, "anchors")
    dir_obs = os.path.join(args.destino, "obstrucciones")
    os.makedirs(dir_anclas, exist_ok=True)
    os.makedirs(dir_obs, exist_ok=True)

    for destino_nombre, origen_nombre in ANCLAS.items():
        origen = os.path.join(args.config, origen_nombre)
        if not os.path.exists(origen):
            print(f"[ANCLA] falta origen: {origen_nombre}")
            continue
        shutil.copyfile(origen, os.path.join(dir_anclas, destino_nombre))
        print(f"[ANCLA] {destino_nombre}  <-  {origen_nombre}")

    for destino_nombre, (origen_nombre, caja) in OBSTRUCCIONES.items():
        origen = os.path.join(args.config, origen_nombre)
        if not os.path.exists(origen):
            print(f"[OBSTRUCCION] falta origen: {origen_nombre}")
            continue
        img = cv2.imread(origen)
        if img is None:
            print(f"[OBSTRUCCION] no se pudo leer: {origen_nombre}")
            continue
        x, y, w, h = caja
        recorte = img[y:y + h, x:x + w]
        cv2.imwrite(os.path.join(dir_obs, destino_nombre), recorte)
        print(f"[OBSTRUCCION] {destino_nombre}  <-  {origen_nombre} {caja}")

    print(f"\nListo. Anclas en: {dir_anclas}")
    print(f"Obstrucciones en: {dir_obs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
