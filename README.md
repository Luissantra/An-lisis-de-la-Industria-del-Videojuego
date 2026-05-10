# 🎮 Análisis de la Industria del Videojuego

Un dashboard interactivo y pipeline de datos (ETL) construido en Python para analizar la industria del videojuego desde tres dimensiones fundamentales: **Geográfica, Financiera y Corporativa**.

Este proyecto extrae datos de múltiples fuentes (APIs, web scraping, bases de datos financieras), los procesa y centraliza en una base de datos relacional SQLite, para luego visualizarlos a través de una aplicación web de alto rendimiento usando **Streamlit**.

---

## ✨ Características Principales

El dashboard está dividido en tres módulos clave:

1. **🌍 Mapa de Estudios (Dimensión Geográfica):**
   * Visualización interactiva con `Folium` de miles de estudios de desarrollo alrededor del mundo.
   * Datos obtenidos vía Web Scraping y geocodificados usando Nominatim (OpenStreetMap).
   * Clústeres dinámicos por región y enlaces directos a Google Maps.

2. **📈 Análisis de Mercado (Dimensión Financiera):**
   * Histórico de cotizaciones en bolsa de los gigantes del sector (Sony, Microsoft, Nintendo, EA, Tencent, etc.).
   * Gráficos interactivos de líneas (retornos porcentuales) y Velas Japonesas (candlestick) con medias móviles (SMA) y volumen.
   * Hitos históricos superpuestos en las gráficas (ej. fecha de lanzamiento de consolas o adquisiciones importantes).
   * Datos impulsados por `yfinance`.

3. **🏢 Estructura Corporativa (Dimensión Empresarial):**
   * Análisis visual mediante gráficos *Sunburst* de la relación entre Conglomerados (Parent) y Estudios Filiales.
   * Integración con la **API de RAWG** para obtener automáticamente los metadatos del juego más destacado de cada estudio, género y su nota en Metacritic.
   * Rendimiento ultra rápido gracias a cruces de datos nativos en SQL.

---

## 🏗️ Arquitectura y Tecnologías

* **Frontend:** Streamlit
* **Procesamiento de Datos:** Pandas, Numpy
* **Visualización:** Plotly, Folium
* **Base de Datos:** SQLite (`videogames.db` como *Single Source of Truth*)
* **ETL & Extracción:** `requests`, `BeautifulSoup` (Scraping), `yfinance` (Bolsa), RAWG API (Juegos), Wikipedia API (Logos).

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Luissantra/An-lisis-de-la-Industria-del-Videojuego.git
cd "An-lisis-de-la-Industria-del-Videojuego"
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En macOS/Linux
# venv\Scripts\activate   # En Windows

pip install -r requirements.txt
```

### 3. Variables de entorno (API Keys)
Para descargar la información de los videojuegos (notas de Metacritic, géneros, etc.), el proyecto utiliza la API de RAWG. Necesitas obtener una clave gratuita en rawg.io y configurarla en tu terminal:

```bash
export RAWG_API_KEY="tu_clave_api_aqui"
```
*(En Windows usa `set RAWG_API_KEY="tu_clave_api_aqui"`).*

---

## 🕹️ Uso del Proyecto

El proyecto se divide en dos partes: el **Pipeline de Datos (Backend)** y el **Dashboard (Frontend)**.

### 1. Actualizar los Datos (Pipeline ETL)
Puedes ejecutar todo el proceso de extracción, transformación y carga (ETL) utilizando el orquestador principal:

```bash
python main.py
```
*Nota: Puedes usar parámetros como `--skip-extract` si solo quieres reconstruir la base de datos sin volver a descargar cosas.*

Para actualizar **solo los metadatos de los juegos** desde la API de RAWG:
```bash
python scripts/etl_games.py
```

### 2. Ejecutar el Dashboard
Una vez que la base de datos `videogames.db` esté generada, levanta la aplicación web con:

```bash
streamlit run dashboard/app.py
```