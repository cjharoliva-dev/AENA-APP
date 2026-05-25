import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
from matplotlib import font_manager


# =========================
# CONFIG VISUAL
# =========================
COTA_COLOR = "black"
COTA_LW = 1.2
COTA_FONT = 10


TEXT_BBOX = dict(facecolor="white", edgecolor="none", alpha=0.85, pad=0.6)

def fmt_m(v):
    return f"{v * 1000:.0f} mm"
def fmt_mm(v):
    return f"{v * 1000:.0f} mm"


# =========================
# Símbolos especiales
# =========================
def _display_char(raw):
    if raw is None:
        return ""
    s = str(raw)
    mapa = {
        "ARROW_LEFT": "←",
        "ARROW_UPLEFT": "↖",
        "ARROW_UP": "↑",
        "ARROW_UPRIGHT": "↗",
        "ARROW_RIGHT": "→",
        "SLASH": "/",
        "CUADRADO": "■",
        "ROM_I": "I",
        "ROM_II": "II",
        "ROM_III": "III",
    }
    return mapa.get(s, s)

# =========================
# COTAS (negras)
# =========================
def _cota_h(ax, x1, x2, y, texto, text_pos="center", dy_text=0.0, bbox=None, z=30):
    ax.annotate(
        "",
        xy=(x2, y),
        xytext=(x1, y),
        arrowprops=dict(arrowstyle="<->", color=COTA_COLOR, lw=COTA_LW),
        zorder=z,
    )
    if text_pos == "left":
        xt = x1 + 0.08 * (x2 - x1)
        ha = "left"
    else:
        xt = (x1 + x2) / 2
        ha = "center"
    ax.text(
        xt, y + dy_text, texto,
        color=COTA_COLOR, fontsize=COTA_FONT,
        ha=ha, va="bottom",
        bbox=bbox, zorder=z
    )

def _cota_v(ax, y1, y2, x, texto, dx_text=0.0, bbox=None, z=30):
    ax.annotate(
        "",
        xy=(x, y2),
        xytext=(x, y1),
        arrowprops=dict(arrowstyle="<->", color=COTA_COLOR, lw=COTA_LW),
        zorder=z,
    )
    ax.text(
        x + dx_text, (y1 + y2) / 2, texto,
        color=COTA_COLOR, fontsize=COTA_FONT,
        ha="left", va="center", rotation=90,
        bbox=bbox, zorder=z
    )

def _ext_v(ax, x, y1, y2, z=25):
    ax.plot([x, x], [y1, y2], color=COTA_COLOR, lw=1.0, zorder=z)

def _ext_h(ax, y, x1, x2, z=25):
    ax.plot([x1, x2], [y, y], color=COTA_COLOR, lw=1.0, zorder=z)

def _tick_h(ax, x, y, tick_len, z=25):
    ax.plot([x, x + tick_len], [y, y], color=COTA_COLOR, lw=1.0, zorder=z)

# =========================
# ÁREAS (fuera del eje)
# =========================
def _fmt_areas(areas):
    if not isinstance(areas, dict) or not areas:
        return None

    # Traducción de claves de color
    mapa_colores = {
        "yellow": "Amarillo",
        "black": "Negro",
        "red": "Rojo",
        "white": "Blanco",
    }

    # Umbral para considerar "cero"
    EPS = 1e-9

    lines = ["ÁREAS (m²)"]

    # 1) Por color en m²
    colores_m2 = areas.get("colores_m2")
    if isinstance(colores_m2, dict) and colores_m2:
        for k, v in colores_m2.items():
            nombre = mapa_colores.get(k, k)
            try:
                val = float(v)
            except Exception:
                
                lines.append(f"- {nombre}: {v} m²")
                continue

        
            if abs(val) <= EPS:
                continue

            lines.append(f"- {nombre}: {val:.3f} m²")

  
    det = areas.get("detalle")
    if isinstance(det, dict) and det:
        lines.append("") 

        if "texto_mm2" in det:
            lines.append(f"Texto (m²): {float(det['texto_mm2'])/1e6:.3f}")
        if "fondo_mm2" in det:
            lines.append(f"Fondo (m²): {float(det['fondo_mm2'])/1e6:.3f}")

       
        borde_mm2 = None
        if "borde_mm2" in det:
            borde_mm2 = float(det["borde_mm2"])
        elif "marco_mm2" in det:
            borde_mm2 = float(det["marco_mm2"])

        if borde_mm2 is not None:
            borde_m2 = borde_mm2 / 1e6
            if borde_m2 > EPS:
                lines.append(f"Borde (m²): {borde_m2:.3f}")

   
    tsa = areas.get("tokens_sin_area_base")
    if tsa:
        lines.append("")
        lines.append(f"Tokens sin área base: {tsa}")

    return "\n".join(lines)



def draw_glyph_embedded(ax, ch, x0, y0, w, h, color="black", fontprops=None):
    """
    Dibuja 'ch' como vector embebido en la caja (x0,y0,w,h) en coords de datos:
    - toca abajo y arriba (altura EXACTA h)
    - si se pasa de ancho, comprime solo en X
    - centrado en X
    """
    tp = TextPath((0, 0), ch, size=1.0, prop=fontprops)
    bb = tp.get_extents()

    if bb.height <= 0 or bb.width <= 0:
        return

    # Escala vertical para tocar arriba/abajo
    sy = h / bb.height

    # Ancho tras escalar en Y
    w_after_sy = bb.width * sy

  
    sx = 1.0
    if w_after_sy > w:
        sx = w / w_after_sy

    # Llevar bbox a origen
    trans = (Affine2D()
             .translate(-bb.x0, -bb.y0)
             .scale(sx * sy, sy))

    # Ancho final y centrado en la caja
    w_final = bb.width * sy * sx
    dx_center = (w - w_final) / 2.0

    # Mover a caja (x0,y0)
    trans = trans.translate(x0 + dx_center, y0)

    patch = PathPatch(tp, transform=trans + ax.transData,
                      facecolor=color, edgecolor="none", zorder=10)
    ax.add_patch(patch)

def draw_symbol_isotropic(ax, ch, x0, y0, w, h, color="black", fontprops=None, fill_ratio=0.80):
   
    tp = TextPath((0, 0), ch, size=1.0, prop=fontprops)
    bb = tp.get_extents()
    if bb.height <= 0 or bb.width <= 0:
        return

    size_target = fill_ratio * min(w, h)
    s = min(size_target / bb.width, size_target / bb.height)

    w_final = bb.width * s
    h_final = bb.height * s

    dx = (w - w_final) / 2.0
    dy = (h - h_final) / 2.0

    trans = (Affine2D()
             .translate(-bb.x0, -bb.y0)
             .scale(s, s)
             .translate(x0 + dx, y0 + dy))

    patch = PathPatch(tp, transform=trans + ax.transData,
                      facecolor=color, edgecolor="none", zorder=10)
    ax.add_patch(patch)


# =========================
# Render principal
# =========================
def dibujar_plano(resultado, debug=False):
    acot = resultado.get("acotacion", {})
    cartel = resultado.get("cartel", {})

    
    MOSTRAR_RECTS_INVISIBLES = debug
    MOSTRAR_CAJAS_VISUALES = debug
    MOSTRAR_COTAS_CARACTER = debug

    # Colores
    colores = resultado.get("colores") or cartel.get("colores") or {}
    c_fondo = colores.get("fondo", "yellow")
    c_texto = colores.get("texto", "black")
    c_borde = colores.get("borde", "black")

    # Datos normativos 
    esp = acot.get("espaciado", [])          # lista ordenada de gaps (mm)
    marg = acot.get("margenes", {})          # {'izq','der','sup','inf'} mm
    bor = acot.get("bordes", {})             # {'lateral','vertical'} mm

    # Altura normativa (mm)
    H_mm = float(resultado.get("altura_mm", 0))

    # Elementos: necesitamos x_min/x_max por carácter para el ancho negro-a-negro
    elementos = resultado.get("elementos") or cartel.get("elementos") or []
    elems = [e for e in elementos if isinstance(e, dict) and ("x_min" in e) and ("x_max" in e)]
    
    if elems and "x" in elems[0]:
        elems.sort(key=lambda d: float(d.get("x", 0)))

    # Construcción de anchos negro-a-negro (mm) — tu único ancho
    w_mm = [float(e["x_max"]) - float(e["x_min"]) for e in elems]

    # Gaps en mm desde acotación (orden ya confirmado por ti)
    gaps_mm = [float(d.get("distancia_mm", 0.0)) for d in esp]

    # --- Composición en serie de rectángulos invisibles ---
    # Rect i: [Li, Ri] × [0, H]
    rects = []
    x_cursor = 0.0
    for i, wi in enumerate(w_mm):
        Li = x_cursor
        Ri = x_cursor + wi
        rects.append((Li, 0.0, Ri, H_mm))  # (L, B, R, T) en mm
        if i < len(w_mm) - 1:
            gap = gaps_mm[i] if i < len(gaps_mm) else 0.0
            x_cursor = Ri + gap

    # bbox texto
    if rects:
        L_text = rects[0][0]
        R_text = rects[-1][2]
    else:
        L_text = 0.0
        R_text = 0.0

    # Márgenes (mm)
    m_izq = float(marg.get("izq", 0.0))
    m_der = float(marg.get("der", 0.0))
    m_sup = float(marg.get("sup", 0.0))
    m_inf = float(marg.get("inf", 0.0))

    # Bordes (mm)
    b_lat = float(bor.get("lateral", 0.0))
    b_ver = float(bor.get("vertical", 0.0))

    # Interior (mm)
    L_int = L_text - m_izq
    R_int = R_text + m_der
    B_int = 0.0 - m_inf
    T_int = H_mm + m_sup

    # Exterior (mm)
    L_ext = L_int - b_lat
    R_ext = R_int + b_lat
    B_ext = B_int - b_ver
    T_ext = T_int + b_ver

    # Shift para que exterior empiece en (0,0)
    sx = -L_ext
    sy = -B_ext

    # Convertir a metros para dibujo
    def mm2m(v): return v / 1000.0

    W_ext = mm2m(R_ext - L_ext)
    H_ext = mm2m(T_ext - B_ext)
    W_int = mm2m(R_int - L_int)
    H_int = mm2m(T_int - B_int)

    x_int0 = mm2m(L_int + sx)
    y_int0 = mm2m(B_int + sy)

    # Figura
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.grid(False)

    # Rect exterior/interior
    ax.add_patch(Rectangle((0, 0), W_ext, H_ext, facecolor=c_borde, edgecolor="black", linewidth=1))
    ax.add_patch(Rectangle((x_int0, y_int0), W_int, H_int, facecolor=c_fondo, edgecolor="black", linewidth=1))

    # Dibujar rectángulos invisibles (debug opcional)
    if MOSTRAR_RECTS_INVISIBLES:
        for (L, B, R, T) in rects:
            ax.add_patch(Rectangle((mm2m(L + sx), mm2m(B + sy)),
                                   mm2m(R - L), mm2m(T - B),
                                   facecolor="none", edgecolor="red", linewidth=1))

    # Dibujar texto embebido en cada rect invisible
    fontprops = font_manager.FontProperties(family="DejaVu Sans")
    
    # símbolos que NO deben estirarse a 4m
    NO_STRETCH_GLYPHS = {"■", "□", "●", "○", "."}
    
    off = max(W_ext, H_ext) * 0.14
    
    for i, (L, B, R, T) in enumerate(rects):
        x0 = mm2m(L + sx)
        y0 = mm2m(B + sy)
        w = mm2m(R - L)
        h = mm2m(T - B)
    
        if MOSTRAR_CAJAS_VISUALES:
            ax.add_patch(Rectangle((x0, y0), w, h,
                                   facecolor="none",
                                   edgecolor="dodgerblue",
                                   linewidth=1))
    
        ch = _display_char(elems[i].get("char", "")) if i < len(elems) else ""
        print(i, repr(ch))
    
        # Dibujo vectorial: números/letras estiran (embebido), símbolos isotrópicos
       # Caso especial: punto como círculo real
        if ch == ".":
            r = min(w, h) * 0.15   # tamaño del punto (ajustable)
            cx = x0 + w / 2
            cy = y0 + h / 2
        
            circ = plt.Circle((cx, cy), r, color=c_texto)
            ax.add_patch(circ)
        
        # Símbolos que no deben estirarse
        elif ch in NO_STRETCH_GLYPHS:
            draw_symbol_isotropic(ax, ch, x0, y0, w, h,
                                  color=c_texto,
                                  fontprops=fontprops,
                                  fill_ratio=0.80)
        
        # Letras y números normales
        else:
            draw_glyph_embedded(ax, ch, x0, y0, w, h,
                                color=c_texto,
                                fontprops=fontprops)

        # ===============================
        # COTAS DE ANCHO POR CARÁCTER
        # ===============================
        if MOSTRAR_COTAS_CARACTER:
        
            y_char_cota = y0 - off * 0.2
        
            # líneas verticales de referencia
            ax.plot([x0, x0], [y0, y_char_cota], color=COTA_COLOR, lw=0.8)
            ax.plot([x0 + w, x0 + w], [y0, y_char_cota], color=COTA_COLOR, lw=0.8)
        
            # cota horizontal
            _cota_h(
                ax,
                x0,
                x0 + w,
                y_char_cota,
                fmt_mm(w),
                bbox=TEXT_BBOX,
                dy_text=off * -0.3
            )
    # ============================
    # COTAS (todas desde la geometría invisible)
    # ============================
    def _cota_v_texto_horizontal(ax, y1, y2, x, texto, dx_text=0.0, dy_text=0.0, bbox=None, z=30):
        ax.annotate(
            "", xy=(x, y2), xytext=(x, y1),
            arrowprops=dict(arrowstyle="<->", color=COTA_COLOR, lw=COTA_LW),
            zorder=z
        )
        ax.text(
            x + dx_text, (y1 + y2) / 2 + dy_text,
            texto,
            color=COTA_COLOR, fontsize=COTA_FONT,
            ha="center", va="bottom",
            rotation=0,
            bbox=bbox, zorder=z
        )

    off = max(W_ext, H_ext) * 0.14
    
    # ¿Hay borde/contraste real?
    bordes = resultado["acotacion"]["bordes"]  # {'lateral':..., 'vertical':...} 【2-a174d7】
    hay_borde = (float(bordes.get("lateral", 0)) > 0) or (float(bordes.get("vertical", 0)) > 0)

    # Abajo: exterior e interior
    y_cota_ext = -off
    y_cota_int = -off * 0.68
    y_cota_6000 = y_cota_int + off * 0.18
    # Interior ancho (6,00 m) — SOLO esta línea más arriba
    _ext_v(ax, x_int0, y_int0, y_cota_6000)
    _ext_v(ax, x_int0 + W_int, y_int0, y_cota_6000)
    _cota_h(ax, x_int0, x_int0 + W_int, y_cota_int, fmt_m(W_int),
        bbox=TEXT_BBOX, dy_text=off*0.15)

    # Exterior ancho
    if hay_borde:
        _ext_v(ax, 0, 0, y_cota_ext)
        _ext_v(ax, W_ext, 0, y_cota_ext)
        _cota_h(ax, 0, W_ext, y_cota_ext, fmt_m(W_ext), text_pos="left")


    # Interior ancho
    _ext_v(ax, x_int0, y_int0, y_cota_int)
    _ext_v(ax, x_int0 + W_int, y_int0, y_cota_int)
    

    # 0,25 m (borde lateral) ARRIBA derecha: entre interior-right y exterior-right, con extensiones claras
    if hay_borde:
        x_inner_right = x_int0 + W_int
        x_outer_right = W_ext
        
        y_borde_top = H_ext + off * 0.10  # altura de la línea de cota (arriba)
        
        _ext_v(ax, x_inner_right, H_ext, y_borde_top)
        _ext_v(ax, x_outer_right, H_ext, y_borde_top)
        
        _cota_h(ax, x_inner_right, x_outer_right, y_borde_top,
                fmt_m(x_outer_right - x_inner_right),
                bbox=TEXT_BBOX, dy_text=off * 0.10)


    # Izquierda: alturas exterior e interior SEPARADAS y legibles
    x_lane_extH = -off * 0.80   # exterior más a la izquierda
    x_lane_intH = -off * 0.28   # interior menos a la izquierda, pero bien separado
    
    # Texto más separado de flechas/líneas
    dx_txt_ext = -off * 0.4
    dx_txt_int = -off * 0.4
    
    # Exterior alto
    if hay_borde:
        _ext_h(ax, 0, x_lane_extH, 0)
        _ext_h(ax, H_ext, x_lane_extH, 0)
        _cota_v(ax, 0, H_ext, x_lane_extH, fmt_m(H_ext),
                dx_text=dx_txt_ext, bbox=TEXT_BBOX)
    
    # Interior alto
    
    _ext_h(ax, y_int0, x_int0, x_lane_intH)
    _ext_h(ax, y_int0 + H_int, x_int0, x_lane_intH)
    _cota_v(ax, y_int0, y_int0 + H_int, x_lane_intH, fmt_m(H_int),
            dx_text=dx_txt_int, bbox=TEXT_BBOX)
   

   # Derecha: H del texto (altura normativa) — flecha corta y fuera
    x_lane_H = W_ext + off * 0.55
    tick = off * 0.10
    y_text0 = mm2m(0.0 + sy)
    y_text1 = mm2m(H_mm + sy)
    
    _tick_h(ax, x_lane_H, y_text0, tick)
    _tick_h(ax, x_lane_H, y_text1, tick)
    _cota_v(ax, y_text0, y_text1, x_lane_H, fmt_m(mm2m(H_mm)),
            dx_text=off * 0.20, bbox=TEXT_BBOX)
    
    # DENTRO (margen superior), centrado sobre el último carácter y TEXTO HORIZONTAL
    y_int_top = y_int0 + H_int
    margen_sup_m = y_int_top - y_text1
    
    x_last_L = mm2m(rects[-1][0] + sx)
    x_last_R = mm2m(rects[-1][2] + sx)
    x_last_C = (x_last_L + x_last_R) / 2.0
    
    x_in = x_last_C
    tick_in = off * 0.06
    
    _tick_h(ax, x_in, y_text1, tick_in)
    _tick_h(ax, x_in, y_int_top, tick_in)
    
    # texto horizontal (no rotado)
    _cota_v_texto_horizontal(ax, y_text1, y_int_top, x_in, fmt_m(margen_sup_m),
                             dx_text=off*0.6, dy_text=off * 0.02, bbox=TEXT_BBOX)
    
    # Derecha: borde vertical (0,50) ALINEADO con el carril
    if hay_borde:
        x_lane_050 = x_lane_H
    
        _tick_h(ax, x_lane_050, y_int_top, tick)
        _tick_h(ax, x_lane_050, H_ext, tick)
    
    # separa el texto un poco más para que no se meta en el borde
        _cota_v(ax, y_int_top, H_ext, x_lane_050, fmt_m(H_ext - y_int_top),
                dx_text=off * 0.2, bbox=TEXT_BBOX)


    # Dentro: gaps (desde rects invisibles) en la zona inferior interior
    if len(rects) >= 2:
        y_gap = y_int0 + H_int * 0.2
        for i in range(len(rects) - 1):
            aR = mm2m(rects[i][2] + sx)
            bL = mm2m(rects[i+1][0] + sx)
            _cota_h(ax, aR, bL, y_gap, fmt_m(bL - aR), bbox=TEXT_BBOX, dy_text=off*0.2)

    # Dentro: márgenes laterales desde interior a texto
    y_margen = y_int0 + H_int * 0.20
    x_text_L = mm2m(L_text + sx)
    x_text_R = mm2m(R_text + sx)
    _cota_h(ax, x_int0, x_text_L, y_margen, fmt_m(x_text_L - x_int0), bbox=TEXT_BBOX, dy_text=off*0.2)
    _cota_h(ax, x_text_R, x_int0 + W_int, y_margen, fmt_m((x_int0 + W_int) - x_text_R), bbox=TEXT_BBOX, dy_text=off*0.2)


    # Áreas fuera del eje (no distorsiona escala)
    texto_areas = _fmt_areas(resultado.get("areas", {}))
    texto_areas = _fmt_areas(resultado.get("areas", {}))
    if texto_areas:
        fig.text(
            0.70, 0.05, texto_areas,          # X,Y en coordenadas de FIGURA (no de ejes)
            ha="left", va="bottom", fontsize=10,
            bbox=dict(facecolor="white", edgecolor="black", alpha=0.95)
        )

        
    fig.subplots_adjust(bottom=0.25)

    # Título
    ficha = resultado.get("ficha", "")
    texto = resultado.get("texto", "")
    nombre = resultado.get("nombre", "")
    titulo = f"EXA-40 {ficha} | Texto: {texto}"
    if nombre:
        titulo += f" | {nombre}"
    ax.set_title(titulo)

    # Límites
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    if hay_borde:
        x_min = x_lane_extH - off * 0.40
        x_max = x_lane_050 + off * 0.40
        y_min = y_cota_int - off * 0.45
        y_max = H_ext + off * 0.40
    else:
        # Sin borde: encuadre más compacto
        x_min = -off * 0.20
        x_max = W_ext + off * 0.60
        y_min = y_cota_int - off * 0.45
        y_max = H_int + y_int0 + off * 0.40
    
        
        x_min = min(x_min, x_lane_intH - off * 0.10)


    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    if debug:
        print("rects:", rects)
        print("gaps_mm:", gaps_mm)
        print("marg:", marg, "bordes:", bor)

    plt.show()


def dibujar_base(resultado, modo_validacion=True):
    return dibujar_plano(resultado, debug=modo_validacion)