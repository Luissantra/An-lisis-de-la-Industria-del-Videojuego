import pandas as pd
import os

def run_geo_etl():
    print("Iniciando proceso ETL para el mapa geográfico de desarrolladoras...")
    
    # 1. Extract
    raw_path = 'data/raw/raw_studios_geocoded.csv'

    df_raw = pd.read_csv(raw_path)

    # 2. Transform
    print("Transformando datos...")

    # Nos quedamos solo con las columnas importantes
    columns_to_keep = ['Company_Name', 'City', 'Country', 'Region', 'Latitude', 'Longitude']
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
    
    # Diccionario de mapeo: País -> Región
    region_mapping = {
        # North & Central America
        'UNITED STATES': 'North America', 'CANADA': 'North America', 'MEXICO': 'North America',
        'COSTA RICA': 'North America', 'GUATEMALA': 'North America', 'EL SALVADOR': 'North America',
        'PANAMA': 'North America', 'JAMAICA': 'North America',

        # South America
        'BRAZIL': 'South America', 'ARGENTINA': 'South America', 'CHILE': 'South America',
        'COLOMBIA': 'South America', 'PERU': 'South America', 'URUGUAY': 'South America',
        'ECUADOR': 'South America', 'PARAGUAY': 'South America', 'VENEZUELA': 'South America',

        # Europe
        'UNITED KINGDOM': 'Europe', 'ENGLAND': 'Europe', 'SCOTLAND': 'Europe', 'WALES': 'Europe', 
        'NORTHERN IRELAND': 'Europe', 'STATES OF JERSEY': 'Europe', 'GERMANY': 'Europe', 
        'SPAIN': 'Europe', 'FRANCE': 'Europe', 'RHONE-ALPES': 'Europe', 'ITALY': 'Europe', 
        'POLAND': 'Europe', 'SWEDEN': 'Europe', 'NETHERLANDS': 'Europe', 'BELGIUM': 'Europe', 
        'SWITZERLAND': 'Europe', 'FINLAND': 'Europe', 'DENMARK': 'Europe', 'NORWAY': 'Europe', 
        'IRELAND': 'Europe', 'AUSTRIA': 'Europe', 'CZECHIA': 'Europe', 'CZECH REPUBLIC': 'Europe', 
        'ROMANIA': 'Europe', 'PORTUGAL': 'Europe', 'HUNGARY': 'Europe', 'GREECE': 'Europe', 
        'SERBIA': 'Europe', 'BULGARIA': 'Europe', 'CROATIA': 'Europe', 'SLOVAKIA': 'Europe', 
        'SLOVENIA': 'Europe', 'LITHUANIA': 'Europe', 'ESTONIA': 'Europe', 'LATVIA': 'Europe', 
        'ICELAND': 'Europe', 'LUXEMBOURG': 'Europe', 'BELARUS': 'Europe', 'UKRAINE': 'Europe', 
        'RUSSIA': 'Europe', 'NORTH MACEDONIA': 'Europe', 'BOSNIA & HERZEGOVINA': 'Europe', 
        'MOLDOVA': 'Europe', 'MONTENEGRO': 'Europe', 'ALBANIA': 'Europe', 'CYPRUS': 'Europe', 
        'MALTA': 'Europe',

        # Asia (Including Middle East & Eurasia)
        'JAPAN': 'Asia', 'CHINA': 'Asia', 'SOUTH KOREA': 'Asia', 'INDIA': 'Asia', 'TAIWAN': 'Asia',
        'SINGAPORE': 'Asia', 'MALAYSIA': 'Asia', 'INDONESIA': 'Asia', 'PHILIPPINES': 'Asia',
        'VIETNAM': 'Asia', 'THAILAND': 'Asia', 'PAKISTAN': 'Asia', 'BANGLADESH': 'Asia', 
        'SRI LANKA': 'Asia', 'NEPAL': 'Asia', 'MYANMAR': 'Asia', 'BRUNEI': 'Asia', 
        'KAZAKHSTAN': 'Asia', 'UZBEKISTAN': 'Asia', 'KYRGYZSTAN': 'Asia', 'TURKEY': 'Asia', 
        'ISRAEL': 'Asia', 'UNITED ARAB EMIRATES': 'Asia', 'SAUDI ARABIA': 'Asia', 'IRAN': 'Asia', 
        'IRAQ': 'Asia', 'SYRIA': 'Asia', 'LEBANON': 'Asia', 'JORDAN': 'Asia', 'KUWAIT': 'Asia', 
        'QATAR': 'Asia', 'BAHRAIN': 'Asia', 'OMAN': 'Asia', 'PALESTINE': 'Asia', 'GEORGIA': 'Asia', 
        'ARMENIA': 'Asia', 'AZERBAIJAN': 'Asia',

        # Africa
        'SOUTH AFRICA': 'Africa', 'EGYPT': 'Africa', 'MOROCCO': 'Africa', 'NIGERIA': 'Africa',
        'KENYA': 'Africa', 'GHANA': 'Africa', 'TUNISIA': 'Africa', 'ALGERIA': 'Africa',
        'CAMEROON': 'Africa', 'ETHIOPIA': 'Africa', 'SENEGAL': 'Africa', 'ZAMBIA': 'Africa',
        'MADAGASCAR': 'Africa', 'MAURITIUS': 'Africa',

        # Oceania
        'AUSTRALIA': 'Oceania', 'NEW ZEALAND': 'Oceania',

        # Uncategorized / Special
        'REMOTE': 'Other'
    }

    # Creamos la nueva columna mapeando el país. 
    # fillna('Other') asegura que los países que no están en el diccionario no queden como NaN
    df_geo['Region'] = df_geo['Country'].map(region_mapping).fillna('Other')
    # Nos olvidamos de las que no tengan coordenadas
    df_geo = df_geo.dropna(subset=['Lat', 'Lon'])

    # Reseteamos índice
    df_geo = df_geo.reset_index(drop=True)
    df_geo.index.name = 'Geo_ID'

    print(f"Transformación completa. Total de estudios geocodificados: {len(df_geo)}")

    # 3. Load
    print("Guardando datos transformados...")

    processed_path = 'data/processed/studios_geocoded.csv'
    df_geo.to_csv(processed_path, index=True)

    print(f"¡ETL completado! Archivo guardado como '{processed_path}'.")


if __name__ == "__main__":
    run_geo_etl()
    