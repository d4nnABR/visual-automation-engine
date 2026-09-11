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
    Devuelve la próxima fecha a reservar:
    el primer día del `dia_semana_objetivo` a partir de hoy + `dias_anticipacion`
    que caiga en una semana habilitada (alternas).
    """
    cfg = _leer_config(cfg)
    hoy = hoy or date.today()
    dia_objetivo = int(cfg["dia_semana_objetivo"])

    base = hoy + timedelta(days=int(cfg["dias_anticipacion"]))
    delta = (dia_objetivo - base.weekday()) % 7
    candidato = base + timedelta(days=delta)

    while not es_semana_on(candidato, cfg):
        candidato += timedelta(days=7)

    return candidato


def calcular_fecha_objetivo_str(hoy=None, cfg=None):
    f = calcular_fecha_objetivo(hoy, cfg)
    return f.strftime("%Y-%m-%d")


def nombre_mes(fecha):
    return MESES[fecha.month - 1]


def nombre_dia(fecha):
    return DIAS_SEMANA[fecha.weekday()]
