import requests
import time
import sys
from pathlib import Path
# Agregamos el directorio raíz al path para que Python encuentre el módulo 'config'
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import config

# Utilizamos los nombres de archivo exactos alojados en Wikimedia Commons
WIKI_FILES = {
    "Microsoft Gaming (Xbox, ZeniMax, Activision Blizzard)": "Xbox_Logo.svg",
    "Sony Interactive Entertainment (PlayStation Studios)": "PlayStation_logo.svg",
    "Tencent": "Tencent_Logo.svg",
    "Nintendo": "Nintendo.svg",
    "Electronic Arts (EA)": "Electronic-Arts-Logo.svg",
    "Take-Two Interactive": "Take-Two_Interactive_Logo.svg",
    "Ubisoft": "Ubisoft_logo.svg",
    "Sega Sammy": "Sega_logo.svg",
    "Epic Games": "Epic_Games_logo.svg",
    "Warner Bros. Games": "Warner_Bros._Discovery.svg",
    "Krafton": "Krafton_Logo.svg",
    "Independent & Other Publishers": "Video_game_controller_icon_designed_by_Maico_Amorim.svg"
}

def descargar_logos():
    config.init_environment()
    print("Iniciando descarga de logos corporativos de forma segura...")
    
    # User-Agent descriptivo (obligatorio para la API de Wikimedia)
    headers = {
        'User-Agent': 'VideoGameIndustryDashboard/1.0 (Datos educativos; info@tudominio.com) Python-requests/2.32'
    }
    
    for empresa, filename in WIKI_FILES.items():
        # Limpiamos el nombre para el archivo local
        safe_name = "".join([c if c.isalnum() or c in " &()_-" else "_" for c in empresa])
        filepath = config.LOGOS_DIR / f"{safe_name}.png"
        
        if filepath.exists():
            print(f"✔️ Ya existe: {safe_name}.png")
            continue
            
        # Usamos el endpoint especial de Wikipedia que genera y redirecciona automáticamente la imagen PNG a 500px
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=500"
        
        try:
            print(f"⏳ Descargando: {empresa}...")
            response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
            response.raise_for_status() # Verifica si hay errores HTTP
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"   ✅ Guardado como: {safe_name}.png")
            
            # Respetamos el servidor de Wikimedia esperando .5 segundos entre cada descarga
            time.sleep(.5) 
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error al descargar {empresa}: {e}")

if __name__ == "__main__":
    descargar_logos()