from pathlib import Path

import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
import numpy as np

from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.plot import show
from loguru import logger



DEM_PATH = Path(
    "data/dem/rasters.tif"
)

SHORELINE_PATH = Path(
    "data/analysis/shoreline_change_2000_2005.gpkg"
)

OUTPUT_PATH = Path(
    "outputs/dem_alignment_check.png"
)



def reproject_dem():

    src = rasterio.open(
        DEM_PATH
    )

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
        source=rasterio.band(src,1),
        destination=data,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=target_crs,
        resampling=Resampling.bilinear
    )


    src.close()


    return data, transform, target_crs



def main():

    logger.info(
        "Loading shoreline..."
    )

    shoreline = gpd.read_file(
        SHORELINE_PATH
    )


    logger.info(
        "Reprojecting DEM..."
    )

    dem_array, transform, crs = reproject_dem()


    logger.info(
        f"DEM CRS: {crs}"
    )

    logger.info(
        f"Shoreline CRS: {shoreline.crs}"
    )


    output_bounds = rasterio.transform.array_bounds(
        dem_array.shape[0],
        dem_array.shape[1],
        transform
    )


    fig, ax = plt.subplots(
        figsize=(10,10)
    )


    show(
        dem_array,
        transform=transform,
        ax=ax
    )


    shoreline.plot(
        ax=ax,
        linewidth=1
    )


    buffer = shoreline.copy()

    buffer["geometry"] = (
        buffer.geometry.buffer(60)
    )


    buffer.boundary.plot(
        ax=ax,
        linewidth=0.5
    )


    ax.set_title(
        "DEM - Shoreline Alignment Check (EPSG:32646)"
    )


    plt.tight_layout()


    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    plt.savefig(
        OUTPUT_PATH,
        dpi=300
    )


    plt.close()


    logger.success(
        f"Saved: {OUTPUT_PATH}"
    )



if __name__ == "__main__":
    main()