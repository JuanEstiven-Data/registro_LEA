import os
import glob
import pandas as pd
import re
import logging

# Iniciar el logger
logger = logging.getLogger(__name__)

# --------------------
# Función para Ingesta de Múltiples Excels
# --------------------
def load_excels_from_folder(path: str)-> pd.DataFrame:
    """
    Escanea un directorio en busca de archivos .xlsx, extrae el año del nombre 
    del archivo, los concatena en un único DataFrame y normaliza los encabezados.
    """
    excel_files = glob.glob(os.path.join(path, "*.xlsx"))
    
    if not excel_files:
        logging.warning("No se encontraron archivos .xlsx para procesar")
        return pd.DataFrame()
    dfs = []

    # Busca exactamente 4 dígitos que representen un año (ej. 2024, 2025)
    year_pattern = re.compile(r'(20\d{2})')

    for file in excel_files:
        file_name = os.path.basename(file)

        # Extraer año
        match = year_pattern.search(file_name)
        if match:
            year = int(match.group(1))
        else:
            logging.warning(f"⚠️ Advertencia: '{file_name}' no contiene un año válido. Usando 0.")
            year = 0
        
        try:
            # df temporal para abrir los archivos .xslx
            temp_df = pd.read_excel(file)
            # Creación de la columna año
            temp_df['año'] = year
            # Agregar el df a la lista "dfs"
            dfs.append(temp_df)
            logging.info(f"Cargado exitosamente: {file_name}")
        except Exception as e:
            logging.error(f"Error leyendo {file_name}: {e}")
 
    if not dfs:
        return pd.DataFrame()
    
    # pd.concat(): Une (apila) todos los DataFrames de la lista.
    # ignore_index=True: Reconstruye el índica de 0 a N para evitar duplicados.
    combined_df = pd.concat(dfs, ignore_index=True)

    # --------------------
    # Normalización de Headers
    # --------------------
    # Estandarización base (minúsculas y espacios por guiones bajos)
    combined_df.columns = (
        combined_df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', '_', regex=True)
        .str.replace(r'\(|\)', '', regex=True) 
    )

    # Renombrado específico (Solo cambia las coincidencias)
    # Las columnas que no estén aquí (ej. 'semestre', 'profesor', etc.) se mantienen intactas.
    diccionario_mapeo = {
    "fecha": "mes",
    "nombres_y_apellidos": "nombre_completo",
    "actividad_simulador,_taller,_uso_de_equipos,_etc.": "actividades",
    "correo_institucional": "email",
    "profesor_encargado_si_aplica": "profesor_encargado",
    "monitor_encargado_si_aplica": "monitor_encargado"
    }
    combined_df = combined_df.rename(columns=diccionario_mapeo)
    combined_df = combined_df.drop(columns=['no.'])

    return combined_df