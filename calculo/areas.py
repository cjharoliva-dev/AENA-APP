# -*- coding: utf-8 -*-
"""
calculo/areas.py — MÉTODO NUEVO (solo 2.7)

Cálculo de superficies para señalización AN 2.1 (ficha 2.7).

"""

import os
import sys
import json
from typing import Dict, Any, List, Tuple

def resource_path(rel_path: str) -> str:
    """
    Devuelve ruta correcta tanto en desarrollo como en .exe (PyInstaller).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.getcwd())
    return os.path.join(base, rel_path)

JSON_DEFAULT = "datos/an21_caracteres_base.json"  


def cargar_datos(ruta_json: str = JSON_DEFAULT) -> dict:
    ruta = resource_path(ruta_json)
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def tabla_caracteres(db: Dict[str, Any]) -> Dict[str, Any]:
    """
    Admite JSON unificado (caracteres) o legado (numeros).
    """
    t = db.get("caracteres") or db.get("numeros")
    if not isinstance(t, dict):
        raise ValueError("El JSON debe contener un diccionario 'caracteres' o 'numeros'.")
    return t


def calcular_area_texto_mm2(tokens: List[str], mm_por_base: float, db: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Suma área de pintura del texto en mm².

    - area_base se asume en unidades_base² (según tu CAD).
    - mm_por_base convierte unidades_base -> mm
      ⇒ factor_area = (mm_por_base)^2

    Devuelve:
      (area_mm2, tokens_sin_area_base)
    """
    t = tabla_caracteres(db)
    faltan: List[str] = []
    total_base2 = 0.0

    for tok in tokens:
        if tok == " ":
            continue
        info = t.get(tok)
        if info is None:
            
            continue
        if "area_base" not in info:
            faltan.append(tok)
            continue
        total_base2 += float(info["area_base"])

    area_mm2 = total_base2 * (float(mm_por_base) ** 2)
    return area_mm2, sorted(set(faltan))


def areas_27(cartel: Dict[str, Any], tokens: List[str], ruta_json: str = JSON_DEFAULT) -> Dict[str, Any]:
    """
    Calcula áreas para ficha 2.7.

    cartel debe traer:
      - cartel['fondo']['ancho_mm'], cartel['fondo']['alto_mm']
      - cartel['exterior']['ancho_mm'], cartel['exterior']['alto_mm']
      - cartel['geometria_texto']['factor'] (mm_por_base) o ['scale'] (base->m)
    """
    db = cargar_datos(ruta_json)

    fondo = cartel.get("fondo", {}) or {}
    exterior = cartel.get("exterior", {}) or {}

    W_int = float(fondo.get("ancho_mm", 0.0) or 0.0)
    H_int = float(fondo.get("alto_mm", 0.0) or 0.0)
    W_ext = float(exterior.get("ancho_mm", 0.0) or 0.0)
    H_ext = float(exterior.get("alto_mm", 0.0) or 0.0)

    area_fondo_mm2 = W_int * H_int
    area_exterior_mm2 = W_ext * H_ext
    area_borde_mm2 = max(area_exterior_mm2 - area_fondo_mm2, 0.0)

    
    geo = cartel.get("geometria_texto", {}) or {}
    mm_por_base = float(geo.get("factor", 0.0) or 0.0)

    
    if mm_por_base <= 0.0:
        scale = geo.get("scale")
        if scale:
            mm_por_base = float(scale) * 1000.0

    if mm_por_base > 0.0:
        area_texto_mm2, tokens_sin_area = calcular_area_texto_mm2(tokens, mm_por_base, db)
    else:
        area_texto_mm2, tokens_sin_area = 0.0, sorted(set([t for t in tokens if t != " "]))

   
    
    colores = cartel.get("colores", {}) or {}
    
    areas_color_mm2 = {}
    
    def suma(color, valor):
        if not color:
            return
        areas_color_mm2[color] = areas_color_mm2.get(color, 0.0) + valor
    
    # fondo SIN texto
    area_fondo_puro = max(area_fondo_mm2 - area_texto_mm2, 0.0)
    
    suma(colores.get("fondo"), area_fondo_puro)
    suma(colores.get("texto"), area_texto_mm2)
    suma(colores.get("borde"), area_borde_mm2)
    
    # conversión a m²
    areas_color_m2 = {
        color: val / 1_000_000.0
        for color, val in areas_color_mm2.items()
    }
    
    return {
        "colores_m2": areas_color_m2,
    
        # DEBUG
        "detalle": {
            "texto_mm2": area_texto_mm2,
            "fondo_mm2": area_fondo_mm2,
            "borde_mm2": area_borde_mm2,
        },
    
        "tokens_sin_area_base": tokens_sin_area,
    }

def areas_texto_rectangular(cartel: dict, tokens: list, colores: dict, ruta_json: str = JSON_DEFAULT) -> dict:
    """
    Áreas genéricas para carteles rectangulares de texto:
    - Fondo = rectángulo interior
    - Borde = exterior - interior (si existe)
    - Texto = suma por tokens (mm²)
    Reparte por colores según `colores` (fondo/texto/borde).
    """
    db = cargar_datos(ruta_json)

    # Dimensiones en mm (cartel_exa40 ya las devuelve)
    W_int, H_int = cartel["dimensiones"]["interior"]
    W_ext, H_ext = cartel["dimensiones"]["exterior"]

    area_fondo_mm2 = float(W_int) * float(H_int)
    area_borde_mm2 = float(W_ext) * float(H_ext) - area_fondo_mm2

    # texto
    mm_por_base = float(cartel.get("geometria_texto", {}).get("factor", 0.0) or 0.0)
    area_texto_mm2, tokens_sin = calcular_area_texto_mm2(tokens, mm_por_base, db)

    # Reparto por colores (dinámico)
    c_fondo = (colores or {}).get("fondo", "yellow")
    c_texto = (colores or {}).get("texto", "black")
    c_borde = (colores or {}).get("borde", "black")

    colores_mm2 = {}
    colores_mm2[c_texto] = colores_mm2.get(c_texto, 0.0) + area_texto_mm2
    colores_mm2[c_fondo] = colores_mm2.get(c_fondo, 0.0) + max(0.0, area_fondo_mm2 - area_texto_mm2)
    if area_borde_mm2 > 0:
        colores_mm2[c_borde] = colores_mm2.get(c_borde, 0.0) + area_borde_mm2

    colores_m2 = {k: v / 1e6 for k, v in colores_mm2.items()}

    return {
        "colores_mm2": colores_mm2,
        "colores_m2": colores_m2,
        "detalle": {
            "texto_mm2": area_texto_mm2,
            "fondo_mm2": area_fondo_mm2,
            "borde_mm2": area_borde_mm2,
        },
        "tokens_sin_area_base": tokens_sin,
    }