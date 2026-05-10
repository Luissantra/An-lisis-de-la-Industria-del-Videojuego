import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import config

# Cargar configuraciones visuales
try:
    with open(config.MARKET_VISUALS_JSON, 'r', encoding='utf-8') as f:
        visual_config = json.load(f)
    BRAND_COLORS = visual_config.get("brand_colors", {})
except Exception:
    BRAND_COLORS = {}

# Mapeador para enlazar las claves del JSON de matriz con las del JSON de colores
PARENT_COLOR_MAP = {
    "Microsoft Gaming (Xbox, ZeniMax, Activision Blizzard)": BRAND_COLORS.get("Microsoft Corporation", "#107C11"),
    "Sony Interactive Entertainment (PlayStation Studios)": "#003791", # Usamos el Azul PlayStation para que no colisione con el negro de Take-Two
    "Tencent": BRAND_COLORS.get("Tencent Holdings", "#3458B0"),
    "Nintendo": BRAND_COLORS.get("Nintendo Co., Ltd.", "#E60012"),
    "Electronic Arts (EA)": BRAND_COLORS.get("Electronic Arts", "#FF4545"),
    "Take-Two Interactive": BRAND_COLORS.get("Take-Two Interactive", "#000000"),
    "Ubisoft": BRAND_COLORS.get("Ubisoft Entertainment", "#0070FF"),
    "Sega Sammy": BRAND_COLORS.get("Sega Sammy", "#0060A8"),
    "Independent & Other Publishers": "#444444" # Color gris genérico
}

def create_sunburst_chart(df):
    """
    Crea el gráfico Sunburst interactivo.
    El tamaño del segmento se basará en el conteo (1 por estudio).
    """
    # Asignamos valor 1 para que el tamaño dependa de la cantidad de estudios filiales
    df['Tamaño'] = 1

    # Creamos un mapa de colores local para asegurar que los no registrados sean grises y no amarillos
    local_color_map = PARENT_COLOR_MAP.copy()
    for parent in df['Parent'].unique():
        if parent not in local_color_map:
            local_color_map[parent] = "#444444"

    fig = px.sunburst(
        df,
        path=['Parent','Studio Name'], 
        values='Tamaño',
        color='Parent',
        color_discrete_map=local_color_map,
        hover_data=['City', 'Country', 'Top_Game', 'Acquisition_Year'],
        template="plotly_dark"
    )

    # Personalizar el Tooltip (Hover)
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "📍 Ubicación: %{customdata[0]}, %{customdata[1]}<br>"
            "🎮 Juego Notable: %{customdata[2]}<br>"
            "🗓️ Adquisición: %{customdata[3]}<extra></extra>"
        )
    )
    
    fig.update_traces(
        # Añade un borde oscuro/claro delgado entre los segmentos para separarlos limpiamente
        marker=dict(line=dict(color='#0E1117', width=1.5)),
        # Muestra el texto y el porcentaje que representa del nodo padre
        textinfo="label+percent parent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "📍 Ciudad: %{customdata[0]}<br>"
            "🎮 Juego Notable: %{customdata[1]}<br>"
            "🗓️ Adquisición: %{customdata[2]}<extra></extra>"
        )
    )
    
    # Añadir trazas invisibles (Scatter) para generar una leyenda personalizada
    for parent in df['Parent'].unique():
        color = local_color_map.get(parent, "#444444")
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=color, symbol='square'),
            name=parent,
            showlegend=True,
            hoverinfo='none' # Para que esta traza fantasma no interfiera con los tooltips
        ))

    fig.update_layout(
        margin=dict(t=20, l=0, r=0, b=80),
        height=750,
        # Fondo transparente para que se integre perfectamente con Streamlit
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            itemclick=False,
            itemdoubleclick=False
        ),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

def create_genre_and_score_chart(df, color="#0070FF"):
    """
    Crea un gráfico de barras mostrando la cantidad de juegos por género 
    del conglomerado, incluyendo información de Metacritic.
    """
    if 'Genres' not in df.columns or df['Genres'].eq('Desconocido').all():
        return None
        
    # Explotar la columna de géneros (ya que un juego puede tener varios separados por coma)
    df_genres = df.copy()
    df_genres = df_genres[df_genres['Genres'] != 'Desconocido']
    df_genres['Genre_List'] = df_genres['Genres'].str.split(', ')
    df_exploded = df_genres.explode('Genre_List')
    
    if df_exploded.empty:
        return None
        
    # Agrupar por género y calcular la media de metacritic
    genre_stats = df_exploded.groupby('Genre_List').agg(
        Count=('Studio Name', 'count'),
        Avg_Metacritic=('Metacritic', 'mean')
    ).reset_index()
    
    genre_stats = genre_stats.sort_values(by='Count', ascending=True)
    
    fig = px.bar(
        genre_stats, x='Count', y='Genre_List', orientation='h', template="plotly_dark",
        labels={'Count': 'Número de Juegos', 'Genre_List': 'Género', 'Avg_Metacritic': 'Nota Media (Metacritic)'},
        hover_data=['Avg_Metacritic']
    )
    fig.update_traces(marker_color=color, marker_line_color='#E5E5E5', marker_line_width=1,
                      hovertemplate="<b>%{y}</b><br>Juegos: %{x}<br>Nota Media: %{customdata[0]:.1f}<extra></extra>")
    fig.update_layout(margin=dict(t=20, l=0, r=0, b=20), yaxis={'categoryorder': 'total ascending'},
                      xaxis_title="Cantidad de Juegos (Estudios)", yaxis_title="")
    return fig