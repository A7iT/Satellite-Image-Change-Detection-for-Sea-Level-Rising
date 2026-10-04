"""
Temporal Feature Engineering for Shoreline Change ML Dataset.

Enriches each transect-period sample with features derived from
the transect's historical behavior across all prior periods.

Features are computed using ONLY past data to prevent leakage.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger



# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = Path(
    "data/dataset/final_ml_dataset.csv"
)

LABELS_DIR = Path(
    "data/statistics"
)

OUTPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v0_temporal.csv"
)



# ==========================================================
# BUILD FULL HISTORY
# ==========================================================

def load_all_labels() -> pd.DataFrame:
    """
    Load and concatenate all period-level label CSVs
    to build a complete temporal record per transect.
    """

    files = sorted(
        LABELS_DIR.glob(
            "shoreline_labels_*.csv"
        )
    )

    if len(files) == 0:

        raise FileNotFoundError(
            f"No label files found in {LABELS_DIR}"
        )


    frames = []

    for file in files:

        logger.info(
            f"Loading {file.name}"
        )

        frames.append(
            pd.read_csv(file)
        )


    labels = pd.concat(
        frames,
        ignore_index=True,
    )


    labels = labels.sort_values(
        ["transect_id", "reference_year"],
    ).reset_index(drop=True)


    logger.info(
        f"Loaded {len(labels)} label records "
        f"across {labels['reference_year'].nunique()} periods"
    )


    return labels



# ==========================================================
# COMPUTE TEMPORAL FEATURES
# ==========================================================

def compute_temporal_features(
    labels: pd.DataFrame,
) -> pd.DataFrame:
    """
    For each transect-period row, compute temporal features
    from all PRIOR periods of the same transect.

    No future data is used — only strictly earlier periods.
    """

    logger.info(
        "Computing temporal features..."
    )

    results = []


    grouped = labels.groupby("transect_id")


    for transect_id, group in grouped:

        group = group.sort_values(
            "reference_year"
        ).reset_index(drop=True)


        for i in range(len(group)):

            row = group.iloc[i]

            prior = group.iloc[:i]


            feature = {

                "transect_id": int(row["transect_id"]),

                "reference_year": int(row["reference_year"]),

                "comparison_year": int(row["comparison_year"]),
            }


            # --------------------------------------------------
            # Previous period values
            # --------------------------------------------------

            if len(prior) >= 1:

                feature["epr_prev"] = float(
                    prior.iloc[-1]["EPR"]
                )

                feature["nsm_prev"] = float(
                    prior.iloc[-1]["NSM"]
                )

            else:

                feature["epr_prev"] = np.nan
                feature["nsm_prev"] = np.nan



            # --------------------------------------------------
            # Rolling mean EPR (3-period window)
            # --------------------------------------------------

            if len(prior) >= 3:

                feature["epr_rolling_3yr"] = float(
                    prior.tail(3)["EPR"].mean()
                )

            elif len(prior) >= 1:

                feature["epr_rolling_3yr"] = float(
                    prior["EPR"].mean()
                )

            else:

                feature["epr_rolling_3yr"] = np.nan



            # --------------------------------------------------
            # Rolling mean EPR (5-period window)
            # --------------------------------------------------

            if len(prior) >= 5:

                feature["epr_rolling_5yr"] = float(
                    prior.tail(5)["EPR"].mean()
                )

            elif len(prior) >= 1:

                feature["epr_rolling_5yr"] = float(
                    prior["EPR"].mean()
                )

            else:

                feature["epr_rolling_5yr"] = np.nan



            # --------------------------------------------------
            # Cumulative NSM (total displacement from start)
            # --------------------------------------------------

            if len(prior) >= 1:

                feature["nsm_cumulative"] = float(
                    prior["NSM"].sum()
                )

            else:

                feature["nsm_cumulative"] = 0.0



            # --------------------------------------------------
            # EPR volatility (std over last 3 periods)
            # --------------------------------------------------

            if len(prior) >= 3:

                feature["epr_std_3yr"] = float(
                    prior.tail(3)["EPR"].std()
                )

            elif len(prior) >= 2:

                feature["epr_std_3yr"] = float(
                    prior["EPR"].std()
                )

            else:

                feature["epr_std_3yr"] = np.nan



            # --------------------------------------------------
            # EPR trend slope (linear regression over all prior)
            # --------------------------------------------------

            if len(prior) >= 3:

                x = np.arange(len(prior), dtype=np.float64)

                y = prior["EPR"].values.astype(np.float64)

                # Simple least-squares slope
                x_mean = x.mean()
                y_mean = y.mean()

                numerator = ((x - x_mean) * (y - y_mean)).sum()

                denominator = ((x - x_mean) ** 2).sum()

                if denominator > 0:

                    feature["epr_trend_slope"] = float(
                        numerator / denominator
                    )

                else:

                    feature["epr_trend_slope"] = 0.0

            else:

                feature["epr_trend_slope"] = np.nan



            # --------------------------------------------------
            # Direction persistence
            # (fraction of prior periods with same direction)
            # --------------------------------------------------

            current_direction = row["Direction"]

            if len(prior) >= 1:

                same = (
                    prior["Direction"] == current_direction
                ).sum()

                feature["direction_persistence"] = float(
                    same / len(prior)
                )

            else:

                feature["direction_persistence"] = np.nan



            # --------------------------------------------------
            # Direction switches
            # (number of times direction changed in history)
            # --------------------------------------------------

            if len(prior) >= 2:

                directions = prior["Direction"].values

                switches = sum(
                    1
                    for j in range(1, len(directions))
                    if directions[j] != directions[j - 1]
                )

                feature["direction_switches"] = int(switches)

            elif len(prior) == 1:

                feature["direction_switches"] = 0

            else:

                feature["direction_switches"] = np.nan



            # --------------------------------------------------
            # Temporal position
            # --------------------------------------------------

            feature["years_since_start"] = (
                int(row["reference_year"]) - 2000
            )

            feature["period_length"] = int(row["years"])


            results.append(feature)


    result_df = pd.DataFrame(results)


    logger.info(
        f"Computed temporal features: {result_df.shape}"
    )

    logger.info(
        f"Temporal columns: "
        f"{[c for c in result_df.columns if c not in ['transect_id', 'reference_year', 'comparison_year']]}"
    )


    return result_df



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info(
        "Loading input dataset..."
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    logger.info(
        f"Input shape: {df.shape}"
    )



    # ----------------------------------------------------------
    # Load all historical labels
    # ----------------------------------------------------------

    labels = load_all_labels()



    # ----------------------------------------------------------
    # Compute temporal features
    # ----------------------------------------------------------

    temporal = compute_temporal_features(labels)



    # ----------------------------------------------------------
    # Merge with main dataset
    # ----------------------------------------------------------

    logger.info(
        "Merging temporal features..."
    )

    merged = df.merge(

        temporal,

        on=[
            "transect_id",
            "reference_year",
            "comparison_year",
        ],

        how="left",
    )


    unmatched = merged["epr_prev"].isna().sum()

    first_period_count = (
        merged["reference_year"] == merged["reference_year"].min()
    ).sum()

    logger.info(
        f"NaN in epr_prev: {unmatched} "
        f"(expected ~{first_period_count} from first period)"
    )



    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    merged.to_csv(
        OUTPUT_FILE,
        index=False,
    )


    logger.success(
        "Temporal feature engineering complete"
    )

    logger.success(
        f"Saved: {OUTPUT_FILE}"
    )

    logger.success(
        f"Final shape: {merged.shape}"
    )


    # Print new columns
    new_cols = [
        c for c in temporal.columns
        if c not in ["transect_id", "reference_year", "comparison_year"]
    ]

    logger.info(
        f"New temporal features ({len(new_cols)}):"
    )

    for col in new_cols:

        logger.info(
            f"  {col}"
        )



if __name__ == "__main__":

    main()

