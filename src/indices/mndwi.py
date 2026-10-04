from pathlib import Path

from src.indices.normalized_difference import NormalizedDifferenceIndex
from src.models.year_dataset import YearDataset


class MNDWI(NormalizedDifferenceIndex):
    """
    Modified Normalized Difference Water Index.

    MNDWI = (Green - SWIR1) / (Green + SWIR1)
    """

    def calculate(
        self,
        dataset: YearDataset,
    ) -> Path:

        return super().calculate(
            dataset=dataset,
            band_a="green",
            band_b="swir1",
            output_name="mndwi.tif",
        )