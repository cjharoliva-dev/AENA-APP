**# EXA40 Señalizador Aeroportuario**



Herramienta en Python para el diseño, cálculo y generación de carteles EXA‑40 y señalización horizontal aeroportuaria conforme a normativa AN2.1 y EXA‑40.  

Incluye motores geométricos, reglas normativas, cálculo de áreas de pintura y un interfaz gráfico (GUI) para facilitar su uso por técnicos y proyectistas.



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------





**## Descripción general**



Este proyecto automatiza la creación de carteles EXA‑40 y elementos de señalización horizontal utilizados en aeropuertos.  

Permite:



\- Componer textos normativos AN2.1

\- Calcular dimensiones, espaciados y proporciones según EXA‑40

\- Generar geometría vectorial de los carteles

\- Renderizar la señal en pantalla

\- Calcular áreas de pintura

\- Exportar resultados

\- Utilizar una interfaz gráfica sencilla para técnicos



El objetivo es disponer de una herramienta fiable, reproducible y basada en normativa oficial.



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------





**# Estructura del proyecto**



exa40\_senalizacion\_h/

│

├── datos/                     # Datos base (caracteres AN2.1, configuraciones…)

│   └── an21\_caracteres\_base.json

│

├── calculo/                   # Cálculos de áreas y métricas

│   └── areas.py

│

├── normativa/                 # Reglas normativas EXA‑40 y AN2.1

│   ├── cartel\_exa40.py

│   ├── dimensiones\_exa.py

│   ├── espaciado\_an21.py

│   └── fichas.py

│

├── geometria/                 # Motores geométricos y composición de texto

│   ├── motor\_texto\_AN21.py

│   ├── acotacion.py

│   └── compositor.py

│

├── interfaz/                  # Interfaz gráfica (GUI)

│   └── app.py

│

├── render/                    # Renderizado final del cartel

│   └── render.py

│

├── dist/                      # Ejecutable (opcional)

│   └── EXA40\_Senalizador.exe

│

├── core.py                    # API principal para la GUI

├── requirements.txt           # Dependencias del proyecto

└── README.md                  # Este archivo



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------



**## Instalación**



\### 1. Clonar el repositorio



```bash

git clone https://github.com/tu\_usuario/tu\_repositorio.git

cd exa40\_senalizacion\_h



\### 2. Dependencias

pip install -r requirements.txt



\----



\#EJECUTAR ARCHIVO



\## DESDE PYTHON



python interfaz/app.py



\---------OR---------------



py interfaz/app.py



(se ha detectado que el comando Python no siempre es reconocido, en mi caso funciona py interfaz/app.py)



\## EJECUTAR EL .EXE



dist/EXA40\_Senalizador.exe



(no requiere Python)



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------



**##Funcionalidades principales**



Motor AN2.1 para composición de texto normativo



Reglas EXA‑40 para dimensiones, colores y espaciados



Renderizado vectorial mediante matplotlib



Cálculo de áreas de pintura



Acotación automática



Interfaz gráfica para uso técnico



API modular (core.py) para integraciones futuras



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------





**Autor**



Proyecto desarrollado por un técnico especializado en infraestructura aeroportuaria, señalización horizontal y digitalización de procesos.



\-----------------------------------------------------------------------------------------------------

\-----------------------------------------------------------------------------------------------------





**Licencia**



Este proyecto puede incluir normativa oficial.

Asegúrate de revisar las condiciones de uso antes de distribuirlo.



