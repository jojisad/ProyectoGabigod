# logica/divisor_voltaje.py
from typing import Optional
# Reutilizamos la función de formato de ley_ohm
from .ley_ohm import formatear_valor

def calcular_divisor_voltaje(voltaje_entrada: Optional[float], r1: Optional[float], r2: Optional[float]) -> Optional[float]:
    """
    Calcula el voltaje de salida (Vout) de un divisor de voltaje simple.
    Vout = Vin * (R2 / (R1 + R2))
    Requiere los tres valores (Vin, R1, R2).
    Devuelve Vout o lanza ValueError si la entrada es inválida.
    """
    if voltaje_entrada is None or r1 is None or r2 is None:
        raise ValueError("Se necesitan los valores de Voltaje de Entrada, R1 y R2.")

    if r1 < 0 or r2 < 0:
         raise ValueError("Las resistencias R1 y R2 deben ser valores positivos.")
         
    # Comprobar división por cero (aunque improbable con resistencias positivas)
    if (r1 + r2) == 0:
        # Podríamos devolver 0 o Vin dependiendo de la convención, pero mejor lanzar error.
        raise ValueError("La suma de R1 y R2 no puede ser cero.")

    try:
        voltaje_salida = voltaje_entrada * (r2 / (r1 + r2))
        return voltaje_salida
    except Exception as e:
        raise ValueError(f"Error en el cálculo del divisor: {e}") from e