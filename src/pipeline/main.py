import os
import sys

# FIX DE RUTAS (Para que Python encuentre tus carpetas)
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_src = os.path.abspath(os.path.join(directorio_actual, '..'))
sys.path.append(directorio_src)

import pandas as pd
import logging
from datetime import datetime

# Importamos todos tus módulos
from ingestion.load_data import load_excels_from_folder # 👈 Tu función estrella
from cleaning.clean_carrera import clean_carrera
from cleaning.clean_curso import clean_curso
from cleaning.clean_semestre import clean_semestre
from cleaning.clean_staff import clean_staff
from cleaning.anonymization import anonymize_data

# Configuración del Logging
log_format = '%(asctime)s | %(filename)s:%(lineno)d | %(funcName)s() | %(levelname)s | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("errores_proyecto.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    start_time = datetime.now()
    logger.info("==========================================")
    logger.info("INICIANDO PIPELINE DE DATOS - REGISTRO LEA")
    logger.info("==========================================")

    try:
        # --- PASO 1 y 2: INGESTA Y ESTANDARIZACIÓN INICIAL ---
        # Delegamos todo a tu función load_data.py
        raw_path = os.path.join(directorio_src, '..', 'data', 'raw')
        df = load_excels_from_folder(raw_path)
        
        if df.empty:
            logger.error("El proceso se detuvo porque no hay datos para procesar.")
            return
            
        logger.info(f"Dataset consolidado inicial: {len(df)} registros.")

        # --- PASO 3: LIMPIEZA POR DOMINIO ---
        df = clean_carrera(df)
        df = clean_curso(df)
        df = clean_semestre(df)
        
        # --- PASO 4: ESTANDARIZACIÓN DE STAFF ---
        df = clean_staff(df)

        # --- PASO 5: GOBERNANZA Y ANONIMIZACIÓN ---
        df = anonymize_data(df, dominio_institucional="@uni.edu.co")

        # --- PASO 6: EXPORTACIÓN ---
        output_dir = os.path.join(directorio_src, '..', 'data', 'processed')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'registro_consolidado.csv')
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        duracion = datetime.now() - start_time
        logger.info("==========================================")
        logger.info(f"PIPELINE FINALIZADO EXITOSAMENTE")
        logger.info(f"Registros finales: {len(df)}")
        logger.info(f"Tiempo total: {duracion}")
        logger.info("==========================================")

    except Exception as e:
        logger.critical(f"ERROR FATAL EN EL PIPELINE: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()