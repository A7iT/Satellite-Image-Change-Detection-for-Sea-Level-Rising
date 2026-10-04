from pathlib import Path

from src.indices.normalized_difference import NormalizedDifferenceIndex
from src.models.year_dataset import YearDataset


class NDWI(NormalizedDifferenceIndex):
    """
    Normalized Difference Water Index.

    NDWI = (Green - NIR) / (Green + NIR)
    """

    def calculate(
        self,
        dataset: YearDataset,
    ) -> Path:

        return super().calculate(
            dataset=dataset,
            band_a="green",
            band_b="nir",
            output_name="ndwi.tif",
        )