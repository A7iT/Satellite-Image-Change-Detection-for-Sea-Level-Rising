from src.io.raster_writer import RasterWriter
from src.models.year_dataset import YearDataset

from src.compositing.loader import CompositeLoader
from src.compositing.median import MedianComposite

from src.preprocessing.constants import OPTICAL_BANDS


class AnnualCompositeBuilder:
    """
    Builds annual median composites for every optical band.

    Workflow
    --------
    1. Load all processed rasters for a band.
    2. Compute the annual median composite.
    3. Save the composite raster.
    """

    def __init__(self):

        self.loader = CompositeLoader()
        self.compositor = MedianComposite()
        self.writer = RasterWriter()

    def build(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        for band in OPTICAL_BANDS:

            # -----------------------------------------------------
            # Load processed rasters
            # -----------------------------------------------------

            stack, profile = self.loader.load(
                dataset=dataset,
                band=band,
            )

            # -----------------------------------------------------
            # Create annual composite
            # -----------------------------------------------------

            composite = self.compositor.create(
                stack,
            )

            # -----------------------------------------------------
            # Save composite
            # -----------------------------------------------------

            output_path = (
                dataset.composite_directory
                / f"{band}.tif"
            )

            self.writer.write(
                image=composite,
                profile=profile,
                output_path=output_path,
            )

        return dataset