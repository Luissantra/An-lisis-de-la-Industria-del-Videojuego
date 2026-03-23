import pandas as pd
from sqlalchemy import create_engine
import os

# Importación limpia sin hacks
import config

def build_database():
    """
    Construye la base de datos a partir de los dataset CSVs procesados.
    """
    print("Construyendo la base de datos...")

    # Crear una conexión a la base de datos SQLite usando SQLAlchemy
    engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
    print("Conexión con la base de datos establecida.")

    # --- Tabla GameDevMap (Estudios) ---
    if os.path.exists(config.GAMEDEVMAP_CSV):
        print(f" - Cargando datos desde {config.GAMEDEVMAP_CSV}...")
        df_geo = pd.read_csv(config.GAMEDEVMAP_CSV)
        
        # Escribimos el DataFrame a la base de datos
        df_geo.to_sql('studio_locations', con=engine, if_exists='replace', index=False)
        print(" [OK] Tabla 'studio_locations' creada y datos insertados.")
    else:
        print(f" [Advertencia] No se encontró {config.GAMEDEVMAP_CSV}. Ejecuta el pipeline de ETL primero.")
        
    # --- Tabla Stock_Prices (Bolsa) ---
    if os.path.exists(config.MARKETDATA_CSV):
        print(f" - Cargando datos desde {config.MARKETDATA_CSV}...")
        df_market = pd.read_csv(config.MARKETDATA_CSV)
        
        df_market.to_sql('stock_prices', con=engine, if_exists='replace', index=False)
        print(" [OK] Tabla 'stock_prices' creada y datos insertados.")
    else:
        print(f" [Advertencia] No se encontró {config.MARKETDATA_CSV}. Ejecuta la extracción de mercado primero.")

if __name__ == "__main__":
    build_database()