import sys
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

# --- RUTAS: Uso de Pathlib ---
# .resolve() obtiene la ruta absoluta exacta.
# .parent sube un nivel de carpeta. Así evitamos usar strings sueltos como ".."
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / 'src'
sys.path.append(str(SRC_DIR))

# --- IMPORTACIONES MODULARES ---
from ingestion.load_data import load_excels_from_folder
from cleaning.clean_date import clean_dates
from cleaning.clean_carrera import clean_carrera
from cleaning.clean_curso import clean_curso
from cleaning.clean_semestre import clean_semestre
from cleaning.clean_actividades import clean_actividades
from cleaning.clean_staff import clean_staff
from cleaning.anonymization import anonymize_data

# --- CONFIGURACIÓN DE LOGGING ---
log_format = '%(asctime)s | %(filename)s:%(lineno)d | %(funcName)s() | %(levelname)s | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    force=True,
    handlers=[
        logging.FileHandler(BASE_DIR / "logs.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    """
    Orquesta la ejecución del pipeline ETL utilizando el método .pipe() de Pandas
    para un procesamiento fluido, encadenado y funcional.
    """
    start_time = datetime.now()
    logger.info("=" * 50)
    logger.info("INICIANDO PIPELINE DE DATOS - REGISTRO LEA")
    logger.info("=" * 50)

    try:
        # 1. Definición de rutas estructuradas
        raw_path = BASE_DIR / 'data' / 'raw'
        processed_path = BASE_DIR / 'data' / 'processed'
        output_file = processed_path / 'registro_consolidado.csv'

        # 2. Ingesta
        df = load_excels_from_folder(str(raw_path))
        
        if df.empty:
            logger.error("El proceso se detuvo: No hay datos para procesar en la ruta origen.")
            return
            
        logger.info(f"Dataset consolidado inicial: {len(df)} registros.")

        # 3. Transformación y Limpieza (Pipeline Funcional con .pipe)
        # Esto evita la mutación de estado constante y permite leer el flujo lógicamente.
        df = (
            df.pipe(clean_dates)
              .pipe(clean_carrera)
              .pipe(clean_curso)
              .pipe(clean_semestre)
              .pipe(clean_actividades)
              .pipe(clean_staff)
              .pipe(anonymize_data, dominio_institucional="@javerianacali.edu.co")
        )

        # 4. Exportación
        processed_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        duracion = datetime.now() - start_time
        logger.info("=" * 50)
        logger.info(f"PIPELINE FINALIZADO EXITOSAMENTE 🚀")
        logger.info(f"Archivo guardado en: {output_file.relative_to(BASE_DIR)}")
        logger.info(f"Registros finales: {len(df)}")
        logger.info(f"Tiempo total: {duracion}")
        logger.info("=" * 50)

    except Exception as e:
        logger.critical(f"ERROR FATAL EN EL PIPELINE: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()