import pandas as pd
import logging
from cleaning.text_utils import normalize_text, apply_mapping
from mappings.staff import PROFESOR_MAPPING, MONITOR_MAPPING

# Activar el logger
logger = logging.getLogger(__name__)

def clean_staff(df: pd.DataFrame)->pd.DataFrame:
    """
    Estandariza los nombres de profesores y monitores antes de la anonimización
    para garantizar que la generación de Hashes (IDs) sea consistente.
    """
    logger.info("Iniciando estandarización de profesores y monitores...")

    # Estandarización de Profesores
    if 'profesor_encargado' in df.columns:
        df['profesor_norm'] = normalize_text(df['profesor_encargado'])
    
    df['profesor_encargado'] = apply_mapping(df['profesor_norm'], PROFESOR_MAPPING, 'profesor_encargado')
    df = df.drop(columns=['profesor_norm'])

    # Estandarizarción de Monitores
    if 'monitor_encargado' in df.columns:
        df['monitor_norm'] = normalize_text(df['monitor_encargado'])
        
        # Aplicamos el mapeo para monitores
        df['monitor_encargado'] = apply_mapping(
            df['monitor_norm'], MONITOR_MAPPING, 'monitor_encargado'
        )
        df = df.drop(columns=['monitor_norm'])

    logger.info("Estandarización de staff finalizada exitosamente.")
    
    return df