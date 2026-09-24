"""Normalise messy CSV fields. Original columns are kept untouched for the report."""
import pandas as pd


def normalize_id(value: str) -> str:
    """' blr-002 ' -> 'BLR-002'. Typos (O vs 0) are NOT fixed here, on purpose."""
    return str(value).strip().upper()


def normalize_text(value: str) -> str:
    """' suresh   gowda ' -> 'Suresh Gowda'."""
    return " ".join(str(value).split()).title()


def clean_parcels(df: pd.DataFrame) -> pd.DataFrame:
    """Add clean_* columns next to the raw ones."""
    out = df.copy()
    out["clean_parcel_id"] = out["parcel_id"].map(normalize_id)
    out["clean_owner"] = out["owner"].map(normalize_text)
    out["clean_village"] = out["village"].map(normalize_text)
    # Blank or non-numeric -> NaN (treated as "area missing" later)
    # "1,080" -> 1080; blank or non-numeric ("N/A") -> NaN, reported later
    out["clean_area_sqm"] = pd.to_numeric(
        out["area_sqm"].str.replace(",", "").str.strip(), errors="coerce")
    return out