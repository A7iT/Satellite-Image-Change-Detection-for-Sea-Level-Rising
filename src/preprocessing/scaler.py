from pathlib import Path

import numpy as np
import rasterio

from src.preprocessing.constants import (
    REFLECTANCE_OFFSET,
    REFLECTANCE_SCALE,
)


class ReflectanceScaler:
    """
    Applies the official USGS Landsat Collection 2 Level-2
    surface reflectance scaling.

    Returns the scaled image and updated raster profile.
    Writing the raster to disk is handled separately by
    RasterWriter.
    """

    def scale(
        self,
        input_path: Path,
    ) -> tuple[np.ndarray, dict]:

        with rasterio.open(input_path) as src:

            image = src.read(1).astype(np.float32)
            profile = src.profile.copy()
            nodata = src.nodata

        # ---------------------------------------------------------
        # Scale only valid pixels
        # ---------------------------------------------------------

        if nodata is not None:

            valid_pixels = ~np.isclose(image, nodata)

            image[valid_pixels] = (
                image[valid_pixels] * REFLECTANCE_SCALE
                + REFLECTANCE_OFFSET
            )

            # Preserve NoData pixels
            image[~valid_pixels] = np.nan

            profile.update(
                nodata=np.nan,
            )

        else:

            image = (
                image * REFLECTANCE_SCALE
                + REFLECTANCE_OFFSET
            )

        # ---------------------------------------------------------
        # Update output profile
        # ---------------------------------------------------------

        profile.update(
            dtype="float32",
            count=1,
            compress="lzw",
        )

        return image, profile