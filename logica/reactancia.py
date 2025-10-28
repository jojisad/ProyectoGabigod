import math
from typing import Optional
# Reutilizamos el formateador de ley_ohm
from .ley_ohm import formatear_valor

def calcular_reactancia_capacitiva(frecuencia: float, capacitancia: float) -> float:
    """
    Calcula la Reactancia Capacitiva (Xc = 1 / (2 * pi * f * C)).
    frecuencia (f) en Hertz (Hz).
    capacitancia (C) en Faradios (F).
    Devuelve Xc en Ohmios (Ω).
    Lanza ValueError si f <= 0 o C <= 0.
    """
    if frecuencia <= 0:
        raise ValueError("La frecuencia debe ser mayor que cero.")
    if capacitancia <= 0:
        raise ValueError("La capacitancia debe ser mayor que cero.")
    
    try:
        omega = 2 * math.pi * frecuencia
        xc = 1 / (omega * capacitancia)
        return xc
    except ZeroDivisionError:
        # Aunque ya validamos C > 0, por si acaso.
        raise ValueError("Error de cálculo (división por cero). Verifique las entradas.")
    except Exception as e:
        raise ValueError(f"Error calculando Xc: {e}")

def calcular_reactancia_inductiva(frecuencia: float, inductancia: float) -> float:
    """
    Calcula la Reactancia Inductiva (Xl = 2 * pi * f * L).
    frecuencia (f) en Hertz (Hz).
    inductancia (L) en Henrios (H).
    Devuelve Xl en Ohmios (Ω).
    Lanza ValueError si f < 0 o L < 0.
    """
    # Permitimos frecuencia = 0 (Xl = 0) y L = 0 (Xl = 0)
    if frecuencia < 0:
        raise ValueError("La frecuencia no puede ser negativa.")
    if inductancia < 0:
        raise ValueError("La inductancia no puede ser negativa.")
        
    try:
        omega = 2 * math.pi * frecuencia
        xl = omega * inductancia
        return xl
    except Exception as e:
        raise ValueError(f"Error calculando Xl: {e}")