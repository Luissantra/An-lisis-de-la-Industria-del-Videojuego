import pandas as pd
import os
from pathlib import Path
import pycountry_convert as pc
import sys
# Añadir la raíz al path para poder importar config
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def obtain_region(country_name):
    """
    Función auxiliar para mapear un país a su región geográfica.
    """
    if pd.isna(country_name) or country_name.upper() == "REMOTE":
        return "Other"
    
    # Casos especiales que a la librería le cuesta entender
    correcciones = {
        'UNITED KINGDOM': 'United Kingdom',
        'ENGLAND': 'United Kingdom',
        'SCOTLAND': 'United Kingdom',
        'WALES': 'United Kingdom',
        'NORTHERN IRELAND': 'United Kingdom',
        'SOUTH KOREA': 'South Korea',
        'RUSSIA': 'Russian Federation',
        'CZECHIA': 'Czech Republic'
    }
    
    nombre_limpio = correcciones.get(country_name.upper(), country_name.title())

    try:
        # 1. País -> Código de 2 letras (Ej: Spain -> ES)
        country_code = pc.country_name_to_country_alpha2(nombre_limpio)
        # 2. Código País -> Código Continente (Ej: ES -> EU)
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        # 3. Código Continente -> Nombre (Ej: EU -> Europe)
        return pc.convert_continent_code_to_continent_name(continent_code)
    except Exception:
        # Si la librería falla con un país rarísimo, lo manda a Other
        return 'Other'


def run_geo_etl():
    print("Iniciando proceso ETL para el mapa geográfico de desarrolladoras...")
    
    # 1. Extract
    df_raw = pd.read_csv(config.RAW_GAMEDEVMAP_CSV)


    # 2. Transform
    print("Transformando datos...")

    # Nos quedamos solo con las columnas importantes
    columns_to_keep = ['Company_Name', 'City', 'Country', 'Latitude', 'Longitude']
    df_geo = df_raw[columns_to_keep].copy()

    # Renombramos columnas para mayor claridad
    df_geo.rename(columns={
        'Company_Name': 'Studio Name',
        'Latitude': 'Lat',
        'Longitude': 'Lon'
    }, inplace=True)

    # Estandarizamos nombres de países
    df_geo["City"] = df_geo["City"].fillna("Unknown City").str.title()
    df_geo["Country"] = df_geo["Country"].fillna("Unknown Country").str.upper()
    
    # Mapeamos cada país a su región usando la función auxiliar
    df_geo['Region'] = df_geo['Country'].apply(obtain_region)

    # Nos olvidamos de las que no tengan coordenadas
    df_geo = df_geo.dropna(subset=['Lat', 'Lon'])

    # Reseteamos índice
    df_geo = df_geo.reset_index(drop=True)
    df_geo.index.name = 'Geo_ID'

    print(f"Transformación completa. Total de estudios geocodificados: {len(df_geo)}")

    # 3. Load
    print("Guardando datos transformados...")

    processed_path = config.GAMEDEVMAP_CSV
    df_geo.to_csv(processed_path, index=True)

    print(f"¡ETL completado! Archivo guardado como '{processed_path}'.")


if __name__ == "__main__":
    run_geo_etl()
    