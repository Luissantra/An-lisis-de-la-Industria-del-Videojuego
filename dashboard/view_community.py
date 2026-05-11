import streamlit as st
import pandas as pd
from model_corporate import get_all_games_data
from charts_community import plot_critic_vs_user, plot_top_controversies, plot_top_acclaimed, plot_social_traction

def render_community_module():
    st.title("🗣️ Comunidad y Recepción (Review Bombing)")
    st.markdown("Analiza el fenómeno del **Review Bombing**, identificando aquellos títulos donde la recepción de los usuarios discrepa severamente de la nota otorgada por la crítica profesional.")
    
    # Cargamos la capa de juegos individuales
    df = get_all_games_data()
    
    # Validación de seguridad defensiva
    if 'rawg_rating' not in df.columns:
        st.warning("⚠️ Faltan métricas de la comunidad. Asegúrate de haber ejecutado el pipeline de extracción de juegos de RAWG.")
        return
    
    # --- Zona de Filtros ---
    st.markdown("#### Filtros de Análisis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Extraer conglomerados únicos descartando nulos
        publishers = ["Todos"] + sorted(df['conglomerate'].dropna().unique().tolist())
        selected_publisher = st.selectbox("Filtrar por Conglomerado (Publisher):", publishers)
        
    with col2:
        # Permitir al usuario ajustar el umbral mínimo de reviews para ver datos más o menos de nicho
        min_reviews = st.number_input("Mínimo de reseñas de usuarios (Ratings Count):", min_value=0, max_value=5000, value=10, step=10)

    # --- Aplicación de Filtros ---
    df_filtered = df.copy()
    if selected_publisher != "Todos":
        df_filtered = df_filtered[df_filtered['conglomerate'] == selected_publisher]
        
    df_filtered['rawg_ratings_count'] = pd.to_numeric(df_filtered['rawg_ratings_count'], errors='coerce').fillna(0)
    df_filtered = df_filtered[df_filtered['rawg_ratings_count'] >= min_reviews]
    
    st.divider()
    
    # --- Renderizado de Gráficos ---
    st.markdown("### 🎭 Capítulo 1: El Espectro de la Crítica")
    st.markdown("""
    ¿Coincide la prensa con los jugadores? En este gráfico buscamos la correlación. Los títulos en la diagonal superior 
    son éxitos unánimes, mientras que los alejados de la línea revelan discrepancias de criterio.
    """)
    fig_scatter = plot_critic_vs_user(df_filtered)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.divider()
    
    st.markdown("### 🧨 Capítulo 2: Review Bombing y Controversias")
    st.markdown("""
    Aquí visualizamos las mayores brechas negativas. Títulos donde la nota de los usuarios es significativamente 
    inferior a la de la crítica, a menudo señal de controversias técnicas, políticas o de monetización.
    """)
    fig_bar = plot_top_controversies(df_filtered)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.markdown("### 🌟 Capítulo 3: Aclamación Popular")
    st.markdown("""
    El "Vox Populi". Juegos que, independientemente de su presupuesto o nota de prensa, han logrado conectar 
    profundamente con la comunidad.
    """)
    fig_acclaim = plot_top_acclaimed(df_filtered)
    st.plotly_chart(fig_acclaim, use_container_width=True)

    st.divider()

    st.markdown("### 🚀 Capítulo 4: Hype y Tracción Social")
    st.markdown("""
    ¿Cuánto se habla de estos juegos? Analizamos el volumen de interacción y la tracción en redes sociales/búsquedas.
    """)
    col_social, col_trends = st.columns([2, 1])
    
    with col_social:
        fig_social = plot_social_traction(df_filtered)
        st.plotly_chart(fig_social, use_container_width=True)
        
    with col_trends:
        st.info("💡 **Análisis de Tendencias Externas**")
        st.markdown("Utiliza Google Trends para comparar el interés de búsqueda en tiempo real.")
        
        search_term = selected_publisher if selected_publisher != "Todos" else "Video Games"
        import urllib.parse
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://trends.google.com/trends/explore?q={encoded_term}"
        
        st.link_button(f"🔍 Ver '{search_term}' en Google Trends", url)
        
        st.caption("Google Trends permite validar si el volumen de reseñas en RAWG se correlaciona con el interés de búsqueda global.")