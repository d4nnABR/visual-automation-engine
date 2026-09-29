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
