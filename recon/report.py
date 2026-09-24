"""Write report.csv / report.geojson and build the summary line."""
from collections import Counter
from pathlib import Path

import geopandas as gpd
import pandas as pd

from recon.verdict import FUZZY_MATCH, ID_MATCH_AREA_MISMATCH, MATCH, NO_MATCH

ORIGINAL_COLUMNS = ["parcel_id", "owner", "area_sqm", "village"]
ADDED_COLUMNS = ["verdict", "matched_parcel_id", "reason"]
# simplestyle-spec colours: GitHub and geojson.io colour polygons by these
VERDICT_COLOURS = {
    MATCH: "#2e7d32",                   # green
    ID_MATCH_AREA_MISMATCH: "#ef6c00",  # orange
    FUZZY_MATCH: "#f9a825",             # yellow
    "NoCsvRecord": "#9e9e9e",           # grey
}

def write_csv(rows: pd.DataFrame, out_dir: Path) -> Path:
    """Original CSV rows (untouched) + verdict, matched_parcel_id, reason."""
    path = out_dir / "report.csv"
    # utf-8-sig so Excel shows "m²" correctly
    rows[ORIGINAL_COLUMNS + ADDED_COLUMNS].to_csv(path, index=False, encoding="utf-8-sig")
    return path


def write_geojson(polygons: gpd.GeoDataFrame, out_dir: Path) -> Path:
    """Input polygons (still lon/lat) + verdict, for colour-coding on a map."""
    path = out_dir / "report.geojson"
    styled = polygons.to_crs("EPSG:4326")
    styled["fill"] = styled["verdict"].map(VERDICT_COLOURS)
    styled["stroke"] = styled["fill"]
    styled["fill-opacity"] = 0.6
    styled.to_file(path, driver="GeoJSON")
    return path


def summary_line(rows: pd.DataFrame, polygons: gpd.GeoDataFrame) -> str:
    counts = Counter(rows["verdict"])
    parts = [f"{v}={counts.get(v, 0)}"
             for v in (MATCH, ID_MATCH_AREA_MISMATCH, FUZZY_MATCH, NO_MATCH)]
    unmatched = (polygons["verdict"] == "NoCsvRecord").sum()
    return (f"{len(rows)} rows: " + " ".join(parts)
            + f" | polygons without a CSV row: {unmatched}")