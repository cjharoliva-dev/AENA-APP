# -*- coding: utf-8 -*-
"""normativa/dimensiones_exa.py
"""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class ReglaAltura:
    alturas_mm: List[int]
    alturas_por_clave: Optional[Dict[str, int]] = None


@dataclass(frozen=True)
class ReglaCartel:
    margen_lateral_mm: float
    margen_vertical_mm: float
    borde_lateral_mm: float
    borde_vertical_mm: float


ALTURAS_EXA: Dict[str, ReglaAltura] = {
    "2.7": ReglaAltura(
        alturas_mm=[2000, 3000, 4000],
        alturas_por_clave={
            "A": 2000, "B": 2000,
            "C": 4000, "D": 4000, "E": 4000, "F": 4000,
        },
    ),
}


REGLAS_CARTEL: Dict[str, ReglaCartel] = {
    "2.7": ReglaCartel(
        margen_lateral_mm=500.0,
        margen_vertical_mm=600.0,
        borde_lateral_mm=250.0,
        borde_vertical_mm=500.0,
    ),
}


def regla_cartel(codigo_ficha: str) -> ReglaCartel:
    base = (codigo_ficha or "").split("_")[0].strip()
    if base not in REGLAS_CARTEL:
        raise KeyError(f"No hay regla de cartel definida para ficha '{base}'")
    return REGLAS_CARTEL[base]

# 2.6 y 2.8: misma geometría base que 2.7 (márgenes iguales)
REGLAS_CARTEL["2.6"] = REGLAS_CARTEL["2.7"]
REGLAS_CARTEL["2.8"] = REGLAS_CARTEL["2.7"]

# Si usas alturas por clave, clona también ALTURAS_EXA
ALTURAS_EXA["2.6"] = ALTURAS_EXA["2.7"]
ALTURAS_EXA["2.8"] = ALTURAS_EXA["2.7"]