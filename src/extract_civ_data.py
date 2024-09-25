import requests
import json
import os
import logging

# Definir la ruta del directorio de salida (output)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, '../output')
log_dir = os.path.join(BASE_DIR, '../logs')

# Ruta del archivo con los 30 CIV más recurrentes
txt_file_path = os.path.join(output_dir, 'top_30_civ_values.txt')

# Crear los directorios si no existen
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Configuración básica del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'extract_civ_data.log')),
        logging.StreamHandler()
    ]
)


def read_civ_file(file_path):
    """Lee el archivo de texto con los 30 valores CIV más recurrentes y filtra solo las líneas útiles."""
    civ_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file.readlines():
                # Ignorar las líneas que no tienen el formato <CIV>: <valor>
                if line.strip() and ':' in line and line.split(':')[0].isdigit():
                    civ = line.split(':')[0].strip()  # Extraer solo el CIV
                    civ_list.append(civ)
        logging.info(f"Leídos {len(civ_list)} CIVs desde el archivo {file_path}")
    except Exception as e:
        logging.error(f"Error al leer el archivo {file_path}: {e}")
        raise
    return civ_list


def fetch_civ_data(civ):
    """Realiza una solicitud a la API de ArcGIS para obtener la información del CIV."""
    url = "https://webidu.idu.gov.co/servergis1/rest/services/Inventario/InventarioIDU/MapServer/0/query"
    params = {
        'f': 'json',
        'where': f'CIV={civ}',  # Filtra por el CIV que queremos consultar
        'outFields': '*',  # Extrae todos los campos
        'returnGeometry': 'true'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Datos obtenidos para CIV: {civ}")
            return data
        else:
            logging.error(f"Error al obtener datos para CIV {civ}: Status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error al conectar con la API de ArcGIS para CIV {civ}: {e}")
        return None


def save_civ_data_to_json(civ_data, output_path):
    """Guarda los datos del CIV obtenidos en un archivo JSON."""
    try:
        with open(output_path, 'w') as json_file:
            json.dump(civ_data, json_file, indent=4)
        logging.info(f"Datos guardados en {output_path}")
    except Exception as e:
        logging.error(f"Error al guardar los datos en {output_path}: {e}")
        raise


def main():
    # Leer el archivo con los 30 CIV más recurrentes
    civ_list = read_civ_file(txt_file_path)

    for civ in civ_list:
        # Obtener los datos de la API para cada CIV
        civ_data = fetch_civ_data(civ)

        if civ_data:
            # Guardar los datos en un archivo JSON
            json_output_path = os.path.join(output_dir, f'civ_{civ}.json')
            save_civ_data_to_json(civ_data, json_output_path)


if __name__ == "__main__":
    main()
