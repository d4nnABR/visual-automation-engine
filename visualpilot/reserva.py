from datetime import date, datetime, timedelta

from .ajustes import DIAS_SEMANA, MESES
from .config import cargar_reserva


def _leer_config(overrides=None):
    cfg = cargar_reserva()
    if overrides:
        cfg.update(overrides)
    return cfg


def lunes_de(fecha):
    return fecha - timedelta(days=fecha.weekday())


def es_semana_on(fecha, cfg=None):
    """True si la semana (lunes-domingo) de `fecha` es una semana "sí"."""
    cfg = _leer_config(cfg)
    ancla = lunes_de(datetime.strptime(cfg["fecha_ancla_semana_on"], "%Y-%m-%d").date())
    semanas = (lunes_de(fecha) - ancla).days // 7
    return semanas % 2 == 0


def toca_reservar(fecha, cfg=None):
    """False solo si hay semanas alternas y `fecha` cae en semana "no"."""
    cfg = _leer_config(cfg)
    return not cfg.get("semanas_alternas") or es_semana_on(fecha, cfg)


def calcular_fecha_objetivo(hoy=None, cfg=None):
    """
    Fecha a reservar.

    Modos (cfg["modo"]):
      - "anticipacion" (por defecto): hoy + `dias_anticipacion`. Es la fecha que
        la app habilita hoy a la hora de inicio (una por día). Ej.: 14/09 -> 22/09.
      - "dia_semana": el próximo `dia_semana_objetivo` después de hoy; con semanas
        alternas, el primero que caiga en semana "sí".

    Con modo "anticipacion" la fecha no se mueve: si cae en semana "no", el flujo
    termina en VERIFICAR_SEMANA sin reservar.
    """
    cfg = _leer_config(cfg)
    hoy = hoy or date.today()

    if cfg.get("modo", "anticipacion") == "dia_semana":
        delta = (int(cfg["dia_semana_objetivo"]) - hoy.weekday()) % 7 or 7
        candidato = hoy + timedelta(days=delta)
        while not toca_reservar(candidato, cfg):
            candidato += timedelta(days=7)
        return candidato

    return hoy + timedelta(days=int(cfg.get("dias_anticipacion", 8)))


def invertir_semanas(cfg):
    """Cambia qué semanas son "sí" (mueve el ancla una semana). Devuelve cfg."""
    ancla = datetime.strptime(cfg["fecha_ancla_semana_on"], "%Y-%m-%d").date()
    cfg["fecha_ancla_semana_on"] = (lunes_de(ancla) + timedelta(days=7)).isoformat()
    return cfg


def proximas_semanas(n=4, hoy=None, cfg=None):
    """[(lunes, domingo, es_on)] desde la semana actual."""
    cfg = _leer_config(cfg)
    lunes = lunes_de(hoy or date.today())
    return [
        (lunes + timedelta(weeks=i), lunes + timedelta(weeks=i, days=6),
         es_semana_on(lunes + timedelta(weeks=i), cfg))
        for i in range(n)
    ]


def nombre_mes(fecha):
    return MESES[fecha.month - 1]


def nombre_dia(fecha):
    return DIAS_SEMANA[fecha.weekday()]


def fecha_del_ciclo(ahora=None, hora_inicio=None, ventana_max_horas=12):
    """
    Día en que corre la reserva que toca (la de la próxima hora de inicio).
    Mismo criterio que WAIT_UNTIL: a las 23:58 la de 00:02 es la de MAÑANA;
    a las 08:00 (las 00:02 quedaron atrás hace más de 12 h) es la de HOY.
    """
    ahora = ahora or datetime.now()
    hora_inicio = hora_inicio or cargar_reserva()["hora_inicio"]
    inicio = datetime.combine(ahora.date(), datetime.strptime(hora_inicio, "%H:%M:%S").time())
    if inicio <= ahora:
        inicio += timedelta(days=1)
    if (inicio - ahora).total_seconds() > ventana_max_horas * 3600:
        inicio -= timedelta(days=1)
    return inicio.date()


def buscar_log_exitoso(directorio_debug, fecha_objetivo, dias_atras=15):
    """
    Ruta del primer registro_ejecucion_*.txt que terminó en "Resultado: OK" para
    `fecha_objetivo` (reservada o semana libre), o None. Solo mira los logs de
    los últimos `dias_atras` días.
    """
    import os
    import re
    import time

    patron = re.compile(rf"Fecha (objetivo: )?{fecha_objetivo.isoformat()}\b")
    limite = time.time() - dias_atras * 86400
    try:
        nombres = sorted(os.listdir(directorio_debug), reverse=True)
    except OSError:
        return None
    for nombre in nombres:
        if not (nombre.startswith("registro_ejecucion_") and nombre.endswith(".txt")):
            continue
        ruta = os.path.join(directorio_debug, nombre)
        if os.path.getmtime(ruta) < limite:
            continue
        try:
            with open(ruta, encoding="utf-8", errors="replace") as f:
                contenido = f.read()
        except OSError:
            continue
        if "Resultado: OK" in contenido and patron.search(contenido):
            return ruta
    return None
