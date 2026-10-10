# Models

Trained models are not committed (the original stability and energy-level models were 26 MB and 64 MB). The training notebooks save them here:

- `classification_model.pkl`: ExtraTrees stability classifier plus its label encoder, imputer, scaler and feature list (`notebooks/03_stability_training.ipynb`, needs the course stability labels)
- `regression_model.pkl`: ExtraTrees + multi-seed MLP models for HOMO and LUMO plus preprocessing (`notebooks/05_energy_level_training.ipynb`, runs on public HOPV data)
