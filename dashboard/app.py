import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

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
@st.cache_data(show_spinner="Cargando datos... Esto puede tardar unos segundos.")
def load_data():
  """
  Carga el dataset preparado para el análisis.
  """
  db_path = "data/database/videogames.db"
  conn = sqlite3.connect(db_path)
  df = pd.read_sql_query("SELECT * FROM studio_locations", conn)
  conn.close()
  return df

# Cargamos en un dataframe de pandas
df_studios = load_data()



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
tab1, tab2 = st.tabs(["Mapa Interactivo", "Datos en Tabla"])

with tab1:
    render_map_module(filtered_df)

with tab2:
    # Añadimos una sección con la lista de la base de datos
    st.expander("Ver datos en formato tabla")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
