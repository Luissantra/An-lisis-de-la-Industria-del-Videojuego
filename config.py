from pathlib import Path

# Calcula dinámicamente la ruta al directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Directorios de datos
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"

# Nos aseguramos de que los directorios existan
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Rutas a archivos específicos
RAW_GAMEDEVMAP_CSV = RAW_DATA_DIR / "raw_studios_geocoded.csv"
GAMEDEVMAP_CSV = PROCESSED_DATA_DIR / "studios_geocoded.csv"

RAW_MARKETDATA_CSV = RAW_DATA_DIR / "raw_market_data.csv"
MARKETDATA_CSV = PROCESSED_DATA_DIR / "market_data.csv"

DATABASE_PATH = DATABASE_DIR / "videogames.db"


