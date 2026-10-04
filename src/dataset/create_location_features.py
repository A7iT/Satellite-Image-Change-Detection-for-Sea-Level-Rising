from pathlib import Path

import geopandas as gpd
import pandas as pd
from loguru import logger



# ==============================================================
# PATHS
# ==============================================================

BASE_DIR = Path("data")


ANALYSIS_DIR = (
    BASE_DIR /
    "analysis"
)


LABEL_FILE = (
    BASE_DIR /
    "dataset" /
    "shoreline_change_labels.csv"
)


OUTPUT_FILE = (
    BASE_DIR /
    "dataset" /
    "shoreline_change_with_location.csv"
)



# ==============================================================
# EXTRACT TRANSECT LOCATIONS
# ==============================================================

def extract_locations(gpkg_file):

    logger.info(
        f"Reading {gpkg_file.name}"
    )


    gdf = gpd.read_file(
        gpkg_file
    )


    # ----------------------------------------------------------
    # Transect midpoint
    # ----------------------------------------------------------

    gdf["midpoint"] = (
        gdf.geometry.centroid
    )


    points = gpd.GeoDataFrame(

        gdf[
            [
                "transect_id",
                "reference_year",
                "comparison_year",
                "midpoint"
            ]
        ],

        geometry="midpoint",

        crs=gdf.crs

    )


    # ----------------------------------------------------------
    # Keep projected coordinates
    # Same CRS as Landsat rasters
    # EPSG:32646
    # ----------------------------------------------------------

    points["utm_x"] = (
        points.geometry.x
    )


    points["utm_y"] = (
        points.geometry.y
    )


    return points[
        [
            "transect_id",
            "reference_year",
            "comparison_year",
            "utm_x",
            "utm_y"
        ]
    ]



# ==============================================================
# MAIN
# ==============================================================

def main():


    logger.info(
        "Loading label dataset..."
    )


    labels = pd.read_csv(
        LABEL_FILE
    )


    gpkg_files = sorted(

        ANALYSIS_DIR.glob(
            "shoreline_change_*.gpkg"
        )

    )


    logger.info(
        f"Found {len(gpkg_files)} GeoPackages"
    )



    locations = []


    for gpkg in gpkg_files:

        locations.append(

            extract_locations(
                gpkg
            )

        )



    locations = pd.concat(

        locations,

        ignore_index=True

    )



    logger.info(
        "Merging coordinates..."
    )


    dataset = labels.merge(

        locations,

        on=[

            "transect_id",

            "reference_year",

            "comparison_year"

        ],

        how="left"

    )



    missing = dataset[
        "utm_x"
    ].isna().sum()



    if missing > 0:

        logger.warning(
            f"{missing} samples missing coordinates"
        )



    dataset.to_csv(

        OUTPUT_FILE,

        index=False

    )


    logger.success(
        "Location feature generation complete"
    )


    logger.success(
        f"Saved: {OUTPUT_FILE}"
    )


    print(
        dataset.head()
    )



if __name__ == "__main__":

    main()