# -*- coding: utf-8 -*-
"""
normativa/cartel_exa40.py

"""

from typing import Dict, Any, Optional

from normativa.fichas import obtener_ficha, TipoSenal, MotorTexto
from normativa.dimensiones_exa import regla_cartel
from geometria.motor_texto_AN21 import componer_texto


def construir_cartel(
    codigo_ficha: str,
    texto: str,
    h_mm: int,
    contexto: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    ficha = obtener_ficha(codigo_ficha)

    # -------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------

    if ficha.tipo != TipoSenal.TEXTO:
        raise NotImplementedError("Solo se soportan señales de tipo TEXTO")

    if ficha.usa_texto and not (texto or "").strip():
        raise ValueError(f"{codigo_ficha} requiere texto")

    if ficha.motor_texto != MotorTexto.AN_21:
        raise NotImplementedError("Se requiere motor AN 2.1")

    # -------------------------------------------------
    # 1) GEOMETRÍA DEL TEXTO (AN 2.1)
    # -------------------------------------------------

    geo = componer_texto(texto, int(h_mm))

    ancho_texto = float(geo["ancho_texto_mm"])  # negro-a-negro
    alto_texto = float(h_mm)

    # -------------------------------------------------
    # 2) REGLAS DEL CARTEL (EXA)
    # -------------------------------------------------

    rc = regla_cartel(codigo_ficha)

    base = codigo_ficha.split("_")[0]
    contraste_mm = float((contexto or {}).get("contraste_mm", 0) or 0)
    
    # Para 2.6/2.8 el borde lo define el usuario
    if base in ("2.6", "2.8"):
        borde_lat = contraste_mm
        borde_ver = contraste_mm
    else:
        borde_lat = rc.borde_lateral_mm
        borde_ver = rc.borde_vertical_mm
    
    # 3) RECTÁNGULO INTERIOR (FONDO)
    W_int = ancho_texto + 2.0 * rc.margen_lateral_mm
    H_int = alto_texto + 2.0 * rc.margen_vertical_mm
    
    # 4) RECTÁNGULO EXTERIOR (BORDE)
    W_ext = W_int + 2.0 * borde_lat
    H_ext = H_int + 2.0 * borde_ver
    
    # 5) POSICIONAMIENTO DEL TEXTO
    dx = (
        float(borde_lat)
        + float(rc.margen_lateral_mm)
        - float(geo["min_x_negro_mm"])
    )
    
    dy = (
        float(borde_ver)
        + float(rc.margen_vertical_mm)
    )


    elementos = []
    for e in geo["elementos"]:
        elementos.append({
            **e,
            "x": float(e["x"]) + dx,
            "y": dy,
        })

    # -------------------------------------------------
    # SALIDA
    # -------------------------------------------------

    return {
        "ficha": ficha.codigo,
        "tipo": ficha.tipo.value,
        "nombre": ficha.nombre,
        "texto": texto,
        "h_mm": int(h_mm),

        # --- geometría interna ---
        "geometria_texto": geo,

        "inscripcion": {
            "ancho_mm": ancho_texto,
            "alto_mm": alto_texto,
        },

        # --- fondo ---
        "fondo": {
            "margen_lateral_mm": rc.margen_lateral_mm,
            "margen_vertical_mm": rc.margen_vertical_mm,
            "ancho_mm": W_int,
            "alto_mm": H_int,
        },

        # --- borde ---
        "borde": {
            "borde_lateral_mm": float(borde_lat),
            "borde_vertical_mm": float(borde_ver),
        },

        # --- dimensiones globales ---
        "exterior": {
            "ancho_mm": W_ext,
            "alto_mm": H_ext,
        },

        "dimensiones": {
            "interior": (W_int, H_int),
            "exterior": (W_ext, H_ext),
        },

        # --- transformación aplicada ---
        "transform": {
            "dx_texto_mm": dx,
            "dy_texto_mm": dy,
        },

        # --- elementos posicionados ---
        "elementos": elementos,

    }
