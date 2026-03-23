import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

from pathlib import Path
import sys

# Añadir la raíz al path para poder importar config
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


# Importamos nuestros módulos de visualización
from view_map import render_map_module


# Page Configuration
st.set_page_config(
    page_title="Análisis de la Industria del Videojuego",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data loading and caching
@st.cache_data(show_spinner="Cargando datos del mapa... Esto puede tardar unos segundos.")
def load_geo_data():
  """
  Carga el dataset preparado para el análisis.
  """

  conn = sqlite3.connect(config.DATABASE_PATH)
  df = pd.read_sql_query("SELECT * FROM studio_locations", conn)
  conn.close()
  return df

@st.cache_data(show_spinner="Cargando datos de mercado... Esto puede tardar unos segundos.")
def load_market_data():
    """
    Carga el dataset de market data preparado para el análisis.
    """
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        df = pd.read_sql_query("SELECT * FROM stock_prices", conn)
        # Convertimos la columna Date a formato fecha para que Streamlit la grafique bien
        df['Date'] = pd.to_datetime(df['Date']) 
        conn.close()
        return df
    except Exception as e:
        # Si la tabla no existe aún, devolvemos un DataFrame vacío
        return pd.DataFrame()

    
  

# Cargamos los datos
df_studios = load_geo_data()
df_market = load_market_data()




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
    st.markdown("### Rendimiento en Bolsa de Gigantes del Sector")
    
    if df_market.empty:
        st.warning("No se encontraron datos financieros. Asegúrate de ejecutar el pipeline de datos (`python main.py`).")
    else:
        # Filtro de empresas para el gráfico financiero
        companies = sorted(df_market['Company Name'].unique().tolist())
        # Por defecto mostramos un par interesantes
        default_companies = [c for c in ["Nintendo Co., Ltd.", "Electronic Arts", "Microsoft Corporation"] if c in companies]
        
        selected_companies = st.multiselect(
            "Selecciona empresas para comparar:", 
            options=companies, 
            default=default_companies
        )
        
        if selected_companies:
            # Filtramos los datos por las empresas seleccionadas
            market_filtered = df_market[df_market['Company Name'].isin(selected_companies)]
            
            # Pivotamos los datos para que Streamlit los dibuje en varias líneas automáticamente
            # Índice: Fecha | Columnas: Nombre de la Empresa | Valores: Rendimiento Acumulado
            chart_data = market_filtered.pivot(index='Date', columns='Company Name', values='Cumulative_Return_%')
            
            st.markdown("#### Retorno Acumulado Histórico (%)")
            st.line_chart(chart_data, use_container_width=True)
            
            # Un pequeño extra: Mostrar la categoría y ticker
            st.markdown("#### Información de Tickers")
            info_df = market_filtered[['Company Name', 'Ticker', 'Category']].drop_duplicates().reset_index(drop=True)
            st.dataframe(info_df, use_container_width=True)
        else:
            st.info("Selecciona al menos una empresa para ver el gráfico.")