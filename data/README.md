# Data

No data is committed to this repository.

## Public data (enough to run the HOMO/LUMO pipeline)

```bash
python scripts/download_hopv.py
```

This downloads the **Harvard Organic Photovoltaics 2015 (HOPV-15)** dataset to `data/raw/HOPV_15_revised_2.data`: 350 donor molecules from the literature, each with its SMILES string, experimental HOMO/LUMO levels and device metrics (16.6 MB).

> Lopez, S. A. et al. (2016). *The Harvard organic photovoltaic dataset.* Scientific Data 3, 160086. Dataset: https://doi.org/10.6084/m9.figshare.1610063, licensed CC BY 4.0.

## Course data (not included)

The original project also used files provided through the course, which cannot be redistributed:

| File (place in `data/course/`) | Contents | Used by |
|---|---|---|
| `HOPV_homolumo.data` | the course copy of HOPV; some HOMO/LUMO values differ from the public release | all notebooks (used instead of the public file when present) |
| `HOPV_stability.csv` | stability labels (low / medium / high) for the HOPV molecules | stability notebooks (required) |
| `sql_molecules.csv` | 232 extra labelled molecules from the course database | training and clustering notebooks (optional) |
| `classification_test.csv`, `regression_test.csv` | the 200 Kaggle test molecules of each competition | inference and clustering notebooks (optional) |

Without these files:
- the HOMO/LUMO notebooks (01, 02, 05, 06) run on public HOPV only, with inference demonstrated on a few HOPV molecules;
- the stability notebooks (03, 04) cannot be re-run, because the public HOPV release has no stability labels; their committed outputs show the original run.

On public HOPV only (233 molecules with both HOMO and LUMO), the energy-level notebook reaches a 5-fold cross-validated ExtraTrees MAE of 0.142 eV (HOMO) and 0.175 eV (LUMO), compared with 0.132 and 0.200 eV on the original 444-molecule training set.

## Generated files

`data/processed/` holds files written by the notebooks (descriptor table, cluster assignments, prediction CSVs). It is gitignored.
