from pathlib import Path

from src.indices.normalized_difference import NormalizedDifferenceIndex
from src.models.year_dataset import YearDataset


class NDVI(NormalizedDifferenceIndex):
    """
    Normalized Difference Vegetation Index.

    NDVI = (NIR - Red) / (NIR + Red)
    """

    def calculate(
        self,
        dataset: YearDataset,
    ) -> Path:

        return super().calculate(
            dataset=dataset,
            band_a="nir",
            band_b="red",
            output_name="ndvi.tif",
        )