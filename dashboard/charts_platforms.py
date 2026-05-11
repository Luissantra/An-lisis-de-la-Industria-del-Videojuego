import plotly.express as px
import config

PLATFORM_COLORS = {
    "Sony": "#003791",        # Azul PlayStation
    "Nintendo": "#E60012",    # Rojo Nintendo
    "Microsoft": "#107C11",   # Verde Xbox
    "Sega": "#0060A8",        # Azul Sega
    "Atari": "#E32636",       # Rojo Atari
    "Apple": "#A3AAAE",       # Plata
    "PC": "#FF8C00",          # Naranja PC
    "Google": "#3DDC84",      # Verde Android
    "Commodore": "#8E512F",   # Marrón retro
    "Other": "#888888"        # Gris
}

def create_roadmap_timeline(df):
    """Crea una línea de tiempo tipo Roadmap separando por carril (Fabricante)"""
    # Ordenamos por año para que se dibuje correctamente
    df = df.sort_values(by="release_year")
    
    # Manejo de compatibilidad si la base de datos aún no tiene la nueva columna
    if 'games_count' not in df.columns:
        df['games_count'] = 0

    # Generamos un tamaño relativo para la burbuja combinando ventas y catálogo de juegos
    # Si units_sold_millions es NaN, usamos el games_count normalizado
    max_games = df['games_count'].max() if df['games_count'].max() > 0 else 1
    df['bubble_size'] = df['units_sold_millions'].fillna((df['games_count'] / max_games) * 50 + 5)
    
    # Nos aseguramos de que nada sea 0 para que Plotly no lance error
    df['bubble_size'] = df['bubble_size'].clip(lower=2)
    
    fig = px.scatter(
        df,
        x="release_year",
        y="manufacturer",
        size="bubble_size",
        color="manufacturer",
        color_discrete_map=PLATFORM_COLORS,
        text="name",
        custom_data=["name", "generation", "units_sold_millions", "games_count"],
        template="plotly_dark",
        size_max=35 # Tamaño máximo de la burbuja
    )

    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1.5, color='white')),
        hovertemplate="<b>%{customdata[0]}</b><br>Año: %{x}<br>Juegos: %{customdata[3]}<extra></extra>"
    )

    fig.update_layout(
        xaxis_title="Año de Lanzamiento", yaxis_title="",
        margin=dict(t=20, l=20, r=20, b=20), height=550,
        showlegend=False # Ocultamos la leyenda ya que el Eje Y ya dice el nombre
    )

    # Añadir bandas de generaciones para el look de infografía
    generaciones = [
        (1980, 1987, "3ª Gen", "rgba(255, 255, 255, 0.03)"),
        (1987, 1993, "4ª Gen", "rgba(255, 255, 255, 0.0)"),
        (1993, 1998, "5ª Gen", "rgba(255, 255, 255, 0.03)"),
        (1998, 2004, "6ª Gen", "rgba(255, 255, 255, 0.0)"),
        (2004, 2012, "7ª Gen", "rgba(255, 255, 255, 0.03)"),
        (2012, 2020, "8ª Gen", "rgba(255, 255, 255, 0.0)"),
        (2020, 2030, "9ª Gen", "rgba(255, 255, 255, 0.03)")
    ]

    for start, end, label, color in generaciones:
        fig.add_vrect(
            x0=start, x1=end, 
            fillcolor=color, opacity=1, 
            layer="below", line_width=0,
            annotation_text=label, 
            annotation_position="top left",
            annotation_font=dict(size=10, color="rgba(255, 255, 255, 0.2)")
        )
    
    return fig