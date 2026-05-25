"""
Definición normativa de fichas de señalización horizontal
EXA-40 + lógica normativa extendida

"""

from enum import Enum
from typing import List, Dict, Optional


# -------------------------------------------------
# ENUMERACIONES AUXILIARES
# -------------------------------------------------

class TipoSenal(Enum):
    TEXTO = "texto"
    PARAMETRICA = "parametrica"
    FIJA = "fija"


class MotorTexto(Enum):
    AN_21 = "AN_2_1"
    NONE = "NONE"


# -------------------------------------------------
# ESTRUCTURA DE FICHA
# -------------------------------------------------

class FichaNormativa:
    def __init__(

        self,
        codigo: str,
        nombre: str,
        capitulo_exa40: int,
        tipo: TipoSenal,
        usa_texto: bool,
        motor_texto: MotorTexto,
        alturas_mm: List[int],
        permite_distorsion: Optional[bool],
        duplicable: bool,
        requiere_contexto: bool,
        normativa: List[str],

        alturas_por_clave: Optional[Dict[str, int]] = None,

        # colores base
        color_fondo: Optional[str] = None,
        color_texto: Optional[str] = None,
        color_borde: Optional[str] = None,

        # NUEVO
        tipo_borde: Optional[str] = None,
        tiene_variantes: bool = False,

        observaciones: Optional[str] = None,
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.capitulo_exa40 = capitulo_exa40
        self.tipo = tipo
        self.usa_texto = usa_texto
        self.motor_texto = motor_texto
        self.alturas_mm = alturas_mm
        self.alturas_por_clave = alturas_por_clave
        self.permite_distorsion = permite_distorsion
        self.duplicable = duplicable
        self.requiere_contexto = requiere_contexto
        self.normativa = normativa

        self.color_fondo = color_fondo
        self.color_texto = color_texto
        self.color_borde = color_borde

        self.tipo_borde = tipo_borde
        self.tiene_variantes = tiene_variantes

        self.observaciones = observaciones

    def __repr__(self):
        return f"<Ficha {self.codigo} ({self.nombre})>"


# -------------------------------------------------
# DEFINICIÓN DE FICHAS
# -------------------------------------------------

FICHAS: Dict[str, FichaNormativa] = {

    # -------------------------------------------------
    # 2.7 — INFORMACIÓN (PRINCIPAL)
    # -------------------------------------------------
    "2.7": FichaNormativa(
        codigo="2.7",
        nombre="Señales de información en calles de rodaje",
        capitulo_exa40=2,
        tipo=TipoSenal.TEXTO,
        usa_texto=True,
        motor_texto=MotorTexto.AN_21,
        alturas_mm=[2000, 4000],
        alturas_por_clave={
            "A": 2000, "B": 2000,
            "C": 4000, "D": 4000, "E": 4000, "F": 4000
        },
        permite_distorsion=True,
        duplicable=False,
        requiere_contexto=True,
        normativa=["EXA-40", "AN 2.1"],

        color_fondo=None,
        color_texto=None,
        color_borde=None,

        tipo_borde="estructural",
        tiene_variantes=True,

        observaciones="Dirección/destino vs emplazamiento",
    ),

    # -------------------------------------------------
    # 2.6 — NO ENTRY
    # -------------------------------------------------
    "2.6": FichaNormativa(
        codigo="2.6",
        nombre="Señal de prohibida la entrada",
        capitulo_exa40=2,
        tipo=TipoSenal.TEXTO,
        usa_texto=True,
        motor_texto=MotorTexto.AN_21,
        alturas_mm=[2000, 4000],

        # ✅ AÑADE ESTO:
        alturas_por_clave={
            "A": 2000, "B": 2000,
            "C": 4000, "D": 4000, "E": 4000, "F": 4000
        },

        permite_distorsion=True,
        duplicable=True,
        requiere_contexto=True,
        normativa=["EXA-40"],

        color_fondo="red",
        color_texto="white",

        tipo_borde="contraste",
    ),

    # -------------------------------------------------
    # 2.8 — OBLIGATORIAS
    # -------------------------------------------------
    "2.8": FichaNormativa(
        codigo="2.8",
        nombre="Señal con instrucciones obligatorias",
        capitulo_exa40=2,
        tipo=TipoSenal.TEXTO,
        usa_texto=True,
        motor_texto=MotorTexto.AN_21,
        alturas_mm=[2000, 4000],

        # ✅ AÑADE ESTO:
        alturas_por_clave={
            "A": 2000, "B": 2000,
            "C": 4000, "D": 4000, "E": 4000, "F": 4000
        },

        permite_distorsion=True,
        duplicable=True,
        requiere_contexto=True,
        normativa=["EXA-40"],

        color_fondo="red",
        color_texto="white",

        tipo_borde="contraste",
    ),
}


# -------------------------------------------------
# FUNCIONES DE ACCESO
# -------------------------------------------------

def obtener_ficha(codigo: str) -> FichaNormativa:
    if codigo not in FICHAS:
        raise KeyError(f"Ficha normativa no definida: {codigo}")
    return FICHAS[codigo]


def listar_fichas() -> List[str]:
    return list(FICHAS.keys())


# -------------------------------------------------
# RESOLUCIÓN DE COLORES (CLAVE)
# -------------------------------------------------


def resolver_colores(ficha: FichaNormativa, contexto: dict):
    # Contexto seguro
    contexto = contexto or {}

    # Código base por si llega "2.7_algo"
    codigo = (getattr(ficha, "codigo", "") or "").split("_")[0]

    # -----------------------------
    # 2.7 (VARIANTES)
    # -----------------------------
    if codigo == "2.7":
        tipo = contexto.get("tipo_2_7", "direccion")

        if tipo == "emplazamiento":
            colores = {"fondo": "black", "texto": "yellow", "borde": "yellow"}
        else:  # direccion + otros
            colores = {"fondo": "yellow", "texto": "black", "borde": "black"}

        # Si la ficha declara borde de contraste, permite sobreescritura por contexto
        if getattr(ficha, "tipo_borde", None) == "contraste":
            colores["borde"] = contexto.get("color_borde_contraste", "black")

        return colores

    # -----------------------------
    # DEFAULT (resto)
    # -----------------------------
    colores = {"fondo": "yellow", "texto": "black", "borde": "black"}

    # -----------------------------
    # 2.6 / 2.8: rojo + blanco, contraste opcional
    # -----------------------------
    if codigo in ("2.6", "2.8"):
        colores["fondo"] = "red"
        colores["texto"] = "white"

        contraste_mm = float(contexto.get("contraste_mm", 0) or 0)
        # Si hay contraste, borde negro; si no, borde igual al fondo (o neutro)
        colores["borde"] = "black" if contraste_mm > 0 else colores["fondo"]

    # -----------------------------
    # borde de contraste (sobreescritura si la ficha lo exige)
    # -----------------------------
    if getattr(ficha, "tipo_borde", None) == "contraste":
        colores["borde"] = contexto.get("color_borde_contraste", colores["borde"])

    return colores


# -------------------------------------------------
# WARNING DE CONTRASTE
# -------------------------------------------------

def warning_contraste(colores: dict):

    borde = colores.get("borde")
    fondo = colores.get("fondo")

    if fondo in ["red", "yellow"] and borde:
        if borde == "white":
            return "⚠ Borde blanco suele usarse sobre pavimento oscuro"
        elif borde == "black":
            return "⚠ Borde negro suele usarse sobre pavimento claro"

    return None