from shapely.geometry import LineString

from src.models.year_dataset import YearDataset

from src.shoreline.contour import ContourExtractor
from src.shoreline.smoother import ShorelineSmoother
from src.shoreline.vector_writer import VectorWriter


class ShorelineProcessor:
    """
    Generates shoreline vectors from annual water masks.

    Workflow
    --------
    1. Extract contours
    2. Convert contours to LineStrings
    3. Smooth geometries
    4. Save shoreline vector
    """

    def __init__(self):

        self.extractor = ContourExtractor()
        self.smoother = ShorelineSmoother()
        self.writer = VectorWriter()

    def process(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        # ---------------------------------------------------------
        # Extract shoreline contours
        # ---------------------------------------------------------

        contours, _, crs = self.extractor.extract(
            dataset,
        )

        shorelines = []

        # ---------------------------------------------------------
        # Convert to LineStrings
        # ---------------------------------------------------------

        for contour in contours:

            if len(contour) < 2:
                continue

            shoreline = LineString(contour)

            shoreline = self.smoother.smooth(
                shoreline,
            )

            shorelines.append(
                shoreline,
            )

        # ---------------------------------------------------------
        # Save shoreline vector
        # ---------------------------------------------------------

        self.writer.write(
            shorelines=shorelines,
            dataset=dataset,
            crs=crs,
        )

        return dataset