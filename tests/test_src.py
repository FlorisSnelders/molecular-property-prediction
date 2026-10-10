import numpy as np
import pandas as pd
import pytest

import src.data as data
from src.data import parse_hopv
from src.features import DESCRIPTOR_NAMES, compute_all_descriptors, descriptor_frame
from src.stability import predict_stability_labels

HOPV_SNIPPET = """CCO
InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3
10.1/abc,KEY1,molecule,bulk,PC71BM,-5.10,-3.20,1.5,1.6,7.8,0.7,17.0,66.3
Compound 1
2
Conformer 1
c1ccccc1
InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H
10.1/def,KEY2,polymer,bulk,PC61BM,nan,nan,nan,nan,3.0,0.9,5.4,63.0
Compound 2
""".splitlines(keepends=True)


def test_parse_hopv_extracts_smiles_and_experimental_values():
    df = parse_hopv(HOPV_SNIPPET)
    assert list(df["smiles"]) == ["CCO", "c1ccccc1"]
    assert df.loc[0, "homo"] == pytest.approx(-5.10)
    assert df.loc[0, "construction"] == "molecule"
    # the file writes missing values as the string "nan"
    assert np.isnan(df.loc[1, "homo"]) and np.isnan(df.loc[1, "lumo"])
    assert df["pce"].dtype == float


def test_descriptors_valid_and_invalid_smiles():
    good = compute_all_descriptors("CCO")
    assert set(good) == set(DESCRIPTOR_NAMES)
    assert good["MolWt"] == pytest.approx(46.069, abs=0.01)
    bad = compute_all_descriptors("not-a-smiles")
    assert all(np.isnan(v) for v in bad.values())
    frame = descriptor_frame(["CCO", "c1ccccc1"])
    assert frame.shape == (2, len(DESCRIPTOR_NAMES))


CLASSES = np.array(["high", "low", "medium"])
PROBA = np.array([
    [0.6, 0.1, 0.3],   # high
    [0.2, 0.3, 0.5],   # medium
    [0.1, 0.5, 0.4],   # low (argmax)
    [0.3, 0.2, 0.5],   # medium
])


def test_default_labels_are_the_most_likely_class():
    assert list(predict_stability_labels(PROBA, CLASSES)) == ["high", "medium", "low", "medium"]


def test_competition_adjustment_forces_n_low():
    labels = predict_stability_labels(PROBA, CLASSES, n_low=2)
    # the two lowest P(high) rows (2 and 1) become "low"; the rest pick high vs medium
    assert list(labels) == ["high", "low", "low", "medium"]
    assert (labels == "low").sum() == 2


def test_course_loaders_return_none_when_files_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "SQL_CSV", tmp_path / "sql.csv")
    monkeypatch.setattr(data, "KAGGLE_TEST", {"classification": tmp_path / "c.csv"})
    assert data.load_sql_molecules() is None
    assert data.load_kaggle_test("classification") is None


def test_hopv_table_adds_stability_only_when_labels_exist(tmp_path, monkeypatch):
    hopv = tmp_path / "hopv.data"
    hopv.write_text("".join(HOPV_SNIPPET + HOPV_SNIPPET[:3]))  # CCO appears twice
    monkeypatch.setattr(data, "HOPV_COURSE", tmp_path / "missing.data")
    monkeypatch.setattr(data, "HOPV_PUBLIC", hopv)
    monkeypatch.setattr(data, "STABILITY_CSV", tmp_path / "missing.csv")
    table = data.load_hopv_table()
    assert list(table.columns) == ["smiles", "homo", "lumo"]
    assert len(table) == 2  # duplicate SMILES dropped

    labels = tmp_path / "stability.csv"
    pd.DataFrame({"smiles": ["CCO", "c1ccccc1"], "stability": ["high", "low"]}).to_csv(labels, index=False)
    monkeypatch.setattr(data, "STABILITY_CSV", labels)
    assert list(data.load_hopv_table()["stability"]) == ["high", "low"]


def test_hopv_path_explains_how_to_download(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "HOPV_COURSE", tmp_path / "a")
    monkeypatch.setattr(data, "HOPV_PUBLIC", tmp_path / "b")
    with pytest.raises(FileNotFoundError, match="download_hopv.py"):
        data.hopv_path()
