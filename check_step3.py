from recon.loader import load_geojson
from recon.geometry import add_area_sqm, to_metric_crs

gdf = load_geojson("sample_data/parcels.geojson")
print("WRONG (area in degrees):", gdf.geometry.area.iloc[0])
print("Metric CRS used:", to_metric_crs(gdf).crs)

gdf = add_area_sqm(gdf)
print(gdf[["parcel_id", "village", "map_area_sqm"]].to_string())