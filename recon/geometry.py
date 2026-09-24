"""CRS handling and polygon area in square metres."""
import geopandas as gpd


def to_metric_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject from degrees (EPSG:4326) to the local UTM zone (metres).

    estimate_utm_crs() picks the zone from the data's location, so this works
    anywhere, not just Bangalore (which resolves to EPSG:32643, UTM 43N).
    """
    return gdf.to_crs(gdf.estimate_utm_crs())


def add_area_sqm(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return a copy with 'map_area_sqm' computed in a metric CRS.

    Geometry stays in the original CRS so the output GeoJSON remains lon/lat.
    """
    out = gdf.copy()
    out["map_area_sqm"] = to_metric_crs(gdf).geometry.area.round(1)
    return out