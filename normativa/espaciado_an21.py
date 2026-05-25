# -*- coding: utf-8 -*-
"""Espaciado AN 2.1 (EXA-40 / AN 2.1)

Implementa el cálculo del espaciado entre caracteres en señalización horizontal (s(sh))
conforme al procedimiento del AN 2.1:
- h(eq) = h(sh) / 2.5
- s(sh) = (h(eq) / hl) * sl

Reglas AN 2.1:
- Espacio entre palabras/grupos: h/2
- Letra↔número: código 1
- Signos (guion, punto, barra) con carácter: código 1

Tablas A/B/C importadas desde TABLAS.xlsx.
"""

from __future__ import annotations

from typing import Dict, Literal




# -----------------------------
# TABLA A (compacta por grupos): letra anterior -> código según grupo de letra siguiente
# -----------------------------
LETRAS_G1 = ['B', 'D', 'E', 'F', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'R', 'U']
LETRAS_G2 = ['C', 'G', 'O', 'Q', 'S', 'X', 'Z']
LETRAS_G3 = ['A', 'J', 'T', 'V', 'W', 'Y']

TABLA_A_G: Dict[str, Dict[str, int]] = {
    "A": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "B": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "C": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    },
    "D": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "E": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    },
    "F": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    },
    "G": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "H": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "I": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "J": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "K": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    },
    "L": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "M": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "N": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "O": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "P": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "Q": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "R": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "S": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "T": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "U": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "V": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "W": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "X": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    },
    "Y": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "Z": {
        "g1": 2,
        "g2": 2,
        "g3": 3
    }
}

# -----------------------------
# TABLA B (compacta por grupos): número anterior -> código según grupo de número siguiente
# -----------------------------
NUM_G1 = ['1', '5']
NUM_G2 = ['0', '2', '3', '6', '8', '9']
NUM_G3 = ['4', '7']

TABLA_B_G: Dict[str, Dict[str, int]] = {
    "1": {
        "g1": 1,
        "g2": 1,
        "g3": 2
    },
    "2": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "3": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "4": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "5": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "6": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "7": {
        "g1": 2,
        "g2": 2,
        "g3": 4
    },
    "8": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "9": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    },
    "0": {
        "g1": 1,
        "g2": 2,
        "g3": 2
    }
}

# -----------------------------
# Tokens especiales (regla AN2.1: signos con carácter → código 1)
# -----------------------------
SIGNOS_CODIGO_1 = {'.', '-', '/', 'SLASH'}


def _tipo_token(tok: str) -> Literal['espacio','letra','numero','flecha','signo','otro']:
    if tok == ' ':
        return 'espacio'
    if tok.startswith('ARROW_'):
        return 'flecha'
    if tok in SIGNOS_CODIGO_1:
        return 'signo'
    if len(tok) == 1 and tok.isdigit():
        return 'numero'
    if len(tok) == 1 and tok.isalpha():
        return 'letra'
    return 'otro'


def _hl_para_h_sh(h_sh_mm: int) -> int:
    """Mapea h(sh) a hl de la tabla C. Soportado: 2000→200, 3000→300, 4000→400."""
    if h_sh_mm == 2000:
        return 200
    if h_sh_mm == 3000:
        return 300
    if h_sh_mm == 4000:
        return 400
    raise ValueError(f"Altura h(sh) no soportada para tablas: {h_sh_mm}. Usa 2000/3000/4000.")


#TABLA C: ESPACIADOS SEGÚN CLAVES PROCEDENTES DE TABLAS A O B

TABLA_C_SH = {
    2000: {1: 480, 2: 380, 3: 250, 4: 130},
    3000: {1: 720, 2: 570, 3: 380, 4: 190},
    4000: {1: 960, 2: 760, 3: 500, 4: 260},
}

def s_sh_mm(codigo: int, h_sh_mm: int) -> float:
    if h_sh_mm not in TABLA_C_SH:
        raise ValueError(f"Altura no soportada: {h_sh_mm}")
    return TABLA_C_SH[h_sh_mm][codigo]


def _codigo_tabla_a(prev: str, nxt: str) -> int:
    # determinar grupo de letra siguiente
    if nxt in LETRAS_G1:
        g = 'g1'
    elif nxt in LETRAS_G2:
        g = 'g2'
    elif nxt in LETRAS_G3:
        g = 'g3'
    else:
        return 1
    if prev not in TABLA_A_G:
        return 1
    return TABLA_A_G[prev][g]


def _codigo_tabla_b(prev: str, nxt: str) -> int:
    if nxt in NUM_G1:
        g = 'g1'
    elif nxt in NUM_G2:
        g = 'g2'
    elif nxt in NUM_G3:
        g = 'g3'
    else:
        return 1
    if prev not in TABLA_B_G:
        return 1
    return TABLA_B_G[prev][g]


def codigo_par(tok_a: str, tok_b: str) -> int:
    """Código 1..4 según tablas A/B y reglas AN 2.1."""
    ta = _tipo_token(tok_a)
    tb = _tipo_token(tok_b)

    # Letra↔número: código 1
    if (ta == 'letra' and tb == 'numero') or (ta == 'numero' and tb == 'letra'):
        return 1

    # Signos con carácter: código 1
    if ta == 'signo' or tb == 'signo':
        return 1

    # Letra-letra
    if ta == 'letra' and tb == 'letra':
        return _codigo_tabla_a(tok_a, tok_b)

    # Número-número
    if ta == 'numero' and tb == 'numero':
        return _codigo_tabla_b(tok_a, tok_b)

    # Por defecto
    return 1


def espacio_normativo(tok_a: str, tok_b: str, h_sh_mm: int, caso_flecha_unico: bool = False) -> float:
    """    Espacio entre tokens en mm:
    - Si tok_b es espacio -> h/2
    - Si caso_flecha_unico -> h/4
    - Si no -> s(sh) a partir de código y tablas
    """
    if tok_b == ' ':
        return h_sh_mm / 2.0
    if caso_flecha_unico:
        return h_sh_mm / 4.0
    return s_sh_mm(codigo_par(tok_a, tok_b), h_sh_mm)

def detalle_espaciado(tok_a: str, tok_b: str, h_sh_mm: int, caso_flecha_unico: bool = False) -> Dict[str, float]:
    """
    Devuelve información completa del espaciado AN 2.1 para acotación:
    - distancia_mm
    - codigo (1–4)
    - tipo (normal, espacio, flecha)
    """

    if tok_b == ' ':
        return {
            "distancia_mm": h_sh_mm / 2.0,
            "codigo": None,
            "tipo": "espacio"
        }

    if caso_flecha_unico:
        return {
            "distancia_mm": h_sh_mm / 4.0,
            "codigo": None,
            "tipo": "flecha"
        }

    codigo = codigo_par(tok_a, tok_b)
    distancia = s_sh_mm(codigo, h_sh_mm)

    return {
        "distancia_mm": distancia,
        "codigo": codigo,
        "tipo": "normal"
    }
