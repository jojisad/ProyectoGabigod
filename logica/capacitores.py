from __future__ import annotations

from typing import Dict


UNIDADES_CAP = [
	("F", 1.0),
	("mF", 1e-3),
	("µF", 1e-6),
	("nF", 1e-9),
	("pF", 1e-12),
]


def formatear_farads(valor_f: float) -> str:
	abs_val = abs(valor_f)
	for sufijo, factor in UNIDADES_CAP:
		if abs_val >= factor:
			return f"{valor_f/factor:.3g} {sufijo}"
	return f"{valor_f:.3g} F"


def parsear_capacitor_eia_tres_digitos(codigo: str) -> float:
	"""XYZ => XY * 10^Z en pF"""
	if not codigo.isdigit() or len(codigo) != 3:
		raise ValueError("Código 3 dígitos inválido")
	base = int(codigo[:2])
	exp = int(codigo[2])
	valor_pf = base * (10 ** exp)
	return float(valor_pf) * 1e-12


def parsear_capacitor_eia_cuatro_digitos(codigo: str) -> float:
	"""WXYZ => WXY * 10^Z en pF"""
	if not codigo.isdigit() or len(codigo) != 4:
		raise ValueError("Código 4 dígitos inválido")
	base = int(codigo[:3])
	exp = int(codigo[3])
	valor_pf = base * (10 ** exp)
	return float(valor_pf) * 1e-12


LETRAS_TOLERANCIA = {"B": 0.1, "C": 0.25, "D": 0.5, "F": 1.0, "G": 2.0, "J": 5.0, "K": 10.0, "M": 20.0, "Z": None}


def parsear_capacitor_eia_cuatro_mixto(codigo: str) -> tuple[float, float | None]:
    """
    Acepta:
    - [0-9R]{3}[0-9]  → XYZ * 10^W pF (R decimal en XYZ)
    - [0-9R]{3}[BCDFGJKMZ] → significativos (con R como decimal) y letra de tolerancia (EIA-198)

    Devuelve (valor_en_faradios, tolerancia_porcentaje | None)
    """
    if len(codigo) != 4:
        raise ValueError("Código debe tener 4 caracteres")
    codigo = codigo.upper()
    sig = codigo[:3]
    suf = codigo[3]

    # Interpretar significativos con 'R' como decimal, en pF
    if 'R' in sig:
        try:
            significativos_pf = float(sig.replace('R', '.'))
        except Exception as exc:
            raise ValueError("Significativos no válidos") from exc
    else:
        if not sig.isdigit():
            raise ValueError("Significativos no válidos")
        significativos_pf = float(int(sig))

    # Caso multiplicador numérico
    if suf.isdigit():
        exp = int(suf)
        valor_pf = significativos_pf * (10 ** exp)
        return float(valor_pf) * 1e-12, None

    # Caso letra de tolerancia
    tol = LETRAS_TOLERANCIA.get(suf)
    if suf in LETRAS_TOLERANCIA:
        # Cuando es letra, Digi-Key interpreta los significativos directamente en pF
        valor_pf = significativos_pf
        return float(valor_pf) * 1e-12, tol

    raise ValueError("Sufijo no reconocido en código de 4 caracteres")


def formatear_mf_y_nf(valor_f: float) -> str:
    mf = valor_f * 1e3
    nf = valor_f * 1e9
    return f"{mf:.6g} mF   |   {nf:.6g} nF"


def formatear_unidades_multiples(valor_f: float) -> str:
    """Devuelve una cadena con el mismo valor en µF, nF, pF y mF."""
    uf = valor_f * 1e6
    nf = valor_f * 1e9
    pf = valor_f * 1e12
    mf = valor_f * 1e3
    return f"µF: {uf:.6g}   |   nF: {nf:.6g}   |   pF: {pf:.6g}   |   mF: {mf:.6g}"


# EIA-198: letras para tolerancia (ejemplos comunes)
TOLERANCIAS_EIA198: Dict[str, float] = {
	"F": 1.0,  # ±1%
	"G": 2.0,
	"J": 5.0,
	"K": 10.0,
	"M": 20.0,
}


def obtener_rango_por_tolerancia(valor_f: float, tol_porcentaje: float) -> tuple[float, float]:
	delta = valor_f * (tol_porcentaje / 100.0)
	return valor_f - delta, valor_f + delta


# EIA-198: tabla de significativos por letra (serie E24 típica)
EIA198_LETRA_A_SIGNIFICATIVO = {
    # Mayúsculas
    "A": 1.0, "B": 1.1, "C": 1.2, "D": 1.3, "E": 1.5, "F": 1.6,
    "G": 1.8, "H": 2.0, "J": 2.2, "K": 2.4, "L": 2.7, "M": 3.0,
    "N": 3.3, "P": 3.6, "Q": 3.9, "R": 4.3, "S": 4.7, "T": 5.1,
    "U": 5.6, "V": 6.2, "W": 6.8, "X": 7.5, "Y": 8.2, "Z": 9.1,
}
# Aceptar también minúsculas como alias
EIA198_LETRA_A_SIGNIFICATIVO.update({k.lower(): v for k, v in list(EIA198_LETRA_A_SIGNIFICATIVO.items())})

# EIA-198: multiplicador por dígito (en Faradios) según referencia Digi-Key
EIA198_DIGITO_A_MULTIPLICADOR_F = {
    # 0..7 escalan desde 1 pF a 10 µF, 9 y 8 son sub-pF
    "0": 1e-12,   # 1 pF
    "1": 10e-12,  # 10 pF
    "2": 100e-12, # 100 pF
    "3": 1e-9,    # 1 nF
    "4": 10e-9,   # 10 nF
    "5": 100e-9,  # 100 nF
    "6": 1e-6,    # 1 µF
    "7": 10e-6,   # 10 µF
    "8": 1e-14,   # 0.01 pF
    "9": 1e-13,   # 0.1 pF
}


def parsear_capacitor_eia_198(codigo: str) -> float:
    """
    Decodifica código EIA-198 de 2 caracteres: Letra + Dígito.
    - Letra: significativos (serie E24)
    - Dígito: multiplicador absoluto en Faradios (tabla anterior)

    Ejemplos:
    - U7 => 5.6 × 10 µF = 56 µF
    - B9 => 1.1 × 0.1 pF = 0.11 pF
    - C2 => 1.2 × 100 pF = 120 pF
    """
    if len(codigo) != 2:
        raise ValueError("Código EIA-198 debe tener 2 caracteres")
    letra, digito = codigo[0], codigo[1]
    base = EIA198_LETRA_A_SIGNIFICATIVO.get(letra)
    if base is None:
        raise ValueError("Letra no válida en EIA-198")
    mult = EIA198_DIGITO_A_MULTIPLICADOR_F.get(digito)
    if mult is None:
        raise ValueError("Dígito no válido en EIA-198")
    return float(base * mult)


