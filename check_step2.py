from recon.loader import load_csv, load_geojson
from recon.cleaner import clean_parcels

df = clean_parcels(load_csv("sample_data/parcels.csv"))
print(df[["parcel_id", "clean_parcel_id", "clean_owner", "clean_village", "clean_area_sqm"]].to_string())
print(f"\nCSV rows: {len(df)}")

gdf = load_geojson("sample_data/parcels.geojson")
print(f"Polygons: {len(gdf)} | CRS: {gdf.crs}")