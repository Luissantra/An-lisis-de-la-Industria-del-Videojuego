import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import json
import config

# Cargamos la configuración visual desde el JSON
try:
    with open(config.MARKET_VISUALS_JSON, 'r', encoding='utf-8') as f:
        visual_config = json.load(f)
    BRAND_COLORS = visual_config.get("brand_colors", {})
    KEY_EVENTS = visual_config.get("key_events", [])
except Exception as e:
    BRAND_COLORS = {}
    KEY_EVENTS = []

def create_comparison_line_chart(df, timeframe, benchmark="Ninguno"):
    """
    Gráfico de líneas con colores de marca y recalculado en base 0.
    """

    # Subtítulo dinámico
    if timeframe == "Max": gran_text = "Evolución Mensual"
    elif timeframe == "5Y": gran_text = "Evolución Semanal"
    else: gran_text = "Evolución Diaria"
    fig = px.line(
        df, 
        x='Date', 
        y='Period_Return_%', 
        color='Company Name',
        color_discrete_map=BRAND_COLORS, 
        title=f"Comparativa de Retorno en {timeframe} ({gran_text})",
        labels={'Period_Return_%': 'Retorno en Período (%)', 'Date': 'Fecha', 'Company Name': 'Empresa'},
        template="plotly_dark"
    )

    # Estilizar el Benchmark para que destaque como índice de referencia
    if benchmark != "Ninguno" and benchmark in df['Company Name'].values:
        fig.update_traces(
            line=dict(dash='dot', width=4, color='rgba(255, 255, 255, 0.4)'),
            name=f"🏁 {benchmark} (Referencia)",
            selector=dict(name=benchmark) # Busca específicamente el trazo con este nombre
        )
    
    # Añadir Líneas de Hitos (Anotaciones)
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    companies_in_df = df['Company Name'].unique()

    for item in KEY_EVENTS:
        event_date = pd.to_datetime(item["date"])
        if min_date <= event_date <= max_date and item["company"] in companies_in_df:
            fig.add_vline(x=event_date, line_width=1, line_dash="dash", line_color=BRAND_COLORS.get(item["company"], "white"))
            fig.add_annotation(
                x=event_date, 
                y=1.05, 
                yref='paper', 
                text=item["event"],
                showarrow=False,
                font=dict(color=BRAND_COLORS.get(item["company"], "white"), size=10),
                textangle=-45 
            )

    fig.update_layout(hovermode="x unified", margin=dict(t=80)) 
    return fig

def create_candlestick_chart(df, company_name, timeframe):
    """
    Vista Pro: Gráfico de velas japonesas con Volumen y Medias Móviles (SMA 50/200).
    """
    # Definimos el subtítulo dinámico
    if timeframe == "Max": gran_text = "Velas Mensuales"
    elif timeframe == "5Y": gran_text = "Velas Semanales"
    else: gran_text = "Velas Diarias"
    company_data = df[df['Company Name'] == company_name].sort_values('Date').copy()
    
    # 1. Calcular Medias Móviles (SMA 50 y SMA 200)
    # IMPORTANTE: Al cambiar de diario a mensual, las medias móviles de 50 y 200 periodos cambian de significado
    # SMA 50 en gráfico mensual equivale a la media de 50 meses (4 años!).
    company_data['SMA_50'] = company_data['Close'].rolling(window=50, min_periods=1).mean()
    company_data['SMA_200'] = company_data['Close'].rolling(window=200, min_periods=1).mean()
    
    # 2. Definir colores del volumen (Verde si cierra más alto de lo que abrió, Rojo si cierra más bajo)
    company_data['Volume_Color'] = company_data.apply(
        lambda row: '#26A69A' if row['Close'] >= row['Open'] else '#EF5350', axis=1
    )

    # 3. Crear Subplots: 2 filas, 1 columna (compartiendo el eje X temporal)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.75, 0.25] # 75% espacio para velas, 25% para volumen
    )

    # Añadir Velas Japonesas (Fila 1)
    fig.add_trace(go.Candlestick(
        x=company_data['Date'],
        open=company_data['Open'],
        high=company_data['High'],
        low=company_data['Low'],
        close=company_data['Close'],
        name='Precio',
        increasing_line_color='#26A69A', # Verde moderno
        decreasing_line_color='#EF5350'  # Rojo moderno
    ), row=1, col=1)

    # Añadir Media Móvil 50 (Fila 1)
    fig.add_trace(go.Scatter(
        x=company_data['Date'], y=company_data['SMA_50'],
        mode='lines', line=dict(color='rgba(255, 165, 0, 0.8)', width=1.5), # Naranja
        name='SMA 50'
    ), row=1, col=1)

    # Añadir Media Móvil 200 (Fila 1)
    fig.add_trace(go.Scatter(
        x=company_data['Date'], y=company_data['SMA_200'],
        mode='lines', line=dict(color='rgba(135, 206, 250, 0.8)', width=1.5), # Azul celeste
        name='SMA 200'
    ), row=1, col=1)

    # Añadir Volumen (Fila 2)
    fig.add_trace(go.Bar(
        x=company_data['Date'], y=company_data['Volume'],
        marker_color=company_data['Volume_Color'],
        name='Volumen'
    ), row=2, col=1)

    # Añadir Hitos al gráfico de velas
    min_date = company_data['Date'].min()
    max_date = company_data['Date'].max()
    for item in KEY_EVENTS:
        if item["company"] == company_name:
            event_date = pd.to_datetime(item["date"])
            if min_date <= event_date <= max_date:
                fig.add_vline(x=event_date, line_width=1, line_dash="dash", line_color="#888", row=1, col=1)
                fig.add_annotation(
                    x=event_date, y=1.05, yref='paper', 
                    text=item["event"], showarrow=False, 
                    font=dict(color="#AAA", size=10)
                )

    # Limpiar y modernizar el diseño general
    fig.update_layout(
        title=f"Análisis Técnico: {company_name} ({gran_text})",
        template="plotly_dark",
        xaxis_rangeslider_visible=False, # Ocultamos el slider nativo de velas porque ya tenemos filtros
        height=650,
        margin=dict(t=80, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # Leyenda horizontal arriba
    )

    # Nombres de los ejes Y
    fig.update_yaxes(title_text="Precio (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volumen", row=2, col=1)
    
    # Ocultar fines de semana y festivos en el eje X para no ver huecos vacíos en las velas
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], row=1, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], row=2, col=1)

    return fig