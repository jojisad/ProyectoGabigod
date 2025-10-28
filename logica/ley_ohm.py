# logica/ley_ohm.py
from typing import Tuple, Optional

def calcular_ley_ohm(voltaje: Optional[float] = None, corriente: Optional[float] = None, resistencia: Optional[float] = None) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calcula la Ley de Ohm (V = I * R).
    Requiere exactamente dos de los tres valores (voltaje, corriente, resistencia).
    Devuelve una tupla (voltaje, corriente, resistencia), donde el valor faltante es el calculado.
    Lanza ValueError si la entrada es inválida (ej. no hay exactamente dos valores, división por cero).
    """
    valores_conocidos = sum(1 for v in [voltaje, corriente, resistencia] if v is not None)

    if valores_conocidos != 2:
        raise ValueError("Se necesitan exactamente dos valores (V, I, R) para calcular el tercero.")

    try:
        if voltaje is None and corriente is not None and resistencia is not None:
            # Calcular Voltaje (V = I * R)
            voltaje_calculado = corriente * resistencia
            return voltaje_calculado, corriente, resistencia
        elif corriente is None and voltaje is not None and resistencia is not None:
            # Calcular Corriente (I = V / R)
            if resistencia == 0:
                raise ValueError("División por cero: La resistencia no puede ser cero al calcular la corriente.")
            corriente_calculada = voltaje / resistencia
            return voltaje, corriente_calculada, resistencia
        elif resistencia is None and voltaje is not None and corriente is not None:
            # Calcular Resistencia (R = V / I)
            if corriente == 0:
                # Podría considerarse resistencia infinita, pero para simplificar, lanzamos error
                raise ValueError("División por cero: La corriente no puede ser cero al calcular la resistencia.")
            resistencia_calculada = voltaje / corriente
            return voltaje, corriente, resistencia_calculada
        else:
            # Esto no debería ocurrir si la lógica anterior es correcta
            raise ValueError("Combinación de entradas inválida.")
    except Exception as e:
        # Re-lanzar cualquier otro error inesperado
        raise ValueError(f"Error en el cálculo: {e}") from e

def formatear_valor(valor: Optional[float], unidad: str) -> str:
    """Formatea un valor numérico con su unidad, manejando None."""
    if valor is None:
        return ""
    
    # Podríamos añadir prefijos (k, M, m, µ, etc.) aquí si quisiéramos, similar a formatear_ohmios
    # Por ahora, un formato simple:
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:.3g} M{unidad}"
    if abs(valor) >= 1_000:
        return f"{valor / 1_000:.3g} k{unidad}"
    if abs(valor) < 0.001 and abs(valor) != 0:
         if abs(valor) < 0.000001:
              return f"{valor * 1_000_000_000:.3g} n{unidad}"
         return f"{valor * 1_000:.3g} m{unidad}"
         
    return f"{valor:.3g} {unidad}"