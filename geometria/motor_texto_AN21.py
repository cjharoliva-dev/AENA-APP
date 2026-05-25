# -*- coding: utf-8 -*-
"""
geometria/motor_texto_AN21.py
"""
import os
import sys

import json
from typing import Dict, List, Any

from normativa.espaciado_an21 import espacio_normativo

def resource_path(rel_path: str) -> str:
    """
    Devuelve ruta correcta tanto en desarrollo como en .exe (PyInstaller).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # carpeta temporal donde PyInstaller extrae recursos
    else:
        base = os.path.abspath(os.getcwd())  # carpeta actual del proyecto al ejecutar en Spyder
    return os.path.join(base, rel_path)


JSON_DEFAULT = os.path.join("datos", "an21_caracteres_base.json")


# -------------------------------------------------
# CARGA DATOS
# -------------------------------------------------

def cargar_datos(ruta_json: str = JSON_DEFAULT) -> Dict[str, Any]:
    ruta = resource_path(ruta_json)  # aquí ruta_json debería ser tipo "datos/an21_caracteres_base.json"
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _tabla_caracteres(db: Dict[str, Any]) -> Dict[str, Any]:
    tabla = db.get("caracteres") or db.get("numeros")
    if not isinstance(tabla, dict):
        raise ValueError("El JSON debe contener 'caracteres' o 'numeros'.")
    return tabla


# -------------------------------------------------
# TOKENIZACIÓN
# -------------------------------------------------

def tokenizar(texto: str) -> List[str]:
    texto = (texto or "").strip().upper()
    if not texto:
        return []

    tokens: List[str] = []
    i = 0

    while i < len(texto):

        # -------------------------
        # TOKEN ENTRE COMILLAS
        # -------------------------
        if texto[i] == '"':
            i += 1
            start = i

            while i < len(texto) and texto[i] != '"':
                i += 1

            token = texto[start:i]

            if token:
                tokens.append(token)

            i += 1
            continue

        # -------------------------
        # ESPACIO REAL
        # -------------------------
        if texto[i] == " ":
            tokens.append(" ")
            i += 1
            continue

        # -------------------------
        # TOKEN ESPECIAL SIN COMILLAS
        # -------------------------
        if texto[i].isalpha():
            start = i
            while i < len(texto) and texto[i].isalpha():
                i += 1

            palabra = texto[start:i]

            # si existe en tabla → token completo
            # si no → descomponer en letras
            if palabra in {"CUADRADO", "SLASH"}:
                tokens.append(palabra)
            else:
                tokens.extend(list(palabra))

            continue

        # -------------------------
        # NÚMEROS
        # -------------------------
        if texto[i].isdigit():
            tokens.append(texto[i])
            i += 1
            continue

        # fallback
        tokens.append(texto[i])
        i += 1

    return tokens


# -------------------------------------------------
# ESCALA
# -------------------------------------------------

def escala_calibrada(altura_mm: int, escala_4000: float = 5.36) -> float:
    return float(escala_4000) * (float(altura_mm) / 4000.0)

def ancho_token_mm(tabla, token, altura_mm):
    datos = tabla[token]
    return float(datos["ancho_4000_mm"]) * (altura_mm / 4000.0)
# -------------------------------------------------
# MOTOR PRINCIPAL
# -------------------------------------------------

def componer_texto(
    texto: str,
    altura_mm: int,
    ruta_json: str = JSON_DEFAULT,
    escala_4000: float = 5.36,
) -> Dict[str, Any]:

    db = cargar_datos(ruta_json)
    tabla = _tabla_caracteres(db)

    tokens = tokenizar(texto)

    if not tokens:
        return {
            "texto": "",
            "tokens": [],
            "altura_mm": int(altura_mm),
            "factor": 0.0,
            "scale": 0.0,
            "elementos": [],
            "min_x_negro_mm": 0.0,
            "max_x_negro_mm": 0.0,
            "ancho_texto_mm": 0.0,
        }

    
    scale = escala_calibrada(int(altura_mm), escala_4000)
    factor_mm = scale * 1000.0

    elementos_out: List[Dict[str, Any]] = []

    x_cursor = 0.0
    prev_real = None
    hay_espacio_pendiente = False
    primer_token_real = True

    for t in tokens:

       
        if t == " ":
            hay_espacio_pendiente = True
            continue

        if t not in tabla:
            raise ValueError(f"Token no soportado: {t}")

        ancho_mm = ancho_token_mm(tabla, t, int(altura_mm))

        if primer_token_real:
            x_actual = 0.0
            primer_token_real = False
        else:
            if prev_real is None:
                gap_mm = 0.0
            elif hay_espacio_pendiente:
                gap_mm = espacio_normativo(prev_real, " ", int(altura_mm))
            else:
                gap_mm = espacio_normativo(prev_real, t, int(altura_mm))

            x_actual = x_cursor + gap_mm

        elementos_out.append({
            "char": t,
            "x": float(x_actual),
            "ancho": float(ancho_mm),
            "alto": float(altura_mm),

         
            "x_min": 0.0,
            "x_max": float(ancho_mm),
        })

        x_cursor = x_actual + ancho_mm
        prev_real = t
        hay_espacio_pendiente = False

    if not elementos_out:
        min_x_negro_mm = 0.0
        max_x_negro_mm = 0.0
        ancho_texto_mm = 0.0
    else:
        min_x_negro_mm = 0.0
        max_x_negro_mm = elementos_out[-1]["x"] + elementos_out[-1]["x_max"]
        ancho_texto_mm = max_x_negro_mm - min_x_negro_mm

    return {
        "texto": texto,
        "tokens": tokens,
        "altura_mm": int(altura_mm),

        
        "factor": factor_mm,
        "scale": scale,

        "elementos": elementos_out,
        "min_x_negro_mm": float(min_x_negro_mm),
        "max_x_negro_mm": float(max_x_negro_mm),
        "ancho_texto_mm": float(ancho_texto_mm),
    }
