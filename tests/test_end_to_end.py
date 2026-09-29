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


def test_provided_company_data_still_works():
    orig = DATA / "company_original"
    rows, polygons = run(orig / "parcels.csv", orig / "parcels.geojson")
    counts = Counter(rows["verdict"])
    assert set(counts) == {"Match", "IdMatchAreaMismatch", "FuzzyMatch", "NoMatch"}
    assert len(rows) == 30 and len(polygons) == 28


def test_sample_polygons_are_real_osm_buildings():
    import geopandas as gpd
    gdf = gpd.read_file(DATA / "parcels.geojson")
    assert gdf["osm_way_id"].notna().all()                 # every polygon traceable to OpenStreetMap
    minx, miny, maxx, maxy = gdf.total_bounds               # and located in J. P. Nagar, Bengaluru
    assert 77.58 < minx and maxx < 77.61 and 12.90 < miny and maxy < 12.93
