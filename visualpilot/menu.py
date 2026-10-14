"""Menú de terminal y comandos de línea (`run` / `validate`)."""

import os
import re
import sys
import time
from datetime import date, datetime

from .config import cargar_reserva, guardar_reserva, resolver_flujo
from .core import AutomatizacionVisual
from .ajustes import DIAS_SEMANA
from . import reserva as regla
from .utils import tomar_instancia_unica, soltar_instancia_unica

USO = "Uso: python main.py [run|reservar|reservar_si_falta|validate] <flujo.txt>"

YA_EN_EJECUCION = "Ya hay otra ejecución de VisualPilot en curso: esta no se inicia."


def _avisar_ya_en_ejecucion():
    marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{marca}] [WARNING] {YA_EN_EJECUCION}")


def _una_sola(funcion):
    """Ejecuta `funcion` solo si no hay otra ejecución de flujo en curso. Suelta
    el candado al terminar: el menú abierto sin hacer nada no debe bloquear la
    tarea programada."""
    if not tomar_instancia_unica():
        _avisar_ya_en_ejecucion()
        return None
    try:
        return funcion()
    finally:
        soltar_instancia_unica()


# ──────────────────────────────────────────────
# LÍNEA DE COMANDOS
# ──────────────────────────────────────────────

def cli(args):
    """Devuelve el código de salida, o None si no hay argumentos (abrir menú)."""
    if not args:
        return None

    comando = args[0].lower()
    archivo = args[1] if len(args) > 1 else None

    # Otra ejecución en curso (p. ej. la tarea de las 23:58 y un auto.bat al
    # encender el PC): no se arranca encima. Sale con 0 porque no es un error.
    if comando in ("run", "ejecutar", "reservar", "reserva", "reservar_si_falta")             and not tomar_instancia_unica():
        _avisar_ya_en_ejecucion()
        return 0

    auto = AutomatizacionVisual()

    if comando in ("run", "ejecutar"):
        return 0 if auto.aplicar_coordenadas_visuales(archivo) else 1

    if comando in ("reservar", "reserva"):
        if not archivo:
            print(USO)
            return 2
        return 0 if auto.reservar_con_reintentos(archivo) else 1

    if comando == "reservar_si_falta":
        if not archivo:
            print(USO)
            return 2
        return 0 if auto.reservar_si_falta(archivo) else 1

    if comando in ("validate", "validar"):
        if not archivo:
            print(USO)
            return 2
        ruta = resolver_flujo(archivo, auto.directorio_base)
        if not os.path.exists(ruta):
            print(f"No se encontró: {ruta}")
            return 1
        lineas = auto.validar_y_limpiar_archivo(ruta)
        if lineas:
            print(f"Archivo válido con {len(lineas)} líneas.")
        return 0 if lineas else 1

    print(USO)
    return 2


# ──────────────────────────────────────────────
# CONFIGURACIÓN DE LA RESERVA
# ──────────────────────────────────────────────

def _pedir(texto, convertir, actual):
    """Pide un valor; Enter conserva el actual. Repite hasta que sea válido."""
    while True:
        valor = input(f"{texto} [{actual}]: ").strip()
        if not valor:
            return actual
        try:
            return convertir(valor)
        except ValueError as e:
            print(f"  Valor inválido: {e}")


def _hora(valor):
    for formato in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(valor, formato).strftime("%H:%M:%S")
        except ValueError:
            pass
    raise ValueError("usa HH:MM o HH:MM:SS (ej. 00:02)")


def _dias(valor):
    n = int(valor)
    if not 0 <= n <= 60:
        raise ValueError("debe estar entre 0 y 60")
    return n


def _prioridad(valor):
    numeros = [n.strip() for n in valor.split(",") if n.strip()]
    if not numeros or not all(re.fullmatch(r"\d+", n) for n in numeros):
        raise ValueError("lista de números separados por coma (ej. 39,38,37)")
    return ",".join(numeros)


def _dia_semana(valor):
    n = int(valor)
    if not 0 <= n <= 6:
        raise ValueError("0=lunes ... 6=domingo")
    return n


def _mostrar_reserva(cfg):
    hoy = date.today()
    objetivo = regla.calcular_fecha_objetivo(hoy, cfg)
    if cfg["modo"] == "dia_semana":
        modo = f"día de semana ({DIAS_SEMANA[int(cfg['dia_semana_objetivo'])]})"
    else:
        modo = f"anticipación (hoy + {cfg['dias_anticipacion']} días)"

    print("\n" + "=" * 50)
    print("CONFIGURAR RESERVA")
    print("=" * 50)
    print(f"  Hora de inicio      : {cfg['hora_inicio']}")
    print(f"  Modo de fecha       : {modo}")
    print(f"  Semanas alternas    : {'SÍ' if cfg['semanas_alternas'] else 'NO (reserva todas las semanas)'}")
    print(f"  Prioridad parqueos  : {cfg['prioridad']}")
    estado = "toca reservar" if regla.toca_reservar(objetivo, cfg) else "semana libre, no reserva"
    print(f"  Si corre hoy        : {objetivo.strftime('%d/%m/%Y')} ({estado})")
    if cfg["semanas_alternas"]:
        print("  Semanas en que se USA el parqueo (la fecha reservada cae en ellas):")
        for lunes, domingo, on in regla.proximas_semanas(5, hoy, cfg):
            marca = "SÍ reserva" if on else "no"
            print(f"    {lunes.strftime('%d/%m')} - {domingo.strftime('%d/%m')}: {marca}")
    print("-" * 50)
    print("  1. Hora de inicio")
    print("  2. Modo de fecha y días de anticipación")
    print("  3. Activar / desactivar semanas alternas")
    print("  4. Invertir semanas (la semana 'sí' pasa a 'no' y viceversa)")
    print("  5. Prioridad de parqueos")
    print("  0. Volver")
    print("=" * 50)


def configurar_reserva():
    cfg = cargar_reserva()
    while True:
        _mostrar_reserva(cfg)
        opcion = input("Elige una opción: ").strip()

        if opcion == "0":
            return
        if opcion == "1":
            cfg["hora_inicio"] = _pedir("Hora de inicio (HH:MM)", _hora, cfg["hora_inicio"])
        elif opcion == "2":
            modo = _pedir("Modo: 1 = anticipación, 2 = día de semana", str,
                          "1" if cfg["modo"] == "anticipacion" else "2")
            if modo == "2":
                cfg["modo"] = "dia_semana"
                cfg["dia_semana_objetivo"] = _pedir(
                    "Día (0=lunes ... 6=domingo)", _dia_semana, cfg["dia_semana_objetivo"])
            else:
                cfg["modo"] = "anticipacion"
                cfg["dias_anticipacion"] = _pedir(
                    "Días de anticipación", _dias, cfg["dias_anticipacion"])
        elif opcion == "3":
            cfg["semanas_alternas"] = not cfg["semanas_alternas"]
        elif opcion == "4":
            regla.invertir_semanas(cfg)
        elif opcion == "5":
            cfg["prioridad"] = _pedir("Parqueos en orden (coma)", _prioridad, cfg["prioridad"])
        else:
            print("Opción inválida.")
            continue

        guardar_reserva(cfg)
        print("Guardado.")


# ──────────────────────────────────────────────
# LOGS Y LIMPIEZA
# ──────────────────────────────────────────────

_CLAVES_LOG = (
    "Fecha objetivo", "seleccionado", "SELECCIONADO", "semana libre", "toca reservar",
    "Se ha reservado", "INTENTO", "RESERVA CONFIRMADA", "SIN confirmar", "[WARNING]", "[ERROR]", "[CRITICAL]",
    "Exitosos:", "Errores:", "Resultado:", "Tiempo total:",
)


def ver_ultimo_log(directorio_debug):
    logs = sorted(
        (f for f in os.listdir(directorio_debug) if f.startswith("registro_ejecucion_")),
        reverse=True,
    )
    if not logs:
        print("No hay logs de ejecución todavía.")
        return

    ruta = os.path.join(directorio_debug, logs[0])
    with open(ruta, encoding="utf-8") as f:
        lineas = f.read().splitlines()

    print(f"\nÚltimo log: {logs[0]}")
    print("-" * 50)
    for linea in lineas:
        if any(clave in linea for clave in _CLAVES_LOG):
            print(linea)
    print("-" * 50)
    if input("¿Ver el log completo? (s/n): ").strip().lower() == "s":
        print("\n".join(lineas))


def limpiar_debug(directorio_debug):
    dias = _pedir("Borrar archivos con más de N días", _dias, 7)
    limite = time.time() - dias * 86400
    conservar = {".gitkeep", "reserva_bat.log"}

    viejos = []
    for nombre in os.listdir(directorio_debug):
        ruta = os.path.join(directorio_debug, nombre)
        if nombre in conservar or not os.path.isfile(ruta):
            continue
        if os.path.getmtime(ruta) < limite:
            viejos.append(ruta)

    if not viejos:
        print(f"No hay archivos de más de {dias} días.")
        return

    total_mb = sum(os.path.getsize(r) for r in viejos) / 1_048_576
    print(f"Se borrarán {len(viejos)} archivos ({total_mb:.1f} MB) de {directorio_debug}")
    if input("¿Confirmas? (s/n): ").strip().lower() != "s":
        print("Cancelado.")
        return

    for ruta in viejos:
        os.remove(ruta)
    print(f"Borrados {len(viejos)} archivos.")


# ──────────────────────────────────────────────
# MENÚ PRINCIPAL
# ──────────────────────────────────────────────

def menu():
    auto = AutomatizacionVisual()
    opciones = {
        "1": ("Ejecutar un flujo",                     lambda: _una_sola(auto.aplicar_coordenadas_visuales)),
        "r": ("Reservar con reintentos (reserva_csi.txt)", lambda: _una_sola(lambda: auto.reservar_con_reintentos("reserva_csi.txt"))),
        "2": ("Configurar reserva (hora, fecha, semanas, parqueos)", configurar_reserva),
        "3": ("Ver último log",                        lambda: ver_ultimo_log(auto.directorio_debug)),
        "4": ("Limpiar debug (logs y capturas viejas)", lambda: limpiar_debug(auto.directorio_debug)),
        "5": ("Grabar flujo nuevo",                    lambda: auto.registrar_coordenadas_visuales("w")),
        "6": ("Continuar grabación existente",         lambda: auto.registrar_coordenadas_visuales("a")),
        "7": ("Validar un flujo",                      lambda: auto.menu_validar_archivo()),
        "8": ("Ver imágenes almacenadas",              lambda: auto.mostrar_imagenes_almacenadas()),
        "9": ("Establecer directorio base",            lambda: auto.establecer_directorio_base()),
        "0": ("Salir",                                 None),
    }

    while True:
        print("\n" + "=" * 50)
        print("VISUALPILOT")
        print(f"  Directorio base: {auto.directorio_base}")
        print("=" * 50)
        for clave, (desc, _) in opciones.items():
            print(f"  {clave}. {desc}")
        print("=" * 50)

        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            print("Saliendo...")
            return
        if opcion in opciones:
            opciones[opcion][1]()
        else:
            print("Opción inválida.")


def main():
    codigo = cli(sys.argv[1:])
    if codigo is None:
        menu()
        codigo = 0
    sys.exit(codigo)
