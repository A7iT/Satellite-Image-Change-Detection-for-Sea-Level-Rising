from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.change_detection.baseline import BaselineGenerator
from src.change_detection.intersection import IntersectionFinder
from src.change_detection.metrics import ChangeMetrics
from src.change_detection.shoreline_loader import ShorelineLoader
from src.change_detection.transects import TransectGenerator


class ShorelineComparison:
    """
    Performs shoreline comparison between two years.
    """


    def __init__(self):

        self.loader = ShorelineLoader()

        self.baseline = BaselineGenerator()

        self.transects = TransectGenerator()

        self.intersections = IntersectionFinder()

        self.metrics = ChangeMetrics()



    def compare(
        self,
        analysis_directory: Path,
        reference_year: int,
        comparison_year: int,
    ) -> gpd.GeoDataFrame:



        # ---------------------------------------------------------
        # Load shorelines
        # ---------------------------------------------------------

        reference = self.loader.load(

            analysis_directory,

            reference_year,

        )


        comparison = self.loader.load(

            analysis_directory,

            comparison_year,

        )



        # ---------------------------------------------------------
        # Generate baseline
        # ---------------------------------------------------------

        baseline = self.baseline.generate(

            reference,

        )



        # ---------------------------------------------------------
        # Generate transects
        # ---------------------------------------------------------

        transects = self.transects.generate(

            baseline,

        )


        transects.set_crs(

            reference.crs,

            inplace=True,

        )



        # ---------------------------------------------------------
        # Find intersections
        # ---------------------------------------------------------

        reference_points = self.intersections.find(

            transects,

            reference,

            reference_year,

        )



        comparison_points = self.intersections.find(

            transects,

            comparison,

            comparison_year,

        )



        # ---------------------------------------------------------
        # Combine points
        # ---------------------------------------------------------

        all_points = pd.concat(

            [

                reference_points,

                comparison_points,

            ],

            ignore_index=True,

        )



        # ---------------------------------------------------------
        # Compute shoreline metrics
        # ---------------------------------------------------------

        water_mask_path = Path('data/water') / str(reference_year) / 'cleaned_water_mask.tif'

        metrics = self.metrics.compute(

            all_points,

            transects,

            reference_year,

            comparison_year,

            water_mask_path,

        )



        # ---------------------------------------------------------
        # Join metrics with transects
        # ---------------------------------------------------------

        results = transects.merge(

            metrics,

            on="transect_id",

            how="inner",

        )


        return results