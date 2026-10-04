from dataclasses import dataclass

import geopandas as gpd

from src.models.change_statistics import ChangeStatisticsResult


@dataclass(slots=True)
class ChangeDetectionResult:
    """
    Complete shoreline change detection result.
    """

    transects: gpd.GeoDataFrame

    statistics: ChangeStatisticsResult

    reference_year: int

    comparison_year: int