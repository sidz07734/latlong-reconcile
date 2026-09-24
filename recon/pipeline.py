"""Glue: load -> clean -> area -> match -> verdict. No file writing here."""
from collections import Counter

import geopandas as gpd
import pandas as pd

from recon.cleaner import clean_parcels, normalize_id
from recon.geometry import add_area_sqm
from recon.loader import load_csv, load_geojson
from recon.matcher import MAX_FUZZY_DISTANCE, match_all
from recon.verdict import DEFAULT_TOLERANCE, NO_MATCH, decide

NO_CSV_RECORD = "NoCsvRecord"  # polygon that no CSV row points to


def reconcile_rows(df: pd.DataFrame, map_areas: dict[str, float],
                   tolerance: float, max_distance: int) -> pd.DataFrame:
    """Add verdict, matched_parcel_id and reason to every CSV row."""
    matches = match_all(list(df["clean_parcel_id"]), set(map_areas), max_distance)
    decided = [decide(m, area, map_areas, tolerance)
               for m, area in zip(matches, df["clean_area_sqm"])]

    out = df.copy()
    out["verdict"] = [v for v, _ in decided]
    # A rejected fuzzy candidate (NoMatch) must not claim the polygon
    out["matched_parcel_id"] = [m.parcel_id if v != NO_MATCH and m.parcel_id else ""
                                for m, (v, _) in zip(matches, decided)]
    out["reason"] = [r for _, r in decided]
    return flag_duplicate_claims(out)


def flag_duplicate_claims(df: pd.DataFrame) -> pd.DataFrame:
    """If 2+ CSV rows point at the same polygon, say so in each row's reason."""
    claims = Counter(pid for pid in df["matched_parcel_id"] if pid)
    dupes = df["matched_parcel_id"].map(lambda pid: claims.get(pid, 0) > 1)
    df.loc[dupes, "reason"] += df.loc[dupes, "matched_parcel_id"].map(
        lambda pid: f"; WARNING: {claims[pid]} CSV rows claim {pid}")
    return df


def tag_polygons(gdf: gpd.GeoDataFrame, rows: pd.DataFrame) -> gpd.GeoDataFrame:
    """Give each polygon the verdict of the CSV row that matched it."""
    matched = rows[rows["matched_parcel_id"] != ""].drop_duplicates("matched_parcel_id")
    lookup = matched.set_index("matched_parcel_id")

    out = gdf.copy()
    out["verdict"] = out["parcel_id"].map(lookup["verdict"]).fillna(NO_CSV_RECORD)
    out["csv_parcel_id"] = out["parcel_id"].map(lookup["clean_parcel_id"]).fillna("")
    out["reason"] = out["parcel_id"].map(lookup["reason"]).fillna(
        "No CSV row matched this polygon")
    return out


def run(csv_path: str, geojson_path: str, tolerance: float = DEFAULT_TOLERANCE,
        max_distance: int = MAX_FUZZY_DISTANCE) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """Full reconciliation. Returns (csv report rows, tagged polygons)."""
    df = clean_parcels(load_csv(csv_path))
    gdf = add_area_sqm(load_geojson(geojson_path))
    gdf["parcel_id"] = gdf["parcel_id"].map(normalize_id)
    map_areas = dict(zip(gdf["parcel_id"], gdf["map_area_sqm"]))

    rows = reconcile_rows(df, map_areas, tolerance, max_distance)
    return rows, tag_polygons(gdf, rows)