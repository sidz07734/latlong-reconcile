from collections import Counter
from pathlib import Path

from recon.pipeline import run

DATA = Path(__file__).parent.parent / "sample_data"


def test_sample_data_produces_all_four_verdicts():
    rows, polygons = run(DATA / "parcels.csv", DATA / "parcels.geojson")
    counts = Counter(rows["verdict"])
    assert set(counts) == {"Match", "IdMatchAreaMismatch", "FuzzyMatch", "NoMatch"}
    assert len(polygons) == 29
    assert "verdict" in polygons.columns
