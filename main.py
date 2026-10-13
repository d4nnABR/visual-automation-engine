"""
Punto de entrada de VisualPilot.

    python main.py                          -> menú
    python main.py run reserva_csi.txt      -> ejecuta un flujo (busca en flujos/)
    python main.py reservar reserva_csi.txt -> reserva con confirmación visual y
                                               hasta 5 intentos (lo usa auto.bat)
    python main.py validate reserva_csi.txt -> valida sin ejecutar

Código de salida de `run`/`reservar`: 0 si terminó bien (o semana libre), 1 si no.
"""

from visualpilot.menu import main

if __name__ == "__main__":
    main()
