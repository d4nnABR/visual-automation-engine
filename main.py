"""
Punto de entrada de VisualPilot.

    python main.py                          -> menú
    python main.py run reserva_csi.txt      -> ejecuta un flujo (busca en flujos/)
    python main.py validate reserva_csi.txt -> valida sin ejecutar

Código de salida de `run`: 0 si terminó bien (o semana libre), 1 si hubo errores.
"""

from visualpilot.menu import main

if __name__ == "__main__":
    main()
