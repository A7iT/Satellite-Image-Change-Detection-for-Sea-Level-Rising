import pandas as pd

from config.config import config

from src.models.change_statistics import (
    ChangeStatisticsResult,
)
from src.models.change_summary import (
    ChangeSummary,
)


class ChangeStatistics:
    """
    Computes shoreline change summary statistics.
    """

    def summarize(
        self,
        results: pd.DataFrame,
    ) -> ChangeStatisticsResult:

        if results.empty:

            summary = ChangeSummary(
                number_of_transects=0,

                mean_nsm=0.0,
                median_nsm=0.0,
                min_nsm=0.0,
                max_nsm=0.0,
                std_nsm=0.0,

                mean_epr=0.0,
                median_epr=0.0,
                min_epr=0.0,
                max_epr=0.0,
                std_epr=0.0,

                eroding_transects=0,
                accreting_transects=0,
                stable_transects=0,
            )

        else:

            nsm = results["NSM"]
            epr = results["EPR"]

            summary = ChangeSummary(

                number_of_transects=len(results),

                mean_nsm=nsm.mean(),
                median_nsm=nsm.median(),
                min_nsm=nsm.min(),
                max_nsm=nsm.max(),
                std_nsm=nsm.std(),

                mean_epr=epr.mean(),
                median_epr=epr.median(),
                min_epr=epr.min(),
                max_epr=epr.max(),
                std_epr=epr.std(),

                eroding_transects=(nsm > config.stable_threshold).sum(),
                accreting_transects=(nsm < -config.stable_threshold).sum(),
                stable_transects=(nsm.abs() <= config.stable_threshold).sum(),
            )

        table = pd.DataFrame(
            {
                "Statistic": [
                    "Number of Transects",
                    "Mean NSM (m)",
                    "Median NSM (m)",
                    "Minimum NSM (m)",
                    "Maximum NSM (m)",
                    "Standard Deviation NSM (m)",
                    "Mean EPR (m/year)",
                    "Median EPR (m/year)",
                    "Minimum EPR (m/year)",
                    "Maximum EPR (m/year)",
                    "Standard Deviation EPR (m/year)",
                    "Eroding Transects",
                    "Accreting Transects",
                    "Stable Transects",
                ],
                "Value": [
                    summary.number_of_transects,

                    summary.mean_nsm,
                    summary.median_nsm,
                    summary.min_nsm,
                    summary.max_nsm,
                    summary.std_nsm,

                    summary.mean_epr,
                    summary.median_epr,
                    summary.min_epr,
                    summary.max_epr,
                    summary.std_epr,

                    summary.eroding_transects,
                    summary.accreting_transects,
                    summary.stable_transects,
                ],
            }
        )

        return ChangeStatisticsResult(
            summary=summary,
            table=table,
        )