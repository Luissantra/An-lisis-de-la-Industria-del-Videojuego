import streamlit as st
import pandas as pd
import base64
import sqlite3
import config
from pathlib import Path
from charts_corporate import create_sunburst_chart, create_genre_and_score_chart, PARENT_COLOR_MAP



@st.cache_data(show_spinner="Cargando estructura corporativa...")
def load_corporate_data():
    """Carga y cruza la matriz de estudios y juegos directamente desde SQLite."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    
    query = """
        SELECT 
            c.name as Parent,
            s.name as "Studio Name",
            s.city as City,
            s.country as Country,
            s.acquisition_year as Acquisition_Year,
            COALESCE(g.name, 'No registrado') as Top_Game,
            COALESCE(g.genres, 'Desconocido') as Genres,
            g.metacritic as Metacritic
        FROM conglomerates c
        JOIN notable_studios s ON c.id = s.parent_id
        LEFT JOIN games_metadata g ON s.id = g.studio_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Aseguramos de rellenar posibles nulos por consistencia en la vista
    df['City'] = df['City'].fillna('N/A')
    df['Country'] = df['Country'].fillna('N/A')
    df['Top_Game'] = df['Top_Game'].fillna('No registrado')
    df['Acquisition_Year'] = df['Acquisition_Year'].fillna('No registrado')
    df['Genres'] = df['Genres'].fillna('Desconocido')
    
    return df

def get_base64_image(empresa_name):
    """Lee el logo local y lo convierte a base64 para inyectarlo en HTML."""
    safe_name = "".join([c if c.isalnum() or c in " &()_-" else "_" for c in empresa_name])
    img_path = config.LOGOS_DIR / f"{safe_name}.png"
    
    if img_path.exists():
        with open(img_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None


# Función Callback para actualizar el estado instantáneamente
def seleccionar_matriz(matriz):
    st.session_state.selected_parent = matriz

def render_corporate_module():
    st.title("🏢 Estructura Corporativa de la Industria")
    
    # CSS Inyectado para interacciones profesionales (Efecto Hover en las tarjetas)
    st.markdown("""
    <style>
    .corp-card {
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .corp-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(255, 255, 255, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    df_corp = load_corporate_data()
    if 'selected_parent' not in st.session_state:
        st.session_state.selected_parent = "Global"

    empresas = list(df_corp['Parent'].unique())
    seleccion = st.session_state.selected_parent
    
    # 1. Galería de Logos con Interacción Visual (Opacidad)
    st.markdown("##### Selecciona un conglomerado:")
    cols = st.columns(6)
    
    for i, empresa in enumerate(empresas):
        with cols[i % 6]:
            with st.container(border=False):
                # Calcular estilos dependiendo de si está seleccionada o no
                is_selected = (seleccion == empresa)
                is_global = (seleccion == "Global")
                
                # Si estamos en Global, todos brillan. Si hay uno seleccionado, los demás se atenúan (30% opacidad).
                opacity = "1.0" if is_selected or is_global else "0.3"
                brand_color = PARENT_COLOR_MAP.get(empresa, "#444444")
                img_b64 = get_base64_image(empresa)
                
                bg_color = "rgba(240, 242, 246, 0.92)" # Blanco suavizado para menos contraste con el fondo oscuro
                div_style = (
                    f"display: flex; justify-content: center; align-items: center; height: 95px; "
                    f"opacity: {opacity}; transition: 0.3s; background-color: {bg_color}; "
                    f"border: 3px solid {brand_color}; border-radius: 10px; padding: 10px; margin-bottom: 10px;"
                )

                if img_b64:
                    st.markdown(
                        f'<div class="corp-card" style="{div_style}">'
                        f'<img src="{img_b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;">'
                        f'</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    # Fallback por si falta el logo local
                    st.markdown(f'<div class="corp-card" style="{div_style}"><span style="color:#000000; font-weight:bold; font-size:12px; text-align:center;">{empresa}</span></div>', unsafe_allow_html=True)
                
                # Botón de control
                if is_selected:
                    st.button("✅ Viendo", key=f"btn_{i}", disabled=True, use_container_width=True)
                else:
                    st.button("Analizar", key=f"btn_{i}", on_click=seleccionar_matriz, args=(empresa,), use_container_width=True)

    # 2. Control Superior
    col_v, col_btn = st.columns([4, 1])
    with col_btn:
        if seleccion != "Global":
            if st.button("🔄 Ver Todas", use_container_width=True):
                seleccionar_matriz("Global")
                st.rerun()
                
    st.divider()

    # 3. Representación Gráfica
    if seleccion == "Global":
        st.subheader("🌍 Visión Macro (Ecosistema Completo)")
        fig = create_sunburst_chart(df_corp)
        
        # Capturamos el evento de clic nativo (soportado en Streamlit >= 1.35)
        try:
            evento = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
            if evento and "selection" in evento and evento["selection"].get("points"):
                clicked_label = evento["selection"]["points"][0].get("label")
                # Si el usuario hace clic en un conglomerado, sincronizamos la tarjeta
                if clicked_label in empresas and clicked_label != seleccion:
                    st.session_state.selected_parent = clicked_label
                    st.rerun()
        except TypeError:
            # Fallback por si la versión de Streamlit es antigua y no soporta on_select
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader(f"🔍 Análisis Estructural: {seleccion}")
        df_filtrado = df_corp[df_corp['Parent'] == seleccion]
        brand_color = PARENT_COLOR_MAP.get(seleccion, "#444444")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Estudios Filiales", len(df_filtrado))
        c2.metric("Presencia (Países)", df_filtrado['Country'].nunique())
        c3.metric("Ciudades Diferentes", df_filtrado['City'].nunique())
        
        st.write("---")
        
        col_grafico, col_lista = st.columns([1.5, 1])
        
        with col_grafico:
            st.markdown("#### Distribución Organizativa")
            fig = create_sunburst_chart(df_filtrado)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_lista:
            st.markdown("### 🎮 Directorio de Estudios")
            for index, row in df_filtrado.iterrows():
                with st.expander(f"🏢 {row['Studio Name']}"):
                    st.write(f"**📍 Sede:** {row['City']}, {row['Country']}")
                    st.write(f"**🕹️ Juego Clave:** {row['Top_Game']}")
                    st.write(f"**🗓️ Adquisición/Fundación:** {row['Acquisition_Year']}")

        st.markdown("---")
        
        st.markdown("#### 🏆 Análisis de Portfolio (Géneros y Calidad)")
        fig_genres = create_genre_and_score_chart(df_filtrado, color=brand_color)
        
        if fig_genres:
            st.plotly_chart(fig_genres, use_container_width=True)
        else:
            st.info("ℹ️ Ejecuta el script `etl_games.py` con tu clave API para habilitar los gráficos de géneros y valoraciones.")