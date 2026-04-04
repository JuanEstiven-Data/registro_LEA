import pandas as pd
import logging
from cleaning.text_utils import normalize_text, clean_text, apply_mapping
from mappings.carrera import CARRERA_MAPPING

# Instanciamos el logger
logger = logging.getLogger(__name__)

def clean_carrera(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline de limpieza específico para la columna 'carrera'.
    Normaliza el texto, filtra roles/correos y aplica el diccionario de homologación.
    """
    logger.info("Iniciando limpieza de la columna 'carrera'...")

    # Normalización y Limpieza base (Usamos tus herramientas importadas)
    df['carrera_norm'] = normalize_text(df['carrera'])
    df['carrera_norm'] = clean_text(df['carrera_norm'])

    # Exclusión de Emails
    mask_email = df['carrera_norm'].str.contains(r'@', na=False)
    df.loc[mask_email, 'carrera_norm'] = 'no aplica'

    # Exclusión de Roles
    roles = ['egresado', 'profesor', 'docente', 'administrativo']
    mask_roles = df['carrera_norm'].str.contains('|'.join(roles), na=False)
    df.loc[mask_roles, 'carrera_norm'] = 'no aplica'

    # Aplicación del Mapeo
    df['carrera'] = apply_mapping(df['carrera_norm'], CARRERA_MAPPING, 'carrera')

    # Formato Estético Final para el Dashboard
    df['carrera'] = df['carrera'].str.title()
    mask_na = df['carrera'].str.lower() == 'no aplica'
    df.loc[mask_na, 'carrera'] = 'NO APLICA'

    # Eliminar 'carrera_norm' para mantener el DataFrame ligero
    df = df.drop(columns=['carrera_norm'])

    logger.info("Limpieza de 'carrera' finalizada exitosamente.")
    
    return df