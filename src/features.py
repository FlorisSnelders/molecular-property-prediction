"""Molecular descriptors.

Every model in this project uses the same input: all RDKit 2D descriptors
computed from the SMILES string (217 with the pinned RDKit version).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors

RDLogger.DisableLog("rdApp.*")  # silence per-molecule RDKit warnings

DESCRIPTOR_NAMES = [name for name, _ in Descriptors._descList]
_CALC = MoleculeDescriptors.MolecularDescriptorCalculator(DESCRIPTOR_NAMES)


def compute_all_descriptors(smiles: str) -> dict:
    """All RDKit descriptors for one SMILES string; NaN for every descriptor
    if the SMILES cannot be parsed or a descriptor fails."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {name: np.nan for name in DESCRIPTOR_NAMES}
    try:
        return dict(zip(DESCRIPTOR_NAMES, _CALC.CalcDescriptors(mol)))
    except Exception:
        return {name: np.nan for name in DESCRIPTOR_NAMES}


def descriptor_frame(smiles) -> pd.DataFrame:
    """Descriptor table (one row per SMILES, one column per descriptor)."""
    return pd.DataFrame([compute_all_descriptors(s) for s in smiles], columns=DESCRIPTOR_NAMES)
