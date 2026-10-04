from src.io.raster_writer import RasterWriter

from src.models.year_dataset import YearDataset

from src.water.morphology import Morphology
from src.water.otsu import OtsuThreshold


class WaterProcessor:
    """
    Generates annual water masks from NDWI imagery.

    Workflow
    --------
    1. Otsu thresholding
    2. Save raw water mask
    3. Morphological cleaning
    4. Save cleaned water mask
    """

    def __init__(self):

        self.threshold = OtsuThreshold()
        self.morphology = Morphology()
        self.writer = RasterWriter()

    def process(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        # ---------------------------------------------------------
        # Initial Water Mask
        # ---------------------------------------------------------

        raw_mask, profile = self.threshold.create(
            dataset,
        )

        profile.update(
            dtype="uint8",
            nodata=0,
            compress="lzw",
        )

        raw_output = (
            dataset.water_directory
            / "raw_water_mask.tif"
        )

        self.writer.write(
            image=raw_mask,
            profile=profile,
            output_path=raw_output,
        )

        # ---------------------------------------------------------
        # Clean Water Mask
        # ---------------------------------------------------------

        cleaned_mask = self.morphology.clean(
            raw_mask,
        )

        cleaned_output = (
            dataset.water_directory
            / "cleaned_water_mask.tif"
        )

        self.writer.write(
            image=cleaned_mask,
            profile=profile,
            output_path=cleaned_output,
        )

        return dataset