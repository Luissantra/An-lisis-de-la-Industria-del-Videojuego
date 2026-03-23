import yfinance as yf
import pandas as pd
import warnings

# Suprimir advertencias para mantener la consola limpia
warnings.simplefilter(action='ignore', category=FutureWarning)

# Diccionario maestro: Ticker -> {Nombre, Categoría}
GAMING_TICKERS = {
    # --- Los "Tres Gigantes" ---
    "MSFT": {"name": "Microsoft Corporation", "category": "Consolas y Ecosistemas"},
    "SONY": {"name": "Sony Group Corporation", "category": "Consolas y Ecosistemas"},
    "NTDOY": {"name": "Nintendo Co., Ltd.", "category": "Consolas y Ecosistemas"},
    
    # --- Grandes Plataformas ---
    "AAPL": {"name": "Apple", "category": "Plataformas de Distribución"},
    "GOOGL": {"name": "Alphabet", "category": "Plataformas de Distribución"},
    
    # --- Desarrolladoras y Editoras ---
    "EA": {"name": "Electronic Arts", "category": "Desarrolladores/Publishers"},
    "TTWO": {"name": "Take-Two Interactive", "category": "Desarrolladores/Publishers"},
    "RBLX": {"name": "Roblox Corporation", "category": "Desarrolladores/Publishers"},
    "TCEHY": {"name": "Tencent Holdings", "category": "Desarrolladores/Publishers"},
    "NTES": {"name": "NetEase", "category": "Desarrolladores/Publishers"},
    "UBSFY": {"name": "Ubisoft Entertainment", "category": "Desarrolladores/Publishers"},
    "CCOEY": {"name": "Capcom Co.", "category": "Desarrolladores/Publishers"},
    "NCBDY": {"name": "Bandai Namco", "category": "Desarrolladores/Publishers"},
    "SQNNY": {"name": "Square Enix", "category": "Desarrolladores/Publishers"},
    "KONMY": {"name": "Konami Group", "category": "Desarrolladores/Publishers"},
    "SGAMY": {"name": "Sega Sammy", "category": "Desarrolladores/Publishers"},
    "OTGLY": {"name": "CD Projekt Red", "category": "Desarrolladores/Publishers"},
    
    # --- Infraestructura y Motor ---
    "NVDA": {"name": "NVIDIA Corporation", "category": "Hardware e Infraestructura"},
    "AMD": {"name": "Advanced Micro Devices", "category": "Hardware e Infraestructura"},
    "U": {"name": "Unity Software", "category": "Motores y Herramientas"},
    "APP": {"name": "AppLovin Corporation", "category": "Motores y Herramientas"},
    
    # --- Periféricos y Retail ---
    "LOGI": {"name": "Logitech International", "category": "Periféricos y Retail"},
    "CRSR": {"name": "Corsair Gaming", "category": "Periféricos y Retail"},
    "GME": {"name": "GameStop Corp.", "category": "Periféricos y Retail"},
    
    # --- Mobile y Otros ---
    "SE": {"name": "Sea Limited (Garena)", "category": "Mobile y Otros"},
    "PLTK": {"name": "Playtika Holding", "category": "Mobile y Otros"},
    
    # --- ÍNDICES DE REFERENCIA (Benchmarks) ---
    "^IXIC": {"name": "Nasdaq Composite", "category": "Índice de Mercado (Tech)"},
    "^GSPC": {"name": "S&P 500", "category": "Índice de Mercado (General)"}
}

def obtener_datos_preparados():
    print("Iniciando descarga masiva incluyendo índices de mercado...\n")
    
    tickers_list = list(GAMING_TICKERS.keys())
    
    # 1. Descarga Vectorizada
    raw_data = yf.download(
        tickers_list,
        start="1970-01-01", 
        end="2025-12-31", 
        group_by='column', 
        progress=True,
        threads=False
        )
    
    if raw_data.empty:
        print("\nFallo crítico. No se obtuvieron datos.")
        return

    print("\nProcesando categorías y calculando rendimientos...")

    # 2. Transformar los datos (Tidy Data)
    df = raw_data.stack(level=1).rename_axis(['Date', 'Ticker']).reset_index()
    
    # Extraer mapeos de nuestro diccionario anidado
    nombres_map = {ticker: info["name"] for ticker, info in GAMING_TICKERS.items()}
    categorias_map = {ticker: info["category"] for ticker, info in GAMING_TICKERS.items()}
    
    # Aplicar mapeos al DataFrame
    df['Company Name'] = df['Ticker'].map(nombres_map)
    df['Category'] = df['Ticker'].map(categorias_map)
    
    if df['Date'].dt.tz is not None:
        df['Date'] = df['Date'].dt.tz_localize(None)

    df = df.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)

    # 3. Cálculos Base
    df['Daily_Return_%'] = df.groupby('Ticker')['Close'].pct_change() * 100

    def calcular_acumulado(serie):
        if serie.dropna().empty:
            return serie
        primer_precio = serie.dropna().iloc[0]
        return ((serie / primer_precio) - 1) * 100

    df['Cumulative_Return_%'] = df.groupby('Ticker')['Close'].transform(calcular_acumulado)

    # 4. Orden final de columnas (añadimos Category)
    cols_to_keep = ['Date', 'Category', 'Company Name', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return_%', 'Cumulative_Return_%']
    cols_available = [col for col in cols_to_keep if col in df.columns]
    final_df = df[cols_available]

    # Exportar
    filename = 'data/raw/dataset_diario_videojuegos_categorizado.csv'
    final_df.to_csv(filename, index=False)
    
    print(f"\n¡Éxito! CSV guardado como '{filename}'. Listo para Streamlit.")

if __name__ == "__main__":
    obtener_datos_preparados()