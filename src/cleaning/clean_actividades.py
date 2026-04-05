import pandas as pd
import logging
from cleaning.text_utils import normalize_text, clean_text, apply_mapping
from mappings.actividades import ACTIVIDADES_MAPPING

# Iniciar el logger
logger = logging.getLogger(__name__)

def clean_actividades(df: pd.DataFrame)-> pd.DataFrame:
    logger.info("Iniciando limpieza de la columna 'actividades'...")

    # Normalizar texto
    df['actividades_norm'] = normalize_text(df['actividades'])
    df['actividades_norm'] = clean_text(df['actividades_norm'])

    # Aplicar el diccionario
    df['actividades'] = apply_mapping(df['actividades_norm'], ACTIVIDADES_MAPPING, 'actividades')

    # Eliminar columna temporal
    df = df.drop(columns=['actividades_norm'])

    logger.info("Limpieza de 'actividades' finalizada exitosamente.")
    return df
