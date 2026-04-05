import pandas as pd
import logging
from datetime import datetime

# Instanciamos el logger
logger = logging.getLogger(__name__)

# Diccionario original: CONSTANTE PRIVADA DEL MÓDULO
_MESES_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

# Diccionario inverso: CONSTANTE PRIVADA DEL MÓDULO
_NUM_A_MES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte textos de meses a formato Datetime ('fecha_analisis'), calcula el 
    periodo académico (1 o 2) para operaciones matemáticas, y construye el 
    ciclo lectivo (ej. '2024-1') para visualización en Dashboards.
    """
    logger.info("Iniciando transformación de fechas y periodos académicos...")

    # Comprobación de columnas
    if 'mes' not in df.columns or 'año' not in df.columns:
        logger.error("Faltan las columnas 'mes' o 'año'. Omitiendo clean_dates().")
        return df

    # Normalización: Method Chaining
    # Se fuerza enero (1) para valores nulos o ilegibles para mantener la serie temporal
    mes_num = (
        df['mes']
        .astype("string")
        .str.lower()
        .str.strip()
        .map(_MESES_MAP)
        .fillna(1)
        .astype(int)
    )
    
    # Relleno de seguridad para el año asumiendo el año actual.
    año_actual = datetime.now().year
    año_num = df['año'].fillna(año_actual).astype(int)
    df['año'] = año_num

    # Creación de la columna DATETIME  
    # Asume el día 1 para permitir agrupaciones mensuales
    df['fecha'] = pd.to_datetime({
        'year': año_num, 
        'month': mes_num, 
        'day': 1
    })

    # VECTORIZACIÓN: Cálculo matemático del Periodo Académico.
    # Al restar 1 al mes, dividir de forma entera entre 6 y sumar 1, 
    # los meses 1-6 se vuelven 1, y los meses 7-12 se vuelven 2.
    df['periodo_academico'] = ((mes_num - 1) // 6) + 1

    # VARIABLE CATEGÓRICA (Para los filtros del Dashboard)
    df['ciclo_lectivo'] = año_num.astype(str) + "-" + df['periodo_academico'].astype(str)
    df['mes'] = df['fecha'].dt.month.map(_NUM_A_MES)

    logger.info("Transformación temporal finalizada exitosamente.")
    
    return df