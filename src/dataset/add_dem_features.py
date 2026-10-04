from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import mapping
from loguru import logger


# ==========================================================
# PATHS
# ==========================================================

INPUT_DATASET = Path(
    "data/dataset/final_ml_dataset_v2_cloud_features.csv"
)

DEM_PATH = Path(
    "data/dem/rasters.tif"
)

SHORELINE_DIR = Path(
    "data/analysis"
)

OUTPUT_DATASET = Path(
    "data/dataset/final_ml_dataset_v3_dem_features.csv"
)


BUFFER_DISTANCE = 60


# ==========================================================
# REPROJECT DEM
# ==========================================================

def reproject_dem(src_path):

    logger.info("Reprojecting DEM...")

    src = rasterio.open(src_path)

    target_crs = "EPSG:32646"

    transform, width, height = calculate_default_transform(
        src.crs,
        target_crs,
        src.width,
        src.height,
        *src.bounds
    )

    data = np.empty(
        (height, width),
        dtype=np.float32
    )

    reproject(
        source=rasterio.band(src, 1),
        destination=data,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=target_crs,
        resampling=Resampling.bilinear
    )

    src.close()

    return data, transform, target_crs



# ==========================================================
# EXTRACT DEM FEATURES
# ==========================================================

def extract_dem_features(
        geometry,
        dem
):

    buffer = geometry.buffer(
        BUFFER_DISTANCE
    )

    values, _ = mask(
        dem,
        [mapping(buffer)],
        crop=True,
        filled=False
    )

    elevation = values[0].compressed()

    if len(elevation) == 0:

        return [
            np.nan,
            np.nan,
            np.nan,
            np.nan
        ]

    return [
        float(np.mean(elevation)),
        float(np.min(elevation)),
        float(np.max(elevation)),
        float(np.std(elevation))
    ]



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("Loading dataset...")

    df = pd.read_csv(
        INPUT_DATASET
    )

    logger.info(
        f"Samples: {len(df)}"
    )


    logger.info(
        "Loading shoreline files..."
    )


    files = sorted(
        SHORELINE_DIR.glob(
            "shoreline_change_*.gpkg"
        )
    )


    shoreline_list = []


    for file in files:

        logger.info(
            file.name
        )

        shoreline_list.append(
            gpd.read_file(file)
        )


    shoreline = gpd.GeoDataFrame(
        pd.concat(
            shoreline_list,
            ignore_index=True
        ),
        crs="EPSG:32646"
    )


    dem_array, transform, crs = reproject_dem(
        DEM_PATH
    )


    profile = {
        "driver": "GTiff",
        "height": dem_array.shape[0],
        "width": dem_array.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform
    }


    results = []


    with rasterio.MemoryFile() as memfile:

        with memfile.open(**profile) as dem:

            dem.write(
                dem_array,
                1
            )


            for i, row in df.iterrows():


                match = shoreline[
                    (shoreline.transect_id == row.transect_id)
                    &
                    (shoreline.reference_year == row.reference_year)
                    &
                    (shoreline.comparison_year == row.comparison_year)
                ]


                if len(match) == 0:

                    results.append(
                        [
                            np.nan,
                            np.nan,
                            np.nan,
                            np.nan
                        ]
                    )

                else:

                    result = extract_dem_features(
                        match.iloc[0].geometry,
                        dem
                    )

                    results.append(
                        result
                    )


                if i % 100 == 0:

                    logger.info(
                        f"Processed {i}/{len(df)}"
                    )


    dem_features = pd.DataFrame(
        results,
        columns=[
            "elevation_mean",
            "elevation_min",
            "elevation_max",
            "elevation_std"
        ]
    )


    final = pd.concat(
        [
            df,
            dem_features
        ],
        axis=1
    )


    final.to_csv(
        OUTPUT_DATASET,
        index=False
    )


    logger.success(
        "DEM features added"
    )

    logger.success(
        f"Saved: {OUTPUT_DATASET}"
    )

    logger.success(
        f"Shape: {final.shape}"
    )



if __name__ == "__main__":
    main()