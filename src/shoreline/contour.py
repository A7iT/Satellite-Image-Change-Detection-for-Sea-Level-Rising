from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import xy
from skimage.measure import find_contours

from src.models.year_dataset import YearDataset


class ContourExtractor:
    """
    Extracts shoreline contours from the cleaned water mask.
    """

    def extract(
        self,
        dataset: YearDataset,
    ) -> tuple[list[np.ndarray], rasterio.Affine]:

        mask_path = dataset.water_directory / "cleaned_water_mask.tif"

        with rasterio.open(mask_path) as src:

            mask = src.read(1)
            transform = src.transform
            crs = src.crs

        # Find contour at the boundary between 0 and 1
        contours = find_contours(mask, level=0.5)

        print(f"Contours extracted : {len(contours)}")

        world_contours = []

        for contour in contours:

            coordinates = []

            for row, col in contour:

                x, y = xy(
                    transform,
                    row,
                    col,
                )

                coordinates.append((x, y))

            world_contours.append(
                np.asarray(coordinates)
            )

        return world_contours, transform, crs