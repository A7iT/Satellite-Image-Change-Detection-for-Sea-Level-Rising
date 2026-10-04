"""
Missing Value Handling with Spatial and Temporal Interpolation.

Strategy:
1. Temporal interpolation — fill from same transect's adjacent periods
2. Spatial interpolation  — fill from nearest neighbor transects (same period)
3. Global median fallback — for any remaining NaN values

This is more principled than global median fill alone.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger



# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v0b_spatial.csv"
)

OUTPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v1_missing_handled.csv"
)



# ==========================================================
# SPECTRAL & TEMPORAL COLUMNS
# ==========================================================

SPECTRAL_COLUMNS = [

    "ndwi_start",
    "ndwi_end",
    "ndwi_change",

    "ndvi_start",
    "ndvi_end",
    "ndvi_change",

    "mndwi_start",
    "mndwi_end",
    "mndwi_change",
]


VARIANCE_COLUMNS = [

    "ndwi_var_start",
    "ndwi_var_end",

    "ndvi_var_start",
    "ndvi_var_end",

    "mndwi_var_start",
    "mndwi_var_end",
]


BAND_COLUMNS = [

    "blue_start",
    "green_start",
    "red_start",
    "nir_start",
    "swir1_start",
    "swir2_start",

    "blue_end",
    "green_end",
    "red_end",
    "nir_end",
    "swir1_end",
    "swir2_end",
]


RATIO_COLUMNS = [

    "nir_green_ratio_start",
    "nir_green_ratio_end",

    "swir_nir_ratio_start",
    "swir_nir_ratio_end",
]


TEMPORAL_COLUMNS = [

    "epr_prev",
    "nsm_prev",
    "epr_rolling_3yr",
    "epr_rolling_5yr",
    "nsm_cumulative",
    "epr_std_3yr",
    "epr_trend_slope",
    "direction_persistence",
    "direction_switches",
]


SPATIAL_COLUMNS = [

    "neighbor_epr_mean",
    "neighbor_epr_std",
    "shoreline_curvature",
]


ALL_NUMERIC_COLUMNS = (
    SPECTRAL_COLUMNS
    + VARIANCE_COLUMNS
    + BAND_COLUMNS
    + RATIO_COLUMNS
    + TEMPORAL_COLUMNS
    + SPATIAL_COLUMNS
)


FLAG_COLUMNS = (
    SPECTRAL_COLUMNS[:6]
    + TEMPORAL_COLUMNS
    + SPATIAL_COLUMNS
)



# ==========================================================
# MISSING VALUE FLAGS
# ==========================================================

def add_missing_flags(df):
    """
    Add binary indicators for missing values.
    """

    for col in FLAG_COLUMNS:

        if col in df.columns:

            flag_name = f"{col}_missing"

            df[flag_name] = (
                df[col]
                .isna()
                .astype(int)
            )

            count = df[flag_name].sum()

            if count > 0:

                logger.info(
                    f"Created flag: {flag_name} "
                    f"({count} missing)"
                )

    return df



# ==========================================================
# TEMPORAL INTERPOLATION
# ==========================================================

def fill_temporal(df):
    """
    Fill missing spectral values from the same transect's
    adjacent time periods (forward-fill then back-fill).
    """

    logger.info(
        "Applying temporal interpolation..."
    )

    cols_to_fill = [
        c for c in SPECTRAL_COLUMNS + VARIANCE_COLUMNS + BAND_COLUMNS + RATIO_COLUMNS
        if c in df.columns
    ]

    if len(cols_to_fill) == 0:
        return df


    total_filled = 0

    missing_before = df[cols_to_fill].isna().sum().sum()


    if "transect_id" in df.columns and "reference_year" in df.columns:

        df = df.sort_values(
            ["transect_id", "reference_year"]
        )

        for col in cols_to_fill:

            if df[col].isna().sum() > 0:

                df[col] = df.groupby(
                    "transect_id"
                )[col].transform(
                    lambda s: s.interpolate(
                        method="linear",
                        limit_direction="both",
                    )
                )


        missing_after = df[cols_to_fill].isna().sum().sum()

        total_filled = missing_before - missing_after


    logger.info(
        f"Temporal interpolation filled {total_filled} values"
    )

    return df



# ==========================================================
# SPATIAL INTERPOLATION
# ==========================================================

def fill_spatial(df):
    """
    Fill remaining missing spectral values from the nearest
    neighbor transects within the same time period.
    """

    logger.info(
        "Applying spatial interpolation..."
    )

    cols_to_fill = [
        c for c in SPECTRAL_COLUMNS + VARIANCE_COLUMNS + BAND_COLUMNS + RATIO_COLUMNS
        if c in df.columns
    ]

    if len(cols_to_fill) == 0:
        return df


    total_filled = 0

    missing_before = df[cols_to_fill].isna().sum().sum()


    if (
        "transect_id" in df.columns
        and "reference_year" in df.columns
    ):

        for col in cols_to_fill:

            if df[col].isna().sum() == 0:
                continue

            # Within each period, fill from neighbor transects
            # (sorted by transect_id = spatial proximity)

            df[col] = df.groupby(
                "reference_year"
            )[col].transform(
                lambda s: s.interpolate(
                    method="linear",
                    limit_direction="both",
                )
            )


        missing_after = df[cols_to_fill].isna().sum().sum()

        total_filled = missing_before - missing_after


    logger.info(
        f"Spatial interpolation filled {total_filled} values"
    )

    return df



# ==========================================================
# GLOBAL MEDIAN FALLBACK
# ==========================================================

def fill_median_fallback(df):
    """
    Fill any remaining NaN values with global median
    as a last resort.
    """

    logger.info(
        "Applying median fallback for remaining gaps..."
    )

    all_cols = [
        c for c in ALL_NUMERIC_COLUMNS
        if c in df.columns
    ]


    total_filled = 0


    for col in all_cols:

        missing = df[col].isna().sum()

        if missing > 0:

            median_value = df[col].median()

            # If median is also NaN (all values missing), use 0
            if pd.isna(median_value):
                median_value = 0.0

            df[col] = df[col].fillna(
                median_value
            )

            total_filled += missing

            logger.info(
                f"{col}: filled {missing} remaining with "
                f"median {median_value:.5f}"
            )


    logger.info(
        f"Median fallback filled {total_filled} values total"
    )

    return df



# ==========================================================
# VALIDATION
# ==========================================================

def validate(df):

    logger.info(
        "Checking remaining missing values..."
    )

    missing = df.isna().sum()

    remaining = missing[
        missing > 0
    ]

    if len(remaining) == 0:

        logger.success(
            "No missing values remain"
        )

    else:

        logger.warning(
            f"Remaining missing values:\n{remaining}"
        )


    return df



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info(
        "Loading dataset..."
    )

    df = pd.read_csv(
        INPUT_FILE
    )


    logger.info(
        f"Original shape: {df.shape}"
    )

    logger.info(
        f"Total NaN values: {df.isna().sum().sum()}"
    )



    # ----------------------------------------------------------
    # Step 1: Add missing value indicators (before filling)
    # ----------------------------------------------------------

    logger.info(
        "Adding missing value indicators..."
    )

    df = add_missing_flags(df)



    # ----------------------------------------------------------
    # Step 2: Temporal interpolation (same transect, nearby years)
    # ----------------------------------------------------------

    df = fill_temporal(df)



    # ----------------------------------------------------------
    # Step 3: Spatial interpolation (nearby transects, same year)
    # ----------------------------------------------------------

    df = fill_spatial(df)



    # ----------------------------------------------------------
    # Step 4: Global median fallback (any remaining gaps)
    # ----------------------------------------------------------

    df = fill_median_fallback(df)



    # ----------------------------------------------------------
    # Step 5: Validate
    # ----------------------------------------------------------

    df = validate(df)



    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    logger.success(
        "Missing value handling complete"
    )

    logger.success(
        f"Saved: {OUTPUT_FILE}"
    )

    logger.success(
        f"Final shape: {df.shape}"
    )



if __name__ == "__main__":

    main()