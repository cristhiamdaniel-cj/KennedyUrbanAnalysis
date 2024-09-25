import os
import pandas as pd
import logging
from collections import Counter
import matplotlib.pyplot as plt

# Obtener el directorio actual donde está ubicado el script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definir rutas de archivos y directorios de manera dinámica
log_dir = os.path.join(BASE_DIR, '../logs')
output_dir = os.path.join(BASE_DIR, '../output')  # Crear el directorio 'output'
log_file = os.path.join(log_dir, 'app.log')
data_file = os.path.join(BASE_DIR, '../data/banco_iniciativas.xlsx')

# Crear los directorios 'logs' y 'output' si no existen
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Configuración básica del logging para escribir tanto en archivo como en la terminal
logging.basicConfig(
    level=logging.INFO,  # Nivel de los logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Guarda logs en archivo
        logging.StreamHandler()  # Muestra logs en la terminal
    ]
)


def check_file_exists(file_path):
    """Verifica si el archivo existe."""
    if os.path.exists(file_path):
        logging.info(f"Archivo encontrado: {file_path}")
        return True
    else:
        logging.error(f"Archivo no encontrado: {file_path}")
        return False


def read_excel_file(file_path, sheet_name):
    """Lee el archivo Excel y retorna un DataFrame de la hoja especificada."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info(f"Hoja '{sheet_name}' leída correctamente.")
        return df
    except FileNotFoundError:
        logging.error("El archivo no fue encontrado.")
        raise
    except ValueError as e:
        logging.error(f"Error al leer la hoja de cálculo: {e}")
        raise


def validate_column_exists(df, column_name):
    """Valida si una columna específica existe en el DataFrame."""
    if column_name in df.columns:
        logging.info(f"Columna '{column_name}' encontrada en el archivo.")
        print(df[column_name].head())  # Mostrar los primeros valores de la columna
        return True
    else:
        logging.error(f"Columna '{column_name}' no encontrada en el archivo.")
        raise ValueError(f"La columna '{column_name}' no existe en el archivo.")


def plot_top_recurrent_values(df, column_name, top_n=10):
    """Genera un gráfico de barras de los valores más recurrentes de una columna."""
    try:
        # Filtramos valores nulos
        df_clean = df[df[column_name].notna()]

        # Contamos los valores más recurrentes
        top_values = Counter(df_clean[column_name]).most_common(top_n)
        labels, values = zip(*top_values) if top_values else ([], [])

        if labels and values:
            # Convertir etiquetas a cadenas para mejor legibilidad
            labels = [str(label) for label in labels]

            # Generamos el gráfico de barras
            plt.bar(labels, values)
            plt.xticks(rotation=90)  # Rotamos las etiquetas para mayor legibilidad
            plt.title(f'Top {top_n} valores más recurrentes en la columna {column_name}')
            plt.ylabel('Frecuencia')
            plt.xlabel(column_name)

            # Añadir los valores de frecuencia sobre las barras
            for i, v in enumerate(values):
                plt.text(i, v + 0.5, str(v), ha='center', va='bottom')

            # Guardar el gráfico como imagen
            output_image_path = os.path.join(output_dir, 'top_civ_values.png')
            plt.tight_layout()
            plt.savefig(output_image_path)
            logging.info(f"Gráfico guardado en '{output_image_path}'")
        else:
            logging.warning(f"No hay suficientes datos válidos en la columna '{column_name}' para generar el gráfico.")
            print(f"No hay suficientes datos válidos en la columna '{column_name}' para generar el gráfico.")

    except Exception as e:
        logging.error(f"Error al generar el gráfico: {e}")
        raise


def save_top_recurrent_values(df, column_name, top_n=30):
    """Guarda los valores más recurrentes de una columna en un archivo de texto."""
    try:
        # Filtramos valores nulos
        df_clean = df[df[column_name].notna()]

        # Contamos los valores más recurrentes
        top_values = Counter(df_clean[column_name]).most_common(top_n)

        if top_values:
            output_txt_path = os.path.join(output_dir, 'top_30_civ_values.txt')

            # Guardar los valores en un archivo de texto
            with open(output_txt_path, 'w') as file:
                file.write(f"Top {top_n} valores más recurrentes en la columna {column_name}:\n\n")
                for label, count in top_values:
                    file.write(f"{label}: {count}\n")

            logging.info(f"Valores guardados en '{output_txt_path}'")
        else:
            logging.warning(f"No hay suficientes datos válidos en la columna '{column_name}' para guardar los valores.")
            print(f"No hay suficientes datos válidos en la columna '{column_name}' para guardar los valores.")

    except Exception as e:
        logging.error(f"Error al guardar los valores: {e}")
        raise


def main():
    # Definir el nombre de la hoja
    sheet_name = 'BANCO DE INICIATIVAS VIAS '  # Espacio incluido según el Excel
    column_name = 'CIV'

    # Validar si el archivo existe
    if not check_file_exists(data_file):
        print("El archivo no se encontró. Verifica la ruta.")
        return

    # Leer el archivo Excel
    try:
        df = read_excel_file(data_file, sheet_name)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    # Validar si la columna existe
    try:
        if validate_column_exists(df, column_name):
            # Guardar los 30 valores más recurrentes en un archivo de texto
            save_top_recurrent_values(df, column_name)

            # Generar gráfico de los 10 valores más recurrentes en la columna 'CIV'
            plot_top_recurrent_values(df, column_name)
    except ValueError as e:
        print(f"Error en la validación de la columna: {e}")
        return


if __name__ == "__main__":
    main()
