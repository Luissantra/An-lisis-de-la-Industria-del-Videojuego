import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import sys

# Añadir la raíz al path para poder importar config
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# Calcula dinámicamente la ruta al directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

def build_database():
    """
    Construye la base de datos a partir de los dataset CSVs.
    """
    print("Construyendo la base de datos...")

    # Crear una conexión a la base de datos SQLite
    engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
    print("Conexión con la base de datos establecida.")


    # --- Tabla GameDevMap ---
    if config.GAMEDEVMAP_CSV.exists():
        print(f" - Cargando datos desde {config.GAMEDEVMAP_CSV}...")
        df_geo = pd.read_csv(config.GAMEDEVMAP_CSV)
        # Escribimos el DataFrame a la base de datos, reemplazando la tabla si ya existe
        df_geo.to_sql('studio_locations', con=engine, if_exists='replace', index=False)
        print("Tabla studio_locations creada y datos insertados.")
    else:
        print(f" - Advertencia: No se encontró el archivo {config.GAMEDEVMAP_CSV}. Saltando la creación de la tabla studio_locations.")
        
    # --- Tabla Stock_Prices ---
    if config.MARKETDATA_CSV.exists():
        print(f" - Cargando datos desde {config.MARKETDATA_CSV}...")
        df_market = pd.read_csv(config.MARKETDATA_CSV)
        df_market.to_sql('stock_prices', con=engine, if_exists='replace', index=False)
        print("Tabla stock_prices creada y datos insertados.")
    else:
        print(f" - Advertencia: No se encontró el archivo {config.MARKETDATA_CSV}. Saltando la creación de la tabla stock_prices.")
   
    


    



if __name__ == "__main__":
    build_database()