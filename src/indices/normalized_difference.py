from pathlib import Path

import numpy as np
import rasterio

from src.io.raster_writer import RasterWriter
from src.models.year_dataset import YearDataset


class NormalizedDifferenceIndex:
    """
    Base class for normalized difference indices.

    Formula:

        (Band A - Band B)
    -------------------------
        (Band A + Band B)
    """

    def __init__(self):

        self.writer = RasterWriter()

    def calculate(
        self,
        dataset: YearDataset,
        band_a: str,
        band_b: str,
        output_name: str,
    ) -> Path:

        band_a_path = dataset.composite_directory / f"{band_a}.tif"
        band_b_path = dataset.composite_directory / f"{band_b}.tif"

        with rasterio.open(band_a_path) as src:

            image_a = src.read(1).astype(np.float32)
            profile = src.profile.copy()

        with rasterio.open(band_b_path) as src:

            image_b = src.read(1).astype(np.float32)

        denominator = image_a + image_b

        index = np.divide(
            image_a - image_b,
            denominator,
            out=np.full_like(image_a, np.nan),
            where=denominator != 0,
        )

        output_path = dataset.indices_directory / output_name

        self.writer.write(
            image=index.astype(np.float32),
            profile=profile,
            output_path=output_path,
        )

        return output_path