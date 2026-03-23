import subprocess
import sys
import argparse 
from pathlib import Path

# Calcula dinámicamente la ruta al directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent

def run_script(script):
    """
    Ejecuta un script dada su ruta
    """

    script_path = BASE_DIR / script
    print(f"Ejecutando {script_path}...")

    result = subprocess.run([sys.executable, str(script_path)])

    if result.returncode != 0:
        print(f"Error al ejecutar {script_path}. Código de salida: {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"{script_path} ejecutado exitosamente.")

def run_pipeline():
  """
  Ejecuta toda la pipeline de ETL y construcción de la base de datos.
  """

  # --- Configuración de argumentos ---
  parser = argparse.ArgumentParser(description="(Orquestador del pipeline) Ejecuta la pipeline de ETL y construcción de la base de datos.")

  # Añadimos flags para saltar pasos específicos
  parser.add_argument("--skip-extract", action="store_true", help="Saltar la fase de extracción de datos.")
  parser.add_argument("--skip-transform", action="store_true", help="Saltar la fase de transformación de datos.")
  parser.add_argument("--skip-load", action="store_true", help="Saltar la fase de carga a la base de datos.")

  args = parser.parse_args()

  # Extracción de datos
  if not args.skip_extract:
      run_script("scripts/get_market_data.py")
      #run_script("scripts/get_gameDevMap.py")
  else:
      print("Saltando fase de extracción de datos...")

  # Transformación (ETL)
  if not args.skip_transform:
      run_script("scripts/etl_gameDevMap.py")
  else:
      print("Saltando fase de transformación de datos...")
  
  # Carga a la base de datos
  if not args.skip_load:
      run_script("scripts/build_db.py") 
  else:
      print("Saltando fase de carga a la base de datos...")

  print("Pipeline completado!")


if __name__ == "__main__":
    run_pipeline()





