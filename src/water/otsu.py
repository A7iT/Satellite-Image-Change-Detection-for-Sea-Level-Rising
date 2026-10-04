from pathlib import Path

import numpy as np
import rasterio
from skimage.filters import threshold_otsu

from src.models.year_dataset import YearDataset


class OtsuThreshold:
    """
    Creates an initial binary water mask using
    Otsu's automatic threshold selection.

    Water = 1
    Non-water = 0
    """

    def create(
        self,
        dataset: YearDataset,
    ) -> tuple[np.ndarray, dict]:

        ndwi_path = dataset.indices_directory / "ndwi.tif"

        with rasterio.open(ndwi_path) as src:

            ndwi = src.read(1).astype(np.float32)
            profile = src.profile.copy()

        # ---------------------------------------------
        # Ignore NaN values
        # ---------------------------------------------

        valid_pixels = ndwi[~np.isnan(ndwi)]

        if valid_pixels.size == 0:
            raise ValueError(
                "NDWI image contains no valid pixels."
            )

        threshold = threshold_otsu(valid_pixels)

        print(f"Otsu Threshold : {threshold:.4f}")

        water_mask = ndwi > threshold

        return water_mask.astype(np.uint8), profile