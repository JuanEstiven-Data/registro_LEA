import pandas as pd
import logging
from cleaning.text_utils import normalize_text, apply_mapping, clean_text
from mappings.curso import CURSO_MAPPING

# Instanciamos el logger para este módulo
logger = logging.getLogger(__name__)

def clean_curso(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline de limpieza específico para la columna 'curso'.
    Normaliza el texto, ajusta los números romanos y aplica el diccionario.
    """
    logger.info("Iniciando limpieza de la columna 'curso'...")

    # Normalización base
    # Rellenar nulos preventivamente
    df['curso'] = df['curso'].fillna('Sin información')
    df['curso_norm'] = normalize_text(df['curso'])
    df['curso_norm'] = clean_text(df['curso_norm'])

    # Se reemplaza primero el más largo (' iii') para evitar cruces con (' ii')
    df['curso_norm'] = (
        df['curso_norm']
        .str.replace(' iii', 'iii', regex=False)
        .str.replace(' ii', 'ii', regex=False)
        .str.replace(' iv', 'iv', regex=False)
    )

    # Aplicación del Mapeo
    df['curso_final'] = apply_mapping(df['curso_norm'], CURSO_MAPPING, 'curso')

    # Formato Estético Final para el Dashboard
    df['curso_final'] = df['curso_final'].str.title()
    
    # Aseguramos que 'Sin Información' quede bien escrito si hubo nulos
    mask_sin_info = df['curso_final'].str.lower() == 'sin información'
    df.loc[mask_sin_info, 'curso_final'] = 'Sin Información'

    # Limpieza de memoria
    df = df.drop(columns=['curso_norm'])

    logger.info("Limpieza de 'curso' finalizada exitosamente.")
    
    return df