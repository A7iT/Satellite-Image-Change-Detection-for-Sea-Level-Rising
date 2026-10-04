from dataclasses import dataclass

import pandas as pd

from src.models.change_summary import ChangeSummary


@dataclass(slots=True)
class ChangeStatisticsResult:
    """
    Result produced by shoreline change statistics.
    """

    summary: ChangeSummary

    table: pd.DataFrame