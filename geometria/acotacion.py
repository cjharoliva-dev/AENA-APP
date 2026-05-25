# -*- coding: utf-8 -*-
"""
geometria/acotacion.py

Acotación para señales EXA-40 (modo nuevo)

- Usa directamente elementos del motor (sin JSON)
- Calcula:
  - separación negro-a-negro
  - márgenes
  - dimensiones
  - bordes
"""

from typing import Dict, Any, List


def acotar_cartel_27(cartel: Dict[str, Any]) -> Dict[str, Any]:

    # -------------------------------------------------
    # DATOS BÁSICOS
    # -------------------------------------------------

    elementos = cartel.get("elementos", [])
    h_mm = float(cartel.get("h_mm", 0.0) or 0.0)

    fondo = cartel.get("fondo", {})
    exterior = cartel.get("exterior", {})
    borde = cartel.get("borde", {})

    W_int = float(fondo.get("ancho_mm", 0.0) or 0.0)
    H_int = float(fondo.get("alto_mm", 0.0) or 0.0)
    W_ext = float(exterior.get("ancho_mm", 0.0) or 0.0)
    H_ext = float(exterior.get("alto_mm", 0.0) or 0.0)

    borde_lat = float(borde.get("borde_lateral_mm", 0.0) or 0.0)
    borde_ver = float(borde.get("borde_vertical_mm", 0.0) or 0.0)

    # -------------------------------------------------
    # LÍMITES DEL FONDO
    # -------------------------------------------------

    fondo_left = borde_lat
    fondo_top = borde_ver
    fondo_right = borde_lat + W_int
    fondo_bottom = borde_ver + H_int

    # -------------------------------------------------
    # 1) ESPACIADO NEGRO-A-NEGRO
    # -------------------------------------------------

    gaps: List[Dict[str, Any]] = []

    for i in range(len(elementos) - 1):

        a = elementos[i]
        b = elementos[i + 1]

        left_a = a["x"] + a["x_max"]
        right_b = b["x"] + b["x_min"]

        gap = right_b - left_a

        gaps.append({
            "entre": f"{a['char']}-{b['char']}",
            "distancia_mm": gap
        })

    # -------------------------------------------------
    # 2) MÁRGENES (respecto al fondo)
    # -------------------------------------------------

    margenes = {
        "izq": None,
        "der": None,
        "sup": None,
        "inf": None,
    }

    if elementos:
        first = elementos[0]
        last = elementos[-1]

        left_texto = first["x"] + first["x_min"]
        right_texto = last["x"] + last["x_max"]

        margenes["izq"] = left_texto - fondo_left
        margenes["der"] = fondo_right - right_texto

        # vertical: constante en 2.7
        margenes["sup"] = (cartel["elementos"][0]["y"] - fondo_top)
        margenes["inf"] = (fondo_bottom - (cartel["elementos"][0]["y"] + h_mm))

    # -------------------------------------------------
    # 3) DIMENSIONES
    # -------------------------------------------------

    dimensiones = {
        "interior": (W_int, H_int),
        "exterior": (W_ext, H_ext),
        "texto": float(cartel.get("inscripcion", {}).get("ancho_mm", 0.0)),
    }

    # -------------------------------------------------
    # 4) BORDES
    # -------------------------------------------------

    bordes = {
        "lateral": borde_lat,
        "vertical": borde_ver,
    }

    # -------------------------------------------------
    # SALIDA
    # -------------------------------------------------

    return {
        "dimensiones": dimensiones,
        "espaciado": gaps,
        "margenes": margenes,
        "bordes": bordes,
    }