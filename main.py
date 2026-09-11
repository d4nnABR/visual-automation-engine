import sys

from core import AutomatizacionVisual


def _cli():
    args = sys.argv[1:]
    if not args:
        return False

    auto = AutomatizacionVisual()
    comando = args[0].lower()

    if comando in ("run", "ejecutar"):
        archivo = args[1] if len(args) > 1 else None
        auto.aplicar_coordenadas_visuales(archivo)
        return True

    if comando in ("validate", "validar"):
        archivo = args[1] if len(args) > 1 else None
        if not archivo:
            print("Uso: python main.py validate <archivo.txt>")
        else:
            _validar(auto, archivo)
        return True

    print("Uso: python main.py [run|validate] <archivo.txt>")
    return True


def _validar(auto, archivo):
    import os
    ruta = archivo if os.path.exists(archivo) else os.path.join(auto.directorio_base, archivo)
    if not os.path.exists(ruta):
        print(f"No se encontró: {ruta}")
        return
    lineas = auto.validar_y_limpiar_archivo(ruta)
    if lineas:
        print(f"Archivo válido con {len(lineas)} líneas.")


def menu():
    auto = AutomatizacionVisual()
    opciones = {
        "1": ("Registrar nuevas coordenadas visuales", lambda: auto.registrar_coordenadas_visuales("w")),
        "2": ("Aplicar coordenadas visuales",          lambda: auto.aplicar_coordenadas_visuales()),
        "3": ("Continuar grabación existente",         lambda: auto.registrar_coordenadas_visuales("a")),
        "4": ("Ver imágenes almacenadas",              lambda: auto.mostrar_imagenes_almacenadas()),
        "5": ("Validar archivo de coordenadas",        lambda: auto.menu_validar_archivo()),
        "6": ("Establecer directorio base",            lambda: auto.establecer_directorio_base()),
        "7": ("Salir",                                 None),
    }

    while True:
        print("\n" + "=" * 50)
        print("AUTOMATIZACIÓN VISUAL")
        print(f"  Directorio base: {auto.directorio_base}")
        print("=" * 50)
        for clave, (desc, _) in opciones.items():
            print(f"  {clave}. {desc}")
        print("=" * 50)

        opcion = input("Elige una opción (1-7): ").strip()

        if opcion == "7":
            print("Saliendo...")
            break
        elif opcion in opciones:
            _, accion = opciones[opcion]
            accion()
        else:
            print("Opción inválida. Por favor, elige 1-7.")


if __name__ == "__main__":
    if not _cli():
        menu()