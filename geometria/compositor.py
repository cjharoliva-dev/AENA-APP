"""
Compositor de señales horizontales EXA-40 / ICC AENA

"""

from typing import Dict, Any

from normativa.fichas import (
    FichaNormativa,
    TipoSenal,
    obtener_ficha,
)

# Motores de bajo nivel
from geometria.motor_texto_AN21 import componer_texto, centrar_geometria


# -------------------------------------------------
# FUNCIÓN PÚBLICA (API INTERNA)
# -------------------------------------------------

def componer_senal(
    codigo_ficha: str,
    texto: str | None = None,
    contexto: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Punto de entrada único para componer una señal.

    :param codigo_ficha: código de ficha (ej. "2.7", "2.8", "3.15")
    :param texto: texto variable si aplica
    :param contexto: información adicional (clave, ancho, borde, etc.)
    """

    ficha = obtener_ficha(codigo_ficha)

    if ficha.requiere_contexto and not contexto:
        raise ValueError(
            f"La ficha {codigo_ficha} requiere contexto y no se ha proporcionado"
        )

    if ficha.tipo == TipoSenal.TEXTO:
        return _componer_senal_texto(ficha, texto, contexto)

    if ficha.tipo == TipoSenal.PARAMETRICA:
        return _componer_senal_parametrica(ficha, contexto)

    raise NotImplementedError(
        f"Tipo de señal no soportado: {ficha.tipo}"
    )


# -------------------------------------------------
# COMPOSICIÓN DE SEÑALES DE TEXTO
# -------------------------------------------------

def _componer_senal_texto(
    ficha: FichaNormativa,
    texto: str | None,
    contexto: Dict[str, Any] | None,
) -> Dict[str, Any]:

    if ficha.usa_texto and not texto:
        raise ValueError(
            f"La ficha {ficha.codigo} requiere texto"
        )

    # 1) Determinación de altura
    h_mm = _resolver_altura(ficha, contexto)

    # 2) Motor de texto
    geometria_texto = componer_texto(
        texto=texto,
        h_mm=h_mm,
    )

    # 3) Centrado geométrico por defecto
    geometria_texto = centrar_geometria(geometria_texto)

    # 4) Duplicación (si aplica)
    instancias = _aplicar_duplicacion(
        ficha=ficha,
        geometria=geometria_texto,
        contexto=contexto,
    )

    return {
        "ficha": ficha.codigo,
        "tipo": ficha.tipo.value,
        "texto": texto,
        "h_mm": h_mm,
        "instancias": instancias,
        "normativa": ficha.normativa,
    
        # colores normativos
        "color_fondo": ficha.color_fondo,
        "color_texto": ficha.color_texto,
        "color_borde": ficha.color_borde,
    }


# -------------------------------------------------
# COMPOSICIÓN DE SEÑALES PARAMÉTRICAS
# -------------------------------------------------

def _componer_senal_parametrica(
    ficha: FichaNormativa,
    contexto: Dict[str, Any] | None,
) -> Dict[str, Any]:

    raise NotImplementedError(
        f"La ficha paramétrica {ficha.codigo} aún no está implementada"
    )


# -------------------------------------------------
# RESOLUCIÓN DE ALTURA NORMATIVA
# -------------------------------------------------

def _resolver_altura(
    ficha: FichaNormativa,
    contexto: Dict[str, Any] | None,
) -> int:
    
    """
    Decide la altura normativa de carácter (h)
    """

    # 1️⃣ Altura forzada explícita (prioridad máxima)
    if contexto and "h_forzada" in contexto:
        return contexto["h_forzada"]

    # Caso simple: una única altura posible
    if len(ficha.alturas_mm) == 1:
        return ficha.alturas_mm[0]

    # Caso dependiente de la clave de la calle (ICC-i-05)
    if contexto and "clave" in contexto:
        clave = contexto["clave"]

        if clave in ["A", "B"]:
            return min(ficha.alturas_mm)

        if clave in ["C", "D", "E", "F"]:
            return max(ficha.alturas_mm)

    # Fallback seguro (normativo)
    return ficha.alturas_mm[0]


# -------------------------------------------------
# DUPLICACIÓN SEGÚN CONTEXTO
# -------------------------------------------------

def _aplicar_duplicacion(
    ficha: FichaNormativa,
    geometria: Dict[str, Any],
    contexto: Dict[str, Any] | None,
):
    

    if not ficha.duplicable:
        return [geometria]

    if not contexto:
        return [geometria]

    # Ejemplo: claves E/F → duplicación lateral
    clave = contexto.get("clave")
    if clave in ["E", "F"]:
        izquierda = _desplazar(geometria, dx=-1)
        derecha = _desplazar(geometria, dx=1)
        return [izquierda, derecha]

    # Caso general: una sola centrada
    return [geometria]


# -------------------------------------------------
# TRANSFORMACIONES GEOMÉTRICAS
# -------------------------------------------------

def _desplazar(
    geometria: Dict[str, Any],
    dx: float,
):

    copia = {
        **geometria,
        "elementos": [],
    }

    for e in geometria["elementos"]:
        copia["elementos"].append({
            **e,
            "x": e["x"] + dx,
        })

    return copia


