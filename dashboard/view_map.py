import streamlit as st
from streamlit_folium import st_folium
from charts import create_interactive_map


# Vistas por regiones
REGION_VIEWS = {
    "Entire World": {"center": [0, 0], "zoom": 2},
    "North America": {"center": [-100, 45], "zoom": 4},
    "Europe": {"center": [15, 50], "zoom": 6},
    "Asia": {"center": [100, 30], "zoom": 3},
    "Japan (Focus)": {"center": [138, 36], "zoom": 8}
}

def render_map_module(filtered_df):
  """"
  Renderiza el módulo del mapa interactivo con los datos filtrados.
  """
  st.subheader("Mapa de Ubicación de Estudios de Videojuegos")

  # Controles locales de visualización
  col1, col2 = st.columns([1, 3]) # el dropdown ocupa menos espacio que el mapa
  with col1:
      selected_region = st.selectbox("📍 Zoom a la región:", list(REGION_VIEWS.keys()))
      
  view_center = REGION_VIEWS[selected_region]["center"]
  view_zoom = REGION_VIEWS[selected_region]["zoom"]

  # Renderizamos el mapa interactivo con los datos filtrados
  folium_map = create_interactive_map(filtered_df, center=view_center, zoom=view_zoom)
  st_folium(folium_map, width=1200, height=600, returned_objects=[])
  
