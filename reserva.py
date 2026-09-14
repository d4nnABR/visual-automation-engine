from datetime import date, datetime, timedelta

from ajustes import RESERVA, DIAS_SEMANA, MESES


def _leer_config(overrides=None):
    cfg = dict(RESERVA)
    if overrides:
        cfg.update(overrides)
    return cfg


def es_semana_on(fecha, cfg=None):
    """True si la semana (lunes-domingo) de `fecha` es una semana habilitada."""
    cfg = _leer_config(cfg)
    ancla = datetime.strptime(cfg["fecha_ancla_semana_on"], "%Y-%m-%d").date()
    ancla = ancla - timedelta(days=ancla.weekday())
    lunes = fecha - timedelta(days=fecha.weekday())
    semanas = (lunes - ancla).days // 7
    return semanas % 2 == 0


def calcular_fecha_objetivo(hoy=None, cfg=None):
    """
    Fecha a reservar.

    Modos (cfg["modo"]):
      - "anticipacion" (por defecto): hoy + `dias_anticipacion`. Es la fecha que
        la app habilita hoy a las 00:02 (una por dia). Ej.: 14/09 -> 22/09,
        15/09 -> 23/09.
      - "dia_semana": el primer `dia_semana_objetivo` despues de hoy que caiga en
        una semana habilitada (alternas).
    """
    cfg = _leer_config(cfg)
    hoy = hoy or date.today()

    if cfg.get("modo", "anticipacion") == "dia_semana":
        dia_objetivo = int(cfg["dia_semana_objetivo"])
        delta = (dia_objetivo - hoy.weekday()) % 7
        if delta == 0:
            delta = 7
        candidato = hoy + timedelta(days=delta)
        while not es_semana_on(candidato, cfg):
            candidato += timedelta(days=7)
        return candidato

    return hoy + timedelta(days=int(cfg.get("dias_anticipacion", 8)))


def calcular_fecha_objetivo_str(hoy=None, cfg=None):
    f = calcular_fecha_objetivo(hoy, cfg)
    return f.strftime("%Y-%m-%d")


def nombre_mes(fecha):
    return MESES[fecha.month - 1]


def nombre_dia(fecha):
    return DIAS_SEMANA[fecha.weekday()]
