"""Download the public HOPV-15 dataset into data/raw/.

Harvard Organic Photovoltaics 2015 dataset, Lopez et al., Scientific Data 3,
160086 (2016). figshare: https://doi.org/10.6084/m9.figshare.1610063 (CC BY 4.0).

Usage:
    python scripts/download_hopv.py
"""

import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data import HOPV_PUBLIC  # noqa: E402

URL = "https://ndownloader.figshare.com/files/4513735"
EXPECTED_BYTES = 16_582_981


def main() -> int:
    if HOPV_PUBLIC.exists() and HOPV_PUBLIC.stat().st_size == EXPECTED_BYTES:
        print(f"Already downloaded: {HOPV_PUBLIC.relative_to(ROOT)}")
        return 0
    HOPV_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading HOPV-15 from figshare ({EXPECTED_BYTES / 1e6:.1f} MB) ...")
    with urlopen(URL, timeout=120) as resp:
        HOPV_PUBLIC.write_bytes(resp.read())
    size = HOPV_PUBLIC.stat().st_size
    if size != EXPECTED_BYTES:
        print(f"Warning: got {size} bytes, expected {EXPECTED_BYTES}.")
    print(f"Saved {HOPV_PUBLIC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
