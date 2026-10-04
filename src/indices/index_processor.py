from src.indices.mndwi import MNDWI
from src.indices.ndvi import NDVI
from src.indices.ndwi import NDWI

from src.models.year_dataset import YearDataset


class IndexProcessor:
    """
    Computes all spectral indices for a year's
    annual composite imagery.
    """

    def __init__(self):

        self.ndwi = NDWI()
        self.mndwi = MNDWI()
        self.ndvi = NDVI()

    def process(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        self.ndwi.calculate(dataset)
        self.mndwi.calculate(dataset)
        self.ndvi.calculate(dataset)

        return dataset