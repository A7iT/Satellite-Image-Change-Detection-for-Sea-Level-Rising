from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString

from src.models.year_dataset import YearDataset


class VectorWriter:
    """
    Writes shoreline vectors to multiple GIS formats.
    """

    def write(
        self,
        shorelines: list[LineString],
        dataset: YearDataset,
        crs,
    ) -> dict[str, Path]:

        shoreline = gpd.GeoDataFrame(
            geometry=shorelines,
            crs=crs,
        )

        geojson_path = (
            dataset.analysis_directory
            / "shoreline.geojson"
        )

        shapefile_path = (
            dataset.analysis_directory
            / "shoreline.shp"
        )

        geopackage_path = (
            dataset.analysis_directory
            / "shoreline.gpkg"
        )

        # ---------------------------------------------------------
        # GeoJSON
        # ---------------------------------------------------------

        shoreline.to_file(
            geojson_path,
            driver="GeoJSON",
        )

        # ---------------------------------------------------------
        # ESRI Shapefile
        # ---------------------------------------------------------

        shoreline.to_file(
            shapefile_path,
            driver="ESRI Shapefile",
        )

        # ---------------------------------------------------------
        # GeoPackage
        # ---------------------------------------------------------

        shoreline.to_file(
            geopackage_path,
            driver="GPKG",
            layer="shoreline",
        )

        print(f"Saved: {geojson_path}")
        print(f"Saved: {shapefile_path}")
        print(f"Saved: {geopackage_path}")

        return {
            "geojson": geojson_path,
            "shapefile": shapefile_path,
            "geopackage": geopackage_path,
        }