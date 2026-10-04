from pathlib import Path
from time import sleep

import geopandas as gpd
import rasterio
from loguru import logger
from rasterio.mask import mask


def download_and_clip(
    url: str,
    output_path: Path,
    aoi: gpd.GeoDataFrame,
    max_retries: int = 3,
) -> Path | None:
    """
    Download remote Cloud Optimized GeoTIFF,
    clip to AOI, save locally.

    Returns None if download fails.
    """

    delays = [5, 15, 30]

    for attempt in range(1, max_retries + 1):

        try:

            with rasterio.open(url) as src:

                aoi_projected = aoi.to_crs(src.crs)

                clipped, transform = mask(
                    src,
                    aoi_projected.geometry,
                    crop=True,
                )

                profile = src.profile.copy()

                profile.update(
                    height=clipped.shape[1],
                    width=clipped.shape[2],
                    transform=transform,
                )

                output_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                with rasterio.open(
                    output_path,
                    "w",
                    **profile,
                ) as dst:

                    dst.write(clipped)

            logger.debug(
                f"Downloaded: {output_path.name}"
            )

            return output_path


        except Exception as e:

            logger.warning(
                f"Attempt {attempt}/{max_retries} failed "
                f"for {output_path.name}: {e}"
            )

            if attempt < max_retries:
                sleep(delays[attempt - 1])


    logger.error(
        f"Skipping failed band: {output_path.name}"
    )

    return None