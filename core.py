# -*- coding: utf-8 -*-
"""
core.py – flujo único normativo (EXA-40)

Flujo:
INPUT → ficha → colores → geometría → acotación → áreas → salida

Soporta:
- 2.7 (variantes)
- 2.6 / 2.8 (borde contraste)
"""

from typing import Dict, Any, Optional, List

from normativa.fichas import (
    obtener_ficha,
    resolver_colores,
    warning_contraste,
)

from normativa.cartel_exa40 import construir_cartel
from geometria.motor_texto_AN21 import tokenizar
from geometria.acotacion import acotar_cartel_27
from calculo.areas import areas_texto_rectangular


# -------------------------------------------------
# META
# -------------------------------------------------

def listar_fichas_disponibles() -> List[Dict[str, str]]:
    return [{"codigo": f.codigo, "nombre": f.nombre} for f in obtener_ficha.__globals__["FICHAS"].values()]


def obtener_requisitos_ficha(codigo_ficha: str) -> Dict[str, Any]:
    ficha = obtener_ficha(codigo_ficha)

    return {
        "usa_texto": ficha.usa_texto,
        "requiere_contexto": ficha.requiere_contexto,
        "requiere_clave_para_altura": bool(ficha.alturas_por_clave),
        "alturas_disponibles": ficha.alturas_mm,
        "tiene_variantes": ficha.tiene_variantes,
        "tipo_borde": ficha.tipo_borde,
    }


# -------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------

def generar_senal(
    codigo_ficha: str,
    texto: Optional[str] = None,
    altura_mm: Optional[int] = None,
    contexto: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    contexto = contexto or {}
    ficha = obtener_ficha(codigo_ficha)
    base = (codigo_ficha or "").split("_")[0]

    # -------------------------------------------------
    # VALIDACIÓN TEXTO
    # -------------------------------------------------

    if ficha.usa_texto and (texto is None or texto.strip() == ""):
        raise ValueError("Esta ficha requiere texto.")

    texto = texto.strip() if texto else ""

    # -------------------------------------------------
    # ALTURA
    # -------------------------------------------------

    if altura_mm is None:

        if ficha.alturas_por_clave:
            clave = (contexto.get("clave") or "").strip().upper()

            if not clave:
                raise ValueError("Debe indicar clave A–F o altura explícita.")

            if clave not in ficha.alturas_por_clave:
                raise ValueError(
                    f"Clave '{clave}' no válida. "
                    f"Válidas: {sorted(ficha.alturas_por_clave.keys())}"
                )

            altura_mm = ficha.alturas_por_clave[clave]

        else:
            altura_mm = ficha.alturas_mm[0]

    if ficha.alturas_mm and altura_mm not in ficha.alturas_mm:
        raise ValueError(
            f"Altura {altura_mm} no válida para {codigo_ficha}. "
            f"Permitidas: {ficha.alturas_mm}"
        )

    # -------------------------------------------------
    # COLORES (CLAVE)
    # -------------------------------------------------

    colores = resolver_colores(ficha, contexto)

    aviso = None
    if ficha.tipo_borde == "contraste":
        aviso = warning_contraste(colores)


    # -------------------------------------------------
    # GEOMETRÍA
    # -------------------------------------------------

    cartel = construir_cartel(
        codigo_ficha,
        texto,
        int(altura_mm),
        contexto=contexto
    )

        # 🔥 EXTRAER ELEMENTOS DEL TEXTO (SIEMPRE)
    elementos = []
    
   
    if "texto_geom" in cartel:
        elementos = cartel["texto_geom"].get("elementos", [])
    elif "geometria" in cartel:
        elementos = cartel["geometria"].get("elementos", [])
    elif "texto" in cartel and isinstance(cartel["texto"], dict):
        elementos = cartel["texto"].get("elementos", [])


    
    cartel["colores"] = colores

    # -------------------------------------------------
    # TOKENS
    # -------------------------------------------------

    tokens = tokenizar(texto)

    # -------------------------------------------------
    # ACOTACIÓN
    # -------------------------------------------------

   # ACOTACIÓN
    if base in ("2.6", "2.7", "2.8"):
        acot = acotar_cartel_27(cartel)
    else:
        acot = None

    # -------------------------------------------------
    # ÁREAS (POR COLOR)
    # -------------------------------------------------

    areas = areas_texto_rectangular(cartel, tokens, colores)

    # -------------------------------------------------
    # SALIDA FINAL
    # -------------------------------------------------

    return {
        "ficha": ficha.codigo,
        "nombre": ficha.nombre,
        "tipo": ficha.tipo.value,
        "texto": texto,
        "altura_mm": int(altura_mm),

        "contexto": contexto if contexto else None,
        "colores": colores,
        "warning": aviso,

        "cartel": cartel,
        "acotacion": acot,
        "areas": areas,

        "normativa": ficha.normativa,
        
        "elementos": elementos,

    }
