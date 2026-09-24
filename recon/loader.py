"""Load the parcel CSV and GeoJSON, failing early with clear messages."""
from pathlib import Path

import geopandas as gpd
import pandas as pd

REQUIRED_CSV_COLUMNS = {"parcel_id", "owner", "area_sqm", "village"}
DEFAULT_CRS = "EPSG:4326"  # GeoJSON standard (RFC 7946): lon/lat in degrees


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read the CSV as raw text so nothing is altered before cleaning."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip().str.lower()

    missing = REQUIRED_CSV_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing required columns {sorted(missing)}")
    return df


def load_geojson(path: str | Path) -> gpd.GeoDataFrame:
    """Read polygons; assume WGS84 if the file declares no CRS."""
    try:
        gdf = gpd.read_file(path)
    except Exception as exc:
        raise ValueError(
            f"{path}: could not be read as GeoJSON ({exc}). "
            "Check the file is plain JSON, not RTF/Word-wrapped."
        ) from exc

    if "parcel_id" not in gdf.columns:
        raise ValueError(f"{path}: features have no 'parcel_id' property")
    if gdf.crs is None:
        gdf = gdf.set_crs(DEFAULT_CRS)
    return gdf