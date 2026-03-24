import pandas as pd
import logging

# Instanciar el logger específico para este archivo
logger = logging.getLogger(__name__)

def normalize_text(columna: pd.Series) -> pd.Series:
    """
    Estandariza la codificación del texto: convierte a minúsculas, 
    elimina tildes (acentos) y caracteres especiales forzando ASCII.
    """
    return (
        columna.astype("string")
        .str.strip()
        .str.lower()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
    )

def clean_text(columna: pd.Series) -> pd.Series:
    """
    Limpia ruido estructural del texto: elimina contenido entre 
    paréntesis y reduce múltiples espacios a un solo espacio.
    """
    return (
        columna
        .str.replace(r'\(.*?\)', '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )

def apply_mapping(columna: pd.Series, mapping: dict, nombre_col: str) -> pd.Series:
    """
    Aplica un diccionario de homologación y audita la calidad de los datos,
    enviando alertas al log si detecta valores que no existen en el diccionario.
    """
    # Encontrar inconsistencias entre los datos y los mappings
    valores_actuales = set(columna.dropna().unique())
    llaves_diccionario = set(mapping.keys())
    valores_huerfanos = valores_actuales - llaves_diccionario
    # Envío de logs usando el logger instanciado (logger.warning)
    if valores_huerfanos:
        logger.warning(f"[{nombre_col}] Hay {len(valores_huerfanos)} categorías no mapeadas.") 
        logger.warning(f"Valores: {valores_huerfanos}")
    
    return columna.map(mapping).fillna(columna).fillna('Sin Información')