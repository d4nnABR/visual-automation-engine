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


_FECHA_EN_LOG = r"Fecha (?:objetivo: )?(\d{4}-\d{2}-\d{2})"
_EVIDENCIA_RESERVA = (
    "RESERVA CONFIRMADA",                  # verificación visual (reservar)
    "Texto encontrado: 'Se ha reservado'",  # logs anteriores a la verificación
    "cae en semana libre",                 # no tocaba reservar: también es OK
)


def log_exitoso_para(contenido, fecha_objetivo):
    """
    True si el log COMPLETO de una ejecución prueba que `fecha_objetivo` quedó
    resuelta. Exige las cuatro cosas, para no tomar por buena una reserva de
    otro día ni un log que otro proceso todavía está escribiendo:
      1. el log está terminado (tiene el RESUMEN DE EJECUCIÓN);
      2. la ÚLTIMA línea "Resultado:" es OK;
      3. todas las fechas que menciona son `fecha_objetivo` (ninguna otra);
      4. hay evidencia de reserva (confirmación / "Se ha reservado" / semana libre).
    """
    import re

    if "RESUMEN DE EJECUCIÓN" not in contenido:
        return False
    resultados = [l for l in contenido.splitlines() if "Resultado:" in l]
    if not resultados or "Resultado: OK" not in resultados[-1]:
        return False
    fechas = set(re.findall(_FECHA_EN_LOG, contenido))
    if fechas != {fecha_objetivo.isoformat()}:
        return False
    return any(e in contenido for e in _EVIDENCIA_RESERVA)


def buscar_log_exitoso(directorio_debug, fecha_objetivo, dias_atras=15):
    """
    Ruta del registro_ejecucion_*.txt más reciente que prueba (leído entero, ver
    `log_exitoso_para`) que `fecha_objetivo` ya quedó reservada o era semana
    libre, o None. Solo mira los logs de los últimos `dias_atras` días.
    """
    import os
    import time

    limite = time.time() - dias_atras * 86400
    try:
        nombres = sorted(os.listdir(directorio_debug), reverse=True)
    except OSError:
        return None
    for nombre in nombres:
        if not (nombre.startswith("registro_ejecucion_") and nombre.endswith(".txt")):
            continue
        ruta = os.path.join(directorio_debug, nombre)
        try:
            if os.path.getmtime(ruta) < limite:
                continue
            with open(ruta, encoding="utf-8", errors="replace") as f:
                contenido = f.read()
        except OSError:
            continue
        if log_exitoso_para(contenido, fecha_objetivo):
            return ruta
    return None


# ──────────────────────────────────────────────
# MARCA DE ÉXITO: debug/reservas_ok/<fecha>.ok
# ──────────────────────────────────────────────

SUBDIR_MARCAS = "reservas_ok"


def _ruta_marca(directorio_debug, fecha_objetivo):
    import os
    return os.path.join(directorio_debug, SUBDIR_MARCAS, f"{fecha_objetivo.isoformat()}.ok")


def marcar_exitosa(directorio_debug, fecha_objetivo, estado, ruta_log=None):
    """
    Deja constancia de que `fecha_objetivo` quedó resuelta (confirmada o semana
    libre). Escritura atómica (temporal + os.replace): quien la lea ve el archivo
    completo o no lo ve, nunca a medias. Devuelve la ruta de la marca.
    """
    import os
    ruta = _ruta_marca(directorio_debug, fecha_objetivo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    temporal = f"{ruta}.{os.getpid()}.tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        f.write(f"fecha_objetivo={fecha_objetivo.isoformat()}\n")
        f.write(f"estado={estado}\n")
        f.write(f"cuando={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"log={os.path.basename(ruta_log) if ruta_log else ''}\n")
    os.replace(temporal, ruta)
    return ruta


def marca_exitosa(directorio_debug, fecha_objetivo):
    """Ruta de la marca de `fecha_objetivo` si existe, o None."""
    import os
    ruta = _ruta_marca(directorio_debug, fecha_objetivo)
    return ruta if os.path.isfile(ruta) else None


def ya_resuelta(directorio_debug, fecha_objetivo):
    """
    Prueba de que `fecha_objetivo` ya quedó reservada (o era semana libre):
    primero la marca; si no hay, un log antiguo que lo pruebe (ver
    `log_exitoso_para`). Devuelve la ruta que lo prueba, o None.
    """
    return marca_exitosa(directorio_debug, fecha_objetivo) or \
        buscar_log_exitoso(directorio_debug, fecha_objetivo)
