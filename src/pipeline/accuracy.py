import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from pipeline.main import OUTPUT_FILE, run_pipeline, validate_public_dataset


logger = logging.getLogger(__name__)

YEAR_COLUMN = "a\u00f1o"
REQUIRED_COLUMNS = {
    "mes",
    "carrera",
    "semestre",
    "curso",
    "actividades",
    YEAR_COLUMN,
    "fecha",
    "periodo_academico",
    "ciclo_lectivo",
    "estudiante_id",
    "profesor_id",
    "monitor_id",
}
TEXT_COLUMNS = ["mes", "carrera", "curso", "actividades", "ciclo_lectivo", "estudiante_id"]
MONTH_BY_NUMBER = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


@dataclass(frozen=True)
class AccuracyCheck:
    name: str
    detail: str


class AccuracyError(AssertionError):
    """Error de calidad de datos detectado en el output del pipeline."""


def assert_quality(condition: bool, message: str) -> None:
    if not condition:
        raise AccuracyError(message)


def load_dataset(path: Path) -> pd.DataFrame:
    assert_quality(path.exists(), f"No existe el dataset esperado: {path}")
    data = pd.read_csv(path)
    assert_quality(not data.empty, "El dataset final esta vacio.")
    return data


def check_schema(data: pd.DataFrame) -> AccuracyCheck:
    missing = sorted(REQUIRED_COLUMNS.difference(data.columns))
    duplicated = data.columns[data.columns.duplicated()].tolist()

    assert_quality(not missing, f"Faltan columnas requeridas: {missing}")
    assert_quality(not duplicated, f"Hay columnas duplicadas: {duplicated}")
    assert_quality(len(data) >= 1_000, f"El volumen parece bajo para el historico: {len(data)} filas.")

    return AccuracyCheck("schema", f"{len(data)} filas y {len(data.columns)} columnas validas")


def check_privacy(data: pd.DataFrame) -> AccuracyCheck:
    validate_public_dataset(data)

    text_data = data.select_dtypes(include=["object", "string"]).fillna("")
    email_like = text_data.apply(lambda col: col.str.contains("@", regex=False, na=False)).any()
    columns_with_email = email_like[email_like].index.tolist()
    assert_quality(not columns_with_email, f"Hay valores con apariencia de email en: {columns_with_email}")

    student_pattern = re.compile(r"^(No Aplica|[A-F0-9]{12})$")
    invalid_ids = ~data["estudiante_id"].astype(str).str.match(student_pattern)
    assert_quality(not invalid_ids.any(), "Hay estudiante_id con formato inesperado.")

    return AccuracyCheck("privacy", "sin columnas PII, emails visibles ni IDs fuera de formato")


def check_completeness(data: pd.DataFrame) -> AccuracyCheck:
    empty_columns: list[str] = []
    for column in TEXT_COLUMNS:
        empty_mask = data[column].isna() | data[column].astype(str).str.strip().eq("")
        if empty_mask.any():
            empty_columns.append(column)

    assert_quality(not empty_columns, f"Hay textos vacios en columnas criticas: {empty_columns}")
    assert_quality(data["estudiante_id"].nunique() > 0, "No hay estudiantes unicos identificables.")
    assert_quality(data["ciclo_lectivo"].nunique() >= 2, "No hay suficientes ciclos para analisis temporal.")

    return AccuracyCheck("completeness", "columnas criticas completas para dashboard")


def check_temporal_logic(data: pd.DataFrame) -> AccuracyCheck:
    dates = pd.to_datetime(data["fecha"], errors="coerce")
    assert_quality(dates.notna().all(), "Hay fechas invalidas o no parseables.")

    expected_period = ((dates.dt.month - 1) // 6) + 1
    actual_period = pd.to_numeric(data["periodo_academico"], errors="coerce")
    assert_quality(actual_period.notna().all(), "Hay periodos academicos no numericos.")
    assert_quality((actual_period.astype(int) == expected_period).all(), "Periodo academico no coincide con fecha.")

    expected_cycle = data[YEAR_COLUMN].astype(int).astype(str) + "-" + expected_period.astype(str)
    assert_quality((data["ciclo_lectivo"].astype(str) == expected_cycle).all(), "Ciclo lectivo no coincide con fecha/anio.")

    expected_month = dates.dt.month.map(MONTH_BY_NUMBER)
    assert_quality((data["mes"].astype(str) == expected_month).all(), "Nombre de mes no coincide con fecha.")

    return AccuracyCheck("temporal_logic", "fechas, meses, periodos y ciclos consistentes")


def check_analysis_readiness(data: pd.DataFrame) -> AccuracyCheck:
    semester = pd.to_numeric(data["semestre"], errors="coerce")
    assert_quality(semester.notna().all(), "Hay semestres no numericos.")
    assert_quality(semester.between(0, 12).all(), "Hay semestres fuera del rango esperado 0-12.")

    matrix = pd.crosstab(data["carrera"], data["actividades"])
    assert_quality(matrix.shape[0] >= 3, "Hay muy pocas carreras para cruces analiticos.")
    assert_quality(matrix.shape[1] >= 3, "Hay muy pocas actividades para cruces analiticos.")
    assert_quality(matrix.to_numpy().sum() == len(data), "La matriz carrera-actividad no conserva el total de visitas.")

    return AccuracyCheck("analysis_readiness", f"matriz carrera-actividad lista: {matrix.shape[0]}x{matrix.shape[1]}")


CHECKS: tuple[Callable[[pd.DataFrame], AccuracyCheck], ...] = (
    check_schema,
    check_privacy,
    check_completeness,
    check_temporal_logic,
    check_analysis_readiness,
)


def run_accuracy_checks(data_path: Path = OUTPUT_FILE, *, execute_pipeline: bool = True) -> list[AccuracyCheck]:
    if execute_pipeline:
        logger.info("Ejecutando pipeline antes de validar accuracy...")
        run_pipeline(output_file=data_path)

    data = load_dataset(data_path)
    return [check(data) for check in CHECKS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida el output minimo del pipeline Registro LEA.")
    parser.add_argument(
        "--skip-pipeline",
        action="store_true",
        help="Valida el CSV existente sin volver a ejecutar el pipeline.",
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=OUTPUT_FILE,
        help="Ruta del CSV final a validar.",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s", force=True)
    args = parse_args()

    try:
        results = run_accuracy_checks(args.data_path, execute_pipeline=not args.skip_pipeline)
    except AccuracyError as error:
        print(f"FAIL | {error}")
        raise SystemExit(1) from error

    for result in results:
        print(f"OK | {result.name}: {result.detail}")

    print("OK | accuracy finalizada sin errores.")


if __name__ == "__main__":
    main()
