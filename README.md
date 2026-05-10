# Análisis de la Industria del Videojuego - Dashboard

Este proyecto es una plataforma de análisis de datos e inteligencia de negocios enfocada en la evolución histórica y comercial de la industria del videojuego. Utiliza herramientas de visualización avanzadas para explorar el ciclo de vida de las plataformas, ventas globales y el tamaño de los catálogos de juegos.

## 🚀 Características

- **Roadmap de Plataformas:** Visualización interactiva tipo línea de tiempo que organiza las consolas por fabricante.
- **Identidad Visual Consistente:** Sistema de colores predefinido para los principales actores de la industria (Sony, Nintendo, Microsoft, Sega, etc.).
- **Métricas Dinámicas:** Representación visual del éxito de mercado mediante el tamaño de burbujas, integrando ventas en millones y conteo de títulos disponibles.
- **Interfaz Profesional:** Gráficos optimizados con temas oscuros (`plotly_dark`) y tooltips detallados.

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**
- **Pandas:** Procesamiento y limpieza de datos.
- **Plotly Express:** Generación de gráficos interactivos.
- **Dashboard Framework:** (Estructura preparada para integración con Streamlit o Dash).

## 📂 Estructura del Proyecto

```text
├── dashboard/
│   ├── charts_platforms.py   # Lógica de visualización de plataformas
│   └── config.py             # Configuraciones globales
├── data/                     # Datasets de la industria (Ventas, fechas, fabricantes)
└── README.md
```

## 📊 Visualizaciones Principales

### Roadmap Timeline
El módulo `charts_platforms.py` genera una línea de tiempo donde el eje Y segmenta a los fabricantes y el eje X representa el año de lanzamiento. El tamaño de cada punto se calcula dinámicamente:
1. Si existen datos de ventas, se utiliza `units_sold_millions`.
2. Si no hay ventas registradas, se normaliza según el `games_count` (cantidad de juegos).

## 📝 Requisitos

Instala las dependencias necesarias con:
`pip install pandas plotly`