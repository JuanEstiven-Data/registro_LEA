import pandas as pd
import hashlib
import logging

logger = logging.getLogger(__name__)

def anonymize_data(df: pd.DataFrame, dominio_institucional: str="@javerianacali.edu.co")->pd.DataFrame:
    """
    Pseudonimiza los datos aplicando una Jerarquía de Confianza para los estudiantes
    (Nivel 1: Email Institucional, Nivel 2: Email Personal, Nivel 3: Nombre) 
    y asignando alias legibles para el staff.
    """
    logger.info("Iniciando proceso de pseudonimización estructurada...")

    # Generar Hashing
    def generar_id(texto: str, prefijo: str="", longitud: int=12)->str:
        texto_str = str(texto).lower().strip()
        if pd.isna(texto) or texto_str in ['', 'nan', 'no aplica', 'sin informacion']:
            return 'No Aplica'
        hash_completo = hashlib.sha256(texto_str.encode('utf-8')).hexdigest()
        return f"{prefijo}{hash_completo[:longitud]}".upper()
    
    # Jerarquía de Confianza
    def seleccionar_dato_confiable(fila)->str:
        # .get()
        email = str(fila.get('email', '')).lower().strip()
        nombre = str(fila.get('nombre_completo', '')).lower().strip()

        # Nivel de confianza 1, Dominio Institucional
        if dominio_institucional in email:
            return email
        
        # Nivel de Confianza 2, Correo Personal
        elif '@' in email:
            return email
        
        # Nivel de Confianza 3, Nombre Completo
        elif nombre and nombre not in ['nan', 'sin informacion', 'no aplica']:
            return nombre
        # Nulos o sin Informacion
        return "Sin_Identificador"
    
    # Aplicar la Jerarquía y Generar el ID de Estudiantes
    df['dato_base_hash'] = df.apply(seleccionar_dato_confiable, axis=1)
    df['estudiante_id'] = df['dato_base_hash'].apply(lambda x: generar_id(x, longitud=12))

    # Alias para Profesores y Monitores
    if 'profesor_encargado' in df.columns:
        df['profesor_id'] = df['profesor_encargado'].apply(
            lambda x: generar_id(x, prefijo="PROF_", longitud=4)
        )
    if 'monitor_encargado' in df.columns:
        df['monitor_id'] = df['monitor_encargado'].apply(
            lambda x: generar_id(x, prefijo="MON_", longitud=4)
        )

    # Eliminar PII orginal y columnas temporales
    columnas_pii = [
        'nombre_completo',
        'email',
        'profesor_encargado',
        'monitor_encargado',
        'dato_base_hash'
    ]

    columnas_a_borrar = [col for col in columnas_pii if col in df.columns]
    df = df.drop(columns=columnas_a_borrar)

    logger.info(f"Pseudonimización exitosa. Columnas eliminadas: {columnas_a_borrar}")

    return df