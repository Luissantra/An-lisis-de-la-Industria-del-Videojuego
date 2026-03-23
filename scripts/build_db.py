import pandas as pd
from sqlalchemy import create_engine
import os

def build_database():
    """
    Construye la base de datos a partir de los dataset CSVs.
    """
    print("Construyendo la base de datos...")

    # Definimos nuestras rutas a los distintos archivos procesados
    geo_csv_path = "data/processed/studios_geocoded.csv"

    # Localización de la base de datos
    db_path = "data/database/videogames.db"

    # Cargar los datasets procesados
    print(f" - Cargando datos desde {geo_csv_path}...")
    df_geo = pd.read_csv(geo_csv_path)

    # Crear una conexión a la base de datos SQLite
    engine = create_engine(f'sqlite:///{db_path}')

    print("Conexión con la base de datos establecida.")

    # Carga de datos a la base de datos

    print("Creando la Tabla studio_locations...")

    # Escribimos el DataFrame a la base de datos, reemplazando la tabla si ya existe
    df_geo.to_sql('studio_locations', con=engine, if_exists='replace', index=False)

    print("Tabla studio_locations creada y datos insertados.")



if __name__ == "__main__":
    build_database()