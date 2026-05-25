# -*- coding: utf-8 -*-
"""
Interfaz gráfica EXA-40 (actualizada)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

messagebox.showinfo(
    "Aviso de uso",
    "Herramienta desarrollada para uso interno.\n"
    "No está permitido distribuir el código ni modificar el software sin autorización."
)


from core import (
    listar_fichas_disponibles,
    obtener_requisitos_ficha,
    generar_senal,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Señalización horizontal EXA-40")
        self.geometry("900x750")

        self._mapa_fichas = {}
        self._requisitos_actuales = {}

        self._crear_widgets()
        self._cargar_fichas()
        
        self.after(100, lambda: self.entry_texto.focus_set())

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def _crear_widgets(self):

        # --- FICHA ---
        frame_ficha = ttk.LabelFrame(self, text="Ficha normativa")
        frame_ficha.pack(fill="x", padx=10, pady=6)

        self.ficha_var = tk.StringVar()
        self.combo_fichas = ttk.Combobox(frame_ficha, textvariable=self.ficha_var, state="readonly")
        self.combo_fichas.pack(fill="x", padx=6, pady=6)
        self.combo_fichas.bind("<<ComboboxSelected>>", self._on_ficha_seleccionada)

        # --- DATOS ---
        self.frame_entrada = ttk.LabelFrame(self, text="Datos de la señal")
        self.frame_entrada.pack(fill="x", padx=10, pady=6)

        # TEXTO
        self.texto_var = tk.StringVar()
        self.label_texto = ttk.Label(self.frame_entrada, text="Texto:")
        self.entry_texto = ttk.Entry(self.frame_entrada, textvariable=self.texto_var)
        
        # LIMPIAR
        frame_texto = ttk.Frame(self.frame_entrada)
        frame_texto.pack(fill="x")
        
        self.entry_texto.pack(in_=frame_texto, side="left", fill="x", expand=True)
        
        btn_limpiar = ttk.Button(
            frame_texto,
            text="Limpiar",
            command=lambda: self.texto_var.set("")
        )
        btn_limpiar.pack(side="right", padx=5)
        
        # CLAVE
        self.clave_var = tk.StringVar()
        self.label_clave = ttk.Label(self.frame_entrada, text="Clave A–F:")
        self.combo_clave = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.clave_var,
            values=["A", "B", "C", "D", "E", "F"],
            state="readonly"
        )

        # ALTURA
        self.altura_var = tk.StringVar()
        self.label_altura = ttk.Label(self.frame_entrada, text="Altura (mm):")
        self.combo_altura = ttk.Combobox(self.frame_entrada, textvariable=self.altura_var, state="readonly")

        # --- NUEVOS SELECTORES ---
        self.tipo_27_var = tk.StringVar(value="direccion")
        self.borde_var = tk.StringVar(value="Negro")
        self.flecha_var = tk.StringVar(value="ninguna")
        self.romano_var = tk.StringVar(value="ninguno")
        self.simbolo_var = tk.StringVar(value="ninguno")

        self.label_tipo_27 = ttk.Label(self.frame_entrada, text="Tipo 2.7:")
        self.combo_tipo_27 = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.tipo_27_var,
            values=["direccion", "emplazamiento", "otros"],
            state="readonly"
        )

        self.label_borde = ttk.Label(self.frame_entrada, text="Borde contraste:")
        self.combo_borde = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.borde_var,
            values=["Negro", "Blanco"],
            state="readonly"
        )
        
        #  Ancho contraste (mm)
        self.contraste_mm_var = tk.StringVar(value="0")
        self.label_contraste_mm = ttk.Label(self.frame_entrada, text="Ancho contraste (cm):")
        self.entry_contraste_mm = ttk.Entry(self.frame_entrada, textvariable=self.contraste_mm_var)
        self.btn_add = ttk.Button(
            self.frame_entrada,
            text="Añadir símbolo",
            command=self._add_token
        )
        # ROMANO
        self.label_romano = ttk.Label(self.frame_entrada, text="Número romano:")
        self.combo_romano = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.romano_var,
            values=["ninguno", "I", "II", "III"],
            state="readonly"
        )

        # SÍMBOLOS CUADRADO, PUNTO Y BARRA
        self.label_simbolo = ttk.Label(self.frame_entrada, text="Símbolo:")
        self.combo_simbolo = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.simbolo_var,
            values=["ninguno", "punto", "cuadrado", "barra"],
            state="readonly"
        )

        # FLECHA
        self.label_flecha = ttk.Label(self.frame_entrada, text="Flecha:")
        self.combo_flecha = ttk.Combobox(
            self.frame_entrada,
            textvariable=self.flecha_var,
            values=[
                "ninguna",
                "izquierda",
                "derecha",
                "arriba",
                "arriba-izquierda",
                "arriba-derecha",
            ],
            state="readonly"
        )

        # MODO VALIDACIÓN
        self.modo_validacion_var = tk.BooleanVar(value=True)
        
        self.chk_validacion = ttk.Checkbutton(
            self,
            text="Modo validación (cotas + rectángulos)",
            variable=self.modo_validacion_var
        )
        self.chk_validacion.pack(pady=5)

        # BOTÓN
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10)
        
        self.btn_generar = ttk.Button(
            frame_botones,
            text="Generar señal",
            command=self._generar_senal
        )
        self.btn_generar.pack(side="left", padx=5)
        
        self.btn_guardar = ttk.Button(
            frame_botones,
            text="Guardar imagen",
            command=self._guardar_imagen
        )
        self.btn_guardar.pack(side="left", padx=5)


        # SALIDA
        frame_salida = ttk.LabelFrame(self, text="Resultado")
        frame_salida.pack(fill="both", expand=True, padx=10, pady=6)

        self.text_salida = tk.Text(frame_salida, state="disabled")
        self.text_salida.pack(fill="both", expand=True, padx=6, pady=6)

    # -------------------------------------------------
    # FICHAS
    # -------------------------------------------------

    def _cargar_fichas(self):
        fichas = listar_fichas_disponibles()
        self._mapa_fichas = {f["codigo"]: f for f in fichas}

        self.combo_fichas["values"] = [
            f"{codigo} — {info['nombre']}"
            for codigo, info in self._mapa_fichas.items()
        ]

    # -------------------------------------------------
    # EVENTOS
    # -------------------------------------------------

    def _limpiar_frame_entrada(self):
        for widget in self.frame_entrada.winfo_children():
            widget.pack_forget()

    def _on_ficha_seleccionada(self, event=None):

        seleccion = self.combo_fichas.get()
        if not seleccion:
            return

        codigo = seleccion.split(" — ")[0]
        requisitos = obtener_requisitos_ficha(codigo)

        self._limpiar_frame_entrada()

        if requisitos.get("usa_texto"):
            self.label_texto.pack(anchor="w")
            self.entry_texto.pack(fill="x")

        if requisitos.get("requiere_clave_para_altura"):
            self.label_clave.pack(anchor="w")
            self.combo_clave.pack(fill="x")

        if requisitos.get("tiene_variantes"):
            self.label_tipo_27.pack(anchor="w")
            self.combo_tipo_27.pack(fill="x")
            
            

            # SOLO PARA 2.7
            self.label_romano.pack(anchor="w")
            self.combo_romano.pack(fill="x")

            self.label_simbolo.pack(anchor="w")
            self.combo_simbolo.pack(fill="x")

            self.label_flecha.pack(anchor="w")
            self.combo_flecha.pack(fill="x")
            self.btn_add.pack(pady=5)

        if requisitos.get("tipo_borde") == "contraste":
            self.label_borde.pack(anchor="w")
            self.combo_borde.pack(fill="x")
        
            self.label_contraste_mm.pack(anchor="w")
            self.entry_contraste_mm.pack(fill="x")

    # -------------------------------------------------
    # GENERACIÓN
    # -------------------------------------------------

    def construir_tokens_extra(self):

        tokens = []

        romano_map = {
            "I": "ROM_I",
            "II": "ROM_II",
            "III": "ROM_III",
        }

        simbolo_map = {
            "punto": ".",
            "cuadrado": "CUADRADO",
            "barra": "SLASH",
        }

        flecha_map = {
            "izquierda": "ARROW_LEFT",
            "derecha": "ARROW_RIGHT",
            "arriba": "ARROW_UP",
            "arriba-izquierda": "ARROW_UPLEFT",
            "arriba-derecha": "ARROW_UPRIGHT",
        }

        # romano
        if self.romano_var.get() in romano_map:
            tokens.append(romano_map[self.romano_var.get()])

        # símbolo
        if self.simbolo_var.get() in simbolo_map:
            tokens.append(simbolo_map[self.simbolo_var.get()])

        # flecha
        flecha = flecha_map.get(self.flecha_var.get())

        return tokens, flecha
    
    def _add_token(self):
    
        tokens = []
    
        # ROMANO
        romano_map = {
            "I": "ROM_I",
            "II": "ROM_II",
            "III": "ROM_III",
        }
        romano = self.romano_var.get()
        if romano in romano_map:
            tokens.append(f'"{romano_map[romano]}"')   
    
        # SÍMBOLOS
        simbolo_map = {
            "punto": ".",
            "cuadrado": "CUADRADO",
            "barra": "SLASH",
        }
        simbolo = self.simbolo_var.get()
        if simbolo in simbolo_map:
            tokens.append(f'"{simbolo_map[simbolo]}"')  
    
        # FLECHA
        flecha_map = {
            "izquierda": "ARROW_LEFT",
            "derecha": "ARROW_RIGHT",
            "arriba": "ARROW_UP",
            "arriba-izquierda": "ARROW_UPLEFT",
            "arriba-derecha": "ARROW_UPRIGHT",
        }
        flecha = self.flecha_var.get()
        if flecha in flecha_map:
            tokens.append(f'"{flecha_map[flecha]}"')  
    
        if tokens:
            token_str = "".join(tokens)
        
            pos = self.entry_texto.index(tk.INSERT)
            actual = self.entry_texto.get()
        
            nuevo = actual[:pos] + token_str + actual[pos:]
        
            self.texto_var.set(nuevo)
        
            # mover cursor después del token insertado
            self.entry_texto.icursor(pos + len(token_str))
          
        self.romano_var.set("ninguno")
        self.simbolo_var.set("ninguno")
        self.flecha_var.set("ninguna")
        self.entry_texto.focus_set()

        self.entry_texto.focus_set()

    
    def _generar_senal(self):
        import traceback
        try:
            seleccion = self.combo_fichas.get()
            codigo = seleccion.split(" — ")[0]
            requisitos = obtener_requisitos_ficha(codigo)
    
            texto_base = self.texto_var.get().strip()
            texto_final = texto_base
    
            contexto = {}
    
            if requisitos.get("requiere_clave_para_altura"):
                contexto["clave"] = self.clave_var.get()
    
            if requisitos.get("tiene_variantes"):
                contexto["tipo_2_7"] = self.tipo_27_var.get()


            
            if requisitos.get("tipo_borde") == "contraste":
                opcion = (self.borde_var.get() or "Negro").strip()
            
                
                raw = (self.contraste_mm_var.get() or "").strip().replace(",", ".")
                try:
                    contraste_cm = float(raw) if raw else 0.0
                except ValueError:
                    contraste_cm = 0.0
            
                contraste_mm = contraste_cm * 10.0  # cm -> mm
            
                if contraste_mm <= 0:
                    contexto["contraste_mm"] = 0.0
                    contexto["color_borde_contraste"] = None
                else:
                    contexto["contraste_mm"] = contraste_mm
                    contexto["color_borde_contraste"] = "black" if opcion == "Negro" else "white"


    
            print("DEBUG contexto:", contexto)
            
            resultado = generar_senal(
                codigo_ficha=codigo,
                texto=texto_final,
                altura_mm=None,
                contexto=contexto if contexto else None
            )
    
            if resultado is None:
                raise ValueError("generar_senal() devolvió None (fallo previo en el core).")
    
            # Debug opcional
            
            
            self._ultimo_resultado = resultado
            self._mostrar_resultado(resultado)
    
            from render.render import dibujar_base
            modo_validacion = self.modo_validacion_var.get()

            dibujar_base(resultado, modo_validacion=modo_validacion)

    
        except Exception:
            
            tb = traceback.format_exc()
            print(tb)  # también a consola
            messagebox.showerror("Error", tb)


    # -------------------------------------------------
    # OUTPUT (igual que tenías)
    # -------------------------------------------------
    def _mostrar_resultado(self, r):

        self.text_salida.config(state="normal")
        self.text_salida.delete("1.0", "end")
    
        # -------------------------
        # DESCRIPCIÓN
        # -------------------------
        self.text_salida.insert("end", f"Ficha: {r['ficha']}\n")
        self.text_salida.insert("end", f"Texto: {r['texto']}\n")
        self.text_salida.insert("end", f"Altura: {r['altura_mm']} mm\n")
    
        # WARNING
        if r.get("warning"):
            self.text_salida.insert("end", f"\n{r['warning']}\n")
    
        # -------------------------
        # ACOTACIÓN
        # -------------------------
        acot = r.get("acotacion", {})
        if acot:
            self.text_salida.insert("end", "\n📐 DIMENSIONES\n")
    
            d = acot.get("dimensiones", {})
    
            W_int, H_int = d.get("interior", (0, 0))
            W_ext, H_ext = d.get("exterior", (0, 0))
            W_txt = d.get("texto", 0)
    
            self.text_salida.insert(
                "end",
                f"Interior: {W_int:.0f} x {H_int:.0f} mm\n"
            )
            self.text_salida.insert(
                "end",
                f"Exterior: {W_ext:.0f} x {H_ext:.0f} mm\n"
            )
            self.text_salida.insert(
                "end",
                f"Texto: {W_txt:.0f} mm\n"
            )
    
            # ESPACIADO
            self.text_salida.insert("end", "\n↔ ESPACIADO\n")
            for e in acot.get("espaciado", []):
                self.text_salida.insert(
                    "end",
                    f"{e['entre']}: {e['distancia_mm']:.0f} mm\n"
                )
    
            # MÁRGENES
            marg = acot.get("margenes", {})
            if marg:
                self.text_salida.insert("end", "\n📏 MÁRGENES\n")
                self.text_salida.insert("end", f"Izq: {marg.get('izq', 0):.0f} mm\n")
                self.text_salida.insert("end", f"Der: {marg.get('der', 0):.0f} mm\n")
                self.text_salida.insert("end", f"Sup: {marg.get('sup', 0):.0f} mm\n")
                self.text_salida.insert("end", f"Inf: {marg.get('inf', 0):.0f} mm\n")
    
            # BORDES
            bord = acot.get("bordes", {})
            if bord:
                self.text_salida.insert("end", "\n🖼 BORDES\n")
                self.text_salida.insert("end", f"Lateral: {bord.get('lateral', 0):.0f} mm\n")
                self.text_salida.insert("end", f"Vertical: {bord.get('vertical', 0):.0f} mm\n")
    
        # -------------------------
        # ÁREAS
        # -------------------------
        self.text_salida.insert("end", "\n--- ÁREAS ---\n")
    
        areas = r.get("areas", {}).get("colores_m2", {})
    
        for color, val in areas.items():
            self.text_salida.insert(
                "end",
                f"{color}: {val:.2f} m²\n"
            )
    
        self.text_salida.config(state="disabled")


    def _guardar_imagen(self):
    
        if not hasattr(self, "_ultimo_resultado"):
            messagebox.showwarning("Aviso", "Primero genera una señal")
            return
    
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            title="Guardar imagen"
        )
    
        if not ruta:
            return
    
        from render.render import dibujar_plano
    
        
        dibujar_plano(self._ultimo_resultado, debug=False)
    
        import matplotlib.pyplot as plt
        plt.savefig(ruta, dpi=300, bbox_inches="tight")
        plt.close()
    
        messagebox.showinfo("OK", "Imagen guardada correctamente")


if __name__ == "__main__":
    app = App()
    app.mainloop()
