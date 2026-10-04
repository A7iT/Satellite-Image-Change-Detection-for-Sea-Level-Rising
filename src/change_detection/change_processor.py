from pathlib import Path

from src.change_detection.comparison import ShorelineComparison
from src.change_detection.statistics import ChangeStatistics
from src.models.change_detection_result import ChangeDetectionResult


class ChangeProcessor:
    """
    Executes the complete shoreline change detection workflow.
    """

    def __init__(self):

        self.comparison = ShorelineComparison()
        self.statistics = ChangeStatistics()

    def process(
        self,
        analysis_directory: Path,
        reference_year: int,
        comparison_year: int,
    ) -> ChangeDetectionResult:
        """
        Compare two shoreline years and compute change statistics.

        Parameters
        ----------
        analysis_directory : Path
            Directory containing shoreline outputs.

        reference_year : int
            Baseline year.

        comparison_year : int
            Comparison year.

        Returns
        -------
        ChangeDetectionResult
            Shoreline change results and statistics.
        """

        transects = self.comparison.compare(
            analysis_directory=analysis_directory,
            reference_year=reference_year,
            comparison_year=comparison_year,
        )

        statistics = self.statistics.summarize(transects)

        return ChangeDetectionResult(
            transects=transects,
            statistics=statistics,
            reference_year=reference_year,
            comparison_year=comparison_year,
        )