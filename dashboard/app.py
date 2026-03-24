import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import config

# Importamos nuestros módulos de visualización
from view_map import render_map_module
from view_market import render_market_module


# Page Configuration
st.set_page_config(
    page_title="Análisis de la Industria del Videojuego",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data loading and caching

# Dimensión geográfica (mapa)
@st.cache_data(show_spinner="Cargando datos del mapa... Esto puede tardar unos segundos.")
def load_geo_data():
  """
  Carga el dataset preparado para el análisis.
  """

  conn = sqlite3.connect(config.DATABASE_PATH)
  df = pd.read_sql_query("SELECT * FROM studio_locations", conn)
  conn.close()
  return df

# Dimensión de mercado (bolsa)
@st.cache_data(show_spinner="Cargando lista de activos...")
def get_market_assets():
    """
    Consulta a la BBDD y separa dinámicamente empresas de índices (benchmarks)
    basándose en la columna 'Category'.
    """
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        # Traemos nombres y categorías
        query = 'SELECT DISTINCT "Company Name", "Category" FROM stock_prices'
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Filtramos dinámicamente: Si la categoría contiene la palabra "Índice", es un benchmark
        indices = df[df['Category'].str.contains('Índice', case=False, na=False)]['Company Name'].tolist()
        empresas = df[~df['Category'].str.contains('Índice', case=False, na=False)]['Company Name'].tolist()
        
        # Las ordenamos alfabéticamente
        return sorted(empresas), sorted(indices)
    except Exception as e:
        return [], []

@st.cache_data(show_spinner="Consultando datos financieros...")
def load_dynamic_market_data(selected_companies):
    """
    Carga el histórico de mercado SOLO para las empresas que el usuario ha seleccionado.
    """
    if not selected_companies:
        return pd.DataFrame() # Si no hay selección, devolvemos un dataframe vacío rápido
        
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        
        # Construimos la consulta SQL con placeholders para evitar inyecciones y problemas de formato
        placeholders = ','.join(['?'] * len(selected_companies))
        query = f'SELECT * FROM stock_prices WHERE "Company Name" IN ({placeholders})'
        
        # Pasamos la lista de empresas como parámetros
        df = pd.read_sql_query(query, conn, params=selected_companies)
        df['Date'] = pd.to_datetime(df['Date']) 
        conn.close()
        
        return df
    except Exception as e:
        return pd.DataFrame()
    
  

# Cargamos los datos
df_studios = load_geo_data()





# Filtros de ubicación
# Interfaz de usuario
st.sidebar.header("Filtros de Ubicación")

# Creamos una lista de países únicos para el filtro y una opción de todos
country_list = ["Todos"] + sorted(df_studios['Country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Selecciona un país:", country_list)

# Añadimos una caja de texto para filtrar por estudios
search_query = st.sidebar.text_input("Buscar por nombre de estudio:")

# Aplicamos los filtros al dataframe
filtered_df = df_studios.copy()

# Filtro de country
if selected_country != "Todos":
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]

# Filtro de búsqueda por nombre de estudio
if search_query:
    filtered_df = filtered_df[filtered_df['Studio Name'].str.contains(search_query, case=False, na=False)]



# Renderizamos los módulos
tab1, tab2, tab3 = st.tabs(["Mapa Interactivo", "Datos en Tabla", "Análisis de Mercado"])

with tab1:
    render_map_module(filtered_df)

with tab2:
    # Añadimos una sección con la lista de la base de datos
    st.expander("Ver datos en formato tabla")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### Análisis Financiero de Gigantes del Sector")
    
    # 1. Obtenemos solo la lista de nombres de empresas y benchmarks
    solo_empresa, indices = get_market_assets()
    
    if not solo_empresa:
        st.warning("No se encontraron datos financieros. Asegúrate de ejecutar el pipeline de datos (`python main.py`).")
    else:
        # 2. Selector de empresas
        default_companies = [c for c in ["Nintendo Co., Ltd.", "Electronic Arts", "Microsoft Corporation"] if c in solo_empresa]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_companies = st.multiselect(
                "Selecciona empresas para comparar:", 
                options=solo_empresa, 
                default=default_companies
            )
        with col2:
            selected_benchmark = st.selectbox(
                "Selecciona un benchmark (opcional):", 
                options=["Ninguno"] + indices
            )

        # Combinamos las empresas y el benchmark para hacer solo una consulta
        query_companies = selected_companies.copy()
        if selected_benchmark != "Ninguno":
            query_companies.append(selected_benchmark)
        
        # 3. Carga dinámica. Solo pedimos a la BBDD lo que el usuario eligió.
        df_market = load_dynamic_market_data(query_companies)
        
        # 4. Renderizamos toda la interfaz pasándole los datos
        render_market_module(df_market, selected_companies, benchmark=selected_benchmark)