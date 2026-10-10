"""Data locations and loaders.

Public data (downloaded by scripts/download_hopv.py):
    data/raw/HOPV_15_revised_2.data   Harvard Organic Photovoltaics 2015 dataset (CC BY 4.0)

Course data (optional, not redistributable; place it in data/course/ to
reproduce the original results, see data/README.md):
    data/course/HOPV_homolumo.data          course copy of HOPV (used instead of the public file)
    data/course/HOPV_stability.csv          stability labels (low / medium / high)
    data/course/sql_molecules.csv           extra labelled molecules from the course database
    data/course/classification_test.csv     Kaggle test molecules (stability competition)
    data/course/regression_test.csv         Kaggle test molecules (energy-level competition)

Every loader for course data returns None when the file is missing, so the
notebooks can skip those parts.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
COURSE_DIR = DATA_DIR / "course"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT / "models"

HOPV_PUBLIC = RAW_DIR / "HOPV_15_revised_2.data"
HOPV_COURSE = COURSE_DIR / "HOPV_homolumo.data"
STABILITY_CSV = COURSE_DIR / "HOPV_stability.csv"
SQL_CSV = COURSE_DIR / "sql_molecules.csv"
KAGGLE_TEST = {
    "classification": COURSE_DIR / "classification_test.csv",
    "regression": COURSE_DIR / "regression_test.csv",
}

# Column layout of the experimental line in the HOPV file (Table 2 of the data descriptor).
HOPV_COLUMNS = [
    "doi", "InChIKEY", "construction", "architecture", "complement",
    "homo", "lumo", "electrochemical_gap", "optical_gap",
    "pce", "voc", "jsc", "ff",
]
NUMERIC_COLUMNS = ["homo", "lumo", "electrochemical_gap", "optical_gap", "pce", "voc", "jsc", "ff"]


def parse_hopv(lines: list[str]) -> pd.DataFrame:
    """Parse the lines of a HOPV ``.data`` file into one row per molecule.

    Each molecule block starts with its SMILES line, followed by the InChI
    line and the comma-separated experimental line. The InChI line is the
    reliable marker, so the SMILES is the line before it and the
    experimental values are the line after it.
    """
    data = []
    for i, line in enumerate(lines):
        if line.startswith("InChI="):
            exp = lines[i + 1].strip().split(",")
            row = {"smiles": lines[i - 1].strip()}
            row.update(dict(zip(HOPV_COLUMNS, exp)))
            data.append(row)
    df = pd.DataFrame(data)
    # Missing values are written as the string "nan" in the file.
    df = df.replace("nan", np.nan)
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def hopv_path() -> Path:
    """The course copy of HOPV if present (to reproduce the original results), else the public file."""
    if HOPV_COURSE.exists():
        return HOPV_COURSE
    if HOPV_PUBLIC.exists():
        return HOPV_PUBLIC
    raise FileNotFoundError(
        f"HOPV data not found. Run `python scripts/download_hopv.py` to download it to {HOPV_PUBLIC}."
    )


def load_hopv() -> pd.DataFrame:
    """All parsed HOPV molecules (350 rows, duplicates included)."""
    with open(hopv_path(), "r") as f:
        return parse_hopv(f.readlines())


def load_hopv_table() -> pd.DataFrame:
    """HOPV molecules with targets: one row per unique SMILES with ``homo``,
    ``lumo`` and, when the course labels are available, ``stability``."""
    df = load_hopv().drop_duplicates(subset="smiles", keep="first")
    df = df[["smiles", "homo", "lumo"]]
    if STABILITY_CSV.exists():
        stability = pd.read_csv(STABILITY_CSV).drop_duplicates(subset="smiles", keep="first")
        df = df.merge(stability, on="smiles")
    return df.reset_index(drop=True)


def load_sql_molecules() -> pd.DataFrame | None:
    """Extra labelled molecules from the course database (smiles, homo, lumo, stability), or None."""
    return pd.read_csv(SQL_CSV) if SQL_CSV.exists() else None


def load_kaggle_test(task: str) -> pd.DataFrame | None:
    """Kaggle test molecules for ``task`` ("classification" or "regression"), or None."""
    path = KAGGLE_TEST[task]
    return pd.read_csv(path) if path.exists() else None
