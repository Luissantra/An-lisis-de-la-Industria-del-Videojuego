import requests
import os
import sys
from pathlib import Path
import time
import sqlite3
import argparse

# Agregamos el directorio raíz al path para que Python encuentre el módulo 'config'
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import config

def run_games_etl(force=False):
    # Leer clave API de entorno
    rawg_key = os.environ.get("RAWG_API_KEY")
    if not rawg_key:
        print("⚠️ ERROR: No se encontró la variable de entorno RAWG_API_KEY.")
        print("Configúrala en tu terminal ejecutando: export RAWG_API_KEY='tu_clave_aqui'")
        return

    print("🎮 Iniciando extracción de datos de juegos desde RAWG API hacia SQLite...")

    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    if force:
        cursor.execute("SELECT id, name FROM games_metadata")
        print("⚠️ Modo forzado: Se volverán a descargar los datos de todos los juegos.")
    else:
        # Seleccionamos solo los juegos que no hemos buscado en la API aún 
        # (name_api es NULL o está vacío)
        cursor.execute("SELECT id, name FROM games_metadata WHERE name_api IS NULL OR name_api = ''")

    juegos_a_procesar = cursor.fetchall()

    if not juegos_a_procesar:
        print("✅ Todos los juegos en la base de datos ya tienen sus metadatos. No hay nada nuevo que descargar.")
        conn.close()
        return

    print(f"📊 Se han encontrado {len(juegos_a_procesar)} juegos pendientes de procesar.")

    nuevos_juegos = 0
    for game_id, game_name in juegos_a_procesar:
        if not game_name or game_name in ["", "No registrado", "N/A", "Desconocido"]:
            continue

        print(f"🔍 Buscando datos para: {game_name}...")
        url = f"https://api.rawg.io/api/games?key={rawg_key}&search={requests.utils.quote(game_name)}&page_size=1"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    name_api = result.get("name", "")
                    released = result.get("released", "")
                    metacritic = result.get("metacritic")
                    genres_list = [g["name"] for g in result.get("genres", [])]
                    genres = ", ".join(genres_list) if genres_list else "Desconocido"

                    cursor.execute("""
                        UPDATE games_metadata 
                        SET name_api = ?, released = ?, metacritic = ?, genres = ?
                        WHERE id = ?
                    """, (name_api, released, metacritic, genres, game_id))
                    print(f"   ✅ Encontrado: {name_api} (Metacritic: {metacritic})")
                    nuevos_juegos += 1
                else:
                    cursor.execute("""
                        UPDATE games_metadata 
                        SET name_api = ?, genres = ?
                        WHERE id = ?
                    """, ("No encontrado", "Desconocido", game_id))
                    print(f"   ⚠️ No encontrado en la API.")
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
            
            conn.commit()
            time.sleep(0.5) # Respetar rate limits de la API
        except Exception as e:
            print(f"   ❌ Excepción: {e}")

    conn.close()
    print(f"\n✅ Proceso completado. Se actualizaron {nuevos_juegos} juegos en SQLite.")
    print("Siguiente paso sugerido: Fase 3 (Refactorizar view_corporate.py para que lea de SQLite y eliminar JSONs).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae metadatos de juegos desde RAWG API a SQLite.")
    parser.add_argument("--force", action="store_true", help="Fuerza la descarga de todos los juegos, ignorando los ya guardados.")
    args = parser.parse_args()
    
    run_games_etl(force=args.force)