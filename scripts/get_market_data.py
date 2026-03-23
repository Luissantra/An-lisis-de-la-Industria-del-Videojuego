import yfinance as yf
import warnings
import config
import json
import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# Suprimir advertencias para mantener la consola limpia
warnings.simplefilter(action='ignore', category=FutureWarning)

def cargar_tickers():
    """
    Carga el diccionario de tickers del archivo JSON de configuración.
    """
    ruta_json = config.TICKERS_JSON # Diccionario maestro: Ticker -> {Nombre, Categoría}
    with open(ruta_json, 'r') as f:
        return json.load(f)

def obtener_ultima_fecha():
    """
    Consulta la BBDD para ver cuál es la última fecha descargada
    """
    if not os.path.exists(config.DATABASE_PATH):
        return "1970-01-01"  # No hay datos previos -> descargar todo el histórico
    
    try:
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            query = "SELECT MAX(Date) as last_date FROM stock_prices"
            df_date = pd.read_sql_query(query, conn)
            ultima_fecha_str = df_date.iloc[0]['last_date']

            if pd.isna(ultima_fecha_str):
                return "1970-01-01"  # No hay datos en la tabla -> descargar todo el histórico
            
            # Sumamos un día para evitar solapamientos
            ultima_fecha = datetime.strptime(ultima_fecha_str.split(' ')[0], "%Y-%m-%d") + timedelta(days=1)
            return ultima_fecha.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error al obtener la última fecha de la base de datos: {e}")
        return "1970-01-01"  # En caso de error, descargar todo el histórico
        



def obtener_datos_preparados():
    print("Iniciando descarga masiva incluyendo índices de mercado...\n")
    
    GAMING_TICKERS = cargar_tickers()
    tickers_list = list(GAMING_TICKERS.keys())

    fecha_inicio = obtener_ultima_fecha()
    fecha_fin = datetime.now().strftime("%Y-%m-%d")

    if fecha_inicio >= fecha_fin:
        print("Los datos ya están actualizados hasta la fecha actual. No se requiere descarga.")
        return
    
    print(f"Descargando datos desde {fecha_inicio} hasta {fecha_fin} para los siguientes tickers:")

    # 1. Descarga Vectorizada
    raw_data = yf.download(
        tickers_list,
        start=fecha_inicio, 
        end=fecha_fin, 
        group_by='column', 
        progress=True,
        threads=False
        )
    
    if raw_data.empty:
        print("\nFallo crítico. No se obtuvieron datos.")
        return

    print("\nProcesando categorías y calculando rendimientos...")

    # 2. Transformar los datos
    df_nuevos = raw_data.stack(level=1).rename_axis(['Date', 'Ticker']).reset_index()
    
    nombres_map = {t: info["name"] for t, info in GAMING_TICKERS.items()}
    categorias_map = {t: info["category"] for t, info in GAMING_TICKERS.items()}
    
    df_nuevos['Company Name'] = df_nuevos['Ticker'].map(nombres_map)
    df_nuevos['Category'] = df_nuevos['Ticker'].map(categorias_map)
    
    if df_nuevos['Date'].dt.tz is not None:
        df_nuevos['Date'] = df_nuevos['Date'].dt.tz_localize(None)

    df_nuevos = df_nuevos.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)

    # 3. Concatenar con los datos históricos existentes (si los hay)
    filename = config.MARKETDATA_CSV
    
    if os.path.exists(filename):
        df_historico = pd.read_csv(filename)
        df_historico['Date'] = pd.to_datetime(df_historico['Date'])
        df_completo = pd.concat([df_historico, df_nuevos], ignore_index=True)
    else:
        df_completo = df_nuevos.copy()

    # 4. Recalcular métricas sobre el dataset completo
    df_completo = df_completo.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)
    df_completo['Daily_Return_%'] = df_completo.groupby('Ticker')['Close'].pct_change() * 100

    def calcular_acumulado(serie):
        if serie.dropna().empty:
            return serie
        primer_precio = serie.dropna().iloc[0]
        return ((serie / primer_precio) - 1) * 100

    df_completo['Cumulative_Return_%'] = df_completo.groupby('Ticker')['Close'].transform(calcular_acumulado)

    # 5. Guardar CSV actualizado
    cols_to_keep = ['Date', 'Category', 'Company Name', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return_%', 'Cumulative_Return_%']
    df_completo = df_completo[cols_to_keep]
    
    df_completo.to_csv(filename, index=False)
    print(f"\n¡Éxito! Datos actualizados guardados en '{filename}'.")

if __name__ == "__main__":
    obtener_datos_preparados()