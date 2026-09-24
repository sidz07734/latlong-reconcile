import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from recon.cleaner import clean_parcels, normalize_id
from recon.geometry import add_area_sqm


def test_normalize_id_fixes_format_not_content():
    assert normalize_id("  blr-002 ") == "BLR-002"
    assert normalize_id("BLR-O13") == "BLR-O13"  # letter O is left for the matcher


def test_area_coercion():
    df = pd.DataFrame({"parcel_id": ["A"] * 4, "owner": ["x"] * 4, "village": ["v"] * 4,
                       "area_sqm": ["1080", " 1,080 ", "", "N/A"]})
    areas = clean_parcels(df)["clean_area_sqm"].tolist()
    assert areas[:2] == [1080.0, 1080.0]
    assert pd.isna(areas[2]) and pd.isna(areas[3])


def test_area_is_in_square_metres_not_degrees():
    # 0.0003° x 0.0003° square in Bangalore ≈ 32.5 m x 33.3 m ≈ 1081 m²
    gdf = gpd.GeoDataFrame({"parcel_id": ["T"]},
                           geometry=[box(77.5946, 12.9716, 77.5949, 12.9719)], crs="EPSG:4326")
    area = add_area_sqm(gdf)["map_area_sqm"].iloc[0]
    assert 1070 < area < 1090
