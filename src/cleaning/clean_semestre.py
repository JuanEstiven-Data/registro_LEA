import pandas as pd
import logging

# Instanciamos el logger para este módulo específico
logger = logging.getLogger(__name__)

def clean_semestre(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia la columna 'semestre' corrigiendo errores tipográficos sutiles
    (como tildes accidentales en los números) y fuerza su conversión a numérico.
    Valores de texto (ej. 'Profesor', 'NA') se transforman de forma segura en 0.
    """
    logger.info("Iniciando limpieza de la columna 'semestre'...")

    # Conversión temporal a texto para quitar el carácter '´' sin afectar los números reales
    semestre_corregido = (
        df['semestre']
        .astype("string")
        .str.replace('´', '', regex=False)
    )

    # Conversión Numérica (Method Chaining)
    df['semestre'] = (
        pd.to_numeric(semestre_corregido, errors='coerce')
        .fillna(0)
        .astype(int)
    )

    logger.info("Limpieza de 'semestre' finalizada exitosamente.")
    
    return df