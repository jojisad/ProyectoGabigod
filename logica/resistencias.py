from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class BandSpec:
	color: str
	value: int | None = None
	multiplier: float | None = None
	tolerance: float | None = None
	ppm: int | None = None


# Base tables per IEC 60062
SIGNIFICANT_VALUES = {
	"negro": 0,
	"marrón": 1,
	"rojo": 2,
	"naranja": 3,
	"amarillo": 4,
	"verde": 5,
	"azul": 6,
	"violeta": 7,
	"gris": 8,
	"blanco": 9,
}

MULTIPLIERS = {
	"rosa": 0.001,
	"plata": 0.01,
	"oro": 0.1,
	"negro": 1,
	"marrón": 10,
	"rojo": 100,
	"naranja": 1_000,
	"amarillo": 10_000,
	"verde": 100_000,
	"azul": 1_000_000,
	"violeta": 10_000_000,
	"gris": 100_000_000,
	"blanco": 1_000_000_000,
}

TOLERANCES = {
	"marrón": 1.0,
	"rojo": 2.0,
	"verde": 0.5,
	"azul": 0.25,
	"violeta": 0.1,
	"gris": 0.05,
	"oro": 5.0,
	"plata": 10.0,
}

PPM_VALUES = {
	"marrón": 100,
	"rojo": 50,
	"naranja": 15,
	"amarillo": 25,
	"azul": 10,
	"violeta": 5,
}


def calculate_resistance_from_bands(bands: List[str]) -> Tuple[float, float | None, int | None]:
	"""
	Calcula resistencia a partir de bandas.

	- 4 bandas: D1 D2 M T
	- 5 bandas: D1 D2 D3 M T
	- 6 bandas: D1 D2 D3 M T PPM

	Devuelve (ohmios, tolerancia %, ppm)
	"""
	band_count = len(bands)
	if band_count not in (4, 5, 6):
		raise ValueError("Número de bandas no soportado")

	if band_count == 4:
		digits = [SIGNIFICANT_VALUES[bands[0]], SIGNIFICANT_VALUES[bands[1]]]
		mult = MULTIPLIERS[bands[2]]
		tol = TOLERANCES.get(bands[3])
		ppm = None
	else:
		digits = [SIGNIFICANT_VALUES[bands[0]], SIGNIFICANT_VALUES[bands[1]], SIGNIFICANT_VALUES[bands[2]]]
		mult = MULTIPLIERS[bands[3]]
		tol = TOLERANCES.get(bands[4])
		ppm = PPM_VALUES.get(bands[5]) if band_count == 6 else None

	value = int("".join(str(d) for d in digits)) * mult
	return float(value), tol, ppm


EIA96_CODE_TO_VALUE = {
    # Tabla completa EIA-96 (valores base, antes del multiplicador)
    "01": 100,
    "02": 102,
    "03": 105,
    "04": 107,
    "05": 110,
    "06": 113,
    "07": 115,
    "08": 118,
    "09": 121,
    "10": 124,
    "11": 127,
    "12": 130,
    "13": 133,
    "14": 137,
    "15": 140,
    "16": 143,
    "17": 147,
    "18": 150,
    "19": 154,
    "20": 158,
    "21": 162,
    "22": 165,
    "23": 169,
    "24": 174,
    "25": 178,
    "26": 182,
    "27": 187,
    "28": 191,
    "29": 196,
    "30": 200,
    "31": 205,
    "32": 210,
    "33": 215,
    "34": 221,
    "35": 226,
    "36": 232,
    "37": 237,
    "38": 243,
    "39": 249,
    "40": 255,
    "41": 261,
    "42": 267,
    "43": 274,
    "44": 280,
    "45": 287,
    "46": 294,
    "47": 301,
    "48": 309,
    "49": 316,
    "50": 324,
    "51": 332,
    "52": 340,
    "53": 348,
    "54": 357,
    "55": 365,
    "56": 374,
    "57": 383,
    "58": 392,
    "59": 402,
    "60": 412,
    "61": 422,
    "62": 432,
    "63": 442,
    "64": 453,
    "65": 464,
    "66": 475,
    "67": 487,
    "68": 499,
    "69": 511,
    "70": 523,
    "71": 536,
    "72": 549,
    "73": 562,
    "74": 576,
    "75": 590,
    "76": 604,
    "77": 619,
    "78": 634,
    "79": 649,
    "80": 665,
    "81": 681,
    "82": 698,
    "83": 715,
    "84": 732,
    "85": 750,
    "86": 768,
    "87": 787,
    "88": 806,
    "89": 825,
    "90": 845,
    "91": 866,
    "92": 887,
    "93": 909,
    "94": 931,
    "95": 953,
    "96": 976,
}

EIA96_MULTIPLIERS = {
	"Z": 0.001,
	"Y": 0.01,
	"R": 0.1,
	"A": 1,
	"B": 10,
	"C": 100,
	"D": 1000,
	"E": 10000,
	"F": 100000,
	"H": 1000000,
	"X": 0.01,  # some vendors
	"S": 0.001,
}


def parse_smd_eia_3digits(code: str) -> float:
	# XY Z => XY * 10^Z
	if not code.isdigit() or len(code) != 3:
		raise ValueError("Código 3 dígitos inválido")
	base = int(code[:2])
	exponent = int(code[2])
	return float(base * (10 ** exponent))


def parse_smd_eia_4digits(code: str) -> float:
	# XYZ W => XYZ * 10^W
	if not code.isdigit() or len(code) != 4:
		raise ValueError("Código 4 dígitos inválido")
	base = int(code[:3])
	exponent = int(code[3])
	return float(base * (10 ** exponent))


def parse_smd_eia_96(code: str) -> float:
	# 2 digits + letter multiplier
	if len(code) != 3:
		raise ValueError("Código EIA-96 inválido")
	base = EIA96_CODE_TO_VALUE.get(code[:2])
	if base is None:
		raise ValueError("Par de dígitos no reconocido en EIA-96")
	mult_char = code[2].upper()
	mult = EIA96_MULTIPLIERS.get(mult_char)
	if mult is None:
		raise ValueError("Multiplicador EIA-96 no reconocido")
	return float(base * mult)


def format_ohms(value_ohms: float) -> str:
	"""Formatea ohmios a cadena con unidad apropiada (Ω, kΩ, MΩ, GΩ)."""
	abs_value = abs(value_ohms)
	if abs_value >= 1_000_000_000:
		return f"{value_ohms/1_000_000_000:.3g} GΩ"
	if abs_value >= 1_000_000:
		return f"{value_ohms/1_000_000:.3g} MΩ"
	if abs_value >= 1_000:
		return f"{value_ohms/1_000:.3g} kΩ"
	return f"{value_ohms:.3g} Ω"


