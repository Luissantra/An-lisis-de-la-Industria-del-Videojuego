import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import os
import re

def get_wikipedia_info(company_name):
    """
    Busca la compañía en Wikipedia, extrae datos de su Infobox y los estandariza.
    """
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(company_name + ' video game developer')}&utf8=&format=json"
    headers = {'User-Agent': 'GameDevEnricherBot/1.0'}
    
    data = {"Founded": "N/A", "Employees": "N/A", "Most_Relevant_Game": "N/A"}
    
    try:
        search_res = requests.get(search_url, headers=headers, timeout=10).json()
        if not search_res['query']['search']:
            return data
        
        page_title = search_res['query']['search'][0]['title']
        page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title)}"
        
        page_res = requests.get(page_url, headers=headers, timeout=10)
        soup = BeautifulSoup(page_res.text, 'html.parser')
        
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return data

        for row in infobox.find_all('tr'):
            th = row.find('th')
            td = row.find('td')
            
            if th and td:
                header_text = th.get_text(strip=True).lower()
                # Separamos con ' | ' temporalmente para poder cortar el texto luego
                value_text = td.get_text(separator=' | ', strip=True) 
                # Limpiar referencias de Wikipedia como [1], [2], etc.
                value_text = re.sub(r'\[\d+\]', '', value_text)

                # --- ESTANDARIZACIÓN ---
                
                # 1. Fundación: Extraer solo el año (4 dígitos que empiecen por 19 o 20)
                if 'founded' in header_text:
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', value_text)
                    if year_match:
                        data["Founded"] = year_match.group(1)
                
                # 2. Empleados: Extraer solo números y quitar comas (Ej: "1,200+" -> "1200")
                elif 'employees' in header_text or 'number of employees' in header_text:
                    emp_match = re.search(r'([\d,]+)', value_text)
                    if emp_match:
                        # Nos quedamos con el número y le quitamos las comas
                        clean_number = emp_match.group(1).replace(',', '')
                        data["Employees"] = clean_number
                
                # 3. Juego Relevante: Quedarnos solo con el primer elemento de la lista
                elif 'notable game' in header_text or 'products' in header_text or 'notable release' in header_text:
                    # Cortamos por nuestro separador o por comas normales y cogemos el primero
                    first_game = value_text.split(' | ')[0].split(',')[0].strip()
                    data["Most_Relevant_Game"] = first_game

        return data

    except Exception as e:
        print(f"  [!] Error buscando {company_name}: {e}")
        return data


def run_enrichment():
    # Usamos el raw geocodificado generado por tu primer script
    input_csv = 'data/raw/raw_studios_geocoded.csv' 
    output_csv = 'data/processed/notable_studios_enriched.csv'

    if not os.path.exists(input_csv):
        # Fallback por si el archivo se llama diferente en tu PC
        input_csv = 'data/raw/raw_studios.csv'
        if not os.path.exists(input_csv):
            print("Error: No se encuentra el archivo CSV base.")
            return

    print(f"--- Iniciando enriquecimiento de datos para ESTUDIOS NOTABLES ---")
    df = pd.read_csv(input_csv, dtype=str)
    
    # 1. Filtramos SOLO los estudios de tu lista
    df_notables = df[df['Location'] == 'Custom Notable List'].copy()
    
    if df_notables.empty:
        print("No se encontraron estudios etiquetados como 'Custom Notable List' en el CSV.")
        return
        
    total = len(df_notables)
    print(f"Se van a procesar {total} estudios...")
    
    founded_list = []
    employees_list = []
    games_list = []

    for i, row in df_notables.iterrows():
        company = row['Company_Name']
        print(f"[{i+1}/{total}] Extrayendo y limpiando datos de: {company}...")
        
        info = get_wikipedia_info(company)
        
        founded_list.append(info['Founded'])
        employees_list.append(info['Employees'])
        games_list.append(info['Most_Relevant_Game'])
        
        # Pausa de cortesía para la API
        time.sleep(1) 

    # 2. Creamos el DataFrame final SOLO con las 4 columnas que pediste
    final_df = pd.DataFrame({
        'Company_Name': df_notables['Company_Name'].tolist(),
        'Founded': founded_list,
        'Employees': employees_list,
        'Most_Relevant_Game': games_list
    })

    # Aseguramos que la carpeta processed exista
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Guardamos el resultado
    final_df.to_csv(output_csv, index=False)
    print(f"\n¡Enriquecimiento completado! Archivo guardado como '{output_csv}'.")

if __name__ == "__main__":
    run_enrichment()